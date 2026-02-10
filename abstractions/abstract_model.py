import typing
import uuid

from django.db import models
from django.utils.translation import gettext_lazy as _

try:
    import solo.models as solo_models


    class AbstractBaseSoloModel(solo_models.SingletonModel):

        class Meta:
            abstract = True

        def save(
                self,
                force_insert: bool = False,
                force_update: bool = False,
                using: typing.Any | None = None,
                update_fields: typing.Any | None = None,
        ) -> None:
            self.full_clean()
            super().save(force_insert=force_insert, force_update=force_update, using=using, update_fields=update_fields)
except ImportError:
    pass


class AbstractBaseModel(models.Model):
    class Meta:
        abstract = True

    def save(
            self,
            force_insert: bool = False,
            force_update: bool = False,
            using: typing.Any | None = None,
            update_fields: typing.Any | None = None,
            **kwargs
    ) -> None:
        self.full_clean()
        super().save(
            force_insert=force_insert,
            force_update=force_update,
            using=using,
            update_fields=update_fields,
        )


class UUIDModel(AbstractBaseModel):
    class Meta:
        abstract = True

    uuid = models.UUIDField(
        help_text=_("UUID"),
        verbose_name=_("UUID"),
        default=uuid.uuid4,
        editable=False,
        unique=True,
    )


class DatedModel(AbstractBaseModel):
    class Meta:
        abstract = True

    created_at = models.DateTimeField(
        help_text=_("creation date"),
        verbose_name=_("creation date"),
        auto_now_add=True,
        editable=False,
    )
    updated_at = models.DateTimeField(
        help_text=_("update date"),
        verbose_name=_("update date"),
        auto_now=True,
        editable=False,
    )
