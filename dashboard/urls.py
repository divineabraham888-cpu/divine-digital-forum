from django.urls import path
from . import views

urlpatterns = [
    # --- DASHBOARDS ---
    path('', views.admin_dashboard, name='admin_dashboard'),
    path('worker/', views.worker_dashboard, name='worker_dashboard'),

    # --- TASK ACTIONS ---
    path('task/create/', views.create_task, name='create_task'),
    path('task/complete/<int:task_id>/', views.complete_task, name='complete_task'),
    path('task/reassign/<int:task_id>/', views.reassign_task, name='reassign_task'),

    # --- WORKER MANAGEMENT ---
    path('workers/', views.manage_workers, name='manage_workers'),
    path('workers/edit/<int:worker_id>/', views.edit_worker, name='edit_worker'),

    # --- SUBMISSIONS ---
    path('submissions/', views.submission_view, name='submission_view'),
    path('submissions/score/<int:sub_id>/', views.update_score, name='update_score'),

    # --- ANNOUNCEMENTS & TIMETABLE ---
    path('announcements/', views.manage_announcements, name='manage_announcements'),
    path('announcements/add/', views.add_announcement, name='add_announcement'),
    path('timetable/add/', views.add_timetable_event, name='add_timetable_event'),

    # --- COMMUNICATIONS ---
    path('messages/send/', views.send_message_to_worker, name='send_message_to_worker'),
    path('messages/', views.message_center, name='message_center'),
    path('messages/chat/<int:worker_id>/', views.message_center, name='message_center_with_worker'),
    path('messages/private/<int:worker_id>/', views.send_private_message, name='send_private_message'),
]