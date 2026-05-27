from django.urls import path

from projects import views


app_name = "projects"

urlpatterns = [
    path("list/", views.ProjectListView.as_view(), name="list"),
    path("favorites/", views.FavoriteProjectsView.as_view(), name="favorites"),
    path("create-project/", views.ProjectCreateView.as_view(), name="create"),
    path("<int:project_id>/", views.ProjectDetailView.as_view(), name="detail"),
    path("<int:project_id>/edit/", views.ProjectEditView.as_view(), name="edit"),
    path(
        "<int:project_id>/toggle-favorite/",
        views.ToggleFavoriteView.as_view(),
        name="toggle-favorite",
    ),
    path(
        "<int:project_id>/toggle-participate/",
        views.ToggleParticipateView.as_view(),
        name="toggle-participate",
    ),
    path(
        "<int:project_id>/complete/",
        views.CompleteProjectView.as_view(),
        name="complete",
    ),
]
