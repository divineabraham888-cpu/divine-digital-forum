from django.contrib.auth.views import LoginView
from django.urls import reverse_lazy

class WorkerLoginView(LoginView):
    template_name = 'accounts/login.html'
    redirect_authenticated_user = True
    
    def get_success_url(self):
        # If the user has 'is_staff' checked in the Admin panel, they go to Admin
        if self.request.user.is_staff:
            return reverse_lazy('admin_dashboard')
        # Otherwise, they go to the Worker dashboard
        return reverse_lazy('worker_dashboard')
    