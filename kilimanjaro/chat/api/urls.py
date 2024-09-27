from django.urls import include, path
from rest_framework import routers
from chat.api.views import ChatRoomViewset, ChatMessageViewset, user_and_partner_single_room_info

router = routers.DefaultRouter()
router.register(r"rooms", ChatRoomViewset, basename="chats")
router.register(r"messages", ChatMessageViewset, basename="chats")


urlpatterns = [
    path("", include((router.urls, "chat"), namespace="chat")),
    path("k/<str:room_partner_username>/", user_and_partner_single_room_info, name="user_and_partner_single_room_info")
]
