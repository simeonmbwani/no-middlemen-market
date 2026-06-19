import os
import django

# Initialize Django environment settings
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from django.contrib.auth import get_user_model
from django.contrib.auth.hashers import make_password

User = get_user_model()

def register_brand_new_superuser():
    # 🔏 BRAND NEW ACCOUNT PARAMETERS TO BYPASS CACHED LOGINS
    username = "simeonmbwani"
    email = "tavongamlauzi@gmail.com"
    password = "@A1n2d3y4" # 👈 Change this to your preferred password string

    # Clean out any old attempts for this specific user
    if User.objects.filter(username=username).exists():
        User.objects.filter(username=username).delete()

    print(f"🚀 Injecting brand-new, valid superuser record for @{username}...")
    
    # Create the user directly by defining all custom model fields to prevent validation errors
    admin_user = User(
        username=username,
        email=email,
        password=make_password(password),
        full_name="System Administrator",
        province="Mashonaland West",  # Default location text to satisfy model fields
        district="Chinhoyi",         # Default location text to satisfy model fields
        is_staff=True,
        is_superuser=True,
        is_active=True,
        is_verified_owner=True
    )
    
    admin_user.save()
    print(f"🟢 Successfully created completely fresh superuser: @{username}")

if __name__ == '__main__':
    register_brand_new_superuser()