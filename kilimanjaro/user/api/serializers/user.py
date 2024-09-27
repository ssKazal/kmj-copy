from django.core.exceptions import ValidationError
from django.forms.models import model_to_dict
from djmoney.money import Money
from rest_framework import serializers

from customer.models import Customer
from occupation.models import Occupation
from skilled_worker.models import SkilledWorker
from user.models import User


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = (
            "id",
            "username",
            "first_name",
            "last_name",
            "date_of_birth",
            "phone_number",
            "email",
            "country",
            "city",
            "profile_picture",
            "age_consent",
            "terms_and_condition",
        )


class UserCustomerProfileSerializer(serializers.ModelSerializer):
    user = UserSerializer()

    class Meta:
        model = Customer
        fields = ("id", "balance_currency", "balance", "user")


class UserSkilledWorkerProfileSerializer(serializers.ModelSerializer):
    user = UserSerializer()
    occupation_name = serializers.SerializerMethodField()

    class Meta:
        model = SkilledWorker
        fields = (
            "id",
            "occupation_name",
            "description",
            "experience",
            "balance_currency",
            "balance",
            "user",
        )

    def get_occupation_name(self, obj):
        if obj.occupation:
            return obj.occupation.name
        return None


class UpdateProfileSerializer(serializers.ModelSerializer):

    # 'skilled worker' model fileds
    occupation = serializers.PrimaryKeyRelatedField(
        required=False, queryset=Occupation.objects.all()
    )
    description = serializers.CharField(required=False, allow_blank=True)
    experience = serializers.FloatField(required=False, min_value=0)

    class Meta:
        model = User
        fields = [
            "first_name",
            "last_name",
            "date_of_birth",
            "phone_number",
            "email",
            "country",
            "city",
            "profile_picture",
            "age_consent",
            "terms_and_condition",
            "email_subscription",
            "occupation",
            "description",
            "experience",
        ]

    def validate(self, attrs):
        user_obj = self.context["request"].user
        request_data = self.context["request"].data

        errors_list = {}  # Error message will append here

        skilled_worker_obj = (
            user_obj.skilledworker if hasattr(user_obj, "skilledworker") else None
        )  # Checking 'user' 'skilledworker' attr

        user_model_fields = [
            "first_name",
            "last_name",
            "date_of_birth",
            "phone_number",
            "email",
            "country",
            "city",
            "profile_picture",
            "age_consent",
            "terms_and_condition",
            "email_subscription",
        ]  # 'user' model fields

        skilled_worker_model_fields = [
            "occupation",
            "description",
            "experience",
        ]  # 'skilled worker' model fields

        user_data_dict = None
        skilled_worker_data_dict = None

        if self.context["request"].method == "PUT":

            serializer_fields = (
                user_model_fields + skilled_worker_model_fields
            )  # Adding two list

            serializer_fields_dict = dict.fromkeys(
                serializer_fields, None
            )  # Creating dictionary and set key's value to none

            user_data_dict = serializer_fields_dict | dict(
                attrs
            )  # Updating key value with attrs value

            skilled_worker_data_dict = {}  # Data-dict for 'skilled worker'

            # Removing fields that are not in 'skilled worker' model
            for key in skilled_worker_model_fields:
                skilled_worker_data_dict[key] = user_data_dict.pop(key, None)

        if self.context["request"].method == "PATCH":

            user_instance_data_dict = model_to_dict(
                user_obj
            )  # Getting 'user' data as dict using default function

            user_instance_updated_data_dict = user_instance_data_dict | dict(
                attrs
            )  # Merging 'user' data-dict with attrs-dict

            filterByKey = lambda keys: {
                x: user_instance_updated_data_dict[x] for x in keys
            }  # Function for filtering data depending on key

            user_data_dict = filterByKey(
                user_model_fields
            )  # 'user' instace data-dict for patch

            if skilled_worker_obj:
                skilled_worker_attrs_dict = (
                    {}
                )  # Data-dict for 'skilled worker' depending on attrs

                for key in skilled_worker_model_fields:
                    if key in request_data:
                        # Updating 'skilled worker' data dict value
                        if request_data.get(key, None) not in ["", None]:
                            skilled_worker_attrs_dict[key] = (
                                int(request_data.get(key))
                                if key == "occupation"
                                else request_data.get(key)
                            )
                        else:
                            skilled_worker_attrs_dict[key] = None

                skilled_worker_instance_data_dict = model_to_dict(
                    skilled_worker_obj
                )  # Getting 'skilled worker' instance data as dict using default function

                skilled_worker_updated_data_dict = (
                    skilled_worker_instance_data_dict | skilled_worker_attrs_dict
                )  # Merging 'skilled worker' data-dict with attrs-dict

                filterByKey = lambda keys: {
                    x: skilled_worker_updated_data_dict[x] for x in keys
                }  # Function for filtering data depending on key

                skilled_worker_data_dict = filterByKey(
                    skilled_worker_model_fields
                )  # 'skilled worker' instance updated data dict

        for key, value in user_data_dict.items():
            key = "country__id" if key == "country" and isinstance(value, int) else key
            setattr(user_obj, key, value)  # Updating 'user' instance

        try:
            user_obj.full_clean()  # Checking model validation for user
        except ValidationError as e:
            errors_list.update(e.message_dict)

        if not skilled_worker_obj:
            occupation = request_data.get("occupation", None)
            description = request_data.get("description", None)  # grab description

            """To create a skilled worker both occupation' & 'description' field value are needed.
            So, have to provide both of fields value or keep both fileds value blank"""
            if occupation and not description:
                errors_list.update({"description": "Add description"})
            if description and not occupation:
                errors_list.update({"occupation": "Add a occupation"})

        else:
            for key, value in skilled_worker_data_dict.items():
                key = (
                    "occupation__id"
                    if key == "occupation" and isinstance(value, int)
                    else key
                )
                setattr(
                    skilled_worker_obj, key, value
                )  # Updating skilled worker instance

            try:
                if not skilled_worker_obj.balance:
                    skilled_worker_obj.balance = Money(
                        0, "USD"
                    )  # 'balance' field value also required while validation check
                skilled_worker_obj.full_clean()  # Checking model validation for 'skilled worker'
            except ValidationError as e:
                errors_list.update(e.message_dict)

        if errors_list:
            raise serializers.ValidationError(errors_list)

        return attrs
