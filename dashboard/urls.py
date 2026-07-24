from django.urls import path

from . import views

app_name = 'dashboard'

urlpatterns = [
    path('', views.dashboard_home, name='home'),
    path('users/', views.user_list, name='users'),
    path('users/<int:user_id>/toggle-status/', views.toggle_user_status, name='toggle_user_status'),
    path('users/<int:user_id>/toggle-verification/', views.toggle_user_verification, name='toggle_user_verification'),
    path('profiles/', views.profile_list, name='profiles'),
    path('profiles/<int:profile_id>/toggle-approval/', views.toggle_profile_approval, name='toggle_profile_approval'),
    path('profiles/<int:profile_id>/toggle-visibility/', views.toggle_profile_visibility, name='toggle_profile_visibility'),
    path('reports/', views.report_list, name='reports'),
    path('reports/<int:report_id>/status/<str:status>/', views.update_report_status, name='update_report_status'),
    path('subscriptions/plans/', views.plan_list, name='plans'),
    path('subscriptions/plans/create/', views.plan_form, name='plan_create'),
    path('subscriptions/plans/<int:plan_id>/edit/', views.plan_form, name='plan_edit'),
    path('subscriptions/plans/<int:plan_id>/toggle-status/', views.toggle_plan_status, name='toggle_plan_status'),
    path('chats/', views.chat_management, name='chats'),
    path('chats/messages/<int:message_id>/clear-report/', views.clear_message_report, name='clear_message_report'),
    path('settings/', views.dashboard_settings, name='settings'),
    path('notifications/', views.notification_list, name='notifications'),
    path('notifications/create/', views.notification_create, name='notification_create'),
    path('matches/', views.match_list, name='matches'),
    path('login/', views.dashboard_login, name='login'),
    path('logout/', views.dashboard_logout, name='logout'),
]
