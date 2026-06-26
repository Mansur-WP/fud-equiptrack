from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.views import LoginView, LogoutView
from django.shortcuts import redirect
from django.urls import reverse
from django.views.generic import CreateView, TemplateView, UpdateView

from .forms import RegisterForm, UserUpdateForm, LoginForm
from .models import User


class RegisterView(CreateView):
    template_name = "accounts/register.html"
    form_class = RegisterForm

    def get_success_url(self):
        return reverse("accounts:login")

    def form_valid(self, form):
        messages.success(self.request, "Account created successfully.")
        return super().form_valid(form)

    def form_invalid(self, form):
        messages.error(self.request, "Please correct the errors below.")
        return super().form_invalid(form)


class CustomLoginView(LoginView):
    template_name = "accounts/login.html"
    form_class = LoginForm

    def get_success_url(self):
        user = self.request.user
        role = getattr(user, "role", None)

        if user.is_superuser or role == User.Role.ADMIN:
            return reverse("accounts:admin_dashboard")
        if role == User.Role.STAFF:
            return reverse("accounts:staff_dashboard")
        if role == User.Role.STUDENT:
            return reverse("accounts:student_dashboard")

        return reverse("accounts:student_dashboard")

    def form_valid(self, form):
        messages.success(self.request, "You have logged in successfully.")
        return super().form_valid(form)

    def form_invalid(self, form):
        messages.error(self.request, "Invalid username/email or password.")
        return super().form_invalid(form)


class CustomLogoutView(LogoutView):
    next_page = "home"

    def get(self, request, *args, **kwargs):
        from django.contrib.auth import logout
        logout(request)
        messages.success(request, "You have logged out successfully.")
        return redirect(self.next_page)

    def post(self, request, *args, **kwargs):
        messages.success(request, "You have logged out successfully.")
        return super().post(request, *args, **kwargs)


class ProfileView(LoginRequiredMixin, UpdateView):
    template_name = "accounts/profile.html"
    model = User
    form_class = UserUpdateForm

    def get_object(self, queryset=None):
        return self.request.user

    def get_success_url(self):
        return reverse("accounts:profile")

    def form_valid(self, form):
        user = self.request.user
        updated = form.save(commit=False)
        # Prevent editing role / is_staff / is_superuser / is_active.
        updated.role = user.role
        updated.is_staff = user.is_staff
        updated.is_superuser = user.is_superuser
        updated.is_active = user.is_active
        updated.save()

        messages.success(self.request, "Profile updated successfully.")
        return redirect(self.get_success_url())

    def form_invalid(self, form):
        messages.error(self.request, "Please correct the errors below.")
        return super().form_invalid(form)


# Dashboard Views
from equipment.models import Equipment
from rentals.models import RentalRequest


class DashboardDispatcherView(LoginRequiredMixin, TemplateView):
    """Single entry point for routing users to the correct dashboard."""

    # Never render a template.
    template_name = "accounts/student_dashboard.html"

    def get(self, request, *args, **kwargs):
        user = request.user

        # Required precedence/order.
        role = getattr(user, "role", None)
        if user.is_superuser or role == User.Role.ADMIN:
            return redirect("accounts:admin_dashboard")
        if role == User.Role.STAFF:
            return redirect("accounts:staff_dashboard")
        if role == User.Role.STUDENT:
            return redirect("accounts:student_dashboard")

        # Fallback (safe default)
        return redirect("accounts:student_dashboard")



class AdminDashboardPlaceholderView(LoginRequiredMixin, TemplateView):
    template_name = "accounts/admin_dashboard.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["total_users"] = User.objects.count()
        context["total_equipment"] = Equipment.objects.count()
        context["pending_requests"] = RentalRequest.objects.filter(status=RentalRequest.Status.PENDING).count()
        context["active_rentals"] = RentalRequest.objects.filter(status=RentalRequest.Status.APPROVED).count()
        
        context["recent_requests"] = RentalRequest.objects.select_related('requester', 'equipment').order_by('-created_at')[:5]
        return context


class StudentDashboardPlaceholderView(LoginRequiredMixin, TemplateView):
    template_name = "accounts/student_dashboard.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        user = self.request.user
        context["active_rentals_count"] = RentalRequest.objects.filter(requester=user, status=RentalRequest.Status.APPROVED).count()
        context["pending_requests_count"] = RentalRequest.objects.filter(requester=user, status=RentalRequest.Status.PENDING).count()
        context["active_rentals"] = RentalRequest.objects.filter(requester=user, status=RentalRequest.Status.APPROVED).order_by('-updated_at')[:5]
        return context


class StaffDashboardPlaceholderView(LoginRequiredMixin, TemplateView):
    template_name = "accounts/staff_dashboard.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        user = self.request.user
        context["active_rentals_count"] = RentalRequest.objects.filter(requester=user, status=RentalRequest.Status.APPROVED).count()
        context["pending_requests_count"] = RentalRequest.objects.filter(requester=user, status=RentalRequest.Status.PENDING).count()
        context["active_rentals"] = RentalRequest.objects.filter(requester=user, status=RentalRequest.Status.APPROVED).order_by('-updated_at')[:5]
        return context



