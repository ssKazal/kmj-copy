"""Custom functions, that will be used multiple places of this projects."""

import logging
import os
import random
import smtplib
import sys
import socket
from collections.abc import Callable
from datetime import datetime
from io import BytesIO
from typing import Optional, Type

import requests 
from asgiref.sync import async_to_sync
from channels.layers import get_channel_layer
from django.apps import apps
from django.conf import settings
from django.core.exceptions import ValidationError
from django.core.files import File
from django.core.mail import BadHeaderError, EmailMultiAlternatives
from django.http.multipartparser import \
    MultiPartParser as DjangoMultiPartParser
from django.http.request import MultiValueDict, QueryDict
from django.template.loader import render_to_string
from django.test.client import RequestFactory
from django.utils.html import format_html
from hashids import Hashids
from PIL import Image
from rest_framework_simplejwt.tokens import RefreshToken
from django.core.files.storage import FileSystemStorage
from django.core.files.uploadedfile import InMemoryUploadedFile

from core.tasks import send_email, send_sms
from core.utils.general_data import ORDER_CREATE_MSG, ORDER_UPDATE_MSG

import base64
from django.core.files.base import ContentFile


# Can't import 'User' from 'user.models', because of circular import issue
User = (
    settings.AUTH_USER_MODEL
)

# logger
notification_logger = logging.getLogger('notification')
email_send_logger = logging.getLogger('email_send')
sms_send_logger = logging.getLogger('sms_send')


def generate_uids():
    """Returns an unique ID"""

    now = datetime.now()
    timestamp = datetime.timestamp(now)
    n1 = random.randint(10000, 1000000)  # Generates random number for Hasids salt
    hashids = Hashids(
        salt="{}{}".format(n1, timestamp)
    )  # Generates Hashids salt from current time & random number
    n2 = random.randint(1, 9999)  # Generating random number for Hasids encode
    ids = hashids.encode(5, 5, 5, n2)  # Generates hash id
    return ids


def generate_random_number():
    """Returns 'six' digit random number"""

    number = random.randint(100000, 999999)
    return number


def get_tokens_for_user(user: Type[User]) -> dict[str, str]:
    """Takes a user object and returns that user's JWT Tokens(refresh & access) as dict"""

    jwt_token = RefreshToken.for_user(user)
    return {"refresh": str(jwt_token), "access": str(jwt_token.access_token)}


def email_send(email_type: str, to_email: str, link: str) -> None:
    """Sends email using celery

    :param email_type: Subject of the email
    :param to_email: Receiver's email address
    :param link: Verfication link
    :return: None
    """

    if email_type == "account_verification":
        subject = "Kilimanjaro Account Verification"
        template = "email_templates/email-verification.html"
    elif email_type == "forget_password":
        subject = "Kilimanjaro Forget Password Email"
        template = "email_templates/forget-password.html"

    context = {"link": link}
    send_email.delay(
        subject=subject, to_email=to_email, template=template, context=context
    )
 

def send_verification_credential(
    request_for: str,
    user_obj: Type[User],
    email: Optional[str] = None,
    phone_number: Optional[int] = None,
) -> str:
    """Depending on "request_for" value an email/sms will send and returns an HTTP response

    :param request_for: Reason of the email/sms send
    :param user_obj: User object
    :param email: Optional[str]
    :param email: Optional[int]
    :returns: HTTP response
    """

    token = generate_random_number()  # Generating 6-digit number
    message = ""
    response_message = ""
    link = ""

    AccountVerificationRequest = apps.get_model("user.AccountVerificationRequest")
    ResetPasswordRequest = apps.get_model("user.ResetPasswordRequest")

    if request_for == "account_verification":
        message = f"Kilimanjaro account verification token: {token}"  # Account verification sms message
        link = f"{settings.FRONT_END_DOMAIN}{settings.FRONT_END_ACC_VERIFICATION_URL}/{token}/"  # Account verification email link "<frontend_host:port>/<path>/<token>/"

    elif request_for == "forget_password":
        message = f"Your password reset verification token: {token}"  # Password reset sms message
        link = f"{settings.FRONT_END_DOMAIN}{settings.FRONT_END_RESET_PASSWORD_URL}/{token}/"  # Password reset email link "<frontend_host:port>/<path>/<token>/"

    if email:
        email_will_send = False

        if request_for == "account_verification":

            # creating 'account verification request' instance
            account_verification_request = AccountVerificationRequest(
                user=user_obj, verify_by="email", token=f"e-{token}"
            )
            try:
                account_verification_request.full_clean()  # Checking model's validation
                account_verification_request.save()
                email_will_send = True
                response_message = (
                    "We have sent a verification related info to your email."
                )
            except ValidationError as e:
                response_message = e.messages[0]

        elif request_for == "forget_password":

            # creating 'forget password' instance
            reset_password_request = ResetPasswordRequest(
                user=user_obj, requested_with="email", token=f"e-{token}"
            )

            try:
                reset_password_request.full_clean()  # Checking model's validation
                reset_password_request.save()
                email_will_send = True
                response_message = (
                    "Success! we've sent password change related info to your email"
                )
            except ValidationError as e:
                response_message = e.messages[0]

        # Sending email using celery
        if email_will_send:
            email_send(email_type=request_for, to_email=email, link=link)


    else:
        sms_will_send = False

        if request_for == "account_verification":

            # creating 'account_verification_request' instance
            account_verification_request = AccountVerificationRequest(
                user=user_obj, verify_by="phone", token=f"p-{token}"
            )

            try:
                account_verification_request.full_clean()  # Checking model's validation
                account_verification_request.save()
                sms_will_send = True
                response_message = "We have sent a verification token to your phone."
            except ValidationError as e:
                response_message = e.messages[0]

        elif request_for == "forget_password":

            # creating 'forget password' instance
            reset_password_request = ResetPasswordRequest(
                user=user_obj, requested_with="phone", token=f"p-{token}"
            )

            try:
                reset_password_request.full_clean()  # Checking model's validation
                reset_password_request.save()
                sms_will_send = True
                response_message = (
                    "Success! we've sent password change related info to your phone"
                )
            except ValidationError as e:
                response_message = e.messages[0]

        # Sending sms using celery
        if sms_will_send:
            send_sms.delay(recipient_number=phone_number, message=message)

    return response_message


