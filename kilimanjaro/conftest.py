# File contains fixtures that have been shared among all tests
import pytest
from djmoney.money import Money
from rest_framework.test import APIClient
from channels.db import database_sync_to_async
from channels.testing import WebsocketCommunicator
from kilimanjaro.asgi import application

from certification.models import Certification
from contact_us.models import ContactUs
from core.models import ClientAPIKey
from core.utils.general_func import file_object
from country.models import Country
from customer.models import Customer
from favorite.models import Favorite
from notification.models import Notification
from occupation.models import Occupation
from portfolio.models import Portfolio, PortfolioImage
from skilled_worker.models import SkilledWorker
from user.models import AccountVerificationRequest, ResetPasswordRequest, User
from chat.models import ChatRoom, ChatMessage

pytest_plugins = ("celery.contrib.pytest",)


@pytest.fixture
def client_api_key_obj(db):
    return ClientAPIKey.objects.create(is_active=True)

@pytest.fixture
def api_client(client_api_key_obj):
    api_client = APIClient()
    api_client.credentials(HTTP_CLIENTAPIKEY=client_api_key_obj.api_key)
    return api_client


@pytest.fixture
def country_obj(db):
    return Country.objects.create(
        name="Germany", currency_name="Euro", currency_code="EUR"
    )


@pytest.fixture
def user_obj(db, country_obj):
    user_obj = User.objects.create(
        email="josephgreene@example.net",
        phone_number="+8801789929182",
        username="whebert",
        first_name="Patrick",
        last_name="Harris",
        date_of_birth="2000-01-01",
        country=country_obj,
        city="Berlin",
        profile_picture=file_object(name="abcde.png"),
        age_consent=25,
        terms_and_condition=True,
        is_email_verified=True,
        is_phone_number_verified=True,
        is_staff=True,
    )
    user_obj.set_password("test136")
    user_obj.save()
    return user_obj


@pytest.fixture
def user_obj1(db):
    user_obj = User.objects.create(
        email="thomas64@example.net",
        username="jason85",
        first_name="Lisa",
        last_name="Hines",
        is_email_verified=False,
    )
    user_obj.set_password("test136")
    user_obj.save()
    return user_obj


@pytest.fixture
def user_obj2(db, country_obj):
    user_obj = User.objects.create(
        email="chadnicholson@example.org",
        phone_number="+8801760000030",
        username="frodriguez",
        first_name="Amanda",
        last_name="Gordon",
        date_of_birth="2000-01-01",
        country=country_obj,
        city="Berlin",
        profile_picture=file_object(name="abcde.png"),
        age_consent=25,
        terms_and_condition=True,
    )
    user_obj.set_password("test136")
    user_obj.save()
    return user_obj


@pytest.fixture
def user_obj3(db, country_obj):
    user_obj = User.objects.create(
        email="randall97@example.com",
        date_of_birth="2000-01-01",
        country=country_obj,
        city="Berlin",
        profile_picture=file_object(name="abcde.png"),
        age_consent=25,
        terms_and_condition=True,
    )
    user_obj.set_password("test136")
    user_obj.save()
    return user_obj


@pytest.fixture
def user_obj4(db, country_obj):
    user_obj = User.objects.create(
        phone_number="+880171212321",
        username="aaron92",
        first_name="Amber",
        last_name="Stafford",
        date_of_birth="2000-01-01",
        country=country_obj,
        city="Berlin",
        profile_picture=file_object(name="abcde.png"),
        age_consent=25,
        terms_and_condition=True,
        is_phone_number_verified=True,
    )
    user_obj.set_password("test136")
    user_obj.save()
    return user_obj


@pytest.fixture
def user_obj5(db, country_obj):
    user_obj = User.objects.create(
        phone_number="+8801723439276",
        username="mcarter",
        first_name="Julie",
        last_name="Rhodes",
        date_of_birth="2000-01-01",
        country=country_obj,
        city="Berlin",
        profile_picture=file_object(name="abcde.png"),
        age_consent=25,
        terms_and_condition=True,
        is_phone_number_verified=True,
    )
    user_obj.set_password("test136")
    user_obj.save()
    return user_obj


