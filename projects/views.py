from http import HTTPStatus

from django.contrib.auth.mixins import LoginRequiredMixin
from django.http import JsonResponse
from django.shortcuts import get_object_or_404
from django.urls import reverse
from django.views import View
from django.views.generic import CreateView, DetailView, ListView, UpdateView

from projects.forms import ProjectForm
from projects.models import Project
from team_finder.constants import DEFAULT_PAGINATION_PER_PAGE


class ProjectQuerySetMixin:
    def get_projects_queryset(self):
        return Project.objects.select_related("owner").prefetch_related(
            "participants",
        )


class ProjectListView(ProjectQuerySetMixin, ListView):
    template_name = "projects/project_list.html"
    context_object_name = "projects"
    paginate_by = DEFAULT_PAGINATION_PER_PAGE

    def get_queryset(self):
        return self.get_projects_queryset()

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["query_prefix"] = ""
        return context


class FavoriteProjectsView(LoginRequiredMixin, ProjectQuerySetMixin, ListView):
    template_name = "projects/favorite_projects.html"
    context_object_name = "projects"

    def get_queryset(self):
        return self.request.user.favorites.select_related(
            "owner",
        ).prefetch_related("participants")


class ProjectDetailView(ProjectQuerySetMixin, DetailView):
    template_name = "projects/project-details.html"
    context_object_name = "project"
    pk_url_kwarg = "project_id"

    def get_queryset(self):
        return self.get_projects_queryset()


class ProjectCreateView(LoginRequiredMixin, CreateView):
    template_name = "projects/create-project.html"
    form_class = ProjectForm

    def form_valid(self, form):
        form.instance.owner = self.request.user
        return super().form_valid(form)

    def get_success_url(self):
        return reverse("projects:detail", kwargs={"project_id": self.object.pk})

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["is_edit"] = False
        return context


class ProjectEditView(LoginRequiredMixin, UpdateView):
    template_name = "projects/create-project.html"
    form_class = ProjectForm
    pk_url_kwarg = "project_id"
    context_object_name = "project"

    def get_queryset(self):
        return Project.objects.filter(owner=self.request.user)

    def get_success_url(self):
        return reverse("projects:detail", kwargs={"project_id": self.object.pk})

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["is_edit"] = True
        return context


class ToggleFavoriteView(LoginRequiredMixin, View):
    def post(self, request, project_id):
        project = get_object_or_404(Project, pk=project_id)
        is_favorited = request.user.favorites.filter(pk=project.pk).exists()
        if is_favorited:
            request.user.favorites.remove(project)
        else:
            request.user.favorites.add(project)
        return JsonResponse({"status": "ok", "favorited": not is_favorited})


class ToggleParticipateView(LoginRequiredMixin, View):
    def post(self, request, project_id):
        project = get_object_or_404(Project, pk=project_id)
        if (
            project.owner_id == request.user.id
            or project.status != Project.STATUS_OPEN
        ):
            return JsonResponse(
                {"status": "error"},
                status=HTTPStatus.BAD_REQUEST,
            )
        is_participant = project.participants.filter(pk=request.user.pk).exists()
        if is_participant:
            project.participants.remove(request.user)
        else:
            project.participants.add(request.user)
        return JsonResponse({"status": "ok", "participant": not is_participant})


class CompleteProjectView(LoginRequiredMixin, View):
    def post(self, request, project_id):
        project = get_object_or_404(Project, pk=project_id)
        if project.owner_id != request.user.id or project.status != Project.STATUS_OPEN:
            return JsonResponse(
                {"status": "error"},
                status=HTTPStatus.BAD_REQUEST,
            )
        project.status = Project.STATUS_CLOSED
        project.save(update_fields=["status"])
        return JsonResponse({"status": "ok", "project_status": project.status})
