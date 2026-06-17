from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from django.utils.timezone import now
from .models import User, NationalIDVerification

# 1. Registering the Custom User Model Admin panel interface
@admin.register(User)
class CustomUserAdmin(UserAdmin):
    """Extends Django's user admin layout to showcase marketplace parameters."""
    list_display = ('username', 'email', 'phone_number', 'national_id', 'is_verified_owner', 'strike_count', 'is_banned', 'is_staff')
    list_filter = ('is_verified_owner', 'is_banned', 'is_staff', 'is_superuser')
    
    # Expose custom registration fields in the admin edit view layout parameters
    fieldsets = UserAdmin.fieldsets + (
        ('Marketplace Accountability & Trust Tracker', {
            'fields': ('phone_number', 'national_id', 'is_verified_owner', 'strike_count', 'is_banned'),
        }),
    )
    add_fieldsets = UserAdmin.add_fieldsets + (
        ('Marketplace Accountability & Trust Tracker', {
            'fields': ('phone_number', 'national_id', 'is_verified_owner', 'strike_count', 'is_banned'),
        }),
    )


# 2. Registering the National ID Verification tracking desk matrix
@admin.register(NationalIDVerification)
class NationalIDVerificationAdmin(admin.ModelAdmin):
    list_display = ('user', 'status', 'submitted_at', 'reviewed_at')
    list_filter = ('status', 'submitted_at')
    search_fields = ('user__username', 'user__national_id')
    readonly_fields = ('submitted_at', 'reviewed_at')
    
    # Custom automated operational action overrides
    actions = ['approve_verification_action', 'reject_verification_action']

    @admin.action(description='Approve documents and verify user account profiles')
    def approve_verification_action(self, request, queryset):
        """Mass action to approve selected IDs and automatically toggle profile flags site-wide."""
        updated_count = 0
        for verification in queryset:
            if verification.status != 'approved':
                # Update the documentation ticket parameter
                verification.status = 'approved'
                verification.reviewed_at = now()
                verification.admin_notes = "Verified by Administrator."
                verification.save()
                
                # Instantly escalate changes to the profile ledger object matrix
                profile = verification.user
                profile.is_verified_owner = True
                profile.save()
                
                updated_count += 1
                
        self.message_user(
            request, 
            f"Successfully authenticated {updated_count} user documentation entries and toggled verification flags."
        )

    @admin.action(description='Reject documents and strip user verification flags')
    def reject_verification_action(self, request, queryset):
        """Mass action to reject inaccurate records or suspected middleman applications."""
        updated_count = 0
        for verification in queryset:
            verification.status = 'rejected'
            verification.reviewed_at = now()
            verification.admin_notes = "Documentation review failed. Please re-upload clear text records."
            verification.save()
            
            profile = verification.user
            profile.is_verified_owner = False
            profile.save()
            
            updated_count += 1
            
        self.message_user(
            request, 
            f"Successfully marked {updated_count} verification entry profiles as rejected."
        )

