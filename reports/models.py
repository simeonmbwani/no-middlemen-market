from django import forms
from django.db import models
from django.conf import settings  # 🚀 Added to fix the AUTH_USER_MODEL relation hint
from listings.models import Listing

class DirectReportForm(forms.Form):
    """
    A model-free reporting form.
    Gathers information without needing to import or save to a database table.
    """
    REASON_CHOICES = [
        ('middleman', 'Agent / Broker pretending to be the Legal Owner'),
        ('fraud', 'Scam / Extortion / Fake contact details'),
        ('duplicate', 'Duplicate asset listed by multiple accounts'),
        ('illegal', 'Prohibited items or unlicensed commercial activity'),
    ]

    reason = forms.ChoiceField(
        choices=REASON_CHOICES, 
        label="Reason for flagging",
        widget=forms.Select(attrs={'class': 'form-select'})
    )
    
    details = forms.CharField(
        label="Supporting details",
        max_length=500,
        widget=forms.Textarea(attrs={
            'rows': 3, 
            'class': 'form-control',
            'placeholder': 'Please state exactly why you believe this user is a broker or scammer...'
        })
    )
    

class ListingReport(models.Model):
    REASON_CHOICES = [
        ('middleman', 'Broker / Agent Hidden Fees'),
        ('viewing_fee', 'Demanding Upfront Viewing Fees'),
        ('fake', 'Fraudulent / Ghost Listing'),
        ('incorrect_info', 'Inaccurate / Misleading Details'),
    ]

    listing = models.ForeignKey(Listing, on_delete=models.CASCADE, related_name='flags')
    
    # 🔧 FIXED: Pointed relationship to settings.AUTH_USER_MODEL to clear the HINT warning
    reporter = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, null=True, blank=True)
    
    reason = models.CharField(max_length=20, choices=REASON_CHOICES)
    
    # 🔧 FIXED: Kept clean without placeholder attributes to prevent the TypeError crash
    details = models.TextField() 
    
    created_at = models.DateTimeField(auto_now_add=True)
    is_reviewed = models.BooleanField(default=False)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"Report on '{self.listing.title}' - Reason: {self.get_reason_display()}" 