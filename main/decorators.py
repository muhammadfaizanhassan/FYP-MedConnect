"""
Decorators for HIPAA-compliant access control
"""
from functools import wraps
from django.shortcuts import redirect
from django.contrib import messages
from main.utils.audit_log import log_phi_access

def require_phi_access(action='view'):
    """
    Decorator to log PHI access and ensure proper authorization
    """
    def decorator(view_func):
        @wraps(view_func)
        def wrapper(request, *args, **kwargs):
            if not request.user.is_authenticated:
                messages.error(request, "Authentication required to access this resource.")
                return redirect('login')
            
            # Log the access
            resource_type = kwargs.get('resource_type', 'unknown')
            resource_id = kwargs.get('resource_id', 'unknown')
            
            log_phi_access(
                user=request.user,
                action=action,
                resource_type=resource_type,
                resource_id=resource_id,
                request=request,
                details={'view': view_func.__name__}
            )
            
            return view_func(request, *args, **kwargs)
        return wrapper
    return decorator

def require_patient_or_doctor(view_func):
    """
    Decorator to ensure user is either a patient or doctor
    """
    @wraps(view_func)
    def wrapper(request, *args, **kwargs):
        if not request.user.is_authenticated:
            messages.error(request, "Please log in to access this page.")
            return redirect('login')
        
        # Check if user has patient or doctor profile
        from main.models import PatientProfile, DoctorProfile
        
        is_patient = PatientProfile.objects.filter(user=request.user).exists()
        is_doctor = DoctorProfile.objects.filter(user=request.user).exists()
        
        if not (is_patient or is_doctor):
            messages.error(request, "You need to complete your profile to access this page.")
            return redirect('home')
        
        return view_func(request, *args, **kwargs)
    return wrapper

