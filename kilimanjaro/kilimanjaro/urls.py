from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import include, path
from rest_framework_simplejwt import views as jwt_views

from user.api.views import MyTokenObtainPairView
from user.views import admin_user_login


urlpatterns = [
    path("admin/", admin.site.urls),
    path("user/", include(("user.api.urls", "user"), namespace="user")),
    path(
        "notifications/",
        include(("notification.urls", "notification"), namespace="notification"),
    ),
    path(
        "contact-us/",
        include(("contact_us.urls", "contact_us"), namespace="contact_us"),
    ),
    path(
        "certifications/",
        include(("certification.urls", "certification"), namespace="certification"),
    ),
    path(
        "portfolios/", include(("portfolio.urls", "portfolio"), namespace="portfolio")
    ),
    path("favorites/", include(("favorite.urls", "favorite"), namespace="favorite")),
    path(
        "skilledworkers/",
        include(("skilled_worker.urls", "skilled_worker"), namespace="skilled_worker"),
    ),
    path("admin-login/", admin_user_login, name="admin-user-login"),
    # jwt auth
    path("api/login/", MyTokenObtainPairView.as_view(), name="token_obtain_pair"),
    path(
        "api/token/refresh_token/", jwt_views.TokenRefreshView.as_view(), name="token_refresh"
    ),
    path("api/token/verify/", jwt_views.TokenVerifyView.as_view(), name="token_verify"),
    path("chat/", include(("chat.api.urls", "chat"), namespace="chat")),
    path("core/", include(("core.urls", "core"), namespace="core")),
]

if settings.DEBUG:
    import debug_toolbar

    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns += (path("__debug__/", include(debug_toolbar.urls)),)


admin.site.site_header = "GigUp Admin"
admin.site.site_title = "GigUp Admin"
admin.site.index_title = ""  # for remove index title
