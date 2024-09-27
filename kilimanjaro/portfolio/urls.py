from django.urls import include, path

urlpatterns = [path("", include(("portfolio.api.urls", "portfolio"), "portfolio_api"))]
