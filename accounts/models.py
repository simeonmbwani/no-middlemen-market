from django.db import models
from django.contrib.auth.models import AbstractUser
from django.core.validators import RegexValidator
from django.conf import settings

class User(AbstractUser):
    """
    Custom User Model for the No-Middlemen Marketplace.
    Tracks verification, Zimbabwean phone formats, system strikes, 
    and tabbed account preferences configuration states natively.
    """
    # Validates +263771234567, 0771234567, etc.
    phone_regex = RegexValidator(
        regex=r'^\+?263\d{9}$|^07\d{8}$', 
        message="Phone number must be entered in the format: '+263771234567' or '0771234567'."
    )
    
    # Core Authentication and Identity Attributes
    full_name = models.CharField(max_length=150, blank=True, help_text="User's real full legal name")
    phone_number = models.CharField(validators=[phone_regex], max_length=13, unique=True, null=True, blank=True)
    national_id = models.CharField(max_length=20, unique=True, null=True, blank=True, help_text="National ID Number")
    
    # 🌍 Regional Mapping Attributes (Airbnb / Property24 Scaling Layer)
    province = models.CharField(max_length=50, blank=True, help_text="Zimbabwean Province location")
    district = models.CharField(max_length=50, blank=True, help_text="Local District location mapping")
    
    # 🔔 Tabbed Notification Preferences Checkboxes
    email_new_message = models.BooleanField(default=True, help_text="Notify user upon incoming DMs")
    email_listing_approved = models.BooleanField(default=True, help_text="Notify user upon listing compliance approval")
    sms_notifications = models.BooleanField(default=False, help_text="Enable SMS broadcast updates")
    
    # 🔑 Listing Privacy & Defaults Controls
    default_price_period = models.CharField(max_length=10, default='monthly', help_text="Fallback choice: daily, weekly, monthly")
    show_phone_number = models.BooleanField(default=True, help_text="Toggle raw phone visibility")
    show_whatsapp = models.BooleanField(default=True, help_text="Toggle click-to-chat WhatsApp communication handles")
    
    # Anti-Middleman Status Flags
    is_verified_owner = models.BooleanField(default=False)
    strike_count = models.IntegerField(default=0)
    is_banned = models.BooleanField(default=False)

    # Overriding groups and permissions to assign completely unique related_names
    groups = models.ManyToManyField(
        'auth.Group',
        related_name='custom_user_groups_set',
        blank=True,
        help_text='The groups this user belongs to. A user will get all permissions granted to each of their groups.',
        verbose_name='groups',
    )
    user_permissions = models.ManyToManyField(
        'auth.Permission',
        related_name='custom_user_permissions_set',
        blank=True,
        help_text='Specific permissions for this user.',
        verbose_name='user permissions',
    )

    REQUIRED_FIELDS = ['email']

    def __str__(self):
        return f"{self.username} - {self.phone_number or 'No Phone'}"
    
    
class NationalIDVerification(models.Model):
    STATUS_CHOICES = [
        ('pending', 'Awaiting Administrator Review'),
        ('approved', 'Document Approved / Owner Verified'),
        ('rejected', 'Document Rejected / Invalid Identification'),
    ]

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='id_verifications'
    )
    
    id_document_front = models.ImageField(upload_to='national_ids/front/%Y/%m/')
    id_document_back = models.ImageField(upload_to='national_ids/back/%Y/%m/', blank=True, null=True)
    
    status = models.CharField(max_length=15, choices=STATUS_CHOICES, default='pending')
    admin_notes = models.TextField(blank=True, help_text="Reason for rejection or verification notes.")
    
    submitted_at = models.DateTimeField(auto_now_add=True)
    reviewed_at = models.DateTimeField(blank=True, null=True)

    class Meta:
        ordering = ['-submitted_at']
        verbose_name = "National ID Verification"
        verbose_name_plural = "National ID Verifications"

    def __str__(self):
        return f"ID Verification for @{self.user.username} - ({self.get_status_display()})"