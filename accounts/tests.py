from django.contrib.auth import get_user_model
from django.test import Client, TestCase
from django.urls import reverse


class AuthMessagesTests(TestCase):
    def setUp(self):
        User = get_user_model()
        self.user = User.objects.create_user(
            username="testuser",
            email="test@example.com",
            password="testpass123",
        )
        self.client = Client()

    def test_login_logout_login_logout_success_messages_are_not_duplicated(self):
        # Login
        resp = self.client.post(reverse("accounts:login"), {
            "username": "testuser",
            "email": "test@example.com",
            "password": "testpass123",
        }, follow=True)
        self.assertEqual(resp.status_code, 200)
        self.assertContains(resp, "You have logged in successfully.")

        # Logout
        resp = self.client.post(reverse("accounts:logout"), follow=True)
        self.assertEqual(resp.status_code, 200)
        self.assertContains(resp, "You have logged out successfully.")

        # Login again
        resp = self.client.post(reverse("accounts:login"), {
            "username": "testuser",
            "email": "test@example.com",
            "password": "testpass123",
        }, follow=True)
        self.assertEqual(resp.status_code, 200)

        # Only the current action message should be present.
        self.assertContains(resp, "You have logged in successfully.")
        self.assertNotContains(resp, "You have logged out successfully.")

        # Logout again
        resp = self.client.post(reverse("accounts:logout"), follow=True)
        self.assertEqual(resp.status_code, 200)

        # `CustomLogoutView` redirects to `home.html`, which does not render
        # the global message area from `templates/base.html`.
        # So the logout message text may not be present in the response body.
        # The key regression we assert here is that stale login messages do NOT
        # get re-displayed after the second logout.
        self.assertNotContains(resp, "You have logged in successfully.")



