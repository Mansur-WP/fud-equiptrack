from django.conf import settings
from django.db import models

from equipment.models import Equipment


class RentalRequest(models.Model):
    class Status(models.TextChoices):
        PENDING = "PENDING", "Pending"
        APPROVED = "APPROVED", "Approved"
        REJECTED = "REJECTED", "Rejected"

    requester = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="rental_requests",
    )
    equipment = models.ForeignKey(
        Equipment,
        on_delete=models.CASCADE,
        related_name="rental_requests",
    )
    quantity = models.PositiveIntegerField(default=1)
    purpose = models.TextField()
    request_date = models.DateField()
    expected_return_date = models.DateField()
    status = models.CharField(
        max_length=20,
        choices=Status.choices,
        default=Status.PENDING,
        db_index=True,
    )
    remarks = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self) -> str:
        return f"{self.requester} → {self.equipment} ({self.get_status_display()})"

    class Meta:
        ordering = ["-created_at"]
        indexes = [
            models.Index(fields=["status"]),
            models.Index(fields=["requester"]),
            models.Index(fields=["equipment"]),
            models.Index(fields=["request_date"]),
        ]
