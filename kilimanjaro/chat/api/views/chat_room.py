from rest_framework import permissions, viewsets
from django.db.models import Q, F, Max
from chat.api.pagination import ResultSetPagination
from rest_framework.decorators import action, api_view, permission_classes
from rest_framework.response import Response

from chat.api.serializers import ChatRoomSerializer, ChatBlockRoomSerializer
from chat.models import ChatRoom, ChatRoomBlockLog
from chat.api.permissions import ChatRoomPermission
from django.contrib.auth import get_user_model

User = get_user_model()


class ChatRoomViewset(viewsets.ModelViewSet):
    """ChatRoom's viewset

    Methods
    -------
        get_queryset:
            Returns chat rooms filtered by request user and ordering by last message modified date
        block_room:
            Block's chat room
        unblock_room:
            Unblock's chat room
        blocked_room_list:
            Block chat room list
    """

    serializer_class = ChatRoomSerializer
    permission_classes = [permissions.IsAuthenticated, ChatRoomPermission]
    pagination_class = ResultSetPagination
    http_method_names = ["get", "post"]

    def get_queryset(self):
        """Returns chat rooms filtered by request user and ordering by last message modified date"""

        # filter rooms and order by last room message modified date
        rooms = ChatRoom.objects.select_related('room_member_1', 'room_member_2').filter(
                    Q(room_member_1=self.request.user)|Q(room_member_2=self.request.user)
                ).annotate(
                    latest_message_date=Max(F('chatmessage__modified'))
                ).order_by(F('latest_message_date').desc(nulls_last=True))

        return rooms

    @action(detail=False, methods=["GET"], url_path='block_list')
    def blocked_chat_room_list(self, request):
        """block chat room list

        Returns:
            List of block chat room
        """
        rooms = ChatRoom.objects.filter(
                    Q(Q(room_member_1=request.user) & Q(is_blocked_by_member_1=True)) |
                    Q(Q(room_member_2=request.user) & Q(is_blocked_by_member_2=True))
                ).select_related('room_member_1', 'room_member_2')
                
        serializer = ChatBlockRoomSerializer(rooms, many=True, context={'request': request})
        return Response(serializer.data, status=200)

    @action(detail=False, methods=["POST"], url_path='block/(?P<room_id>[^/.]+)')
    def block_chat_room(self, request, room_id):
        """Blocks chat room

        Parameters:
            room_id (int): room's id
        Returns:
            Success or error response
        """
        room = ChatRoom.objects.filter(id=room_id)
        if not room:
            return Response({"message": "Chat Room not found for this room id"}, status=404)

        room = room.filter(Q(room_member_1=request.user)|Q(room_member_2=request.user)).first()
        if not room:
            return Response({"message": "You are not connected with this chat room"}, status=400)

        if request.user == room.room_member_1:
            room.is_blocked_by_member_1 = True
        elif request.user == room.room_member_2:
            room.is_blocked_by_member_2 = True

        room.save() 

        # chat room block log 
        partner = room.get_room_partner(request.user)
        chat_room_block_log, _ = ChatRoomBlockLog.objects.get_or_create(blocked_by_user=request.user, blocked_to_user=partner)
        chat_room_block_log.block_type = 'blocked'
        chat_room_block_log.save()

        return Response({"message": "Chat Room is blocked successfully."}, status=200)
        

    @action(detail=False, methods=["POST"], url_path='unblock/(?P<room_id>[^/.]+)')
    def unblock_chat_room(self, request, room_id):
        """Unblocks chat room

        Parameters:
            room_id (int): room's id
        Returns:
            Success or error response
        """

        room = ChatRoom.objects.filter(id=room_id)
        if not room:
            return Response({"message": "Chat Room not found for this room id"}, status=404)

        room = room.filter(Q(room_member_1=request.user)|Q(room_member_2=request.user)).first()
        if not room:
            return Response({"message": "You are not connected with this chat room"}, status=400)


        if request.user == room.room_member_1:
            room.is_blocked_by_member_1 = False
        elif request.user == room.room_member_2:
            room.is_blocked_by_member_2 = False

        room.save()

        # chat room block log 
        partner = room.get_room_partner(request.user)
        chat_room_block_log = ChatRoomBlockLog.objects.filter(blocked_by_user=request.user, blocked_to_user=partner).first()
        if chat_room_block_log:
            chat_room_block_log.block_type = 'unblocked'
            chat_room_block_log.save()

        return Response({"message": "Chat Room is unblocked successfully."}, status=200)


@api_view(['GET',])
@permission_classes([permissions.IsAuthenticated,])
def user_and_partner_single_room_info(request, room_partner_username):
    """Takes room partner username and return message of their corresponding room"""
    
    room_partner = User.objects.filter(username=room_partner_username).first()
    if room_partner:
        room = ChatRoom.objects.filter(
                Q(room_member_1=request.user, room_member_2=room_partner)|
                Q(room_member_1=room_partner, room_member_2=request.user)
            ).first()
        if not room and request.user.can_chat_together(room_partner):
            room = ChatRoom.objects.create(room_member_1=request.user, room_member_2=room_partner)

        room_serializer = ChatRoomSerializer(room, context={'request': request})
        return Response(room_serializer.data, status=200)
    return Response({"message": "Not found any user with this username"}, status=404)

