import sqlite3
import pickle
from datetime import datetime
import hashlib  # <--- NEW: Hashing

DB_NAME = "facesecure.db"

def setup_db():
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    # Users Table
    cursor.execute('''CREATE TABLE IF NOT EXISTS users 
                      (u_id INTEGER PRIMARY KEY, 
                       name TEXT, 
                       daily_limit REAL, 
                       spent REAL DEFAULT 0.0, 
                       face_encoding BLOB,
                       last_reset_date TEXT)''')
    
    # Transactions Table (Updated with Hash column)
    cursor.execute('''CREATE TABLE IF NOT EXISTS transactions 
                      (id INTEGER PRIMARY KEY AUTOINCREMENT, 
                       user_id INTEGER, 
                       amount REAL, 
                       date TEXT,
                       tx_hash TEXT)''') # <--- NEW: Blockchain Hash column
    conn.commit()
    conn.close()

# --- NEW: BLOCKCHAIN HASH GENERATOR ---
def generate_tx_hash(u_id, amount, date, prev_hash="0"):
    """Har transaction ka unique SHA-256 hash banata hai"""
    block_string = f"{u_id}-{amount}-{date}-{prev_hash}"
    return hashlib.sha256(block_string.encode()).hexdigest()

def can_user_pay(u_id, amount):
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute("SELECT daily_limit, spent FROM users WHERE u_id=?", (u_id,))
    user = cursor.fetchone()
    conn.close()
    
    if user:
        limit, spent = user[0], user[1]
        if (spent + amount) <= limit:
            return True, "Success"
        else:
            remaining = limit - spent
            return False, f"Limit Exceeded! Remaining: ${remaining:.2f}"
    return False, "User Not Found"

def get_all_users():
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute("SELECT u_id, name, daily_limit, spent FROM users")
    data = cursor.fetchall()
    conn.close()
    return data

def get_monthly_revenue():
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute("SELECT SUM(amount) FROM transactions")
    total = cursor.fetchone()[0]
    conn.close()
    return total if total else 0.0

def add_user(u_id, name, limit):
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    today = datetime.now().strftime('%Y-%m-%d')
    try:
        cursor.execute("INSERT INTO users (u_id, name, daily_limit, spent, last_reset_date) VALUES (?, ?, ?, ?, ?)", 
                        (u_id, name, limit, 0.0, today))
        conn.commit()
        print(f"[SUCCESS] User {name} added to DB.")
    except Exception as e:
        print(f"[ERROR] Add User failed: {e}")
    finally:
        conn.close()

def delete_user(u_id):
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    try:
        cursor.execute("DELETE FROM users WHERE u_id = ?", (u_id,))
        conn.commit()
        return True
    except Exception as e:
        print(f"Delete failed: {e}")
        return False
    finally:
        conn.close()

# --- TERMINAL KE LIYE FUNCTIONS (Updated with Blockchain Logic) ---
def update_spent(u_id, amount):
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    today = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    
    try:
        # 1. Pichli transaction ka hash uthao (Linking blocks)
        cursor.execute("SELECT tx_hash FROM transactions ORDER BY id DESC LIMIT 1")
        last_row = cursor.fetchone()
        prev_hash = last_row[0] if last_row else "00000000"

        # 2. Is transaction ka naya hash banao
        new_hash = generate_tx_hash(u_id, amount, today, prev_hash)

        # 3. Spent update
        cursor.execute("UPDATE users SET spent = spent + ? WHERE u_id = ?", (amount, u_id))
        
        # 4. Transaction record with HASH
        cursor.execute("INSERT INTO transactions (user_id, amount, date, tx_hash) VALUES (?, ?, ?, ?)", 
                        (u_id, amount, today, new_hash))
        
        conn.commit()
        print(f"[BLOCKCHAIN] Transaction Verified & Linked. Hash: {new_hash[:10]}...")
        return True
    except Exception as e:
        print(f"Update spent failed: {e}")
        return False
    finally:
        conn.close()

setup_db()