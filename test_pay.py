from database import update_spent, get_all_users

def run_backend_test():
    # Configuration for manual transaction test
    test_u_id = 101
    test_amount = 10.0

    print("\n" + "="*40)
    print("   FACESECURE: BACKEND LOGIC TEST   ")
    print("="*40)
    
    print(f"[ACTION] Manual Debit: ${test_amount} | Target ID: {test_u_id}")
    
    # Executing the transaction protocol (Database + Blockchain Hash)
    success = update_spent(test_u_id, test_amount)
    
    if success:
        print(f"[SUCCESS] Transaction authorized and committed to ledger.")
        print("[INFO] New SHA-256 block generated for this operation.")
        print("-" * 40)
        print("VERIFICATION: Please execute 'check_balance.py' to audit the ledger.")
    else:
        print("[FAIL] Transaction failed. Ensure ID 101 exists in the database.")
    
    print("="*40 + "\n")

if __name__ == "__main__":
    run_backend_test()