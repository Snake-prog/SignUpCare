import io
import typing

import pydantic
from django.core.serializers import base as base_serializers
from rest_framework import serializers

try:
    import restdoctor.rest_framework.serializers


    class PydanticSerializer(restdoctor.rest_framework.serializers.PydanticSerializer):
        @property
        def pydantic_instance(self) -> pydantic.BaseModel:
            if not hasattr(self, "_validated_data"):
                msg = "You must call `.is_valid()` before accessing `.pydantic_instance`."
                raise AssertionError(msg)
            return self._pydantic_instance


    class PydanticSerializerWithAliases(restdoctor.rest_framework.serializers.PydanticSerializer):
        def pydantic_use_aliases(self) -> bool:
            return True
except ImportError:
    pass


class AbstractModelSerializer(serializers.ModelSerializer):
    """
    Base class from which all serializer classes should be inherited,
    in order to have an option to add behavior to the group of serializers.
    """

    ...


class AbstractSerializer(serializers.Serializer):
    ...


class IdSerializer(serializers.Serializer):
    """Сериализатор полей дата начала и окончания действия."""

    id = serializers.IntegerField(help_text='Идентификатор')


class DateFromDateToSerializer(serializers.Serializer):
    """Сериализатор полей дата начала и окончания действия."""

    date_from = serializers.DateField(
        format="%Y-%m-%d", required=False, allow_null=True
    )
    date_to = serializers.DateField(format="%Y-%m-%d", required=False, allow_null=True)


class AbstractModelFileSerializer(AbstractSerializer):

    def __init__(self, **kwargs: typing.Any) -> None:
        super().__init__(**kwargs)
        if not self.Meta.content_type and not self.data:
            raise base_serializers.SerializationError("content_type is required")

    class Meta:
        content_disposition = ''
        content_type = ''

    _data: io.BytesIO | None = None

    @property
    def data(self) -> dict[str, typing.Any]:
        return {
            'universe': self._data,
            'headers': {
                'Content-Disposition': self.Meta.content_disposition or None,
            },
            'content_type': self.Meta.content_type
        }
