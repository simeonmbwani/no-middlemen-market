from django.contrib import admin
from .models import Listing

@admin.register(Listing)
class ListingAdmin(admin.ModelAdmin):
    list_display = ['title', 'owner', 'category', 'price', 'province', 'district', 'is_paid', 'is_active']
    list_filter = ['category', 'province', 'is_paid', 'is_active', 'created_at']
    search_fields = ['title', 'description', 'district', 'owner__username', 'owner__phone_number']
    actions = ['approve_listings', 'reject_listings']

    def approve_listings(self, request, queryset):
        queryset.update(is_active=True)
    approve_listings.short_description = "Approve selected listings for publication"

    def reject_listings(self, request, queryset):
        queryset.update(is_active=False)
    reject_listings.short_description = "Take selected listings offline"
