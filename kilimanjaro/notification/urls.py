from django.urls import include, path

urlpatterns = [
    path("", include(("notification.api.urls", "notification"), "notification_api"))
]
