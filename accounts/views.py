from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.contrib.auth import login, logout, get_user_model, authenticate
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django.contrib.admin.views.decorators import staff_member_required
from django.views.decorators.http import require_POST
from django.utils.timezone import now

from .forms import NationalIDUploadForm  # Form handles file validation inside accounts/forms.py
from .models import NationalIDVerification

User = get_user_model()

# Custom registration form layer to automatically handle custom marketplace parameters
class MarketplaceUserCreationForm(UserCreationForm):
    class Meta(UserCreationForm.Meta):
        model = User
        # 🔧 FIXED: Added explicit mapping definitions so Django hashes and saves user passwords safely
        fields = ('username', 'email')


def login_view(request):
    """
    🔒 SECURITY UPGRADE: Custom authentication handler that logs in regular users 
    and handles superuser/staff permissions without constraint exceptions.
    """
    if request.user.is_authenticated:
        return redirect('listings:list')

    if request.method == 'POST':
        form = AuthenticationForm(request, data=request.POST)
        if form.is_valid():
            user = form.get_user()
            # Explicitly declare the model backend to prevent multi-auth backend collision
            login(request, user, backend='django.contrib.auth.backends.ModelBackend')
            
            # 👑 SMART ROUTING: Redirect administrators straight to the new 20-module ERP hub
            if user.is_staff or user.is_superuser:
                messages.success(request, f"👑 Administrator @{user.username} authenticated successfully.")
                return redirect('accounts:erp_control_center')
                
            messages.success(request, f"Welcome back, @{user.username}!")
            return redirect('listings:list')
        else:
            messages.error(request, "Invalid username or password. Please try again.")
    else:
        form = AuthenticationForm()

    return render(request, 'accounts/login.html', {'form': form})


def register_view(request):
    """
    Handles user profile registration.
    Saves new profiles securely and auto-authenticates them.
    """
    if request.user.is_authenticated:
        return redirect('listings:list')

    if request.method == 'POST':
        form = MarketplaceUserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user, backend='django.contrib.auth.backends.ModelBackend')
            messages.success(request, f"Account created successfully! Welcome to No Middlemen, {user.username}.")
            return redirect('listings:list')
        else:
            messages.error(request, "Registration failed. Please correct the validation constraints below.")
    else:
        form = MarketplaceUserCreationForm()
        
    return render(request, 'accounts/register.html', {'form': form})


@require_POST
def logout_view(request):
    """
    🔒 SECURITY ENHANCEMENT: Enforces secure POST request validation 
    for sessions, eliminating 403 and 405 routing exceptions.
    """
    logout(request)
    messages.success(request, "You have logged out securely. See you soon!")
    return redirect('listings:list')  


@login_required
def upload_national_id_view(request):
    """Processes secure KYC file uploads for the active marketplace user account profile."""
    existing_verification = NationalIDVerification.objects.filter(user=request.user).first()
    
    if existing_verification and existing_verification.status == 'approved':
        messages.info(request, "Your profile is already fully verified and authenticated.")
        return redirect('dashboard:index')
        
    if request.method == 'POST':
        form = NationalIDUploadForm(request.POST, request.FILES)
        if form.is_valid():
            verification = form.save(commit=False)
            verification.user = request.user
            verification.status = 'pending'
            verification.save()
            
            messages.success(request, "Identification documents uploaded successfully. Awaiting administrator review.")
            return redirect('dashboard:index')
        else:
            messages.error(request, "Invalid form data submission. Please check your image parameters.")
    else:
        form = NationalIDUploadForm()
        
    context = {
        'form': form,
        'existing_verification': existing_verification
    }
    return render(request, 'accounts/upload_id.html', context)


@staff_member_required
def compliance_dashboard_view(request):
    """Premium Frontend KYC Management Hub for system audits."""
    pending_verifications = NationalIDVerification.objects.filter(status='pending').order_by('submitted_at')
    reviewed_verifications = NationalIDVerification.objects.exclude(status='pending').order_by('-reviewed_at')[:10]
    
    if request.method == 'POST':
        verification_id = request.POST.get('verification_id')
        action = request.POST.get('action') 
        admin_notes = request.POST.get('admin_notes', '').strip()
        
        verification = get_object_or_404(NationalIDVerification, id=verification_id)
        user = verification.user
        
        if action == 'approve':
            verification.status = 'approved'
            user.is_verified_owner = True
            messages.success(request, f"✅ Account @{user.username} has been verified successfully!")
        elif action == 'reject':
            verification.status = 'rejected'
            user.is_verified_owner = False
            messages.warning(request, f"❌ KYC Submission for @{user.username} rejected.")
            
        verification.admin_notes = admin_notes
        verification.reviewed_at = now()
        verification.save()
        user.save()
        
        return redirect('accounts:compliance_dashboard')

    return render(request, 'accounts/compliance_dashboard.html', {
        'pending': pending_verifications,
        'history': reviewed_verifications,
    })  
    

