from django.urls import path
from . import views

app_name = 'listings'

urlpatterns = [
    path('', views.listing_list_view, name='list'),
    path('asset/<int:listing_id>/', views.listing_detail_view, name='detail'),
    path('asset/create/', views.listing_create_view, name='create'),
    path('set-language/', views.set_language_view, name='set_language'),
    path('asset/<int:listing_id>/edit/', views.edit_listing_view, name='edit_listing'),
    path('asset/<int:listing_id>/delete/', views.delete_listing_view, name='delete_listing'),
]