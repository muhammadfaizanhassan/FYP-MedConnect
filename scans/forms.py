from django import forms
from .models import Scan

class ScanForm(forms.ModelForm):
    scan_type = forms.ChoiceField(
        choices=Scan.SCAN_TYPE_CHOICES,
        widget=forms.Select(attrs={
            'class': 'form-select form-select-lg',
            'id': 'scan_type',
        }),
        label='Scan Type',
        help_text='Select the type of medical scan you are uploading',
        required=True
    )
    
    image = forms.ImageField(
        widget=forms.FileInput(attrs={
            'class': 'file-input',
            'accept': 'image/*',
            'id': 'image',
        }),
        label='Scan Image',
        help_text='Upload your medical scan image (JPG, PNG, GIF - Max 10MB)',
        required=True
    )
    
    class Meta:
        model = Scan
        fields = ['scan_type', 'image']
