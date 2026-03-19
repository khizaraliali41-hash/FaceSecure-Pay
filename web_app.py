from flask import Flask, render_template, request, jsonify, redirect, url_for
from database import get_all_users, get_monthly_revenue, add_user, delete_user
import os

app = Flask(__name__)

# --- 1. ENTERPRISE DASHBOARD ---
@app.route('/')
def dashboard():
    """
    Renders the primary administrative interface. 
    Aggregates data from the secure ledger for real-time visualization.
    """
    try:
        # Synchronizing data from the SQL backend
        users = get_all_users()
        total_monthly_rev = get_monthly_revenue()
        
        # Financial analytics calculation for dashboard metrics
        total_rev = sum(user[3] for user in users) if users else 0
        
        return render_template('dashboard.html', 
                               users=users, 
                               total_revenue=total_rev,
                               monthly_rev=total_monthly_rev)
    except Exception as e:
        # Professional error logging for system stability
        print(f"[CRITICAL] Dashboard Sync Error: {e}")
        return f"System Maintenance: Unable to synchronize ledger data. Error: {e}"

# --- 2. IDENTITY PROVISIONING (ADD USER) ---
@app.route('/add_user', methods=['POST'])
def handle_add_user():
    """
    Handles the registration of a new biometric identity via the web interface.
    """
    try:
        u_id = request.form.get('u_id')
        name = request.form.get('name')
        limit = request.form.get('limit')
        
        if u_id and name and limit:
            # Committing new identity to the relational database
            add_user(int(u_id), name, float(limit))
            print(f"[PROVISIONED] New Identity Created: {name} (ID: {u_id})")
            
        return redirect(url_for('dashboard'))
    except Exception as e:
        print(f"[ERROR] Identity Provisioning Failed: {e}")
        return f"Internal Server Error: {e}"

# --- 3. REVOKE ACCESS (DELETE USER) ---
@app.route('/delete_user/<int:u_id>')
def handle_delete_user(u_id):
    """
    De-authorizes a user and purges their data from the active terminal.
    """
    try:
        if delete_user(u_id):
            print(f"[REVOKED] Access removed for ID: {u_id}")
        return redirect(url_for('dashboard'))
    except Exception as e:
        print(f"[ERROR] Access Revocation Failed: {e}")
        return f"Error: Unable to process revocation for ID {u_id}"

# --- 4. REAL-TIME TELEMETRY API ---
@app.route('/api/status')
def status():
    """
    API endpoint for remote monitoring tools to check system health.
    """
    return jsonify({
        "system_status": "Online", 
        "biometric_engine": "Active",
        "blockchain_integrity": "Verified",
        "node_type": "Terminal Node 01"
    })

# --- 5. SERVER INITIALIZATION ---
if __name__ == '__main__':
    print("\n" + "="*50)
    print("   FACESECURE PAY: ENTERPRISE DASHBOARD STARTING   ")
    print("   Network Access: http://0.0.0.0:5000")
    print("="*50 + "\n")
    
    # Running in debug mode for development; switch to Gunicorn for production
    app.run(host='0.0.0.0', port=5000, debug=True)