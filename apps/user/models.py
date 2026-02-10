from django.contrib.auth import (
    models as auth_models,
    validators as auth_validators,
    base_user
)
from django.core import validators
from django.db import models
from django.utils import timezone
from django.utils.translation import gettext_lazy as _

from abstractions import abstract_model
from apps.user.logic.interactors import user as user_interactors


class GroupManager(auth_models.GroupManager):
    pass


class Group(auth_models.Group, abstract_model.UUIDModel, abstract_model.DatedModel):
    class Meta:
        verbose_name = _("group")
        verbose_name_plural = _("groups")
        default_related_name = "groups"

    objects = GroupManager()


class PermissionsMixin(auth_models.PermissionsMixin):
    groups = models.ManyToManyField(
        help_text=_(
            "The groups this user belongs to. A user will get all permissions "
            "granted to each of their groups."
        ),
        verbose_name=_("groups"),
        to=Group,
        related_name="users",
        related_query_name="user",
        blank=True,
    )
    is_active = models.BooleanField(
        help_text=_(
            "Designates whether this user should be treated as active. "
            "Unselect this instead of deleting accounts."
        ),
        verbose_name=_("active"),
        default=False
    )

    def has_module_perms(self, app_label: str) -> bool:
        if self.is_active and self.is_superuser:
            return True
        try:
            # noinspection PyUnresolvedReferences,PyProtectedMember
            return auth_models._user_has_module_perms(self, app_label)
        except ValueError:
            return False

    class Meta:
        abstract = True


class UserManager(base_user.BaseUserManager):

    def create_superuser(self, email: str, password: str) -> base_user.AbstractBaseUser:
        """

        """
        if not email:
            raise ValueError(_("Username cannot be empty."))

        user = self.model(email=email)
        user.set_password(password)

        user.is_superuser = True
        user.is_admin = True
        user.is_active = True
        user.save(using=self._db)
        return user


class User(base_user.AbstractBaseUser, PermissionsMixin, abstract_model.UUIDModel, abstract_model.DatedModel):
    class Meta:
        verbose_name = _("user")
        verbose_name_plural = _("users")
        default_related_name = "users"

    username_validator = auth_validators.UnicodeUsernameValidator()

    is_admin = models.BooleanField(
        help_text=_("Designates whether the user can log into this admin site."),
        verbose_name=_("staff status"),
        default=False
    )

    email = models.EmailField(
        help_text=_(
            "Required."
        ),
        verbose_name=_("email"),
        unique=True,
        error_messages={
            "unique": _("A user with that email already exists."),
        },
    )
    phone = models.CharField(
        verbose_name="Номер телефона",
        help_text="Номер телефона",
        max_length=13,
        validators=(
            validators.RegexValidator(
                r'(\+7|7|8)?[\s\-]?\(?[1-9][0-9]{2}\)?[\s\-]?[0-9]{3}[\s\-]?[0-9]{2}[\s\-]?[0-9]{2}'
            ),
        ),
        null=True,
        blank=True,
    )
    name = models.CharField(
        verbose_name=_("name"),
        help_text=_("name"),
        max_length=150,
        null=True,
        blank=True,
    )
    passport = models.CharField(
        verbose_name=_("паспорт"),
        help_text=_("паспорт"),
        max_length=150,
        validators=(
            validators.RegexValidator(
                r'\d{4}\s?\d{6}'
            ),
        ),
        null=True,
        blank=True,
    )
    policy = models.CharField(
        verbose_name=_("полис ОМС"),
        help_text=_("полис ОМС"),
        max_length=150,
        validators=(
            validators.RegexValidator(
                r'(\d{4}\s?){4}'
            ),
        ),
        null=True,
        blank=True,
    )
    last_login = models.DateTimeField(
        help_text=_("last login"),
        verbose_name=_("last login"),
        auto_now=True
    )
    date_joined = models.DateTimeField(
        help_text=_("date joined"),
        verbose_name=_("User registration date"),
        default=timezone.now
    )

    USERNAME_FIELD = "email"
    objects = UserManager()

    @property
    def is_staff(self) -> bool:
        return self.is_admin

    def clean(self) -> None:
        if self.phone:
            self.phone = user_interactors.normalize_phone(phone=self.phone)
        if self.passport:
            self.passport = user_interactors.normalize_passport(passport=self.passport)
        if self.policy:
            self.policy = user_interactors.normalize_policy(policy=self.policy)
        return super().clean()
