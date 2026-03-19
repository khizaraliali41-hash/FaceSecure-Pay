from flask import Flask, render_template, request, redirect, url_for
import sqlite3
import hashlib
from database import get_all_users, add_user, DB_NAME

app = Flask(__name__)

def verify_blockchain():
    """
    Validates the integrity of all transactions by re-calculating 
    the SHA-256 hashes in a sequential cryptographic chain.
    """
    try:
        conn = sqlite3.connect(DB_NAME)
        cursor = conn.cursor()
        # Fetching transactions in ascending order to verify the chain continuity
        cursor.execute("SELECT user_id, amount, date, tx_hash FROM transactions ORDER BY id ASC")
        txs = cursor.fetchall()
        conn.close()
    except Exception as e:
        return False, f"DATABASE ERROR: {str(e)}"

    prev_hash = "00000000"
    for tx in txs:
        u_id, amount, date, saved_hash = tx
        
        # Re-calculating the block hash for verification against the ledger
        block_string = f"{u_id}-{amount}-{date}-{prev_hash}"
        calculated_hash = hashlib.sha256(block_string.encode()).hexdigest()
        
        # Validation gate: Detects unauthorized manual modifications in the database
        if calculated_hash != saved_hash:
            return False, "CRITICAL: DATABASE INTEGRITY COMPROMISED"
        
        # Update previous hash pointer for the next block in the sequence
        prev_hash = saved_hash
    
    return True, "SYSTEM SECURE: LEDGER SYNCHRONIZED"

@app.route('/')
def dashboard():
    """
    Renders the primary administrative interface with real-time analytics 
    and security telemetry.
    """
    users = get_all_users()
    
    # Real-time execution of the blockchain integrity protocol
    is_secure, status_message = verify_blockchain()
    
    # Calculate aggregate revenue across all registered identities
    total_revenue = sum(user[3] for user in users) if users else 0
    
    return render_template('dashboard.html', 
                           users=users, 
                           total_revenue=total_revenue, 
                           blockchain_status=status_message,
                           is_secure=is_secure)

@app.route('/add_user', methods=['POST'])
def handle_add_user():
    """
    Processes the registration of a new identity and initializes their credit parameters.
    """
    u_id = request.form.get('u_id')
    name = request.form.get('name')
    limit = request.form.get('limit')
    
    if u_id and name and limit:
        add_user(u_id, name, float(limit))
    
    return redirect(url_for('dashboard'))

@app.route('/delete_user/<int:u_id>')
def delete_user(u_id):
    """
    Purges a user profile and their associated transaction history for data consistency.
    """
    try:
        conn = sqlite3.connect(DB_NAME)
        cursor = conn.cursor()
        
        # Remove primary user record
        cursor.execute("DELETE FROM users WHERE u_id = ?", (u_id,))
        
        # Purge associated transaction history to maintain relational integrity
        cursor.execute("DELETE FROM transactions WHERE user_id = ?", (u_id,))
        
        conn.commit()
        conn.close()
    except Exception as e:
        print(f"CRITICAL SYSTEM ERROR: {e}")
        
    return redirect(url_for('dashboard'))

if __name__ == '__main__':
    # Initializing server in development mode
    app.run(debug=True)