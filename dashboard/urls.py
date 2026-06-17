from django.urls import path
from . import views

app_name = 'dashboard'

urlpatterns = [
    # Paths traffic to http://127.0.0.1:8000/dashboard/my-control-panel/
    path('my-control-panel/', views.user_dashboard_view, name='index'),
]