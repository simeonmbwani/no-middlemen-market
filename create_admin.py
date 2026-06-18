import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from django.contrib.auth import get_user_model

User = get_user_model()

username = 'simeonmbwani'
email = 'simeonmbwani@gmail.com'
password = '@A1n2d3y4' # ⚠️ Set your actual password here

if not User.objects.filter(username=username).exists():
    print(f"🚀 Creating production superuser profile for @{username}...")
    
    # 🔧 SETUP FOR CUSTOM MODEL PROPERTIES
    admin_user = User.objects.create_superuser(
        username=username, 
        email=email, 
        password=password
    )
    
    # If your Custom User model requires verification flags to pass, explicitly flag them here:
    if hasattr(admin_user, 'is_verified_owner'):
        admin_user.is_verified_owner = True
    if hasattr(admin_user, 'is_staff'):
        admin_user.is_staff = True
        
    admin_user.save()
    print("✅ Superuser initialized and verified in production database clusters successfully!")
else:
    print(f"ℹ️ Superuser account @{username} already verified in database clusters.")