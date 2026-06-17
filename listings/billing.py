# listings/billing.py
from django.utils import timezone
from datetime import timedelta
from .models import Listing

# 💵 Upfront pricing structure mapped by asset category token
PRICING_MATRIX = {
    'room': {'fee_usd': 1.50, 'max_per_month': 10, 'label': 'Room Advertisement'},
    'student_accom': {'fee_usd': 1.50, 'max_per_month': 10, 'label': 'Student Accommodation'},
    'cottage': {'fee_usd': 2.50, 'max_per_month': 5, 'label': 'Cottage'},
    'flat': {'fee_usd': 3.00, 'max_per_month': 5, 'label': 'Apartment / Flat'},
    'house': {'fee_usd': 5.00, 'max_per_month': 3, 'label': 'House / Full Property'},
    'res_stand': {'fee_usd': 5.00, 'max_per_month': 3, 'label': 'Residential Stand'},
    'comm_stand': {'fee_usd': 5.00, 'max_per_month': 3, 'label': 'Commercial Stand'},
    'land_plot': {'fee_usd': 5.00, 'max_per_month': 3, 'label': 'Land / Plot'},
    # Heavy assets tier
    'excavator': {'fee_usd': 10.00, 'max_per_month': 2, 'label': 'Excavator Heavy Rental'},
    'truck': {'fee_usd': 5.00, 'max_per_month': 4, 'label': 'Commercial Truck'},
}

DEFAULT_RULE = {'fee_usd': 2.00, 'max_per_month': 5, 'label': 'Standard Listing'}

def check_posting_limit(user, category):
    """
    Returns (is_allowed, current_count, max_allowed)
    Checks if the user has exceeded their monthly allocation limit for a specific category.
    """
    rule = PRICING_MATRIX.get(category, DEFAULT_RULE)
    limit = rule['max_per_month']
    
    # Calculate exactly 30 days ago
    thirty_days_ago = timezone.now() - timedelta(days=30)
    
    # Count how many total listings this user posted in this category over the month
    current_count = Listing.objects.filter(
        owner=user,
        category=category,
        created_at__gte=thirty_days_ago
    ).count()
    
    if current_count >= limit:
        return False, current_count, limit
    return True, current_count, limit

def get_listing_fee(category):
    """Returns the fee configuration dictionary for a category."""
    return PRICING_MATRIX.get(category, DEFAULT_RULE)