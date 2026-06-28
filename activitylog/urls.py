from django.urls import path

from . import views

app_name = "activitylog"

urlpatterns = [
    path("", views.ActivityLogListView.as_view(), name="log_list"),
    path("<int:pk>/", views.ActivityLogDetailView.as_view(), name="log_detail"),
    path("dashboard/", views.ActivityLogDashboardView.as_view(), name="log_dashboard"),
]
