
from utils import generate_nickname

# Mock Data
current_user_email = "me@example.com"
users = [
    {"id": "me@example.com", "name": "My Real Name", "nickname": "SuperMe"},
    {"id": "other1@example.com", "name": "Other Real Name", "nickname": "OtherNick"},
    {"id": "other2@example.com", "name": "No Nick Name", "nickname": None},
]

print("--- Testing Ranking Display Logic ---")

for user in users:
    user_display = user.copy()
    display_name = ""
    
    if current_user_email and user.get('id') != current_user_email:
        # Logic from Ranking Page
        display_name = user.get('nickname') or generate_nickname(user.get('id', 'unknown'))
        print(f"User: {user['id']} | Is Me? NO | Has Nick? {bool(user.get('nickname'))} -> Display: {display_name}")
    else:
        # Logic from Ranking Page
        if user.get('nickname'):
             display_name = f"{user['nickname']} ({user['name']})"
        else:
             display_name = user['name']
        print(f"User: {user['id']} | Is Me? YES | Has Nick? {bool(user.get('nickname'))} -> Display: {display_name}")

# Expected:
# me@example.com -> SuperMe (My Real Name)
# other1@example.com -> OtherNick
# other2@example.com -> [Generated Nickname]
