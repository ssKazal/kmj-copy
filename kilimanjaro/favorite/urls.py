from django.urls import include, path

urlpatterns = [path("", include(("favorite.api.urls", "favorite"), "favorite_api"))]
