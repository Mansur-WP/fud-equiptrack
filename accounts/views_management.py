from django.contrib import messages
from django.shortcuts import get_object_or_404, redirect
from django.urls import reverse_lazy, reverse
from django.views.generic import TemplateView, ListView, DetailView, UpdateView, View
from django.utils.decorators import method_decorator

from accounts.models import User
from accounts.mixins import AdminRequiredMixin
from accounts.forms import UserManagementUpdateForm
from accounts.services.user_management import (
    get_user_dashboard_stats,
    search_and_filter_users,
    toggle_user_status,
    get_user_rental_statistics,
)

class UserManagementDashboardView(AdminRequiredMixin, TemplateView):
    template_name = "accounts/management/dashboard.html"
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context.update(get_user_dashboard_stats())
        return context

class UserManagementListView(AdminRequiredMixin, ListView):
    model = User
    template_name = "accounts/management/user_list.html"
    context_object_name = "users"
    paginate_by = 20
    ordering = ["-created_at"]
    
    def get_queryset(self):
        qs = super().get_queryset()
        
        # Get query parameters
        search_query = self.request.GET.get('q', '').strip()
        role = self.request.GET.get('role', '').strip()
        status = self.request.GET.get('status', '').strip()
        faculty = self.request.GET.get('faculty', '').strip()
        
        return search_and_filter_users(qs, search_query, role, status, faculty)
        
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['roles'] = User.Role.choices
        context['faculties'] = User.objects.exclude(faculty='').values_list('faculty', flat=True).distinct().order_by('faculty')
        # Preserve GET parameters for pagination
        get_params = self.request.GET.copy()
        if 'page' in get_params:
            del get_params['page']
        context['query_string'] = get_params.urlencode()
        return context

class UserManagementDetailView(AdminRequiredMixin, DetailView):
    model = User
    template_name = "accounts/management/user_detail.html"
    context_object_name = "user_obj"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context.update(get_user_rental_statistics(self.object))
        return context

class UserManagementUpdateView(AdminRequiredMixin, UpdateView):
    model = User
    form_class = UserManagementUpdateForm
    template_name = "accounts/management/user_form.html"
    context_object_name = "user_obj"
    
    def form_valid(self, form):
        response = super().form_valid(form)
        from activitylog.services import log_activity, get_client_ip
        from activitylog.models import ActivityLog
        log_activity(
            user=self.request.user,
            action=ActivityLog.ActionType.USER_UPDATED,
            description=f"Updated user profile for: {self.object.username}",
            target_object=self.object,
            ip_address=get_client_ip(self.request)
        )
        return response

    def get_success_url(self):
        messages.success(self.request, "User updated successfully.")
        return reverse('accounts:manage_user_detail', kwargs={'pk': self.object.pk})

class UserManagementSuspendView(AdminRequiredMixin, View):
    
    def post(self, request, *args, **kwargs):
        user_to_toggle = get_object_or_404(User, pk=kwargs['pk'])
        success, message = toggle_user_status(user_to_toggle, request.user)
        
        if success:
            messages.success(request, message)
        else:
            messages.error(request, message)
            
        return redirect('accounts:manage_user_detail', pk=user_to_toggle.pk)
