from django import forms
from django.contrib.auth.forms import AuthenticationForm, UserCreationForm
from django.core.exceptions import ValidationError

from .models import User
from .upload_validation import validate_image_upload




class BootstrapFormMixin:

    """Mixin to automatically apply Bootstrap 5 form classes to form fields."""

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field_name, field in self.fields.items():
            if isinstance(field.widget, forms.CheckboxInput):
                field.widget.attrs.setdefault("class", "form-check-input")
            elif isinstance(field.widget, forms.FileInput):
                field.widget.attrs.setdefault("class", "form-control")
            else:
                field.widget.attrs.setdefault("class", "form-control")


class RegisterForm(BootstrapFormMixin, UserCreationForm):
    """Create user with unique email and password confirmation."""

    email = forms.EmailField(required=True)
    password1 = forms.CharField(
        label="Password",
        strip=False,
        widget=forms.PasswordInput,
    )
    password2 = forms.CharField(
        label="Confirm password",
        widget=forms.PasswordInput,
        strip=False,
    )

    class Meta:
        model = User
        fields = (
            "role",
            "username",
            "email",
            "first_name",
            "last_name",
            "phone",
            "faculty",
            "department",
            "profile_image",
        )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Limit the role choices so users can't register as ADMIN
        self.fields['role'].choices = [
            (User.Role.STUDENT.value, User.Role.STUDENT.label),
            (User.Role.STAFF.value, User.Role.STAFF.label),
        ]

    def clean_email(self):
        email = self.cleaned_data.get("email")
        if email and User.objects.filter(email__iexact=email).exists():
            raise ValidationError("This email is already registered.")
        return email


class UserUpdateForm(BootstrapFormMixin, forms.ModelForm):
    class Meta:
        model = User
        fields = (
            "first_name",
            "last_name",
            "phone",
            "faculty",
            "department",
            "profile_image",
        )

    def clean_profile_image(self):
        img = self.cleaned_data.get("profile_image")
        validate_image_upload(img, field_name="profile_image")
        return img






class LoginForm(BootstrapFormMixin, AuthenticationForm):
    """Custom login form that applies Bootstrap styling."""
    pass




