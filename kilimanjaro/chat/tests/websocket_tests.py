import pytest

from .test_gn_data import (GREATHER_THAN_2MIN_AUDIO_FILE, VOICE_STRING_FILE, 
    IMAGE_STRING_FILE, GREATHER_THAN_5_MB_FILE)
from core.utils.general_data import MAX_VOICE_MESSAGE_FOR_PER_CHATTING_ROOM


@pytest.mark.django_db(transaction=True)
@pytest.mark.asyncio
async def test_join_to_chat_room(ws_communicator, ws_chat_room1):

    # connects user
    connected, _ = await ws_communicator.connect()
    assert connected


    # joins user to group
    await ws_communicator.send_json_to(
        {
            "command": "join",
            "room_id": ws_chat_room1.id,
        }
    )
    await ws_communicator.disconnect()


@pytest.mark.django_db(transaction=True)
@pytest.mark.asyncio
async def test_try_to_join_another_users_chat_room(ws_communicator3, ws_chat_room1):

    await ws_communicator3.connect()

    # joins user1 to group
    await ws_communicator3.send_json_to(
        {
            "command": "join",
            "room_id": ws_chat_room1.id,
        }
    )
    response = await ws_communicator3.receive_json_from()

    assert response.get('response_type') == 'Error'
    assert response.get('message') == 'Invalid Room ID!'

    await ws_communicator3.disconnect()


@pytest.mark.django_db(transaction=True)
@pytest.mark.asyncio
async def test_try_to_join_as_unauthorized_user(ws_communicator4, ws_chat_room1):

    await ws_communicator4.connect()

    # joins user1 to group
    await ws_communicator4.send_json_to(
        {
            "command": "join",
            "room_id": ws_chat_room1.id,
        }
    )
    response = await ws_communicator4.receive_json_from()

    assert response.get('response_type') == 'Error'
    assert response.get('message') == 'Authentication is required.'

    await ws_communicator4.disconnect()


@pytest.mark.django_db(transaction=True)
@pytest.mark.asyncio
async def test_try_to_chat_together_two_customer(ws_communicator, ws_user3):

    await ws_communicator.connect()

    # joins user1 to group
    await ws_communicator.send_json_to(
        {
            "command": "send_first_message",
            "partner_id": ws_user3.id,
            "text_message": 'hi'
        }
    )
    response = await ws_communicator.receive_json_from()

    assert response.get('response_type') == 'Error'
    assert response.get('message') == "Two skilled worker or two customer can't chat together"

    await ws_communicator.disconnect()


@pytest.mark.django_db(transaction=True)
@pytest.mark.asyncio
async def test_send_first_message_with_invalid_room_partner_id(ws_communicator):

    await ws_communicator.connect()

    # joins user1 to group
    await ws_communicator.send_json_to(
        {
            "command": "send_first_message",
            "partner_id": 999999,
            "text_message": 'hey'
        }
    )
    response = await ws_communicator.receive_json_from()
    assert response.get('response_type') == 'Error'
    assert response.get('message') == 'Invalid Room partner ID!'

    await ws_communicator.disconnect()


@pytest.mark.django_db(transaction=True)
@pytest.mark.asyncio
async def test_send_first_message_for_room_creation(ws_communicator, ws_user2):

    await ws_communicator.connect()

    # joins user1 to group
    await ws_communicator.send_json_to(
        {
            "command": "send_first_message",
            "partner_id": ws_user2.id,
            "text_message": 'hi'
        }
    )
    response = await ws_communicator.receive_json_from()
    assert response.get('response_type') == 'new_message'

    await ws_communicator.disconnect()

@pytest.mark.django_db(transaction=True)
@pytest.mark.asyncio
async def test_try_to_send_message_with_wrong_room_id(ws_communicator):

    await ws_communicator.connect()

    # sends text message
    await ws_communicator.send_json_to(
        {
            "command": "send_message",
            "room_id": 232332,
            "text_message": 'hi'
        }
    )
    response = await ws_communicator.receive_json_from()
    assert response.get('response_type') == 'Error'
    assert response.get('message') == 'Invalid Room ID!'

    await ws_communicator.disconnect()


