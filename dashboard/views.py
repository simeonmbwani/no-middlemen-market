from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.db.models import Sum
from listings.models import Listing
from messaging.models import MessageInquiry

@login_required
def user_dashboard_view(request):
    user = request.user
    active_tab = request.GET.get('tab', 'inventory')
    
    # BASE CONTEXT (Safe version: No references to missing 'view_count' or ForeignKey fields)
    context = {
        'active_tab': active_tab,
        'user': user,
        'stats': {
            'rating': 4.8, 
            'listings': Listing.objects.filter(owner=user).count(),
            'saved': 0,
            'chats': MessageInquiry.objects.count(),
            # CHANGED: 'views' now defaults to 0 to avoid the FieldError
            'views': 0 
        }
    }

    # ACCOUNT UPDATES
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

    return render(request, 'dashboard/index.html', context)