from django.db import models


class Equipment(models.Model):
    class Category(models.TextChoices):
        LAPTOP = "LAPTOP", "Laptop"
        PROJECTOR = "PROJECTOR", "Projector"
        PRINTER = "PRINTER", "Printer"
        SCANNER = "SCANNER", "Scanner"
        CAMERA = "CAMERA", "Camera"
        NETWORKING = "NETWORKING", "Networking Device"

    class Status(models.TextChoices):
        AVAILABLE = "AVAILABLE", "Available"
        UNAVAILABLE = "UNAVAILABLE", "Unavailable"
        MAINTENANCE = "MAINTENANCE", "Maintenance"

    class Condition(models.TextChoices):
        EXCELLENT = "EXCELLENT", "Excellent"
        GOOD = "GOOD", "Good"
        FAIR = "FAIR", "Fair"
        DAMAGED = "DAMAGED", "Damaged"

    name = models.CharField(max_length=255)
    category = models.CharField(
        max_length=50,
        choices=Category.choices,
        default=Category.LAPTOP,
    )
    description = models.TextField(blank=True)
    serial_number = models.CharField(max_length=100, unique=True)
    quantity = models.PositiveIntegerField(default=1)
    available_quantity = models.PositiveIntegerField(default=1)
    condition = models.CharField(
        max_length=50,
        choices=Condition.choices,
        default=Condition.EXCELLENT,
    )
    image = models.ImageField(
        upload_to="equipment_images/",
        blank=True,
        null=True,
    )
    status = models.CharField(
        max_length=50,
        choices=Status.choices,
        default=Status.AVAILABLE,
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self) -> str:
        return f"{self.name} ({self.serial_number})"

    class Meta:
        ordering = ["name"]
        indexes = [
            models.Index(fields=["category"]),
            models.Index(fields=["status"]),
        ]

