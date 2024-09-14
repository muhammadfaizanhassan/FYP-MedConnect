from django.contrib.auth.models import User
from django.db import models


class DoctorProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    specialization = models.CharField(max_length=255)
    office_location = models.CharField(max_length=255)  # Add office location field

    def __str__(self):
        return self.user.username


class PatientProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    age = models.IntegerField()
    medical_history = models.TextField()

    def __str__(self):
        return self.user.username


class Appointment(models.Model):
    patient = models.ForeignKey(User, on_delete=models.CASCADE)
    doctor = models.ForeignKey(DoctorProfile, on_delete=models.CASCADE)
    appointment_date = models.DateField()
    appointment_time = models.TimeField()
    is_confirmed = models.BooleanField(default=False)
    payment_status = models.BooleanField(default=False)

    def __str__(self):
        return f"Appointment with {self.doctor.user.username} on {self.appointment_date} at {self.appointment_time}"



class Contact(models.Model):
    name = models.CharField(max_length=255)
    email = models.EmailField()
    message = models.TextField()
    submitted_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Message from {self.name} ({self.email})"
