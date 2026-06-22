from django.urls import path
from django.contrib.auth import views as auth_views
from . import views

app_name = 'accounts'

urlpatterns = [
    # 🔐 Authentication Gates (Using your custom view to handle smart admin routing)
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
    path('register/', views.register_view, name='register'),
    
    # 👤 KYC Profile Verification & Localized Settings
    path('verify-identity/', views.upload_national_id_view, name='verify_identity'),
    path('dashboard/compliance/', views.compliance_dashboard_view, name='compliance_dashboard'),
    path('terms-and-faq/', views.terms_faq_view, name='terms_faq'),
    path('settings/', views.settings_dashboard_view, name='settings_dashboard'),
    
    # 👑 ERP Core Control Center Modules
    path('dashboard/control-center/', views.erp_control_center_view, name='erp_control_center'),
    
    # 👥 MODULE 1: Live User Management Core URL Route Configuration
    path('admin/users/', views.erp_user_management_view, name='erp_user_management'),

    # 🔄 Secure Key & Password Reset Protocols
    path('password-change/', auth_views.PasswordChangeView.as_view(template_name='accounts/password_change.html'), name='password_change'),
    path('password-reset/', 
         auth_views.PasswordResetView.as_view(template_name='accounts/password_reset_form.html', email_template_name='accounts/password_reset_email.html', success_url='/accounts/password-reset/done/'), 
         name='password_reset'),
    path('password-reset/done/', 
         auth_views.PasswordResetDoneView.as_view(template_name='accounts/password_reset_done.html'), 
         name='password_reset_done'),
    path('password-reset-confirm/<uidb64>/<token>/', 
         auth_views.PasswordResetConfirmView.as_view(template_name='accounts/password_reset_confirm.html', success_url='/accounts/password-reset/complete/'), 
         name='password_reset_confirm'),
    path('password-reset/complete/', 
         auth_views.PasswordResetCompleteView.as_view(template_name='accounts/password_reset_complete.html'), 
         name='password_reset_complete'),
    # ... your existing login, register, and control-center paths ...
    path('admin/users/', views.erp_user_management_view, name='erp_user_management'),
    
    # 👑 THE COMPLETELY WIRED MULTI-MODULE URL SCHEME
    path('admin/assets/', views.erp_asset_catalog_view, name='erp_asset_catalog'),
    path('admin/chats/', views.erp_chat_monitor_view, name='erp_chat_monitor'),
    path('admin/payments-core/', views.erp_payment_center_view, name='erp_payment_center'),
    path('admin/red-flags/', views.erp_red_flags_view, name='erp_red_flags'),
    path('admin/violations/', views.erp_violations_hub_view, name='erp_violations_hub'),
    path('admin/suspensions/', views.erp_suspensions_view, name='erp_suspensions'),
    path('admin/blocked-matrix/', views.erp_blocked_matrix_view, name='erp_blocked_matrix'),
    path('admin/archive/', views.erp_records_archive_view, name='erp_records_archive'),
    path('admin/categories/', views.erp_categories_view, name='erp_categories'),
    path('admin/search-analytics/', views.erp_search_analytics_view, name='erp_search_analytics'),
    path('admin/reviews/', views.erp_review_logs_view, name='erp_review_logs'),
    path('admin/alerts/', views.erp_system_alerts_view, name='erp_system_alerts'),
    path('admin/audit-logs/', views.erp_immutable_audit_view, name='erp_immutable_audit'),
    path('admin/geo-stats/', views.erp_geo_statistics_view, name='erp_geo_statistics'),
    path('admin/support-tickets/', views.erp_support_tickets_view, name='erp_support_tickets'),
    path('admin/disaster-recovery/', views.erp_disaster_recovery_view, name='erp_disaster_recovery'),
    path('admin/global-settings/', views.erp_global_settings_view, name='erp_global_settings'),
    path('admin/exports/', views.erp_export_engines_view, name='erp_export_engines'),
    path('admin/super-root/', views.erp_super_admin_view, name='erp_super_admin'),
]