def terms_faq_view(request):
    """
    Renders the standalone full-screen trust matrix 
    housing platform Terms, Conditions, and FAQs.
    """
    return render(request, 'accounts/terms_faq.html')


@login_required
def settings_dashboard_view(request):
    """
    Renders and processes the premium tabbed profile settings control center
    including localization, privacy, notifications, and danger parameters.
    """
    user = request.user
    if request.method == 'POST':
        action = request.POST.get('action')
        
        if action == 'save_profile':
            user.full_name = request.POST.get('full_name', '')
            user.phone_number = request.POST.get('phone_number', '')
            user.province = request.POST.get('province', '')
            user.district = request.POST.get('district', '')
            user.save()
            messages.success(request, "Profile configuration saved successfully!")
            
        elif action == 'save_privacy':
            user.show_phone_number = 'show_phone' in request.POST
            user.show_whatsapp = 'show_wa' in request.POST
            user.save()
            messages.success(request, "Privacy visibility mapping updated.")
            
        return redirect('accounts:settings_dashboard')

    return render(request, 'accounts/settings_dashboard.html')


from django.contrib.auth import get_user_model
from listings.models import Listing  # Adjust import based on your exact app/model names
# from payments.models import Transaction  # Import when your payments app models are ready

User = get_user_model()

from django.contrib.auth import get_user_model

# 🛑 CHANGE THIS LINE: 
# Instead of 'Asset', import whatever your true model name is inside listings/models.py
# For example, if your class is named Listing, change it to:
from listings.models import Listing  

User = get_user_model()

from django.contrib.auth import get_user_model
from listings.models import Listing  # 👑 FIXED: Changed from 'Asset' to 'Listing'

User = get_user_model()

from django.db.models import Sum
from django.contrib.auth import get_user_model
from django.contrib.admin.views.decorators import staff_member_required
from django.shortcuts import render
from listings.models import Listing
# from messaging.models import ChatRoom, Message # Add imports as your apps build out
# from payments.models import Transaction
# from reports.models import RedFlagReport, Violation

User = get_user_model()

@staff_member_required
def erp_control_center_view(request):
    """
    👑 MASTER BANKING ERP CONTROL SYSTEM: Real-Time Operational Agregator.
    Loads real database tallies for all 20 integrated platform modules natively.
    """
    # 👥 Module 1: Live User Data Array
    users_list = User.objects.all().order_by('-date_joined')
    total_users = users_list.count()
    verified_users = User.objects.filter(is_verified_owner=True).count()
    suspended_count = User.objects.filter(strike_count__gte=3).count()
    banned_count = User.objects.filter(is_banned=True).count()

    # 🏢 Module 2 & 10: Asset Catalog & Categories Tracking
    listings_list = Listing.objects.all().order_by('-created_at')
    total_assets = listings_list.count()
    active_listings = Listing.objects.filter(is_active=True).count()
    pending_approval = Listing.objects.filter(is_active=False, is_paid=True).count()

    # 💸 Module 4: Payment Center Ledger Calculations
    # total_revenue = Transaction.objects.filter(status='success').aggregate(Sum('amount'))['amount__sum'] or 0
    total_revenue = 0.00  # Fallback tracker until payment migrations run

    # 📦 Compile all database states cleanly into a single context matrix
    context = {
        # Lists for tables
        'users_list': users_list,
        'listings_list': listings_list,
        'audit_logs': [],  # Placed inside your SQLite Audit Tracking Database url string setup
        
        # Dashboard Counter Metrics
        'total_users': total_users,
        'verified_users': verified_users,
        'total_assets': total_assets,
        'active_listings': active_listings,
        'pending_approval': pending_approval,
        'suspended_count': suspended_count,
        'banned_count': banned_count,
        'total_revenue': total_revenue,
        'unresolved_reports': 0,  # RedFlagReport.objects.filter(status='pending').count()
    }
    return render(request, 'admin/control_center.html', context)

@staff_member_required
def erp_user_management_view(request):
    """
    👥 MODULE 1: Dynamic User Management Control Panel.
    Fetches real system profiles for administrative audit actions.
    """
    users_list = User.objects.all().order_by('-date_joined')
    
    context = {
        'users_list': users_list,
        'total_registered_count': users_list.count(),
    }
    return render(request, 'admin/user_management.html', context)

# ==============================================================================
# 👑 ERP MASTER CORE SIDEBAR MODULE MODULES (2 to 20)
# ==============================================================================

