from django.shortcuts import render, redirect
from django.contrib.auth import login
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth import get_user_model
from .forms import NationalIDUploadForm
from .models import NationalIDVerification
from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.admin.views.decorators import staff_member_required
from django.utils.timezone import now


User = get_user_model()

# Custom registration form layer to automatically handle mandatory custom fields
class MarketplaceUserCreationForm(UserCreationForm):
    class Meta(UserCreationForm.Meta):
        model = User
        fields = UserCreationForm.Meta.fields + ('email', 'phone_number', 'national_id')

def register_view(request):
    """
    Handles user profile registration.
    Saves new profiles securely and auto-authenticates them.
    """
    # Redirect already authenticated users straight to the listings stream
    if request.user.is_authenticated:
        return redirect('listings:list')

    if request.method == 'POST':
        # 🔧 FIXED: Swapped out base form for custom creation architecture to include phone and ID fields
        form = MarketplaceUserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            # Auto-authenticate the new user into their secure active browsing session
            login(request, user)
            messages.success(request, f"Account created successfully! Welcome to No Middlemen, {user.username}.")
            return redirect('listings:list')
        else:
            messages.error(request, "Registration failed. Please correct the layout errors highlighted below.")
    else:
        form = MarketplaceUserCreationForm()
        
    return render(request, 'accounts/register.html', {'form': form})


@login_required
def upload_national_id_view(request):
    """Processes secure KYC file uploads for the active marketplace user account profile."""
    # Check if user already has an active or approved verification submission
    existing_verification = NationalIDVerification.objects.filter(user=request.user).first()
    
    # 🔧 FIXED: Swapped 'dashboard:my-control-panel' redirect to point directly to your verified active index route
    if existing_verification and existing_verification.status == 'approved':
        messages.info(request, "Your profile is already fully verified and authenticated.")
        return redirect('dashboard:index')
        
    if request.method == 'POST':
        # request.FILES handles the incoming image binary data layout safely
        form = NationalIDUploadForm(request.POST, request.FILES)
        if form.is_valid():
            # Create object instance without saving to database immediately
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
    """
    Premium Frontend KYC Management Hub.
    Allows platform operators to audit national ID submissions dynamically.
    """
    # Fetch all pending verifications first, then historical records
    pending_verifications = NationalIDVerification.objects.filter(status='pending').order_by('submitted_at')
    reviewed_verifications = NationalIDVerification.objects.exclude(status='pending').order_by('-reviewed_at')[:10]
    
    if request.method == 'POST':
        verification_id = request.POST.get('verification_id')
        action = request.POST.get('action') # 'approve' or 'reject'
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