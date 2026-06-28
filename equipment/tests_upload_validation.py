import io
from PIL import Image
from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import TestCase

from .forms import EquipmentForm
from .models import Equipment


def make_uploaded_image(filename: str, *, content_type: str = "image/png", payload: bytes) -> SimpleUploadedFile:
    return SimpleUploadedFile(filename, payload, content_type=content_type)


class EquipmentImageUploadValidationTests(TestCase):
    def test_accept_valid_png(self):
        def generate_valid_png():
            f = io.BytesIO()
            image = Image.new("RGB", (10, 10), color=(0, 0, 255))
            image.save(f, "PNG")
            return f.getvalue()
            
        png_bytes = generate_valid_png()
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

