from django.contrib import admin
from django.urls import path, include
from django.shortcuts import redirect

def home_redirect(request):
    return redirect('dashboard:auth')

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', home_redirect, name='home'), # Redirects root URL '/' to your login page
    path('dashboard/', include('dashboard.urls', namespace='dashboard')), # Includes your dashboard urls
]