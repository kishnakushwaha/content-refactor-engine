import uuid

def generate_job_id() -> str:
    """
    Generates a unique job ID for asynchronous processing tasks.
    (Useful when transitioning from synchronous FastAPI to Celery/Redis).
    """
    return uuid.uuid4().hex

def calculate_token_estimate(text: str) -> int:
    """
    Provides a rough 1 token ~= 4 chars estimate for basic cost calculations 
    without needing the heavy tiktoken library.
    """
    if not text:
        return 0
    return len(text) // 4
