"""
URL configuration for config project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/6.0/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from django.views.generic import TemplateView
from accounts import views as account_views

urlpatterns = [
    # 👑 1. Your Custom ERP Hub remains the primary entry point for /admin/
    path('admin/', account_views.erp_control_center_view, name='erp_control_center'),
    
    # 🛡️ 2. KEEP NATIVE DJANGO ADMIN SAFE (Under a new name so namespaces don't break!)
    path('admin-core/', admin.site.urls), 
    
    # 🛒 Rest of your operational apps
    path('', include('listings.urls', namespace='listings')),
    path('reports/', include('reports.urls', namespace='reports')),
    path('messages/', include('messaging.urls', namespace='messaging')),
    path('payments/', include('payments.urls', namespace='payments')),
    path('dashboard/', include('dashboard.urls', namespace='dashboard')),
    path('accounts/', include('accounts.urls', namespace='accounts')),
    
    path('manifest.json', TemplateView.as_view(template_name='manifest.json', content_type='application/json')),
    path('service-worker.js', TemplateView.as_view(template_name='service-worker.js', content_type='application/javascript')),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)