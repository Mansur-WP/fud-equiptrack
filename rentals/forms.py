from django import forms
from django.core.exceptions import ValidationError

from accounts.forms import BootstrapFormMixin
from .models import RentalRequest


class RentalRequestForm(BootstrapFormMixin, forms.ModelForm):
    """Form for students and staff to submit equipment rental requests."""

    request_date = forms.DateField(
        widget=forms.DateInput(attrs={"type": "date"}),
    )
    expected_return_date = forms.DateField(
        widget=forms.DateInput(attrs={"type": "date"}),
    )

    class Meta:
        model = RentalRequest
        fields = (
            "equipment",
            "quantity",
            "purpose",
            "request_date",
            "expected_return_date",
        )

    def clean_quantity(self):
        quantity = self.cleaned_data.get("quantity")
        if quantity is None or quantity <= 0:
            raise ValidationError("Quantity must be greater than zero.")
        return quantity

    def clean(self):
        cleaned_data = super().clean()
        equipment = cleaned_data.get("equipment")
        quantity = cleaned_data.get("quantity")
        request_date = cleaned_data.get("request_date")
        expected_return_date = cleaned_data.get("expected_return_date")

        # Validate quantity against available stock
        if equipment and quantity:
            if quantity > equipment.available_quantity:
                self.add_error(
                    "quantity",
                    f"Only {equipment.available_quantity} unit(s) available for "
                    f"'{equipment.name}'.",
                )

        # Validate return date is not before request date
        if request_date and expected_return_date:
            if expected_return_date < request_date:
                self.add_error(
                    "expected_return_date",
                    "Expected return date cannot be before the request date.",
                )

        return cleaned_data


class AdminRemarksForm(BootstrapFormMixin, forms.Form):
    """Form for admins to leave remarks when approving or rejecting requests."""

    remarks = forms.CharField(
        widget=forms.Textarea(attrs={"rows": 4, "placeholder": "Enter any optional remarks or reasons..."}),
        required=False,
    )
