from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator
from django.http import JsonResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.utils.decorators import method_decorator
from django.views import View

from projects.forms import ProjectForm
from projects.models import Project


def paginate_queryset(request, queryset, per_page=12):
    paginator = Paginator(queryset, per_page)
    return paginator.get_page(request.GET.get("page"))


class ProjectListView(View):
    template_name = "projects/project_list.html"

    def get(self, request):
        projects = Project.objects.select_related(
            "owner",
        ).prefetch_related("participants")
        page_obj = paginate_queryset(request, projects)
        context = {
            "projects": projects,
            "page_obj": page_obj,
            "query_prefix": "",
        }
        return render(request, self.template_name, context)


@method_decorator(login_required, name="dispatch")
class FavoriteProjectsView(View):
    template_name = "projects/favorite_projects.html"

    def get(self, request):
        projects = request.user.favorites.select_related(
            "owner",
        ).prefetch_related("participants")
        return render(request, self.template_name, {"projects": projects})


class ProjectDetailView(View):
    template_name = "projects/project-details.html"

    def get(self, request, project_id):
        project = get_object_or_404(
            Project.objects.select_related("owner").prefetch_related(
                "participants",
            ),
            pk=project_id,
        )
        return render(request, self.template_name, {"project": project})


@method_decorator(login_required, name="dispatch")
class ProjectCreateView(View):
    template_name = "projects/create-project.html"

    def get(self, request):
        form = ProjectForm()
        return render(
            request,
            self.template_name,
            {"form": form, "is_edit": False},
        )

    def post(self, request):
        form = ProjectForm(request.POST)
        if form.is_valid():
            project = form.save(commit=False)
            project.owner = request.user
            project.save()
            return redirect("projects:detail", project_id=project.id)
        return render(
            request,
            self.template_name,
            {"form": form, "is_edit": False},
        )


@method_decorator(login_required, name="dispatch")
class ProjectEditView(View):
    template_name = "projects/create-project.html"

    def get_project(self, request, project_id):
        return get_object_or_404(Project, pk=project_id, owner=request.user)

    def get(self, request, project_id):
        project = self.get_project(request, project_id)
        form = ProjectForm(instance=project)
        return render(
            request,
            self.template_name,
            {"form": form, "is_edit": True, "project": project},
        )

    def post(self, request, project_id):
        project = self.get_project(request, project_id)
        form = ProjectForm(request.POST, instance=project)
        if form.is_valid():
            project = form.save()
            return redirect("projects:detail", project_id=project.id)
        return render(
            request,
            self.template_name,
            {"form": form, "is_edit": True, "project": project},
        )


@method_decorator(login_required, name="dispatch")
class ToggleFavoriteView(View):
    def post(self, request, project_id):
        project = get_object_or_404(Project, pk=project_id)
        if request.user.favorites.filter(pk=project.pk).exists():
            request.user.favorites.remove(project)
            favorited = False
        else:
            request.user.favorites.add(project)
            favorited = True
        return JsonResponse({"status": "ok", "favorited": favorited})


@method_decorator(login_required, name="dispatch")
class ToggleParticipateView(View):
    def post(self, request, project_id):
        project = get_object_or_404(Project, pk=project_id)
        if (
            project.owner_id == request.user.id
            or project.status != Project.STATUS_OPEN
        ):
            return JsonResponse({"status": "error"}, status=400)
        if project.participants.filter(pk=request.user.pk).exists():
            project.participants.remove(request.user)
            participant = False
        else:
            project.participants.add(request.user)
            participant = True
        return JsonResponse({"status": "ok", "participant": participant})


@method_decorator(login_required, name="dispatch")
class CompleteProjectView(View):
    def post(self, request, project_id):
        project = get_object_or_404(Project, pk=project_id)
        if project.owner_id != request.user.id or project.status != Project.STATUS_OPEN:
            return JsonResponse({"status": "error"}, status=400)
        project.status = Project.STATUS_CLOSED
        project.save(update_fields=["status"])
        return JsonResponse({"status": "ok", "project_status": project.status})
