import io
from PIL import Image
from django.contrib.auth import get_user_model
from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import TestCase

from .forms import UserUpdateForm

User = get_user_model()


def make_uploaded_image(
    *,
    filename: str,
    payload: bytes,
    content_type: str = "image/png",
):
    return SimpleUploadedFile(filename, payload, content_type=content_type)


class ProfileImageUploadValidationTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username="u1",
            email="u1@test.com",
            password="pass12345",
        )

    def test_accept_valid_png(self):
        def generate_valid_png():
            f = io.BytesIO()
            image = Image.new("RGB", (10, 10), color=(0, 255, 0))
            image.save(f, "PNG")
            return f.getvalue()
            
        png_bytes = generate_valid_png()
        upload = make_uploaded_image(
            filename="avatar.png",
            payload=png_bytes,
        )

        form = UserUpdateForm(
            data={},
            files={"profile_image": upload},
            instance=self.user,
        )
        self.assertTrue(form.is_valid())

    def test_reject_exe_renamed_as_png(self):
        exe_bytes = b"MZ" + b"X" * 1024
        upload = make_uploaded_image(
            filename="evil.png",
            payload=exe_bytes,
        )

        form = UserUpdateForm(
            data={},
            files={"profile_image": upload},
            instance=self.user,
        )
        self.assertFalse(form.is_valid())
        self.assertIn("profile_image", form.errors)

