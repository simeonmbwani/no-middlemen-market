from django.urls import path
from django.contrib.auth import views as auth_views
from . import views

app_name = 'accounts'

urlpatterns = [
    path('login/', auth_views.LoginView.as_view(template_name='accounts/login.html'), name='login'),
    path('logout/', auth_views.LogoutView.as_view(), name='logout'),
    path('register/', views.register_view, name='register'),
    path('verify-identity/', views.upload_national_id_view, name='verify_identity'),
    path('dashboard/compliance/', views.compliance_dashboard_view, name='compliance_dashboard'),
    path('terms-and-faq/', views.terms_faq_view, name='terms_faq'),
    path('settings/', views.settings_dashboard_view, name='settings_dashboard'),
    path('password-change/', auth_views.PasswordChangeView.as_view(template_name='accounts/password_change.html'), name='password_change'),

    # 🔧 FIXED: These paths must be explicitly saved here to clear the 'password_reset not found' error!
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