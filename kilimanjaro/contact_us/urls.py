from django.urls import include, path

urlpatterns = [
    path("", include(("contact_us.api.urls", "contact_us"), "contact_us_api"))
]
