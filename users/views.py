from django.contrib.auth import login, logout, update_session_auth_hash
from django.contrib.auth.mixins import LoginRequiredMixin
from django.core.paginator import Paginator
from django.shortcuts import get_object_or_404, redirect, render
from django.views import View

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


def paginate_queryset(request, queryset, per_page=12):
    paginator = Paginator(queryset, per_page)
    return paginator.get_page(request.GET.get("page"))


class RegisterView(View):
    template_name = "users/register.html"

    def get(self, request):
        return render(request, self.template_name, {"form": RegistrationForm()})

    def post(self, request):
        form = RegistrationForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect("users:login")
        return render(request, self.template_name, {"form": form})


class LoginView(View):
    template_name = "users/login.html"

    def get(self, request):
        if request.user.is_authenticated:
            return redirect("projects:list")
        return render(
            request,
            self.template_name,
            {"form": LoginForm(request=request)},
        )

    def post(self, request):
        form = LoginForm(request=request, data=request.POST)
        if form.is_valid():
            login(request, form.get_user())
            return redirect("projects:list")
        return render(request, self.template_name, {"form": form})


class LogoutView(View):
    def get(self, request):
        logout(request)
        return redirect("projects:list")


class UserDetailView(View):
    template_name = "users/user-details.html"

    def get(self, request, user_id):
        profile_user = get_object_or_404(
            User.objects.prefetch_related("owned_projects__participants"),
            pk=user_id,
        )
        return render(request, self.template_name, {"user": profile_user})


class UserListView(View):
    template_name = "users/participants.html"

    def get(self, request):
        participants = User.objects.all().order_by("-id")
        active_filter = None
        query_prefix = ""

        if request.user.is_authenticated:
            active_filter = request.GET.get("filter")
            if active_filter in USER_FILTERS:
                participants = self.apply_filter(
                    request.user,
                    participants,
                    active_filter,
                )
                query_prefix = f"filter={active_filter}&"
            else:
                active_filter = None

        page_obj = paginate_queryset(request, participants.distinct())
        context = {
            "participants": participants,
            "page_obj": page_obj,
            "active_filter": active_filter,
            "query_prefix": query_prefix,
        }
        return render(request, self.template_name, context)

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


class EditProfileView(LoginRequiredMixin, View):
    template_name = "users/edit_profile.html"

    def get(self, request):
        form = ProfileForm(instance=request.user)
        return render(
            request,
            self.template_name,
            {"form": form, "user": request.user},
        )

    def post(self, request):
        form = ProfileForm(request.POST, request.FILES, instance=request.user)
        if form.is_valid():
            user = form.save()
            if not user.avatar:
                user.ensure_avatar()
                user.save(update_fields=["avatar"])
            return redirect("users:detail", user_id=request.user.id)
        return render(
            request,
            self.template_name,
            {"form": form, "user": request.user},
        )


class ChangePasswordView(LoginRequiredMixin, View):
    template_name = "users/change_password.html"

    def get(self, request):
        return render(
            request,
            self.template_name,
            {"form": PasswordChangeForm(user=request.user)},
        )

    def post(self, request):
        form = PasswordChangeForm(user=request.user, data=request.POST)
        if form.is_valid():
            user = form.save()
            update_session_auth_hash(request, user)
            return redirect("users:detail", user_id=request.user.id)
        return render(request, self.template_name, {"form": form})
