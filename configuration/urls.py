from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import include, path
from drf_yasg import openapi
from drf_yasg.views import get_schema_view

from configuration.router import router

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/', include(router.urls)),
    path(
        'documentation/',
        get_schema_view(
            openapi.Info(
                title=" API",
                default_version='',
                description="",
                terms_of_service="https://www.google.com/policies/terms/",
                contact=openapi.Contact(email="youth.prodigy.main@gmail.com"),
                license=openapi.License(name="BSD License"),
            ),
            public=True,
            # permission_classes=(permissions.AllowAny,),
        ).with_ui('redoc', cache_timeout=0),
        name='swagger',
    ),
    path('', include("apps.user.gui.urls", namespace='user')),
    path('', include("apps.care.gui.urls", namespace='care')),
]
if settings.DEBUG:
    urlpatterns += static(prefix=settings.STATIC_URL, document_root=settings.STATIC_ROOT)
    urlpatterns += static(prefix=settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
