from django.urls import path
from . import views

app_name = "dashboard"

urlpatterns = [

    # =========================
    # DASHBOARDS
    # =========================
    path(
        "admin-dashboard/",
        views.admin_dashboard,
        name="admin_dashboard"
    ),

    path(
        "worker-dashboard/",
        views.worker_dashboard,
        name="worker_dashboard"
    ),

    # =========================
    # TASKS
    # =========================
    path(
        "create-task/",
        views.create_task,
        name="create_task"
    ),

    path(
        "complete-task/<int:task_id>/",
        views.complete_task,
        name="complete_task"
    ),

    path(
        "reassign-task/<int:task_id>/",
        views.reassign_task,
        name="reassign_task"
    ),

    # =========================
    # WORKERS
    # =========================
    path(
        "manage-workers/",
        views.manage_workers,
        name="manage_workers"
    ),

    path(
        "edit-worker/<int:worker_id>/",
        views.edit_worker,
        name="edit_worker"
    ),

    path(
        "delete-worker/<int:worker_id>/",
        views.delete_worker,
        name="delete_worker"
    ),

    # =========================
    # SUBMISSIONS
    # =========================
    path(
        "submissions/",
        views.submissions_dashboard,
        name="submissions_dashboard"
    ),

    # =========================
    # ANNOUNCEMENTS
    # =========================
    path(
        "announcements/",
        views.manage_announcements,
        name="manage_announcements"
    ),

    path(
        "add-announcement/",
        views.add_announcement,
        name="add_announcement"
    ),

    # =========================
    # TIMETABLE
    # =========================
    path(
        "add-timetable-event/",
        views.add_timetable_event,
        name="add_timetable_event"
    ),

    # =========================
    # MESSAGES
    # =========================
    path(
        "messages/",
        views.message_center,
        name="message_center"
    ),

    path(
        "send-message/",
        views.send_message_to_worker,
        name="send_message_to_worker"
    ),

    path(
        "private-message/<int:worker_id>/",
        views.send_private_message,
        name="send_private_message"
    ),

    # =========================
    # SUGGESTIONS
    # =========================
    path(
        "suggestions/",
        views.suggestion_box,
        name="suggestion_box"
    ),

    # =========================
    # REPORTS
    # =========================
    path(
        "reports/",
        views.reports_analytics,
        name="reports_analytics"
    ),

    # =========================
    # PAYMENTS
    # =========================
    path(
        "payments/",
        views.payment_management,
        name="payment_management"
    ),

    # =========================
    # SETTINGS
    # =========================
    path(
        "settings/",
        views.settings_page,
        name="settings_page"
    ),

]