@pytest.fixture
def user_without_skp(db, country_obj):
    user_obj = User.objects.create(
        email="bellmichele@example.net",
        username="ubenitez",
        first_name="Erika",
        last_name="Adkins",
        date_of_birth="2000-01-01",
        country=country_obj,
        profile_picture=file_object(name="abcde.png"),
        city="Berlin",
        age_consent=25,
        terms_and_condition=True,
        is_email_verified=True,
    )
    user_obj.set_password("test136")
    user_obj.save()
    return user_obj


@pytest.fixture
def occupation_obj(db):
    return Occupation.objects.create(name="Cleaner2")


@pytest.fixture
def customer_obj(db, user_obj):
    return Customer.objects.create(user=user_obj)


@pytest.fixture
def customer_obj1(db, user_obj1):
    return Customer.objects.create(user=user_obj1)


@pytest.fixture
def customer_obj2(db, user_obj2):
    customer_obj = Customer.objects.create(user=user_obj2)
    customer_obj.balance = Money(10, "USD")
    customer_obj.save()

    return customer_obj


@pytest.fixture
def skilled_worker_obj(db, user_obj, occupation_obj):
    return SkilledWorker.objects.create(
        user=user_obj,
        occupation=occupation_obj,
        description="skill worker description",
        experience=23.32,
    )


@pytest.fixture
def skilled_worker_obj1(db, user_obj1, occupation_obj):
    return SkilledWorker.objects.create(
        user=user_obj1,
        occupation=occupation_obj,
        description="skill worker description",
        experience=33.32,
    )


@pytest.fixture
def skilled_worker_obj2(db, user_obj2):
    return SkilledWorker.objects.create(
        user=user_obj2,
        description="skill worker description",
        experience=43.32,
    )


@pytest.fixture
def skilled_worker_obj3(db, user_obj5):
    skilled_worker_obj = SkilledWorker.objects.create(
        user=user_obj5,
        description="skill worker description",
        experience=43.32,
    )

    skilled_worker_obj.balance = Money(10, "USD")
    skilled_worker_obj.save()

    return skilled_worker_obj


@pytest.fixture
def skilled_worker_obj4(db, user_obj4):
    skilled_worker_obj = SkilledWorker.objects.create(
        user=user_obj4,
        description="skill worker description",
        experience=43.32,
    )

    skilled_worker_obj.balance = Money(10, "USD")
    skilled_worker_obj.save()

    return skilled_worker_obj


@pytest.fixture
def auth_token(api_client, skilled_worker_obj, customer_obj):
    endpoint = "/api/login/"
    response = api_client.post(
        endpoint,
        data={"email": skilled_worker_obj.user.email, "password": "test136"},
    )
    return response.data


@pytest.fixture
def auth_token1(api_client, skilled_worker_obj1, customer_obj1):
    endpoint = "/api/login/"
    response = api_client.post(
        endpoint,
        data={"email": skilled_worker_obj1.user.email, "password": "test136"},
    )
    return response.data


@pytest.fixture
def auth_token_for_phone(api_client, user_obj2):
    endpoint = "/api/login/"
    response = api_client.post(
        endpoint,
        data={"email": user_obj2.phone_number.raw_input, "password": "test136"},
    )
    return response.data


@pytest.fixture
def auth_token_for_without_skp(api_client, user_without_skp):
    endpoint = "/api/login/"
    response = api_client.post(
        endpoint, data={"email": user_without_skp.email, "password": "test136"}
    )
    return response.data


@pytest.fixture
def auth_headers(auth_token):
    access_key = auth_token.get("access")
    return f"Bearer {access_key}"


@pytest.fixture
def auth_headers_for_phone(auth_token_for_phone):
    access_key = auth_token_for_phone.get("access")
    return f"Bearer {access_key}"


@pytest.fixture
def auth_headers_for_without_skp(auth_token_for_without_skp):
    access_key = auth_token_for_without_skp.get("access")
    return f"Bearer {access_key}"


@pytest.fixture
def auth_headers1(auth_token1):
    access_key = auth_token1.get("access")
    return f"Bearer {access_key}"


@pytest.fixture
def certification_obj(db, skilled_worker_obj):
    return Certification.objects.create(
        skilled_worker=skilled_worker_obj,
        certification_name="New Certificate",
        description="test description",
        date_earned="2020-02-20",
    )


@pytest.fixture
def certification_obj1(db, skilled_worker_obj1):
    return Certification.objects.create(
        skilled_worker=skilled_worker_obj1,
        certification_name="New Certificate",
        description="test description",
        date_earned="2020-02-20",
    )


