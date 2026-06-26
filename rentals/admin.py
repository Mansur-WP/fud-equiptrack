from django.contrib import admin

from .models import Rental, RentalRequest, Return


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


@admin.register(Rental)
class RentalAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "equipment",
        "issued_to",
        "issued_by",
        "quantity",
        "issued_date",
        "expected_return_date",
        "status",
    )
    search_fields = (
        "equipment__name",
        "equipment__serial_number",
        "issued_to__username",
        "issued_to__email",
        "issued_by__username",
    )
    list_filter = ("status", "issued_date", "expected_return_date")
    ordering = ("-issued_date", "-created_at")


@admin.register(Return)
class ReturnAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "rental",
        "returned_by",
        "return_date",
        "condition_on_return",
        "created_at",
        "updated_at",
    )
    search_fields = (
        "returned_by__username",
        "returned_by__email",
        "rental__equipment__name",
        "rental__equipment__serial_number",
    )
    list_filter = ("condition_on_return", "return_date", "returned_by")
    ordering = ("-return_date", "-created_at")

