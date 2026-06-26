from django.urls import path
from . import views

app_name = "rentals"

urlpatterns = [
    path("", views.RentalRequestListView.as_view(), name="list"),
    path("pending/", views.PendingRequestsListView.as_view(), name="pending_list"),
    path("create/", views.RentalRequestCreateView.as_view(), name="create"),
    path("<int:pk>/", views.RentalRequestDetailView.as_view(), name="detail"),
    path("<int:pk>/approve/", views.ApproveRequestView.as_view(), name="approve"),
    path("<int:pk>/reject/", views.RejectRequestView.as_view(), name="reject"),
    path("<int:pk>/issue/", views.IssueEquipmentView.as_view(), name="issue"),
    path("issuance/", views.EquipmentIssuanceListView.as_view(), name="issuance_list"),
    path("active/", views.RentalListView.as_view(), name="active_rentals"),
    path("active/<int:pk>/", views.RentalDetailView.as_view(), name="rental_detail"),
    path(
        "admin/request-management/",
        views.AdminRequestManagementListView.as_view(),
        name="admin_request_management",
    ),
]


