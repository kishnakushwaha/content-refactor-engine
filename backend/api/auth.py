from fastapi import APIRouter, HTTPException, Request, Depends
from pydantic import BaseModel
import sqlite3
import uuid
import os
import secrets

DB_PATH = os.path.join(os.path.dirname(__file__), '../../database/cre.db')

router = APIRouter()

class SignupRequest(BaseModel):
    email: str
    current_guest_key: str | None = None

@router.post("/guest-session")
def create_guest_session():
    """Generates a transient guest account with 3 free lifetime limits."""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    user_id = str(uuid.uuid4())
    # Generate unique pseudo-email and api key
    dummy_email = f"guest_{user_id}@anonymous.local"
    api_key = f"cre-guest-{secrets.token_hex(8)}"
    
    try:
        cursor.execute(
            "INSERT INTO users (id, email, api_key, subscription_tier) VALUES (?, ?, ?, ?)",
            (user_id, dummy_email, api_key, 'guest')
        )
        conn.commit()
    except Exception as e:
        conn.close()
        raise HTTPException(status_code=500, detail="Failed to provision guest session")
    
    conn.close()
    
    return {"status": "success", "api_key": api_key, "message": "Guest session created"}

@router.post("/signup")
def signup(payload: SignupRequest):
    """
    Signs up a user physically. If they have a guest key, upgrades their account
    so they retain history!
    """
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    email = payload.email.strip().lower()
    if not email:
        conn.close()
        raise HTTPException(status_code=400, detail="Email is required")
        
    # Check if this real email already exists
    cursor.execute("SELECT id, api_key FROM users WHERE email=?", (email,))
    existing_user = cursor.fetchone()
    
    if existing_user:
        # If they already signed up, just return their existing key
        # (For MVP this acts as a pseudo-login)
        conn.close()
        return {
            "status": "success", 
            "api_key": existing_user[1], 
            "message": "Welcome back! Account recovered."
        }
    
    # Otherwise, either upgrade their guest key or create a new user
    if payload.current_guest_key and payload.current_guest_key.startswith("cre-guest-"):
        # Attempt to find the guest record
        cursor.execute("SELECT id FROM users WHERE api_key=? AND subscription_tier='guest'", (payload.current_guest_key,))
        guest = cursor.fetchone()
        
        if guest:
            # Upgrade!
            new_key = f"cre-free-{secrets.token_hex(8)}"
            cursor.execute("""
                UPDATE users 
                SET email=?, api_key=?, subscription_tier='free' 
                WHERE id=?
            """, (email, new_key, guest[0]))
            conn.commit()
            conn.close()
            return {
                "status": "success",
                "api_key": new_key,
                "message": "Account upgraded successfully! History retained."
            }
            
    # Fallback: Just create a completely new free tier user
    user_id = str(uuid.uuid4())
    api_key = f"cre-free-{secrets.token_hex(8)}"
    
    try:
        cursor.execute(
            "INSERT INTO users (id, email, api_key, subscription_tier) VALUES (?, ?, ?, ?)",
            (user_id, email, api_key, 'free')
        )
        conn.commit()
    except Exception as e:
        conn.close()
        raise HTTPException(status_code=500, detail="Signup failed, email might be in use.")
        
    conn.close()
    
    return {
        "status": "success",
        "api_key": api_key,
        "message": "Account created successfully!"
    }
