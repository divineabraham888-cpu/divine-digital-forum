from django.db import models
from django.contrib.auth.models import AbstractUser
from django.conf import settings

# --- USER MODEL ---
class CustomUser(AbstractUser):
    is_worker = models.BooleanField(default=False)
    is_admin = models.BooleanField(default=False)
    
    def __str__(self):
        return self.username

# --- SYSTEM LOGS ---
class ActivityLog(models.Model):
    # Add the related_name='account_logs' here
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='account_logs')
    # ... rest of your code ...
# --- TASKS & MESSAGES (Added to prevent views.py from crashing) ---
class Task(models.Model):
    title = models.CharField(max_length=200)
    assigned_to = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='tasks')
    status = models.CharField(max_length=50, default='Pending')
    
    def __str__(self):
        return self.title

class Message(models.Model):
    sender = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='sent_messages')
    receiver = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='received_messages')
    content = models.TextField()
    timestamp = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Message from {self.sender.username} to {self.receiver.username}"

# --- ANNOUNCEMENTS & TIMETABLE ---
class Announcement(models.Model):
    PRIORITY_CHOICES = [
        ('Low', 'Low'),
        ('Medium', 'Medium'),
        ('High', 'High'),
    ]
    
    title = models.CharField(max_length=200)
    message = models.TextField()
    priority = models.CharField(max_length=20, choices=PRIORITY_CHOICES, default='Medium')
    posted_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='announcements')
    date_posted = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"[{self.priority}] {self.title}"

class TimetableEvent(models.Model):
    title = models.CharField(max_length=200)
    description = models.TextField(blank=True, null=True)
    event_date = models.DateField()
    event_time = models.TimeField()

    def __str__(self):
        return f"{self.title} - {self.event_date}"