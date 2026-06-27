from __future__ import annotations

from django.http import HttpRequest, HttpResponse
from django.shortcuts import render


def custom_404(request: HttpRequest, exception: Exception) -> HttpResponse:
    # exception may carry details; we keep it simple for template rendering.
    return render(request, "404.html", status=404, context={"requested_path": getattr(request, "path", "")})

