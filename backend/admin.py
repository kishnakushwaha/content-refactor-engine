import sqlite3
import argparse
import os

DB_PATH = os.path.join(os.path.dirname(__file__), '../database/cre.db')

def get_connection():
    if not os.path.exists(DB_PATH):
        print(f"Error: Database not found at {DB_PATH}")
        exit(1)
    return sqlite3.connect(DB_PATH)

def list_users():
    conn = get_connection()
    cursor = conn.cursor()
    
    # We ignore guests since they haven't signed up properly
    cursor.execute("""
        SELECT email, subscription_tier, created_at 
        FROM users 
        WHERE subscription_tier != 'guest'
        ORDER BY created_at DESC
    """)
    users = cursor.fetchall()
    conn.close()
    
    if not users:
        print("No users have signed up yet.")
        return
        
    print(f"\n{'-'*60}")
    print(f"{'Email':<30} | {'Tier':<10} | {'Signup Date'}")
    print(f"{'-'*60}")
    for u in users:
        print(f"{u[0]:<30} | {u[1]:<10} | {u[2]}")
    print(f"{'-'*60}\n")

def upgrade_user(email):
    conn = get_connection()
    cursor = conn.cursor()
    
    # Verify user exists
    cursor.execute("SELECT id FROM users WHERE email=? COLLATE NOCASE", (email,))
    user = cursor.fetchone()
    
    if not user:
        print(f"Error: No user found with email '{email}'.")
        conn.close()
        return
        
    # Upgrade to enterprise/premium to unlock limits
    cursor.execute("UPDATE users SET subscription_tier='enterprise' WHERE email=? COLLATE NOCASE", (email,))
    conn.commit()
    conn.close()
    
    print(f"✅ Success! Unlocked unlimited access for '{email}'.")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="CRE Admin Helper")
    subparsers = parser.add_subparsers(dest="command")
    
    # The list command
    list_parser = subparsers.add_parser("list", help="List all signed up users")
    
    # The upgrade command
    upgrade_parser = subparsers.add_parser("upgrade", help="Remove limits for a specific user")
    upgrade_parser.add_argument("email", type=str, help="The email address to upgrade")
    
    args = parser.parse_args()
    
    if args.command == "list":
        list_users()
    elif args.command == "upgrade":
        upgrade_user(args.email)
    else:
        parser.print_help()
