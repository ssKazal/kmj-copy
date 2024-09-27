import pytest
from django.core.exceptions import ValidationError
from django.db.models import Q

from user.api.serializers import ResetPasswordRequestSerializer
from user.models import ResetPasswordRequest


@pytest.mark.django_db
class TestAuthModels:
    reset_password_request_endpoint = "/user/reset-password-request/"
    reset_password_endpoint = "/user/reset-password/"

    def test_forget_password_serializer_without_verification_key(
        self, reset_password_request_obj1
    ):
        data = {
            "verification_key": "",
            "new_password": "testing321",
            "confirm_new_password": "testing321",
        }
        serializer = ResetPasswordRequestSerializer(data=data)
        assert serializer.is_valid() == False

    def test_forget_password_serializer_with_wrong_password(
        self, reset_password_request_obj1
    ):
        data = {
            "verification_key": "123456",
            "new_password": "123",
            "confirm_new_password": "testing321",
        }
        serializer = ResetPasswordRequestSerializer(data=data)
        assert serializer.is_valid() == False

    def test_forget_password_serializer_without_passwords(
        self, reset_password_request_obj1
    ):
        data = {
            "verification_key": "000000",
            "new_password": "",
            "confirm_new_password": "",
        }
        serializer = ResetPasswordRequestSerializer(data=data)
        assert serializer.is_valid() == False

    def test_reset_password_active_status_for_email(self, reset_password_request_obj1):
        requested_with_phone = Q(requested_with="phone") & Q(token="p-123456")
        requested_with_email = Q(requested_with="email") & Q(token="e-123456")

        request_obj = (
            ResetPasswordRequest.objects.active_sms()
            .filter(requested_with_phone, is_used=False)
            .first()
        )

        if not request_obj:
            request_obj = (
                ResetPasswordRequest.objects.active_email()
                .filter(requested_with_email, is_used=False)
                .first()
            )

        assert request_obj.requested_with == "email"

    def test_reset_password_active_status_for_phone(self, reset_password_request_obj2):
        requested_with_phone = Q(requested_with="phone") & Q(token="p-123455")
        requested_with_email = Q(requested_with="email") & Q(token="e-123455")

        request_obj = (
            ResetPasswordRequest.objects.active_sms()
            .filter(requested_with_phone, is_used=False)
            .first()
        )

        if not request_obj:
            request_obj = (
                ResetPasswordRequest.objects.active_email()
                .filter(requested_with_email, is_used=False)
                .first()
            )

        assert request_obj.requested_with == "phone"

    def test_reset_password_request_create_time_limit_for_email(
        self, user_obj1, reset_password_request_obj1
    ):
        reset_password_request = ResetPasswordRequest(
            user=user_obj1, requested_with="email", token="123445"
        )
        try:
            reset_password_request.full_clean()
            reset_password_request.save()
        except ValidationError as e:
            assert e.messages[0] == "With in one minute can sent one request"

    def test_reset_password_request_create_time_limit_for_phone(
        self, user_obj2, reset_password_request_obj2
    ):
        reset_password_request = ResetPasswordRequest(
            user=user_obj2, requested_with="phone", token="123445"
        )
        try:
            reset_password_request.full_clean()
            reset_password_request.save()
        except ValidationError as e:
            assert e.messages[0] == "With in one minute can sent one request"

    def test_api_login_with_phone_number(self, api_client, user_obj):
        data = {"email": user_obj.phone_number, "password": "test136"}
        endpoint = "/api/login/"
        response = api_client.post(endpoint, data=data)
        assert response.status_code == 200

    def test_api_login_with_email_address(self, api_client, user_obj):
        data = {"email": user_obj.email, "password": "test136"}
        endpoint = "/api/login/"
        response = api_client.post(endpoint, data=data)
        assert response.status_code == 200

    def test_api_login_with_unverified_user(self, api_client, user_obj1):
        data = {"email": user_obj1.email, "password": "test136"}
        endpoint = "/api/login/"
        response = api_client.post(endpoint, data=data)
        assert response.status_code == 200

    def test_api_login_as_admin(self, api_client, user_obj):
        data = {"user_id": user_obj.email, "password": "test136"}
        endpoint = "/admin-login/"
        response = api_client.post(endpoint, data=data)
        assert response.status_code == 302

    def test_api_login_as_admin_with_wrong_password(self, api_client, user_obj):
        data = {"user_id": user_obj.email, "password": "wrong-password"}
        endpoint = "/admin-login/"
        response = api_client.post(endpoint, data=data)
        assert response.status_code == 302

    def test_api_login_as_admin_with_unknown_email(self, api_client):
        data = {"user_id": "unknown", "password": "test136"}
        endpoint = "/admin-login/"
        response = api_client.post(endpoint, data=data)
        assert response.status_code == 302

    def test_api_refresh_token(self, auth_token, api_client):
        refresh = auth_token.get("refresh")
        endpoint = "/api/token/refresh_token/"
        response = api_client.post(endpoint, data={"refresh": refresh})
        assert response.status_code == 200

    def test_verification_token_send(self, api_client, auth_headers1):
        endpoint = "/user/send-verification-key/"
        response = api_client.post(endpoint, HTTP_AUTHORIZATION=auth_headers1)
        assert response.status_code == 200

    def test_verify_account(
        self, api_client, auth_headers1, account_verification_request_obj1
    ):
        endpoint = "/user/verify-account/"
        data = {"verification_key": "098765"}
        response = api_client.post(
            endpoint, data=data, HTTP_AUTHORIZATION=auth_headers1
        )
        assert response.status_code == 200

    def test_forget_password_email_send(self, api_client, user_obj1):
        data = {"email": user_obj1.email}
        response = api_client.post(self.reset_password_request_endpoint, data=data)
        assert response.status_code == 200

    def test_forget_password_token_send(self, api_client, user_obj2):
        data = {"phone_number": user_obj2.phone_number}
        response = api_client.post(self.reset_password_request_endpoint, data=data)
        assert response.status_code == 200

    def test_forget_password_token_send_without_user_id_check(
        self, api_client, user_obj1
    ):
        data = {}
        response = api_client.post(self.reset_password_request_endpoint, data=data)
        assert response.status_code == 422

    def test_forget_password_token_send_with_incorrect_user_id(
        self, api_client, user_obj1
    ):
        data = {"email": "abc@gmail.com"}
        response = api_client.post(self.reset_password_request_endpoint, data=data)
        assert response.status_code == 422

    def test_reset_password(self, api_client, reset_password_request_obj1):
        data = {
            "verification_key": "123456",
            "new_password": "update123",
            "confirm_new_password": "update123",
        }
        response = api_client.post(self.reset_password_endpoint, data=data)
        assert response.status_code == 200

    def test_reset_password_error_response_check(
        self, api_client, reset_password_request_obj1
    ):
        data = {
            "verification_key": "11111",
            "new_password": "update123",
            "confirm_new_password": "update123",
        }
        response = api_client.post(self.reset_password_endpoint, data=data)
        assert response.status_code == 422
