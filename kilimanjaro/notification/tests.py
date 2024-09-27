import pytest
from mixer.backend.django import mixer

from core.utils.general_func import request_factory
from notification.api.serializers import NotificationSerializer
from notification.models import Notification


@pytest.mark.django_db
class TestNotification:
    endpoint = "/notifications/"

    def test_notification_mark_as_read(
        self, api_client, auth_headers, notification_obj
    ):
        response = api_client.patch(
            f"{self.endpoint}{notification_obj.id}/mark_as_read/",
            {"is_read": True},
            HTTP_AUTHORIZATION=auth_headers,
        )
        assert response.status_code == 200

    def test_notification_for_display(self, api_client, auth_headers, notification_obj):
        endpoint = f"{self.endpoint}{notification_obj.id}/"
        response = api_client.get(endpoint, HTTP_AUTHORIZATION=auth_headers)

        assert response.data["notification_for_display"] == "Order Create"

    def test_notification_string_representation(self, notification_obj):
        assert notification_obj.__str__() == str(notification_obj.id)
