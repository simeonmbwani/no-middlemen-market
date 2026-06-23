from django.db import models
from django.conf import settings
from listings.models import Listing

class MessageInquiry(models.Model):
    # Added null=True, blank=True to stop the 'NOT NULL' errors
    listing = models.ForeignKey(Listing, on_delete=models.CASCADE, related_name='inquiries', null=True, blank=True)
    sender = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='sent_messages', null=True, blank=True)
    receiver = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='received_messages', null=True, blank=True)
    
    attachment = models.FileField(upload_to='chat_attachments/%Y/%m/%d/', blank=True, null=True)
    message_text = models.TextField(max_length=500, help_text="Keep text clear and concise.")
    
    is_delivered = models.BooleanField(default=True)
    is_read = models.BooleanField(default=False)
    
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['created_at']
        verbose_name_plural = "Message Inquiries"

    def __str__(self):
        # We need a safe string representation in case sender/receiver are null
        sender_name = self.sender.username if self.sender else "Unknown"
        listing_name = self.listing.title[:20] if self.listing else "No Listing"
        return f"From {sender_name} re: {listing_name}"