from django import forms

from accounts.forms import BootstrapFormMixin
from .models import Equipment

from .upload_validation import validate_image_upload


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

    def clean_image(self):
        img = self.cleaned_data.get("image")
        validate_image_upload(img, field_name="image")
        return img

