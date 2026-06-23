from django.db import models
from django.conf import settings
from listings.models import Listing


class MessageInquiry(models.Model):
    """
    Lightweight text-only inquiry system.
    Designed for low data usage and direct negotiations.
    """

    listing = models.ForeignKey(
        Listing,
        on_delete=models.CASCADE,
        related_name='inquiries'
    )

    sender = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='sent_messages'
    )

    receiver = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='received_messages'
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
        listing_title = self.listing.title[:30] if self.listing else "Unknown Listing"
        return (
            f"{self.sender.username} → "
            f"{self.receiver.username} "
            f"({listing_title})"
        )