from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import get_user_model
from django.contrib.auth.decorators import login_required, user_passes_test
from django.http import HttpResponse

from .models import (
    Task,
    ActivityLog,
    Message,
    Submission,
    Announcement,
    TimetableEvent
)

User = get_user_model()


# =========================
# CHECK STAFF USER
# =========================
def is_staff_member(user):
    return user.is_staff


# =========================
# ADMIN DASHBOARD
# =========================
@login_required
@user_passes_test(is_staff_member)
def admin_dashboard(request):

    tasks = Task.objects.all()

    context = {
        'all_tasks': tasks,
        'all_workers': User.objects.filter(is_staff=False),
        'recent_logs': ActivityLog.objects.all().order_by('-timestamp')[:10],
        'submissions': Submission.objects.all(),
        'total_tasks': tasks.count(),
        'pending_tasks': tasks.filter(status='Pending').count(),
        'completed_tasks': tasks.filter(status='Completed').count(),
    }

    return render(
        request,
        'dashboard/admin_dashboard.html',
        context
    )


# =========================
# WORKER DASHBOARD
# =========================
@login_required
def worker_dashboard(request):

    tasks = Task.objects.filter(
        assigned_to=request.user
    )

    return render(
        request,
        'dashboard/worker_dashboard.html',
        {'tasks': tasks}
    )


# =========================
# MANAGE WORKERS
# =========================
@login_required
@user_passes_test(is_staff_member)
def manage_workers(request):

    workers = User.objects.filter(is_staff=False)

    context = {
        "workers": workers
    }

    return render(
        request,
        "dashboard/manage_workers.html",
        context
    )


# =========================
# DELETE WORKER
# =========================
@login_required
@user_passes_test(is_staff_member)
def delete_worker(request, worker_id):

    worker = get_object_or_404(
        User,
        id=worker_id
    )

    worker.delete()

    return redirect(
        "dashboard:manage_workers"
    )


# =========================
# EDIT WORKER
# =========================
@login_required
@user_passes_test(is_staff_member)
def edit_worker(request, worker_id):

    worker = get_object_or_404(
        User,
        id=worker_id
    )

    context = {
        'worker': worker
    }

    return render(
        request,
        'dashboard/worker_form.html',
        context
    )


# =========================
# SUBMISSIONS DASHBOARD
# =========================
@login_required
@user_passes_test(is_staff_member)
def submissions_dashboard(request):

    submissions = Submission.objects.all()

    context = {
        'submissions': submissions
    }

    return render(
        request,
        'dashboard/submissions_dashboard.html',
        context
    )


# =========================
# MANAGE ANNOUNCEMENTS
# =========================
@login_required
@user_passes_test(is_staff_member)
def manage_announcements(request):

    announcements = Announcement.objects.all()

    context = {
        'announcements': announcements
    }

    return render(
        request,
        'dashboard/manage_announcements.html',
        context
    )


# =========================
# MESSAGE CENTER
# =========================
@login_required
def message_center(request):

    messages = Message.objects.all()

    context = {
        'messages': messages
    }

    return render(
        request,
        'dashboard/message_center.html',
        context
    )


# =========================
# SUGGESTION BOX
# =========================
@login_required
def suggestion_box(request):

    return render(
        request,
        'dashboard/suggestion_box.html'
    )


# =========================
# CREATE TASK
# =========================
@login_required
@user_passes_test(is_staff_member)
def create_task(request):

    if request.method == "POST":

        title = request.POST.get("title")
        description = request.POST.get("description")
        assigned_to_id = request.POST.get("assigned_to")

        worker = User.objects.get(
            id=assigned_to_id
        )

        Task.objects.create(
            title=title,
            description=description,
            assigned_to=worker,
            status="Pending"
        )

        return redirect(
            "dashboard:admin_dashboard"
        )

    return render(
        request,
        'dashboard/task_form.html'
    )


# =========================
# COMPLETE TASK
# =========================
@login_required
def complete_task(request, task_id):

    task = get_object_or_404(
        Task,
        id=task_id
    )

    task.status = "Completed"
    task.save()

    return redirect(
        'dashboard:worker_dashboard'
    )


# =========================
# REASSIGN TASK
# =========================
@login_required
@user_passes_test(is_staff_member)
def reassign_task(request, task_id):

    task = get_object_or_404(
        Task,
        id=task_id
    )

    if request.method == "POST":

        new_worker_id = request.POST.get(
            "new_worker"
        )

        new_worker = User.objects.get(
            id=new_worker_id
        )

        task.assigned_to = new_worker
        task.save()

    return redirect(
        'dashboard:admin_dashboard'
    )


# =========================
# ADD ANNOUNCEMENT
# =========================
@login_required
@user_passes_test(is_staff_member)
def add_announcement(request):

    return render(
        request,
        'dashboard/announcement_form.html'
    )


# =========================
# ADD TIMETABLE EVENT
# =========================
@login_required
@user_passes_test(is_staff_member)
def add_timetable_event(request):

    return render(
        request,
        'dashboard/timetable_form.html'
    )


# =========================
# SEND MESSAGE
# =========================
@login_required
def send_message_to_worker(request):

    return redirect(
        'dashboard:message_center'
    )


# =========================
# PRIVATE MESSAGE
# =========================
@login_required
def send_private_message(request, worker_id):

    return redirect(
        'dashboard:message_center'
    )


# =========================
# REPORTS & ANALYTICS
# =========================
@login_required
def reports_analytics(request):

    return render(
        request,
        'dashboard/reports_analytics.html'
    )


# =========================
# PAYMENT MANAGEMENT
# =========================
@login_required
def payment_management(request):

    return render(
        request,
        'dashboard/payment_management.html'
    )


# =========================
# SETTINGS PAGE
# =========================
@login_required
def settings_page(request):

    return render(
        request,
        'dashboard/settings_page.html'
    )