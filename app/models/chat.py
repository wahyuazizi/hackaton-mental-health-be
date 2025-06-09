from pydantic import BaseModel
from typing import List, Optional

class Message(BaseModel):
    role: str  # "user" or "assistant"
    content: str

class ChatRequest(BaseModel):
    message: str
    conversation_history: Optional[List[Message]] = []
    user_risk_level: Optional[str] = None

class ChatResponse(BaseModel):
    response: str
    is_crisis: bool = False
    crisis_resources: Optional[List[str]] = None