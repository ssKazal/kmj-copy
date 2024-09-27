from rest_framework import permissions, viewsets
from django.db.models import Q, F
from chat.api.pagination import ResultSetPagination
from rest_framework.decorators import action
from rest_framework.response import Response

from chat.api.serializers import ChatMessageSerializer
from chat.models import ChatMessage, ChatRoom, ChatMessageReport
from chat.api.permissions import ChatmessagePermission


class ChatMessageViewset(viewsets.ModelViewSet):
    """ChatMessage's viewset

    Methods
    -------
        get_queryset:
            Returns chat room messages filtered by room
    """

    serializer_class = ChatMessageSerializer
    permission_classes = [permissions.IsAuthenticated, ChatmessagePermission]
    pagination_class = ResultSetPagination
    http_method_names = ["get", 'post']

    def get_queryset(self):
        """Returns chat rooms filtered by request user and ordering by last message's modified date"""

        room_id = self.request.GET.get('room_id')
        room = ChatRoom.objects.filter(id=room_id).filter(
                    Q(room_member_1=self.request.user)|Q(room_member_2=self.request.user)
                ).first()

        messages = []

        if room:
            messages = ChatMessage.objects.select_related('sender', 'receiver').filter(room=room).order_by(F('modified').desc(nulls_last=True))

        return messages

    @action(detail=False, methods=["POST"], url_path='report/(?P<message_id>[^/.]+)')
    def report_message(self, request, message_id):
        """Report a message
        
        Parameters: 
            message_id (int) : Message id

        Returns:
            Success or error response
        """
        reason = request.POST.get('reason')
        if not reason:
            return Response({"message": "Reason is required!"}, status=400)

        message = ChatMessage.objects.filter(id=message_id).first()
        if not message:
            return Response({'message': 'Message not found for this message id'}, status=404)

        if not message.receiver == request.user:
            return Response({'message': 'Your are not a receiver of this message. Only message receiver can report a message'}, status=400)

        msg_report_obj, _ = ChatMessageReport.objects.get_or_create(message=message)
        msg_report_obj.reported_by = request.user
        msg_report_obj.reason = reason
        msg_report_obj.save()
        return Response({'message': 'Success!'}, status=200)