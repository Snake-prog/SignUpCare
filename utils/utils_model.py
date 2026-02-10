import traceback
import typing
from contextlib import suppress

from django.apps import apps
from django.contrib.contenttypes import fields as contenttypes_fields
from django.core import exceptions
from django.db import models, transaction
from rest_framework.utils import model_meta

from utils import utils_dto as dto_utils

GenericContext = typing.Dict[str, typing.Any]


def get_all_fields_names(*, model: type[models.Model]) -> list[str]:
    return [field.name for field in model._meta.fields]


def get_updated_fields(*, model: type[models.Model], data: dict) -> dict:
    return {
        element: data.get(element)
        for element in filter(lambda field: field in get_all_fields_names(model=model), data)
    }


def model_update(*, instance: models.Model, updated_fields: dict) -> None:
    for key, value in updated_fields.items():
        setattr(instance, key, value)
    instance.save()


def field__is_auto_now(*, field: models.Field) -> bool:
    return isinstance(field, (models.DateField, models.DateTimeField, models.TimeField)) and getattr(
        field, "auto_now", False
    )


def update_model_instance_suppressed(  # noqa: CAC001 because used DRF realisation
        *,
        instance: dto_utils.DjangoModel,
        validated_data: GenericContext,
        update_fields: list[str] | None = None,
) -> dto_utils.DjangoModel:
    info = model_meta.get_field_info(instance)
    model_fields = instance.__class__._meta.fields
    auto_fields = [field.attname for field in model_fields if field__is_auto_now(field=field)]
    # Simply set each attribute on the instance, and then save it.
    # Note that unlike `create_model_instance()` we don't need to treat many-to-many
    # relationships as being a special case. During updates we already
    # have an instance pk for the relationships to be associated with.
    m2m_fields = []
    common_fields = []
    for attr, value in validated_data.items():
        if attr in info.relations and info.relations[attr].to_many:
            m2m_fields.append((attr, value))
        else:
            setattr(instance, attr, value)
            common_fields.append(attr)
    update_fields = update_fields or common_fields
    update_fields += auto_fields
    instance.save(update_fields=update_fields)
    # Note that many-to-many fields are set after updating instance.
    # Setting m2m fields triggers signals which could potentially change
    # updated instance and we do not want it to collide with update_model_instance()
    for attr, value in m2m_fields:
        field = getattr(instance, attr)
        field.set(value)
    return instance


def create_model_instance_suppressed(  # noqa: CAC001 because used DRF realisation
        *, model_class: typing.Type[dto_utils.DjangoModel], validated_data: GenericContext
) -> dto_utils.DjangoModel:
    """
    We have a bit of extra checking around this in order to provide
    descriptive messages when something goes wrong, but this method is
    essentially just:

        return ExampleModel.objects.create(**validated_data)

    If there are many to many fields present on the instance then they
    cannot be set until the model is instantiated, in which case the
    implementation is like so:

        example_relationship = validated_data.pop('example_relationship')
        instance = ExampleModel.objects.create(**validated_data)
        instance.example_relationship = example_relationship
        return instance

    The default implementation also does not handle nested relationships.
    If you want to support writable nested relationships you'll need
    to write an explicit `create_model_instance()` method.
    """

    # Remove many-to-many relationships from validated_data.
    # They are not valid arguments to the default `.create()` method,
    # as they require that the instance has already been saved.
    info = model_meta.get_field_info(model_class)
    many_to_many = {}
    for field_name, relation_info in info.relations.items():
        if relation_info.to_many and (field_name in validated_data):
            many_to_many[field_name] = validated_data.pop(field_name)

    try:
        instance = model_class._default_manager.create(**validated_data)
    except TypeError:
        tb = traceback.format_exc()
        msg = (
            "Got a `TypeError` when calling `{model}.{manager}.create()`. "
            "This may be because you have a writable field on the "
            "serializer class that is not a valid argument to "
            "`{model}.{manager}.create()`.\nOriginal exception was:\n {traceback}".format(
                model=model_class.__name__, manager=model_class._default_manager.name, traceback=tb
            )
        )
        raise TypeError(msg)

    # Save many-to-many relationships after the instance is created.
    if many_to_many:
        for field_name, value in many_to_many.items():
            field = getattr(instance, field_name)
            field.set(value)

    return instance


