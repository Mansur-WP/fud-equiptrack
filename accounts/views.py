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
        role = user.role
        if role == User.Role.ADMIN:
            return reverse("accounts:admin_dashboard")
        elif role == User.Role.STUDENT:
            return reverse("accounts:student_dashboard")
        elif role == User.Role.STAFF:
            return reverse("accounts:staff_dashboard")
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


# Temporary placeholder dashboards so role redirects work.
class AdminDashboardPlaceholderView(LoginRequiredMixin, TemplateView):
    template_name = "accounts/admin_dashboard.html"


class StudentDashboardPlaceholderView(LoginRequiredMixin, TemplateView):
    template_name = "accounts/student_dashboard.html"


class StaffDashboardPlaceholderView(LoginRequiredMixin, TemplateView):
    template_name = "accounts/staff_dashboard.html"



