"""
Audit logging for HIPAA compliance
Tracks all access to Protected Health Information (PHI)
"""
import json
from datetime import datetime
from django.contrib.auth.models import User

# Import AuditLog from models to avoid circular import
def get_audit_log_model():
    """Get AuditLog model to avoid circular imports"""
    from main.models import AuditLog
    return AuditLog

def log_phi_access(user, action, resource_type, resource_id, request=None, details=None):
    """
    Log access to Protected Health Information (PHI)
    
    Args:
        user: User accessing the data
        action: Type of action (view, create, update, delete, export, access)
        resource_type: Type of resource being accessed
        resource_id: ID of the resource
        request: Django request object (for IP and user agent)
        details: Additional details as dictionary
    """
    try:
        ip_address = None
        user_agent = ''
        
        if request:
            ip_address = get_client_ip(request)
            user_agent = request.META.get('HTTP_USER_AGENT', '')[:500]  # Limit length
        
        AuditLog = get_audit_log_model()
        AuditLog.objects.create(
            user=user,
            action=action,
            resource_type=resource_type,
            resource_id=str(resource_id),
            ip_address=ip_address,
            user_agent=user_agent,
            details=details or {}
        )
    except Exception as e:
        # Log error but don't break the application
        print(f"Audit logging error: {e}")

def get_client_ip(request):
    """Get client IP address from request"""
    x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
    if x_forwarded_for:
        ip = x_forwarded_for.split(',')[0]
    else:
        ip = request.META.get('REMOTE_ADDR')
    return ip

