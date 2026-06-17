from django.db import models
from django.conf import settings
from listings.models import Listing

from django.db import models
from django.conf import settings
from listings.models import Listing

class MessageInquiry(models.Model):
    """
    Lightweight, text-only inquiry system.
    Strictly no attachments or media to enforce data saving.
    """
    listing = models.ForeignKey(Listing, on_delete=models.CASCADE, related_name='inquiries')
    sender = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='sent_messages')
    receiver = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='received_messages')
    
    message_text = models.TextField(max_length=500, help_text="Keep text clear and concise.")
    
    # 🔧 NEW: Added WhatsApp-style delivery tracking flag status variables
    is_delivered = models.BooleanField(default=True)
    is_read = models.BooleanField(default=False)
    
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['created_at']
        verbose_name_plural = "Message Inquiries"

    def __str__(self):
        return f"From {self.sender.username} to {self.receiver.username} re: {self.listing.title[:20]}"