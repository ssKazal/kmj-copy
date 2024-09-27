from django.db.models import F
from rest_framework import viewsets
from rest_framework.decorators import action
from rest_framework.response import Response

from certification.api.serializers import CertificationSerializer
from portfolio.api.serializers import (PortfolioImageSerializer,
                                       PortfolioSerializer)
from portfolio.models import Portfolio
from skilled_worker.api.filters import SkilledWorkerFilterSet
from skilled_worker.api.serializers import UserSkilledWorkerProfileSerializer
from user.models import User


class SkillWorkerViewset(viewsets.ModelViewSet):
    """Returns SkilledWorker info to non-logged in user

    Methods
    -------
    portfolio():
        Returns SW portfolio and portfolio images
    certifications():
        Returns SW certifications
    """

    serializer_class = UserSkilledWorkerProfileSerializer
    filter_class = SkilledWorkerFilterSet
    http_method_names = ["get"]

    def get_queryset(self):

        # To get 'country_name' & 'occupation_name' is serializer
        skilled_worker_qs = User.objects.exclude(skilledworker=None).annotate(
            country_name=F("country__name"),
            occupation_name=F("skilledworker__occupation__name"),
        )
        return skilled_worker_qs

    @action(detail=True, methods=["GET"])
    def portfolio(self, request, pk=None):
        """Returns SW portfolio and portfolio images"""

        instance = self.get_object()
        instance_portfolio_obj = instance.skilledworker.portfolio
        instance_portfolio_image_qs = instance_portfolio_obj.portfolioimage_set.all()
        portfolio_serializer = PortfolioSerializer(instance_portfolio_obj)
        portfolio_img_serializer = PortfolioImageSerializer(
            instance_portfolio_image_qs, many=True
        )

        data = {
            "portfolio": portfolio_serializer.data,
            "portfolio_images": portfolio_img_serializer.data,
        }
        return Response(data, status=200)

    @action(detail=True, methods=["GET"])
    def certifications(self, request, pk=None):
        """Returns SW certifications"""

        instance = self.get_object()
        instance_certifications = instance.skilledworker.certification_set.all()
        serializer = CertificationSerializer(instance_certifications, many=True)

        return Response(serializer.data, status=200)
