
from django.http import Http404
from django.utils.deprecation import MiddlewareMixin
from .models import Tenant


class TenantMiddleware(MiddlewareMixin):
    """
    Middleware to identify tenant based on HTTP Host header
    and make tenant available throughout the request
    """
    
    def process_request(self, request):
        host = request.get_host().split(':')[0]  # Remove port if present
        
        try:
            tenant = Tenant.objects.get(domain=host, is_active=True)
            request.tenant = tenant
        except Tenant.DoesNotExist:
            # For development, allow localhost and replit domains
            if host in ['localhost', '127.0.0.1'] or 'replit' in host:
                # Try to get first active tenant for development
                tenant = Tenant.objects.filter(is_active=True).first()
                if tenant:
                    request.tenant = tenant
                else:
                    request.tenant = None
            else:
                request.tenant = None
        
        return None
