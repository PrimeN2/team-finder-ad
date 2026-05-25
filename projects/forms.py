from django import forms
from django.core.exceptions import ValidationError

from projects.models import Project
from users.utils import is_github_url


class ProjectForm(forms.ModelForm):
    class Meta:
        model = Project
        fields = ("name", "description", "github_url", "status")
        labels = {
            "name": "Название проекта",
            "description": "Описание проекта",
            "github_url": "GitHub",
            "status": "Статус",
        }
        widgets = {
            "description": forms.Textarea(attrs={"rows": 6, "class": "form-input"}),
            "name": forms.TextInput(attrs={"class": "form-input"}),
            "github_url": forms.URLInput(attrs={"class": "form-input"}),
            "status": forms.Select(attrs={"class": "form-input"}),
        }

    def clean_github_url(self):
        github_url = self.cleaned_data.get("github_url", "")
        if github_url and not is_github_url(github_url):
            raise ValidationError("Укажите ссылку на GitHub.")
        return github_url
