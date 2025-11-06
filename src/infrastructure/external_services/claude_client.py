"""
Claude AI service client
Clean Architecture - Frameworks & Drivers Layer
"""
from typing import List, Dict
from anthropic import AsyncAnthropic
from src.core.config.settings import settings
from src.core.exceptions.handlers import AIServiceException
import logging

logger = logging.getLogger(__name__)


class ClaudeClient:
    """
    Claude API client implementing the AI service interface
    Follows adapter pattern for external service integration
    """

    def __init__(self):
        if not settings.ANTHROPIC_API_KEY:
            raise ValueError("ANTHROPIC_API_KEY is required for Claude service")
        
        self.client = AsyncAnthropic(api_key=settings.ANTHROPIC_API_KEY)
        self.model = settings.DEFAULT_AI_MODEL
        logger.info(f"Claude client initialized with model: {self.model}")

    async def generate_message(
        self,
        system_prompt: str,
        user_message: str,
        max_tokens: int = None,
        temperature: float = None
    ) -> str:
        """
        Generate AI message using Claude API (single message)

        Args:
            system_prompt: System prompt for the AI
            user_message: User's message
            max_tokens: Maximum tokens to generate
            temperature: Temperature for response randomness

        Returns:
            Generated AI message

        Raises:
            AIServiceException: When API call fails
        """
        try:
            max_tokens = max_tokens or settings.DEFAULT_MAX_TOKENS
            temperature = temperature or settings.DEFAULT_TEMPERATURE

            logger.debug(f"Generating message with Claude - tokens: {max_tokens}, temp: {temperature}")

            message = await self.client.messages.create(
                model=self.model,
                max_tokens=max_tokens,
                temperature=temperature,
                system=system_prompt,
                messages=[
                    {
                        "role": "user",
                        "content": user_message
                    }
                ]
            )

            response_text = message.content[0].text
            logger.info(f"Claude response generated successfully - length: {len(response_text)}")
            return response_text

        except Exception as e:
            logger.error(f"Claude API error: {str(e)}")
            raise AIServiceException("claude", str(e))

    async def generate_message_with_history(
        self,
        system_prompt: str,
        messages: List[Dict[str, str]],
        max_tokens: int = None,
        temperature: float = None
    ) -> str:
        """
        Generate AI message with conversation history

        Args:
            system_prompt: System prompt for the AI
            messages: List of conversation messages [{"role": "user", "content": "..."}, ...]
            max_tokens: Maximum tokens to generate
            temperature: Temperature for response randomness

        Returns:
            Generated AI message

        Raises:
            AIServiceException: When API call fails
        """
        try:
            max_tokens = max_tokens or settings.DEFAULT_MAX_TOKENS
            temperature = temperature or settings.DEFAULT_TEMPERATURE

            logger.debug(f"Generating message with Claude - history: {len(messages)} messages")

            message = await self.client.messages.create(
                model=self.model,
                max_tokens=max_tokens,
                temperature=temperature,
                system=system_prompt,
                messages=messages
            )

            response_text = message.content[0].text
            logger.info(f"Claude response with history generated - length: {len(response_text)}")
            return response_text

        except Exception as e:
            logger.error(f"Claude API error with history: {str(e)}")
            raise AIServiceException("claude", str(e))

    def get_model_info(self) -> Dict[str, str]:
        """Get information about the current model"""
        return {
            "service": "claude",
            "model": self.model,
            "provider": "anthropic"
        }


# Singleton instance following dependency injection pattern
claude_client = ClaudeClient()