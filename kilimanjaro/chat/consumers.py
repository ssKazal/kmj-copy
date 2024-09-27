import asyncio
import copy
from typing import Type

from asgiref.sync import sync_to_async
import mutagen
from channels.generic.websocket import AsyncJsonWebsocketConsumer
from channels.db import database_sync_to_async
from chat.models import ChatRoom, ChatMessage, ChatMessageEditLog
from django.contrib.auth import get_user_model
from django.db.models import Q
from django.conf import settings

from core.utils.general_func import base64_to_file, upload_file, resize_image
from core.utils.general_data import MAX_FILE_SIZE_FOR_CHATTING, MAX_VOICE_DURATION_FOR_CHATTING, MAX_VOICE_MESSAGE_FOR_PER_CHATTING_ROOM, MAX_VOICE_DURATION_MIN

User = get_user_model()


class ChatConsumer(AsyncJsonWebsocketConsumer):
    """Realtime chatting consumer"""

    async def connect(self):
        """Accepts the socket connection"""
        await self.accept()
        self.room_id = None

    async def receive_json(self, content: dict[str, str]):
        """Receive json data from frontend and do some work

        Parameters:
            content (json): Json content 

        Returns:
            None
        """

        # Authentication is required
        if not self.scope["user"].is_authenticated:
            await self.send_json({
                "response_type": "Error",
                "message": "Authentication is required.",
            })
            return False

        self.user = self.scope["user"]  # request user

        command = content.get('command') # instruction like 'send_message', 'join' etc..
        room_id = content.get('room_id') # chat room id

        text_message = content.get('text_message')
        attachment_links = content.get('attachment_links')
        voice_file = content.get('voice_file')

        # Get's room from room partner id
        if command == 'send_first_message':
            partner_id = content.get('partner_id')

            # Gets room partner object 
            try:
                room_partner = await sync_to_async(User.objects.get)(id=partner_id)
            except User.DoesNotExist:
                await self.send_json({
                    "response_type": "Error",
                    "message": "Invalid Room partner ID!",
                })
                return

            room_id = await self.get_room_id_or_none(room_partner)
        
        # Gets room or return null
        room = await self.get_room_or_none(room_id)
        if not room: return
        
        # join to the room
        if command == 'join':
            await self.join_room(room)

        elif command == 'send_first_message':

            if str(self.room_id) != room_id:
                await self.join_room(room)

            # validates user can chat to another user or not
            if room_partner and not await can_chat_together(self.user, room_partner):
                await self.send_json({
                    "response_type": "Error",
                    "message": "Two skilled worker or two customer can't chat together",
                })
                return

            await self.send_chat_message(room, text_message, attachment_links, voice_file)

        elif command == 'send_message':

            # Joined room when not joined already
            if str(self.room_id) != room_id:
                await self.join_room(room)

            await self.send_chat_message(room, text_message, attachment_links, voice_file)

        elif command == 'edit_message':

            message_id = content.get('message_id') 
            # Joined room when not joined already
            if str(self.room_id) != room_id:
                await self.join_room(room)

            await self.edit_chat_message(room, text_message, message_id)

        elif command == 'delete_message':

            message_id = content.get('message_id') 
            # Joined room when not joined already
            if str(self.room_id) != room_id:
                await self.join_room(room)

            await self.delete_chat_message(room, message_id)
            

    async def disconnect(self, close_code: int) -> None:
        """Disconnect from room"""

        # leave the room
        if self.room_id != None:
            await self.leave_room(self.room_id)

    async def join_room(self, room: Type[ChatRoom]):
        """Takes room id and adds to group"""

        # adds room to the channel layer group
        await self.channel_layer.group_add(
            room.group_name,
            self.channel_name,
        )

        self.room_id = room.id

    async def leave_room(self, room_id: int):
        """Discard from room"""

        room_obj = await get_room_or_error(room_id, self.scope['user'])

        self.room_id = None

        if room_obj:
            # Remove room from channel layer group
            await self.channel_layer.group_discard(
                room_obj.group_name,
                self.channel_name
            )

    async def forward_message(self, event: dict[str, str]):
        """Formates sends message

        Parameters:
            event(dict): dict message data

        Returns:
            None
        """

        # couldn't remove unnecessary key from 'event' that's why copies from 'event' and remove unnecessary key
        newEvent = copy.deepcopy(event)
        newEvent.pop('type', None)

        # add send_by to message 
        if newEvent.get('response_type') == 'new_message':
            newEvent['send_by'] = "me" if self.user.id == newEvent['sender']['id'] else "other"

        await self.send_json(newEvent)

    async def send_chat_message(self, room: Type[ChatRoom], text_message: str, attachment_links: list, voice_file: str) -> None:
        """Takes some parameters and sends message payload"""

        if room and (room.is_blocked_by_member_1 or room.is_blocked_by_member_2):  # Checks room already block or not
            await self.send_json({
                "response_type": "Error",
                "message": "Chat Room is already blocked",
            })
            return False

        # Process attachment files
        attachment_link_list = []
        if attachment_links:
            attachment_link_list = await self.process_attachment_file(room, attachment_links)

        # process voice file
        if voice_file:
            voice_file = await self.process_voice_file(room, voice_file)

        # Sends message process
        if text_message and text_message.lstrip() or attachment_link_list or voice_file:

            # asyncio.gather for waitting on a bunch of futures and returns their results in a given order
            message = await asyncio.gather(create_chat_message(room, self.user, text_message, attachment_link_list, voice_file))

            # Adds site host to all attachment link
            attachment_links = []
            if message[0].attachment_links:
                attachment_links = [f"{settings.SITE_HOST}{link}" for link in message[0].attachment_links]
            
            # sends message to group
            await self.channel_layer.group_send(
                room.group_name,
                {
                    'type': 'forward_message',
                    'response_type': 'new_message',
                    'id': message[0].id,
                    'sender': {
                        'id': self.user.id,
                        'username': self.user.__str__(),
                        'profile_pic': self.user.profile_image
                    },
                    'send_by': "me" if self.user == message[0].sender else "other",
                    'text_message': message[0].message_text,
                    'message_type': message[0].message_type,
                    'attachment_links': attachment_links,
                    'voice': message[0].voice,
                    'created_at': {
                        "date": message[0].created.strftime("%d %b, %Y"),
                        "time": message[0].created.strftime("%I:%M %p")
                    }
                }
            )

    async def edit_chat_message(self, room: Type[ChatRoom], text_message: str, message_id: int) -> None:
        """Takes some parameters and send edit chat message payload"""

        if room and (room.is_blocked_by_member_1 or room.is_blocked_by_member_2):  # Checks room already block or not
            await self.send_json({
                "response_type": "Error",
                "message": "Chat Room is already blocked",
            })
            return

        # Sends message process
        if text_message and text_message.lstrip():

            # asyncio.gather for waitting on a bunch of futures and returns their results in a given order
            message = await asyncio.gather(update_chat_message(self.scope['user'], text_message, message_id))
            if not message[0]:
                await self.send_json({
                    "response_type": "Error",
                    "message": "Invalid message ID!",
                })
                return False

            # Adds site host to all attachment link
            attachment_links = message[0].attachment_links
            if message[0].attachment_links:
                attachment_links = [f"{settings.SITE_HOST}{link}" for link in message[0].attachment_links]

            # Notifies chat room that message is edited
            await self.channel_layer.group_send(
                room.group_name,
                {
                    'type': 'forward_message',
                    'response_type': 'edited_message',
                    'id': message[0].id,
                    'text_message': message[0].message_text,
                    'message_type': message[0].message_type,
                    'attachment_links': attachment_links,
                    'voice': message[0].voice,
                }
            )

    async def delete_chat_message(self, room: Type[ChatRoom], message_id: int):
        """Deletes chat message and notify to the room"""

        message = await asyncio.gather(delete_chat_message(self.scope['user'], room, message_id))

        if not message[0]:
            await self.send_json({
                "response_type": "Error",
                "message": "Invalid message ID!",
            })
            return

        # Notifies room that message is deleted
        await self.channel_layer.group_send(
            room.group_name,
            {
                'type': 'forward_message',
                'response_type': 'deleted_message',
                'id': message_id,
                'is_deleted': True
            }
        )

    async def process_attachment_file(self, room: Type[ChatRoom], attachment_links: list) -> list:
        """Takes attachment link list as blob and returns as file"""

        attachment_link_list = []
        for attachment_link in attachment_links:  # loop through all attachment files blob
            file = base64_to_file(attachment_link)  # convert blob to file

            if file.size > MAX_FILE_SIZE_FOR_CHATTING:
                file = resize_image(file)  # resize file

            # after resizing still file is more than MAX_FILE_SIZE_FOR_CHATTING through an error
            if file.size > MAX_FILE_SIZE_FOR_CHATTING:
                await self.send_json({
                    "response_type": "Error",
                    'message': "File is too large",
                })
            else:
                # upload file using filesystemstorage
                attachment_link_list.append(upload_file(file, f"{room.uuid}/"))

        return attachment_link_list

    async def process_voice_file(self, room: Type[ChatRoom], voice_file: list) -> list:
        """Takes voice file as blob and returns as file"""

        file = base64_to_file(voice_file)  # convert blob to file
        audio_info = mutagen.File(file).info  # reads audio file metadata

        # Verifies duration limit is cross or not
        if audio_info.length > MAX_VOICE_DURATION_FOR_CHATTING:
            await self.send_json({
                "response_type": "Error",
                "message": f"You can send only {MAX_VOICE_DURATION_MIN} minutes duration's voice",
            })
            return

        # Check's total voice message limit for per room
        total_voice_msg = await asyncio.gather(count_user_voice_chat(self.user, room))
        if  total_voice_msg[0] > MAX_VOICE_MESSAGE_FOR_PER_CHATTING_ROOM:
            await self.send_json({
                "response_type": "Error",
                "message": "You already cross your voice send limit",
            })
            return
            

        return upload_file(file, f"{room.uuid}/") # upload file to file system by filestystem storage

    async def get_room_or_none(self, room_id: int):
        room = await get_room_or_error(room_id, self.user)
        if not room:
            await self.send_json({
                "response_type": "Error",
                "message": "Invalid Room ID!",
            })
            return False
        return room

    async def get_room_id_or_none(self, partner: Type[User]):
        room_id = None
        room_obj = await asyncio.gather(get_room_or_create(partner, self.scope['user']))
        if room_obj:
            room_id = room_obj[0].id
        return room_id


