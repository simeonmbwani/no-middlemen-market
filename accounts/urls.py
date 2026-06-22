from django.urls import path
from django.contrib.auth import views as auth_views
from . import views

app_name = 'accounts'

urlpatterns = [
    # 🔐 Authentication Gates
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
    path('register/', views.register_view, name='register'),
    
    # 👤 KYC Profile Verification & Localized Settings
    path('verify-identity/', views.upload_national_id_view, name='verify_identity'),
    path('dashboard/compliance/', views.compliance_dashboard_view, name='compliance_dashboard'),
    path('terms-and-faq/', views.terms_faq_view, name='terms_faq'),
    path('settings/', views.settings_dashboard_view, name='settings_dashboard'),
    
    # 👑 MASTER CONTROL CENTER HUB (Handles all 20 modules interactively via tab parameters)
    path('dashboard/control-center/', views.erp_control_center_view, name='erp_control_center'),

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
]
