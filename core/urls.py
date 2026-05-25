from django.contrib import admin
from django.urls import path, include
from django.shortcuts import redirect


# HOME REDIRECT
def home_redirect(request):
    return redirect('/accounts/login/')


urlpatterns = [
    path('', home_redirect),

    path('admin/', admin.site.urls),

    path('accounts/', include('accounts.urls')),

    path('dashboard/', include('dashboard.urls')),
]