from django.urls import path

from . import views


app_name = "rentals"

urlpatterns = [
    # Placeholder route (no models/views implemented yet)
    path("", views.placeholder, name="placeholder"),
]


