from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin, PermissionRequiredMixin
from django.db import models
from django.urls import reverse
from django.views.generic import (
    CreateView,
    DeleteView,
    DetailView,
    ListView,
    UpdateView,
)

from .forms import EquipmentForm
from .models import Equipment


class EquipmentListView(LoginRequiredMixin, ListView):
    model = Equipment
    template_name = "equipment/equipment_list.html"
    context_object_name = "equipment_list"
    paginate_by = 6

    def get_queryset(self):
        queryset = super().get_queryset()
        q = self.request.GET.get("q")
        if q:
            queryset = queryset.filter(
                models.Q(name__icontains=q) | models.Q(serial_number__icontains=q)
            )

        category = self.request.GET.get("category")
        if category:
            queryset = queryset.filter(category=category)

        status = self.request.GET.get("status")
        if status:
            queryset = queryset.filter(status=status)

        condition = self.request.GET.get("condition")
        if condition:
            queryset = queryset.filter(condition=condition)

        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["categories"] = Equipment.Category.choices
        context["statuses"] = Equipment.Status.choices
        context["conditions"] = Equipment.Condition.choices

        # Keep GET parameters in pagination links
        get_copy = self.request.GET.copy()
        if "page" in get_copy:
            del get_copy["page"]
        context["query_params"] = get_copy.urlencode()
        return context


class EquipmentDetailView(LoginRequiredMixin, DetailView):
    model = Equipment
    template_name = "equipment/equipment_detail.html"
    context_object_name = "equipment"


class EquipmentCreateView(LoginRequiredMixin, PermissionRequiredMixin, CreateView):
    model = Equipment
    form_class = EquipmentForm
    template_name = "equipment/equipment_create.html"
    permission_required = "equipment.add_equipment"

    def get_success_url(self):
        messages.success(self.request, "Equipment added successfully.")
        return reverse("equipment:detail", kwargs={"pk": self.object.pk})


class EquipmentUpdateView(LoginRequiredMixin, PermissionRequiredMixin, UpdateView):
    model = Equipment
    form_class = EquipmentForm
    template_name = "equipment/equipment_update.html"
    permission_required = "equipment.change_equipment"

    def get_success_url(self):
        messages.success(self.request, "Equipment updated successfully.")
        return reverse("equipment:detail", kwargs={"pk": self.object.pk})


class EquipmentDeleteView(LoginRequiredMixin, PermissionRequiredMixin, DeleteView):
    model = Equipment
    template_name = "equipment/equipment_delete.html"
    permission_required = "equipment.delete_equipment"

    def get_success_url(self):
        messages.success(self.request, "Equipment deleted successfully.")
        return reverse("equipment:list")
