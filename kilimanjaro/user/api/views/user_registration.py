from rest_framework import viewsets
from rest_framework.response import Response

from core.utils import get_tokens_for_user, send_verification_credential
from country.models import Country
from customer.models import Customer
from user.api.serializers import UserRegistrationSerializer
from user.models import User


class UserRegistrationViewset(viewsets.ModelViewSet):
    serializer_class = UserRegistrationSerializer
    http_method_names = ["post"]

    def create(self, request, *args, **kwargs):
        """Creates User object and returns verification info and 'JWT' as response"""

        data = request.data
        serializer = self.get_serializer(data=data)
        serializer.is_valid(raise_exception=True)

        user_creation_fields = [
            "username",
            "first_name",
            "last_name",
            "date_of_birth",
            "phone_number",
            "email",
            "city",
            "profile_picture",
            "age_consent",
            "terms_and_condition",
        ]

        request_data_dict = data.dict()

        user_data_dict = {}  # 'request' data to create a 'user' will append here

        # Updating 'user_data_dict'
        for key in user_creation_fields:
            if key in request_data_dict:
                user_data_dict[key] = request_data_dict[key]
            else:
                user_data_dict[key] = None

        # FK instance needs as value while creating. So, passing FK value this way
        user_data_dict["country_id"] = request_data_dict.get("country", None)

        password = request_data_dict.get("password", None)
        user = User(**user_data_dict)
        user.set_password(password)
        user.save()
        Customer.objects.create(user=user)

        """Custom func to get 'user' access & refresh token
        because, those token are needed to verify account"""
        jwt_token = get_tokens_for_user(user)

        response_data = {}  # Response messages will append here
        data_dict = {
            "request_for": "account_verification",
            "user_obj": user,
        }  # Account verification data-dict

        phone_number = request_data_dict.get("phone_number", None)
        email = request_data_dict.get("email", None)

        # Sends verification info using custom function
        if phone_number:
            data_dict.update(phone_number=phone_number)
            response_message = send_verification_credential(**data_dict)
            response_data["sms_send_message"] = response_message
        if email:
            data_dict.update(email=email)
            response_message = send_verification_credential(**data_dict)
            response_data["email_send_message"] = response_message

        response_data.update(jwt_token)

        return Response(response_data)
