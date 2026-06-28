from django.db.models import Count, Q
from django.utils import timezone
from datetime import timedelta
from accounts.models import User

def get_user_dashboard_stats():
    now = timezone.now()
    seven_days_ago = now - timedelta(days=7)
    
    stats = User.objects.aggregate(
        total_users=Count('id'),
        active_users=Count('id', filter=Q(is_active=True)),
        suspended_users=Count('id', filter=Q(is_active=False)),
        admin_count=Count('id', filter=Q(role=User.Role.ADMIN)),
        staff_count=Count('id', filter=Q(role=User.Role.STAFF)),
        student_count=Count('id', filter=Q(role=User.Role.STUDENT)),
        new_users=Count('id', filter=Q(created_at__gte=seven_days_ago)),
    )
    return stats

def search_and_filter_users(queryset, search_query=None, role=None, status=None, faculty=None):
    if search_query:
        queryset = queryset.filter(
            Q(first_name__icontains=search_query) |
            Q(last_name__icontains=search_query) |
            Q(email__icontains=search_query) |
            Q(username__icontains=search_query)
        )
    
    if role and role in User.Role.values:
        queryset = queryset.filter(role=role)
        
    if status:
        if status == 'active':
            queryset = queryset.filter(is_active=True)
        elif status == 'suspended':
            queryset = queryset.filter(is_active=False)
            
    if faculty:
        queryset = queryset.filter(faculty__icontains=faculty)
            
    return queryset

def get_user_rental_statistics(user):
    from rentals.models import RentalRequest, Rental
    
    recent_requests = RentalRequest.objects.filter(requester=user).select_related('equipment').order_by('-created_at')[:5]
    active_rentals = Rental.objects.filter(issued_to=user, status=Rental.Status.ACTIVE).select_related('equipment').order_by('-issued_date')
    rental_history = Rental.objects.filter(issued_to=user).exclude(status=Rental.Status.ACTIVE).select_related('equipment').order_by('-issued_date')[:10]
    
    stats = {
        'total_requests': RentalRequest.objects.filter(requester=user).count(),
        'active_rentals_count': active_rentals.count(),
        'total_rentals': Rental.objects.filter(issued_to=user).count(),
        'overdue_rentals_count': Rental.objects.filter(issued_to=user, status=Rental.Status.OVERDUE).count(),
        
        'recent_requests': recent_requests,
        'active_rentals': active_rentals,
        'rental_history': rental_history,
    }
    
    return stats

def toggle_user_status(user_to_toggle, modified_by):
    """
    Toggles the is_active status of the given user.
    Returns (success_boolean, message_string)
    """
    if user_to_toggle == modified_by:
        return False, "You cannot suspend your own account."
        
    if user_to_toggle.role == User.Role.ADMIN and user_to_toggle.is_active:
        # Check if they are the last active admin
        active_admins_count = User.objects.filter(role=User.Role.ADMIN, is_active=True).count()
        if active_admins_count <= 1:
            return False, "Cannot suspend the last active administrator."
            
    user_to_toggle.is_active = not user_to_toggle.is_active
    user_to_toggle.save(update_fields=['is_active'])
    
    action_str = "activated" if user_to_toggle.is_active else "suspended"
    
    from activitylog.services import log_activity
    from activitylog.models import ActivityLog
    
    log_action = ActivityLog.ActionType.USER_ACTIVATED if user_to_toggle.is_active else ActivityLog.ActionType.USER_SUSPENDED
    log_activity(
        user=modified_by,
        action=log_action,
        description=f"{action_str.capitalize()} user: {user_to_toggle.username}",
        target_object=user_to_toggle
    )
    
    return True, f"User {user_to_toggle.get_username()} has been successfully {action_str}."
