from django.urls import include, path
from rest_framework import routers

from user.api.views import (AccountVerificationRequestViewset,
                            ResetPasswordViewset, UserRegistrationViewset,
                            UserViewset)

send_verification_key = AccountVerificationRequestViewset.as_view(
    {"post": "send_verification_key"}
)
verify_account = AccountVerificationRequestViewset.as_view({"post": "verify_account"})
reset_password_request = ResetPasswordViewset.as_view(
    {"post": "reset_password_request"}
)
reset_password = ResetPasswordViewset.as_view({"post": "reset_password"})

router = routers.DefaultRouter()
router.register(
    r"registration", UserRegistrationViewset, basename="user_registration"
)
router.register(r"", UserViewset, basename="users")


urlpatterns = [
    path(
        "send-verification-key/",
        send_verification_key,
        name="send_verification_key",
    ),
    path("verify-account/", verify_account, name="verify_account"),
    path(
        "reset-password-request/",
        reset_password_request,
        name="reset_password_request",
    ),
    path("reset-password/", reset_password, name="reset_password"),
    path("", include((router.urls, "user"), namespace="user")),
]
