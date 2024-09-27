from django.conf import settings
from django.core.cache import cache
from django.core.cache.backends.base import DEFAULT_TIMEOUT
from rest_framework import viewsets

from portfolio.api.permissions import PortfolioPermission
from portfolio.api.serializers import PortfolioSerializer
from portfolio.models import Portfolio

CACHE_TTL = getattr(settings, "CACHE_TTL", DEFAULT_TIMEOUT)


class PortfolioViewset(viewsets.ModelViewSet):
    serializer_class = PortfolioSerializer
    permission_classes = [PortfolioPermission]
    http_method_names = ["get", "put", "patch"]

    def get_queryset(self):
        portfolio_qs = cache.get(
            f"portfolio_id_{self.request.user.id}"
        )  # Checks user porfolio instance in cache

        if not portfolio_qs:
            portfolio_qs = Portfolio.objects.filter(
                skilled_worker=self.request.user.skilledworker
            )
            cache.set(
                f"portfolio_id_{self.request.user.id}", portfolio_qs, timeout=CACHE_TTL
            )  # add request.user porfolio instance in cache

        return portfolio_qs
