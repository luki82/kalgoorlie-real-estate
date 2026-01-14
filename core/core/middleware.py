from django.http import Http404

class RestrictAdminMiddleware:
    """
    Restricts access to the admin page to specific IP addresses.
    """
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        # Change 'staff-portal-secure' to match whatever your actual admin URL is
        if request.path.startswith('/staff-portal-secure/'):
            
            # Get the user's IP address
            ip = request.META.get('REMOTE_ADDR')
            
            # List of allowed IPs (Add your Home/Office IP here)
            # 127.0.0.1 is 'localhost' (your computer right now)
            ALLOWED_IPS = ['127.0.0.1'] 
            
            if ip not in ALLOWED_IPS:
                # If they are not on the list, pretend the page doesn't exist
                raise Http404

        return self.get_response(request)