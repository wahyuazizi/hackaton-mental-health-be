from openai import AsyncAzureOpenAI
from app.config.settings import settings
from app.core.exceptions import AzureOpenAIException
import logging

logger = logging.getLogger(__name__)

class AzureOpenAIService:
    def __init__(self):
        self.client = AsyncAzureOpenAI(
            api_key=settings.azure_openai_api_key,
            api_version=settings.azure_openai_api_version,
            azure_endpoint=settings.azure_openai_endpoint
        )
    
    async def generate_response(self, messages: list, max_tokens: int = 500, temperature: float = 0.7) -> str:
        """Generate response from Azure OpenAI"""
        try:
            response = await self.client.chat.completions.create(
                model=settings.azure_openai_deployment_name,
                messages=messages,
                max_tokens=max_tokens,
                temperature=temperature,
                top_p=0.9
            )
            return response.choices[0].message.content
        except Exception as e:
            logger.error(f"Azure OpenAI error: {str(e)}")
            raise AzureOpenAIException(f"Failed to generate response: {str(e)}")

# Create singleton instance
azure_openai_service = AzureOpenAIService()