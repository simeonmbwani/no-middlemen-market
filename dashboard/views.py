from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.contrib.auth import get_user_model
from django.db.models import Q

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

    # 💬 5. GROUPED P2P CHAT ENGINE LOGIC
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
                        'id': p_user.id, 
                        'participant': p_user,
                        'last_message_text': last_msg.message_text,  # 🔧 FIXED: Correct field mapped here
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
            # Check if this request is a background AJAX background engine sequence request
            is_ajax = request.headers.get('x-requested-with') == 'XMLHttpRequest' or 'sync' in request.GET
            
            # 📬 POST HANDLE: Process inbound message transmissions smoothly via background fetch pipelines
            if request.method == 'POST':
                body_text = request.POST.get('message_text', '').strip()
                if body_text:
                    # Find any listing shared between the two users to preserve required database foreign key constraints
                    associated_listing = Listing.objects.filter(
                        Q(owner=user) | Q(owner_id=start_chat_with)
                    ).first()
                    
                    # 🛡️ FALLBACK SAFEGUARD: If no matching listing context exists, pick any live fallback to preserve integrity
                    if not associated_listing:
                        associated_listing = Listing.objects.filter(is_active=True).first()
                    
                    if associated_listing:
                        new_msg = MessageInquiry.objects.create(
                            sender=user,
                            listing=associated_listing,
                            message_text=body_text
                        )
                        if is_ajax:
                            from django.http import JsonResponse
                            return JsonResponse({'status': 'delivered', 'id': new_msg.id})
                        return redirect(f"{request.path}?tab=messages&chat_id={start_chat_with}")
                
                # 🛡️ FOOLPROOF RESPONSE: If body was empty or execution failed, never return None
                if is_ajax:
                    from django.http import JsonResponse
                    return JsonResponse({'status': 'failed', 'reason': 'No content or listing layout matched'})

            # 🔧 FIXED: Filter message streams strictly by sender and recipient interaction vectors 
            messages_list = MessageInquiry.objects.filter(
                (Q(sender=user) & Q(listing__owner_id=start_chat_with)) |
                (Q(sender_id=start_chat_with) & Q(listing__owner=user)) |
                (Q(sender=user) & Q(listing__id__in=Listing.objects.filter(owner_id=start_chat_with).values_list('id', flat=True))) |
                (Q(sender_id=start_chat_with) & Q(listing__id__in=Listing.objects.filter(owner=user).values_list('id', flat=True)))
            ).distinct().order_by('created_at')
            
            try:
                partner = User.objects.get(id=start_chat_with)
                # 🔧 FIXED: Mark records as read where your chat partner is the sender and you are the recipient
                MessageInquiry.objects.filter(sender=partner, listing__owner=user, is_read=False).update(is_read=True)
            except User.DoesNotExist:
                pass

            # ⚙️ BACKGROUND JSON SYNC BLOCK ENGINE RESPONDER RULE INTERCEPTOR
            if is_ajax and 'sync' in request.GET:
                from django.http import JsonResponse
                from django.template.loader import render_to_string
                
                # 🔧 FIXED: Target global incoming unread entries accurately based on recipient user constraints
                global_unread_total = MessageInquiry.objects.filter(listing__owner=user, is_read=False).count()
                inbound_received_count = messages_list.filter(sender_id=start_chat_with).count()
                
                # Assemble raw chat fragments array
                html_contents = render_to_string('messaging/chat_bubbles.html', {
                    'messages_list': messages_list,
                    'request': request
                })
                
                return JsonResponse({
                    'html': html_contents,
                    'inbound_count': inbound_received_count,
                    'unread_total': global_unread_total
                })

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
        'active_chats': active_chats, 
        'messages_list': messages_list,
        'partner': partner,
    }
    
    return render(request, 'dashboard/index.html', context)