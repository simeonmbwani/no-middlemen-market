from django.shortcuts import render
from django.contrib.auth.decorators import login_required

# Core Application Model Imports
from listings.models import Listing
from payments.models import Payment, EscrowInvoice
from messaging.models import MessageInquiry 

@login_required
def user_dashboard_view(request):
    """
    Dynamically aggregates inventory tracking metrics, text negotiations,
    and P2P escrow transaction status invoices for the active account context.
    """
    user = request.user

    # 1. Core Asset Inventory Datasets & Metrics
    listings = Listing.objects.filter(owner=user)
    total_count = listings.count()
    active_count = listings.filter(is_active=True, is_paid=True).count()
    expired_count = listings.filter(is_active=False).count()
    
    # 2. Inbound Client Direct Text Inquiries
    inquiries = MessageInquiry.objects.filter(listing__owner=user).order_by('-created_at')[:5]
    
    # 🔧 NEW AUTO-UPDATE: Automatically marks fetched unread inquiries as read upon view rendering
    MessageInquiry.objects.filter(listing__owner=user, is_read=False).update(is_read=True)

    # 3. Escrow Invoice Tracking Pipelines
    my_sales = EscrowInvoice.objects.filter(seller=user)
    my_purchases = EscrowInvoice.objects.filter(buyer=user)
    
    # Unpaid bills metric counter based on pending inbound purchase invoices
    pending_count = my_purchases.filter(status='pending').count()

    # 4. Standard Gateway Financial Transactions Statements Audit Logs
    # 🔧 FIXED: Changed 'user=user' to 'owner=user' to match your model layout fields
    payments = Payment.objects.filter(owner=user).order_by('-created_at')[:5]

    # 5. Context Matrix Bundle
    context = {
        'listings': listings,
        'total_count': total_count,
        'active_count': active_count,
        'expired_count': expired_count,
        'pending_count': pending_count,
        'inquiries': inquiries,
        'my_sales': my_sales,
        'my_purchases': my_purchases,
        'payments': payments,
    }
    
    return render(request, 'dashboard/index.html', context)