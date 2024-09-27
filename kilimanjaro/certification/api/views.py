from rest_framework import viewsets

from certification.api.permissions import CertificationPermission
from certification.api.serializers import CertificationSerializer
from certification.models import Certification


class CertificationViewset(viewsets.ModelViewSet):
    serializer_class = CertificationSerializer
    permission_classes = [CertificationPermission]
    http_method_names = ["post", "get", "put", "patch", "delete"]

    def get_queryset(self):
        return Certification.objects.filter(
            skilled_worker=self.request.user.skilledworker
        )
