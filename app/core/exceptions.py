class GamblingAPIException(Exception):
    """Base exception for the Gambling API"""
    pass

class AssessmentException(GamblingAPIException):
    """Exception for assessment-related errors"""
    pass

class ChatException(GamblingAPIException):
    """Exception for chat-related errors"""
    pass

class AzureOpenAIException(GamblingAPIException):
    """Exception for Azure OpenAI-related errors"""
    pass