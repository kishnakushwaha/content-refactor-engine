from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from api.routes import router as api_router
from models.database import init_db
import time

# Initialize DB on boot
init_db()

app = FastAPI(title="CRE SaaS MVP")

@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    print("CRITICAL ERROR:", str(exc))
    return JSONResponse(
        status_code=500,
        content={"error": str(exc), "status": "failed"}
    )

# Production CORS config
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:8000", "https://your-production-domain.com"], # Strict security
    allow_credentials=True,
    allow_methods=["GET", "POST"],
    allow_headers=["*"],
)

# Very basic Rate Limiting (In a real SaaS, use Redis)
request_history = {}
MAX_REQS_PER_MIN = 10

@app.middleware("http")
async def rate_limit_middleware(request: Request, call_next):
    # Only limit the heavy AI endpoints
    if "/api/process" in request.url.path:
        client_ip = request.client.host
        current_time = time.time()
        
        if client_ip not in request_history:
            request_history[client_ip] = []
            
        history = request_history[client_ip]
        # Remove timestamps older than 60 seconds
        request_history[client_ip] = [t for t in history if current_time - t < 60]
        
        if len(request_history[client_ip]) >= MAX_REQS_PER_MIN:
            return JSONResponse(status_code=429, content={"message": "Rate limit exceeded. Try again in a minute."})
            
        request_history[client_ip].append(current_time)

    response = await call_next(request)
    return response

app.include_router(api_router, prefix="/api")

# Serve the frontend statically from the root
import os
frontend_dir = os.path.join(os.path.dirname(__file__), "../frontend")
app.mount("/", StaticFiles(directory=frontend_dir, html=True), name="frontend")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
