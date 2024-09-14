from django.urls import path
from . import views

app_name = 'scans'  # Ensure this is set if you're using a namespace in the main urls.py

urlpatterns = [
    path('upload/', views.upload_scan, name='upload_scan'),  # Ensure this is present
]