def send_notification(
    user_id,
    first_name: Optional[str] = None,
    last_name: Optional[str] = None,
    notification_for: Optional[str] = None,
) -> None:
    """Sends notification to channel layer
    :param first_name: Optional[str]
    :param last_name: Optional[str]
    :param notification_for: Optional[str]
    """

    if notification_for == "order_create":
        message = ORDER_CREATE_MSG.format(
            first_name="first_name", last_name="last_name"
        )
    else:
        message = ORDER_UPDATE_MSG.format(
            first_name="first_name", last_name="last_name"
        )

    extra = {}  # Adding custom key & value for logging formatter
    response_dict = {}
    exception_happen = False

    # Sending notification to channel layer
    try:
        async_to_sync(get_channel_layer().group_send)(
            f"notification_room_{user_id}",
            {
                "type": "message.notification",
                "message": message,
            },
        )
        response_dict.update({"Success": "Notification send successfully"})
    except ConnectionRefusedError:  # when redis server doesn't exists
        exception_happen = True
        response_dict.update(
            {"ConnectionRefusedError": "Can't connect to the Redis server"}
        )
    except TimeoutError:  # Taking long time to send
        exception_happen = True
        response_dict.update(
            {"TimeoutError": "Can't send the notification, because of time out"}
        )
    except OSError:  # Redis set-up error
        exception_happen = True
        response_dict.update({"OSError": "OS error happen"})
    except NameError:  # object related error
        exception_happen = True
        response_dict.update({"NameError": "Something is incorrect"})

    # saves log to file
    if exception_happen:
        notification_logger.info("Exception happend", extra={"response_dict": response_dict})
    else:
        notification_logger.info("Info", extra={"response_dict": response_dict})
    

def convert_form_data_to_dict_data(meta, stream, upload_handlers, encoding):
    """
    Converting form-data into dictionary

        Parameters:
            meta (obj): Request meta
            stream (obj) : Request stream
            upload_handlers (str) : Upload handlers
            encoding (str) : Encoding

        Returns:
            Dict query
    """
    parser = DjangoMultiPartParser(meta, stream, upload_handlers, encoding)
    data, files = parser.parse()

    q_dict = QueryDict("", mutable=True)
    q_dict.update(MultiValueDict(data))
    q_dict.update(files)
    return q_dict


def admin_list_page_action(buttons: list):
    """
    Custom action buttons for admin list page

        Parameters:
            buttons (list) : List of buttons

        Returns:
            Html formated buttons

        Button list demo
        [
            {
                "button_name": "Edit",
                "has_perm": request.user.has_perm("certification.change_certification"),
                "path": f"/certification/certification/{obj.id}/change",
                "background_color": "#ff3737bf"
            }
        ]
    """

    format_html_button = ""

    for button in buttons:
        if button.get("has_perm"):
            format_html_button = (
                format_html_button
                + f""" <a 
                style="margin-right: 10px; background-color: {button.get("background_color", "#ff3737bf")}; color: white!important; padding: 6px 10px 6px 10px; border-radius: 4px;" 
                class="btn" href="/admin{button.get('path', "#")}">
                {button.get("button_name")}
            </a>"""
            )

    return format_html(
        f"""
            <div style='display:flex'>
                {format_html_button}
            </div>
        """
    )


def request_factory(
    user_obj: Type[User], endpoint: str, request_type: Optional[str] = None
):
    """
    Request factory for unit testing especially serializer test

        Parameters:
            user_obj (object) : User's model object
            endpoint (str) : Endpoint of url
            request_type (str) : The type of request (post, get etc..)

        Returns:
            Request factory

    """

    factory = RequestFactory()
    content_type = "multipart/form-data; boundary=BoUnDaRyStRiNg"
    request = factory.get(endpoint, content_type=content_type)

    if request_type == "post":
        request = factory.post(endpoint, content_type=content_type)
    elif request_type == "put":
        request = factory.put(endpoint, content_type=content_type)
    elif request_type == "patch":
        request = factory.patch(endpoint, content_type=content_type)
    request.user = user_obj
    return request


