from django.contrib.auth import user_logged_in, user_logged_out
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.conf import settings

from .models import ActivityLog
from .services import log_activity, get_client_ip

@receiver(post_save, sender=settings.AUTH_USER_MODEL)
def log_user_registered(sender, instance, created, **kwargs):
    if created:
        log_activity(
            user=instance,
            action=ActivityLog.ActionType.USER_REGISTERED,
            description=f"New user registered: {instance.username}",
            target_object=instance
        )

@receiver(user_logged_in)
def log_user_login(sender, request, user, **kwargs):
    ip_address = get_client_ip(request) if request else None
    log_activity(
        user=user,
        action=ActivityLog.ActionType.USER_LOGIN,
        description=f"User logged in: {user.username}",
        target_object=user,
        ip_address=ip_address
    )

@receiver(user_logged_out)
def log_user_logout(sender, request, user, **kwargs):
    if user:
        ip_address = get_client_ip(request) if request else None
        log_activity(
            user=user,
            action=ActivityLog.ActionType.USER_LOGOUT,
            description=f"User logged out: {user.username}",
            target_object=user,
            ip_address=ip_address
        )
