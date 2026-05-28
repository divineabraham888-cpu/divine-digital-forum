from django.contrib import admin
from django.urls import path, include
from django.shortcuts import redirect
from django.conf import settings # Add this
from django.conf.urls.static import static # Add this

# HOME REDIRECT
def home_redirect(request):
    return redirect('dashboard:auth') 

urlpatterns = [
    path('', home_redirect),
    path('admin/', admin.site.urls),
    path('dashboard/', include('dashboard.urls')),
]

# Add this block at the very bottom
if settings.DEBUG:
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)