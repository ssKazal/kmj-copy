import pytest
from django.core.exceptions import ValidationError

from core.utils.general_func import file_object
from user.api.serializers import UserRegistrationSerializer
from user.models import User


@pytest.mark.django_db
class TestUserResistration:
    user_registration_endpoint = "/user/registration/"

    def test_user_registration(self, country_obj, api_client):
        user_data_dict = {
            "username": "user1",
            "email": "user1@gmail.com",
            "first_name": "user",
            "last_name": "one",
            "date_of_birth": "2000-01-01",
            "password": "testing321",
            "confirm_password": "testing321",
            "phone_number": "+8801700005001",
            "country": country_obj.id,
            "city": "Berlin",
            "profile_picture": file_object(name="abcdye.png"),
            "age_consent": "25",
        }
        response = api_client.post(
            self.user_registration_endpoint, data=user_data_dict, format="multipart"
        )
        assert response.status_code == 200

    def test_user_registration_without_confirm_password(self, country_obj, api_client):
        user_data_dict = {
            "username": "user1",
            "email": "user1@gmail.com",
            "first_name": "user",
            "last_name": "one",
            "date_of_birth": "2000-01-01",
            "password": "testing321",
            "phone_number": "",
            "country": country_obj.id,
            "city": "Berlin",
            "profile_picture": file_object(name="abcde.png"),
            "age_consent": "25",
            "terms_and_condition": True,
        }

        response = api_client.post(
            self.user_registration_endpoint, data=user_data_dict, format="multipart"
        )
        assert response.data["confirm_password"][0] == "Enter confirm-password"

    def test_user_registration_with_unequal_pass(self, country_obj, api_client):

        user_data_dict = {
            "username": "user1",
            "email": "user1@gmail.com",
            "first_name": "user",
            "last_name": "one",
            "date_of_birth": "2000-01-01",
            "password": "testing321!",
            "confirm_password": "testing321",
            "phone_number": "",
            "country": country_obj.id,
            "city": "Berlin",
            "profile_picture": file_object(name="abcde.png"),
            "age_consent": "25",
            "terms_and_condition": True,
        }

        response = api_client.post(
            self.user_registration_endpoint, data=user_data_dict, format="multipart"
        )
        assert response.data["non_field_error"][0] == "Password doesn't match"

    def test_user_registration_with_short_password(self, country_obj, api_client):

        user_data_dict = {
            "username": "user1",
            "email": "user1@gmail.com",
            "first_name": "user",
            "last_name": "one",
            "date_of_birth": "2000-01-01",
            "password": "abc12345",
            "confirm_password": "abc12345",
            "phone_number": "",
            "country": country_obj.id,
            "city": "Berlin",
            "profile_picture": file_object(name="abcde.png"),
            "age_consent": "25",
            "terms_and_condition": True,
        }

        response = api_client.post(
            self.user_registration_endpoint, data=user_data_dict, format="multipart"
        )
        assert response.data["password"][0] == "This password is too common."

    def test_user_registration_without_first_name(self, country_obj, api_client):
        user_data_dict = {
            "username": "user1",
            "email": "user1@gmail.com",
            "last_name": "one",
            "date_of_birth": "2000-01-01",
            "password": "testing321",
            "confirm_password": "testing321",
            "phone_number": "+8801700005001",
            "country": country_obj.id,
            "city": "Berlin",
            "profile_picture": file_object(name="abcdye.png"),
            "age_consent": "25",
        }

        response = api_client.post(
            self.user_registration_endpoint, data=user_data_dict, format="multipart"
        )
        assert response.data["first_name"][0] == "This field cannot be blank."

    def test_staff_user_create(self):
        try:
            User.objects.create_user(
                email="newuser@gmail.com",
                password="testpass!!!",
                phone_number="+8801750222223",
            )
        except ValueError as e:
            assert e.args[0] == "Use '/admin/user' for creating new user."

    def test_super_user_create(self):
        user_obj = User.objects.create_superuser(
            email="newuser@gmail.com", password="testpass!!!"
        )
        assert user_obj.email == "newuser@gmail.com"

    def test_super_user_create_without_email(self):
        try:
            User.objects.create_superuser(email="", password="testpass!!!")
        except ValueError as e:
            assert e.args[0] == "Enter an email address"

    def test_try_to_create_user_without_email_and_phone_number(
        self, user_obj, country_obj
    ):
        data = {
            "email": "",
            "username": "sajib1",
            "password": "trjhf8477",
            "first_name": "s",
            "last_name": "k",
            "date_of_birth": "2000-01-01",
            "country": country_obj,
            "city": "Berlin",
            "profile_picture": file_object(name="abcde.png"),
            "age_consent": 25,
            "terms_and_condition": True,
            "is_email_verified": True,
            "is_phone_number_verified": True,
        }

        user_obj = User(**data)
        try:
            user_obj.full_clean()
        except ValidationError as e:
            assert e.messages[0] == "Either phone number or email is required"

    def test_try_to_create_user_with_existing_email(self, user_obj, country_obj):
        data = {
            "email": "sk@gmail.com",
            "username": "sajib1",
            "password": "trjhf8477",
            "first_name": "s",
            "last_name": "k",
            "date_of_birth": "2000-01-01",
            "country": country_obj,
            "city": "Berlin",
            "profile_picture": file_object(name="abcde.png"),
            "age_consent": 25,
            "terms_and_condition": True,
            "is_email_verified": True,
            "is_phone_number_verified": True,
        }

        user_obj = User(**data)
        try:
            user_obj.full_clean()
        except ValidationError as e:
            assert e.messages[0] == "User with this email already exists"

    def test_try_to_create_user_with_existing_phone_number(
        self, user_obj2, country_obj
    ):
        data = {
            "phone_number": "+8801760000030",
            "username": "sajib1",
            "password": "trjhf8477",
            "first_name": "s",
            "last_name": "k",
            "date_of_birth": "2000-01-01",
            "country": country_obj,
            "city": "Berlin",
            "profile_picture": file_object(name="abcde.png"),
            "age_consent": 25,
            "terms_and_condition": True,
            "is_email_verified": True,
            "is_phone_number_verified": True,
        }

        user_obj = User(**data)
        try:
            user_obj.full_clean()
        except ValidationError as e:
            assert e.messages[0] == "User with this phone_number already exists"

    def test_user_age_in_clean_method(self, country_obj):
        data = {
            "phone_number": "+8801760000030",
            "username": "sajib1",
            "password": "trjhf8477",
            "first_name": "s",
            "last_name": "k",
            "date_of_birth": "2010-01-01",
            "country": country_obj,
            "city": "Berlin",
            "profile_picture": file_object(name="abcde.png"),
            "age_consent": 25,
            "terms_and_condition": True,
            "is_email_verified": True,
            "is_phone_number_verified": True,
        }

        user_obj = User(**data)
        try:
            user_obj.full_clean()
        except ValidationError as e:
            assert e.messages[0] == "Min age: 18 years"
