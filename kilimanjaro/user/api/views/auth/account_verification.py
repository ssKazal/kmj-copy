from django.db.models import Q
from rest_framework import permissions, viewsets
from rest_framework.decorators import action
from rest_framework.response import Response

from core.utils import send_verification_credential
from user.models import AccountVerificationRequest


class AccountVerificationRequestViewset(viewsets.ViewSet):
    """A class to do verification related task

    Methods
    -------
    send_verification_key():
        Sends verification related info to User and retruns response
    verify_account():
        Updates user's verification status and retruns response
    """

    def get_permissions(self):
        """Instantiates and returns the list of permissions that this view requires."""

        permission_classes = []
        if self.action == "send_verification_key":
            permission_classes = [permissions.IsAuthenticated]

        return [permission() for permission in permission_classes]

    @action(detail=False, methods=["POST"])
    def send_verification_key(self, request):
        """Sends verification related info to User and retruns str or error response"""

        email = None
        phone_number = None

        if request.user.phone_number and not request.user.is_phone_number_verified:
            phone_number = request.user.phone_number.raw_input
        elif request.user.email and not request.user.is_email_verified:
            email = request.user.email

        if not (email or phone_number):
            return Response({"message": "Something went wrong"}, status=422)

        data_dict = {
            "request_for": "account_verification",
            "user_obj": request.user,
        }  # Account verification related info

        if email:
            data_dict.update(email=email)
        else:
            data_dict.update(phone_number=phone_number)

        response_message = send_verification_credential(
            **data_dict
        )  # Custom function to send account verification info to 'user'

        return Response({"message": response_message}, status=200)

    @action(detail=False, methods=["POST"])
    def verify_account(self, request):
        """Updates user's verification status and retruns success or error response"""

        verification_key = request.data.get("verification_key")
        if not verification_key:
            return Response({"message": "Please insert verification token"}, status=422)

        # Making query parameter first to make the query looks short
        requested_with_phone = Q(verify_by="phone") & Q(token=f"p-{verification_key}")
        requested_with_email = Q(verify_by="email") & Q(token=f"e-{verification_key}")

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

        if request_obj:
            user = request_obj.user
            if request_obj.verify_by == "email":
                user.is_email_verified = True
            else:
                user.is_phone_number_verified = True
            user.save()
            request_obj.is_used = True
            request_obj.save()
            data = {"message": "Success! Your account is verified"}
            return Response(data, status=200)

        data = {"message": "Token already used or invalid"}

        return Response(data, status=422)
