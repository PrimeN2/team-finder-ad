from django.contrib.auth import login, logout
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.views import PasswordChangeView as BasePasswordChangeView
from django.shortcuts import redirect
from django.urls import reverse
from django.views import View
from django.views.generic import CreateView, DetailView, FormView, ListView, UpdateView

from team_finder.constants import DEFAULT_PAGINATION_PER_PAGE
from users.forms import (
    LoginForm,
    PasswordChangeForm,
    ProfileForm,
    RegistrationForm,
)
from users.models import User


FILTER_OWNERS_OF_FAVORITE_PROJECTS = "owners-of-favorite-projects"
FILTER_OWNERS_OF_PARTICIPATING_PROJECTS = "owners-of-participating-projects"
FILTER_INTERESTED_IN_MY_PROJECTS = "interested-in-my-projects"
FILTER_PARTICIPANTS_OF_MY_PROJECTS = "participants-of-my-projects"
USER_FILTERS = {
    FILTER_OWNERS_OF_FAVORITE_PROJECTS,
    FILTER_OWNERS_OF_PARTICIPATING_PROJECTS,
    FILTER_INTERESTED_IN_MY_PROJECTS,
    FILTER_PARTICIPANTS_OF_MY_PROJECTS,
}


class RegisterView(CreateView):
    template_name = "users/register.html"
    form_class = RegistrationForm

    def get_success_url(self):
        return reverse("users:login")


class LoginView(FormView):
    template_name = "users/login.html"
    form_class = LoginForm

    def dispatch(self, request, *args, **kwargs):
        if request.user.is_authenticated:
            return redirect("projects:list")
        return super().dispatch(request, *args, **kwargs)

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs["request"] = self.request
        return kwargs

    def form_valid(self, form):
        login(self.request, form.get_user())
        return super().form_valid(form)

    def get_success_url(self):
        return reverse("projects:list")


class LogoutView(View):
    def get(self, request):
        logout(request)
        return redirect("projects:list")


class UserDetailView(DetailView):
    template_name = "users/user-details.html"
    context_object_name = "user"
    pk_url_kwarg = "user_id"

    def get_queryset(self):
        return User.objects.prefetch_related(
            "owned_projects__participants",
        )


class UserListView(ListView):
    template_name = "users/participants.html"
    context_object_name = "participants"
    paginate_by = DEFAULT_PAGINATION_PER_PAGE

    def get_queryset(self):
        participants = User.objects.all().order_by("-id")
        if not self.request.user.is_authenticated:
            return participants

        active_filter = self.request.GET.get("filter")
        if active_filter not in USER_FILTERS:
            return participants
        return self.apply_filter(
            self.request.user,
            participants,
            active_filter,
        ).distinct()

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        active_filter = None
        query_prefix = ""
        if self.request.user.is_authenticated:
            active_filter = self.request.GET.get("filter")
            if active_filter in USER_FILTERS:
                query_prefix = f"filter={active_filter}&"
            else:
                active_filter = None
        context["active_filter"] = active_filter
        context["query_prefix"] = query_prefix
        return context

    def apply_filter(self, user, participants, active_filter):
        if active_filter == FILTER_OWNERS_OF_FAVORITE_PROJECTS:
            project_ids = user.favorites.values_list("id", flat=True)
            return participants.filter(
                owned_projects__id__in=project_ids,
            ).exclude(id=user.id)
        if active_filter == FILTER_OWNERS_OF_PARTICIPATING_PROJECTS:
            return participants.filter(
                owned_projects__participants=user,
            ).exclude(id=user.id)
        if active_filter == FILTER_INTERESTED_IN_MY_PROJECTS:
            return participants.filter(
                favorites__owner=user,
            ).exclude(id=user.id)
        if active_filter == FILTER_PARTICIPANTS_OF_MY_PROJECTS:
            return participants.filter(
                participated_projects__owner=user,
            ).exclude(id=user.id)
        return participants


class EditProfileView(LoginRequiredMixin, UpdateView):
    template_name = "users/edit_profile.html"
    form_class = ProfileForm
    model = User
    context_object_name = "user"

    def get_object(self, queryset=None):
        return self.request.user

    def form_valid(self, form):
        response = super().form_valid(form)
        if not self.object.avatar:
            self.object.ensure_avatar()
            self.object.save(update_fields=["avatar"])
        return response

    def get_success_url(self):
        return reverse("users:detail", kwargs={"user_id": self.request.user.id})


class ChangePasswordView(LoginRequiredMixin, BasePasswordChangeView):
    template_name = "users/change_password.html"
    form_class = PasswordChangeForm

    def get_success_url(self):
        return reverse("users:detail", kwargs={"user_id": self.request.user.id})
