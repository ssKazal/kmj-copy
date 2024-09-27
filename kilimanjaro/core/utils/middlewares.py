"""This file contains some custom middlewares"""
from os import closerange

from django.conf import settings
from django.core.cache import cache
from django.core.cache.backends.base import DEFAULT_TIMEOUT
from django.http import JsonResponse
from django.shortcuts import reverse
from django.test import client
from django.utils.deprecation import MiddlewareMixin
from rest_framework import status

from core.models import ClientAPIKey
from core.utils.general_data import (
    ALLOWED_PATHS_WITH_EXTENSION_WITHOUT_CLIENT_API_KEY,
    ALLOWED_PATHS_WITHOUT_CLIENT_API_KEY)

CACHE_TTL = getattr(settings, "CACHE_TTL", DEFAULT_TIMEOUT)


class ForceAccountVerification(MiddlewareMixin):
    """Checks non-staff 'user' 'email'/'phone' verification status, depending on
    verification status they get response or error response
    """

    def process_response(self, request, response):
        user = request.user

        if not user.is_authenticated:
            return response

        if (
            user.is_superuser
            or user.is_staff
            or user.is_email_verified
            or user.is_phone_number_verified
        ):
            return response 

        current_path = request.META["PATH_INFO"]  # current request path
        account_verify_url = reverse("user:verify_account")
        send_verification_key_url = reverse("user:send_verification_key")

        # accessible url path for unverified(email/phone) 'user'
        valid_urls = [
            account_verify_url,
            send_verification_key_url,
        ]

        if current_path in valid_urls:
            return response

        # Response data for unverified 'user'
        data = {
            "is_account_verified": False,
            "message": "Verify your phone number or email",
        }

        return JsonResponse(data, status=status.HTTP_428_PRECONDITION_REQUIRED)


class ClientAPIVerification(MiddlewareMixin):
    """Client API key verification"""

    def process_response(self, request, response):

        client_api_key = request.META.get('HTTP_CLIENTAPIKEY') # getting client api keys from headers
        current_path = request.META["PATH_INFO"] # current request path

        # gets api keys from cache
        client_api_list = cache.get("client_api_keys")

        # when api keys is not exists into cache
        if client_api_list == None or len(client_api_list) == 0:
            client_api_list = ClientAPIKey.objects.filter(is_active=True).values_list(
                "api_key", flat=True
            )

            # set api keys to cache
            cache.set("client_api_keys", client_api_list, timeout=CACHE_TTL)

        # List of url path for which is not required client api key
        allowed_path = (
            current_path in ALLOWED_PATHS_WITHOUT_CLIENT_API_KEY
            or len(
                [
                    path
                    for path in ALLOWED_PATHS_WITH_EXTENSION_WITHOUT_CLIENT_API_KEY
                    if current_path.startswith(path)
                ]
            )
            > 0
        )

        # when provided an invalid key, won't get response
        if client_api_key not in client_api_list and not allowed_path:
            return JsonResponse(
                data={"message": "Invalid Client API"},
                status=status.HTTP_406_NOT_ACCEPTABLE,
            )

        return response
