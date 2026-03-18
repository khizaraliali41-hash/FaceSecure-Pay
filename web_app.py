from flask import Flask, render_template, request, jsonify, redirect, url_for
from database import get_all_users, get_monthly_revenue, add_user, delete_user
import os

app = Flask(__name__)

# --- 1. MAIN DASHBOARD ROUTE ---
@app.route('/')
def dashboard():
    try:
        # Database se data uthana
        users = get_all_users()
        total_monthly_rev = get_monthly_revenue() # Single value return karta hai ab
        
        # Total Spent calculate karna chart ke liye
        total_rev = sum(user[3] for user in users) if users else 0
        
        return render_template('dashboard.html', 
                               users=users, 
                               total_revenue=total_rev,
                               monthly_rev=total_monthly_rev)
    except Exception as e:
        return f"Database Error: {e}. Make sure database.py is updated and saved."

# --- 2. ADD USER ROUTE ---
@app.route('/add_user', methods=['POST'])
def handle_add_user():
    try:
        u_id = request.form.get('u_id')
        name = request.form.get('name')
        limit = request.form.get('limit')
        
        if u_id and name and limit:
            # Correct function call: add_user
            add_user(int(u_id), name, float(limit))
            print(f">> SUCCESS: {name} added to Database!")
            
        return redirect(url_for('dashboard'))
    except Exception as e:
        return f"Form Error: {e}"

# --- 3. DELETE USER ROUTE (Revoke Access button ke liye) ---
@app.route('/delete_user/<int:u_id>')
def handle_delete_user(u_id):
    try:
        delete_user(u_id)
        return redirect(url_for('dashboard'))
    except Exception as e:
        return f"Delete Error: {e}"

# --- 4. STATUS API ---
@app.route('/api/status')
def status():
    return jsonify({
        "status": "Online", 
        "terminal_mode": "Active",
        "server_time": "Real-time"
    })

# --- 5. START SERVER ---
if __name__ == '__main__':
    print("\n" + "="*50)
    print(">> FACSECURE PAY: SaaS DASHBOARD IS STARTING...")
    print(">> Access on PC: http://127.0.0.1:5000")
    print("="*50 + "\n")
    app.run(host='0.0.0.0', port=5000, debug=True)