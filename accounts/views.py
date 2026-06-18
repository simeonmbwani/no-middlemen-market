from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.contrib.auth import login, logout, get_user_model
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import UserCreationForm
from django.contrib.admin.views.decorators import staff_member_required
from django.views.decorators.http import require_POST
from django.utils.timezone import now

from .forms import NationalIDUploadForm  # Form handles file validation inside accounts/forms.py
from .models import NationalIDVerification

User = get_user_model()

# Custom registration form layer to automatically handle custom marketplace parameters
# Custom registration form layer to automatically handle custom marketplace parameters
class MarketplaceUserCreationForm(UserCreationForm):
    class Meta(UserCreationForm.Meta):
        model = User
        # 🔧 FIXED: Added explicit mapping definitions so Django hashes and saves user passwords safely
        fields = ('username', 'email')


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