from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.contrib.auth import get_user_model
from django.db.models import Q, Sum, Count
from django.http import JsonResponse
from django.template.loader import render_to_string

# Models
from listings.models import Listing
from payments.models import Payment, EscrowInvoice
from messaging.models import MessageInquiry
from accounts.models import Profile # Ensure this is your profile model

@login_required
def user_dashboard_view(request):
    user = request.user
    active_tab = request.GET.get('tab', 'inventory')
    
    # 1. BASE CONTEXT (Common data for all tabs)
    context = {
        'active_tab': active_tab,
        'user': user,
        'profile': Profile.objects.get_or_create(user=user)[0],
        'stats': {
            'rating': 4.8, 
            'listings': Listing.objects.filter(owner=user).count(),
            'saved': getattr(user, 'saved_assets', Listing.objects.none()).count(),
            'chats': MessageInquiry.objects.filter(Q(sender=user) | Q(listing__owner=user)).count(),
            'views': Listing.objects.filter(owner=user).aggregate(v=Sum('view_count'))['v'] or 0
        }
    }

    # 2. ACCOUNT UPDATES (Unified logic)
    if active_tab == 'account' and request.method == 'POST':
        user.first_name = request.POST.get('full_name', user.first_name)
        user.username = request.POST.get('username', user.username)
        profile = context['profile']
        profile.phone_number = request.POST.get('phone_number', profile.phone_number)
        profile.national_id = request.POST.get('national_id', profile.national_id)
        profile.province = request.POST.get('province', profile.province)
        profile.district = request.POST.get('district', profile.district)
        profile.save()
        user.save()
        return redirect(f"{request.path}?tab=account")

    # 3. MESSAGING LOGIC (Your existing complex engine)
    if active_tab == 'messages':
        # ... (keep your existing message logic here) ...
        # Ensure you update the 'context' dictionary with 'messages_list' and 'partner'
        pass 

    return render(request, 'dashboard/index.html', context)