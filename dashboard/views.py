from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.contrib.auth import get_user_model
from django.db.models import Q, Max, Count

# Core Application Model Imports
from listings.models import Listing
from payments.models import Payment, EscrowInvoice
from messaging.models import MessageInquiry 

@login_required
def user_dashboard_view(request):
    """
    Dynamically aggregates inventory tracking metrics, text negotiations,
    and P2P escrow transaction status invoices for the active account context.
    Supports dynamic mobile app tab switching via query strings.
    """
    user = request.user
    User = get_user_model()
    
    # 🚨 CAPTURE THE ACTIVE NAVIGATION TAB (Defaults to 'inventory' if not specified)
    active_tab = request.GET.get('tab', 'inventory')

    # 1. Core Asset Inventory Datasets & Metrics
    user_listings = Listing.objects.filter(owner=user)
    total_count = user_listings.count()
    active_count = user_listings.filter(is_active=True, is_paid=True).count()
    expired_count = user_listings.filter(is_active=False).count()
    
    # 2. Inbound Client Direct Text Inquiries (Used on default summary view)
    inquiries = MessageInquiry.objects.filter(listing__owner=user).order_by('-created_at')[:5]
    
    # Automatically mark unread inquiries as read on layout initialization
    MessageInquiry.objects.filter(listing__owner=user, is_read=False).update(is_read=True)

    # 3. Escrow Invoice Tracking Pipelines
    my_sales = EscrowInvoice.objects.filter(seller=user)
    my_purchases = EscrowInvoice.objects.filter(buyer=user)
    pending_count = my_purchases.filter(status='pending').count()

    # 4. Standard Gateway Financial Transactions Statements Audit Logs
    payments = Payment.objects.filter(owner=user).order_by('-created_at')[:5]

    # 💬 5. GROUPED P2P CHAT ENGINE LOGIC (Feeds active_chats straight to template)
    active_chats = []
    messages_list = []
    partner = None

    if active_tab == 'messages':
        # Find all distinct users you have interacted with via listings
        interacted_user_ids = MessageInquiry.objects.filter(
            Q(listing__owner=user) | Q(sender=user)
        ).values_list('sender_id', 'listing__owner_id')

        # Clean duplicates out into a single flat unique ID set
        unique_partners = set()
        for s_id, o_id in interacted_user_ids:
            if s_id and s_id != user.id: unique_partners.add(s_id)
            if o_id and o_id != user.id: unique_partners.add(o_id)

        # Build dynamic payload dictionaries that match the dashboard template keys
        for p_id in unique_partners:
            try:
                p_user = User.objects.get(id=p_id)
                # Fetch the absolute newest message for this connection row
                last_msg = MessageInquiry.objects.filter(
                    (Q(sender=user) & Q(listing__owner=p_user)) |
                    (Q(sender=p_user) & Q(listing__owner=user))
                ).order_by('-created_at').first()

                if last_msg:
                    unread_count = MessageInquiry.objects.filter(
                        sender=p_user, listing__owner=user, is_read=False
                    ).count()

                    active_chats.append({
                        'id': p_user.id, # Tracks context tab filtering query targets
                        'participant': p_user,
                        'last_message_text': last_msg.description, # Pulls description text row string safely
                        'last_message_sender': last_msg.sender,
                        'unread_messages_count': unread_count,
                        'updated_at': last_msg.created_at,
                    })
            except User.DoesNotExist:
                continue

        # Sort whole active inbox stack so freshest messages always show first
        active_chats.sort(key=lambda x: x['updated_at'], reverse=True)

        # Single Chat Conversation Panel Log View
        start_chat_with = request.GET.get('chat_id') or request.GET.get('start_chat_with')
        if start_chat_with:
            messages_list = MessageInquiry.objects.filter(
                (Q(sender=user) & Q(listing__owner_id=start_chat_with)) |
                (Q(sender_id=start_chat_with) & Q(listing__owner=user))
            ).order_by('created_at')
            
            try:
                partner = User.objects.get(id=start_chat_with)
            except User.DoesNotExist:
                pass

    # 6. Context Matrix Bundle Matching Index Keys Complete Mapping
    context = {
        'active_tab': active_tab,
        'user_listings': user_listings,
        'total_count': total_count,
        'active_count': active_count,
        'expired_count': expired_count,
        'unpaid_bills_count': pending_count,
        'inquiries': inquiries,
        'my_sales': my_sales,
        'my_purchases': my_purchases,
        'payments': payments,
        'active_chats': active_chats, # 👈 Delivers data cleanly directly to your template loop!
        'messages_list': messages_list,
        'partner': partner,
    }
    
    return render(request, 'dashboard/index.html', context)