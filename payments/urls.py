from django.urls import path
from . import views

app_name = 'payments'

urlpatterns = [
    path('checkout/<int:listing_id>/', views.checkout_view, name='checkout'),
    path('verify/<int:payment_id>/', views.verify_payment_view, name='verify'),
    path('issue/<int:listing_id>/', views.create_invoice_view, name='create_invoice'),
    path('release/<int:invoice_id>/', views.release_escrow_view, name='release_escrow'),
    path('invoice/<int:invoice_id>/secure/', views.secure_payment_view, name='secure_payment'),
    path('invoice/<int:invoice_id>/release/', views.release_escrow_view, name='release_escrow'),
]