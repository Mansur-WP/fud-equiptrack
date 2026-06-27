from __future__ import annotations

from typing import Any

from django.conf import settings


def branding(request: Any) -> dict[str, str]:
    return {
        "system_name": getattr(settings, "SYSTEM_NAME", "ICT Equipment Rental Management System"),
        "short_system_name": getattr(settings, "SHORT_SYSTEM_NAME", "FUD EquipTrack"),
        "organization_name": getattr(settings, "ORGANIZATION_NAME", "Federal University Dutse ICT Centre"),
        "system_description": getattr(
            settings,
            "SYSTEM_DESCRIPTION",
            "A secure platform for requesting, issuing, tracking, and managing ICT equipment.",
        ),
        "copyright_text": getattr(
            settings,
            "COPYRIGHT_TEXT",
            "© 2026 Federal University Dutse ICT Centre",
        ),
    }

