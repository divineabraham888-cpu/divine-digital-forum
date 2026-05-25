from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from accounts.models import CustomUser 
from .models import ActivityLog, Task, Submission, Message, Announcement, TimetableEvent


admin.site.register(ActivityLog)
admin.site.register(Task)
admin.site.register(Submission)
admin.site.register(Message)
admin.site.register(Announcement)
admin.site.register(TimetableEvent)