@pytest.mark.django_db(transaction=True)
@pytest.mark.asyncio
async def test_send_text_message(ws_communicator, ws_chat_room1):

    await ws_communicator.connect()

    # sends text messsage
    await ws_communicator.send_json_to(
        {
            "command": "send_message",
            "room_id": ws_chat_room1.id,
            "text_message": 'hi'
        }
    )
    response = await ws_communicator.receive_json_from()
    assert response.get('response_type') == 'new_message'
    assert response.get('text_message') == 'hi'

    await ws_communicator.disconnect()


@pytest.mark.django_db(transaction=True)
@pytest.mark.asyncio
async def test_send_attachment_message(ws_communicator, ws_chat_room1):

    await ws_communicator.connect()

    # sends attachment
    await ws_communicator.send_json_to(
        {
            "command": "send_message",
            "room_id": ws_chat_room1.id,
            "attachment_links": [
                IMAGE_STRING_FILE,
                IMAGE_STRING_FILE
            ]
        }
    )
    response = await ws_communicator.receive_json_from()
    assert response.get('response_type') == 'new_message'
    assert len(response.get('attachment_links')) == 2

    await ws_communicator.disconnect()


@pytest.mark.django_db(transaction=True)
@pytest.mark.asyncio
async def test_send_big_attachment_file_like_greather_than_5mb(ws_communicator, ws_chat_room1):

    await ws_communicator.connect()

    # sends attachment
    await ws_communicator.send_json_to(
        {
            "command": "send_message",
            "room_id": ws_chat_room1.id,
            "attachment_links": [
                GREATHER_THAN_5_MB_FILE
            ]
        }
    )
    response = await ws_communicator.receive_json_from()
    assert response.get('response_type') == 'new_message'
    assert len(response.get('attachment_links')) == 1

    await ws_communicator.disconnect()

@pytest.mark.django_db(transaction=True)
@pytest.mark.asyncio
async def test_send_attachment_and_text_message(ws_communicator2, ws_chat_room1):

    await ws_communicator2.connect()

    # sends attachment
    await ws_communicator2.send_json_to(
        {
            "command": "send_message",
            "room_id": ws_chat_room1.id,
            "text_message": "This is my attachment check it out.",
            "attachment_links": [
                IMAGE_STRING_FILE,
                IMAGE_STRING_FILE
            ]
        }
    )
    response = await ws_communicator2.receive_json_from()
    assert response.get('response_type') == 'new_message'
    assert response.get('text_message') == "This is my attachment check it out."
    assert len(response.get('attachment_links')) == 2

    await ws_communicator2.disconnect()


@pytest.mark.django_db(transaction=True)
@pytest.mark.asyncio
async def test_send_voice_message(ws_communicator, ws_chat_room1):

    await ws_communicator.connect()

    # sends attachment
    await ws_communicator.send_json_to(
        {
            "command": "send_message",
            "room_id": ws_chat_room1.id,
            "voice_file": VOICE_STRING_FILE,
        }
    )
    response = await ws_communicator.receive_json_from()
    assert response.get('response_type') == 'new_message'
    assert response.get('voice') != None

    await ws_communicator.disconnect()


@pytest.mark.django_db(transaction=True)
@pytest.mark.asyncio
async def test_send_greather_than_2min_voice_message(ws_communicator, ws_chat_room1):

    await ws_communicator.connect()

    # sends attachment
    await ws_communicator.send_json_to(
        {
            "command": "send_message",
            "room_id": ws_chat_room1.id,
            "voice_file": GREATHER_THAN_2MIN_AUDIO_FILE,
        }
    )
    response = await ws_communicator.receive_json_from()
    assert response.get('response_type') == 'Error'
    assert response.get('message') == "You can send only 2 minutes duration's voice"

    await ws_communicator.disconnect()


@pytest.mark.django_db(transaction=True)
@pytest.mark.asyncio
async def test_another_room_member_receives_message(ws_communicator, ws_communicator2, ws_chat_room1):

    await ws_communicator.connect()
    await ws_communicator2.connect()

    # join user2 to group
    await ws_communicator2.send_json_to(
        {
            "command": "join",
            "room_id": ws_chat_room1.id,
        }
    )

    # sends text messsage
    await ws_communicator.send_json_to(
        {
            "command": "send_message",
            "room_id": ws_chat_room1.id,
            "text_message": 'hi'
        }
    )
    response = await ws_communicator2.receive_json_from()
    assert response.get('response_type') == 'new_message'
    assert response.get('text_message') == 'hi'

    await ws_communicator2.disconnect()
    await ws_communicator.disconnect()

