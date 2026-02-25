from django import forms
from django.contrib import admin
from django.contrib.auth import (
    admin as auth_admin,
    models as auth_models,
)
from django.core.handlers import wsgi
from django.db import models
from django.utils.translation import gettext_lazy as _

from abstractions import abstract_admin
from apps.user import models as user_models


@admin.register(user_models.User)
class UserAdmin(auth_admin.UserAdmin, abstract_admin.AbstractAdmin):
    # noinspection PyUnresolvedReferences
    fieldsets = (
        (
            "",
            {
                "fields": (
                    "email",
                    "password",
                )
            }
        ),
        (
                _("personal information"),
                {
                    "fields": (
                        "phone",
                        "name",
                        "passport",
                        "policy",
                    )
                }
        ),
        (
            _("permissions"),
            {
                "fields": (
                    "is_active",
                    "is_admin",
                    "is_superuser",
                    "groups",
                    "user_permissions",
                ),
            },
        ),
        (
            _("readonly information"),
            {
                "fields": (
                    "id",
                    "last_login",
                    "date_joined",
                )
            }
        ),
    )
    readonly_fields = (
        "id",
        "last_login",
        "date_joined",
    )
    list_display = (
        "email",
        "is_admin",
        "is_active",
        "last_login",
    )
    list_filter = (
        "is_admin",
        "is_active",
        "groups"
    )
    search_fields = (
        "email",
        "phone"
    )
    ordering = ("date_joined",)
    actions = (
        "make_disadmin",
        "make_admin",
        "make_active",
        "make_banned",
    )

    # noinspection PyUnusedLocal
    @admin.action(description=_("revoke administrator rights"))
    def make_disadmin(self, request: wsgi.WSGIRequest, queryset: models.QuerySet[user_models.User]) -> None:
        queryset.update(is_admin=False, is_superuser=False)

    # noinspection PyUnusedLocal
    @admin.action(description=_("grant administrator rights"))
    def make_admin(self, request: wsgi.WSGIRequest, queryset: models.QuerySet[user_models.User]) -> None:
        queryset.update(is_admin=True, is_superuser=True)

    # noinspection PyUnusedLocal
    @admin.action(description=_("activate"))
    def make_active(self, request: wsgi.WSGIRequest, queryset: models.QuerySet[user_models.User]) -> None:
        queryset.update(is_active=True)

    # noinspection PyUnusedLocal
    @admin.action(description=_("deactivate"))
    def make_banned(self, request: wsgi.WSGIRequest, queryset: models.QuerySet[user_models.User]) -> None:
        queryset.update(is_active=False)


admin.site.unregister(auth_models.Group)


@admin.register(user_models.Group)
class GroupAdmin(abstract_admin.AbstractAdmin):
    search_fields = ("name",)
    ordering = ("name",)
    filter_horizontal = ("permissions",)
    list_display = (
        "name",
    )
    fieldsets = (
        (
            "",
            {
                "fields": (
                    "name",
                )
            }
        ),
        (
            _("permissions"),
            {
                "fields": (
                    "permissions",
                ),
            },
        ),
        (
            _("readonly information"),
            {
                "fields": (
                    "id",
                    "uuid",
                    "created_at",
                    "updated_at",
                )
            }
        ),
    )
    readonly_fields = (
        "id",
        "uuid",
        "created_at",
        "updated_at",
    )

    def formfield_for_manytomany(
            self,
            db_field: models.ManyToManyField,
            request: wsgi.WSGIRequest | None = None,
            queryset: models.QuerySet | None = None,
            **kwargs: dict
    ) -> forms.ModelMultipleChoiceField | None:
        if db_field.name == "permissions":
            queryset = queryset or db_field.remote_field.model.objects
            kwargs["queryset"] = queryset.select_related("content_type")  # noqa: PEP 484
        return super().formfield_for_manytomany(db_field, request=request, **kwargs)
