from fastapi import APIRouter, Request, Depends
from fastapi.responses import StreamingResponse
from api.controllers import process_article_controller, get_user_history
from pydantic import BaseModel
from api.auth_middleware import authenticate_request
from services.limit_service import enforce_limits
from services.usage_service import track_usage
import asyncio
import json

router = APIRouter()

class ProcessRequest(BaseModel):
    content: str


@router.post("/process")
async def process(req: Request, payload: ProcessRequest, auth=Depends(authenticate_request)):
    user = req.state.user
    content = payload.content

    enforce_limits(user, content)

    result = await process_article_controller(content, user_id=user["id"])

    track_usage(user["id"], len(content.split()))

    return result


@router.post("/process-stream")
async def process_stream(req: Request, payload: ProcessRequest, auth=Depends(authenticate_request)):
    """
    SSE endpoint that streams progress updates to the frontend in real-time.
    Each event contains a step name and a human-readable status message.
    """
    user = req.state.user
    content = payload.content

    enforce_limits(user, content)

    progress_queue = asyncio.Queue()

    async def progress_callback(step: str, message: str):
        await progress_queue.put({"step": step, "message": message})

    async def run_pipeline():
        result = await process_article_controller(content, user_id=user["id"], progress_callback=progress_callback)
        track_usage(user["id"], len(content.split()))
        await progress_queue.put({"step": "complete", "result": result})

    async def event_generator():
        task = asyncio.create_task(run_pipeline())
        
        while True:
            try:
                event = await asyncio.wait_for(progress_queue.get(), timeout=120)
            except asyncio.TimeoutError:
                yield f"data: {json.dumps({'step': 'timeout', 'message': 'Processing timed out'})}\n\n"
                break
            
            yield f"data: {json.dumps(event)}\n\n"
            
            if event.get("step") == "complete":
                break
        
        await task

    return StreamingResponse(
        event_generator(),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
            "X-Accel-Buffering": "no"
        }
    )


@router.get("/history")
async def get_history(req: Request, auth=Depends(authenticate_request)):
    """Returns the user's past processing history."""
    user = req.state.user
    history = get_user_history(user["id"])
    return {"history": history}
