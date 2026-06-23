from django.contrib import admin
from .models import Equipment


@admin.register(Equipment)
class EquipmentAdmin(admin.ModelAdmin):
    list_display = (
        "name",
        "category",
        "serial_number",
        "quantity",
        "available_quantity",
        "status",
        "condition",
        "created_at",
    )
    search_fields = ("name", "serial_number", "description")
    list_filter = ("category", "status", "condition")

