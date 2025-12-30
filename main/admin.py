from django.contrib import admin
from .models import DoctorProfile, PatientProfile, Appointment, Contact, Report, AuditLog

@admin.register(DoctorProfile)
class DoctorProfileAdmin(admin.ModelAdmin):
    list_display = ('user', 'specialization', 'office_location')
    readonly_fields = ('phone_number',)  # Encrypted field - read-only in admin
    
    def get_readonly_fields(self, request, obj=None):
        # Make encrypted fields read-only to prevent accidental exposure
        return self.readonly_fields + ('phone_number',)

@admin.register(PatientProfile)
class PatientProfileAdmin(admin.ModelAdmin):
    list_display = ('user', 'age', 'gender')
    readonly_fields = ('medical_history', 'contact_number')  # Encrypted fields
    
    def get_readonly_fields(self, request, obj=None):
        # Make encrypted fields read-only to prevent accidental exposure
        return self.readonly_fields + ('medical_history', 'contact_number')

@admin.register(Appointment)
class AppointmentAdmin(admin.ModelAdmin):
    list_display = ('patient', 'doctor', 'appointment_date', 'status')
    readonly_fields = ('medical_history', 'notes')  # Encrypted fields
    
    def get_readonly_fields(self, request, obj=None):
        return self.readonly_fields + ('medical_history', 'notes')

@admin.register(Contact)
class ContactAdmin(admin.ModelAdmin):
    list_display = ('name', 'email', 'subject', 'submitted_at', 'is_resolved')
    readonly_fields = ('message',)  # Encrypted field
    
    def get_readonly_fields(self, request, obj=None):
        return self.readonly_fields + ('message',)

@admin.register(Report)
class ReportAdmin(admin.ModelAdmin):
    list_display = ('appointment', 'uploaded_at')

@admin.register(AuditLog)
class AuditLogAdmin(admin.ModelAdmin):
    list_display = ('user', 'action', 'resource_type', 'resource_id', 'timestamp', 'ip_address')
    list_filter = ('action', 'resource_type', 'timestamp')
    search_fields = ('user__username', 'resource_id', 'ip_address')
    readonly_fields = ('user', 'action', 'resource_type', 'resource_id', 'ip_address', 
                      'user_agent', 'details', 'timestamp')
    date_hierarchy = 'timestamp'
    
    def has_add_permission(self, request):
        return False  # Prevent manual creation of audit logs
    
    def has_change_permission(self, request, obj=None):
        return False  # Prevent modification of audit logs
