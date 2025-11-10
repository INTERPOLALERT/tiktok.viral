"""
Script Writing Module
AI-powered content script generation and optimization
"""

import logging
import asyncio
from typing import List, Dict, Any, Optional
from datetime import datetime
import re
import json

logger = logging.getLogger(__name__)


class ScriptGenerator:
    """AI-powered script writing and optimization"""

    def __init__(self, ai_client=None):
        if ai_client is None:
            from ..api.ai_client import AIClientFactory
            self.ai_client = AIClientFactory.get_client("openai")
        else:
            self.ai_client = ai_client

        logger.info("Script generator initialized")

    async def generate_video_script(
        self,
        topic: str,
        duration: int = 60,
        style: str = "engaging",
        target_audience: str = "general",
        key_points: Optional[List[str]] = None
    ) -> Dict[str, Any]:
        """Generate video script"""
        logger.info(f"Generating video script for: {topic}")

        key_points_str = ""
        if key_points:
            key_points_str = "\n".join([f"- {point}" for point in key_points])

        prompt = f"""Create a compelling {duration}-second video script about: {topic}

Style: {style}
Target Audience: {target_audience}

{f'Key points to cover:{key_points_str}' if key_points else ''}

The script should include:
1. Hook (first 3 seconds)
2. Introduction
3. Main content
4. Call to action
5. Outro

For each section, provide:
- The spoken text
- Suggested visuals
- Timing in seconds

Format as JSON with structure:
{{
    "title": "...",
    "total_duration": {duration},
    "sections": [
        {{
            "type": "hook",
            "duration": 3,
            "text": "...",
            "visuals": "..."
        }},
        ...
    ],
    "hashtags": ["...", "..."],
    "thumbnail_suggestion": "..."
}}"""

        try:
            response = await self.ai_client.generate_text(
                prompt,
                temperature=0.8,
                max_tokens=2000
            )

            # Parse JSON response
            script = json.loads(response.content)

            # Calculate word count
            total_words = sum(len(section.get('text', '').split()) for section in script.get('sections', []))
            script['word_count'] = total_words

            logger.info(f"Video script generated: {script.get('title', 'Untitled')}")
            return script

        except json.JSONDecodeError:
            # If JSON parsing fails, return raw content
            logger.warning("Failed to parse JSON response, returning raw content")
            return {
                "title": topic,
                "content": response.content,
                "word_count": len(response.content.split())
            }
        except Exception as e:
            logger.error(f"Failed to generate script: {e}")
            raise

    async def generate_social_post(
        self,
        topic: str,
        platform: str = "instagram",
        tone: str = "casual",
        include_hashtags: bool = True,
        include_emojis: bool = True,
        max_length: Optional[int] = None
    ) -> Dict[str, Any]:
        """Generate social media post"""
        logger.info(f"Generating {platform} post for: {topic}")

        platform_limits = {
            "twitter": 280,
            "instagram": 2200,
            "tiktok": 150,
            "facebook": 5000,
            "linkedin": 3000
        }

        if max_length is None:
            max_length = platform_limits.get(platform, 2200)

        prompt = f"""Create an engaging social media post for {platform} about: {topic}

Requirements:
- Tone: {tone}
- Maximum length: {max_length} characters
- {'Include relevant hashtags' if include_hashtags else 'No hashtags'}
- {'Use emojis appropriately' if include_emojis else 'No emojis'}
- Optimize for {platform} best practices

Provide the response as JSON:
{{
    "post_text": "...",
    "hashtags": ["...", "..."],
    "character_count": 0,
    "hook": "first line to grab attention",
    "call_to_action": "..."
}}"""

        try:
            response = await self.ai_client.generate_text(
                prompt,
                temperature=0.8,
                max_tokens=1000
            )

            post = json.loads(response.content)

            # Ensure character count is accurate
            post['character_count'] = len(post.get('post_text', ''))

            logger.info(f"{platform} post generated ({post['character_count']} chars)")
            return post

        except json.JSONDecodeError:
            logger.warning("Failed to parse JSON response")
            return {
                "post_text": response.content,
                "character_count": len(response.content)
            }
        except Exception as e:
            logger.error(f"Failed to generate social post: {e}")
            raise

    async def optimize_for_seo(
        self,
        content: str,
        keywords: List[str],
        target_platform: str = "google"
    ) -> Dict[str, Any]:
        """Optimize content for SEO"""
        logger.info(f"Optimizing content for SEO with {len(keywords)} keywords")

        keywords_str = ", ".join(keywords)

        prompt = f"""Analyze and optimize this content for SEO:

Content: {content}

Target Keywords: {keywords_str}
Platform: {target_platform}

Provide optimization analysis as JSON:
{{
    "seo_score": 0-100,
    "optimized_content": "...",
    "improvements": ["...", "..."],
    "keyword_density": {{
        "keyword": "percentage"
    }},
    "meta_description": "...",
    "suggested_title": "...",
    "readability_score": 0-100,
    "recommendations": ["...", "..."]
}}"""

        try:
            response = await self.ai_client.generate_text(
                prompt,
                temperature=0.3,
                max_tokens=2000
            )

            result = json.loads(response.content)
            logger.info(f"SEO optimization complete. Score: {result.get('seo_score', 0)}")
            return result

        except json.JSONDecodeError:
            logger.warning("Failed to parse JSON response")
            return {
                "seo_score": 50,
                "optimized_content": content,
                "improvements": []
            }
        except Exception as e:
            logger.error(f"Failed to optimize for SEO: {e}")
            raise

    async def generate_headlines(
        self,
        topic: str,
        count: int = 10,
        style: str = "clickbait"
    ) -> List[str]:
        """Generate headline variations"""
        logger.info(f"Generating {count} headlines for: {topic}")

        prompt = f"""Generate {count} compelling headlines for: {topic}

Style: {style}

Requirements:
- Attention-grabbing
- Clear and concise
- Include numbers or questions where appropriate
- Varied approaches

Provide as JSON array: ["headline 1", "headline 2", ...]"""

        try:
            response = await self.ai_client.generate_text(
                prompt,
                temperature=0.9,
                max_tokens=1000
            )

            headlines = json.loads(response.content)
            logger.info(f"Generated {len(headlines)} headlines")
            return headlines if isinstance(headlines, list) else [response.content]

        except json.JSONDecodeError:
            # Extract headlines from text
            headlines = response.content.strip().split('\n')
            return [h.strip('- ').strip() for h in headlines if h.strip()]
        except Exception as e:
            logger.error(f"Failed to generate headlines: {e}")
            raise

    async def improve_readability(self, content: str) -> Dict[str, Any]:
        """Improve content readability"""
        logger.info("Improving content readability")

        prompt = f"""Improve the readability of this content while maintaining its message:

{content}

Provide as JSON:
{{
    "improved_content": "...",
    "original_score": 0-100,
    "improved_score": 0-100,
    "changes_made": ["...", "..."],
    "readability_level": "elementary/middle school/high school/college"
}}"""

        try:
            response = await self.ai_client.generate_text(
                prompt,
                temperature=0.5,
                max_tokens=2000
            )

            result = json.loads(response.content)
            logger.info(f"Readability improved: {result.get('original_score', 0)} -> {result.get('improved_score', 0)}")
            return result

        except json.JSONDecodeError:
            logger.warning("Failed to parse JSON response")
            return {
                "improved_content": response.content,
                "changes_made": []
            }
        except Exception as e:
            logger.error(f"Failed to improve readability: {e}")
            raise

    async def generate_captions(
        self,
        video_description: str,
        duration: int = 60,
        language: str = "en"
    ) -> List[Dict[str, Any]]:
        """Generate video captions/subtitles"""
        logger.info(f"Generating captions for {duration}s video")

        prompt = f"""Generate timed captions for a {duration}-second video about: {video_description}

Provide captions as JSON array:
[
    {{
        "start_time": 0.0,
        "end_time": 3.0,
        "text": "..."
    }},
    ...
]

Requirements:
- Each caption should be 3-5 seconds
- Keep text concise (max 2 lines per caption)
- Ensure captions cover the full {duration} seconds"""

        try:
            response = await self.ai_client.generate_text(
                prompt,
                temperature=0.7,
                max_tokens=2000
            )

            captions = json.loads(response.content)
            logger.info(f"Generated {len(captions)} captions")
            return captions if isinstance(captions, list) else []

        except json.JSONDecodeError:
            logger.warning("Failed to parse JSON response")
            return []
        except Exception as e:
            logger.error(f"Failed to generate captions: {e}")
            raise

    async def analyze_sentiment(self, content: str) -> Dict[str, Any]:
        """Analyze content sentiment"""
        logger.info("Analyzing content sentiment")

        try:
            result = await self.ai_client.analyze_sentiment(content)
            logger.info(f"Sentiment: {result.get('sentiment', 'unknown')}")
            return result
        except Exception as e:
            logger.error(f"Failed to analyze sentiment: {e}")
            raise

    async def generate_script_variations(
        self,
        original_script: str,
        count: int = 3,
        variation_type: str = "tone"
    ) -> List[Dict[str, Any]]:
        """Generate script variations"""
        logger.info(f"Generating {count} script variations")

        variation_types = {
            "tone": "different tones (formal, casual, humorous, serious)",
            "length": "different lengths (short, medium, long)",
            "audience": "different target audiences (young adults, professionals, general)",
            "style": "different styles (educational, entertaining, inspirational)"
        }

        variation_desc = variation_types.get(variation_type, "different approaches")

        prompt = f"""Create {count} variations of this script using {variation_desc}:

Original Script:
{original_script}

Provide as JSON array:
[
    {{
        "variation_name": "...",
        "script": "...",
        "differences": "..."
    }},
    ...
]"""

        try:
            response = await self.ai_client.generate_text(
                prompt,
                temperature=0.8,
                max_tokens=3000
            )

            variations = json.loads(response.content)
            logger.info(f"Generated {len(variations)} variations")
            return variations if isinstance(variations, list) else []

        except json.JSONDecodeError:
            logger.warning("Failed to parse JSON response")
            return []
        except Exception as e:
            logger.error(f"Failed to generate variations: {e}")
            raise

    def calculate_reading_time(self, content: str, words_per_minute: int = 200) -> float:
        """Calculate estimated reading time"""
        word_count = len(content.split())
        minutes = word_count / words_per_minute
        return round(minutes, 1)

    def extract_keywords(self, content: str, max_keywords: int = 10) -> List[str]:
        """Extract keywords from content (basic implementation)"""
        # Remove common words
        common_words = {
            'the', 'a', 'an', 'and', 'or', 'but', 'in', 'on', 'at', 'to', 'for',
            'of', 'with', 'by', 'from', 'as', 'is', 'was', 'are', 'were', 'be',
            'been', 'being', 'have', 'has', 'had', 'do', 'does', 'did', 'will',
            'would', 'could', 'should', 'may', 'might', 'can', 'this', 'that',
            'these', 'those', 'i', 'you', 'he', 'she', 'it', 'we', 'they'
        }

        # Tokenize and filter
        words = re.findall(r'\b[a-z]{3,}\b', content.lower())
        keywords = [w for w in words if w not in common_words]

        # Count frequency
        from collections import Counter
        keyword_freq = Counter(keywords)

        # Return top keywords
        return [word for word, _ in keyword_freq.most_common(max_keywords)]
