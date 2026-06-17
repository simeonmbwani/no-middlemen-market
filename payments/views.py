import uuid
from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.contrib.auth import get_user_model

from listings.models import Listing
from .models import Payment, EscrowInvoice
from listings.billing import get_listing_fee, check_posting_limit

# Active custom User model namespace
User = get_user_model()

# =========================================================================
# 💵 PART 1: CORE UPFRONT PAYMENT ENGINE & CHECKOUT FLOWS
# =========================================================================

@login_required
def checkout_view(request, listing_id):
    """Displays the listing processing fee invoice using the central billing matrix rules."""
    listing = get_object_or_404(Listing, id=listing_id, owner=request.user)
    
    if listing.is_paid:
        messages.info(request, "This listing has already been processed.")
        return redirect('listings:list')

    # Integrates with your central billing rules matrix
    fee_info = get_listing_fee(listing.category)
    fee = fee_info['fee_usd']
    
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

    return render(request, 'payments/checkout.html', {'listing': listing, 'fee': fee, 'label': fee_info['label']})


@login_required
def payment_gate_view(request, listing_id):
    """Fallback / testing portal wrapper that handles upfront verification routes."""
    listing = get_object_or_404(Listing, id=listing_id, owner=request.user)
    
    if listing.is_paid and listing.is_active:
        return redirect('listings:list')
        
    fee_info = get_listing_fee(listing.category)
    _, current_count, max_allowed = check_posting_limit(request.user, listing.category)
    
    context = {
        'listing': listing,
        'fee_usd': fee_info['fee_usd'],
        'label': fee_info['label'],
        'current_count': current_count,
        'max_allowed': max_allowed,
    }
    
    if request.method == 'POST':
        # Direct simulation pass route for validation testing
        listing.is_paid = True
        listing.is_active = True
        listing.market_tier = 'standard'
        listing.save()
        messages.success(request, f"Payment for {listing.title} processed completely!")
        return redirect('listings:list')

    return render(request, 'listings/payment_gate.html', context)


@login_required
def verify_payment_view(request, payment_id):
    """Simulates/processes live gateway confirmation requests."""
    payment = get_object_or_404(Payment, id=payment_id, owner=request.user)
    listing = payment.listing

    if request.method == 'POST':
        action = request.POST.get('action')
        
        if action == 'confirm_simulation':
            payment.status = 'success'
            payment.save()
            
            listing.is_paid = True
            listing.is_active = True
            listing.save()
            
            messages.success(request, "Payment confirmed successfully! Your asset listing is now live across Zimbabwe.")
            return redirect('listings:list')
            
        elif action == 'fail_simulation':
            payment.status = 'failed'
            payment.save()
            messages.error(request, "Transaction was cancelled or failed. Please try again.")
            return redirect('payments:checkout', listing_id=listing.id)

    return render(request, 'payments/verify.html', {'payment': payment})


# =========================================================================
# 🏗️ PART 2: DIRECT-OWNER LISTING CREATION ENGINE (WITH AUTOMATED LIMITS)
# =========================================================================

@login_required
def create_listing_view(request):
    """Creates an asset entry, intercepting attempts that breach category allowances."""
    if request.method == 'POST':
        category = request.POST.get('category')
        
        # Enforce automated monthly spam-protection threshold limit
        is_allowed, current_count, max_limit = check_posting_limit(request.user, category)
        
        if not is_allowed:
            messages.error(
                request, 
                f"🚫 Account Limit Exceeded: You have already posted your maximum allocation of "
                f"{max_limit} advertisements for this specific category this month. "
                f"Your access will automatically unlock as your older posts clear."
            )
            return redirect('listings:list')
            
        title = request.POST.get('title')
        description = request.POST.get('description')
        price = request.POST.get('price')
        province = request.POST.get('province')
        district = request.POST.get('district')
        
        listing = Listing(
            owner=request.user,
            title=title,
            description=description,
            price=price,
            province=province,
            district=district,
            category=category,
            image1=request.FILES.get('image1'),
            image2=request.FILES.get('image2'),
            image3=request.FILES.get('image3'),
            is_paid=False,     
            is_active=False,   
        )
        listing.save() # Automatic image compression takes place here
        
        return redirect('listings:payment_gate', listing_id=listing.id)
        
    return render(request, 'listings/listing_form.html')


# =========================================================================
# 🛡️ PART 3: PEER-TO-PEER ESCROW TRUST SYSTEM
# =========================================================================

@login_required
def create_invoice_view(request, listing_id):
    """Allows owners to issue milestone-protected escrow invoices to targeted buyers."""
    listing = get_object_or_404(Listing, id=listing_id)
    
    if request.method == 'POST':
        buyer_username = request.POST.get('buyer_username')
        amount_usd = request.POST.get('amount_usd')
        
        try:
            buyer = User.objects.get(username=buyer_username)
            EscrowInvoice.objects.create(
                listing=listing,
                seller=request.user,
                buyer=buyer,
                amount_usd=amount_usd,
                status='pending'
            )
            messages.success(request, f"Invoice issued successfully to @{buyer.username}!")
            return redirect('dashboard:index')
            
        except User.DoesNotExist:
            messages.error(request, f"User @{buyer_username} does not exist. Please verify username structure spelling.")
            
    return render(request, 'payments/create_invoice.html', {'listing': listing})


@login_required
def secure_payment_view(request, invoice_id):
    """Secures buyer deposit funds safely inside the platform holding tank."""
    invoice = get_object_or_404(EscrowInvoice, id=invoice_id)
    
    if invoice.buyer != request.user:
        messages.error(request, "Unauthorized action. This invoice belongs to another buyer profile.")
        return redirect('dashboard:index')
        
    if invoice.status == 'pending':
        invoice.status = 'secured'
        invoice.save()
        messages.success(request, f"Payment for Invoice #{invoice.id} has been secured in escrow. Awaiting physical inspection.")
    else:
        messages.warning(request, "This invoice is not awaiting payment status parameters.")
        
    return redirect('dashboard:index')


@login_required
def release_escrow_view(request, invoice_id):
    """Finalizes trade milestones, moving escrow capital into seller's wallet balance."""
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
        
    return redirect('dashboard:index')