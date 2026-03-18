from database import update_spent

# Hum manually ID 101 ke $10 kat-te hain
u_id = 101
amount = 10

print(f"Testing: Deducting ${amount} from ID {u_id}...")
update_spent(u_id, amount)
print("Done! Now run check_balance.py to see the magic.")