from fastapi import Request, HTTPException
import sqlite3
import os

DB_PATH = os.path.join(os.path.dirname(__file__), '../../database/cre.db')

def get_user_from_api_key(api_key: str):
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    cursor.execute(
        "SELECT id, email, subscription_tier FROM users WHERE api_key=?",
        (api_key,)
    )

    user = cursor.fetchone()
    conn.close()

    if not user:
        return None

    return {
        "id": user[0],
        "email": user[1],
        "tier": user[2]
    }


async def authenticate_request(request: Request):
    api_key = request.headers.get("X-API-Key")

    if not api_key:
        raise HTTPException(status_code=401, detail="Missing API Key")

    user = get_user_from_api_key(api_key)

    if not user:
        raise HTTPException(status_code=401, detail="Invalid API Key")

    request.state.user = user
