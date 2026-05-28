from django.urls import path
from . import views

app_name = 'dashboard'

urlpatterns = [
    # --- Authentication ---
    path('auth/', views.auth_view, name='auth'),

    # --- Dashboards ---
    path('admin-dashboard/', views.admin_dashboard, name='admin_dashboard'),
    path('worker-dashboard/', views.worker_dashboard, name='worker_dashboard'),
    
    # --- Worker Management ---
    path('manage-workers/', views.manage_workers, name='manage_workers'),
    path('manage-worker/<int:user_id>/<str:action>/', views.manage_worker_action, name='manage_worker'),
    path('worker/edit/<int:user_id>/', views.edit_worker_profile, name='edit_worker_profile'),

    # --- Task Management ---
    path('create-task/', views.create_task, name='create_task'),
    path('task-list/', views.task_list, name='task_list'),
    path('submit-task/<int:task_id>/', views.submit_task, name='submit_task'),
    
    # --- Performance & Metrics ---
    # Added this line to fix the NoReverseMatch error!
    path('check-efficiency/', views.check_efficiency_api, name='check_efficiency'),
    
    # --- Communications & Suggestions ---
    path('suggestion-box/', views.suggestion_box, name='suggestion_box'),
    path('message-center/', views.message_center, name='message_center'),
    path('message-center/<int:worker_id>/', views.message_center_with_worker, name='message_center_with_worker'),
    
    # --- API Endpoints ---
    path('api/messages/fetch/<int:user_id>/', views.fetch_messages, name='fetch_messages'),
    path('api/messages/send/<int:user_id>/', views.send_message, name='send_message'),
    
    # --- Live & Extras ---
    path('live-communications/<str:room_name>/', views.live_communications, name='live_communications'),
    path('manage-announcements/', views.manage_announcements, name='manage_announcements'),
]
# urls.py
from django.urls import path
from . import views

urlpatterns = [
    # ... your other urls ...
    path('dashboard/live-room/', views.live_communication_view, name='live_room'),
]