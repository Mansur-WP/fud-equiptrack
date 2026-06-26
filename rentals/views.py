from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.urls import reverse
from django.views.generic import CreateView, DetailView, ListView
from django.db.models import Q

from accounts.models import User
from .forms import RentalRequestForm
from .models import RentalRequest


class StudentOrStaffRequiredMixin(UserPassesTestMixin):
    """Only STUDENT and STAFF roles may access these views."""

    def test_func(self):
        user = self.request.user
        return user.is_authenticated and user.role in (
            User.Role.STUDENT,
            User.Role.STAFF,
        )


class RentalRequestListView(LoginRequiredMixin, ListView):
    model = RentalRequest
    template_name = "rentals/request_list.html"
    context_object_name = "requests"
    paginate_by = 8

    def get_queryset(self):
        qs = super().get_queryset().select_related("requester", "equipment")
        user = self.request.user

        # Admins see all requests; students/staff see only their own
        if user.role != User.Role.ADMIN:
            qs = qs.filter(requester=user)

        # Status filter
        status = self.request.GET.get("status")
        if status:
            qs = qs.filter(status=status)

        return qs

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["statuses"] = RentalRequest.Status.choices
        get_copy = self.request.GET.copy()
        if "page" in get_copy:
            del get_copy["page"]
        context["query_params"] = get_copy.urlencode()
        return context


class RentalRequestCreateView(
    LoginRequiredMixin, StudentOrStaffRequiredMixin, CreateView
):
    model = RentalRequest
    form_class = RentalRequestForm
    template_name = "rentals/request_create.html"

    def form_valid(self, form):
        form.instance.requester = self.request.user
        form.instance.status = RentalRequest.Status.PENDING
        messages.success(self.request, "Equipment request submitted successfully.")
        return super().form_valid(form)

    def form_invalid(self, form):
        messages.error(self.request, "Please correct the errors below.")
        return super().form_invalid(form)

    def get_success_url(self):
        return reverse("rentals:detail", kwargs={"pk": self.object.pk})


class RentalRequestDetailView(LoginRequiredMixin, DetailView):
    model = RentalRequest
    template_name = "rentals/request_detail.html"
    context_object_name = "rental_request"

    def get_queryset(self):
        qs = super().get_queryset().select_related("requester", "equipment")
        user = self.request.user
        # Non-admins can only see their own requests
        if user.role != User.Role.ADMIN:
            qs = qs.filter(requester=user)
        return qs


from django.views.generic.edit import FormView
from django.views.generic.detail import SingleObjectMixin
from .forms import AdminRemarksForm
from .services import approve_request, reject_request, RequestAlreadyProcessedError, InvalidRequestStateError

class AdminRequiredMixin(UserPassesTestMixin):
    """Only ADMIN roles may access these views."""

    def test_func(self):
        user = self.request.user
        return user.is_authenticated and (user.role == User.Role.ADMIN or user.is_superuser)


class PendingRequestsListView(LoginRequiredMixin, AdminRequiredMixin, ListView):
    model = RentalRequest
    template_name = "rentals/pending_requests.html"
    context_object_name = "requests"
    paginate_by = 10

    def get_queryset(self):
        qs = super().get_queryset().select_related("requester", "equipment")
        return qs.filter(status=RentalRequest.Status.PENDING)


class ApproveRequestView(LoginRequiredMixin, AdminRequiredMixin, SingleObjectMixin, FormView):
    model = RentalRequest
    template_name = "rentals/approve_request.html"
    form_class = AdminRemarksForm
    context_object_name = "rental_request"

    def get(self, request, *args, **kwargs):
        self.object = self.get_object()
        return super().get(request, *args, **kwargs)

    def post(self, request, *args, **kwargs):
        self.object = self.get_object()
        return super().post(request, *args, **kwargs)

    def form_valid(self, form):
        try:
            approve_request(self.object, remarks=form.cleaned_data["remarks"])
            messages.success(self.request, f"Request for {self.object.equipment.name} has been approved.")
        except RequestAlreadyProcessedError as e:
            messages.error(self.request, str(e))
        except InvalidRequestStateError as e:
            messages.error(self.request, str(e))
            return self.form_invalid(form)
        return super().form_valid(form)

    def get_success_url(self):
        return reverse("rentals:pending_list")


