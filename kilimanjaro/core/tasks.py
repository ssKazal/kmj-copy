"""Contains celery task"""
from collections.abc import Callable

from core.utils import general_func
from kilimanjaro.celery import app


@app.task(name="send_email")
def send_email(
    subject: str, to_email: str, template: str, context: Callable[dict, dict[str, str]]
) -> None:
    """
    Sending email using celery and save logs in file

        Parameters:
            subject (str) : The title of email content
            to_email (str) : Receiver email address
            template (str) : Format of email template
            context (dict) : Dict for use as template dynamic key value

        Returns:
            None
    """
    general_func.send_mail_for_task(subject, to_email, template, context)


@app.task(name="send_sms")
def send_sms(recipient_number: str, message: str) -> bool:
    """
    Sending SMS using celery and save logs in file

        Parameters:
            recipient_number (str) : Receiver phone number
            message (str) : Text message

        Returns:
            None
    """
    general_func.send_sms_for_task(recipient_number, message)
