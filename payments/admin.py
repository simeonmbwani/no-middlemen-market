from django.contrib import admin
from .models import Payment

@admin.register(Payment)
class PaymentAdmin(admin.ModelAdmin):
    list_display = ['reference', 'listing', 'owner', 'amount', 'gateway', 'status', 'created_at']
    list_filter = ['status', 'gateway', 'created_at']
    search_fields = ['reference', 'owner__username', 'listing__title']
