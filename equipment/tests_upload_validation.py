from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import TestCase

from .forms import EquipmentForm
from .models import Equipment


def make_uploaded_image(filename: str, *, content_type: str = "image/png", payload: bytes) -> SimpleUploadedFile:
    return SimpleUploadedFile(filename, payload, content_type=content_type)


class EquipmentImageUploadValidationTests(TestCase):
    def test_accept_valid_png(self):
        # Minimal valid PNG (1x1 transparent)
        png_bytes = (
            b"\x89PNG\r\n\x1a\n\x00\x00\x00\rIHDR\x00\x00\x00\x01\x00\x00\x00\x01\x08\x06\x00\x00\x00\x1f\x15\xc4\x89\x00\x00\x00\x0cIDATx\x9cc\x00\x01\x00\x00\x05\x00\x01\r\x0a\x2d\xb4\x00\x00\x00\x00IEND\xaeB`\x82"
        )
        upload = make_uploaded_image("eq.png", payload=png_bytes)

        eq = Equipment(
            name="Laptop",
            category=Equipment.Category.LAPTOP,
            serial_number="LT-900",
            quantity=1,
            available_quantity=1,
            condition=Equipment.Condition.GOOD,
            status=Equipment.Status.AVAILABLE,
        )

        form = EquipmentForm(
            data={
                "name": eq.name,
                "category": eq.category,
                "serial_number": eq.serial_number,
                "quantity": eq.quantity,
                "available_quantity": eq.available_quantity,
                "condition": eq.condition,
                "status": eq.status,
                "description": "",
            },
            files={"image": upload},
            instance=eq,
        )
        self.assertTrue(form.is_valid(), form.errors)

    def test_reject_exe_renamed_as_png(self):
        exe_bytes = b"MZ" + b"X" * 2048
        upload = make_uploaded_image("payload.png", payload=exe_bytes, content_type="image/png")

        eq = Equipment(
            name="Laptop2",
            category=Equipment.Category.LAPTOP,
            serial_number="LT-901",
            quantity=1,
            available_quantity=1,
            condition=Equipment.Condition.GOOD,
            status=Equipment.Status.AVAILABLE,
        )

        form = EquipmentForm(
            data={
                "name": eq.name,
                "category": eq.category,
                "serial_number": eq.serial_number,
                "quantity": eq.quantity,
                "available_quantity": eq.available_quantity,
                "condition": eq.condition,
                "status": eq.status,
                "description": "",
            },
            files={"image": upload},
            instance=eq,
        )
        self.assertFalse(form.is_valid())
        self.assertIn("image", form.errors)

