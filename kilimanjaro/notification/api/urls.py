from django.urls import include, path
from rest_framework import routers

from notification.api.views import NotificationViewset

router = routers.DefaultRouter()
router.register(r"", NotificationViewset, basename="notifications")

urlpatterns = [
    path("", include((router.urls, "notification"), namespace="notification")),
]