@database_sync_to_async
def get_room_or_error(room_id: int, user: Type[User]) -> Type[ChatRoom]:
    """Gets room object by room id and request user

    Parameters:
        room_id (str): room object id
        user (object): request user

    Returns:
        Room object
    """
    room = ChatRoom.objects.filter(Q(room_member_1=user) | Q(
        room_member_2=user), id=room_id).select_related('room_member_1', 'room_member_2').first()

    return room

@database_sync_to_async
def get_room_or_create(room_partner: Type[User], user: Type[User]) -> Type[ChatRoom]:
    """Gets or creates a chat room

    Parameters:
        room_partner (str): user object
        user (object): request user

    Returns:
        Room object
    """

    # get or create chat room 
    room_obj = ChatRoom.objects.filter(
        Q(room_member_1=user, room_member_2=room_partner) |
        Q(room_member_1=room_partner, room_member_2=user)
    ).first()

    if not room_obj:
        room_obj = ChatRoom.objects.create(room_member_1=user, room_member_2=room_partner)

    return room_obj

@database_sync_to_async
def create_chat_message(room: Type[ChatRoom], user: Type[User], message_text: str, attachment_links: list, voice_file: str) -> Type[ChatMessage]:
    """Creates chat message object

    Parameters: 
        room (object): chat room where sends message
        user (object): message sender
        message (str): text message like 'hello'

    Returns:
        Message object
    """
    if message_text:
        message_type = "text"
    if attachment_links:
        message_type = "attachments"
    if message_text and attachment_links:
        message_type = "text_and_attachments"
    if voice_file:
        message_type = "voice"

    receiver = room.get_room_partner(user)  # Message receiver

    # Creates message instance
    message = ChatMessage(
        sender=user, receiver=receiver,
        room=room, message_type=message_type
    )

    if attachment_links:
        message.attachment_links = attachment_links
    if voice_file:
        message.voice = voice_file
    if message_text:
        message.message_text = message_text
    
    message.save()
    return message

