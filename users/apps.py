from django.apps import AppConfig

from team_finder.constants import APP_VERBOSE_NAME_USERS


class UsersConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "users"
    verbose_name = APP_VERBOSE_NAME_USERS
