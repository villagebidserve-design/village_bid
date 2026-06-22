#!/usr/bin/env python
import os
import sys
import django
from pathlib import Path

# Set up Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
sys.path.insert(0, 'd:\\village_bid_approval')
django.setup()

from django.contrib.auth import get_user_model

User = get_user_model()

print("Creating superuser...")

# Check if superuser already exists
if User.objects.filter(username='admin').exists():
    print("Superuser 'admin' already exists!")
else:
    # Create superuser
    User.objects.create_superuser(
        username='admin',
        email='admin@villagebid.com',
        password='admin123'
    )
    print("✓ Superuser created!")
    print("\nLogin credentials:")
    print("  Username: admin")
    print("  Email: admin@villagebid.com")
    print("  Password: admin123")
    print("\nVisit: http://127.0.0.1:8000/admin/")

print("\nDone! You can now start the server:")
print("  python manage.py runserver")