@database_sync_to_async
def update_chat_message(user: Type[User], message_text: str, message_id: int) -> Type[ChatMessage]:
    """update chat message object

    Parameters: 
        message_id (str): chat message id
        user (object): message sender
        message (str): text message like 'hello'

    Returns:
        message object
    """

    message = ChatMessage.objects.filter(id=message_id, sender=user).first()

    # When edit message contains text message
    if message and not message.is_deleted:
        # Edit message log creation
        ChatMessageEditLog.objects.create(
            message=message, previous_text_message=message.message_text, message_text=message_text)

        message.message_text = message_text

        message.save()

    return message

@database_sync_to_async
def delete_chat_message(user: Type[User], room: Type[ChatRoom], message_id: int) -> Type[ChatMessage]:
    """Delete chat message object

    Parameters: 
        message_id (str): chat message id
        user (object): message sender

    Returns:
        None
    """

    message = ChatMessage.objects.filter(
        room=room, id=message_id, sender=user).first()
    if message:
        message.is_deleted = True
        message.save()

    return message

@database_sync_to_async
def count_user_voice_chat(user: Type[User], room: Type[ChatRoom]) -> Type[ChatMessage]:
    """Return the number of voice chat of user

    Parameters: 
        room (object) : chat room message object's
        user (object): message sender
    """
    return ChatMessage.objects.filter(room=room, sender=user).exclude(voice__isnull=True, voice="").count()

@database_sync_to_async
def can_chat_together(user: Type[User], room_partner: Type[User]) -> Type[ChatMessage]:
    """Return the number of voice chat of user

    Parameters: 
        room_partner (object) : user object 
        user (object): request user
    """
    return user.can_chat_together(room_partner)