def create_model_instance(
        model_class: typing.Type[dto_utils.DjangoModel], validated_data: GenericContext,
        refresh: bool = False
) -> dto_utils.DjangoModel:
    instance = create_model_instance_suppressed(
        model_class=model_class, validated_data=validated_data
    )
    if refresh:
        instance.refresh_from_db()

    return instance


def update_model_instance(
        instance: dto_utils.DjangoModel,
        validated_data: GenericContext,
        refresh: bool = False,
        update_fields: list[str] | None = None,
) -> dto_utils.DjangoModel:
    instance = update_model_instance_suppressed(
        instance=instance, validated_data=validated_data, update_fields=update_fields
    )
    if refresh:
        instance.refresh_from_db()

    return instance


def create_or_update_model_instance(
        validated_data: GenericContext,
        model_class: typing.Type[dto_utils.DjangoModel],
        refresh: bool = False,
        update_fields: list[str] | None = None,
) -> tuple[dto_utils.DjangoModel, bool]:
    with suppress(Exception):
        return (
            update_model_instance(
                instance=model_class(**validated_data),
                validated_data=validated_data,
                refresh=refresh,
                update_fields=update_fields,
            ),
            False,
        )
    return (
        create_model_instance(
            model_class=model_class, validated_data=validated_data, refresh=refresh
        ),
        True,
    )


def generate_generic_fields(ignored_attributes: list[str]) -> list[str]:
    generic_fields = []
    for model in apps.get_models():
        for field_name, field in filter(lambda x: isinstance(x[1], contenttypes_fields.GenericForeignKey),
                                        model.__dict__.items()):
            if field.get_attname() not in ignored_attributes:
                generic_fields.append(field)
    return generic_fields


def generate_blank_local_fields(primary_object: models.Model) -> set[str]:
    blank_local_fields = set()
    for field in primary_object._meta.local_fields:
        if getattr(primary_object, field.attname) in [None, '']:
            blank_local_fields.add(field.attname)
    return blank_local_fields


def save_related_objects(
        *,
        related_objects: models.QuerySet[models.Model],
        obj_varname: str,
        allow_self_relation: bool,
        ignored_attributes: list[str] | None,
        primary_object: models.Model
) -> None:
    for obj in related_objects.all():
        try:
            from django_pgviews import view as pgview
            if isinstance(obj, pgview.View):
                continue
        except ImportError:
            pass
        if obj_varname not in ignored_attributes:  # type: ignore
            if not allow_self_relation and obj == primary_object:
                continue
            try:
                setattr(obj, obj_varname, primary_object)
            except TypeError:
                continue
            try:
                obj.save()
            except (exceptions.ValidationError, NotImplementedError):
                continue


def migrate_foreign_key_to_alias_objects(
        *,
        alias_object: models.Model,
        ignored_attributes: list[str] | None,
        primary_object: models.Model,
        allow_self_relation: bool
) -> None:
    for related_object in alias_object._meta.related_objects:
        # The variable name on the alias_object model.
        alias_varname = related_object.get_accessor_name()
        # The variable name on the related model.
        obj_varname = related_object.field.name
        related_objects = getattr(alias_object, alias_varname)
        save_related_objects(
            related_objects=related_objects,
            ignored_attributes=ignored_attributes,
            primary_object=primary_object,
            allow_self_relation=allow_self_relation,
            obj_varname=obj_varname
        )


def migrate_foreign_key_to_primary_object(
        *,
        generic_fields: list[typing.Any],
        alias_object: models.Model,
        primary_object: models.Model
) -> None:
    for field in generic_fields:
        filter_kwargs = {
            field.fk_field: alias_object._get_pk_val(),
            field.ct_field: field.get_content_type(alias_object)
        }
        for generic_related_object in field.model.objects.filter(**filter_kwargs):  # type: ignore
            setattr(generic_related_object, field.name, primary_object)  # type: ignore
            generic_related_object.save()


def migrate_many_to_many_objects(
        alias_object: models.Model,
        ignored_attributes: list[str] | None,
        allow_self_relation: bool,
        primary_object: models.Model
) -> None:
    for related_many_object in alias_object._meta.many_to_many:
        alias_varname = related_many_object.get_attname()
        obj_varname = related_many_object._related_name
        related_many_objects = []
        many_objects = []
        try:
            related_many_objects = list(getattr(alias_object, obj_varname).all())
        except AttributeError:
            pass
        try:
            many_objects = list(getattr(alias_object, alias_varname).all())
        except AttributeError:
            continue
        if obj_varname in ignored_attributes:  # type: ignore
            continue
        try:
            for obj in related_many_objects:
                if (not allow_self_relation and obj != primary_object) or allow_self_relation:
                    getattr(obj, obj_varname).remove(alias_object)
                    getattr(primary_object, obj_varname).add(obj)
        except AttributeError:
            continue
        try:
            for obj in many_objects:
                if (not allow_self_relation and obj != primary_object) or allow_self_relation:
                    getattr(obj, alias_varname).remove(alias_object)
                    getattr(primary_object, alias_varname).add(obj)
        except AttributeError:
            continue


