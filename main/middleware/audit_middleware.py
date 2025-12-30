"""
Middleware for automatic audit logging of PHI access
"""
from main.utils.audit_log import log_phi_access

class PHIAuditMiddleware:
    """
    Middleware to automatically log access to Protected Health Information
    """
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        # Process request
        response = self.get_response(request)
        
        # Log PHI access for specific views
        if request.user.is_authenticated:
            # Check if this is a view that accesses PHI
            path = request.path
            
            # Patient profile access
            if '/patient/dashboard/' in path or '/patient/' in path:
                log_phi_access(
                    user=request.user,
                    action='access',
                    resource_type='patient_profile',
                    resource_id=str(request.user.id),
                    request=request,
                    details={'path': path, 'method': request.method}
                )
            
            # Doctor profile access
            elif '/doctor/dashboard/' in path or '/doctor/' in path:
                log_phi_access(
                    user=request.user,
                    action='access',
                    resource_type='patient_profile',
                    resource_id=str(request.user.id),
                    request=request,
                    details={'path': path, 'method': request.method}
                )
            
            # Appointment access
            elif '/appointment/' in path or '/book-appointment/' in path:
                log_phi_access(
                    user=request.user,
                    action='access',
                    resource_type='appointment',
                    resource_id='multiple',
                    request=request,
                    details={'path': path, 'method': request.method}
                )
            
            # Medical reports/scans
            elif '/scans/' in path:
                log_phi_access(
                    user=request.user,
                    action='access',
                    resource_type='scan',
                    resource_id='multiple',
                    request=request,
                    details={'path': path, 'method': request.method}
                )
        
        return response

