from django.urls import include, path
from rest_framework import routers

from favorite.api.views import FavoriteViewset

router = routers.DefaultRouter()
router.register(r"", FavoriteViewset, basename="favorites")


urlpatterns = [path("", include((router.urls, "favorite"), namespace="favorite"))]
