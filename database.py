import psycopg2
from psycopg2 import extras
from datetime import datetime
import hashlib
import os

# --- Configuration ---
# Is URL ko aapne Supabase/Neon se replace karna hai
DB_URL = "postgresql://postgres:your_password@your_host:5432/postgres"

def get_connection():
    """Establishes a connection to the PostgreSQL database."""
    try:
        conn = psycopg2.connect(DB_URL)
        return conn
    except Exception as e:
        print(f"[CRITICAL] Connection failed: {e}")
        return None

def setup_db():
    """Initializes PostgreSQL schema with Blockchain & Financial constraints."""
    conn = get_connection()
    if not conn: return
    
    try:
        cur = conn.cursor()
        
        # 1. User Registry Table
        cur.execute('''CREATE TABLE IF NOT EXISTS users (
            u_id SERIAL PRIMARY KEY, 
            name VARCHAR(255) NOT NULL, 
            monthly_budget DECIMAL(15, 2) DEFAULT 0.0,
            remaining_budget DECIMAL(15, 2) DEFAULT 0.0,
            daily_limit DECIMAL(15, 2) DEFAULT 0.0, 
            spent_today DECIMAL(15, 2) DEFAULT 0.0, 
            face_encoding TEXT,
            last_reset_date TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
        )''')
        
        # 2. Immutable Ledger Table (Blockchain)
        cur.execute('''CREATE TABLE IF NOT EXISTS transactions (
            id SERIAL PRIMARY KEY, 
            user_id INTEGER REFERENCES users(u_id), 
            amount DECIMAL(15, 2), 
            type VARCHAR(50), 
            date TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
            tx_hash VARCHAR(64) UNIQUE,
            prev_hash VARCHAR(64)
        )''')

        # 3. Admin Vault
        cur.execute('''CREATE TABLE IF NOT EXISTS admin_vault (
            id INTEGER PRIMARY KEY, 
            total_refunded_assets DECIMAL(15, 2) DEFAULT 0.0,
            last_reconciliation TIMESTAMP WITH TIME ZONE
        )''')
        
        cur.execute("INSERT INTO admin_vault (id, total_refunded_assets) VALUES (1, 0.0) ON CONFLICT (id) DO NOTHING")
        
        conn.commit()
        print("[INFO] PostgreSQL Enterprise Engine Synchronized.")
    except Exception as e:
        print(f"[CRITICAL] Database setup failed: {e}")
    finally:
        cur.close()
        conn.close()

# --- Core Blockchain Logic ---

def generate_tx_hash(u_id, amount, date, tx_type, prev_hash="00000000"):
    block_string = f"{u_id}-{amount}-{date}-{tx_type}-{prev_hash}"
    return hashlib.sha256(block_string.encode()).hexdigest()

# --- Business Logic Functions ---

def add_user(name, m_budget, d_limit):
    """Registers a new user and creates an allocation block."""
    conn = get_connection()
    if not conn: return
    cur = conn.cursor()
    
    try:
        # Insert user and get the serial u_id
        cur.execute("""INSERT INTO users (name, monthly_budget, remaining_budget, daily_limit, spent_today) 
                       VALUES (%s, %s, %s, %s, %s) RETURNING u_id""", 
                    (name, m_budget, m_budget, d_limit, 0.0))
        u_id = cur.fetchone()[0]
        
        # Genesis hash logic
        cur.execute("SELECT tx_hash FROM transactions ORDER BY id DESC LIMIT 1")
        last_row = cur.fetchone()
        prev_hash = last_row[0] if last_row else "00000000"
        
        now = datetime.now()
        g_hash = generate_tx_hash(u_id, m_budget, now, "ALLOCATION", prev_hash)
        
        cur.execute("INSERT INTO transactions (user_id, amount, type, tx_hash, prev_hash) VALUES (%s, %s, %s, %s, %s)", 
                    (u_id, m_budget, "ALLOCATION", g_hash, prev_hash))
        
        conn.commit()
        print(f"[SUCCESS] Entity {name} committed with ID: {u_id}")
        return u_id
    except Exception as e:
        print(f"[ERROR] Registration Failed: {e}")
        conn.rollback()
    finally:
        cur.close()
        conn.close()

def process_payment(u_id, amount):
    """PostgreSQL Atomic Transaction for Payments."""
    conn = get_connection()
    if not conn: return False
    cur = conn.cursor(cursor_factory=extras.RealDictCursor)
    
    try:
        cur.execute("SELECT remaining_budget, daily_limit, spent_today FROM users WHERE u_id = %s FOR UPDATE", (u_id,))
        user = cur.fetchone()
        
        if not user or (user['spent_today'] + amount > user['daily_limit']) or (amount > user['remaining_budget']):
            print("[DENIED] Limits exceeded or User not found.")
            return False

        cur.execute("SELECT tx_hash FROM transactions ORDER BY id DESC LIMIT 1")
        prev_hash = cur.fetchone()['tx_hash'] if cur.rowcount > 0 else "00000000"
        new_hash = generate_tx_hash(u_id, amount, datetime.now(), "PAYMENT", prev_hash)

        # Update and Log
        cur.execute("UPDATE users SET remaining_budget = remaining_budget - %s, spent_today = spent_today + %s WHERE u_id = %s", 
                    (amount, amount, u_id))
        cur.execute("INSERT INTO transactions (user_id, amount, type, tx_hash, prev_hash) VALUES (%s, %s, %s, %s, %s)", 
                    (u_id, amount, "PAYMENT", new_hash, prev_hash))
        
        conn.commit()
        return True
    except Exception as e:
        print(f"[SYSTEM ERROR] Payment Failed: {e}")
        conn.rollback()
        return False
    finally:
        cur.close()
        conn.close()

if __name__ == "__main__":
    setup_db()