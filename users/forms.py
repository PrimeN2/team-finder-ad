from django import forms
from django.contrib.auth import authenticate
from django.contrib.auth.forms import (
    ReadOnlyPasswordHashField,
    SetPasswordForm,
)
from django.core.exceptions import ValidationError

from users.models import User
from users.utils import is_github_url, normalize_phone


class StyledFormMixin:
    def apply_styles(self):
        for field in self.fields.values():
            field.widget.attrs.setdefault("class", "form-input")


class RegistrationForm(StyledFormMixin, forms.ModelForm):
    password = forms.CharField(
        label="Пароль",
        widget=forms.PasswordInput(attrs={"autocomplete": "new-password"}),
    )

    class Meta:
        model = User
        fields = ("name", "surname", "email", "phone", "password")
        labels = {
            "name": "Имя",
            "surname": "Фамилия",
            "email": "Email",
            "phone": "Телефон",
        }
        widgets = {
            "name": forms.TextInput(),
            "surname": forms.TextInput(),
            "email": forms.EmailInput(attrs={"autocomplete": "email"}),
            "phone": forms.TextInput(),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.apply_styles()

    def save(self, commit=True):
        cleaned_data = self.cleaned_data
        user = User.objects.create_user(
            email=cleaned_data["email"],
            password=cleaned_data["password"],
            name=cleaned_data["name"],
            surname=cleaned_data["surname"],
            phone=cleaned_data["phone"],
        )
        return user

    def clean_phone(self):
        try:
            normalized_phone = normalize_phone(
                self.cleaned_data.get("phone", ""),
            )
        except ValueError as error:
            raise ValidationError(str(error)) from error
        if User.objects.filter(phone=normalized_phone).exists():
            raise ValidationError(
                "Пользователь с таким номером телефона уже существует.",
            )
        return normalized_phone


class LoginForm(StyledFormMixin, forms.Form):
    email = forms.EmailField(
        label="Email",
        widget=forms.EmailInput(attrs={"autocomplete": "email"}),
    )
    password = forms.CharField(
        label="Пароль",
        widget=forms.PasswordInput(attrs={"autocomplete": "current-password"}),
    )

    error_messages = {
        "invalid_login": "Неверный email или пароль",
    }

    def __init__(self, request=None, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.request = request
        self.user_cache = None
        self.apply_styles()

    def clean(self):
        cleaned_data = super().clean()
        email = cleaned_data.get("email")
        password = cleaned_data.get("password")
        if email and password:
            self.user_cache = authenticate(
                self.request,
                email=email,
                password=password,
            )
            if self.user_cache is None:
                raise ValidationError(self.error_messages["invalid_login"])
        return cleaned_data

    def get_user(self):
        return self.user_cache


class ProfileForm(StyledFormMixin, forms.ModelForm):
    class Meta:
        model = User
        fields = ("name", "surname", "avatar", "about", "phone", "github_url")
        labels = {
            "name": "Имя",
            "surname": "Фамилия",
            "avatar": "Аватар",
            "about": "О себе",
            "phone": "Телефон",
            "github_url": "GitHub",
        }
        widgets = {
            "about": forms.Textarea(attrs={"rows": 4}),
        }

    def __init__(self, *args, **kwargs):
        self.user = kwargs.get("instance")
        super().__init__(*args, **kwargs)
        self.fields["avatar"].required = False
        self.fields["phone"].required = True
        self.apply_styles()

    def clean_phone(self):
        phone = self.cleaned_data.get("phone", "")
        if not phone:
            return ""
        try:
            normalized_phone = normalize_phone(phone)
        except ValueError as error:
            raise ValidationError(str(error)) from error
        queryset = User.objects.filter(phone=normalized_phone)
        if self.user is not None:
            queryset = queryset.exclude(pk=self.user.pk)
        if queryset.exists():
            raise ValidationError(
                "Пользователь с таким номером телефона уже существует.",
            )
        return normalized_phone

    def clean_github_url(self):
        github_url = self.cleaned_data.get("github_url", "")
        if github_url and not is_github_url(github_url):
            raise ValidationError("Укажите ссылку на GitHub.")
        return github_url


class PasswordChangeForm(SetPasswordForm):
    old_password = forms.CharField(
        label="Текущий пароль",
        widget=forms.PasswordInput(attrs={"autocomplete": "current-password"}),
    )

    field_order = ("old_password", "new_password1", "new_password2")

    def clean_old_password(self):
        old_password = self.cleaned_data.get("old_password")
        if not self.user.check_password(old_password):
            raise ValidationError("Текущий пароль указан неверно.")
        return old_password


class AdminUserCreationForm(forms.ModelForm):
    password1 = forms.CharField(label="Пароль", widget=forms.PasswordInput)
    password2 = forms.CharField(
        label="Подтвердите пароль",
        widget=forms.PasswordInput,
    )

    class Meta:
        model = User
        fields = ("email", "name", "surname", "phone")

    def clean_password2(self):
        password1 = self.cleaned_data.get("password1")
        password2 = self.cleaned_data.get("password2")
        if password1 and password2 and password1 != password2:
            raise ValidationError("Пароли не совпадают.")
        return password2

    def save(self, commit=True):
        try:
            normalized_phone = normalize_phone(self.cleaned_data["phone"])
        except ValueError as error:
            raise ValidationError(str(error)) from error
        user = User(
            email=self.cleaned_data["email"],
            name=self.cleaned_data["name"],
            surname=self.cleaned_data["surname"],
            phone=normalized_phone,
        )
        user.set_password(self.cleaned_data["password1"])
        user.ensure_avatar()
        if commit:
            user.save()
        return user


class AdminUserChangeForm(forms.ModelForm):
    password = ReadOnlyPasswordHashField(label="Пароль")

    class Meta:
        model = User
        fields = (
            "email",
            "password",
            "name",
            "surname",
            "avatar",
            "phone",
            "github_url",
            "about",
            "is_active",
            "is_staff",
            "is_superuser",
            "favorites",
        )
