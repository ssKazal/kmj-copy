from rest_framework import viewsets

from portfolio.api.permissions import PortfolioImagePermission
from portfolio.api.serializers import PortfolioImageSerializer
from portfolio.models import PortfolioImage


class PortfolioImageViewset(viewsets.ModelViewSet):
    serializer_class = PortfolioImageSerializer
    permission_classes = [PortfolioImagePermission]
    http_method_names = ["post", "get", "put", "patch", "delete"]

    def get_queryset(self):
        return PortfolioImage.objects.filter(
            portfolio__skilled_worker=self.request.user.skilledworker
        )
