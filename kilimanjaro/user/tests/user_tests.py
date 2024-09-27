import pytest
from django.core.cache import cache

from core.utils.general_func import file_object, request_factory
from customer.models import Customer
from skilled_worker.models import SkilledWorker
from user.api.serializers import (PasswordChangeSerializer,
                                  UpdateProfileSerializer, UserSerializer,
                                  UserSkilledWorkerProfileSerializer)


@pytest.mark.django_db
class TestUser:

    user_profile_endpoint = "/user/"
    update_profile_endpoint = "/user/update_profile/"
    user_customer_profile_endpoint = "/user/user_customer_profile/"
    user_skilled_worker_profile_endpoint = "/user/user_skilled_worker_profile/"
    change_password_endpoint = "/user/change_password/"

    def test_user_profile_update(
        self, country_obj, occupation_obj, api_client, user_obj, auth_headers
    ):
        user_data_dict = {
            "email": "sk@gmail.com",
            "first_name": "user updated",
            "last_name": "one",
            "date_of_birth": "2000-01-01",
            "phone_number": "+8801700000001",
            "country": country_obj.id,
            "city": "Berlin",
            "profile_picture": file_object(name="afbcde.png"),
            "age_consent": "25",
            "terms_and_condition": True,
            "occupation": occupation_obj.id,
            "description": "Skilled worker descriptions",
            "experience": 2,
        }
        response = api_client.put(
            f"{self.update_profile_endpoint}",
            data=user_data_dict,
            format="multipart",
            HTTP_AUTHORIZATION=auth_headers,
        )
        assert response.data["message"] == "Success! Your profile is updated"

    def test_user_profile_partial_update(
        self, country_obj, occupation_obj, api_client, user_obj, auth_headers
    ):
        user_data_dict = {
            "email": "sk@gmail.com",
            "first_name": "user updated",
            "last_name": "one updated",
            "date_of_birth": "2000-03-01",
        }
        response = api_client.patch(
            f"{self.update_profile_endpoint}",
            data=user_data_dict,
            format="multipart",
            HTTP_AUTHORIZATION=auth_headers,
        )
        assert response.data["message"] == "Success! Your profile is updated"

    def test_skilled_worker_create(
        self, occupation_obj, api_client, user_obj, auth_headers
    ):
        SkilledWorker.objects.filter(user__id=user_obj.id).delete()
        user_data_dict = {
            "occupation": occupation_obj.id,
            "description": "Skilled worker descriptions",
            "experience": 2,
        }

        response = api_client.patch(
            f"{self.update_profile_endpoint}",
            data=user_data_dict,
            format="multipart",
            HTTP_AUTHORIZATION=auth_headers,
        )
        assert response.status_code == 200

    def test_try_to_update_user_profile_update_without_required_field_value(
        self, api_client, user_obj, auth_headers, occupation_obj
    ):
        user_data_dict = {
            "email": "user1@gmail.com",
            "first_name": "user updated",
            "last_name": "one",
            "date_of_birth": "2000-01-01",
            "phone_number": "+8801700000001",
            "city": "Berlin",
            "profile_picture": file_object(name="abcde1.png"),
            "age_consent": "25",
            "terms_and_condition": True,
            "email_subscription": False,
            "description": "Skilled worker descriptions",
            "occupation": occupation_obj.id,
            "experience": 2.5,
        }
        response = api_client.put(
            f"{self.update_profile_endpoint}",
            data=user_data_dict,
            format="multipart",
            HTTP_AUTHORIZATION=auth_headers,
        )
        assert response.data["country"][0] == "This field cannot be blank."

    def test_user_profile_update_occupation_check(
        self, api_client, user_without_skp, auth_headers_for_without_skp
    ):
        user_data_dict = {
            "description": "Skilled worker descriptions",
        }
        response = api_client.patch(
            f"{self.update_profile_endpoint}",
            data=user_data_dict,
            format="multipart",
            HTTP_AUTHORIZATION=auth_headers_for_without_skp,
        )
        assert response.data["occupation"][0] == "Add a occupation"

    def test_user_profile_update_description_check(
        self, occupation_obj, api_client, user_without_skp, auth_headers_for_without_skp
    ):
        user_data_dict = {
            "occupation": occupation_obj.id,
        }
        response = api_client.patch(
            f"{self.update_profile_endpoint}",
            data=user_data_dict,
            format="multipart",
            HTTP_AUTHORIZATION=auth_headers_for_without_skp,
        )
        assert response.data["description"][0] == "Add description"

    def test_user_profile_email_update(
        self, api_client, auth_headers, skilled_worker_obj, occupation_obj
    ):
        user_data_dict = {
            "first_name": "Uptated First name",
            "last_name": "New lastname",
            "email": "upsk@gmail.com",
            "description": "des",
        }
        response = api_client.patch(
            f"{self.update_profile_endpoint}",
            data=user_data_dict,
            format="multipart",
            HTTP_AUTHORIZATION=auth_headers,
        )
        assert response.status_code == 200

    def test_user_profile_phone_number_update(
        self, api_client, auth_headers, skilled_worker_obj, occupation_obj
    ):
        user_data_dict = {
            "first_name": "Uptated First name",
            "last_name": "New lastname",
            "phone_number": "+8801700000001",
            "description": "des",
        }
        response = api_client.patch(
            f"{self.update_profile_endpoint}",
            data=user_data_dict,
            format="multipart",
            HTTP_AUTHORIZATION=auth_headers,
        )
        assert response.status_code == 200

    def test_user_profile_partial_update_error_check(
        self, api_client, auth_headers, skilled_worker_obj, occupation_obj
    ):
        user_data_dict = {
            "first_name": "Uptated First name",
            "last_name": "New lastname",
            "occupation": occupation_obj.id,
            "experience": "",
            "description": "des",
        }
        response = api_client.patch(
            f"{self.update_profile_endpoint}",
            data=user_data_dict,
            format="multipart",
            HTTP_AUTHORIZATION=auth_headers,
        )

        assert response.status_code == 422

    def test_change_password_serializer(self, user_obj):
        data = {
            "old_password": "test136",
            "new_password": "testing321",
            "confirm_new_password": "testing321",
        }
        serializer = PasswordChangeSerializer(data=data, context={"user": user_obj})
        assert serializer.is_valid(raise_exception=True)
        assert serializer.errors == {}

    def test_change_password_serializer_without_previous_password(self, user_obj):
        data = {
            "old_password": "",
            "new_password": "testing321",
            "confirm_new_password": "testing321",
        }
        serializer = PasswordChangeSerializer(data=data, context={"user": user_obj})
        response = serializer.is_valid()
        assert response == False

    def test_change_password_serializer_with_incorrect_password(self, user_obj):
        data = {
            "old_password": "wrongpass",
            "new_password": "123",
            "confirm_new_password": "testing321",
        }
        serializer = PasswordChangeSerializer(data=data, context={"user": user_obj})
        response = serializer.is_valid()
        assert response == False

    def test_change_password_serializer_without_passwords(self, user_obj):
        data = {
            "old_password": "wrongpass",
            "new_password": "",
            "confirm_new_password": "",
        }
        serializer = PasswordChangeSerializer(data=data, context={"user": user_obj})
        response = serializer.is_valid()
        assert response == False

    def test_skilled_worker_serializer(self, skilled_worker_obj2):
        serializer = UserSkilledWorkerProfileSerializer(skilled_worker_obj2)
        assert serializer.data["description"] == "skill worker description"

    def test_user_profile(self, api_client, auth_headers, customer_obj):
        response = api_client.get(
            self.user_profile_endpoint, HTTP_AUTHORIZATION=auth_headers
        )
        assert response.status_code == 200

    def test_user_without_customer_profile(
        self, api_client, auth_headers, customer_obj
    ):
        cache.delete(f"custom_profile_{customer_obj.user.id}")
        Customer.objects.filter(user__id=customer_obj.user.id).delete()
        response = api_client.get(
            f"{self.user_customer_profile_endpoint}", HTTP_AUTHORIZATION=auth_headers
        )
        assert response.status_code == 422

    def test_user_without_skilledworker_profile(
        self, api_client, auth_headers, skilled_worker_obj
    ):
        cache.delete(f"skilled_worker_profile{skilled_worker_obj.user.id}")
        SkilledWorker.objects.filter(user__id=skilled_worker_obj.user.id).delete()
        response = api_client.get(
            f"{self.user_skilled_worker_profile_endpoint}",
            HTTP_AUTHORIZATION=auth_headers,
        )
        assert response.status_code == 422

    def test_customer_profile(self, api_client, auth_headers, customer_obj):
        cache.delete(f"custom_profile_{customer_obj.user.id}")
        response = api_client.get(
            f"{self.user_customer_profile_endpoint}", HTTP_AUTHORIZATION=auth_headers
        )
        assert response.status_code == 200

    def test_customer_profile_cache(self, api_client, auth_headers, customer_obj):
        response = api_client.get(
            f"{self.user_customer_profile_endpoint}", HTTP_AUTHORIZATION=auth_headers
        )
        assert response.status_code == 200

    def test_skilledworker_profile(self, api_client, auth_headers, skilled_worker_obj):
        cache.delete(f"skilled_worker_profile{skilled_worker_obj.user.id}")
        response = api_client.get(
            f"{self.user_skilled_worker_profile_endpoint}",
            HTTP_AUTHORIZATION=auth_headers,
        )
        assert response.status_code == 200

    def test_skilledworker_profile_cache(
        self, api_client, auth_headers, skilled_worker_obj
    ):
        response = api_client.get(
            f"{self.user_skilled_worker_profile_endpoint}",
            HTTP_AUTHORIZATION=auth_headers,
        )
        assert response.status_code == 200

    def test_change_password(self, api_client, auth_headers):
        data = {
            "old_password": "test136",
            "new_password": "changedpass123",
            "confirm_new_password": "changedpass123",
        }
        response = api_client.put(
            f"{self.change_password_endpoint}",
            data=data,
            HTTP_AUTHORIZATION=auth_headers,
        )
        assert response.status_code == 200

    def test_change_password_error(self, api_client, auth_headers):
        data = {
            "old_password": "test136",
            "new_password": "changedpass123",
            "confirm_new_password": "hangedpass123",
        }
        response = api_client.put(
            f"{self.change_password_endpoint}",
            data=data,
            HTTP_AUTHORIZATION=auth_headers,
        )
        assert response.status_code == 422

    def test_user_string_representation(self, user_obj3):
        assert user_obj3.__str__() in [user_obj3.get_full_name(), user_obj3.username, "GigUP User"]
