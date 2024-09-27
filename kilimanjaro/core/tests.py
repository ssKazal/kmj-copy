from unittest.mock import patch

import pytest
from django.test.utils import override_settings

from core.tasks import send_email, send_sms
from core.utils.general_func import send_mail_for_task, send_sms_for_task


@pytest.mark.usefixtures("celery_session_app")
@pytest.mark.usefixtures("celery_session_worker")
class TestCeleryWorker:
    @patch("core.utils.general_func.send_mail_for_task")
    def test_email_send_worker(self, mock_send):
        subject = "Kilimanjaro Forget Password Email"
        template = "email_templates/forget-password.html"
        context = {"message": "Hello this is for testing purpose"}

        send_email(subject, "test@gmail.com", template, context)

        mock_send.assert_called_with(subject, "test@gmail.com", template, context)
        assert mock_send.called == True

    @patch("core.utils.general_func.send_sms_for_task")
    def test_sms_send_worker(self, sms_send_mock):
        send_sms("+8801711223344", "This is only for testing purposes")

        sms_send_mock.assert_called_with(
            "+8801711223344", "This is only for testing purposes"
        )
        assert sms_send_mock.called == True


class TestGeneralFunction:
    @override_settings(EMAIL_BACKEND="django.core.mail.backends.smtp.EmailBackend")
    def test_email_send_function(self):
        subject = "Kilimanjaro Forget Password Email"
        template = "email_templates/forget-password.html"
        context = {"message": "Hello this is for testing purpose"}

        res = send_mail_for_task(subject, "test@gmail.com", template, context)
        assert res == True

    @override_settings(EMAIL_BACKEND="django.core.mail.backends.smtp.EmailBacken")
    def test_email_send_function_with_invalid_email_backend(self):
        subject = ""
        template = "email_templates/forget-password.html"
        context = {"message": "Hello this is for testing purpose"}

        res = send_mail_for_task(subject, "test@gmail.com", template, context)
        assert res == False

    @override_settings(EMAIL_BACKEND="django.core.mail.backends.smtp.EmailBackend")
    @override_settings(EMAIL_HOST="invlaid")
    def test_email_send_function_with_invalid_host(self):
        subject = "hello world"
        template = "email_templates/forget-password.html"
        context = {"message": "Hello this is for testing purpose"}

        res = send_mail_for_task(subject, "test@gmail.com", template, context)
        assert res == False

    @override_settings(EMAIL_BACKEND="django.core.mail.backends.smtp.EmailBackend")
    @override_settings(EMAIL_PORT=6568)
    def test_email_send_function_with_invalid_port(self):
        subject = "New header"
        template = "email_templates/forget-password.html"
        context = {"message": "Hello this is for testing purpose"}

        res = send_mail_for_task(subject, "test@gmail.com", template, context)
        assert res == False

    @override_settings(EMAIL_BACKEND="django.core.mail.backends.smtp.EmailBackend")
    def test_email_send_function_with_invalid_header(self):
        subject = "bad header \n"
        template = "email_templates/forget-password.html"
        context = {"message": "Hello this is for testing purpose"}

        res = send_mail_for_task(subject, "test@gmail.com", template, context)
        assert res == False

    @override_settings(EMAIL_BACKEND="django.core.mail.backends.smtp.EmailBackend")
    @override_settings(EMAIL_HOST_PASSWORD="t3st")
    def test_email_send_function_with_invalid_wrong_password(self):
        subject = "New header"
        template = "email_templates/forget-password.html"
        context = {"message": "Hello this is for testing purpose"}

        res = send_mail_for_task(subject, "test@gmail.com", template, context)
        assert res == False

    def test_sms_send_worker(sell):
        res = send_sms_for_task("+8801750490667", "This is only for testing purposes")
        assert res == True

    def test_sms_send_worker_with_wrong_number(sell):
        res = send_sms_for_task("+880175049067", "This is only for testing purposes")
        assert res == False
