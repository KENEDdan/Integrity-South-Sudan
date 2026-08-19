from django.urls import path
from django.contrib.auth import views as auth_views
from . import views
from .forms import StyledAuthenticationForm

app_name = "accounts"

urlpatterns = [
    path(
        "login/",
        auth_views.LoginView.as_view(
            template_name="accounts/login.html",
            authentication_form=StyledAuthenticationForm,
        ),
        name="login",
    ),
    path("logout/", auth_views.LogoutView.as_view(), name="logout"),
    path("password-change/", views.ForcedPasswordChangeView.as_view(), name="password_change"),
    path("dashboard/", views.dashboard, name="dashboard"),

    path("admin-accounts/", views.admin_account_list, name="admin_account_list"),
    path("admin-accounts/add/", views.admin_account_create, name="admin_account_create"),
    path("admin-accounts/<int:pk>/toggle-active/", views.admin_account_toggle_active, name="admin_account_toggle_active"),
    path("admin-accounts/<int:pk>/reset-password/", views.admin_account_reset_password, name="admin_account_reset_password"),
]