from django.conf import settings
from django.core.cache import cache
from django.core.cache.backends.base import DEFAULT_TIMEOUT
from rest_framework import permissions, viewsets
from rest_framework.decorators import action
from rest_framework.response import Response

from core.utils import send_verification_credential
from customer.models import Customer
from occupation.models import Occupation
from skilled_worker.api.filters import SkilledWorkerFilterSet
from skilled_worker.models import SkilledWorker
from user.api.serializers import (PasswordChangeSerializer,
                                  UpdateProfileSerializer,
                                  UserCustomerProfileSerializer,
                                  UserSerializer,
                                  UserSkilledWorkerProfileSerializer)
from user.models import User

CACHE_TTL = getattr(settings, "CACHE_TTL", DEFAULT_TIMEOUT)


class UserViewset(viewsets.ModelViewSet):
    """User's related task

    Methods
    -------
    user_customer_profile():
        Returns user's 'customer' object serialized data
    user_skilled_worker_profile():
        Returns user's 'skilled worker' object serialized data
    change_password():
        Updates 'user' existing password
    update_profile():
        Updates 'user' data and also creates/updates user's 'skilled worker' object
    """

    serializer_class = UserSerializer
    permission_classes = [permissions.IsAuthenticated]
    filter_class = SkilledWorkerFilterSet
    http_method_names = ["get", "put", "patch"]

    def get_queryset(self):
        return User.objects.filter(id=self.request.user.id)

    @action(detail=False, methods=["GET"])
    def user_customer_profile(self, request):
        """Returns user's 'customer' object serialized data and use cache to store data"""

        customer_obj = cache.get(f"custom_profile_{request.user.id}")
        if not customer_obj:
            customer_obj = Customer.objects.filter(user__id=request.user.id).first()
            cache.set(
                f"custom_profile_{request.user.id}", customer_obj, timeout=CACHE_TTL
            )

        if customer_obj:
            serializer = UserCustomerProfileSerializer(customer_obj)
            return Response(serializer.data, status=200)
        return Response(status=422)

    @action(detail=False, methods=["GET"])
    def user_skilled_worker_profile(self, request):
        """Returns user's 'skilled worker' object serialized data and use cache to store data"""

        skilled_worker_obj = cache.get(f"skilled_worker_profile{request.user.id}")
        if not skilled_worker_obj:
            skilled_worker_obj = SkilledWorker.objects.filter(
                user__id=request.user.id
            ).first()
            if skilled_worker_obj:
                cache.set(
                    f"skilled_worker_profile{request.user.id}",
                    skilled_worker_obj,
                    timeout=CACHE_TTL,
                )

        if skilled_worker_obj:
            serializer = UserSkilledWorkerProfileSerializer(skilled_worker_obj)
            return Response(serializer.data, status=200)

        return Response(status=422)

    @action(detail=False, methods=["PUT"])
    def change_password(self, request):
        """Updates User's existing password and returns str response"""

        data = request.data
        serializer = PasswordChangeSerializer(data=data, context={"user": request.user})
        if serializer.is_valid():
            serializer.set_user_password(
                request.user, data.get("new_password")
            )  # Setting password using serializer's custom method
            return Response({"message": "Password updated successfully"}, status=200)

        return Response({"message": serializer.errors}, status=422)

    @action(detail=False, methods=["PUT", "PATCH"])
    def update_profile(self, request):
        """Updates 'user' object and also create/update user's 'skilled worker' object if data provides and returns dict response"""

        serializer = UpdateProfileSerializer(
            data=request.data, context={"request": request}
        )

        if serializer.is_valid():
            user_obj = request.user
            success_msg = {}

            if user_obj:
                data = request.data
                (occupation, description, experience,) = (
                    data.get("occupation", None),
                    data.get("description", None),
                    data.get("experience", None),
                )

                # Sends verification info using custom function if 'phone number'/'email' changed
                if user_obj.email and user_obj.email != user_obj._User__email:
                    user_obj.is_email_verified = False
                    email_change_msg = send_verification_credential(
                        request_for="account_verification",
                        user_obj=user_obj,
                        email=user_obj.email,
                    )
                    success_msg["email_change_msg"] = email_change_msg

                if (
                    user_obj.phone_number
                    and user_obj.phone_number != user_obj._User__phone_number
                ):
                    user_obj.is_phone_number_verified = False
                    phone_number_change_msg = send_verification_credential(
                        request_for="account_verification",
                        user_obj=user_obj,
                        phone_number=user_obj.phone_number.raw_input,
                    )
                    success_msg["phone_number_change_msg"] = phone_number_change_msg

                user_obj.save()

                is_account_verified = False
                if user_obj.is_email_verified or user_obj.is_phone_number_verified:
                    is_account_verified = True

                success_msg["is_account_verified"] = is_account_verified

                skilled_worker = (
                    user_obj.skilledworker
                    if hasattr(user_obj, "skilledworker")
                    else None
                )  # Grabing user 'skilled worker' instance

                if occupation and description and not skilled_worker:
                    data_dict = {
                        "user": user_obj,
                        "description": description,
                        "experience": experience,
                    }
                    data_dict["occupation_id"] = occupation
                    SkilledWorker.objects.create(**data_dict)

                if skilled_worker:
                    if occupation:
                        skilled_worker.occupation__id = int(occupation)
                    if description:
                        skilled_worker.description = description
                    if experience:
                        skilled_worker.experience

                    skilled_worker.save()

            success_msg["message"] = "Success! Your profile is updated"
            return Response(success_msg, status=200)

        return Response(serializer.errors, status=422)
