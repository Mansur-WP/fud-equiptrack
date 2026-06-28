"""Security tests for URL authorization, role enforcement, and upload validation."""

from django.contrib.auth import get_user_model
from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import Client, TestCase
from django.urls import reverse

User = get_user_model()


# ---------------------------------------------------------------------------
# Minimal valid PNG for upload tests (1×1 transparent)
# ---------------------------------------------------------------------------
import io
import logging
from PIL import Image

def generate_valid_png():
    f = io.BytesIO()
    image = Image.new("RGB", (100, 100), color=(255, 0, 0))
    image.save(f, "PNG")
    return f.getvalue()

VALID_PNG = generate_valid_png()


class DashboardRoleEnforcementTests(TestCase):
    """Student dashboard is student-only; staff dashboard is staff-only."""

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        logging.disable(logging.CRITICAL)

    @classmethod
    def tearDownClass(cls):
        super().tearDownClass()
        logging.disable(logging.NOTSET)

    def setUp(self):
        self.student = User.objects.create_user(
            "student", "s@t.com", "pass12345", role=User.Role.STUDENT
        )
        self.staff = User.objects.create_user(
            "staff", "st@t.com", "pass12345", role=User.Role.STAFF
        )
        self.admin = User.objects.create_superuser(
            "admin", "a@t.com", "pass12345"
        )
        self.client = Client()

    # -- Student dashboard --------------------------------------------------

    def test_student_dashboard_allows_student(self):
        self.client.force_login(self.student)
        resp = self.client.get(reverse("accounts:student_dashboard"))
        self.assertEqual(resp.status_code, 200)

    def test_student_dashboard_denies_staff(self):
        self.client.force_login(self.staff)
        resp = self.client.get(reverse("accounts:student_dashboard"))
        self.assertEqual(resp.status_code, 403)

    def test_student_dashboard_denies_admin(self):
        self.client.force_login(self.admin)
        resp = self.client.get(reverse("accounts:student_dashboard"))
        self.assertEqual(resp.status_code, 403)

    def test_student_dashboard_denies_anonymous(self):
        resp = self.client.get(reverse("accounts:student_dashboard"))
        self.assertEqual(resp.status_code, 302)  # redirect to login

    # -- Staff dashboard ----------------------------------------------------

    def test_staff_dashboard_allows_staff(self):
        self.client.force_login(self.staff)
        resp = self.client.get(reverse("accounts:staff_dashboard"))
        self.assertEqual(resp.status_code, 200)

    def test_staff_dashboard_denies_student(self):
        self.client.force_login(self.student)
        resp = self.client.get(reverse("accounts:staff_dashboard"))
        self.assertEqual(resp.status_code, 403)

    def test_staff_dashboard_denies_admin(self):
        self.client.force_login(self.admin)
        resp = self.client.get(reverse("accounts:staff_dashboard"))
        self.assertEqual(resp.status_code, 403)

    def test_staff_dashboard_denies_anonymous(self):
        resp = self.client.get(reverse("accounts:staff_dashboard"))
        self.assertEqual(resp.status_code, 302)  # redirect to login

    # -- Admin dashboard ----------------------------------------------------

    def test_admin_dashboard_allows_admin(self):
        self.client.force_login(self.admin)
        resp = self.client.get(reverse("accounts:admin_dashboard"))
        self.assertEqual(resp.status_code, 200)

    def test_admin_dashboard_denies_student(self):
        self.client.force_login(self.student)
        resp = self.client.get(reverse("accounts:admin_dashboard"))
        self.assertEqual(resp.status_code, 403)

    def test_admin_dashboard_denies_staff(self):
        self.client.force_login(self.staff)
        resp = self.client.get(reverse("accounts:admin_dashboard"))
        self.assertEqual(resp.status_code, 403)


