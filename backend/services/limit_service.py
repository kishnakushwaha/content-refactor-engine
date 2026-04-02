import os
from fastapi import HTTPException
from services.usage_service import get_daily_usage, get_lifetime_usage

FREE_MAX_WORDS = int(os.getenv("FREE_PLAN_MAX_WORDS", 3000))
FREE_MAX_REQ = int(os.getenv("FREE_PLAN_MAX_REQUESTS_PER_DAY", 10))
GUEST_MAX_REQ = 3

def enforce_limits(user, text: str):
    words = len(text.split())

    if user["tier"] == "guest":
        if words > FREE_MAX_WORDS:
            raise HTTPException(
                status_code=403,
                detail="Word limit exceeded for guest (Max 3000 words). Sign up to bypass or increase limits."
            )
        
        usage = get_lifetime_usage(user["id"])
        if usage >= GUEST_MAX_REQ:
            raise HTTPException(
                status_code=403,
                detail="guest_limit_reached"
            )

    elif user["tier"] == "free":
        if words > FREE_MAX_WORDS:
            raise HTTPException(
                status_code=403,
                detail="Word limit exceeded for free plan"
            )

        usage = get_daily_usage(user["id"])
        if usage >= FREE_MAX_REQ:
            raise HTTPException(
                status_code=429,
                detail="daily_limit_reached"
            )