class RejectRequestView(LoginRequiredMixin, AdminRequiredMixin, SingleObjectMixin, FormView):
    model = RentalRequest
    template_name = "rentals/reject_request.html"
    form_class = AdminRemarksForm
    context_object_name = "rental_request"

    def get(self, request, *args, **kwargs):
        self.object = self.get_object()
        return super().get(request, *args, **kwargs)

    def post(self, request, *args, **kwargs):
        self.object = self.get_object()
        return super().post(request, *args, **kwargs)

    def form_valid(self, form):
        try:
            reject_request(self.object, remarks=form.cleaned_data["remarks"])
            messages.success(self.request, f"Request for {self.object.equipment.name} has been rejected.")
        except RequestAlreadyProcessedError as e:
            messages.error(self.request, str(e))
        except InvalidRequestStateError as e:
            messages.error(self.request, str(e))
            return self.form_invalid(form)
        return super().form_valid(form)

    def get_success_url(self):
        return reverse("rentals:pending_list")


from .models import Rental
from .services import issue_equipment, InvalidRentalRequestError

class RentalListView(LoginRequiredMixin, ListView):
    model = Rental
    template_name = "rentals/active_rentals.html"
    context_object_name = "rentals"
    paginate_by = 10

    def get_queryset(self):
        qs = Rental.objects.select_related("equipment", "issued_to", "issued_by")
        user = self.request.user
        
        if user.role != User.Role.ADMIN and not user.is_superuser:
            qs = qs.filter(issued_to=user)

        status = self.request.GET.get("status")
        if status:
            qs = qs.filter(status=status)
        else:
            # Default to active if not specified
            qs = qs.filter(status=Rental.Status.ACTIVE)

        search = self.request.GET.get("search")
        if search:
            qs = qs.filter(
                Q(equipment__name__icontains=search) |
                Q(equipment__serial_number__icontains=search) |
                Q(issued_to__username__icontains=search)
            )
        return qs

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["statuses"] = Rental.Status.choices
        get_copy = self.request.GET.copy()
        if "page" in get_copy:
            del get_copy["page"]
        context["query_params"] = get_copy.urlencode()
        return context


class RentalDetailView(LoginRequiredMixin, DetailView):
    model = Rental
    template_name = "rentals/rental_detail.html"
    context_object_name = "rental"

    def get_queryset(self):
        qs = super().get_queryset().select_related("equipment", "issued_to", "issued_by", "rental_request")
        user = self.request.user
        if user.role != User.Role.ADMIN and not user.is_superuser:
            qs = qs.filter(issued_to=user)
        return qs


class IssueEquipmentView(LoginRequiredMixin, AdminRequiredMixin, SingleObjectMixin, FormView):
    model = RentalRequest
    template_name = "rentals/issue_equipment.html"
    form_class = AdminRemarksForm
    context_object_name = "rental_request"

    def get(self, request, *args, **kwargs):
        self.object = self.get_object()
        return super().get(request, *args, **kwargs)

    def post(self, request, *args, **kwargs):
        self.object = self.get_object()
        return super().post(request, *args, **kwargs)

    def form_valid(self, form):
        try:
            issue_equipment(
                rental_request=self.object,
                issued_by=self.request.user,
                notes=form.cleaned_data.get("remarks", "")
            )
            messages.success(self.request, f"Equipment successfully issued to {self.object.requester}.")
        except InvalidRentalRequestError as e:
            messages.error(self.request, str(e))
            return self.form_invalid(form)
        return super().form_valid(form)

    def get_success_url(self):
        return reverse("rentals:active_rentals")
