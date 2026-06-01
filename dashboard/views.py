import json
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import JsonResponse
from django.db.models import Q
from django.db import transaction
from django.contrib.auth import get_user_model, login
from django.contrib.auth.forms import AuthenticationForm
from django.utils.text import slugify

# Imports from models
from .models import (
    ActivityLog, PerformanceMetric, WorkerProfile, 
    SupportTicket, Task, ChatMessage, SystemBroadcast, WorkerActivity,
    WorkSubmission, Suggestion
)
from .forms import UserRegistrationForm, ProfileForm

User = get_user_model()
FORUM_BRANDING = "Divine Digital Forum"

# ==========================================
# 1. AUTHENTICATION SYSTEM
# ==========================================

def auth(request):
    user_form = UserRegistrationForm()
    profile_form = ProfileForm()
    login_form = AuthenticationForm()

    if request.method == 'POST':
        if 'signup_btn' in request.POST:
            user_form = UserRegistrationForm(request.POST)
            profile_form = ProfileForm(request.POST, request.FILES)
            if user_form.is_valid() and profile_form.is_valid():
                with transaction.atomic():
                    user = user_form.save(commit=False)
                    user.set_password(user_form.cleaned_data['password'])
                    user.save()
                    profile = profile_form.save(commit=False)
                    profile.user = user
                    profile.save()
                    login(request, user)
                    return redirect('dashboard:worker_dashboard')

        elif 'login_btn' in request.POST:
            login_form = AuthenticationForm(data=request.POST)
            if login_form.is_valid():
                user = login_form.get_user()
                login(request, user)
                return redirect('dashboard:admin_dashboard' if user.is_superuser else 'dashboard:worker_dashboard')

    return render(request, 'dashboard/auth.html', {
        'user_form': user_form, 'profile_form': profile_form, 'login_form': login_form
    })

# ==========================================
# 2. DASHBOARD CENTRALS
# ==========================================
@login_required
def admin_dashboard(request):
    if not request.user.is_superuser: 
        return redirect('dashboard:worker_dashboard')
    
    if request.method == 'POST':
        if 'broadcast_submit' in request.POST:
            SystemBroadcast.objects.create(
                title=request.POST.get('title'), 
                message=request.POST.get('message')
            )
            messages.success(request, "Broadcast deployed.")
            return redirect('dashboard:admin_dashboard')
            
        elif 'delete_broadcast' in request.POST:
            broadcast_id = request.POST.get('broadcast_id')
            SystemBroadcast.objects.filter(id=broadcast_id).delete()
            messages.success(request, "Broadcast removed.")
            return redirect('dashboard:admin_dashboard')

    # ADDED: 'submissions' query included in the context dictionary below
    context = {
        'workers': User.objects.exclude(is_superuser=True).prefetch_related('worker_profile'),
        'broadcasts': SystemBroadcast.objects.all().order_by('-created_at'),
        'worker_activities': WorkerActivity.objects.all().order_by('-last_seen')[:10],
        'submissions': WorkSubmission.objects.all().order_by('-submitted_at'), 
    }
    return render(request, 'dashboard/admin_dashboard.html', context)
    

@login_required
def worker_dashboard(request):
    if request.user.is_superuser: 
        return redirect('dashboard:admin_dashboard')
    
    metrics, _ = PerformanceMetric.objects.get_or_create(worker=request.user)
    
    context = {
        'forum_name': FORUM_BRANDING,
        'user_details': request.user,
        'tasks': Task.objects.filter(assigned_to=request.user, status='Pending'),
        'metrics': metrics,
        'broadcasts': SystemBroadcast.objects.all().order_by('-created_at'),
        'submissions': WorkSubmission.objects.filter(worker=request.user).order_by('-submitted_at'),
        'suggestions': Suggestion.objects.filter(user=request.user).order_by('-created_at'),
        'activities': ActivityLog.objects.filter(worker=request.user).order_by('-timestamp')[:5],
        'tickets': SupportTicket.objects.filter(user=request.user).order_by('-created_at')[:3],
        'ai_health': "Optimal" if metrics.score > 70 else "Warning",
    }
    return render(request, 'dashboard/worker_dashboard.html', context)

# ==========================================
# 3. WORKER MANAGEMENT & TASKS
# ==========================================

@login_required
def manage_workers(request):
    workers = User.objects.exclude(is_superuser=True).prefetch_related('worker_profile')
    return render(request, 'dashboard/manage_workers.html', {
        'forum_name': FORUM_BRANDING, 
        'workers': workers
    })

@login_required
def manage_worker_action(request, user_id, action):
    target_user = get_object_or_404(User, id=user_id)
    profile, _ = WorkerProfile.objects.get_or_create(user=target_user)
    
    if action == 'suspend':
        profile.is_suspended = not profile.is_suspended
        profile.save()
    elif action == 'reset_pwd':
        target_user.set_password('DivineUnit2026!')
        target_user.save()
        
    return redirect('dashboard:manage_workers')

@login_required
def edit_worker_profile(request, user_id):
    worker = get_object_or_404(User, id=user_id)
    profile, _ = WorkerProfile.objects.get_or_create(user=worker)
    
    if request.method == 'POST':
        access_level = request.POST.get('access_level')
        if access_level and request.user.is_superuser:
            profile.access_level = access_level
            profile.save()
        return redirect('dashboard:admin_dashboard' if request.user.is_superuser else 'dashboard:worker_dashboard')
        
    return render(request, 'dashboard/edit_worker_profile.html', {'worker': worker})

