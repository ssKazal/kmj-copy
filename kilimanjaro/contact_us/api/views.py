from rest_framework import permissions, viewsets

from contact_us.api.serializers import ContactUsSerializer


class ContactUsViewset(viewsets.ModelViewSet):
    serializer_class = ContactUsSerializer
    permission_classes = [permissions.IsAuthenticated]
    http_method_names = ["post"]
