from fastapi import APIRouter
from fastapi.responses import StreamingResponse
from pydantic import BaseModel

from app.orchestrator.orchestrator import handle_message


router = APIRouter(tags=["chat"])


class ChatRequest(BaseModel):
    session_id: str
    message: str


@router.post("/chat")
async def chat(req: ChatRequest):
    """Server-Sent Events stream of message / status / profile_ready /
    candidates / recommendation / error events."""
    return StreamingResponse(
        handle_message(req.session_id, req.message),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
            "X-Accel-Buffering": "no",
        },
    )