def fill_all_missing_values(
        *,
        blank_local_fields: set[str],
        alias_object: models.Model,
        primary_object: models.Model
) -> None:
    filled_up = set()
    for field_name in blank_local_fields:
        val = getattr(alias_object, field_name)
        if val not in [None, '']:
            setattr(primary_object, field_name, val)
            filled_up.add(field_name)
    blank_local_fields -= filled_up


def generate_related_fields(
        *,
        alias_objects: list[models.Model],
        ignored_attributes: list[str] | None,
        allow_self_relation: bool,
        primary_object: models.Model,
        generic_fields: list[str],
        blank_local_fields: set[str]
) -> None:
    # Loop through all alias objects and migrate their data to the primary object.
    for alias_object in alias_objects:
        # Migrate all foreign key references from alias object to primary object.
        migrate_foreign_key_to_alias_objects(
            alias_object=alias_object,
            primary_object=primary_object,
            allow_self_relation=allow_self_relation,
            ignored_attributes=ignored_attributes
        )
        migrate_many_to_many_objects(
            alias_object=alias_object,
            ignored_attributes=ignored_attributes,
            allow_self_relation=allow_self_relation,
            primary_object=primary_object
        )
        migrate_foreign_key_to_primary_object(
            generic_fields=generic_fields,
            alias_object=alias_object,
            primary_object=primary_object
        )
        fill_all_missing_values(
            blank_local_fields=blank_local_fields,
            alias_object=alias_object,
            primary_object=primary_object
        )


@transaction.atomic
def merge_model_objects(
        primary_object: models.Model,
        alias_objects: list | dto_utils.DjangoModel = [],
        keep_old: bool = False,
        allow_self_relation: bool = True,
        ignored_attributes: list[str] | None = None
) -> models.Model:
    """
    Use this function to merge model objects (i.e. Users, Organizations, Polls,
    etc.) and migrate all the related fields from the alias objects to the
    primary object.

    Usage:
    from django.contrib.auth.models import User
    primary_user = User.objects.get(email='good_email@example.com')
    duplicate_user = User.objects.get(email='good_email+duplicate@example.com')
    merge_model_objects(primary_user, duplicate_user)
    """
    if not isinstance(ignored_attributes, list):
        ignored_attributes = [ignored_attributes]  # type: ignore

    if not isinstance(alias_objects, list):
        alias_objects = [alias_objects]

    # check that all aliases are the same class as primary one and that
    # they are subclass of model
    primary_class = primary_object.__class__

    if not issubclass(primary_class, models.Model):
        raise TypeError('Only django.db.models.Model subclasses can be merged')

    for alias_object in alias_objects:
        if not isinstance(alias_object, primary_class):
            raise TypeError('Only models of same class can be merged')

    # Get a list of all GenericForeignKeys in all models
    # method to the ForeignKey field for accessing the generic related fields.
    generic_fields = generate_generic_fields(
        ignored_attributes=ignored_attributes
    )
    blank_local_fields = generate_blank_local_fields(
        primary_object=primary_object
    )

    # Loop through all alias objects and migrate their data to the primary object.
    for alias_object in alias_objects:
        # Migrate all foreign key references from alias object to primary object.
        generate_related_fields(
            alias_objects=alias_objects,
            ignored_attributes=ignored_attributes,
            allow_self_relation=allow_self_relation,
            primary_object=primary_object,
            generic_fields=generic_fields,
            blank_local_fields=blank_local_fields
        )

        if not keep_old:
            alias_object.delete()
    primary_object.save()
    return primary_object


def skip_reverse(relation: models.ForeignKey) -> models.ForeignKey:
    relation.skip_reverse = True
    return relation


def remove_reverse(relation: models.ForeignKey) -> models.ForeignKey:
    if getattr(relation, 'skip_reverse', None) is not None:
        delattr(relation, 'skip_reverse')
    return relation
