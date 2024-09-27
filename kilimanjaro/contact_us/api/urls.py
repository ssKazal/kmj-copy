from django.urls import include, path
from rest_framework import routers

from contact_us.api.views import ContactUsViewset

router = routers.DefaultRouter()

router.register(r"", ContactUsViewset, basename="contact_us")


urlpatterns = [path("", include((router.urls, "contact_us"), namespace="contact_us"))]
