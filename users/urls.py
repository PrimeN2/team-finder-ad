from django.urls import path

from users import views


app_name = "users"

urlpatterns = [
    path("register/", views.RegisterView.as_view(), name="register"),
    path("login/", views.LoginView.as_view(), name="login"),
    path("logout/", views.LogoutView.as_view(), name="logout"),
    path("list/", views.UserListView.as_view(), name="list"),
    path("edit-profile/", views.EditProfileView.as_view(), name="edit-profile"),
    path(
        "change-password/",
        views.ChangePasswordView.as_view(),
        name="change-password",
    ),
    path("<int:user_id>/", views.UserDetailView.as_view(), name="detail"),
]
