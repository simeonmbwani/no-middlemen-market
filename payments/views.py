import uuid
from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.contrib.auth import get_user_model

from listings.models import Listing
from .models import Payment, EscrowInvoice

# 🔧 FIXED: Correctly grab the active custom User model namespace to stop NameErrors
User = get_user_model()


@login_required
def checkout_view(request, listing_id):
    """Displays the listing processing fee invoice based on choice groupings."""
    listing = get_object_or_404(Listing, id=listing_id, owner=request.user)
    
    if listing.is_paid:
        messages.info(request, "This listing has already been processed.")
        return redirect('listings:detail', listing_id=listing.id)

    # 💰 Dynamic Structural Pricing Tiers based on Main Equipment Types
    # Heavy Duty Gear (Mining, Farming Industrial Properties) = $3.00
    # Standard Gear (Vehicles, Infrastructure, IT, Events) = $2.00
    # Light/Micro Gear & Other unlisted fields = $1.00
    
    cat = listing.category
    
    if cat in ['excavator', 'bulldozer', 'drill_rig', 'crusher', 'dump_truck', 'land_plot', 'ind_building', 'harvester']:
        fee = 3.00
    elif cat in ['car', 'truck', 'bus', 'minibus', 'tipper', 'fuel_tanker', 'house', 'flat', 'warehouse', 'starlink_kit', 'pa_system', 'server']:
        fee = 2.00
    else:
        # 🔧 AUTOMATIC FALLBACK BASE RATE: For 'other_asset' or anything not listed above explicitly
        fee = 1.00

    if request.method == 'POST':
        gateway = request.POST.get('gateway')
        if not gateway:
            messages.error(request, "Please select a payment provider.")
            return redirect('payments:checkout', listing_id=listing.id)

        unique_ref = f"NMM-{uuid.uuid4().hex[:8].upper()}"
        payment = Payment.objects.create(
            listing=listing,
            owner=request.user,
            amount=fee,
            gateway=gateway,
            reference=unique_ref,
            status='pending'
        )
        return redirect('payments:verify', payment_id=payment.id)

    return render(request, 'payments/checkout.html', {'listing': listing, 'fee': fee})

@login_required
def verify_payment_view(request, payment_id):
    """
    Simulates / processes real-time transaction confirmation requests.
    Once successful, updates payment status and unlocks public listing.
    """
    payment = get_object_or_404(Payment, id=payment_id, owner=request.user)
    listing = payment.listing

    if request.method == 'POST':
        action = request.POST.get('action')
        
        if action == 'confirm_simulation':
            # 🚀 Transaction Success Loop Execution
            payment.status = 'success'
            payment.save()
            
            # Instantly update flags to push the asset live to search feeds
            listing.is_paid = True
            listing.is_active = True
            listing.save()
            
            messages.success(request, "Payment confirmed successfully! Your asset listing is now live across Zimbabwe.")
            return redirect('listings:detail', listing_id=listing.id)
            
        elif action == 'fail_simulation':
            payment.status = 'failed'
            payment.save()
            messages.error(request, "Transaction was cancelled or failed. Please try again.")
            return redirect('payments:checkout', listing_id=listing.id)

    return render(request, 'payments/verify.html', {'payment': payment})


# 🔧 FIXED: Removed duplicatestacked decorator initialization lines
@login_required
def create_invoice_view(request, listing_id):
    listing = get_object_or_404(Listing, id=listing_id)
    
    if request.method == 'POST':
        buyer_username = request.POST.get('buyer_username')
        amount_usd = request.POST.get('amount_usd')
        
        try:
            buyer = User.objects.get(username=buyer_username)
            
            # 🔧 FIXED: Changed field argument from 'amount' to 'amount_usd' to match your database schema
            invoice = EscrowInvoice.objects.create(
                listing=listing,
                seller=request.user,
                buyer=buyer,
                amount_usd=amount_usd,
                status='pending'
            )
            
            messages.success(request, f"Invoice issued successfully to @{buyer.username}!")
            return redirect('dashboard:index')  # Reroute straight to dashboard metrics
            
        except User.DoesNotExist:
            messages.error(request, f"User @{buyer_username} does not exist. Please check the username spelling.")
            
    return render(request, 'payments/create_invoice.html', {'listing': listing})
@login_required
def secure_payment_view(request, invoice_id):
    """Simulates the buyer depositing funds safely into the marketplace escrow tank."""
    invoice = get_object_or_404(EscrowInvoice, id=invoice_id)
    
    # Secure validation: Only the assigned buyer can fund this specific invoice
    if invoice.buyer != request.user:
        messages.error(request, "Unauthorized action. This invoice belongs to another buyer profile.")
        return redirect('dashboard:index')
        
    if invoice.status == 'pending':
        invoice.status = 'secured'
        invoice.save()
        messages.success(request, f"Payment for Invoice #{invoice.id} has been secured in escrow. Awaiting physical inspection.")
    else:
        messages.warning(request, "This invoice is not awaiting payment status parameters.")
        
    # 🔧 FIXED: Routed redirect paths back to your valid workspace dashboard index pattern name
    return redirect('dashboard:index')


@login_required
def release_escrow_view(request, invoice_id):
    """Triggers the on-site release of funds once the asset is physically inspected and verified."""
    invoice = get_object_or_404(EscrowInvoice, id=invoice_id)
    
    if invoice.buyer != request.user:
        messages.error(request, "Unauthorized verification action.")
        return redirect('dashboard:index')
        
    if invoice.status == 'secured':
        invoice.buyer_confirmed_delivery = True
        invoice.status = 'released'
        invoice.save()
        messages.success(request, f"Transaction finalized! Funds for Invoice #{invoice.id} have been cleanly released to @{invoice.seller.username}.")
    else:
        messages.error(request, "Funds cannot be released unless they are actively secured in escrow.")
        
    # 🔧 FIXED: Routed redirect paths back to your valid workspace dashboard index pattern name
    return redirect('dashboard:index')