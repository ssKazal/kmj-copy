from django.urls import include, path
from rest_framework import routers

from skilled_worker.api.views import SkillWorkerViewset

router = routers.DefaultRouter()
router.register(r"", SkillWorkerViewset, basename="skilledworkers")

urlpatterns = [
    path("", include((router.urls, "skilled_worker"), namespace="skilled_worker")),
]
