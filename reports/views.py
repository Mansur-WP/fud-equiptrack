from django.contrib.auth.decorators import login_required
from django.core.exceptions import PermissionDenied
from django.http import HttpResponse


@login_required
def placeholder(request):
    user = request.user
    if not (user.is_superuser or getattr(user, "role", None) == "ADMIN"):
        raise PermissionDenied
    return HttpResponse("reports app is wired. models not created yet.")
