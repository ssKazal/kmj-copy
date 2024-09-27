import pytest
from django.core.exceptions import ValidationError
from django.db.models import Q

from user.models import AccountVerificationRequest


@pytest.mark.django_db
class TestAccountVerificationRequest:

    verification_key_send_endpoint = "/user/send-verification-key/"
    verify_account_endpoint = "/user/verify-account/"

    def test_account_verification_request_model_for_email(
        self, user_obj1, account_verification_request_obj1
    ):
        account_verification_request_obj2 = AccountVerificationRequest(
            user=user_obj1, verify_by="email", token="123445"
        )

        try:
            account_verification_request_obj2.full_clean()
            account_verification_request_obj2.save()
        except ValidationError as e:
            assert e.messages[0] == "With in one minute can sent one request"

    def test_account_verification_request_model_for_phone(
        self, user_obj2, account_verification_request_obj2
    ):
        account_verification_request_obj = AccountVerificationRequest(
            user=user_obj2, verify_by="phone", token="123445"
        )

        try:
            account_verification_request_obj.full_clean()
            account_verification_request_obj.save()
        except ValidationError as e:
            assert e.messages[0] == "With in one minute can sent one request"

    def test_account_verification_active_status_for_phone(
        self, account_verification_request_obj2
    ):
        requested_with_phone = Q(verify_by="phone") & Q(token="p-098766")
        requested_with_email = Q(verify_by="email") & Q(token="e-098766")

        request_obj = (
            AccountVerificationRequest.objects.active_sms()
            .filter(requested_with_phone, is_used=False)
            .first()
        )

        if not request_obj:
            request_obj = (
                AccountVerificationRequest.objects.active_email()
                .filter(requested_with_email, is_used=False)
                .first()
            )

        assert request_obj.verify_by == "phone"

    def test_account_verification_active_status_for_email(
        self, account_verification_request_obj1
    ):
        requested_with_phone = Q(verify_by="phone") & Q(token="p-098765")
        requested_with_email = Q(verify_by="email") & Q(token="e-098765")

        request_obj = (
            AccountVerificationRequest.objects.active_sms()
            .filter(requested_with_phone, is_used=False)
            .first()
        )

        if not request_obj:
            request_obj = (
                AccountVerificationRequest.objects.active_email()
                .filter(requested_with_email, is_used=False)
                .first()
            )

        assert request_obj.verify_by == "email"

    def test_send_verification_key_if_email_and_phone_both_verified(
        self, api_client, auth_headers
    ):
        response = api_client.post(
            self.verification_key_send_endpoint, HTTP_AUTHORIZATION=auth_headers
        )
        assert response.status_code == 422

    def test_verify_account_with_email(
        self, api_client, auth_headers1, account_verification_request_obj1
    ):
        data = {"verification_key": "098765"}
        response = api_client.post(
            self.verify_account_endpoint, data=data, HTTP_AUTHORIZATION=auth_headers1
        )
        assert response.status_code == 200

    def test_send_verification_key_for_phone(self, api_client, auth_headers_for_phone):
        response = api_client.post(
            self.verification_key_send_endpoint,
            HTTP_AUTHORIZATION=auth_headers_for_phone,
        )
        assert response.status_code == 200

    def test_verify_account_with_phone(
        self, api_client, auth_headers_for_phone, account_verification_request_obj2
    ):
        data = {"verification_key": "098766"}
        response = api_client.post(
            self.verify_account_endpoint,
            data=data,
            HTTP_AUTHORIZATION=auth_headers_for_phone,
        )
        assert response.status_code == 200

    def test_verify_account_without_verification_key(
        self, api_client, auth_headers1, account_verification_request_obj1
    ):
        data = {}
        response = api_client.post(
            self.verify_account_endpoint, data=data, HTTP_AUTHORIZATION=auth_headers1
        )
        assert response.status_code == 422

    def test_verify_account_with_invalid_verification_key(
        self, api_client, auth_headers1, account_verification_request_obj1
    ):
        data = {"verification_key": "000000"}
        response = api_client.post(
            self.verify_account_endpoint, data=data, HTTP_AUTHORIZATION=auth_headers1
        )
        assert response.status_code == 422
