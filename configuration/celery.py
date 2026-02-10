import os
import typing

from celery import Celery
from configurations import importer
from django.conf import settings
from dotenv import load_dotenv

load_dotenv()
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "configuration.settings")
if not os.environ.get("DJANGO_CONFIGURATION", None):
    os.environ.setdefault("DJANGO_CONFIGURATION", "Development")

importer.install()
app = Celery("configuration.celery")
app.config_from_object("django.conf:settings", namespace="CELERY")
app.autodiscover_tasks(settings.INSTALLED_APPS, related_name="tasks")
app.conf.broker_connection_retry_on_startup = True


@app.task(bind=True, ignore_result=True)
def debug_task(self: typing.Any) -> None:
    print(f'Request: {self.request!r}')
