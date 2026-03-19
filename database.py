import sqlite3
from datetime import datetime
import hashlib

# Configuration for Global Database
DB_NAME = "facesecure.db"

def setup_db():
    """
    Initializes the FaceSecure relational database and establishes 
    the identity and cryptographic transaction schemas.
    """
    try:
        conn = sqlite3.connect(DB_NAME)
        cursor = conn.cursor()
        
        # User Registry: Manages biometric identities and credit boundaries
        cursor.execute('''CREATE TABLE IF NOT EXISTS users 
                          (u_id INTEGER PRIMARY KEY, 
                           name TEXT, 
                           daily_limit REAL, 
                           spent REAL DEFAULT 0.0, 
                           face_encoding BLOB,
                           last_reset_date TEXT)''')
        
        # Immutable Ledger: Stores transaction blocks with cryptographic hashes
        cursor.execute('''CREATE TABLE IF NOT EXISTS transactions 
                          (id INTEGER PRIMARY KEY AUTOINCREMENT, 
                           user_id INTEGER, 
                           amount REAL, 
                           date TEXT,
                           tx_hash TEXT)''')
        
        conn.commit()
        conn.close()
        print("[INFO] Database Engine Synchronized.")
    except Exception as e:
        print(f"[CRITICAL] Database setup failed: {e}")

def generate_tx_hash(u_id, amount, date, prev_hash="0"):
    """
    Generates a unique SHA-256 cryptographic signature for a transaction block.
    """
    block_string = f"{u_id}-{amount}-{date}-{prev_hash}"
    return hashlib.sha256(block_string.encode()).hexdigest()

def can_user_pay(u_id, amount):
    """
    Verifies if the requested transaction adheres to the user's credit limits.
    """
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute("SELECT daily_limit, spent FROM users WHERE u_id=?", (u_id,))
    user = cursor.fetchone()
    conn.close()
    
    if user:
        limit, spent = user[0], user[1]
        if (spent + amount) <= limit:
            return True, "Authorization Successful"
        else:
            remaining = limit - spent
            return False, f"Limit Exceeded! Remaining Balance: ${remaining:.2f}"
    return False, "Identity Not Found"

def get_all_users():
    """Retrieves all registered user profiles for the administrative dashboard."""
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.format("SELECT u_id, name, daily_limit, spent FROM users")
    data = cursor.fetchall()
    conn.close()
    return data

def add_user(u_id, name, limit):
    """Registers a new identity with a daily credit threshold."""
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    today = datetime.now().strftime('%Y-%m-%d')
    try:
        cursor.execute("INSERT OR REPLACE INTO users (u_id, name, daily_limit, spent, last_reset_date) VALUES (?, ?, ?, ?, ?)", 
                        (u_id, name, limit, 0.0, today))
        conn.commit()
        print(f"[SUCCESS] Identity {name} enrolled into the secure vault.")
    except Exception as e:
        print(f"[ERROR] Enrollment failed: {e}")
    finally:
        conn.close()

def update_spent(u_id, amount):
    """
    Updates the expenditure record and links the transaction to the blockchain.
    """
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    
    try:
        # Step 1: Retrieve the cryptographic hash of the preceding block
        cursor.execute("SELECT tx_hash FROM transactions ORDER BY id DESC LIMIT 1")
        last_row = cursor.fetchone()
        prev_hash = last_row[0] if last_row else "00000000"

        # Step 2: Generate current block hash for chain continuity
        new_hash = generate_tx_hash(u_id, amount, timestamp, prev_hash)

        # Step 3: Atomic update of user credit status
        cursor.execute("UPDATE users SET spent = spent + ? WHERE u_id = ?", (amount, u_id))
        
        # Step 4: Record block into the immutable ledger
        cursor.execute("INSERT INTO transactions (user_id, amount, date, tx_hash) VALUES (?, ?, ?, ?)", 
                        (u_id, amount, timestamp, new_hash))
        
        conn.commit()
        print(f"[BLOCKCHAIN] Block Verified. Hash: {new_hash[:10]}...")
        return True
    except Exception as e:
        print(f"[CRITICAL] Ledger update protocol failed: {e}")
        return False
    finally:
        conn.close()

# Auto-initialize database on import
setup_db()