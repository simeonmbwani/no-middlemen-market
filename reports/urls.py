from django.urls import path
from . import views

app_name = 'reports'

urlpatterns = [
    # 🔧 FIXED: Cleaned up paths duplication and added proper closing array metrics
    path('listing/<int:listing_id>/report/', views.report_listing_view, name='report_listing'),
    path('listing/<int:listing_id>/flag/', views.report_listing_view, name='flag'), # Secondary alternate path anchor alias
]