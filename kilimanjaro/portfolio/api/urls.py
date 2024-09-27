from django.urls import include, path
from rest_framework import routers

from portfolio.api.views import PortfolioImageViewset, PortfolioViewset

router = routers.DefaultRouter()
router.register(r"portfolio-image", PortfolioImageViewset, basename="portfolio_image")
router.register(r"", PortfolioViewset, basename="portfolio")

urlpatterns = [path("", include((router.urls, "portfolio"), namespace="portfolio"))]
