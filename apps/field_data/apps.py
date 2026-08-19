from django.apps import AppConfig


class FieldDataConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "apps.field_data"
    label = "field_data"
    verbose_name = "Field Data (KoboToolBox)"