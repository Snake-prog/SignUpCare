from django.contrib import admin
from django.core.handlers import wsgi
from django.db import models

try:
    from solo import admin as solo_admin


    class AbstractSoloAdmin(solo_admin.SingletonModelAdmin):
        ...
except ImportError:
    pass


class AbstractAdmin(admin.ModelAdmin):
    ...


class AbstractStackedInline(admin.StackedInline):
    ...


class ReadOnlyStackedInline(AbstractStackedInline):

    def has_change_permission(self, request: wsgi.WSGIRequest, obj: models.Model = None) -> bool:
        return False

    def has_add_permission(self, request: wsgi.WSGIRequest, obj: models.Model = None) -> bool:
        return False

    def has_delete_permission(self, request: wsgi.WSGIRequest, obj: models.Model = None) -> bool:
        return False
