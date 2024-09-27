from django.db.models import Q
from rest_framework import viewsets
from rest_framework.decorators import action
from rest_framework.response import Response

from core.utils import send_verification_credential
from user.api.serializers import ResetPasswordRequestSerializer
from user.models import ResetPasswordRequest, User


class ResetPasswordViewset(viewsets.ViewSet):
    """A class to do reset password related task

    Methods
    -------
    reset_password_request():
        Sends reset password related info to User and retruns response
    reset_password():
        Resets User password and retruns response
    """

    @action(detail=False, methods=["POST"])
    def reset_password_request(self, request):
        """Sends reset password related info to User and retruns response
        Checks requested "email"/"phone number". If they are valid then sends vefification realted info to that "email"/"phone_number".
        Unless returns error response
        """

        email = request.data.get("email", None)
        phone_number = request.data.get("phone_number", None)
        user_obj = None

        if not (email or phone_number):
            return Response(
                {"message": "Please enter your email/phone number"}, status=422
            )

        user_id = {}  # 'user' data will append here

        if email:
            user_id = {"email__exact": email}
        else:
            user_id = {"phone_number__exact": phone_number}

        user_obj = User.objects.filter(**user_id).first()

        if not user_obj:
            return Response(
                {"message": "Email or phone number doesn't exists."}, status=422
            )

        data_dict = {"request_for": "forget_password", "user_obj": user_obj}

        if email:
            data_dict.update(email=email)
        else:
            data_dict.update(phone_number=phone_number)

        response_message = send_verification_credential(
            **data_dict
        )  # Custom functon to send 'forget password' info to user

        return Response({"message": response_message})

    @action(detail=False, methods=["POST"])
    def reset_password(self, request):
        """Resets User password and retruns response
        Takes requested "verifiacation_key" and get that User. Then resets that user password.
        Unless returns error response
        """

        serializer = ResetPasswordRequestSerializer(
            data=request.data, context={"request": request}
        )

        if serializer.is_valid():
            verification_key = request.data["verification_key"]
            requested_with_phone = Q(requested_with="phone") & Q(
                token=f"p-{verification_key}"
            )
            requested_with_email = Q(requested_with="email") & Q(
                token=f"e-{verification_key}"
            )

            request_obj = ResetPasswordRequest.objects.filter(
                Q(requested_with_phone | requested_with_email)
            ).first()
            request_obj.is_used = True
            request_obj.save()

            serializer.set_user_password(request_obj.user, request.data["new_password"])
            return Response({"message": "Password has been updated successfully"})

        return Response(serializer.errors, status=422)
