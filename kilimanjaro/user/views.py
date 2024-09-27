from django.contrib import auth, messages
from django.shortcuts import redirect


def admin_user_login(request):
    """To login into admin pannel"""
    if request.method == "POST":
        user_id = request.POST.get("user_id")
        password = request.POST.get("password")

        user = auth.authenticate(request, email=user_id, password=password)

        if user and user.is_staff:
            auth.login(request, user)
            return redirect("/admin")

    messages.error(request, "Invalid Email or Password.")
    return redirect("/admin")
