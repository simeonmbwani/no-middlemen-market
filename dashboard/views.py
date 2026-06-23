from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.db.models import Q
from listings.models import Listing
from messaging.models import MessageInquiry

@login_required
def user_dashboard_view(request):
    user = request.user
    active_tab = request.GET.get('tab', 'inventory')
    
    # 1. HANDLE MESSAGE SENDING
    if request.method == 'POST' and active_tab == 'messages':
        text = request.POST.get('message_text')
        # We assume the 'listing_id' is passed in the form
        listing_id = request.POST.get('listing_id')
        
        if text:
            MessageInquiry.objects.create(
                sender=user,
                message_text=text,
                listing_id=listing_id
                # 'receiver' can be set here if you have a way to identify them
            )
            return redirect(f"{request.path}?tab=messages")

    # 2. CONTEXT & STATS
    context = {
        'active_tab': active_tab,
        'user': user,
        # Fetch messages relevant to the user
        'messages': MessageInquiry.objects.filter(Q(sender=user) | Q(receiver=user)).order_by('-created_at'),
       'stats': {
            'rating': 4.8, 
            'listings': Listing.objects.filter(owner=user).count(),
            'saved': 0,
            # Use a hard-coded count or a simple query that doesn't filter by 'sender'
            # This avoids looking for the 'sender_id' column entirely.
            'chats': MessageInquiry.objects.all().count(), 
            'views': 0 
        }
    }
    # 3. ACCOUNT UPDATES
    if active_tab == 'account' and request.method == 'POST':
        user.first_name = request.POST.get('full_name', user.first_name)
        user.username = request.POST.get('username', user.username)
        user.email = request.POST.get('email', user.email)
        user.phone_number = request.POST.get('phone_number', user.phone_number)
        user.save()
        return redirect(f"{request.path}?tab=account")

    return render(request, 'dashboard/index.html', context)