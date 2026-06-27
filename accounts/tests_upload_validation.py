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
        png_bytes = (
            b"\x89PNG\r\n\x1a\n"
            b"\x00\x00\x00\rIHDR"
            b"\x00\x00\x00\x01\x00\x00\x00\x01"
            b"\x08\x06\x00\x00\x00\x1f\x15\xc4\x89"
            b"\x00\x00\x00\x0cIDATx\x9cc\x00\x01"
            b"\x00\x00\x05\x00\x01\r\x0a\x2d\xb4"
            b"\x00\x00\x00\x00IEND\xaeB`\x82"
        )
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

