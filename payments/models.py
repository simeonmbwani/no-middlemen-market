from django.db import models
from django.conf import settings
from listings.models import Listing

class Payment(models.Model):
    """
    Tracks local mobile money and cash-agency transaction records.
    Directly connected to a single specific asset listing.
    """
    STATUS_CHOICES = [
        ('pending', 'Pending Authentication'),
        ('success', 'Payment Confirmed'),
        ('failed', 'Transaction Failed'),
    ]
    GATEWAY_CHOICES = [
        ('ecocash', 'EcoCash USSD'),
        ('onemoney', 'OneMoney USSD'),
        ('innbucks', 'Innbucks Voucher'),
        ('paynow', 'Paynow Web Portal'),
    ]

    listing = models.OneToOneField(
        Listing, 
        on_delete=models.CASCADE, 
        related_name='payment'
    )
    owner = models.ForeignKey(
        settings.AUTH_USER_MODEL, 
        on_delete=models.CASCADE, 
        related_name='payments'
    )
    
    amount = models.DecimalField(
        max_digits=6, 
        decimal_places=2, 
        help_text="Amount in USD"
    )
    gateway = models.CharField(max_length=15, choices=GATEWAY_CHOICES)
    
    # Tracking fields for Paynow API integration
    reference = models.CharField(
        max_length=50, 
        unique=True, 
        help_text="Unique invoice/system transaction reference"
    )
    poll_url = models.URLField(
        blank=True, 
        null=True, 
        help_text="Internal tracking URL provided by Paynow to check status changes"
    )
    
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='pending')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"Ref: {self.reference} | {self.listing.title[:20]} | Status: {self.status}"

class Report(models.Model):
    """
    The main verification tracking table.
    Allows public users to flag brokers, fake owners, or illegal listings.
    """
    REASON_CHOICES = [
        ('middleman', 'Agent / Broker pretending to be the Legal Owner'),
        ('fraud', 'Scam / Extortion / Fake contact details'),
        ('duplicate', 'Duplicate asset listed by multiple accounts'),
        ('illegal', 'Prohibited items or unlicensed commercial activity'),
    ]

    reporter = models.ForeignKey(
        settings.AUTH_USER_MODEL, 
        on_delete=models.SET_NULL, 
        null=True, 
        blank=True,
        related_name='reports_filed'
    )
    listing = models.ForeignKey(
        Listing, 
        on_delete=models.CASCADE, 
        related_name='reports'
    )
    
    reason = models.CharField(max_length=20, choices=REASON_CHOICES)
    details = models.TextField(
        max_length=500, 
        help_text="Provide supporting evidence (e.g., 'This person asked for a viewing fee via EcoCash before showing the mill')."
    )
    
    # Administration controls
    is_resolved = models.BooleanField(default=False)
    admin_notes = models.TextField(max_length=500, blank=True, null=True)
    
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"Report #{self.id} against [{self.listing.title[:20]}] - Reason: {self.get_reason_display()}"    

class EscrowInvoice(models.Model):
    STATUS_CHOICES = [
        ('pending', 'Invoice Issued / Awaiting Payment'),
        ('secured', 'Funds Escrowed Safely'),
        ('released', 'Funds Released to Owner'),
        ('disputed', 'Transaction Under Review / Disputed'),
        ('cancelled', 'Invoice Cancelled'),
    ]

    listing = models.ForeignKey(Listing, on_delete=models.CASCADE, related_name='invoices')
    buyer = models.ForeignKey(
        settings.AUTH_USER_MODEL, 
        on_delete=models.CASCADE, 
        related_name='purchases'
    )
    seller = models.ForeignKey(
        settings.AUTH_USER_MODEL, 
        on_delete=models.CASCADE, 
        related_name='sales'
    )
    
    # Financial fields tracking values dynamically
    amount_usd = models.DecimalField(max_digits=10, decimal_places=2)
    system_fee_usd = models.DecimalField(max_digits=8, decimal_places=2, default=0.00)
    
    status = models.CharField(max_length=15, choices=STATUS_CHOICES, default='pending')
    
    # Audit trail trackers
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    # Verification checks completed on-site before release
    buyer_confirmed_delivery = models.BooleanField(default=False)
    seller_confirmed_delivery = models.BooleanField(default=False)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"Invoice #{self.id} - {self.listing.title} ({self.get_status_display()})"    