from app.services.assessment_service import AssessmentService
from app.services.chat_service import ChatService

def get_assessment_service() -> AssessmentService:
    return AssessmentService()

def get_chat_service() -> ChatService:
    return ChatService()
