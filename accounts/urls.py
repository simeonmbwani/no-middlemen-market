from django.urls import path
from django.contrib.auth import views as auth_views
from . import views

app_name = 'accounts'

urlpatterns = [
    # 🔑 Using Django's built-in secure login view wrapper
    path('login/', auth_views.LoginView.as_view(template_name='accounts/login.html'), name='login'),
    # 🚪 Logout handler
    path('logout/', auth_views.LogoutView.as_view(next_page='listings:list'), name='logout'),
    # 📝 Custom User/Owner Registration path
    path('register/', views.register_view, name='register'),
    path('verify-identity/', views.upload_national_id_view, name='verify_identity'),
    path('dashboard/compliance/', views.compliance_dashboard_view, name='compliance_dashboard'),

]