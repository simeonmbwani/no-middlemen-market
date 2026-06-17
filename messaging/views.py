from django.shortcuts import get_object_or_404, redirect, render
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from listings.models import Listing
from .models import MessageInquiry
from django.contrib.auth.models import User


@login_required
def send_inquiry_view(request, listing_id):
    """Processes incoming communication text forms from buyers straight to asset owners."""
    if request.method == 'POST':
        target_listing = get_object_or_404(Listing, id=listing_id)
        buyer_text = request.POST.get('message_text', '').strip()

        # Prevent a user from sending a message inquiry to themselves
        if target_listing.owner == request.user:
            messages.error(request, "Operation Denied: You cannot send an inquiry text on your own listing.")
            return redirect('listings:detail', listing_id=target_listing.id)

        if buyer_text:
            MessageInquiry.objects.create(
                listing=target_listing,
                sender=request.user,
                receiver=target_listing.owner,
                message_text=buyer_text
            )
            messages.success(request, "Your direct inquiry has been securely sent! The owner will respond via your dashboard panel.")
        else:
            messages.error(request, "Message transmission failed. Cannot dispatch empty message fields.")

    return redirect('listings:detail', listing_id=listing_id)
@login_required
def inbox_view(request):
    """A low-data inbox dashboard showing messages received or sent by the user."""
    # Fetch incoming messages sorted by newest first
    received_messages = MessageInquiry.objects.filter(receiver=request.user).order_by('-created_at')
    sent_messages = MessageInquiry.objects.filter(sender=request.user).order_by('-created_at')
    
    context = {
        'received_messages': received_messages,
        'sent_messages': sent_messages,
    }
    return render(request, 'messaging/inbox.html', context)

@login_required
def chat_hub_view(request):
    """Renders all direct messaging threads grouped by participant handles."""
    user = request.user
    
    # Fetch all chats where the user is either the sender or receiver
    all_messages = MessageInquiry.objects.filter(sender=user) | MessageInquiry.objects.filter(receiver=user)
    
    # Extract unique users you are talking to
    chat_partners_ids = set()
    for msg in all_messages:
        if msg.sender != user:
            chat_partners_ids.add(msg.sender.id)
        if msg.receiver != user:
            chat_partners_ids.add(msg.receiver.id)
            
    chat_partners = User.objects.filter(id__in=chat_partners_ids)

    return render(request, 'messaging/chat_hub.html', {'chat_partners': chat_partners})

@login_required
def direct_chat_thread_view(request, partner_id):
    """Displays chronological text bubbles between you and a specific user profile."""
    partner = get_object_or_404(User, id=partner_id)
    user = request.user
    
    # Chronological history conversation loop query
    messages_stream = MessageInquiry.objects.filter(
        sender=user, receiver=partner
    ) | MessageInquiry.objects.filter(
        sender=partner, receiver=user
    ).order_by('created_at')

    # Mark incoming items as read instantly upon screen loading
    MessageInquiry.objects.filter(sender=partner, receiver=user, is_read=False).update(is_read=True)

    return render(request, 'messaging/chat_thread.html', {
        'partner': partner,
        'messages_stream': messages_stream
    })
    
from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from listings.models import Listing
from .models import MessageInquiry

@login_required
def send_message_view(request, listing_id):
    """Handles an initial inquiry from a buyer on an asset detail page."""
    listing = get_object_or_404(Listing, id=listing_id)
    
    if request.method == 'POST':
        message_content = request.POST.get('message_text')
        if message_content:
            MessageInquiry.objects.create(
                listing=listing,
                sender=request.user,
                receiver=listing.owner, # Direct targeting
                message_text=message_content,
                is_delivered=True
            )
            messages.success(request, "Your message has been sent directly to the asset owner!")
    return redirect('listings:detail', listing_id=listing.id)

@login_required
def reply_message_view(request, parent_id):
    """Enables seamless direct reply configurations back to the inquirer."""
    parent_message = get_object_or_404(MessageInquiry, id=parent_id, receiver=request.user)
    
    if request.method == 'POST':
        reply_text = request.POST.get('reply_text')
        if reply_text:
            MessageInquiry.objects.create(
                listing=parent_message.listing,
                sender=request.user,
                receiver=parent_message.sender, # Flip fields: original sender becomes receiver
                message_text=reply_text,
                is_delivered=True
            )
            messages.success(request, "Reply dispatched instantly!")
    return redirect('dashboard:index')