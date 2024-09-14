from django import forms
from .models import Scan

class ScanForm(forms.ModelForm):
    class Meta:
        model = Scan
        fields = ['image']  # Assuming 'image' is the field that stores the uploaded file
