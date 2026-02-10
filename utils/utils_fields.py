import datetime
import typing

import django_filters
from django import forms
from django.core import exceptions, validators, files
from django.db import models
from django.utils import dateparse
from django.utils.duration import duration_string as base_duration_string
from django_filters import fields as filter_fields
from rest_framework import ISO_8601
from rest_framework import fields as rest_fields
from rest_framework.settings import api_settings
from rest_framework.utils import humanize_datetime


def validate_image_or_svg_file_extension(value: files.File) -> None:
    allowed_extensions = validators.get_available_image_extensions()
    # noinspection PyUnresolvedReferences
    allowed_extensions.append("svg")
    validators.FileExtensionValidator(allowed_extensions=allowed_extensions)(value)


class ImageOrSVGField(models.ImageField):
    default_validators = [validate_image_or_svg_file_extension]

    def pre_save(self, model_instance: models.Model, add: typing.Any) -> super:
        return super().pre_save(model_instance=model_instance, add=add)


class DateTimeField(rest_fields.DateTimeField):

    # noinspection D
    def to_internal_value(self, value: str | float | int) -> datetime.datetime | typing.Any:
        input_formats = getattr(self, 'input_formats', api_settings.DATETIME_INPUT_FORMATS)

        if isinstance(value, datetime.date) and not isinstance(value, datetime.datetime):
            self.fail('date')

        if isinstance(value, datetime.datetime):
            return self.enforce_timezone(value)

        for input_format in input_formats:
            if input_format.lower() == ISO_8601:
                try:
                    parsed = dateparse.parse_datetime(value)
                    if parsed is not None:
                        return self.enforce_timezone(parsed)
                except (ValueError, TypeError):
                    pass
            elif input_format.lower() == "%s":
                try:
                    parsed = datetime.datetime.fromtimestamp(float(value))
                    return self.enforce_timezone(parsed)
                except (ValueError, TypeError, OSError):
                    pass
            else:
                try:
                    parsed = self.datetime_parser(value, input_format)
                    return self.enforce_timezone(parsed)
                except (ValueError, TypeError):
                    pass

        humanized_format = humanize_datetime.datetime_formats(input_formats)
        self.fail('invalid', format=humanized_format)
        return None

    def to_representation(
            self, value: datetime.datetime,
    ) -> typing.Union[typing.Optional[str], datetime.datetime]:
        if not value:
            return None

        output_format = getattr(self, 'format', api_settings.DATETIME_FORMAT)

        if output_format is None or isinstance(value, str):
            return value

        value = self.enforce_timezone(value)

        if output_format.lower() == ISO_8601:
            value = value.isoformat(timespec='microseconds')
            return value
        if output_format.lower() == "%s":
            return value.timestamp()
        return value.strftime(output_format)


def field_get_min_max(*, model: typing.Type[models.Model], field_name: str) -> tuple[int | None, int | None]:
    field = model._meta.get_field(field_name)
    if not isinstance(field, (models.IntegerField, models.PositiveIntegerField)):
        raise TypeError('Поле должно быть числовым')
    _validators = field.validators
    max_value = None
    min_value = None
    for validator in _validators:
        if isinstance(validator, validators.MinValueValidator):
            min_value = validator.limit_value
        if isinstance(validator, validators.MaxValueValidator):
            max_value = validator.limit_value

    return min_value, max_value


def duration_string(duration: datetime.timedelta, _format: str | None = None) -> str | float:
    """Version of str(timedelta) which is not English specific."""
    if _format == '%s':
        return duration.total_seconds()
    return base_duration_string(duration=duration)


def parse_duration(value: str, _format: str | None = None) -> datetime.timedelta:
    if _format == '%s':
        return datetime.timedelta(seconds=float(value))
    return dateparse.parse_duration(value=value)


class DurationField(rest_fields.DurationField):

    def __init__(self, **kwargs: dict) -> None:
        self.format = kwargs.pop('format', None)
        super().__init__(**kwargs)

    def to_internal_value(self, value: typing.Any) -> datetime.timedelta | None:
        if isinstance(value, datetime.timedelta):
            return value
        parsed = parse_duration(str(value), _format=str(self.format))
        if parsed is not None:
            return parsed
        self.fail('invalid', format='[DD] [HH:[MM:]]ss[.uuuuuu]')
        return None

    def to_representation(self, value: datetime.timedelta) -> str | float:
        return duration_string(duration=value, _format=str(self.format))


class FormDurationField(forms.DurationField):
    def __init__(self, **kwargs: dict) -> None:
        self.format = kwargs.pop('format', None)
        super().__init__(**kwargs)

    def prepare_value(self, value: typing.Any) -> str | float:
        if isinstance(value, datetime.timedelta):
            return duration_string(value, _format=str(self.format))
        return value

    def to_python(self, value: typing.Any) -> datetime.timedelta | None:
        if value in self.empty_values:
            return None
        if isinstance(value, datetime.timedelta):
            return value
        try:
            value = parse_duration(str(value))
        except OverflowError:
            raise exceptions.ValidationError(
                self.error_messages["overflow"].format(
                    min_days=datetime.timedelta.min.days,
                    max_days=datetime.timedelta.max.days,
                ),
                code="overflow",
            )
        if value is None:
            raise exceptions.ValidationError(self.error_messages["invalid"], code="invalid")
        return value


class DurationFilter(django_filters.DurationFilter):
    field_class = FormDurationField


class DurationRangeFilter(django_filters.Filter):
    field_class = filter_fields.RangeField

    def filter(
            self,
            qs: models.QuerySet,
            value: typing.Any
    ) -> models.QuerySet:
        if value:
            if value.start is not None and value.stop is not None:
                self.lookup_expr = "range"
                value = (
                    datetime.timedelta(
                        seconds=float(value.start)
                    ),
                    datetime.timedelta(
                        seconds=float(value.stop)
                    )
                )
            elif value.start is not None:
                self.lookup_expr = "gte"
                value = datetime.timedelta(seconds=float(value.start))
            elif value.stop is not None:
                self.lookup_expr = "lte"
                value = datetime.timedelta(seconds=float(value.stop))
        return super().filter(qs, value)


try:
    from django.contrib.gis import measure, geos


    class DistanceField(forms.CharField):

        def __init__(
                self,
                *,
                separator: str = ';',
                empty_value: tuple[geos.Point, measure.D] = (geos.Point(), measure.D()),
                **kwargs: dict
        ) -> None:
            self.separator = separator
            self.empty_value: tuple[geos.Point, measure.D] = empty_value
            self.lat = None
            self.lon = None
            self.rad = None
            self.point = geos.Point()
            self.distance = measure.D()
            super().__init__(**kwargs)
            # self.validators.append(validators.ProhibitNullCharactersValidator())

        def to_python(self, value: str) -> str | None | tuple[geos.Point, measure.Distance]:
            """Return a string."""
            if value not in self.empty_values:
                value = str(value)
            if value in self.empty_values:
                return self.empty_value
            attrs = value.split(sep=self.separator)

            for attr in attrs:
                try:
                    setattr(self, attr.split(sep='=')[0], float(attr.split(sep='=')[1]))
                except ValueError:
                    exceptions.ValidationError('Неверный формат ввода')
            if self.lat and self.lon:
                self.point = geos.Point(x=self.lat, y=self.lon, srid=4326)
            if self.rad:
                self.distance = measure.D(m=self.rad)
            return self.point, self.distance


    class DistanceFilter(django_filters.CharFilter):
        field_class = DistanceField
except exceptions.ImproperlyConfigured:
    pass
