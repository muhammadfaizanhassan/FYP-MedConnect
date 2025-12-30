from django.contrib.auth.models import User
from django.db import models
from django.core.validators import MinValueValidator, MaxValueValidator
from datetime import timedelta

class DoctorProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    specialization = models.CharField(max_length=255)
    office_location = models.CharField(max_length=255)  
    phone_number = models.CharField(max_length=15, blank=True, null=True)
    consultation_fee = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    profile_picture = models.ImageField(upload_to='doctor_profiles/', blank=True, null=True)

    def __str__(self):
        return f"{self.user.username} - {self.specialization}"

    class Meta:
        verbose_name_plural = "Doctor Profiles"


class PatientProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    age = models.IntegerField(
        validators=[MinValueValidator(0), MaxValueValidator(120)]
    )
    medical_history = models.TextField(blank=True)
    gender = models.CharField(max_length=10, choices=[
        ('male', 'Male'), 
        ('female', 'Female'), 
        ('other', 'Other')
    ], blank=True, null=True)
    contact_number = models.CharField(max_length=15, blank=True, null=True)
    profile_picture = models.ImageField(upload_to='patient_profiles/', blank=True, null=True)

    def __str__(self):
        return f"{self.user.username} - {self.age} years old"

    class Meta:
        verbose_name_plural = "Patient Profiles"


class Appointment(models.Model):
    APPOINTMENT_STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('confirmed', 'Confirmed'),
        ('cancelled', 'Cancelled'),
        ('completed', 'Completed')
    ]

    patient = models.ForeignKey(User, on_delete=models.CASCADE, related_name='appointments')
    doctor = models.ForeignKey(DoctorProfile, on_delete=models.CASCADE, related_name='appointments')
    appointment_date = models.DateField()
    appointment_time = models.TimeField()
    appointment_duration = models.DurationField(default=timedelta(minutes=30))
    is_confirmed = models.BooleanField(default=False)
    payment_status = models.BooleanField(default=False)
    status = models.CharField(
        max_length=20, 
        choices=APPOINTMENT_STATUS_CHOICES, 
        default='pending'
    )
    notes = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Appointment with Dr. {self.doctor.user.username} on {self.appointment_date}"

    class Meta:
        ordering = ['-appointment_date', '-appointment_time']
        unique_together = [['doctor', 'appointment_date', 'appointment_time']]


class Contact(models.Model):
    name = models.CharField(max_length=255)
    email = models.EmailField()
    subject = models.CharField(max_length=255, blank=True)  # Added subject field
    message = models.TextField()
    submitted_at = models.DateTimeField(auto_now_add=True)
    is_resolved = models.BooleanField(default=False)

    def __str__(self):
        return f"Message from {self.name} ({self.email})"

    class Meta:
        ordering = ['-submitted_at']
        verbose_name_plural = "Contact Messages"