@pytest.fixture
def certification_obj2(db, skilled_worker_obj3):
    return Certification.objects.create(
        skilled_worker=skilled_worker_obj3,
        certification_name="New Certificate2",
        description="test description",
        date_earned="2020-02-20",
    )


@pytest.fixture
def portfolio_obj(db, skilled_worker_obj, certification_obj):
    portfolio_obj = Portfolio.objects.get(skilled_worker=skilled_worker_obj)
    portfolio_obj.education = "Test education"
    portfolio_obj.certification = certification_obj
    portfolio_obj.description = "Test description"
    portfolio_obj.save()

    return portfolio_obj


@pytest.fixture
def portfolio_obj2(db, skilled_worker_obj3, certification_obj2):
    portfolio_obj = Portfolio.objects.get(skilled_worker=skilled_worker_obj3)
    portfolio_obj.education = "Test education"
    portfolio_obj.certification = certification_obj2
    portfolio_obj.description = "Test description"
    portfolio_obj.save()

    return portfolio_obj


@pytest.fixture
def portfolio_image_obj(db, portfolio_obj):
    return PortfolioImage.objects.create(
        picture=file_object(name="abc.png"), portfolio=portfolio_obj
    )


@pytest.fixture
def portfolio_image_obj2(db, portfolio_obj2):
    return PortfolioImage.objects.create(
        picture=file_object(name="abcd.png"), portfolio=portfolio_obj2
    )


@pytest.fixture
def account_verification_request_obj1(db, user_obj1):
    return AccountVerificationRequest.objects.create(
        user=user_obj1, verify_by="email", token="e-098765", is_used=False
    )


@pytest.fixture
def account_verification_request_obj2(db, user_obj2):
    return AccountVerificationRequest.objects.create(
        user=user_obj2, verify_by="phone", token="p-098766", is_used=False
    )


@pytest.fixture
def reset_password_request_obj1(db, user_obj1):
    return ResetPasswordRequest.objects.create(
        user=user_obj1, requested_with="email", token="e-123456", is_used=False
    )


@pytest.fixture
def reset_password_request_obj2(db, user_obj2):
    return ResetPasswordRequest.objects.create(
        user=user_obj2, requested_with="phone", token="p-123455", is_used=False
    )


@pytest.fixture
def notification_obj(db, user_obj):
    return Notification.objects.create(user=user_obj, notification_for="order_create")


@pytest.fixture
def favorite_obj(db, customer_obj, skilled_worker_obj):
    return Favorite.objects.create(
        customer=customer_obj, skilled_worker=skilled_worker_obj
    )


@pytest.fixture
def contact_us_obj(db, user_obj):

    return ContactUs.objects.create(
        user=user_obj,
        title="Contact us title",
        message="This is an important message",
        attachment=file_object(name="abcde.png"),
    )


@pytest.fixture
def chat_room_obj(db, user_obj, user_obj2):

    return ChatRoom.objects.create(
        room_member_1=user_obj,
        room_member_2=user_obj2
    )

@pytest.fixture
def chat_room_obj2(db, user_obj, user_obj2):

    return ChatRoom.objects.create(
        room_member_1=user_obj2,
        room_member_2=user_obj,
        is_blocked_by_member_2 = True
    )

@pytest.fixture
def chat_room_obj3(db, user_obj3, user_obj2):

    return ChatRoom.objects.create(
        room_member_1=user_obj2,
        room_member_2=user_obj3
    )

@pytest.fixture
def chat_message_obj(db, user_obj, user_obj2, chat_room_obj):

    return ChatMessage.objects.create(
            sender=user_obj2, receiver=user_obj, 
            message_text="hello world", room=chat_room_obj,
            message_type='text',
            attachment_links=['/media/37c89079-2f34-4ca5-8644-7367918495c6/xy83z@file.png']
        )


# chat websocket realted fixtures

@database_sync_to_async
def create_user(email, username):
    user_obj = User.objects.create(
        email=email,
        username=username,
        first_name="Nathaniel",
        last_name="Herring",
        date_of_birth="2000-01-01",
        city="Berlin",
        profile_picture=file_object(name="abcde.png"),
        age_consent=25,
        terms_and_condition=True,
        is_phone_number_verified=True,
    )
    user_obj.set_password("test136")
    user_obj.save()

    # create customer profile 
    Customer.objects.create(user=user_obj)
    return user_obj

@database_sync_to_async
def create_occupation():
    return Occupation.objects.create(name="Cleaner2")

