import pytest

from chat.models import ChatRoom, ChatRoomBlockLog


@pytest.mark.django_db
class TestChatRoom:

    api_end = '/chat/rooms/'

    def test_chat_room_model(
        self, user_obj1, user_obj2
    ):
        chat_room = ChatRoom.objects.create(
            room_member_1=user_obj1, room_member_2=user_obj2
        )

        chat_room2 = ChatRoom(
            room_member_1=user_obj1, room_member_2=user_obj2
        )

        chat_room.clean()

        has_exception = False
        try:
            chat_room2.save()
            chat_room2.clean()
        except:
            has_exception = True # should through exception already exists room with those user

        room_partner = chat_room.get_room_partner(user_obj2)

        assert room_partner == user_obj1
        assert has_exception == True
        assert chat_room.group_name == f"PrivateChatRoom-{chat_room.uuid}"
        assert chat_room.__str__() == f"{user_obj1}-{user_obj2}"

    def test_chat_room_list(self, api_client, auth_headers, chat_room_obj, chat_room_obj2):
        response = api_client.get(
            f"{self.api_end}",
            HTTP_AUTHORIZATION=auth_headers,
        )

        assert response.status_code == 200

    def test_chat_room_post(self, api_client, auth_headers):
        response = api_client.post(
            f"{self.api_end}",
            HTTP_AUTHORIZATION=auth_headers,
        )

        assert response.status_code == 403

    def test_blocked_chat_room_list(self, api_client, auth_headers, chat_room_obj2):
        response = api_client.get(
            f"{self.api_end}block_list/",
            HTTP_AUTHORIZATION=auth_headers,
        )
        assert response.status_code == 200
    
    def test_blocked_chat_room(self, api_client, auth_headers, chat_room_obj):
        response = api_client.post(
            f"{self.api_end}block/{chat_room_obj.id}/",
            HTTP_AUTHORIZATION=auth_headers,
        )
        assert response.status_code == 200

    def test_blocked_chat_room_by_partner(self, api_client, auth_headers, chat_room_obj2):
        response = api_client.post(
            f"{self.api_end}block/{chat_room_obj2.id}/",
            HTTP_AUTHORIZATION=auth_headers,
        )

        assert response.status_code == 200

    def test_blocked_chat_room_by_wrong_user(self, api_client, auth_headers, chat_room_obj3):
        response = api_client.post(
            f"{self.api_end}block/{chat_room_obj3.id}/",
            HTTP_AUTHORIZATION=auth_headers,
        )

        assert response.status_code == 400

    def test_unblocked_chat_room(self, api_client, auth_headers, chat_room_obj):
        response = api_client.post(
            f"{self.api_end}unblock/{chat_room_obj.id}/",
            HTTP_AUTHORIZATION=auth_headers,
        )
        assert response.status_code == 200

    def test_unblocked_chat_room_by_partner(self, api_client, auth_headers, chat_room_obj2):
        response = api_client.post(
            f"{self.api_end}unblock/{chat_room_obj2.id}/",
            HTTP_AUTHORIZATION=auth_headers,
        )

        assert response.status_code == 200

    def test_unblocked_chat_room_by_wrong_user(self, api_client, auth_headers, chat_room_obj3):
        response = api_client.post(
            f"{self.api_end}unblock/{chat_room_obj3.id}/",
            HTTP_AUTHORIZATION=auth_headers,
        )

        assert response.status_code == 400

    def test_user_and_partner_single_room_info(self, api_client, auth_headers, user_obj2):

        print(user_obj2.username)
        response = api_client.get(
            f"/chat/k/{user_obj2.username}/",
            HTTP_AUTHORIZATION=auth_headers,
        )
        assert response.status_code == 200

    def test_user_and_partner_single_room_info_with_invalid_username(self, api_client, auth_headers):
        response = api_client.get(
            f"/chat/k/test-user-invalid/",
            HTTP_AUTHORIZATION=auth_headers,
        )
        return response.status_code == 400


@pytest.mark.django_db
class TestChatRoomBlockLog:

    def test_chat_room_block_log_model(
        self, user_obj1, user_obj2
    ):
        chat_room_block_log = ChatRoomBlockLog.objects.create(
            block_type='block',
            blocked_by_user=user_obj1,
            blocked_to_user=user_obj2
        )

        assert chat_room_block_log.__str__() == f"{user_obj1} -> {user_obj2}"