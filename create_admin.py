import os
import django

# Initialize the Django ecosystem settings layer
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from django.contrib.auth import get_user_model
from django.contrib.auth.hashers import make_password

User = get_user_model()

def force_inject_clean_admin():
    username = "simeonadmin"
    email = "simeonmbwani@gmail.com"
    password = "@A1n2d3y4" # 🔏 Change this to your preferred password string

    # 1. Purge any old, broken or mismatched admin records under this username
    if User.objects.filter(username=username).exists():
        print(f"🗑️ Found an existing record for @{username}. Purging to prevent field corruption...")
        User.objects.filter(username=username).delete()

    print(f"🚀 Injecting cleanly configured superuser record for @{username}...")
    
    # 2. Build the record using a direct query to bypass custom UserManager restrictions
    admin_user = User(
        username=username,
        email=email,
        password=make_password(password), # 🔏 Explicitly hashes the password text cleanly
        full_name="Simeon Mbwani",
        phone_number=None,   # Set to None/Null to avoid validator flags
        national_id=None,    # Set to None/Null to avoid unique constraint collisions
        is_staff=True,       # 👑 Required to view Django admin suites
        is_superuser=True,   # 👑 Grants universal permissions override
        is_active=True,      # 🟢 Ensures the account isn't locked out by default
        is_verified_owner=True
    )
    
    # Save the record directly to your production database instance
    admin_user.save()
    print("🟢 Master Superuser successfully injected into your production database!")

if __name__ == '__main__':
    force_inject_clean_admin()