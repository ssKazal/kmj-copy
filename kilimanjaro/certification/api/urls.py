from django.urls import include, path
from rest_framework import routers

from certification.api.views import CertificationViewset

router = routers.DefaultRouter()

router.register(r"", CertificationViewset, basename="certifications")


urlpatterns = [
    path("", include((router.urls, "certification"), namespace="certification")),
]
