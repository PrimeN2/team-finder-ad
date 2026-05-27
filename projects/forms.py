from django import forms

from projects.models import Project
from team_finder.forms import GitHubUrlValidationMixin


class ProjectForm(GitHubUrlValidationMixin, forms.ModelForm):
    class Meta:
        model = Project
        fields = ("name", "description", "github_url", "status")
        widgets = {
            "description": forms.Textarea(attrs={"rows": 6, "class": "form-input"}),
            "name": forms.TextInput(attrs={"class": "form-input"}),
            "github_url": forms.URLInput(attrs={"class": "form-input"}),
            "status": forms.Select(attrs={"class": "form-input"}),
        }
