from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib.auth import get_user_model  # 💡 Injected to query real system profile counts
from django.contrib import messages
from django.db.models import Q
from django.utils import translation
from django.conf import settings
from django.utils.timezone import now

# Core Model, Form, and Billing Module Imports
from .models import Listing
from .forms import ListingForm
from .billing import check_posting_limit, get_listing_fee

# ==========================================
# 🔍 PUBLIC ASSET-MARKET DISCOVERY VIEWS
# ==========================================

def listing_list_view(request):
    """
    Dynamically filters and streams verified live marketplace listings.
    ⚡ OPTIMIZED: Uses select_related('owner') to pull user profiles in 1 single database trip,
    completely eliminating the sluggish load times for users.
    """
    # Start with active, fully paid verified owner entries joined with their owner profile variables
    queryset = Listing.objects.filter(is_active=True, is_paid=True).select_related('owner').order_by('-created_at')
    
    # Extract structural query parameters from template inputs
    search_text = request.GET.get('search_text', '').strip()
    selected_category = request.GET.get('category', '').strip()
    selected_province = request.GET.get('province', '').strip()
    selected_district = request.GET.get('district', '').strip()
    max_price = request.GET.get('max_price', '').strip()

    # 1. Broad Text Query Vector (Matches Title or Description)
    if search_text:
        queryset = queryset.filter(
            Q(title__icontains=search_text) | Q(description__icontains=search_text)
        )

    # 2. Category Nested Option Matching
    if selected_category:
        queryset = queryset.filter(category=selected_category)

    # 3. Geo-Location Filtering (Province and District)
    if selected_province:
        queryset = queryset.filter(province__iexact=selected_province)
    if selected_district:
        queryset = queryset.filter(district__iexact=selected_district)

    # 4. Maximum Daily Budget Limits Check
    if max_price:
        try:
            queryset = queryset.filter(price__lte=max_price)
        except ValueError:
            pass  # Gracefully skip if string serialization is corrupted

    # Extract non-duplicate districts dynamically to keep select layout contextual
    available_districts = Listing.objects.filter(is_active=True, is_paid=True)\
                                         .values_list('district', flat=True)\
                                         .distinct().order_by('district')

    # 📊 DYNAMIC COUNTER CALCULATION: Replaces the hardcoded 5K+ with real database metrics
    live_users_count = User.objects.count()

    context = {
        'listings': queryset,
        'total_users_count': live_users_count,  # 👈 Passed seamlessly to your metrics card row layout!
        'category_choices': Listing.CATEGORY_CHOICES,  # Feeds nested select groupings
        'available_districts': available_districts,
        'ZIG_MID_RATE': getattr(settings, 'ZIG_MID_RATE', 25.00),  # Injected from global configuration metrics
    }
    return render(request, 'listings/listing_list.html', context)


def listing_detail_view(request, listing_id):
    """Fetches details for a single asset and showcases alternative local options in the same district."""
    # ⚡ OPTIMIZED: Joined with owner profile details instantly
    listing = get_object_or_404(Listing.objects.select_related('owner'), id=listing_id, is_active=True)
    
    # Identify alternative local listings in the matching region (excluding current listing context)
    related_items = Listing.objects.filter(
        district__iexact=listing.district,
        is_active=True,
        is_paid=True
    ).select_related('owner').exclude(id=listing.id)[:3]

    return render(request, 'listings/listing_detail.html', {
        'listing': listing,
        'related_items': related_items,
        'ZIG_MID_RATE': getattr(settings, 'ZIG_MID_RATE', 25.00),
    })


# ==========================================
# 🏗️ OWNER CRUD MANAGEMENT LIFECYCLE VIEWS
# ==========================================

@login_required
def listing_create_view(request):
    """
    Handles asset registration while catching duplicate submissions from malicious middleman loops
    and enforcing automated listing posting frequency limits.
    """
    if request.method == 'POST':
        form = ListingForm(request.POST, request.FILES)
        if form.is_valid():
            category = form.cleaned_data.get('category')
            title = form.cleaned_data.get('title')
            district = form.cleaned_data.get('district')
            
            # 📈 1. Run our automated posting threshold limit interceptor check
            is_allowed, total_posts, max_limit = check_posting_limit(request.user, category)
            
            if not is_allowed:
                # Enforce automatic suspension block rule for this category tier
                messages.error(
                    request, 
                    f"🚫 Limit Reached: You have reached your max allocation limit of {max_limit} posts per month "
                    f"for this asset classification type. Posting access will automatically restore as older ads expire."
                )
                return redirect('listings:list')
            
            # 🛡️ 2. Anti-broker flood protection match check
            duplicate_exists = Listing.objects.filter(
                owner=request.user,
                title__iexact=title,
                district__iexact=district,
                is_active=True
            ).exists()
            
            if duplicate_exists:
                messages.error(request, f"Duplicate Entry Detected! You already have an active listing for '{title}' in {district.title()}.")
                return render(request, 'listings/listing_form.html', {'form': form})
            
            # Calculate the fee structure variables to hook into invoice pipelines
            fee_info = get_listing_fee(category)
            fee_due = fee_info['fee_usd']
            
            # Proceed with form commit tracking
            new_listing = form.save(commit=False)
            new_listing.owner = request.user
            new_listing.save()
            
            messages.success(request, f"Asset registered (Fee: ${fee_due:.2f} USD)! Complete listing invoice to publish live.")
            return redirect('payments:checkout', listing_id=new_listing.id)
    else:
        form = ListingForm()
        
    return render(request, 'listings/listing_form.html', {'form': form})


@login_required
def edit_listing_view(request, listing_id):
    """Securely updates asset properties. Enforces direct owner authentication matching."""
    listing = get_object_or_404(Listing, id=listing_id, owner=request.user)
    
    if request.method == 'POST':
        form = ListingForm(request.POST, request.FILES, instance=listing)
        if form.is_valid():
            form.save()
            messages.success(request, f"'{listing.title}' has been successfully updated.")
            return redirect('dashboard:index')
    else:
        form = ListingForm(instance=listing)
        
    return render(request, 'listings/edit_listing.html', {'form': form, 'listing': listing})


@login_required
def delete_listing_view(request, listing_id):
    """Safely drops a listing row from data feeds (triggers post_delete files-cleanup signals)."""
    listing = get_object_or_404(Listing, id=listing_id, owner=request.user)
    
    if request.method == 'POST':
        title = listing.title
        listing.delete()  # Physical cleanup files triggered automatically via signals.py
        messages.success(request, f"'{title}' has been permanently removed from your inventory.")
        return redirect('dashboard:index')
        
    return render(request, 'listings/delete_confirm.html', {'listing': listing})


# ==========================================
# 🌍 LOCALIZATION & SESSION MANAGEMENT
# ==========================================

def set_language_view(request):
    """Dynamically updates and persists user language preferences (English, Shona, Ndebele) across sessions."""
    next_page = request.META.get('HTTP_REFERER', '/')
    response = redirect(next_page)
    
    if request.method == 'POST':
        lang_code = request.POST.get('language')
        if lang_code in ['en', 'sn', 'nd']:
            translation.activate(lang_code)
            
            # Persist choices securely via framework cookie tokens and system states
            response.set_cookie(settings.LANGUAGE_COOKIE_NAME, lang_code)
            if hasattr(request, 'session'):
                request.session['_language'] = lang_code
                
    return response