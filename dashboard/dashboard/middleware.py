from .models import WorkerActivity

class ActivityTrackingMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        response = self.get_response(request)
        
        # Only log authenticated workers moving through the dashboard
        if request.user.is_authenticated and 'dashboard' in request.path:
            WorkerActivity.objects.create(
                user=request.user,
                activity_type='NAVIGATE',
                page_url=request.path,
                ip_address=request.META.get('REMOTE_ADDR')
            )
        return response