from rest_framework import viewsets
from rest_framework.decorators import action
from rest_framework.response import Response

from notification.api.permissions import NotificationPermission
from notification.api.serializers import NotificationSerializer
from notification.models import Notification


class NotificationViewset(viewsets.ModelViewSet):
    serializer_class = NotificationSerializer
    permission_classes = [NotificationPermission]
    http_method_names = ["get", "patch"]

    def get_queryset(self):
        return Notification.objects.filter(user=self.request.user)

    @action(
        detail=True,
        methods=[
            "PATCH",
        ],
    )
    def mark_as_read(self, request, pk=None):
        """Updates instance 'is_read' status and returns Http response"""

        instance = self.get_object()
        is_read = request.data.get("is_read", None)

        if is_read:
            instance.is_read = True
            instance.save()

        return Response({"message": "Success"}, status=200)
