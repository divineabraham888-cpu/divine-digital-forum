from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import get_user_model
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib import messages
from django.db.models import Q
from .models import Task, ActivityLog, Message, Announcement, TimetableEvent, WorkerSubmission
from .forms import SubmissionForm

User = get_user_model()

# --- DASHBOARDS ---
@user_passes_test(lambda u: u.is_staff)
def admin_dashboard(request):
    tasks = Task.objects.all()
    workers = User.objects.all()
    recent_logs = ActivityLog.objects.all().order_by('-timestamp')[:10]
    submissions = WorkerSubmission.objects.all()
    context = {
        'all_tasks': tasks, 'all_workers': workers, 'recent_logs': recent_logs, 
        'submissions': submissions, 'total_tasks': tasks.count(),
        'pending_tasks': tasks.filter(status='Pending').count(),
        'completed_tasks': tasks.filter(status='Completed').count(),
    }
    return render(request, 'dashboard/admin_dashboard.html', context)

@login_required
def worker_dashboard(request):
    tasks = Task.objects.filter(assigned_to=request.user)
    return render(request, 'dashboard/worker_dashboard.html', {'tasks': tasks})

# --- TASK ACTIONS ---
@login_required
def complete_task(request, task_id):
    task = get_object_or_404(Task, id=task_id)
    if request.user == task.assigned_to or request.user.is_staff:
        task.status = 'Completed'
        task.save()
        ActivityLog.objects.create(user=request.user, action=f"Completed task: {task.title}")
    return redirect('worker_dashboard')

@user_passes_test(lambda u: u.is_staff)
def reassign_task(request, task_id):
    if request.method == 'POST':
        task = get_object_or_404(Task, id=task_id)
        new_worker = get_object_or_404(User, id=request.POST.get('new_worker'))
        task.assigned_to = new_worker
        task.save()
        ActivityLog.objects.create(user=request.user, action=f"Reassigned {task.title} to {new_worker.username}")
    return redirect('admin_dashboard')

@user_passes_test(lambda u: u.is_staff)
def create_task(request):
    if request.method == 'POST':
        title = request.POST.get('title')
        worker = get_object_or_404(User, id=request.POST.get('assigned_to'))
        Task.objects.create(title=title, assigned_to=worker, status='Pending')
        ActivityLog.objects.create(user=request.user, action=f"Created task: {title}")
        return redirect('admin_dashboard')
    workers = User.objects.filter(is_staff=False)
    return render(request, 'dashboard/create_task.html', {'all_workers': workers})

# --- WORKER MANAGEMENT ---
@user_passes_test(lambda u: u.is_staff)
def manage_workers(request):
    return render(request, 'dashboard/manage_workers.html', {'workers': User.objects.all()})

@user_passes_test(lambda u: u.is_staff)
def edit_worker(request, worker_id):
    if request.method == 'POST':
        worker = get_object_or_404(User, id=worker_id)
        worker.username = request.POST.get('username', worker.username)
        worker.email = request.POST.get('email', worker.email)
        if request.POST.get('password'): worker.set_password(request.POST.get('password'))
        worker.save()
        ActivityLog.objects.create(user=request.user, action=f"Updated: {worker.username}")
    return redirect('manage_workers')

# --- SUBMISSIONS ---
@login_required
def submission_view(request):
    if request.method == 'POST':
        form = SubmissionForm(request.POST, request.FILES)
        if form.is_valid():
            sub = form.save(commit=False)
            sub.worker = request.user
            sub.save()
            return redirect('worker_dashboard')
    else: form = SubmissionForm()
    return render(request, 'dashboard/submissions.html', {'form': form})

@user_passes_test(lambda u: u.is_staff)
def update_score(request, sub_id):
    if request.method == 'POST':
        sub = get_object_or_404(WorkerSubmission, id=sub_id)
        sub.score = request.POST.get('score')
        sub.save()
    return redirect('admin_dashboard')

# --- ANNOUNCEMENTS & TIMETABLE ---
@user_passes_test(lambda u: u.is_staff)
def manage_announcements(request):
    return render(request, 'dashboard/announcements.html', {
        'announcements': Announcement.objects.all().order_by('-date_posted'),
        'timetable_events': TimetableEvent.objects.all().order_by('event_date', 'event_time')
    })

@user_passes_test(lambda u: u.is_staff)
def add_announcement(request):
    if request.method == 'POST':
        Announcement.objects.create(
            title=request.POST.get('title'),
            message=request.POST.get('message'),
            priority=request.POST.get('priority'),
            posted_by=request.user
        )
    return redirect('manage_announcements')

@user_passes_test(lambda u: u.is_staff)
def add_timetable_event(request):
    if request.method == 'POST':
        TimetableEvent.objects.create(
            event_name=request.POST.get('title'),
            description=request.POST.get('description'),
            event_date=request.POST.get('event_date'),
            event_time=request.POST.get('event_time')
        )
    return redirect('manage_announcements')

# --- COMMUNICATIONS ---
@user_passes_test(lambda u: u.is_staff)
def send_message_to_worker(request):
    if request.method == 'POST':
        worker = get_object_or_404(User, id=request.POST.get('worker_id'))
        Message.objects.create(sender=request.user, receiver=worker, content=request.POST.get('content'))
        ActivityLog.objects.create(user=request.user, action=f"Sent message to {worker.username}")
    return redirect('admin_dashboard')

@user_passes_test(lambda u: u.is_staff)
def message_center(request, worker_id=None):
    workers = User.objects.filter(is_staff=False)
    selected_worker = get_object_or_404(User, id=worker_id) if worker_id else None
    messages_list = None
    if selected_worker:
        messages_list = Message.objects.filter(
            (Q(sender=request.user) & Q(receiver=selected_worker)) |
            (Q(sender=selected_worker) & Q(receiver=request.user))
        ).order_by('timestamp')
    return render(request, 'dashboard/communications.html', {'workers': workers, 'selected_worker': selected_worker, 'chat_messages': messages_list})

@user_passes_test(lambda u: u.is_staff)
def send_private_message(request, worker_id):
    if request.method == 'POST':
        content = request.POST.get('content')
        receiver = get_object_or_404(User, id=worker_id)
        Message.objects.create(sender=request.user, receiver=receiver, content=content)
        ActivityLog.objects.create(user=request.user, action=f"Sent private message to {receiver.username}")
    return redirect('message_center', worker_id=worker_id)