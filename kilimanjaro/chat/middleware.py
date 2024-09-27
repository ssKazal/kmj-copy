from django.contrib.auth.models import AnonymousUser
from rest_framework_simplejwt.tokens import AccessToken
from channels.db import database_sync_to_async
from channels.middleware import BaseMiddleware
from django.contrib.auth import get_user_model


User = get_user_model()


@database_sync_to_async
def get_user(token_key):
    try:
        access_token = AccessToken(token_key)
        user_id = access_token.get("user_id")
    except:
        user_id = None

    if user_id:
        user = User.objects.filter(id=user_id).first()
        if user:
            return user
    return AnonymousUser()


class TokenAuthMiddleware(BaseMiddleware):
    def __init__(self, inner):
        super().__init__(inner)

    async def __call__(self, scope, receive, send):
        headers = dict(scope['headers'])
        token_key = None

        if b'authorization' in headers:
            token_key = headers[b'authorization'].decode().split()[0]
 
        scope['user'] = AnonymousUser() if token_key is None else await get_user(token_key)

        return await super().__call__(scope, receive, send)