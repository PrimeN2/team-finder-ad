from django.conf import settings
from django.db import models

from team_finder.constants import (
    FIELD_VERBOSE_NAME_AUTHOR,
    FIELD_VERBOSE_NAME_CREATED_AT,
    FIELD_VERBOSE_NAME_DESCRIPTION,
    FIELD_VERBOSE_NAME_GITHUB,
    FIELD_VERBOSE_NAME_PARTICIPANTS,
    FIELD_VERBOSE_NAME_PROJECT_NAME,
    FIELD_VERBOSE_NAME_STATUS,
    MODEL_VERBOSE_NAME_PROJECT,
    MODEL_VERBOSE_NAME_PROJECTS,
    PROJECT_NAME_MAX_LENGTH,
    PROJECT_STATUS_MAX_LENGTH,
)


class Project(models.Model):
    STATUS_OPEN = "open"
    STATUS_CLOSED = "closed"
    STATUS_CHOICES = (
        (STATUS_OPEN, "Open"),
        (STATUS_CLOSED, "Closed"),
    )

    name = models.CharField(
        FIELD_VERBOSE_NAME_PROJECT_NAME,
        max_length=PROJECT_NAME_MAX_LENGTH,
    )
    description = models.TextField(FIELD_VERBOSE_NAME_DESCRIPTION, blank=True)
    owner = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="owned_projects",
        verbose_name=FIELD_VERBOSE_NAME_AUTHOR,
    )
    created_at = models.DateTimeField(
        FIELD_VERBOSE_NAME_CREATED_AT,
        auto_now_add=True,
    )
    github_url = models.URLField(FIELD_VERBOSE_NAME_GITHUB, blank=True)
    status = models.CharField(
        FIELD_VERBOSE_NAME_STATUS,
        max_length=PROJECT_STATUS_MAX_LENGTH,
        choices=STATUS_CHOICES,
        default=STATUS_OPEN,
    )
    participants = models.ManyToManyField(
        settings.AUTH_USER_MODEL,
        related_name="participated_projects",
        blank=True,
        verbose_name=FIELD_VERBOSE_NAME_PARTICIPANTS,
    )

    class Meta:
        ordering = ("-created_at", "-id")
        verbose_name = MODEL_VERBOSE_NAME_PROJECT
        verbose_name_plural = MODEL_VERBOSE_NAME_PROJECTS

    def __str__(self):
        return self.name