@pytest.mark.django_db(transaction=True)
@pytest.mark.asyncio
async def test_try_to_send_message_already_blocked_chat_room(ws_communicator, ws_chat_room2):

    await ws_communicator.connect()

    # sends text messsage
    await ws_communicator.send_json_to(
        {
            "command": "send_message",
            "room_id": ws_chat_room2.id,
            "text_message": 'hi'
        }
    )
    response = await ws_communicator.receive_json_from()
    assert response.get('response_type') == 'Error'
    assert response.get('message') == 'Chat Room is already blocked'

    await ws_communicator.disconnect()

@pytest.mark.django_db(transaction=True)
@pytest.mark.asyncio
async def test_edit_text_message(ws_communicator, ws_chat_room1, ws_message_obj):

    await ws_communicator.connect()

    # sends text messsage
    await ws_communicator.send_json_to(
        {
            "command": "edit_message",
            "room_id": ws_chat_room1.id,
            "text_message": 'hello->',
            "message_id": ws_message_obj.id
        }
    )
    response = await ws_communicator.receive_json_from()
    assert response.get('response_type') == 'edited_message'
    assert response.get('text_message') == 'hello->'

    await ws_communicator.disconnect()

@pytest.mark.django_db(transaction=True)
@pytest.mark.asyncio
async def test_try_to_edit_text_message_by_wrong_msg_id(ws_communicator, ws_chat_room1, ws_message_obj):

    await ws_communicator.connect()

    # sends text messsage
    await ws_communicator.send_json_to(
        {
            "command": "edit_message",
            "room_id": ws_chat_room1.id,
            "text_message": 'hey->',
            "message_id": 2323323
        }
    )
    response = await ws_communicator.receive_json_from()
    assert response.get('response_type') == 'Error'
    assert response.get('message') == 'Invalid message ID!'

    await ws_communicator.disconnect()


@pytest.mark.django_db(transaction=True)
@pytest.mark.asyncio
async def test_try_to_edit_message_already_blocked_chat_room(ws_communicator, ws_chat_room2, ws_message_obj2):

    await ws_communicator.connect()

    # sends text messsage
    await ws_communicator.send_json_to(
        {
            "command": "edit_message",
            "room_id": ws_chat_room2.id,
            "text_message": 'hi',
            "message_id": ws_message_obj2.id
        }
    )
    response = await ws_communicator.receive_json_from()
    assert response.get('response_type') == 'Error'
    assert response.get('message') == 'Chat Room is already blocked'

    await ws_communicator.disconnect()


@pytest.mark.django_db(transaction=True)
@pytest.mark.asyncio
async def test_delete_message(ws_communicator, ws_chat_room1, ws_message_obj):

    await ws_communicator.connect()

    # sends text messsage
    await ws_communicator.send_json_to(
        {
            "command": "delete_message",
            "room_id": ws_chat_room1.id,
            "message_id": ws_message_obj.id
        }
    )
    response = await ws_communicator.receive_json_from()
    assert response.get('response_type') == 'deleted_message'
    assert response.get('id') == ws_message_obj.id

    await ws_communicator.disconnect()


@pytest.mark.django_db(transaction=True)
@pytest.mark.asyncio
async def test_try_to_delete_message_with_invalid_msg_id(ws_communicator, ws_chat_room1):

    await ws_communicator.connect()

    # sends text messsage
    await ws_communicator.send_json_to(
        {
            "command": "delete_message",
            "room_id": ws_chat_room1.id,
            "message_id": 33434343
        }
    )
    response = await ws_communicator.receive_json_from()
    assert response.get('response_type') == 'Error'
    assert response.get('message') == 'Invalid message ID!'

    await ws_communicator.disconnect()


@pytest.mark.django_db(transaction=True)
@pytest.mark.asyncio
async def test_send_max_limit_voice_message(ws_communicator, ws_chat_room1):

    await ws_communicator.connect()

    for _ in range(MAX_VOICE_MESSAGE_FOR_PER_CHATTING_ROOM + 2):
        # sends attachment
        await ws_communicator.send_json_to(
            {
                "command": "send_message",
                "room_id": ws_chat_room1.id,
                "voice_file": VOICE_STRING_FILE,
            }
        )


        response = await ws_communicator.receive_json_from()
        
    assert response.get('response_type') == 'Error'
    assert response.get('message') == 'You already cross your voice send limit'

    await ws_communicator.disconnect()
