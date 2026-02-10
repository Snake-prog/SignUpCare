import os
from pathlib import Path

from configurations import Configuration, values


class Base(Configuration):
    BASE_DIR = Path(__file__).resolve().parent.parent.parent

    SECRET_KEY = values.Value(default="dev-key")

    DEBUG = values.BooleanValue(default=False)

    ALLOWED_HOSTS = ["*"]

    INSTALLED_APPS = [
        "jazzmin",
        "django.contrib.admin",
        "django.contrib.auth",
        "django.contrib.contenttypes",
        "django.contrib.sessions",
        "django.contrib.messages",
        "django.contrib.staticfiles",
        "rest_framework",
        "restdoctor",
        "django_filters",
        "corsheaders",
        "drf_yasg",
        "apps.user",
        "apps.care",
    ]

    MIDDLEWARE = [
        "django.middleware.security.SecurityMiddleware",
        "django.contrib.sessions.middleware.SessionMiddleware",
        "corsheaders.middleware.CorsMiddleware",
        "django.middleware.common.CommonMiddleware",
        "django.middleware.csrf.CsrfViewMiddleware",
        "django.contrib.auth.middleware.AuthenticationMiddleware",
        "django.contrib.messages.middleware.MessageMiddleware",
        "restdoctor.django.middleware.api_selector.ApiSelectorMiddleware",
    ]

    ROOT_URLCONF = "configuration.urls"

    TEMPLATES = [
        {
            "BACKEND": "django.template.backends.django.DjangoTemplates",
            "DIRS": [BASE_DIR / "templates"],
            "APP_DIRS": True,
            "OPTIONS": {
                "context_processors": [
                    "django.template.context_processors.debug",
                    "django.template.context_processors.request",
                    "django.contrib.auth.context_processors.auth",
                    "django.contrib.messages.context_processors.messages",
                ],
            },
        },
    ]

    WSGI_APPLICATION = "configuration.wsgi.application"

    REST_FRAMEWORK = {
        "DATETIME_FORMAT": "%s",  # for using date and time in timestamp
        "DEFAULT_AUTHENTICATION_CLASSES": [
            "rest_framework.authentication.BasicAuthentication",
            "rest_framework.authentication.SessionAuthentication",
        ],
        "DEFAULT_RENDERER_CLASSES": [
            "rest_framework.renderers.JSONRenderer",
            "rest_framework.renderers.BrowsableAPIRenderer",
        ],
        "EXCEPTION_HANDLER": "restdoctor.rest_framework.exception_handlers.exception_handler",
    }

    AUTHENTICATION_BACKENDS = [
        "django.contrib.auth.backends.ModelBackend",
    ]

    DATABASES = {
        "default": {"ENGINE": "django.db.backends.sqlite3", "NAME": BASE_DIR / "db.sqlite3"}
    }

    AUTH_USER_MODEL = "user.User"

    AUTH_PASSWORD_VALIDATORS = [
        {
            "NAME": "django.contrib.auth.password_validation.UserAttributeSimilarityValidator",
        },
        {
            "NAME": "django.contrib.auth.password_validation.MinimumLengthValidator",
        },
        {
            "NAME": "django.contrib.auth.password_validation.CommonPasswordValidator",
        },
        {
            "NAME": "django.contrib.auth.password_validation.NumericPasswordValidator",
        },
    ]

    LANGUAGE_CODE = "ru"

    TIME_ZONE = "UTC"

    USE_I18N = True

    USE_TZ = True
    LOGIN_URL = "user:login"

    STATIC_URL = "admin/static/"
    MEDIA_ROOT = BASE_DIR / "media/"
    MEDIA_URL = "api/media/"
    STATIC_ROOT = os.path.join(BASE_DIR, "static")

    STATICFILES_DIRS = (os.path.join(BASE_DIR, "apps\\static"),)

    DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"

    CORS_ORIGIN_ALLOW_ALL = True
    CORS_ALLOW_HEADERS = (  # noqa: static object
        "x-requested-with",
        "universe-type",
        "accept",
        "origin",
        "authorization",
        "x-csrftoken",
        "token",
        "x-device-id",
        "x-device-type",
        "x-push-id",
        "dataserviceversion",
        "maxdataserviceversion",
        "universe-disposition",
    )

    CORS_ALLOW_METHODS = ("GET", "POST", "PUT", "PATCH", "DELETE", "OPTIONS")
    CORS_ORIGIN_WHITELIST = values.ListValue(
        [
            "http://127.0.0.1:3000",
            "http://0.0.0.0:3000",
            "http://localhost:3000",
            "https://realdomain",
        ]
    )

    @property
    def CACHES(self) -> dict:
        return {
            "default": {  # noqa: static object
                "BACKEND": "django.core.cache.backends.locmem.LocMemCache",
                "LOCATION": "legacy-local-cache",
            },
        }

    API_DEFAULT_OPENAPI_VERSION = values.Value("3.0.2")
    API_V1_URLCONF = values.Value("configuration.urls")
    API_VENDOR_STRING = values.Value("signupcare")
    API_FALLBACK_VERSION = values.Value("fallback")
    API_DEFAULT_VERSION = values.Value("v1")
    API_DEFAULT_FORMAT = values.Value("full")
    API_PREFIXES = values.TupleValue(
        (
            "/api"
        )
    )
    API_FORMATS = values.TupleValue(("full", "compact"))
    API_RESOURCE_DISCRIMINATIVE_PARAM = values.Value("view_type")
    API_RESOURCE_DEFAULT = values.Value("common")
    API_RESOURCE_SET_PARAM = values.BooleanValue(False)
    API_RESOURCE_SET_PARAM_FOR_DEFAULT = values.BooleanValue(False)

    API_FALLBACK_URLCONF = values.Value("configuration.urls")

    SITE_ID = 1
    site_name = "SignUpCare"
    logo = "logo.svg"

    JAZZMIN_SETTINGS: dict = {
        "show_ui_builder": False,
        "site_title": site_name,
        "site_header": site_name,
        "site_brand": site_name,
        "site_logo": logo,
        "login_logo": logo,
        "login_logo_dark": logo,
        "site_logo_classes": "img-clear",
        "site_icon": logo,
        "welcome_sign": "Welcome to the admin panel of " + site_name,
        "copyright": site_name,
        "user_avatar": "avatar",
        #############
        # Side Menu #
        #############
        "show_sidebar": True,
        "navigation_expanded": True,
        "hide_apps": [
            "django_celery_beat",
            "django_celery_results",
        ],
        "hide_models": [],
        "topmenu_links": [
            {"app": "django_celery_beat"},
        ],
        "usermenu_links": [],
        "order_with_respect_to": [],
        # https://fontawesome.com/v5/search?ic=free&o=r
        # for the full list of 5.13.0 free icon classes
        "icons": {},
        "default_icon_parents": "fas fa-chevron-circle-right",
        "default_icon_children": "fas fa-circle",
        #################
        # Related Modal #
        #################
        "related_modal_active": True,
        #############
        # UI Tweaks #
        #############
        "custom_css": "jazzmin.css",
        "custom_js": "",
        "use_google_fonts_cdn": True,
        ###############
        # Change view #
        ###############
        # - single
        # - horizontal_tabs (default)
        # - vertical_tabs
        # - collapsible
        # - carousel
        "changeform_format": "horizontal_tabs",
        "changeform_format_overrides": {
            "auth.user": "horizontal_tabs",
            "auth.group": "horizontal_tabs",
        },
    }

    JAZZMIN_UI_TWEAKS = {
        "navbar_small_text": False,
        "footer_small_text": False,
        "body_small_text": False,
        "brand_small_text": False,
        "brand_colour": "navbar-dark-navy",
        "accent": "accent-navy",
        "navbar": "navbar-navy navbar-dark",
        "no_navbar_border": True,
        "navbar_fixed": False,
        "layout_boxed": False,
        "footer_fixed": False,
        "sidebar_fixed": False,
        "sidebar": "sidebar-light-navy",
        "sidebar_nav_small_text": False,
        "sidebar_disable_expand": False,
        "sidebar_nav_child_indent": True,
        "sidebar_nav_compact_style": True,
        "sidebar_nav_legacy_style": False,
        "sidebar_nav_flat_style": False,
        "theme": "minty",
        "dark_mode_theme": None,
        "button_classes": {
            "primary": "btn-primary",
            "secondary": "btn-secondary",
            "info": "btn-info",
            "warning": "btn-warning",
            "danger": "btn-danger",
            "success": "btn-success",
        },
        "actions_sticky_top": True,
    }
