from django.shortcuts import redirect
from django.contrib.auth.decorators import login_required

from core.models import ClientAPIKey

@login_required
def client_api(request):
    if request.user.is_superuser:
        ClientAPIKey.objects.create(is_active=True)
    return redirect("/admin/core/clientapikey")
