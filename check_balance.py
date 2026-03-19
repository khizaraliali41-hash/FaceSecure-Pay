import sqlite3

def show_all_users():
    """
    Connects to the local database and generates a high-level 
    audit report of all registered identities and their credit status.
    """
    # Establish connection with the primary relational database
    try:
        conn = sqlite3.connect("facesecure.db")
        cursor = conn.cursor()
        
        # Extract core financial and identity telemetry
        cursor.execute("SELECT u_id, name, limit_amt, spent FROM users")
        rows = cursor.fetchall()
        
        print("\n" + "="*60)
        print("          FACESECURE ENTERPRISE DATABASE REPORT          ")
        print("="*60)
        # Header with standardized padding for high readability
        print(f"{'UID':<10} | {'IDENTITY NAME':<20} | {'LIMIT':<10} | {'SPENT':<10}")
        print("-" * 60)
        
        if not rows:
            print("System Log: No active records found in the ledger.")
        else:
            for row in rows:
                u_id, name, limit_amt, spent = row
                # Displaying formatted data rows
                print(f"#{u_id:<9} | {name:<20} | ${limit_amt:<9} | ${spent:<9}")
        
        print("-" * 60)
        print(f"Audit Complete. Total Records: {len(rows)}")
        print("="*60 + "\n")
        
        conn.close()
    except Exception as e:
        print(f"CRITICAL SYSTEM ERROR: Unable to access ledger. {e}")

if __name__ == "__main__":
    # Execution gate for manual database auditing
    show_all_users()