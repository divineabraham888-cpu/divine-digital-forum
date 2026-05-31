from django.urls import path
from . import views

app_name = 'dashboard'

urlpatterns = [
    # --- Video Call ---
    path('call/<str:room_name>/', views.video_call_room, name='video_call'),

    # --- Authentication ---
    path('login/', views.auth, name='auth'),

    # --- Dashboards ---
    path('admin-dashboard/', views.admin_dashboard, name='admin_dashboard'),
    path('worker-dashboard/', views.worker_dashboard, name='worker_dashboard'),
    path('submissions-dashboard/', views.submissions_dashboard, name='submissions_dashboard'),
    
    # --- Worker Management ---
    path('manage-workers/', views.manage_workers, name='manage_workers'),
    path('manage-worker/<int:user_id>/<str:action>/', views.manage_worker_action, name='manage_worker'),
    path('worker/edit/<int:user_id>/', views.edit_worker_profile, name='edit_worker_profile'),

    # --- Task Management ---
    path('create-task/', views.create_task, name='create_task'),
    path('task-list/', views.task_list, name='task_list'),
    path('submit-task/<int:task_id>/', views.submit_task, name='submit_task'),
    
    # --- Performance & Metrics ---
    path('check-efficiency/', views.check_efficiency_api, name='check_efficiency'),
    
    # --- Communications ---
    path('suggestion-box/', views.suggestion_box, name='suggestion_box'),
    path('manage-announcements/', views.manage_announcements, name='manage_announcements'),
    path('message-center/', views.message_center_view, name='old_message_center'),
    path('message-center/<int:worker_id>/', views.message_center_with_worker, name='message_center_with_worker'),
    
    # --- Async API Endpoints ---
    path('api/messages/fetch/<int:user_id>/', views.fetch_messages, name='fetch_messages'),
    path('api/messages/send/<int:user_id>/', views.send_message, name='send_message'),

    # --- Structural Interface Views ---
    path('profile/', views.profile_view, name='profile_view'),
    path('settings/', views.settings_view, name='settings_view'),
    path('leaderboard/', views.leaderboard_view, name='leaderboard_view'),
    
    # --- Modern Views ---
    path('p2p/', views.p2p_view, name='p2p_hub'),
    path('messages/', views.message_center_view, name='message_center'),
    path('general-hub/', views.general_hub_view, name='general_hub'),
]