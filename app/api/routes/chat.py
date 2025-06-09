from fastapi import APIRouter, HTTPException, Depends
from app.models.chat import ChatRequest, ChatResponse
from app.services.chat_service import ChatService
from app.api.dependencies import get_chat_service
from app.core.constants import CRISIS_RESOURCES

router = APIRouter(prefix="/api/chat", tags=["chat"])

@router.post("", response_model=ChatResponse)
async def chat_endpoint(
    request: ChatRequest,
    chat_service: ChatService = Depends(get_chat_service)
):
    """Chat with AI Counselor"""
    try:
        response = await chat_service.process_chat(request)
        return response
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Chat service error: {str(e)}")

@router.post("/crisis-check")
async def crisis_check(
    request: dict,
    chat_service: ChatService = Depends(get_chat_service)
):
    """Endpoint for crisis detection"""
    message = request.get("message", "")
    is_crisis = chat_service.detect_crisis(message)
    
    return {
        "is_crisis": is_crisis,
        "crisis_resources": CRISIS_RESOURCES if is_crisis else None
    }
