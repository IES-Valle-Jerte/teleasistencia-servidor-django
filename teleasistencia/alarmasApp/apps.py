from django.apps import AppConfig, apps
from django.db.models import Q
from django.utils.timezone import now


class AlarmasAppConfig(AppConfig):
    """
    Documentación django signals: https://docs.djangoproject.com/en/3.2/topics/signals/
    """
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'alarmasApp'