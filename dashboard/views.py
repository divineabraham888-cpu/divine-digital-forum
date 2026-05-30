import json
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import JsonResponse
from django.db.models import Q, Avg
from django.db import transaction
from django.contrib.auth import get_user_model, login
from django.contrib.auth.forms import AuthenticationForm

# Consolidated model and form imports
from .models import (
    ActivityLog, PerformanceMetric, GlobalAnnouncement, WorkerProfile, 
    SupportTicket, Task, ChatMessage, SystemBroadcast, WorkerActivity,
    WorkSubmission, Suggestion
)
from .forms import UserRegistrationForm, ProfileForm

User = get_user_model()
FORUM_BRANDING = "Divine Digital Forum"

# ==========================================
# 1. AUTHENTICATION SYSTEM
# ==========================================

def auth_view(request):
    """Handles unified user registration and authentication logic."""
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
    """Master panel tracking system actions, broadcasts, and active operations."""
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

    context = {
        'workers': User.objects.exclude(is_superuser=True).prefetch_related('worker_profile'),
        'broadcasts': SystemBroadcast.objects.all().order_by('-created_at'),
        'worker_activities': WorkerActivity.objects.all().order_by('-last_seen')[:10] 
    }
    return render(request, 'dashboard/admin_dashboard.html', context)


@login_required
def worker_dashboard(request):
    """The terminal dashboard workspace view for workers."""
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
    """Directory panel for administrative overview of existing workers."""
    if not request.user.is_superuser: 
        return redirect('dashboard:worker_dashboard')
    
    workers = User.objects.exclude(is_superuser=True).prefetch_related('worker_profile')
    return render(request, 'dashboard/manage_workers.html', {
        'forum_name': FORUM_BRANDING, 
        'workers': workers
    })


@login_required
def manage_worker_action(request, user_id, action):
    """Executes state parameters adjustments (Suspend, Block, Passwords resets)."""
    if not request.user.is_superuser: 
        return redirect('dashboard:worker_dashboard')
        
    target_user = get_object_or_404(User, id=user_id)
    profile, created = WorkerProfile.objects.get_or_create(user=target_user)
    
    if action == 'suspend':
        profile.is_suspended = not profile.is_suspended
        profile.save()
        status = "suspended" if profile.is_suspended else "reactivated"
        messages.success(request, f"Unit {target_user.username} has been {status}.")
        
    elif action == 'block':
        profile.is_blocked = not profile.is_blocked
        profile.save()
        status = "blocked" if profile.is_blocked else "unblocked"
        messages.success(request, f"Unit {target_user.username} has been {status}.")
        
    elif action == 'reset_pwd':
        new_password = 'DivineUnit2026!'
        target_user.set_password(new_password)
        target_user.save()
        messages.success(request, f"Password for {target_user.username} reset to: {new_password}")
        
    return redirect('dashboard:manage_workers')


@login_required
def edit_worker_profile(request, user_id):
    """Allows administrators or individual users to edit custom configurations."""
    if not request.user.is_superuser and request.user.id != user_id:
        return redirect('dashboard:worker_dashboard')
        
    worker = get_object_or_404(User, id=user_id)
    profile, created = WorkerProfile.objects.get_or_create(user=worker)
    
    if request.method == 'POST':
        access_level = request.POST.get('access_level')
        if access_level and request.user.is_superuser:
            profile.access_level = access_level
            profile.save()
            messages.success(request, f"Parameters modified for unit {worker.username}.")
        return redirect('dashboard:admin_dashboard' if request.user.is_superuser else 'dashboard:worker_dashboard')
        
    return render(request, 'dashboard/edit_worker_profile.html', {
        'worker': worker,
        'forum_name': FORUM_BRANDING
    })


@login_required
def create_task(request):
    """Enables administrators to assign discrete execution pieces to active accounts."""
    if not request.user.is_superuser: 
        return redirect('dashboard:worker_dashboard')
        
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
    """Returns task structural rows allocated to the requesting user profile."""
    return render(request, 'dashboard/task_list.html', {
        'tasks': Task.objects.filter(assigned_to=request.user).order_by('-created_at'),
        'forum_name': FORUM_BRANDING
    })


@login_required
def submit_task(request, task_id):
    """Pushes a completion record and content up for administrator evaluation reviews."""
    task = get_object_or_404(Task, id=task_id)
    if request.method == 'POST':
        content = request.POST.get('content')
        WorkSubmission.objects.create(
            worker=request.user,
            task=task,
            content=content,
            is_reviewed=False
        )
        task.status = 'Submitted'
        task.save()
        
        messages.success(request, f"Work submitted for: {task.title}")
        return redirect('dashboard:worker_dashboard')
        
    return render(request, 'dashboard/submit_task.html', {'task': task, 'forum_name': FORUM_BRANDING})


# ==========================================
# 4. SUBMISSIONS LOGISTICS
# ==========================================

@login_required
def submissions_dashboard(request):
    """Central structural auditing center for submitted items evaluation metrics."""
    if not request.user.is_superuser:
        return redirect('dashboard:worker_dashboard')
        
    context = {
        'forum_name': FORUM_BRANDING,
        'submissions': WorkSubmission.objects.all().order_by('-submitted_at'),
        'pending_count': WorkSubmission.objects.filter(is_reviewed=False).count(),
        'reviewed_count': WorkSubmission.objects.filter(is_reviewed=True).count(),
        'avg_ai_score': WorkSubmission.objects.filter(ai_score__isnull=False).aggregate(Avg('ai_score'))['ai_score__avg']
    }
    return render(request, 'dashboard/submissions_dashboard.html', context)


# ==========================================
# 5. CONSOLIDATED MESSAGING & LIVE WORKSPACE (SPA)
# ==========================================

