from django.db import models
from django.conf import settings
from django.utils import timezone
from datetime import timedelta
from django.db.models.signals import post_save
from django.dispatch import receiver

USER_MODEL = settings.AUTH_USER_MODEL

# --- 1. USER & PROFILE MODELS ---
class Profile(models.Model):
    user = models.OneToOneField(USER_MODEL, on_delete=models.CASCADE)
    image = models.ImageField(default='default.jpg', upload_to='profile_pics')
    
    def __str__(self): 
        return f'{self.user.username} Profile'

class WorkerProfile(models.Model):
    user = models.OneToOneField(USER_MODEL, on_delete=models.CASCADE, related_name='worker_profile')
    access_level = models.CharField(max_length=50, default='Standard Worker', blank=True)
    is_suspended = models.BooleanField(default=False)
    is_blocked = models.BooleanField(default=False)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self): 
        return f"{self.user.username} - {self.access_level}"

class WorkerActivity(models.Model):
    user = models.OneToOneField(USER_MODEL, on_delete=models.CASCADE, related_name='activity')
    current_page = models.CharField(max_length=255, default="Dashboard Home")
    last_action = models.CharField(max_length=255, default="Viewing Dashboard")
    last_seen = models.DateTimeField(auto_now=True)
    
    class Meta: 
        verbose_name_plural = "Worker Activities"
        
    def is_online(self): 
        return self.last_seen >= timezone.now() - timedelta(seconds=15)
        
    def __str__(self): 
        return f"{self.user.username} - {self.current_page}"

# --- 2. TASKS & SUBMISSIONS ---
class Task(models.Model):
    title = models.CharField(max_length=255)
    description = models.TextField()
    assigned_to = models.ForeignKey(USER_MODEL, on_delete=models.CASCADE, related_name='assigned_tasks')
    created_by = models.ForeignKey(USER_MODEL, on_delete=models.CASCADE, related_name='created_tasks')
    status = models.CharField(max_length=50, default='Pending')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self): 
        return self.title

class Submission(models.Model):
    task = models.ForeignKey(Task, on_delete=models.CASCADE, related_name='submissions')
    worker = models.ForeignKey(USER_MODEL, on_delete=models.CASCADE)
    content = models.TextField()
    worker_notes = models.TextField(blank=True, null=True)
    file_upload = models.FileField(upload_to='uploads/', blank=True, null=True)
    submitted_at = models.DateTimeField(auto_now_add=True)

class WorkSubmission(models.Model):
    worker = models.ForeignKey(USER_MODEL, on_delete=models.CASCADE)
    title = models.CharField(max_length=200)
    content_or_link = models.TextField(help_text="The actual work or a link to it")
    submitted_at = models.DateTimeField(auto_now_add=True)
    ai_score = models.IntegerField(null=True, blank=True)
    ai_feedback = models.TextField(null=True, blank=True)
    is_reviewed = models.BooleanField(default=False)

# --- 3. SYSTEM LOGGING & METRICS ---
class ActivityLog(models.Model):
    worker = models.ForeignKey(USER_MODEL, on_delete=models.CASCADE, related_name='activities')
    action = models.CharField(max_length=255)
    ip_address = models.GenericIPAddressField(null=True, blank=True)
    risk_score = models.IntegerField(default=0)
    timestamp = models.DateTimeField(auto_now_add=True)
class PerformanceMetric(models.Model):
    worker = models.OneToOneField(USER_MODEL, on_delete=models.CASCADE, related_name='metrics')
    score = models.IntegerField(default=100)
    tasks_completed = models.PositiveIntegerField(default=0)
    avg_resolution_time_minutes = models.FloatField(default=0.0)
    efficiency_score = models.FloatField(default=0.0)
    last_active = models.DateTimeField(auto_now=True)
    
    def update_score(self):
        self.efficiency_score = (self.tasks_completed * 10) / (self.avg_resolution_time_minutes or 1)
        self.save()

# --- 4. COMMUNICATIONS & LOGISTICS ---
class GlobalAnnouncement(models.Model):
    title = models.CharField(max_length=200)
    message = models.TextField()
    is_high_priority = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    # --- 5. SUPPORT, CHAT & FEEDBACK ---
class SupportTicket(models.Model):
    user = models.ForeignKey(USER_MODEL, on_delete=models.CASCADE, related_name='tickets')
    title = models.CharField(max_length=200, default="Support Request")
    message = models.TextField(blank=True, null=True)
    status = models.CharField(max_length=50, default='Open')
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Ticket {self.id} - {self.user.username}"

class ChatMessage(models.Model):
    sender = models.ForeignKey(USER_MODEL, on_delete=models.CASCADE, related_name='sent_messages')
    receiver = models.ForeignKey(USER_MODEL, on_delete=models.CASCADE, related_name='received_messages')
    content = models.TextField()
    timestamp = models.DateTimeField(auto_now_add=True)
    is_read = models.BooleanField(default=False)

    def __str__(self):
        return f"From {self.sender} to {self.receiver}"

class SystemBroadcast(models.Model):
    title = models.CharField(max_length=200)
    message = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.title

class Suggestion(models.Model):
    user = models.ForeignKey(USER_MODEL, on_delete=models.CASCADE)
    title = models.CharField(max_length=200)
    content = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.title