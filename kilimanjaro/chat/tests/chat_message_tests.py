import pytest

from chat.models import ChatMessage, ChatMessageEditLog, ChatMessageReport


@pytest.mark.django_db
class TestChatMessage:

    api_end = '/chat/messages/'

    def test_model(
        self, user_obj, user_obj2, chat_room_obj
    ):
        chat_message = ChatMessage.objects.create(
            sender=user_obj, receiver=user_obj2, 
            message_text="hello world", room=chat_room_obj,
            message_type='text'
        )

        assert chat_message.__str__() == "hello world"

    def test_chat_message_list(self, api_client, auth_headers, chat_room_obj, chat_message_obj):
        response = api_client.get(
            f"{self.api_end}?room_id={chat_room_obj.id}",
            HTTP_AUTHORIZATION=auth_headers,
        )
        assert response.status_code == 200

    def test_chat_message_post(self, api_client, auth_headers, chat_room_obj):
        response = api_client.post(
            f"{self.api_end}",
            HTTP_AUTHORIZATION=auth_headers,
        )
        assert response.status_code == 403

    def test_message_report(self, api_client, auth_headers, chat_message_obj):
        response = api_client.post(
            f"{self.api_end}report/{chat_message_obj.id}/",
            data={'reason': 'spam'},
            HTTP_AUTHORIZATION=auth_headers,
        )
        assert response.status_code == 200

    def test_report_message_without_reason(self, api_client, auth_headers, chat_message_obj):
        response = api_client.post(
            f"{self.api_end}report/{chat_message_obj.id}/",
            HTTP_AUTHORIZATION=auth_headers,
        )
        assert response.status_code == 400

    def test_report_message_with_wrong_msg_id(self, api_client, auth_headers):
        response = api_client.post(
            f"{self.api_end}report/349/",
            data={'reason': 'spam'},
            HTTP_AUTHORIZATION=auth_headers,
        )
        assert response.status_code == 404


@pytest.mark.django_db
class TestChatMessageEditLog:

    def test_model(
        self, chat_message_obj
    ):
        chat_message_edit_log = ChatMessageEditLog.objects.create(
            message=chat_message_obj, 
            previous_text_message=chat_message_obj.message_text,
            message_text='hi'
        )
        assert chat_message_edit_log.__str__() == chat_message_obj.__str__()


@pytest.mark.django_db
class TestChatMessageReport:

    def test_model(
        self, user_obj2, chat_message_obj
    ):
        chat_message_edit_log = ChatMessageReport.objects.create(
            reported_by=user_obj2,
            message=chat_message_obj,
            reason='spam message'
        )
        assert chat_message_edit_log.__str__() == chat_message_obj.__str__()

