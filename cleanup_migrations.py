import os
import shutil

# List of apps with migrations
apps = [
    'd:\\village_bid_approval\\accounts\\migrations',
    'd:\\village_bid_approval\\auctions\\migrations',
    'd:\\village_bid_approval\\bids\\migrations',
    'd:\\village_bid_approval\\payments\\migrations',
    'd:\\village_bid_approval\\products\\migrations',
    'd:\\village_bid_approval\\reviews\\migrations',
    'd:\\village_bid_approval\\dashboard\\migrations',
    'd:\\village_bid_approval\\notifications\\migrations',
    'd:\\village_bid_approval\\categories\\migrations',
    'd:\\village_bid_approval\\favorites\\migrations',
    'd:\\village_bid_approval\\messages_app\\migrations',
    'd:\\village_bid_approval\\adminpanel\\migrations',
]

print("Cleaning up migrations...\n")

for mig_dir in apps:
    if os.path.exists(mig_dir):
        app_name = mig_dir.split('\\')[-2]
        # Keep only __init__.py
        for file in os.listdir(mig_dir):
            if file != '__init__.py' and file.endswith('.py'):
                filepath = os.path.join(mig_dir, file)
                try:
                    os.remove(filepath)
                    print(f"Removed: {app_name}/{file}")
                except Exception as e:
                    print(f"Error removing {app_name}/{file}: {e}")

print("\n✓ Migration files cleaned up")
