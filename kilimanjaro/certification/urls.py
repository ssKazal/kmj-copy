from django.urls import include, path

urlpatterns = [
    path(
        "",
        include(("certification.api.urls", "certification"), "certification_api"),
    )
]
