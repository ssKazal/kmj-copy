from typing import Type

from django.contrib.auth.password_validation import validate_password
from django.core.exceptions import ValidationError
from django.db.models import Q
from rest_framework import serializers

from user.models import ResetPasswordRequest, User


class ResetPasswordRequestSerializer(serializers.Serializer):
    """Password reset related task happens here

    Methods
    -------
    set_user_password(user_obj=User, new_password=""):
        Resets User password and returns User
    """

    # Custom fields to insert data
    verification_key = serializers.CharField(
        max_length=200, required=False, allow_blank=True
    )
    new_password = serializers.CharField(
        required=False, allow_blank=True, style={"input_type": "password"}
    )
    confirm_new_password = serializers.CharField(
        required=False, allow_blank=True, style={"input_type": "password"}
    )

    def validate(self, attrs):

        errors_list = {}  # Error message will append here
        verification_key = attrs.get("verification_key", None)
        password_change_obj = None

        if not verification_key:
            errors_list.update({"verification_key": ["Enter verification key"]})

        if verification_key:

            # Making query parameter first to make the query looks short
            requested_with_phone = Q(requested_with="phone") & Q(
                token=f"p-{verification_key}"
            )
            requested_with_email = Q(requested_with="email") & Q(
                token=f"e-{verification_key}"
            )

            password_change_obj = ResetPasswordRequest.objects.active_sms().filter(
                requested_with_phone,
                is_used=False,
            )

            if not password_change_obj:  # When previous query return None
                password_change_obj = (
                    ResetPasswordRequest.objects.active_email().filter(
                        requested_with_email,
                        is_used=False,
                    )
                )

        if verification_key and not password_change_obj:
            confirm_password_err = {
                "verification_key": ["Token is already used or invalid"]
            }
            errors_list.update(confirm_password_err)

        new_password = attrs.get("new_password", None)
        confirm_new_password = attrs.get("confirm_new_password", None)

        if not new_password:
            errors_list.update({"new_password": ["Enter new password"]})
        if not confirm_new_password:
            errors_list.update({"confirm_new_password": ["Enter confirm new password"]})

        if (
            new_password
            and confirm_new_password
            and new_password != confirm_new_password
        ):
            password_not_match_err = {"non_field_error": ["Password doesn't match"]}
            errors_list.update(password_not_match_err)

        if password_change_obj and new_password:
            try:
                validate_password(
                    new_password, password_change_obj.first().user
                )  # Checking password validation
            except ValidationError as e:
                password_err = {"new_password": e.messages}
                errors_list.update(password_err)

        if errors_list:
            raise serializers.ValidationError(errors_list)

        return attrs

    def set_user_password(self, user_obj: Type[User], new_password: str) -> User:
        """
        Resets User password and returns User

        If the arguments "user_obj" and "new_password" is passed, then sets 'new_password' as user's password.

        Parameters
        ----------
        user_obj : User
            A User object
        new_password : str

        Returns
        -------
        None
        """

        user_obj.set_password(new_password)
        user_obj.save()
        return user_obj
