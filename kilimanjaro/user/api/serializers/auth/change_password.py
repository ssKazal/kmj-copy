from typing import Type

from django.contrib.auth.password_validation import validate_password
from django.core.exceptions import ValidationError
from rest_framework import serializers

from user.models import User


class PasswordChangeSerializer(serializers.Serializer):
    """Password change related task happens here

    Methods
    -------
    set_user_password(user_obj=User, new_password=""):
        Updates User password and returns User
    """

    # Custom fields to insert data
    old_password = serializers.CharField(
        required=False, allow_blank=True, style={"input_type": "password"}
    )
    new_password = serializers.CharField(
        required=False, allow_blank=True, style={"input_type": "password"}
    )
    confirm_new_password = serializers.CharField(
        required=False, allow_blank=True, style={"input_type": "password"}
    )

    def validate(self, attrs):
        user_obj = self.context["user"]
        old_password = attrs.get("old_password", None)

        errors_list = {}  # Error message will append here

        if not old_password:
            errors_list.update({"old_password": ["Enter your current password"]})

        if old_password and not user_obj.check_password(
            old_password
        ):  # Checking old password
            errors_list.update({"old_password": ["Password is incorrect"]})

        new_password = attrs.get("new_password", None)
        confirm_new_password = attrs.get("confirm_new_password", None)

        if not new_password:
            errors_list.update({"new_password": ["Enter a new password"]})

        if not confirm_new_password:
            errors_list.update({"confirm_new_password": ["Re-enter new password"]})

        if (
            new_password
            and confirm_new_password
            and new_password != confirm_new_password
        ):
            errors_list.update({"non_field_error": ["Password doesn't match"]})

        if user_obj and new_password:
            try:
                validate_password(
                    new_password, user_obj
                )  # Checking password validation
            except ValidationError as e:
                errors_list.update({"password": e.messages})

        if errors_list:
            raise serializers.ValidationError(errors_list)

        return attrs

    def set_user_password(self, user_obj: Type[User], new_password: str) -> User:
        """
        Updates User password and returns User

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
