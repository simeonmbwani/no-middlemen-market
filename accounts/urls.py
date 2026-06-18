from django.urls import path
from django.contrib.auth import views as auth_views
from . import views

app_name = 'accounts'

urlpatterns = [
    # 🔑 Using Django's built-in secure login view wrapper
    path('login/', auth_views.LoginView.as_view(template_name='accounts/login.html'), name='login'),
    
    # 🚪 Logout handler (🔧 FIXED: Single, clean path mapping to Django's native authentication controller)
    path('logout/', auth_views.LogoutView.as_view(), name='logout'),
    
    # 📝 Custom User/Owner Registration path
    path('register/', views.register_view, name='register'),
    path('verify-identity/', views.upload_national_id_view, name='verify_identity'),
    
    # 🛡️ Compliance Dashboard Hub (🔧 FIXED: Resolved the dangling quotation string closure bracket error)
    path('dashboard/compliance/', views.compliance_dashboard_view, name='compliance_dashboard'),
    path('terms-and-faq/', views.terms_faq_view, name='terms_faq'),
    path('password-change/', auth_views.PasswordChangeView.as_view(template_name='accounts/password_change.html'), name='password_change'),
    path('password-change/done/', auth_views.PasswordChangeDoneView.as_view(template_name='accounts/password_change_done.html'), name='password_change_done'),
    path('settings/', views.settings_dashboard_view, name='settings_dashboard'),

]