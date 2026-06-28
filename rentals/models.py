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
    )
    remarks = models.TextField(blank=True)

    # Set when an admin approves a request (approval does NOT issue equipment).
    approved_date = models.DateField(null=True, blank=True, db_index=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)


    def __str__(self) -> str:
        return f"{self.requester} → {self.equipment} ({self.get_status_display()})"

    class Meta:
        ordering = ["-created_at"]
        indexes = [
            models.Index(fields=["status"]),
            models.Index(fields=["request_date"]),
        ]

class Rental(models.Model):
    class Status(models.TextChoices):
        ACTIVE = "ACTIVE", "Active"
        RETURNED = "RETURNED", "Returned"
        OVERDUE = "OVERDUE", "Overdue"

    rental_request = models.OneToOneField(
        RentalRequest,
        on_delete=models.CASCADE,
        related_name="rental",
    )
    equipment = models.ForeignKey(
        Equipment,
        on_delete=models.CASCADE,
        related_name="rentals",
    )
    issued_to = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="rentals_received",
    )
    issued_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="rentals_issued",
    )
    quantity = models.PositiveIntegerField(default=1)
    issued_date = models.DateField()
    expected_return_date = models.DateField()
    status = models.CharField(
        max_length=20,
        choices=Status.choices,
        default=Status.ACTIVE,
    )
    notes = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self) -> str:
        return f"Rental of {self.equipment} to {self.issued_to} ({self.get_status_display()})"

    class Meta:
        verbose_name = "Rental"
        verbose_name_plural = "Rentals"
        ordering = ["-issued_date", "-created_at"]
        indexes = [
            models.Index(fields=["status"]),
            models.Index(fields=["expected_return_date"]),
        ]


class Return(models.Model):
    class Condition(models.TextChoices):
        EXCELLENT = "EXCELLENT", "Excellent"
        GOOD = "GOOD", "Good"
        FAIR = "FAIR", "Fair"
        DAMAGED = "DAMAGED", "Damaged"
        LOST = "LOST", "Lost"

    rental = models.OneToOneField(
        Rental,
        on_delete=models.CASCADE,
        related_name="returns_record",
    )
    returned_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="returns",
    )
    return_date = models.DateField()
    condition_on_return = models.CharField(
        max_length=20,
        choices=Condition.choices,
    )
    notes = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self) -> str:
        condition = self.get_condition_on_return_display()
        return f"Return for Rental #{self.rental_id} by {self.returned_by} ({condition})"


    class Meta:
        verbose_name = "Return"
        verbose_name_plural = "Returns"
        ordering = ["-return_date", "-created_at"]
        indexes = [
            models.Index(fields=["return_date"]),
            models.Index(fields=["condition_on_return"]),
        ]

