from django.contrib.auth.models import AbstractBaseUser, PermissionsMixin
from django.db import models

from team_finder.constants import (
    FIELD_VERBOSE_NAME_ABOUT,
    FIELD_VERBOSE_NAME_AVATAR,
    FIELD_VERBOSE_NAME_EMAIL,
    FIELD_VERBOSE_NAME_FAVORITES,
    FIELD_VERBOSE_NAME_GITHUB,
    FIELD_VERBOSE_NAME_IS_ACTIVE,
    FIELD_VERBOSE_NAME_IS_STAFF,
    FIELD_VERBOSE_NAME_NAME,
    FIELD_VERBOSE_NAME_PHONE,
    FIELD_VERBOSE_NAME_SURNAME,
    MODEL_VERBOSE_NAME_USER,
    MODEL_VERBOSE_NAME_USERS,
    USER_ABOUT_MAX_LENGTH,
    USER_NAME_MAX_LENGTH,
    USER_PHONE_MAX_LENGTH,
)
from users.managers import UserManager
from users.utils import generate_avatar


class User(AbstractBaseUser, PermissionsMixin):
    email = models.EmailField(FIELD_VERBOSE_NAME_EMAIL, unique=True)
    name = models.CharField(FIELD_VERBOSE_NAME_NAME, max_length=USER_NAME_MAX_LENGTH)
    surname = models.CharField(
        FIELD_VERBOSE_NAME_SURNAME,
        max_length=USER_NAME_MAX_LENGTH,
    )
    avatar = models.ImageField(
        FIELD_VERBOSE_NAME_AVATAR,
        upload_to="avatars/",
        blank=True,
    )
    phone = models.CharField(
        FIELD_VERBOSE_NAME_PHONE,
        max_length=USER_PHONE_MAX_LENGTH,
    )
    github_url = models.URLField(FIELD_VERBOSE_NAME_GITHUB, blank=True)
    about = models.TextField(
        FIELD_VERBOSE_NAME_ABOUT,
        max_length=USER_ABOUT_MAX_LENGTH,
        blank=True,
    )
    is_active = models.BooleanField(FIELD_VERBOSE_NAME_IS_ACTIVE, default=True)
    is_staff = models.BooleanField(FIELD_VERBOSE_NAME_IS_STAFF, default=False)
    favorites = models.ManyToManyField(
        "projects.Project",
        related_name="interested_users",
        blank=True,
        verbose_name=FIELD_VERBOSE_NAME_FAVORITES,
    )

    objects = UserManager()

    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = ["name", "surname", "phone"]

    class Meta:
        verbose_name = MODEL_VERBOSE_NAME_USER
        verbose_name_plural = MODEL_VERBOSE_NAME_USERS

    def ensure_avatar(self):
        if self.avatar:
            return
        self.avatar = generate_avatar(self.name)

    def __str__(self):
        full_name = f"{self.name} {self.surname}".strip()
        return full_name or self.email
