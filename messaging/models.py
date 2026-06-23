from django.db import models
from django.conf import settings
from listings.models import Listing

class MessageInquiry(models.Model):
    """
    Lightweight, robust inquiry system.
    Nullable ForeignKeys prevent deployment crashes.
    """

    listing = models.ForeignKey(
        Listing,
        on_delete=models.SET_NULL, # Prevents deleting messages if listing is gone
        related_name='inquiries',
        null=True, 
        blank=True
    )

    sender = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL, # Keeps history if user account is removed
        related_name='sent_messages',
        null=True, 
        blank=True
    )

    receiver = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        related_name='received_messages',
        null=True, 
        blank=True
    )

    message_text = models.TextField(
        max_length=500,
        help_text="Keep text clear and concise."
    )

    # Message status
    is_delivered = models.BooleanField(default=True)
    is_read = models.BooleanField(default=False)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['created_at']
        verbose_name = "Message Inquiry"
        verbose_name_plural = "Message Inquiries"

    def __str__(self):
        # Safe string handling: avoids errors if sender/receiver/listing are None
        sender_name = self.sender.username if self.sender else "Deleted User"
        receiver_name = self.receiver.username if self.receiver else "Deleted User"
        listing_title = self.listing.title[:30] if self.listing else "No Listing"
        
        return f"{sender_name} → {receiver_name} ({listing_title})"