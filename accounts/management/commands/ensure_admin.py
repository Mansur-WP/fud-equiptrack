from __future__ import annotations

from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model


class Command(BaseCommand):
    help = "Ensure an initial admin user exists (idempotent)."

    def add_arguments(self, parser):
        parser.add_argument("--email", default=None)
        parser.add_argument("--username", default=None)
        parser.add_argument("--password", default=None)

    def handle(self, *args, **options):
        User = get_user_model()

        email = options.get("email")
        username = options.get("username")
        password = options.get("password")

        # Fallback to env vars
        import os

        email = email or os.getenv("DJANGO_ADMIN_EMAIL")
        username = username or os.getenv("DJANGO_ADMIN_USERNAME")
        password = password or os.getenv("DJANGO_ADMIN_PASSWORD")

        if not email or not username or not password:
            raise ValueError(
                "Admin bootstrap requires "
                "DJANGO_ADMIN_EMAIL/USERNAME/PASSWORD"
            )

        # If any admin exists, do nothing.
        Role = getattr(User, "Role")

        if User.objects.filter(role=Role.ADMIN).exists():
            self.stdout.write(self.style.SUCCESS("Admin already exists;"))

            self.stdout.write(self.style.SUCCESS("skipping."))
            return

        user = User(
            username=username,
            email=email,
            role=getattr(User, "Role").ADMIN,
            is_staff=True,
            is_superuser=True,
            is_active=True,
        )
        user.set_password(password)
        user.save()

        created_msg = f"Admin created: {username} ({email})"
        self.stdout.write(self.style.SUCCESS(created_msg))


