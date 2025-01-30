from django.contrib import admin
from .models import DoctorProfile, PatientProfile, Appointment, Contact, Review, Report

@admin.register(DoctorProfile)
class DoctorProfileAdmin(admin.ModelAdmin):
    list_display = ('user', 'specialization', 'office_location', 'phone_number')

@admin.register(PatientProfile)
class PatientProfileAdmin(admin.ModelAdmin):
    list_display = ('user', 'age', 'gender', 'contact_number')

@admin.register(Appointment)
class AppointmentAdmin(admin.ModelAdmin):
    list_display = ('patient', 'doctor', 'appointment_date', 'status')
    list_filter = ('status', 'appointment_date', 'doctor')
    search_fields = ('patient__username', 'doctor__user__username')

@admin.register(Contact)
class ContactAdmin(admin.ModelAdmin):
    list_display = ('name', 'email', 'subject', 'submitted_at', 'is_resolved')
    list_filter = ('is_resolved',)
    search_fields = ('name', 'email', 'subject')

@admin.register(Review)
class ReviewAdmin(admin.ModelAdmin):
    list_display = ('appointment', 'rating', 'created_at')
    list_filter = ('rating',)
    search_fields = ('appointment__patient__username', 'appointment__doctor__user__username')

@admin.register(Report)
class ReportAdmin(admin.ModelAdmin):
    list_display = ('appointment', 'file', 'uploaded_at')
    search_fields = ('appointment__patient__username', 'appointment__doctor__user__username')
