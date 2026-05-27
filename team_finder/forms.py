from django.core.exceptions import ValidationError

from users.utils import is_github_url


class GitHubUrlValidationMixin:
    def clean_github_url(self):
        github_url = self.cleaned_data.get("github_url", "")
        if github_url and not is_github_url(github_url):
            raise ValidationError("Укажите ссылку на GitHub.")
        return github_url
