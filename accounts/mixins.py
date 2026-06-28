from django.contrib.auth.mixins import AccessMixin
from accounts.models import User

class AdminRequiredMixin(AccessMixin):
    """Verify that the current user is authenticated and is an Admin."""

    def dispatch(self, request, *args, **kwargs):
        if not request.user.is_authenticated or request.user.role != User.Role.ADMIN:
            return self.handle_no_permission()
        return super().dispatch(request, *args, **kwargs)
