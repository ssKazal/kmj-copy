from django.contrib.auth.password_validation import validate_password
from django.core.exceptions import ValidationError
from rest_framework import serializers

from user.models import User


class UserRegistrationSerializer(serializers.ModelSerializer):
    password = serializers.CharField(
        required=False, write_only=True, style={"input_type": "password"}
    )
    confirm_password = serializers.CharField(
        required=False, write_only=True, style={"input_type": "password"}
    )

    class Meta:
        model = User
        fields = [
            "username",
            "first_name",
            "last_name",
            "date_of_birth",
            "phone_number",
            "email",
            "password",
            "confirm_password",
            "country",
            "city",
            "profile_picture",
            "age_consent",
            "terms_and_condition",
        ]

    def validate(self, attrs):
        confirm_password = attrs.pop("confirm_password", None)
        user = User(**attrs)

        errors_list = {}  # Error messages will append here
        try:
            user.full_clean()  # Checking model of validation
        except ValidationError as e:
            errors_list.update(e.message_dict)

        if not confirm_password:
            errors_list.update({"confirm_password": ["Enter confirm-password"]})

        password = attrs.get("password", None)
        if password and confirm_password and password != confirm_password:
            errors_list.update({"non_field_error": ["Password doesn't match"]})

        if user and password:
            try:
                validate_password(password, user)  # Checking password validation
            except ValidationError as e:
                errors_list.update({"password": e.messages})

        if errors_list:
            raise serializers.ValidationError(errors_list)

        return attrs
