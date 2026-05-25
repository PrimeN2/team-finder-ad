from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.shortcuts import redirect
from django.urls import include, path


def root_redirect(_request):
    return redirect("/projects/list")


urlpatterns = [
    path("", root_redirect, name="root"),
    path("admin/", admin.site.urls),
    path("users/", include(("users.urls", "users"), namespace="users")),
    path("projects/", include(("projects.urls", "projects"), namespace="projects")),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
