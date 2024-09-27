"""File contains custom authentication backend"""

from typing import Optional

from django.contrib.auth.backends import BaseBackend
from django.db.models import Q

from user.models import User


class CustomAuthBackend(BaseBackend):
    """Makes a User login

    Methods
    -------
    authenticate(email="", password=""):
        Returns "user" if exist
    """

    supports_object_permissions = False
    supports_anonymous_user = False
    supports_inactive_user = False

    def authenticate(
        self, request, email: Optional[str] = None, password: Optional[str] = None
    ) -> User:
        """
        Returns "user" if exist

        If the arguments "email" and "password" is passed, then it check user "email" and "phone number" verification status.
        If verified then check password and return "user"

        Parameters
        ----------
        email : str, optional
            default is None
        password : str, optional
            default is None

        Returns
        -------
        User
        """

        user_id = email  # 'email' can be 'email address/phone number'

        try:
            user = User.objects.get(
                Q(email__iexact=user_id) | Q(phone_number__iexact=user_id)
            )

            can_access = False

            if request.path and request.path.startswith("/admin"):
                if "@" in user_id:
                    can_access = True
            else:
                if not user.is_email_verified and not user.is_phone_number_verified:
                    can_access = True
                elif "@" in user_id and user.is_email_verified:
                    can_access = True
                elif user_id.startswith("+") and user.is_phone_number_verified:
                    can_access = True

            if can_access and user.check_password(password):
                return user

            else:
                return None

        except User.DoesNotExist:
            return None
