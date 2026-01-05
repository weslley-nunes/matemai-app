
# import streamlit as st
# from database import get_database
from utils import generate_nickname

# Mock session state if needed (though we are running this as a script, we might need to mock st.session_state if utils depends on it heavily, but generate_nickname shouldn't)
# Actually, let's just test the functions directly.

# print("--- Testing Database Leaderboard Update ---")
# db = get_database()
# leaderboard = db.get_leaderboard(limit=5)
# print(f"Leaderboard entries found: {len(leaderboard)}")
# if leaderboard:
#     first_entry = leaderboard[0]
#     print(f"First entry keys: {first_entry.keys()}")
#     if 'id' in first_entry:
#         print("SUCCESS: 'id' field is present in leaderboard entry.")
#         print(f"Sample ID: {first_entry['id']}")
#     else:
#         print("FAILURE: 'id' field is MISSING.")
# else:
#     print("WARNING: Leaderboard is empty, cannot verify 'id' field.")

print("\n--- Testing Nickname Generation ---")
test_emails = [
    "student.a@example.com",
    "student.b@example.com",
    "teacher@school.org",
    "random.user@gmail.com"
]

for email in test_emails:
    nickname = generate_nickname(email)
    print(f"Email: {email} -> Nickname: {nickname}")
    
    # Verify determinism
    nickname2 = generate_nickname(email)
    if nickname == nickname2:
        print(f"  Determinism Check: PASS")
    else:
        print(f"  Determinism Check: FAIL ({nickname} != {nickname2})")

