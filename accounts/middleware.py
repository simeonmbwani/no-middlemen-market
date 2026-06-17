from django.shortcuts import redirect
from django.contrib import messages
from django.urls import reverse

class AntiMiddlemanProtectionMiddleware:
    """
    Automated marketplace protection guard.
    Blocks unverified or banned users from accessing asset creation flows.
    """
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        # Allow background processes and unauthenticated users to pass naturally
        if not request.user.is_authenticated:
            return self.get_response(request)

        # Dynamic URL detection path strings
        current_url_name = request.resolver_match.url_name if request.resolver_match else None
        
        # Target route check parameters: Intercept asset listing uploads or edit paths
        target_creation_routes = ['create', 'listing_create', 'add_listing']
        
        if current_url_name in target_creation_routes:
            
            # Rule A: Enforce absolute blacklisting restriction status parameters
            if getattr(request.user, 'is_banned', False):
                messages.error(request, "Access Denied. Your account has been suspended for broker profile behavior.")
                return redirect('dashboard:index')

            # Rule B: Intercept unverified owners and reroute them to the KYC upload page
            if not getattr(request.user, 'is_verified_owner', False):
                messages.warning(
                    request, 
                    "Account Verification Required. Please upload your National ID card before listing assets."
                )
                return redirect('accounts:verify_identity')

        return self.get_response(request)