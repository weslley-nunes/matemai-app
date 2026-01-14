import urllib.request
import urllib.error
from avatar_assets import AVATAR_ASSETS

# Base URL for v9
BASE_URL = "https://api.dicebear.com/9.x/avataaars/svg?seed=Felix"

def check_asset(category, asset_id):
    url = f"{BASE_URL}&{category}={asset_id}"
    try:
        with urllib.request.urlopen(url) as response:
            if response.getcode() == 200:
                return True, url
    except urllib.error.HTTPError as e:
        return False, f"{e.code} - {url}"
    except Exception as e:
        return False, f"{e} - {url}"
    return False, f"Unknown - {url}"

print("--- Verifying Avatar Assets ---")
broken_assets = []

for category, items in AVATAR_ASSETS.items():
    print(f"\nChecking Category: {category}")
    for item in items:
        asset_id = item['id']
        is_valid, msg = check_asset(category, asset_id)
        if is_valid:
            print(f"✅ {asset_id}")
        else:
            print(f"❌ {asset_id} [BROKEN]")
            broken_assets.append(f"{category}: {asset_id}")

print("\n--- Summary of Broken Assets ---")
if broken_assets:
    for broken in broken_assets:
        print(broken)
else:
    print("All assets are valid!")
