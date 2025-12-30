from django.contrib.auth.models import User
from django.db import models
from django.core.validators import MinValueValidator, MaxValueValidator
from datetime import timedelta
from main.fields import EncryptedTextField, EncryptedCharField

class DoctorProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, unique=True)
    specialization = models.CharField(max_length=255)
    office_location = models.CharField(max_length=255)
    phone_number = EncryptedCharField(max_length=15, blank=True, null=True, help_text="Encrypted phone number")
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
    # Encrypted fields for HIPAA compliance
    medical_history = EncryptedTextField(blank=True, help_text="Encrypted medical history")
    gender = models.CharField(
        max_length=10,
        choices=[('male', 'Male'), ('female', 'Female'), ('other', 'Other')],
        blank=True, null=True
    )
    contact_number = EncryptedCharField(max_length=15, blank=True, null=True, help_text="Encrypted contact number")
    profile_picture = models.ImageField(upload_to='patient_profiles/', blank=True, null=True)

    def __str__(self):
        return f"{self.user.username} - {self.age} years old"

    class Meta:
        verbose_name_plural = "Patient Profiles"


    class Meta:
        verbose_name_plural = "Patient Profiles"



from django.core.exceptions import ValidationError

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
    medical_history = EncryptedTextField(blank=True, null=True, help_text="Encrypted medical history for appointment")
    notes = EncryptedTextField(blank=True, null=True, help_text="Encrypted appointment notes")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-appointment_date', '-appointment_time']
        unique_together = [['doctor', 'appointment_date', 'appointment_time']]

    def __str__(self):
        return f"Appointment with Dr. {self.doctor.user.username} on {self.appointment_date}"


class Contact(models.Model):
    name = models.CharField(max_length=255)
    email = models.EmailField()
    subject = models.CharField(max_length=255, blank=True)
    message = EncryptedTextField(help_text="Encrypted contact message")
    submitted_at = models.DateTimeField(auto_now_add=True)
    is_resolved = models.BooleanField(default=False)

    def __str__(self):
        return f"Message from {self.name} ({self.email})"

    class Meta:
        ordering = ['-submitted_at']
        verbose_name_plural = "Contact Messages"



from django.db import models
from django.contrib.auth.models import User

class Report(models.Model):
    appointment = models.ForeignKey(
        'Appointment',
        on_delete=models.CASCADE,
        related_name='reports'
    )
    file = models.FileField(upload_to='patient_reports/', help_text="Encrypted file storage")
    uploaded_at = models.DateTimeField(auto_now_add=True)
    # Note: File encryption should be handled at storage level in production


class AuditLog(models.Model):
    """
    Audit log for tracking access to PHI (Protected Health Information)
    Required for HIPAA compliance
    """
    ACTION_CHOICES = [
        ('view', 'View'),
        ('create', 'Create'),
        ('update', 'Update'),
        ('delete', 'Delete'),
        ('export', 'Export'),
        ('access', 'Access'),
    ]
    
    RESOURCE_TYPE_CHOICES = [
        ('patient_profile', 'Patient Profile'),
        ('appointment', 'Appointment'),
        ('medical_history', 'Medical History'),
        ('report', 'Medical Report'),
        ('scan', 'Medical Scan'),
        ('conversation', 'Chat Conversation'),
    ]
    
    user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, related_name='audit_logs')
    action = models.CharField(max_length=20, choices=ACTION_CHOICES)
    resource_type = models.CharField(max_length=50, choices=RESOURCE_TYPE_CHOICES)
    resource_id = models.CharField(max_length=255)
    ip_address = models.GenericIPAddressField(null=True, blank=True)
    user_agent = models.TextField(blank=True)
    details = models.JSONField(default=dict, blank=True)
    timestamp = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['-timestamp']
        indexes = [
            models.Index(fields=['user', 'timestamp']),
            models.Index(fields=['resource_type', 'resource_id']),
            models.Index(fields=['action', 'timestamp']),
        ]
        verbose_name = 'Audit Log Entry'
        verbose_name_plural = 'Audit Log Entries'
    
    def __str__(self):
        return f"{self.user} - {self.action} - {self.resource_type} - {self.timestamp}"

    def __str__(self):
        return f"Report for Appointment #{self.appointment.id}"
