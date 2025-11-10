"""
AI Client
Unified interface for multiple AI providers (OpenAI, Anthropic, etc.)
"""

import asyncio
import logging
from typing import List, Dict, Any, Optional
from dataclasses import dataclass
import openai
from anthropic import Anthropic

logger = logging.getLogger(__name__)


@dataclass
class AIMessage:
    """AI message structure"""
    role: str
    content: str


@dataclass
class AIResponse:
    """AI response structure"""
    content: str
    model: str
    usage: Dict[str, int]
    finish_reason: str


class AIClient:
    """Unified AI client for multiple providers"""

    def __init__(self, provider: str = "openai", api_key: Optional[str] = None):
        self.provider = provider.lower()
        self.api_key = api_key

        if self.provider == "openai":
            if api_key:
                openai.api_key = api_key
            self.client = openai
        elif self.provider == "anthropic":
            self.client = Anthropic(api_key=api_key) if api_key else None
        else:
            raise ValueError(f"Unsupported AI provider: {provider}")

        logger.info(f"AI Client initialized with provider: {provider}")

    async def generate_text(
        self,
        prompt: str,
        model: Optional[str] = None,
        temperature: float = 0.7,
        max_tokens: int = 2000,
        system_prompt: Optional[str] = None
    ) -> AIResponse:
        """Generate text using AI"""
        try:
            if self.provider == "openai":
                return await self._generate_openai(
                    prompt, model, temperature, max_tokens, system_prompt
                )
            elif self.provider == "anthropic":
                return await self._generate_anthropic(
                    prompt, model, temperature, max_tokens, system_prompt
                )
        except Exception as e:
            logger.error(f"AI generation failed: {e}")
            raise

    async def _generate_openai(
        self,
        prompt: str,
        model: Optional[str],
        temperature: float,
        max_tokens: int,
        system_prompt: Optional[str]
    ) -> AIResponse:
        """Generate using OpenAI"""
        if model is None:
            model = "gpt-4-turbo-preview"

        messages = []
        if system_prompt:
            messages.append({"role": "system", "content": system_prompt})
        messages.append({"role": "user", "content": prompt})

        response = await asyncio.to_thread(
            openai.chat.completions.create,
            model=model,
            messages=messages,
            temperature=temperature,
            max_tokens=max_tokens
        )

        return AIResponse(
            content=response.choices[0].message.content,
            model=response.model,
            usage={
                "prompt_tokens": response.usage.prompt_tokens,
                "completion_tokens": response.usage.completion_tokens,
                "total_tokens": response.usage.total_tokens
            },
            finish_reason=response.choices[0].finish_reason
        )

    async def _generate_anthropic(
        self,
        prompt: str,
        model: Optional[str],
        temperature: float,
        max_tokens: int,
        system_prompt: Optional[str]
    ) -> AIResponse:
        """Generate using Anthropic"""
        if model is None:
            model = "claude-3-sonnet-20240229"

        if not self.client:
            raise ValueError("Anthropic client not initialized. API key required.")

        kwargs = {
            "model": model,
            "max_tokens": max_tokens,
            "temperature": temperature,
            "messages": [{"role": "user", "content": prompt}]
        }

        if system_prompt:
            kwargs["system"] = system_prompt

        response = await asyncio.to_thread(
            self.client.messages.create,
            **kwargs
        )

        return AIResponse(
            content=response.content[0].text,
            model=response.model,
            usage={
                "input_tokens": response.usage.input_tokens,
                "output_tokens": response.usage.output_tokens,
                "total_tokens": response.usage.input_tokens + response.usage.output_tokens
            },
            finish_reason=response.stop_reason
        )

    async def generate_image_prompt(
        self,
        description: str,
        style: Optional[str] = None,
        size: str = "1024x1024"
    ) -> str:
        """Generate DALL-E image from prompt"""
        try:
            if self.provider != "openai":
                raise ValueError("Image generation only supported with OpenAI")

            full_prompt = description
            if style:
                full_prompt = f"{description}, style: {style}"

            response = await asyncio.to_thread(
                openai.images.generate,
                model="dall-e-3",
                prompt=full_prompt,
                size=size,
                quality="hd",
                n=1
            )

            return response.data[0].url

        except Exception as e:
            logger.error(f"Image generation failed: {e}")
            raise

    async def analyze_sentiment(self, text: str) -> Dict[str, Any]:
        """Analyze sentiment of text"""
        prompt = f"""Analyze the sentiment of the following text and provide:
1. Overall sentiment (positive, negative, neutral)
2. Confidence score (0-1)
3. Key emotions detected
4. Brief explanation

Text: {text}

Respond in JSON format."""

        response = await self.generate_text(
            prompt,
            temperature=0.3,
            max_tokens=500
        )

        # Parse JSON response
        import json
        try:
            return json.loads(response.content)
        except:
            return {
                "sentiment": "neutral",
                "confidence": 0.5,
                "emotions": [],
                "explanation": response.content
            }

    async def optimize_for_seo(self, content: str, keywords: List[str]) -> Dict[str, Any]:
        """Optimize content for SEO"""
        keywords_str = ", ".join(keywords)
        prompt = f"""Optimize the following content for SEO with these keywords: {keywords_str}

Content: {content}

Provide:
1. Optimized content
2. SEO score (0-100)
3. Suggested improvements
4. Meta description
5. Suggested title

Respond in JSON format."""

        response = await self.generate_text(
            prompt,
            temperature=0.5,
            max_tokens=2000
        )

        import json
        try:
            return json.loads(response.content)
        except:
            return {
                "optimized_content": content,
                "seo_score": 50,
                "improvements": [],
                "meta_description": "",
                "title": ""
            }


class AIClientFactory:
    """Factory for creating AI clients"""

    _clients: Dict[str, AIClient] = {}

    @classmethod
    def get_client(cls, provider: str = "openai", api_key: Optional[str] = None) -> AIClient:
        """Get or create AI client"""
        cache_key = f"{provider}_{api_key[:8] if api_key else 'none'}"

        if cache_key not in cls._clients:
            cls._clients[cache_key] = AIClient(provider, api_key)

        return cls._clients[cache_key]

    @classmethod
    def clear_cache(cls):
        """Clear client cache"""
        cls._clients.clear()
