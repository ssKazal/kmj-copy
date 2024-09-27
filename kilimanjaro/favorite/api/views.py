from rest_framework import viewsets

from favorite.api.permissions import FavoritePermission
from favorite.api.serializers import FavoriteSerializer
from favorite.models import Favorite


class FavoriteViewset(viewsets.ModelViewSet):
    serializer_class = FavoriteSerializer
    permission_classes = [FavoritePermission]
    http_method_names = ["post", "get", "put", "patch", "delete"]

    def get_queryset(self):
        return Favorite.objects.filter(customer=self.request.user.customer)
