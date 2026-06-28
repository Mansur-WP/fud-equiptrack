from django.urls import path, reverse_lazy
from django.contrib.auth import views as auth_views

from . import views, views_management


app_name = "accounts"

urlpatterns = [
    path("register/", views.RegisterView.as_view(), name="register"),
    path("login/", views.CustomLoginView.as_view(), name="login"),
    path("logout/", views.CustomLogoutView.as_view(), name="logout"),
    path("profile/", views.ProfileView.as_view(), name="profile"),

    path(
        "dashboard/",
        views.DashboardDispatcherView.as_view(),
        name="dashboard",
    ),

    # Placeholder dashboards (final destinations)
    path(
        "admin-dashboard/",
        views.AdminDashboardPlaceholderView.as_view(),
        name="admin_dashboard",
    ),
    path(
        "student-dashboard/",
        views.StudentDashboardPlaceholderView.as_view(),
        name="student_dashboard",
    ),
    path(
        "staff-dashboard/",
        views.StaffDashboardPlaceholderView.as_view(),
        name="staff_dashboard",
    ),
    
    # Management URLs
    path("manage/dashboard/", views_management.UserManagementDashboardView.as_view(), name="manage_dashboard"),
    path("manage/users/", views_management.UserManagementListView.as_view(), name="manage_user_list"),
    path("manage/users/<int:pk>/", views_management.UserManagementDetailView.as_view(), name="manage_user_detail"),
    path("manage/users/<int:pk>/edit/", views_management.UserManagementUpdateView.as_view(), name="manage_user_edit"),
    path("manage/users/<int:pk>/toggle-status/", views_management.UserManagementSuspendView.as_view(), name="manage_user_toggle_status"),

    # Password Reset URLs
    path(
        "password-reset/",
        auth_views.PasswordResetView.as_view(
            template_name="accounts/password_reset/forgot_password.html",
            email_template_name="accounts/password_reset/password_reset_email.html",
            html_email_template_name="accounts/password_reset/password_reset_email_html.html",
            subject_template_name="accounts/password_reset/password_reset_subject.txt",
            success_url=reverse_lazy("accounts:password_reset_done"),
        ),
        name="password_reset",
    ),
    path(
        "password-reset/done/",
        auth_views.PasswordResetDoneView.as_view(
            template_name="accounts/password_reset/password_reset_done.html"
        ),
        name="password_reset_done",
    ),
    path(
        "password-reset/<uidb64>/<token>/",
        auth_views.PasswordResetConfirmView.as_view(
            template_name="accounts/password_reset/password_reset_confirm.html",
            success_url=reverse_lazy("accounts:password_reset_complete"),
        ),
        name="password_reset_confirm",
    ),
    path(
        "password-reset/complete/",
        auth_views.PasswordResetCompleteView.as_view(
            template_name="accounts/password_reset/password_reset_complete.html"
        ),
        name="password_reset_complete",
    ),
]

