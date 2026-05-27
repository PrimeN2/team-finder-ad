from django.apps import AppConfig

from team_finder.constants import APP_VERBOSE_NAME_PROJECTS


class ProjectsConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "projects"
    verbose_name = APP_VERBOSE_NAME_PROJECTS
