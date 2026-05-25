from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import CustomUser


@admin.register(CustomUser)
class CustomUserAdmin(UserAdmin):
    model = CustomUser
    list_display = ['username', 'email', 'is_worker', 'is_admin', 'is_staff']

    fieldsets = UserAdmin.fieldsets + (
        (None, {'fields': ('is_worker', 'is_admin')}),
    )