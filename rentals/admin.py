from django.contrib import admin
from .models import RentalRequest


@admin.register(RentalRequest)
class RentalRequestAdmin(admin.ModelAdmin):
    list_display = (
        "requester",
        "equipment",
        "quantity",
        "request_date",
        "expected_return_date",
        "status",
        "created_at",
    )
    search_fields = (
        "requester__username",
        "requester__email",
        "equipment__name",
        "equipment__serial_number",
        "purpose",
    )
    list_filter = ("status", "request_date", "equipment__category")
