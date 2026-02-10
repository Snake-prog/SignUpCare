import typing

from rest_framework import permissions


def get_permission_classes_from_map(
        action: str,
        permission_classes_map: typing.Any,
        default_permission_classes: list[permissions.BasePermission],
) -> list[permissions.BasePermission]:
    permission_classes = permission_classes_map.get(
        'default', {'permissions_list': default_permission_classes}
    ).get(
        'permissions_list', {'permissions_list': default_permission_classes}
    )
    return permission_classes_map.get(
        action, {'permissions_list': permission_classes}
    ).get('permissions_list', permission_classes)


try:
    from restdoctor.rest_framework import views


    class CustomSerializerClassMapApiView(views.SerializerClassMapApiView):
        @property
        def get_permissions(self) -> typing.List[permissions.BasePermission]:
            permission_classes = get_permission_classes_from_map(
                action=self.get_action(),
                permission_classes_map=getattr(self, 'permission_classes_map', {}),
                default_permission_classes=self.permission_classes,
            )
            # noinspection PyCallingNonCallable
            return [_permission() for _permission in permission_classes]
except ImportError:
    from rest_framework import generics


    class CustomSerializerClassMapApiView(generics.GenericAPIView):
        def get_action(self) -> str:
            action = getattr(self, 'action', None)
            if action:
                return action
            if self.request:
                return self.request.method.lower()
            return 'default'

        @property
        def get_permissions(self) -> typing.List[permissions.BasePermission]:
            permission_classes = get_permission_classes_from_map(
                action=self.get_action(),
                permission_classes_map=getattr(self, 'permission_classes_map', {}),
                default_permission_classes=self.permission_classes,
            )
            # noinspection PyCallingNonCallable
            return [_permission() for _permission in permission_classes]
