from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import CustomUser

# Use the decorator to register the model AND the admin class at once
@admin.register(CustomUser)
class CustomUserAdmin(UserAdmin):
    model = CustomUser
    list_display = ['username', 'email', 'is_worker', 'is_admin', 'is_staff']
    fieldsets = UserAdmin.fieldsets + (
        (None, {'fields': ('is_worker', 'is_admin')}),
    )

# DELETE THIS LINE IF IT EXISTS AT THE BOTTOM OF THE FILE:
# admin.site.register(CustomUser, CustomUserAdmin)