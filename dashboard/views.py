from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.db.models import Q, Sum
from listings.models import Listing
from messaging.models import MessageInquiry
# REMOVED: from accounts.models import Profile (Not needed anymore)

@login_required
def user_dashboard_view(request):
    user = request.user
    active_tab = request.GET.get('tab', 'inventory')
    
    # 1. BASE CONTEXT (Pulling directly from the custom User model)
    context = {
        'active_tab': active_tab,
        'user': user,
        'stats': {
            'rating': 4.8, 
            'listings': Listing.objects.filter(owner=user).count(),
            'saved': 0, # Update this relation if you have one
            'chats': MessageInquiry.objects.filter(Q(sender=user) | Q(listing__owner=user)).count(),
            'views': Listing.objects.filter(owner=user).aggregate(v=Sum('view_count'))['v'] or 0
        }
    }

    # 2. ACCOUNT UPDATES (Unified logic using custom User fields)
    if active_tab == 'account' and request.method == 'POST':
        user.first_name = request.POST.get('full_name', user.first_name)
        user.username = request.POST.get('username', user.username)
        user.email = request.POST.get('email', user.email)
        user.phone_number = request.POST.get('phone_number', user.phone_number)
        user.national_id = request.POST.get('national_id', user.national_id)
        user.province = request.POST.get('province', user.province)
        user.district = request.POST.get('district', user.district)
        user.save()
        return redirect(f"{request.path}?tab=account")

    # 3. MESSAGING LOGIC
    if active_tab == 'messages':
        # Your previous logic stays here. 
        # Just ensure your template uses {{ user.username }} instead of {{ user.profile.username }}
        pass 

    return render(request, 'dashboard/index.html', context)