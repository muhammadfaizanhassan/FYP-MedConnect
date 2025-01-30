from django import forms
from django.contrib.auth.models import User
from django.contrib.auth.forms import UserCreationForm
from .models import DoctorProfile, PatientProfile
from .models import Appointment

class DoctorRegistrationForm(UserCreationForm):
    email = forms.EmailField(required=True)
    specialization = forms.CharField(max_length=255)
    office_location = forms.CharField(max_length=255, required=False)

    class Meta:
        model = User
        fields = ['username', 'email', 'password1', 'password2']

class PatientRegistrationForm(UserCreationForm):
    email = forms.EmailField(required=True)
    age = forms.IntegerField()
    medical_history = forms.CharField(widget=forms.Textarea, required=False)

    class Meta:
        model = User
        fields = ['username', 'email', 'password1', 'password2']

class AppointmentForm(forms.ModelForm):
    class Meta:
        model = Appointment
        fields = ['doctor', 'appointment_date', 'appointment_time']
        widgets = {
            'appointment_date': forms.DateInput(attrs={'type': 'date'}),
            'appointment_time': forms.TimeInput(attrs={'type': 'time'}),
        }