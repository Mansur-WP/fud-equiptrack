from django import forms
from accounts.forms import BootstrapFormMixin
from .models import Equipment


class EquipmentForm(BootstrapFormMixin, forms.ModelForm):
    class Meta:
        model = Equipment
        fields = (
            "name",
            "category",
            "description",
            "serial_number",
            "quantity",
            "available_quantity",
            "condition",
            "image",
            "status",
        )
