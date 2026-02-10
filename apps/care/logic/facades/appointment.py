from django.core import exceptions
from django.db import IntegrityError

from apps.care import models as care_models
from apps.user import models as user_models
from utils import utils_model


def create(
        *,
        date: str,
        time: str,
        specialist_id: str,
        service: care_models.Service,
        user: user_models.User,
) -> care_models.Appointment:
    error_dict: dict[str, str] = {}

    if not specialist_id:
        error_dict["specialist_id"] = "Не выбран специалист"

    if not date:
        error_dict["date"] = "Дата обязательна"

    if not time:
        error_dict["time"] = "Время обязательно"

    if error_dict:
        raise exceptions.ValidationError("Ошибка валидации", error_dict=error_dict)

    specialist_exists = service.specialists.filter(pk=specialist_id).exists()
    if not specialist_exists:
        raise exceptions.ValidationError(
            "Ошибка валидации",
            error_dict={"specialist_id": "Специалист не относится к выбранной услуге"},
        )

    try:
        appointment = utils_model.create_model_instance(
            model_class=care_models.Appointment,
            validated_data={
                "date": date,
                "time": time,
                "specialist_id": specialist_id,
                "service": service,
                "user": user,
            },
        )
    except IntegrityError:
        raise exceptions.ValidationError("Ошибка создания приёма")
    return appointment