class ReportsPlaceholderAuthorizationTests(TestCase):
    """Reports placeholder must require login + admin role."""

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        logging.disable(logging.CRITICAL)

    @classmethod
    def tearDownClass(cls):
        super().tearDownClass()
        logging.disable(logging.NOTSET)

    def setUp(self):
        self.student = User.objects.create_user(
            "student_r", "sr@t.com", "pass12345", role=User.Role.STUDENT
        )
        self.staff = User.objects.create_user(
            "staff_r", "str@t.com", "pass12345", role=User.Role.STAFF
        )
        self.admin = User.objects.create_superuser(
            "admin_r", "ar@t.com", "pass12345"
        )
        self.client = Client()

    def test_anonymous_redirected(self):
        resp = self.client.get(reverse("reports:index"))
        self.assertEqual(resp.status_code, 302)

    def test_student_denied(self):
        self.client.force_login(self.student)
        resp = self.client.get(reverse("reports:index"))
        self.assertEqual(resp.status_code, 403)

    def test_staff_denied(self):
        self.client.force_login(self.staff)
        resp = self.client.get(reverse("reports:index"))
        self.assertEqual(resp.status_code, 403)

    def test_admin_allowed(self):
        self.client.force_login(self.admin)
        resp = self.client.get(reverse("reports:index"))
        self.assertEqual(resp.status_code, 200)


class RegisterFormUploadValidationTests(TestCase):
    """RegisterForm must reject malicious uploads (parity with UserUpdateForm)."""

    def test_register_rejects_exe_renamed_as_png(self):
        exe_bytes = b"MZ" + b"X" * 1024
        upload = SimpleUploadedFile("evil.png", exe_bytes, content_type="image/png")

        from accounts.forms import RegisterForm

        form = RegisterForm(
            data={
                "role": "STUDENT",
                "username": "newuser",
                "email": "new@test.com",
                "first_name": "New",
                "last_name": "User",
                "password1": "ComplexP@ss123",
                "password2": "ComplexP@ss123",
            },
            files={"profile_image": upload},
        )
        self.assertFalse(form.is_valid())
        self.assertIn("profile_image", form.errors)

    def test_register_accepts_valid_png(self):
        upload = SimpleUploadedFile("avatar.png", VALID_PNG, content_type="image/png")

        from accounts.forms import RegisterForm

        form = RegisterForm(
            data={
                "role": "STUDENT",
                "username": "newuser2",
                "email": "new2@test.com",
                "first_name": "New",
                "last_name": "User",
                "password1": "ComplexP@ss123",
                "password2": "ComplexP@ss123",
            },
            files={"profile_image": upload},
        )
        self.assertTrue(form.is_valid(), form.errors)


class AdminURLAuthorizationTests(TestCase):
    """Admin-only rental management URLs reject students and staff."""

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        logging.disable(logging.CRITICAL)

    @classmethod
    def tearDownClass(cls):
        super().tearDownClass()
        logging.disable(logging.NOTSET)

    def setUp(self):
        self.student = User.objects.create_user(
            "student_au", "sau@t.com", "pass12345", role=User.Role.STUDENT
        )
        self.staff = User.objects.create_user(
            "staff_au", "stau@t.com", "pass12345", role=User.Role.STAFF
        )
        self.admin = User.objects.create_superuser(
            "admin_au", "aau@t.com", "pass12345"
        )
        self.client = Client()

    def test_pending_list_denies_student(self):
        self.client.force_login(self.student)
        resp = self.client.get(reverse("rentals:pending_list"))
        self.assertEqual(resp.status_code, 403)

    def test_pending_list_denies_staff(self):
        self.client.force_login(self.staff)
        resp = self.client.get(reverse("rentals:pending_list"))
        self.assertEqual(resp.status_code, 403)

    def test_pending_list_allows_admin(self):
        self.client.force_login(self.admin)
        resp = self.client.get(reverse("rentals:pending_list"))
        self.assertEqual(resp.status_code, 200)

    def test_issuance_list_denies_student(self):
        self.client.force_login(self.student)
        resp = self.client.get(reverse("rentals:issuance_list"))
        self.assertEqual(resp.status_code, 403)

    def test_admin_request_management_denies_student(self):
        self.client.force_login(self.student)
        resp = self.client.get(reverse("rentals:admin_request_management"))
        self.assertEqual(resp.status_code, 403)

    def test_admin_request_management_allows_admin(self):
        self.client.force_login(self.admin)
        resp = self.client.get(reverse("rentals:admin_request_management"))
        self.assertEqual(resp.status_code, 200)

    def test_anonymous_redirected_to_login(self):
        for url_name in ["rentals:pending_list", "rentals:issuance_list", "rentals:admin_request_management"]:
            resp = self.client.get(reverse(url_name))
            self.assertEqual(resp.status_code, 302, f"{url_name} should redirect anonymous users")
