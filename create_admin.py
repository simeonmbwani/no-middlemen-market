import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from django.contrib.auth import get_user_model

User = get_user_model()

# 🔧 AUTOMATION GATEWAY: Automatically ensures your admin profile exists in PostgreSQL safely
username = 'simeonmbwani'
email = 'simeonmbwani@gmail.com'
password = 'YourSecurePassword123!' # <-- Change this to your actual private secure password!

if not User.objects.filter(username=username).exists():
    print(f"🚀 Creating production superuser profile for @{username}...")
    User.objects.create_superuser(username=username, email=email, password=password)
    print("✅ Superuser created successfully!")
else:
    print(f"ℹ️ Superuser account @{username} already verified in database clusters.")