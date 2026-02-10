from typing import Any

from django.http import HttpRequest
from rest_framework import response
from rest_framework import viewsets, mixins

from utils import serializer as serializer_utils


class BaseAbstractSingleView(mixins.ListModelMixin, viewsets.GenericViewSet):
    queryset = None
    serializer_class = None

    def list(self, request: HttpRequest, *args: Any, **kwargs: Any) -> response.Response:
        if not self.get_queryset().exists():
            return response.Response(status=404, data={'message': 'ObjectDoesNotExist'})
        instance = self.get_queryset().get()
        serializer = self.get_serializer(instance=instance)
        return response.Response(status=200, data=serializer.data)


try:
    from restdoctor.rest_framework import mixins as restdoctor_mixins, viewsets as restdoctor_viewsets


    class AbstractModelViewSet(restdoctor_viewsets.ModelViewSet, serializer_utils.CustomSerializerClassMapApiView):
        ...


    class AbstractSingleView(
        BaseAbstractSingleView,
        restdoctor_mixins.ListModelMixin,
        restdoctor_viewsets.GenericViewSet
    ):
        ...

except ImportError:

    class AbstractModelViewSet(viewsets.ModelViewSet):
        ...


    class AbstractSingleView(BaseAbstractSingleView):
        ...
