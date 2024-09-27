import uuid
from django.db import models
from django.contrib.postgres.fields import ArrayField

from model_utils.models import TimeStampedModel
from django.contrib.auth import get_user_model
from chat.models import ChatRoom

User = get_user_model()


class ChatMessage(TimeStampedModel):

    _MESSAGE_TYPE = (
        ('text', 'Text'),
        ('attachments', 'Attachments'),
        ('text_and_attachments', 'Text_and_attachments'),
        ('voice', 'Voice')
    ) 

    uuid = models.UUIDField(default=uuid.uuid4, unique=True)
    sender = models.ForeignKey(User, null=True, on_delete=models.SET_NULL, related_name='sender')
    receiver = models.ForeignKey(User, null=True, on_delete=models.SET_NULL, related_name='receiver')
    room = models.ForeignKey(ChatRoom, on_delete=models.CASCADE)
    message_text = models.TextField(max_length=140, null=True, blank=True)
    message_type = models.CharField(max_length=20, choices=_MESSAGE_TYPE)
    attachment_links = ArrayField(models.TextField(null=True, blank=True), blank=True, null=True) # url path of attachments file
    voice = models.CharField(max_length=500, null=True, blank=True) # url path of voice file
    is_deleted = models.BooleanField(default=False)

    class Meta:
        verbose_name = "Chat Message"
        verbose_name_plural = "Chat Messages"

    def __str__(self):
        return str(self.message_text)


class ChatMessageEditLog(TimeStampedModel):
    uuid = models.UUIDField(default=uuid.uuid4, unique=True)
    message = models.ForeignKey(ChatMessage, null=True, on_delete=models.SET_NULL)
    previous_text_message = models.TextField(max_length=140, null=True, blank=True)
    message_text = models.TextField(max_length=140, null=True, blank=True)

    class Meta:
        verbose_name = "Chat Message Edit Log"
        verbose_name_plural = "Chat Message Edit Logs"

    def __str__(self):
        return str(self.message)


class ChatMessageReport(TimeStampedModel):
    uuid = models.UUIDField(default=uuid.uuid4, unique=True)
    reported_by = models.ForeignKey(User, null=True, on_delete=models.SET_NULL)
    message = models.ForeignKey(ChatMessage, null=True, on_delete=models.SET_NULL)
    reason = models.TextField(max_length=1000, null=True, blank=True)

    class Meta:
        verbose_name = "Chat Message Report"
        verbose_name_plural = "Chat Message Reports"

    def __str__(self):
        return str(self.message)