"""This file contains custom logging middleware"""

import json
import logging
import os
from pathlib import Path

from django.conf import settings
from django.http.request import QueryDict
from django.utils.deprecation import MiddlewareMixin

from core.utils.custom_modules import KJMJsonEncoder
from core.utils.general_data import sensitive_fields
from core.utils.general_func import convert_form_data_to_dict_data

logger = logging.getLogger('request_track')

# Tracking every request with it's response and save those data to logs
class LoggingMiddleware(MiddlewareMixin):
    def process_request(self, request):

        """taking the request body and check sensitive information, if sensitive information then change the value
        with dummy value to save in file"""

        if request.method == "GET":
            request_data = getattr(
                request, "_body", request.GET
            )  # Grabbing request body

            # Converting binary formatted request.body into json and pass it into another field of 'request'
            self._initial_http_body = json.dumps(request_data)
        else:
            request_data = getattr(
                request, "_body", request.body
            )  # Grabbing request body
            request_data = request_data.decode(
                "utf-8", errors="ignore"
            )  # Decode the request body

            if request.content_type == "multipart/form-data":

                # converting request body into dict
                request_data = convert_form_data_to_dict_data(
                    request.META, request, request.upload_handlers, request._encoding
                )

            if request.content_type == "application/x-www-form-urlencoded":

                # converting urlencoded request data into dict
                request_data = QueryDict(
                    request.read(), encoding=request._encoding, mutable=True
                )

            if request.content_type == "application/json":
                request_data = json.loads(
                    request_data
                )  # Converting binary formatted request.body to json

            # Setting dummy value for sensitive info
            if isinstance(request_data, (QueryDict, dict)):
                if (
                    request.path in sensitive_fields.keys()
                ):  # Checking if this request.path contains any sensitive info
                    for field in sensitive_fields.get(
                        request.path, []
                    ):  # Search sensitive key
                        if request_data.get(field, None):
                            request_data[field] = ["***secret"]  # set dummy value

                elif request.path.startswith(
                    "/admin/user/user/"
                ) and request.path.endswith(
                    "/password/"
                ):  # When password update from admin panel
                    request_data["password1"] = ["***secret"]  # set dummy value
                    request_data["password2"] = ["***secret"]  # set dummy value

            # Passing request body into another field of 'request'
            self._initial_http_body = json.dumps(request_data, cls=KJMJsonEncoder)

    def process_response(self, request, response):
        """Saveing request and response data into file"""

        if request.path.startswith(
            settings.MEDIA_URL
        ):  # when media url then no log will be creating
            return response

        """While data is uploading from the admin panel then checking request.data type.
        If the data-type doesn't match with what kilimanjaro support then exception will raise"""
        if (
            not request.method == "GET"
            and not request.path.startswith("/admin")
            and request.content_type
            and request.content_type
            not in [
                "multipart/form-data",
                "application/x-www-form-urlencoded",
                "application/json",
                "*/*",
            ]
        ):
            response.status_code = 415
            user_dict = {
                "detail": f"Unsupported media type {request.content_type} in request."
            }  # Error response message
            user_encode_data = json.dumps(user_dict).encode(
                "utf-8"
            )  # Converting into json
            response.content = user_encode_data

        # Adds extra data to logs 
        extra = {
            "log_data": {
                "data": {
                    "user": request.user.id if request.user else None,
                    "content": self._initial_http_body,  # Grabbing the request body
                }
            },
            "request_data": {
                "status": response.status_code, 
                "data": response.content
            }
        }

        # Set logger response level, log formatter and logging level
        if str(response.status_code).startswith("5") or str(
            response.status_code
        ).startswith(
            "4"
        ):  
            logger.error("Exception happened", extra=extra)
        else:
            logger.info("Info", extra=extra)

        return response

