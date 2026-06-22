#!/usr/bin/env python
import os
import sys
import django
from pathlib import Path

# Set up Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
sys.path.insert(0, 'd:\\village_bid_approval')
django.setup()

from django.core.management import call_command
from django.db import connection

print("=" * 60)
print("VILLAGEBID DATABASE RESET SCRIPT")
print("=" * 60)

# Step 1: Delete old database
db_path = Path('d:\\village_bid_approval\\db.sqlite3')
if db_path.exists():
    print("\n[1/4] Deleting old database...")
    try:
        db_path.unlink()
        print("✓ Database deleted")
    except Exception as e:
        print(f"✗ Error deleting database: {e}")
        print("  (You may need to close Django/VS Code and try again)")
        sys.exit(1)
else:
    print("\n[1/4] No old database found - skipping")

# Step 2: Clean up migration files (keep only __init__.py)
print("\n[2/4] Cleaning migration files...")
apps = [
    'accounts', 'auctions', 'bids', 'payments', 'products', 'reviews',
    'dashboard', 'notifications', 'categories', 'favorites', 'messages_app', 'adminpanel'
]

for app in apps:
    mig_dir = Path(f'd:\\village_bid_approval\\{app}\\migrations')
    if mig_dir.exists():
        for file in mig_dir.glob('*.py'):
            if file.name != '__init__.py':
                try:
                    file.unlink()
                except:
                    pass

print("✓ Migration files cleaned")

# Step 3: Create fresh migrations
print("\n[3/4] Creating fresh migrations...")
try:
    call_command('makemigrations', verbosity=1)
    print("✓ Migrations created")
except Exception as e:
    print(f"✗ Error creating migrations: {e}")
    sys.exit(1)

# Step 4: Apply migrations
print("\n[4/4] Applying migrations...")
try:
    call_command('migrate', verbosity=1)
    print("✓ Migrations applied")
except Exception as e:
    print(f"✗ Error applying migrations: {e}")
    sys.exit(1)

print("\n" + "=" * 60)
print("SUCCESS! Database is ready.")
print("=" * 60)
print("\nNext steps:")
print("1. Run: python manage.py createsuperuser")
print("2. Run: python manage.py runserver")
print("3. Visit: http://127.0.0.1:8000/")
