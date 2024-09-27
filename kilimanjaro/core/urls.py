from django.urls import path
from core.views import client_api


urlpatterns = [
    path("client-api/", client_api, name="client_api")
]


