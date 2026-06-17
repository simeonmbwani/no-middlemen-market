from decimal import Decimal
from django import template

register = template.Library()

@register.filter(name='to_zig')
def to_zig(usd_value, zig_rate):
    """
    Dynamically converts a USD decimal price directly into a ZiG valuation.
    Usage in HTML: {{ listing.price|to_zig:ZIG_MID_RATE }}
    """
    try:
        # Safeguard conversion parameters against empty data strings cleanly
        usd = Decimal(str(usd_value))
        rate = Decimal(str(zig_rate))
        converted = usd * rate
        # Format with thousand separators and two decimal points
        return f"{converted:,.2f}"
    except (ValueError, TypeError, ZeroDivisionError):
        return "0.00"