@database_sync_to_async
def create_skilled_worker(user_obj, occupation_obj):
    return SkilledWorker.objects.create(
        user=user_obj,
        occupation=occupation_obj,
        description="skill worker description",
        experience=23.32,
    )

@database_sync_to_async
def create_message(ws_user1, ws_user2, ws_chat_room1, msg_text, msg_type, attachment_links=[]):
    return ChatMessage.objects.create(
        sender=ws_user1, 
        receiver=ws_user2, 
        room=ws_chat_room1, 
        message_text=msg_text,
        message_type=msg_type,
        attachment_links=attachment_links
    )

@pytest.fixture
async def ws_user1(db):
    return await create_user('ws_test1@hotmail.com', 'ws_test1')

@pytest.fixture
async def ws_user2(db, ws_occupation_obj):
    user = await create_user('ws_test2@hotmail.com', 'ws_test2')
    await create_skilled_worker(user, ws_occupation_obj)
    return user

@pytest.fixture
async def ws_user3(db):
    return await create_user('ws_test3@hotmail.com', 'ws_test3')

@pytest.fixture
async def ws_user4(db):
    return await create_user('ws_test4@hotmail.com', 'ws_test4')

@pytest.fixture
async def ws_user5(db):
    return await create_user('ws_test5@hotmail.com', 'ws_test5')

@pytest.fixture
async def ws_occupation_obj(db):
    return await create_occupation()

@database_sync_to_async
def create_ws_chat_room(user1, user2, is_blocked_by_member_1, is_blocked_by_member_2):
    return ChatRoom.objects.create(
        room_member_1=user1,
        room_member_2=user2,
        is_blocked_by_member_1=is_blocked_by_member_1,
        is_blocked_by_member_2=is_blocked_by_member_2
    )

@pytest.fixture
async def ws_chat_room1(db, ws_user1, ws_user2):
    return await create_ws_chat_room(ws_user1, ws_user2, False, False)

@pytest.fixture
async def ws_chat_room2(db, ws_user1, ws_user5):
    return await create_ws_chat_room(ws_user1, ws_user5, True, False)

@pytest.fixture
async def ws_message_obj(db, ws_user1, ws_user2, ws_chat_room1):
    return await create_message(ws_user1, ws_user2, ws_chat_room1, "Hey what's up", "text_and_attachment", ["/media/37c89079-2f34-4ca5-8644-7367918495c6/xy83z@file.png"])

@pytest.fixture
async def ws_message_obj2(db, ws_user1, ws_user5, ws_chat_room2):
    return await create_message(ws_user1, ws_user5, ws_chat_room2, "Hey buddy", "text")

@pytest.fixture
def auth_token_for_user1(api_client, ws_user1):
    endpoint = "/api/login/"
    response = api_client.post(
        endpoint,
        data={"email": ws_user1.email, "password": "test136"},
    )
    return response.data.get('access')

@pytest.fixture
def auth_token_for_user2(api_client, ws_user2):
    endpoint = "/api/login/"
    response = api_client.post(
        endpoint,
        data={"email": ws_user2.email, "password": "test136"},
    )
    return response.data.get('access')


@pytest.fixture
def auth_token_for_user3(api_client, ws_user3):
    endpoint = "/api/login/"
    response = api_client.post(
        endpoint,
        data={"email": ws_user3.email, "password": "test136"},
    )
    return response.data.get('access')

@pytest.fixture
def auth_token_for_user4(api_client, ws_user4):
    endpoint = "/api/login/"
    response = api_client.post(
        endpoint,
        data={"email": ws_user4.email, "password": "test136"},
    )
    return response.data.get('access')

@pytest.fixture
def ws_communicator(auth_token_for_user1):
    headers = [(b'authorization', auth_token_for_user1.encode('ascii'))]
    return WebsocketCommunicator(application, "/chat/", headers)

@pytest.fixture
def ws_communicator2(auth_token_for_user2):
    headers = [(b'authorization', auth_token_for_user2.encode('ascii'))]
    return WebsocketCommunicator(application, "/chat/", headers)

@pytest.fixture
def ws_communicator3(auth_token_for_user3):
    headers = [(b'authorization', auth_token_for_user3.encode('ascii'))]
    return WebsocketCommunicator(application, "/chat/", headers)

@pytest.fixture
def ws_communicator4():
    return WebsocketCommunicator(application, "/chat/")
