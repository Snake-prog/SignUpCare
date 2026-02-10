import typing

import pydantic
from django.db import models


class BaseDto(pydantic.BaseModel):
    class Config:
        arbitrary_types_allowed = True
        use_enum_values = True
        from_attributes = True


BaseDtoTyping = typing.TypeVar("BaseDtoTyping", bound=BaseDto)
DjangoModel = typing.TypeVar("DjangoModel", bound=models.Model)