def file_object(name: str):
    """
    Temporary file object creating for unit testing

        Parameters:
            name (str) : Name of file

        Returns:
            File object
    """
    file_obj = BytesIO()
    image = Image.new("RGBA", size=(100, 100), color=(155, 0, 0))
    image.save(file_obj, "png")
    file_obj.seek(0)
    return File(file_obj, name=name)


def send_mail_for_task(
    subject: str, to_email: str, template: str, context: Callable[dict, dict[str, str]]
) -> bool:
    """
    Sends email and save logs

        Parameters:
            subject (str) : The title of email content
            to_email (str) : Receiver email address
            template (str) : Format of email template
            context (dict) : Dict for use as template dynamic key value

        Returns:
            Sends status (like True or False)
    """

    from_email = settings.FROM_EMAIL
    text_content = "This is an important message."  # email content
    msg = EmailMultiAlternatives(
        subject,
        text_content,
        from_email,
        [
            to_email,  # recipient email
        ],
    )

    html_content = render_to_string(template, context)
    msg.attach_alternative(html_content, "text/html")

    extra = {
        "subject": f"'{subject}' to",
        "to_email": f"'{to_email}'",
        "reason_of_fail": "",
    }  # Adds custom key & value for logging formatter

    exception_happen = False

    try:
        msg.send()  # email send
    except smtplib.SMTPException as e:  # 'SMTP' related errors
        exception_happen = True
        extra.update({"reason_of_fail": f"'smtplib.SMTPException {e}'"})
    except BadHeaderError:  # 'Subject' in bad format
        exception_happen = True
        extra.update({"reason_of_fail": "BadHeaderError Invalid header found"})
    except TimeoutError as e:  # Wrong port
        exception_happen = True
        extra.update({"reason_of_fail": f"'TimeoutError {e.args}'"})
    except socket.gaierror as e:  # Invalid host
        exception_happen = True
        extra.update({"reason_of_fail": f"'socket.gaierror {e.args}'"})
    except:  # Error that are not usually happen
        exception_happen = True
        extra.update({"reason_of_fail": "unknown exception happen"})

    # saves log to file
    if exception_happen:
        email_send_logger.error("Exception happend", extra=extra)
    else:
        email_send_logger.error("Successfully send", extra=extra)

    return not exception_happen


def send_sms_for_task(recipient_number: str, message: str) -> bool:
    """
    Sends SMS and save logs in file

        Parameters:
            recipient_number (str) : Receiver phone number
            message (str) : Text message

        Returns:
            Sends status (like True or False)
    """

    url = f"https://api.twilio.com/2010-04-01/Accounts/{settings.TWILIO_ACCOUNT_SID}/Messages.json"  # twilio api url
    auth = (settings.TWILIO_ACCOUNT_SID, settings.TWILIO_AUTH_TOKEN)  # Twilio auth
    data = {"Body": message, "From": settings.TWILIO_NUMBER, "To": recipient_number}

    response = requests.post(url, auth=auth, data=data)  # Sms send response
    exception_happen = False

    extra = {
        "recipient_number": f"SMS to '{recipient_number}'",
        "reason_of_fail": ""
    }  # Add custom key & value for logging formatter

    # saves log to file
    if str(response.status_code).startswith("5") or str(
        response.status_code
    ).startswith("4"):
        exception_happen = True
        extra.update({"reason_of_fail": f"'{response.content}'"})
        sms_send_logger.error("Exception happend", extra=extra)
    else:
        sms_send_logger.error("Successfully send", extra=extra)
        
    return not exception_happen


def base64_to_file(data: str, name: Optional[str]=None):
    """Converts binary string to file"""

    _format, _img_str = data.split(';base64,')
    _name, ext = _format.split('/')
    if not name:
        name = _name.split(":")[-1]

    return ContentFile(base64.b64decode(_img_str), name='{}.{}'.format(name, ext))


def upload_file(file, path: str ):
    """Uploads file to django file system using django filesystem storage"""

    # generage a random file name
    random_int = generate_random_number()
    hashids = Hashids(salt=file.name)
    hashid = hashids.encode(random_int)

    server_location = os.path.join(settings.MEDIA_ROOT, path) # Where save the file

    # save the file 
    fs = FileSystemStorage(location=server_location)
    filename = fs.save(f"{hashid}{file.name}", file)

    final_file = settings.MEDIA_URL + path + filename # file path
    return final_file


def resize_image(file):
    """Reduce image size"""

    img = Image.open(file) # open image
    outputIoStream = BytesIO()
    img = img.resize((500, 500), Image.ANTIALIAS) # resize image
    img.save(outputIoStream, format='JPEG') # save resizes image
    outputIoStream.seek(0)
    uploadedImage = InMemoryUploadedFile(outputIoStream,'ImageField', file.name, 'image/jpeg', sys.getsizeof(outputIoStream), None)
    return uploadedImage

