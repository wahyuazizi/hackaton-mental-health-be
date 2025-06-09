from typing import List
from app.models.chat import ChatRequest, ChatResponse, Message
from app.services.azure_openai_service import azure_openai_service
from app.core.constants import CRISIS_KEYWORDS, CRISIS_RESOURCES, SYSTEM_PROMPT
from app.core.exceptions import ChatException
import logging

logger = logging.getLogger(__name__)

class ChatService:
    @staticmethod
    def detect_crisis(message: str) -> bool:
        """Detect if message contains crisis indicators"""
        message_lower = message.lower()
        return any(keyword in message_lower for keyword in CRISIS_KEYWORDS)
    
    @staticmethod
    async def process_chat(request: ChatRequest) -> ChatResponse:
        """Process chat request and return response"""
        try:
            # Detect crisis
            is_crisis = ChatService.detect_crisis(request.message)
            
            # Prepare system prompt with user risk information
            system_prompt = SYSTEM_PROMPT
            if request.user_risk_level:
                system_prompt += f"\n\nINFORMASI PENGGUNA: Tingkat risiko kecanduan judi pengguna adalah '{request.user_risk_level}'. Sesuaikan pendekatan Anda dengan tingkat risiko ini."
            
            # Prepare messages for Azure OpenAI
            messages = [{"role": "system", "content": system_prompt}]
            
            # Add conversation history (keep last 10 messages for context)
            for msg in request.conversation_history[-10:]:
                messages.append({
                    "role": msg.role,
                    "content": msg.content
                })
            
            # Add current user message
            messages.append({
                "role": "user",
                "content": request.message
            })
            
            # Generate response
            bot_response = await azure_openai_service.generate_response(messages)
            
            # Log for monitoring
            logger.info(f"User message: {request.message[:100]}...")
            logger.info(f"Bot response: {bot_response[:100]}...")
            logger.info(f"Crisis detected: {is_crisis}")
            logger.info(f"User risk level: {request.user_risk_level}")
            
            return ChatResponse(
                response=bot_response,
                is_crisis=is_crisis,
                crisis_resources=CRISIS_RESOURCES if is_crisis else None
            )
            
        except Exception as e:
            logger.error(f"Error in chat service: {str(e)}")
            
            # Fallback response
            fallback_response = "Maaf, saya mengalami gangguan teknis. Silakan coba lagi dalam beberapa saat. Jika Anda dalam keadaan darurat, hubungi 119 atau layanan kesehatan mental terdekat."
            
            return ChatResponse(
                response=fallback_response,
                is_crisis=False,
                crisis_resources=None
            )