from django import forms
from django.contrib.auth.models import User
from django.contrib.auth.forms import UserCreationForm
from .models import DoctorProfile, PatientProfile
from .models import Appointment

class DoctorRegistrationForm(UserCreationForm):
    email = forms.EmailField(required=True)
    specialization = forms.CharField(max_length=255)
    office_location = forms.CharField(max_length=255, required=False)
    phone_number = forms.CharField(max_length=15, required=False)
    consultation_fee = forms.DecimalField(max_digits=10, decimal_places=2, required=False)
    profile_picture = forms.ImageField(required=False)

    class Meta:
        model = User
        fields = ['username', 'email', 'password1', 'password2']
        
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Add Bootstrap classes and placeholders
        self.fields['username'].widget.attrs.update({
            'class': 'form-control',
            'placeholder': 'Choose a username'
        })
        self.fields['email'].widget.attrs.update({
            'class': 'form-control',
            'placeholder': 'your.email@example.com'
        })
        self.fields['password1'].widget.attrs.update({
            'class': 'form-control',
            'placeholder': 'Create a strong password'
        })
        self.fields['password2'].widget.attrs.update({
            'class': 'form-control',
            'placeholder': 'Confirm your password'
        })
        self.fields['specialization'].widget.attrs.update({
            'class': 'form-control',
            'placeholder': 'e.g., Cardiology, Pediatrics, General Medicine'
        })
        self.fields['office_location'].widget.attrs.update({
            'class': 'form-control',
            'placeholder': 'Your clinic or hospital address'
        })
        self.fields['phone_number'].widget.attrs.update({
            'class': 'form-control',
            'placeholder': '+1 (555) 123-4567'
        })
        self.fields['consultation_fee'].widget.attrs.update({
            'class': 'form-control',
            'placeholder': '0.00',
            'step': '0.01',
            'min': '0'
        })
        self.fields['profile_picture'].widget.attrs.update({
            'class': 'form-control',
            'accept': 'image/*'
        })

class PatientRegistrationForm(UserCreationForm):
    email = forms.EmailField(required=True)
    age = forms.IntegerField()
    medical_history = forms.CharField(widget=forms.Textarea(attrs={'rows': 4}), required=False)
    gender = forms.ChoiceField(
        choices=[('', 'Select Gender'), ('male', 'Male'), ('female', 'Female'), ('other', 'Other')],
        required=False
    )
    contact_number = forms.CharField(max_length=15, required=False)
    profile_picture = forms.ImageField(required=False)

    class Meta:
        model = User
        fields = ['username', 'email', 'password1', 'password2']
        
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Add Bootstrap classes and placeholders
        self.fields['username'].widget.attrs.update({
            'class': 'form-control',
            'placeholder': 'Choose a username'
        })
        self.fields['email'].widget.attrs.update({
            'class': 'form-control',
            'placeholder': 'your.email@example.com'
        })
        self.fields['password1'].widget.attrs.update({
            'class': 'form-control',
            'placeholder': 'Create a strong password'
        })
        self.fields['password2'].widget.attrs.update({
            'class': 'form-control',
            'placeholder': 'Confirm your password'
        })
        self.fields['age'].widget.attrs.update({
            'class': 'form-control',
            'placeholder': 'Your age',
            'min': '0',
            'max': '120'
        })
        self.fields['gender'].widget.attrs.update({
            'class': 'form-select'
        })
        self.fields['contact_number'].widget.attrs.update({
            'class': 'form-control',
            'placeholder': '+1 (555) 123-4567'
        })
        self.fields['profile_picture'].widget.attrs.update({
            'class': 'form-control',
            'accept': 'image/*'
        })
        self.fields['medical_history'].widget.attrs.update({
            'class': 'form-control',
            'placeholder': 'Any previous medical conditions, allergies, or relevant health information (optional)'
        })

class AppointmentForm(forms.ModelForm):
    class Meta:
        model = Appointment
        fields = ['doctor', 'appointment_date', 'appointment_time']
        widgets = {
            'appointment_date': forms.DateInput(attrs={'type': 'date'}),
            'appointment_time': forms.TimeInput(attrs={'type': 'time'}),
        }