@login_required
def create_task(request):
    if not request.user.is_superuser: return redirect('dashboard:worker_dashboard')
    if request.method == 'POST':
        Task.objects.create(
            title=request.POST.get('title'),
            description=request.POST.get('description'),
            assigned_to=get_object_or_404(User, id=request.POST.get('assigned_to')),
            created_by=request.user
        )
        return redirect('dashboard:admin_dashboard')
    return render(request, 'dashboard/create_task.html', {'workers': User.objects.exclude(is_superuser=True)})

@login_required
def task_list(request):
    return render(request, 'dashboard/task_list.html', {
        'tasks': Task.objects.filter(assigned_to=request.user).order_by('-created_at'),
    })

@login_required
def submit_task(request, task_id):
    task = get_object_or_404(Task, id=task_id)
    
    if request.method == 'POST':
        # Match the exact fields defined in your WorkSubmission model
        WorkSubmission.objects.create(
            worker=request.user,
            title=task.title,                           # Satisfies the required title field
            content_or_link=request.POST.get('content', '') # Maps your form content to content_or_link
        )
        
        # Optional: Update the task status so it clears from the worker's pending list
        task.status = 'Submitted'
        task.save()
        
        messages.success(request, "Task submitted successfully!")
        return redirect('dashboard:worker_dashboard')
        
    return render(request, 'dashboard/submit_task.html', {'task': task})
# ==========================================
# 4. SUBMISSIONS & COMMUNICATIONS
# ==========================================
import json # Ensure this is at the top of your file

@login_required
def send_message(request, user_id):
    if request.method == 'POST':
        try:
            # TRY TO LOAD JSON FIRST
            data = json.loads(request.body)
            content = data.get('content', '').strip()
        except json.JSONDecodeError:
            # FALLBACK TO POST IF JSON FAILS
            content = request.POST.get('content', '').strip()
            
        if not content:
            return JsonResponse({'status': 'error', 'message': 'Empty message'}, status=400)
        
        try:
            receiver = None
            if int(user_id) != 0:
                receiver = User.objects.get(id=user_id)
            ChatMessage.objects.create(sender=request.user, receiver=receiver, content=content)
            return JsonResponse({'status': 'success'})
        except Exception as e:
            # THIS WILL RETURN THE ACTUAL ERROR TO YOUR BROWSER
            return JsonResponse({'status': 'error', 'message': f'Server Error: {str(e)}'}, status=500)
            
    return JsonResponse({'status': 'error', 'message': 'Method not allowed'}, status=405)


@login_required
def fetch_messages(request, user_id):
    try:
        uid = int(user_id)
        if uid == 0:
            messages_qs = ChatMessage.objects.filter(receiver__isnull=True).order_by('timestamp')
        else:
            target_user = User.objects.get(id=uid)
            messages_qs = ChatMessage.objects.filter(
                (Q(sender=request.user) & Q(receiver=target_user)) |
                (Q(sender=target_user) & Q(receiver=request.user))
            ).order_by('timestamp')
        
        data = [{'sender__username': m.sender.username, 'content': m.content, 'timestamp': m.timestamp.isoformat()} for m in messages_qs]
        return JsonResponse(data, safe=False)
    except:
        return JsonResponse([], safe=False)

@login_required
def video_call_room(request, room_name):
    return render(request, 'dashboard/video_call.html', {
        'room_name': slugify(room_name),
        'user_name': request.user.username,
    })

# ==========================================
# 5. UTILITIES
# ==========================================

@login_required
def p2p_view(request):
    return render(request, 'dashboard/p2p.html', {'contacts': User.objects.exclude(id=request.user.id)})

@login_required
def message_center_view(request):
    return render(request, 'dashboard/message_center.html', {'contacts': User.objects.exclude(id=request.user.id)})

@login_required
def manage_announcements(request):
    if request.method == 'POST':
        SystemBroadcast.objects.create(title=request.POST.get('title'), message=request.POST.get('message'))
    return render(request, 'dashboard/announcements.html', {'announcements': SystemBroadcast.objects.all()})

@login_required
def suggestion_box(request):
    if request.method == 'POST':
        Suggestion.objects.create(user=request.user, content=request.POST.get('content'))
    return render(request, 'dashboard/suggestion_box.html', {'suggestions': Suggestion.objects.all()})

def profile_view(request): return render(request, 'dashboard/profile.html')
def settings_view(request): return render(request, 'dashboard/settings.html')
def leaderboard_view(request): return render(request, 'dashboard/leaderboard.html')

@login_required 
def check_efficiency_api(request):
    metrics, _ = PerformanceMetric.objects.get_or_create(worker=request.user)
    return JsonResponse({'score': metrics.score})

@login_required
def general_hub_view(request):
    return render(request, 'dashboard/general_hub.html', {'contacts': User.objects.exclude(id=request.user.id)})
@login_required
def submissions_dashboard(request):
    return render(request, 'dashboard/submissions_dashboard.html', {
        'submissions': WorkSubmission.objects.all().order_by('-submitted_at'),
    })
@login_required
def message_center_with_worker(request, worker_id):
    # Retrieve the specific worker the user is trying to message
    target_worker = get_object_or_404(User, id=worker_id)
    
    # Return the same template as your message center, 
    # but pass the target worker to the context
    return render(request, 'dashboard/message_center.html', {
        'contacts': User.objects.exclude(id=request.user.id),
        'active_worker': target_worker
    })
