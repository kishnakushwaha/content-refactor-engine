import os
from fastapi import HTTPException
from services.usage_service import get_daily_usage

FREE_MAX_WORDS = int(os.getenv("FREE_PLAN_MAX_WORDS", 3000))
FREE_MAX_REQ = int(os.getenv("FREE_PLAN_MAX_REQUESTS_PER_DAY", 10))

def enforce_limits(user, text: str):
    words = len(text.split())

    if user["tier"] == "free":
        if words > FREE_MAX_WORDS:
            raise HTTPException(
                status_code=403,
                detail="Word limit exceeded for free plan"
            )

        usage = get_daily_usage(user["id"])

        if usage >= FREE_MAX_REQ:
            raise HTTPException(
                status_code=429,
                detail="Daily request limit exceeded"
            )
