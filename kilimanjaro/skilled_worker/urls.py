from django.urls import include, path

urlpatterns = [
    path(
        "",
        include(("skilled_worker.api.urls", "skilled_worker"), "skilled_worker_api"),
    )
]
