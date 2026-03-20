import os
from celery import Celery
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "hrm_service.settings.prod")
app = Celery("hrm_service")
app.config_from_object("django.conf:settings", namespace="CELERY")
app.autodiscover_tasks()
