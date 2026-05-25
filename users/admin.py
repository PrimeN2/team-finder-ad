from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.contrib.auth.forms import AdminPasswordChangeForm
from django.contrib.auth.models import Group

from users.forms import AdminUserCreationForm, AdminUserChangeForm
from users.models import User


@admin.register(User)
class UserAdmin(BaseUserAdmin):
    add_form = AdminUserCreationForm
    form = AdminUserChangeForm
    change_password_form = AdminPasswordChangeForm
    list_display = ("email", "name", "surname", "is_active", "is_staff")
    list_filter = ("is_active", "is_staff", "is_superuser")
    ordering = ("-id",)
    readonly_fields = ("last_login",)
    fieldsets = (
        (
            None,
            {
                "fields": (
                    "email",
                    "password",
                    "name",
                    "surname",
                    "avatar",
                    "phone",
                    "github_url",
                    "about",
                )
            },
        ),
        (
            "Права",
            {"fields": ("is_active", "is_staff", "is_superuser", "groups")},
        ),
        ("Избранное", {"fields": ("favorites",)}),
        ("Служебное", {"fields": ("last_login",)}),
    )
    add_fieldsets = (
        (
            None,
            {
                "classes": ("wide",),
                "fields": ("email", "name", "surname", "password1", "password2"),
            },
        ),
    )
    search_fields = ("email", "name", "surname", "phone")
    filter_horizontal = ("groups", "user_permissions", "favorites")


admin.site.unregister(Group)
