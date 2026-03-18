import sqlite3

def show_all_users():
    # Database se connect karein
    conn = sqlite3.connect("facesecure.db")
    cursor = conn.cursor()
    
    # Saara data nikalien
    cursor.execute("SELECT id, name, limit_amt, spent FROM users")
    rows = cursor.fetchall()
    
    print("\n--- FACESECURE DATABASE REPORT ---")
    print(f"{'ID':<10} | {'NAME':<15} | {'LIMIT':<10} | {'SPENT':<10}")
    print("-" * 50)
    
    for row in rows:
        u_id, name, limit, spent = row
        print(f"{u_id:<10} | {name:<15} | {limit:<10} | {spent:<10}")
    
    conn.close()

if __name__ == "__main__":
    show_all_users()