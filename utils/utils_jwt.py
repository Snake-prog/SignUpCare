import jwt
from django.conf import settings


def jwt_decode(
        *,
        token: str
) -> dict:
    return jwt.decode(token, settings.SECRET_KEY, ['HS256'])
