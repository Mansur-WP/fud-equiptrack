from django.db.models import Count
from django.utils import timezone
from datetime import timedelta

from .models import ActivityLog

def get_client_ip(request):
    """Extract IP address from a Django request."""
    if not request:
        return None
    x_forwarded = request.META.get("HTTP_X_FORWARDED_FOR")
    if x_forwarded:
        return x_forwarded.split(",")[0].strip()
    return request.META.get("REMOTE_ADDR")

def log_activity(user, action, description, target_object=None, ip_address=None):
    """Create an ActivityLog entry."""
    target_model = ""
    target_id = None
    if target_object:
        target_model = target_object.__class__.__name__
        target_id = target_object.pk

    ActivityLog.objects.create(
        user=user,
        action=action,
        description=description,
        target_model=target_model,
        target_id=target_id,
        ip_address=ip_address,
    )

def get_activity_dashboard_stats():
    """Gather key statistics for the activity log dashboard."""
    now = timezone.now()
    today_start = now.replace(hour=0, minute=0, second=0, microsecond=0)
    seven_days_ago = now - timedelta(days=7)
    thirty_days_ago = now - timedelta(days=30)
    
    total_events = ActivityLog.objects.count()
    events_today = ActivityLog.objects.filter(created_at__gte=today_start).count()
    events_this_week = ActivityLog.objects.filter(created_at__gte=seven_days_ago).count()
    events_this_month = ActivityLog.objects.filter(created_at__gte=thirty_days_ago).count()
    unique_users_today = ActivityLog.objects.filter(created_at__gte=today_start).exclude(user__isnull=True).values('user').distinct().count()
    
    events_by_action = list(ActivityLog.objects.values('action').annotate(count=Count('id')).order_by('-count'))
    # Optional: Map action codes to human readable choices if we want in the view
    
    recent_activity = ActivityLog.objects.select_related('user').order_by('-created_at')[:10]
    
    return {
        'total_events': total_events,
        'events_today': events_today,
        'events_this_week': events_this_week,
        'events_this_month': events_this_month,
        'unique_users_today': unique_users_today,
        'events_by_action': events_by_action,
        'recent_activity': recent_activity,
    }
