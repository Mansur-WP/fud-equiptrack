from django.db import models
from django.conf import settings

class ActivityLog(models.Model):
    class ActionType(models.TextChoices):
        USER_REGISTERED     = "USER_REGISTERED",     "User Registered"
        USER_LOGIN          = "USER_LOGIN",          "User Login"
        USER_LOGOUT         = "USER_LOGOUT",         "User Logout"
        EQUIPMENT_ADDED     = "EQUIPMENT_ADDED",     "Equipment Added"
        EQUIPMENT_UPDATED   = "EQUIPMENT_UPDATED",   "Equipment Updated"
        EQUIPMENT_DELETED   = "EQUIPMENT_DELETED",   "Equipment Deleted"
        RENTAL_REQUEST_CREATED = "RENTAL_REQUEST_CREATED", "Rental Request Created"
        RENTAL_APPROVED     = "RENTAL_APPROVED",     "Rental Approved"
        RENTAL_REJECTED     = "RENTAL_REJECTED",     "Rental Rejected"
        EQUIPMENT_ISSUED    = "EQUIPMENT_ISSUED",    "Equipment Issued"
        EQUIPMENT_RETURNED  = "EQUIPMENT_RETURNED",  "Equipment Returned"
        USER_UPDATED        = "USER_UPDATED",        "User Updated"
        USER_SUSPENDED      = "USER_SUSPENDED",      "User Suspended"
        USER_ACTIVATED      = "USER_ACTIVATED",      "User Activated"
        REPORT_GENERATED    = "REPORT_GENERATED",    "Report Generated"

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True, blank=True,
        related_name="activity_logs",
        help_text="The user who performed the action.",
    )
    action = models.CharField(max_length=50, choices=ActionType.choices, db_index=True)
    description = models.TextField(help_text="Human-readable description of what happened.")
    target_model = models.CharField(max_length=100, blank=True, help_text="e.g. 'Equipment', 'User', 'RentalRequest'")
    target_id = models.PositiveIntegerField(null=True, blank=True, help_text="PK of the affected object.")
    ip_address = models.GenericIPAddressField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True, db_index=True)

    class Meta:
        ordering = ["-created_at"]
        indexes = [
            models.Index(fields=["action"]),
            models.Index(fields=["-created_at"]),
            models.Index(fields=["user", "-created_at"]),
        ]

    def __str__(self):
        return f"[{self.get_action_display()}] {self.description}"