@login_required
def message_center(request):
    """
    Core interface presenting available contact maps. Defaults natively 
    to the Shared Global Network Room mapping all active units.
    """
    available_contacts = User.objects.exclude(id=request.user.id)
    
    # Fetch existing global communications records (receiver is null)
    global_messages = ChatMessage.objects.filter(receiver__isnull=True).order_by('timestamp')
    
    return render(request, 'dashboard/message_center.html', {
        'contacts': available_contacts,
        'messages': global_messages,       # Injected history context
        'forum_name': FORUM_BRANDING,
        'target_worker': None,            # Signifies Global Comms Room active
        'room_name': "sync_global_channel" 
    })


@login_required
def message_center_with_worker(request, worker_id):
    """
    Unified Single Page View tracking active text streams while serving dynamic 
    room hashes for instant P2P audio/video/canvas integrations.
    """
    target_worker = get_object_or_404(User, id=worker_id)
    available_contacts = User.objects.exclude(id=request.user.id)
    
    chat_messages = ChatMessage.objects.filter(
        (Q(sender=request.user) & Q(receiver=target_worker)) |
        (Q(sender=target_worker) & Q(receiver=request.user))
    ).order_by('timestamp')
    
    sorted_ids = sorted([request.user.id, target_worker.id])
    computed_room_name = f"sync_{sorted_ids[0]}_{sorted_ids[1]}"
    
    return render(request, 'dashboard/message_center.html', {
        'contacts': available_contacts,
        'target_worker': target_worker, 
        'messages': chat_messages, 
        'forum_name': FORUM_BRANDING,
        'room_name': computed_room_name
    })


@login_required
def send_message(request, user_id):
    """Async engine pipeline receiving message elements payloads via JSON requests."""
    if request.method == 'POST':
        content_text = request.POST.get('content')
        
        if int(user_id) == 0:
            ChatMessage.objects.create(
                sender=request.user,
                receiver=None,  
                content=content_text
            )
        else:
            ChatMessage.objects.create(
                sender=request.user, 
                receiver=get_object_or_404(User, id=user_id), 
                content=content_text
            )
        return JsonResponse({'status': 'success'})
    return JsonResponse({'status': 'error'}, status=400)


@login_required
def fetch_messages(request, user_id):
    """Poll endpoint fetching update packages during direct client chat conversations."""
    if int(user_id) == 0:
        messages_data = ChatMessage.objects.filter(
            receiver__isnull=True
        ).order_by('timestamp').values('sender__username', 'content', 'timestamp')
    else:
        target_user = get_object_or_404(User, id=user_id)
        messages_data = ChatMessage.objects.filter(
            (Q(sender=request.user) & Q(receiver=target_user)) |
            (Q(sender=target_user) & Q(receiver=request.user))
        ).order_by('timestamp').values('sender__username', 'content', 'timestamp')
        
    return JsonResponse(list(messages_data), safe=False)

# ==========================================
# 6. ANNOUNCEMENTS & DISCRETE BUFFER FEEDBACK
# ==========================================

@login_required
def manage_announcements(request):
    """Allows administrators to send global announcements out onto system hubs."""
    if request.method == 'POST':
        SystemBroadcast.objects.create(
            title=request.POST.get('title'),
            message=request.POST.get('message') 
        )
        messages.success(request, "Broadcast successfully deployed.")
        return redirect('dashboard:manage_announcements')
    
    context = {
        'forum_name': FORUM_BRANDING,
        'announcements': SystemBroadcast.objects.all().order_by('-created_at')
    }
    return render(request, 'dashboard/announcements.html', context)


@login_required
def suggestion_box(request):
    """Anonymous/Private pipeline collection terminal for user base suggestions feedback."""
    if request.method == 'POST':
        content = request.POST.get('content')
        title = request.POST.get('title', 'Feedback Record')
        if content:
            Suggestion.objects.create(user=request.user, title=title, content=content)
        messages.success(request, "Your suggestion has been received.")
        return redirect('dashboard:worker_dashboard')

    all_suggestions = Suggestion.objects.all().order_by('-created_at')
    return render(request, 'dashboard/suggestion_box.html', {
        'forum_name': FORUM_BRANDING,
        'suggestions': all_suggestions
    })


# ==========================================
# 7. METRICS & STRUCTURAL UTILITIES
# ==========================================

@login_required
def profile_view(request): 
    return render(request, 'dashboard/profile.html', {'forum_name': FORUM_BRANDING})


@login_required
def settings_view(request): 
    return render(request, 'dashboard/settings.html', {'forum_name': FORUM_BRANDING})


@login_required
def leaderboard_view(request): 
    return render(request, 'dashboard/leaderboard.html', {'forum_name': FORUM_BRANDING})


@login_required 
def check_efficiency_api(request):
    """API endpoint providing async system metric verification updates."""
    metrics, _ = PerformanceMetric.objects.get_or_create(worker=request.user)
    return JsonResponse({'score': metrics.score})
@login_required
def fetch_messages(request, user_id):
    # If Global (0), filter where receiver is None
    if int(user_id) == 0:
        messages = ChatMessage.objects.filter(receiver__isnull=True).order_by('timestamp')
    else:
        target_user = get_object_or_404(User, id=user_id)
        messages = ChatMessage.objects.filter(
            (Q(sender=request.user) & Q(receiver=target_user)) |
            (Q(sender=target_user) & Q(receiver=request.user))
        ).order_by('timestamp')

    # Force a list of dicts with clear mapping
    data = [{
        'sender__username': m.sender.username,
        'content': m.content,
        'timestamp': m.timestamp.isoformat()
    } for m in messages]
    
    return JsonResponse(data, safe=False)
