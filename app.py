from flask import Flask, render_template, request, redirect, url_for
import sqlite3
import hashlib
from database import get_all_users, add_user, DB_NAME

app = Flask(__name__)

# --- BLOCKCHAIN INTEGRITY VERIFICATION ---
def verify_blockchain():
    """
    Validates the integrity of all transactions by re-calculating 
    the SHA-256 hashes in a sequential chain.
    """
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    # Fetching transactions in ascending order to verify the chain
    cursor.execute("SELECT user_id, amount, date, tx_hash FROM transactions ORDER BY id ASC")
    txs = cursor.fetchall()
    conn.close()

    prev_hash = "00000000"
    for tx in txs:
        u_id, amount, date, saved_hash = tx
        
        # Re-calculating the hash for verification
        block_string = f"{u_id}-{amount}-{date}-{prev_hash}"
        calculated_hash = hashlib.sha256(block_string.encode()).hexdigest()
        
        # Check if the data has been tampered with
        if calculated_hash != saved_hash:
            return False, "⚠️ TAMPERED: Database Integrity Compromised!"
        
        # Update prev_hash for the next block in the chain
        prev_hash = saved_hash
    
    return True, "✅ SECURE: Ledger Synchronized"

@app.route('/')
def dashboard():
    """Renders the main admin dashboard with real-time security status."""
    users = get_all_users()
    
    # Perform real-time blockchain integrity check
    is_secure, status_message = verify_blockchain()
    
    # Calculate total revenue; 'spent' amount is at index 3 of the user tuple
    total_revenue = sum(user[3] for user in users) if users else 0
    
    return render_template('dashboard.html', 
                           users=users, 
                           total_revenue=total_revenue, 
                           blockchain_status=status_message,
                           is_secure=is_secure)

@app.route('/add_user', methods=['POST'])
def handle_add_user():
    """Handles the form submission to register a new user."""
    u_id = request.form.get('u_id')
    name = request.form.get('name')
    limit = request.form.get('limit')
    
    if u_id and name and limit:
        add_user(u_id, name, float(limit))
    
    return redirect(url_for('dashboard'))

@app.route('/delete_user/<int:u_id>')
def delete_user(u_id):
    """Deletes a user and their associated transaction history from the database."""
    try:
        conn = sqlite3.connect(DB_NAME)
        cursor = conn.cursor()
        
        # Delete user from the users table
        cursor.execute("DELETE FROM users WHERE u_id = ?", (u_id,))
        
        # Also clean up transaction history for data consistency
        cursor.execute("DELETE FROM transactions WHERE user_id = ?", (u_id,))
        
        conn.commit()
        conn.close()
    except Exception as e:
        print(f">> DATABASE ERROR: {e}")
        
    return redirect(url_for('dashboard'))

if __name__ == '__main__':
    app.run(debug=True)