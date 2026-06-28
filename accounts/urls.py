from django.urls import path

from . import views


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
]



