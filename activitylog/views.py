from django.views.generic import ListView, TemplateView
from django.db.models import Q
from accounts.models import User
from accounts.mixins import AdminRequiredMixin

from .models import ActivityLog
from .services import get_activity_dashboard_stats

class ActivityLogListView(AdminRequiredMixin, ListView):
    model = ActivityLog
    template_name = "activitylog/log_list.html"
    context_object_name = "logs"
    paginate_by = 25
    
    def get_queryset(self):
        qs = super().get_queryset().select_related("user")
        
        # Filters
        action = self.request.GET.get("action")
        if action:
            qs = qs.filter(action=action)
            
        user_id = self.request.GET.get("user_id")
        if user_id:
            qs = qs.filter(user_id=user_id)
            
        date_from = self.request.GET.get("date_from")
        if date_from:
            qs = qs.filter(created_at__gte=date_from)
            
        date_to = self.request.GET.get("date_to")
        if date_to:
            qs = qs.filter(created_at__lte=date_to)
            
        # Search
        q = self.request.GET.get("q")
        if q:
            qs = qs.filter(
                Q(description__icontains=q) | 
                Q(target_model__icontains=q)
            )
            
        return qs
        
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["actions"] = ActivityLog.ActionType.choices
        
        # Populate users for filter dropdown (only those with logs)
        user_ids = ActivityLog.objects.exclude(user__isnull=True).values_list('user_id', flat=True).distinct()
        context["users"] = User.objects.filter(id__in=user_ids).order_by("username")
        
        # Keep query parameters for pagination
        get_copy = self.request.GET.copy()
        if "page" in get_copy:
            del get_copy["page"]
        context["query_params"] = get_copy.urlencode()
        
        return context

class ActivityLogDashboardView(AdminRequiredMixin, TemplateView):
    template_name = "activitylog/log_dashboard.html"
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context.update(get_activity_dashboard_stats())
        return context

from django.views.generic import DetailView

class ActivityLogDetailView(AdminRequiredMixin, DetailView):
    model = ActivityLog
    template_name = "activitylog/log_detail.html"
    context_object_name = "log"
    
    def get_queryset(self):
        return super().get_queryset().select_related("user")
