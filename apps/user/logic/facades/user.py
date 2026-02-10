from django.contrib.auth import authenticate, login as base_login
from django.core import exceptions
from django.core.handlers.wsgi import WSGIRequest
from django.db import IntegrityError

from apps.user import models as user_models
from utils import utils_model


def login(
        *,
        request: WSGIRequest,
        email: str,
        password: str
) -> user_models.User:
    user = authenticate(
        request=request,
        username=email,
        password=password,
    )
    if user is None:
        raise exceptions.ValidationError("Неверный email или пароль")
    base_login(request=request, user=user)
    return user


def register(
        *,
        request: WSGIRequest,
        email: str,
        password: str,
        password_repeat: str,
        phone: str | None,
        name: str | None
) -> user_models.User:
    if password != password_repeat:
        raise exceptions.ValidationError("Пароли не совпадают")
    if user_models.User.objects.filter(email=email).exists():
        raise exceptions.ValidationError("Пользователь с таким email уже существует")
    try:
        user = utils_model.create_model_instance(
            model_class=user_models.User,
            validated_data={
                "email": email,
                "phone": phone,
                "name": name,
                "password": password,
                "is_active": True,
            },
        )
        user.set_password(password)
        user.save()
    except IntegrityError:
        raise exceptions.ValidationError("Ошибка создания пользователя")
    base_login(request, user)
    return user


def update(
        *,
        user: user_models.User,
        email: str | None,
        phone: str | None,
        name: str | None,
        passport: str | None,
        policy: str | None,
) -> user_models.User:
    return utils_model.update_model_instance(
        instance=user,
        validated_data={
            "email": email,
            "phone": phone,
            "name": name,
            "passport": passport,
            "policy": policy,
        },
    )
