from django.shortcuts import render, redirect, get_object_or_404
from django.core.mail import send_mail
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.utils.timezone import now

from listings.models import Listing
from .models import ListingReport  # 🔧 FIXED: Swapped form with actual DB model

@login_required
def report_listing_view(request, listing_id):
    """
    Processes marketplace violation flags via ListingReport DB model layouts.
    Automatically increments system strikes and executes account bans.
    """
    listing = get_object_or_404(Listing, id=listing_id)
    
    # Secure Validation: Prevent users from flagging their own assets out of loop context
    if listing.owner == request.user:
        messages.error(request, "You cannot file a community violation report against your own asset.")
        return redirect('listings:detail', listing_id=listing.id)
        
    if request.method == 'POST':
        reason = request.POST.get('reason')
        details = request.POST.get('details', '').strip()
        
        if not reason or not details:
            messages.error(request, "Please provide a valid violation reason and description text.")
            return redirect('listings:detail', listing_id=listing.id)
            
        # Anti-Spam Check: Prevent a user from flagging the exact same listing twice for an active review
        already_flagged = ListingReport.objects.filter(
            listing=listing, 
            reporter=request.user,
            is_reviewed=False
        ).exists()
        
        if already_flagged:
            messages.warning(request, "You have already submitted an active investigation report on this asset.")
            return redirect('listings:detail', listing_id=listing.id)

        # 🔧 FIXED: Cleanly construct database record instead of triggering empty form.save() error hooks
        report = ListingReport.objects.create(
            listing=listing,
            reporter=request.user,
            reason=reason,
            details=details
        )
        
        # 🔨 DYNAMIC ANTI-FRAUD ENGINE TRIGGER:
        # We track strikes on the target asset owner directly from the account model ledger
        target_owner = listing.owner
        
        # Safe fallback initialization check if strike_count parameter isn't structured as field yet
        if not hasattr(target_owner, 'strike_count'):
            target_owner.strike_count = 0
            
        target_owner.strike_count += 1
        
        # Critical Threshold Enforcement: 3 strikes triggers an immediate automated platform ban
        if target_owner.strike_count >= 3:
            target_owner.is_banned = True
            target_owner.is_verified_owner = False  # Revoke validated status instantly
            
            # 🔧 FUNCTIONAL ADDITION: Automatically alert marketplace admins via your terminal email backend
            send_mail(
                subject=f"🚨 SECURITY ALERT: Account Ban @{target_owner.username}",
                message=f"User @{target_owner.username} has been automatically banned from the platform after reaching {target_owner.strike_count} system strikes. Final infraction occurred on listing ID #{listing.id}.",
                from_email='security@nomiddlemen.co.zw',
                recipient_list=['admin@nomiddlemen.co.zw'],
                fail_silently=True
            )
            
            messages.error(
                request, 
                f"Warning: Listing owner @{target_owner.username} has reached 3 strikes and is now banned."
            )
        else:
            messages.warning(
                request, 
                f"Violation logged. Owner @{target_owner.username} has accrued a strike ({target_owner.strike_count}/3)."
            )
            
        target_owner.save()
        
        # Cleanly unpublish the flagged item from the active marketplace feed for inspection
        listing.is_active = False
        listing.save()
        
        messages.success(request, "Thank you. The marketplace violation report has been submitted securely for review.")
        return redirect('listings:list')
        
    return redirect('listings:detail', listing_id=listing.id)