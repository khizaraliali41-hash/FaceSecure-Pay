from flask import Flask, render_template, request, redirect, url_for
from database import get_all_users, add_user  # database.py mein ye functions hone chahiye

app = Flask(__name__)

@app.route('/')
def dashboard():
    users = get_all_users()
    # Har user ke index 3 par 'spent' amount honi chahiye
    total_revenue = sum(user[3] for user in users) if users else 0
    return render_template('dashboard.html', users=users, total_revenue=total_revenue)

@app.route('/add_user', methods=['POST'])
def handle_add_user():
    u_id = request.form.get('u_id')
    name = request.form.get('name')
    limit = request.form.get('limit')
    
    if u_id and name and limit:
        # spent hamesha 0.0 se start hoga naye user ke liye
        add_user(u_id, name, float(limit))
    
    return redirect(url_for('dashboard'))

@app.route('/delete_user/<int:u_id>')
def delete_user(u_id):
    import sqlite3
    try:
        conn = sqlite3.connect('facesecure.db')
        cursor = conn.cursor()
        cursor.execute("DELETE FROM users WHERE u_id = ?", (u_id,))
        conn.commit()
        conn.close()
        print(f">> SYSTEM: User {u_id} deleted successfully.")
    except Exception as e:
        print(f">> ERROR: {e}")
        
    return redirect(url_for('dashboard'))

if __name__ == '__main__':
    app.run(debug=True)