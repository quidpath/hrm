from django.apps import AppConfig


class CoreConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "hrm_service.core"
    label = "hrm_core"
    verbose_name = "Core (base models, utils, services)"
