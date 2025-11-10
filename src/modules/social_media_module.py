"""
Social Media Module
Multi-platform scheduling, posting, and management
"""

import logging
import asyncio
from typing import List, Dict, Any, Optional
from datetime import datetime, timedelta
import json
from pathlib import Path
import schedule
import aiohttp

logger = logging.getLogger(__name__)


class PlatformOptimizer:
    """Optimize content for different platforms"""

    PLATFORM_SPECS = {
        "tiktok": {
            "video": {
                "max_duration": 600,  # 10 minutes
                "recommended_duration": 60,
                "aspect_ratio": "9:16",
                "resolution": (1080, 1920),
                "max_size_mb": 287
            },
            "caption": {
                "max_length": 150,
                "hashtags": 30
            }
        },
        "instagram": {
            "post": {
                "aspect_ratio": "1:1",
                "resolution": (1080, 1080),
                "max_size_mb": 30
            },
            "story": {
                "aspect_ratio": "9:16",
                "resolution": (1080, 1920),
                "max_size_mb": 100
            },
            "reel": {
                "max_duration": 90,
                "aspect_ratio": "9:16",
                "resolution": (1080, 1920)
            },
            "caption": {
                "max_length": 2200,
                "hashtags": 30
            }
        },
        "youtube": {
            "video": {
                "max_duration": 43200,  # 12 hours
                "aspect_ratio": "16:9",
                "resolution": (1920, 1080),
                "max_size_mb": 128000
            },
            "short": {
                "max_duration": 60,
                "aspect_ratio": "9:16",
                "resolution": (1080, 1920)
            },
            "title": {
                "max_length": 100
            },
            "description": {
                "max_length": 5000
            }
        },
        "twitter": {
            "text": {
                "max_length": 280
            },
            "video": {
                "max_duration": 140,
                "max_size_mb": 512
            },
            "image": {
                "aspect_ratio": "16:9",
                "max_count": 4
            }
        },
        "facebook": {
            "post": {
                "max_length": 63206
            },
            "video": {
                "max_duration": 240,  # 4 hours
                "max_size_mb": 10000
            }
        }
    }

    @classmethod
    def get_specs(cls, platform: str, content_type: str = "post") -> Dict[str, Any]:
        """Get platform specifications"""
        platform = platform.lower()
        if platform in cls.PLATFORM_SPECS:
            platform_specs = cls.PLATFORM_SPECS[platform]
            return platform_specs.get(content_type, platform_specs)
        return {}

    @classmethod
    def validate_content(cls, platform: str, content_type: str, **kwargs) -> Dict[str, Any]:
        """Validate content against platform requirements"""
        specs = cls.get_specs(platform, content_type)
        issues = []
        suggestions = []

        # Validate video duration
        if "duration" in kwargs and "max_duration" in specs:
            if kwargs["duration"] > specs["max_duration"]:
                issues.append(f"Duration exceeds maximum of {specs['max_duration']}s")
                suggestions.append(f"Trim video to {specs['max_duration']}s")

        # Validate file size
        if "size_mb" in kwargs and "max_size_mb" in specs:
            if kwargs["size_mb"] > specs["max_size_mb"]:
                issues.append(f"File size exceeds {specs['max_size_mb']}MB")
                suggestions.append("Compress or reduce quality")

        # Validate caption length
        if "caption" in kwargs and "max_length" in specs.get("caption", {}):
            if len(kwargs["caption"]) > specs["caption"]["max_length"]:
                issues.append(f"Caption exceeds {specs['caption']['max_length']} characters")
                suggestions.append("Shorten caption")

        return {
            "valid": len(issues) == 0,
            "issues": issues,
            "suggestions": suggestions,
            "specs": specs
        }


class SocialMediaScheduler:
    """Schedule and manage social media posts"""

    def __init__(self, db_session=None):
        self.db_session = db_session
        self.scheduled_posts = []
        logger.info("Social media scheduler initialized")

    async def schedule_post(
        self,
        platform: str,
        content: str,
        media_paths: List[str],
        scheduled_time: datetime,
        hashtags: Optional[List[str]] = None,
        metadata: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """Schedule a post for future publishing"""
        logger.info(f"Scheduling {platform} post for {scheduled_time}")

        post_data = {
            "id": len(self.scheduled_posts) + 1,
            "platform": platform,
            "content": content,
            "media_paths": media_paths,
            "scheduled_time": scheduled_time,
            "hashtags": hashtags or [],
            "status": "scheduled",
            "metadata": metadata or {},
            "created_at": datetime.now()
        }

        # Validate content
        validation = PlatformOptimizer.validate_content(
            platform,
            "post",
            caption=content,
            size_mb=sum(Path(p).stat().st_size / 1024 / 1024 for p in media_paths if Path(p).exists())
        )

        if not validation["valid"]:
            post_data["status"] = "validation_failed"
            post_data["issues"] = validation["issues"]
            logger.warning(f"Post validation failed: {validation['issues']}")

        self.scheduled_posts.append(post_data)

        # Save to database if available
        if self.db_session:
            from ..database.models import SocialMediaPost
            db_post = SocialMediaPost(
                platform=platform,
                content=content,
                media_paths=media_paths,
                status=post_data["status"],
                scheduled_time=scheduled_time,
                metadata=post_data
            )
            self.db_session.add(db_post)
            self.db_session.commit()

        logger.info(f"Post scheduled successfully: {post_data['id']}")
        return post_data

    async def cancel_post(self, post_id: int) -> bool:
        """Cancel a scheduled post"""
        for post in self.scheduled_posts:
            if post["id"] == post_id and post["status"] == "scheduled":
                post["status"] = "cancelled"
                logger.info(f"Post {post_id} cancelled")
                return True
        return False

    async def get_scheduled_posts(
        self,
        platform: Optional[str] = None,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None
    ) -> List[Dict[str, Any]]:
        """Get scheduled posts with optional filters"""
        posts = self.scheduled_posts

        if platform:
            posts = [p for p in posts if p["platform"] == platform]

        if start_date:
            posts = [p for p in posts if p["scheduled_time"] >= start_date]

        if end_date:
            posts = [p for p in posts if p["scheduled_time"] <= end_date]

        return posts

    async def suggest_best_time(
        self,
        platform: str,
        target_audience: str = "general"
    ) -> List[datetime]:
        """Suggest optimal posting times based on platform and audience"""
        logger.info(f"Suggesting best posting times for {platform}")

        # Best times based on research (simplified)
        best_times = {
            "tiktok": [
                {"hour": 7, "minute": 0},   # 7 AM
                {"hour": 12, "minute": 0},  # 12 PM
                {"hour": 19, "minute": 0}   # 7 PM
            ],
            "instagram": [
                {"hour": 6, "minute": 0},   # 6 AM
                {"hour": 12, "minute": 0},  # 12 PM
                {"hour": 17, "minute": 0}   # 5 PM
            ],
            "youtube": [
                {"hour": 14, "minute": 0},  # 2 PM
                {"hour": 20, "minute": 0}   # 8 PM
            ],
            "twitter": [
                {"hour": 9, "minute": 0},   # 9 AM
                {"hour": 12, "minute": 0},  # 12 PM
                {"hour": 17, "minute": 0}   # 5 PM
            ],
            "facebook": [
                {"hour": 13, "minute": 0},  # 1 PM
                {"hour": 15, "minute": 0}   # 3 PM
            ]
        }

        times = best_times.get(platform.lower(), [{"hour": 12, "minute": 0}])

        # Generate suggested times for next 7 days
        suggestions = []
        now = datetime.now()

        for day_offset in range(7):
            day = now + timedelta(days=day_offset)
            for time_slot in times:
                suggested_time = day.replace(
                    hour=time_slot["hour"],
                    minute=time_slot["minute"],
                    second=0,
                    microsecond=0
                )
                if suggested_time > now:
                    suggestions.append(suggested_time)

        return suggestions[:10]  # Return next 10 optimal times

    def generate_content_calendar(
        self,
        platforms: List[str],
        days: int = 30,
        posts_per_day: int = 2
    ) -> Dict[str, Any]:
        """Generate a content calendar"""
        logger.info(f"Generating {days}-day content calendar for {len(platforms)} platforms")

        calendar = {}
        start_date = datetime.now().replace(hour=0, minute=0, second=0, microsecond=0)

        for day_offset in range(days):
            date = start_date + timedelta(days=day_offset)
            date_key = date.strftime("%Y-%m-%d")

            calendar[date_key] = {
                "date": date,
                "posts": []
            }

            for platform in platforms:
                for post_num in range(posts_per_day):
                    # Simple time distribution
                    hour = 9 + (post_num * 6)  # 9 AM, 3 PM, etc.

                    calendar[date_key]["posts"].append({
                        "platform": platform,
                        "suggested_time": date.replace(hour=hour),
                        "status": "planned",
                        "content_type": "to_be_created"
                    })

        return calendar


class EngagementTracker:
    """Track engagement metrics across platforms"""

    def __init__(self, db_session=None):
        self.db_session = db_session
        logger.info("Engagement tracker initialized")

    async def track_post_performance(
        self,
        post_id: str,
        platform: str,
        metrics: Dict[str, Any]
    ):
        """Track performance metrics for a post"""
        logger.info(f"Tracking performance for {platform} post {post_id}")

        if self.db_session:
            from ..database.models import Analytics

            for metric_type, value in metrics.items():
                analytics_record = Analytics(
                    platform=platform,
                    post_id=post_id,
                    metric_type=metric_type,
                    value=value,
                    recorded_at=datetime.now()
                )
                self.db_session.add(analytics_record)

            self.db_session.commit()

    async def get_engagement_summary(
        self,
        platform: Optional[str] = None,
        days: int = 30
    ) -> Dict[str, Any]:
        """Get engagement summary"""
        logger.info(f"Getting engagement summary for last {days} days")

        # Mock data for demonstration
        summary = {
            "total_posts": 150,
            "total_views": 50000,
            "total_likes": 5000,
            "total_comments": 500,
            "total_shares": 250,
            "engagement_rate": 11.5,
            "average_views_per_post": 333,
            "top_performing_posts": [],
            "growth": {
                "views": "+15%",
                "followers": "+8%",
                "engagement": "+12%"
            }
        }

        return summary

    async def compare_platforms(self) -> Dict[str, Any]:
        """Compare performance across platforms"""
        logger.info("Comparing platform performance")

        comparison = {
            "tiktok": {
                "total_posts": 50,
                "avg_views": 5000,
                "avg_engagement": 12.5,
                "best_performing_type": "short_videos"
            },
            "instagram": {
                "total_posts": 60,
                "avg_views": 3000,
                "avg_engagement": 8.5,
                "best_performing_type": "reels"
            },
            "youtube": {
                "total_posts": 40,
                "avg_views": 10000,
                "avg_engagement": 6.2,
                "best_performing_type": "tutorials"
            }
        }

        return comparison


class HashtagGenerator:
    """Generate and optimize hashtags"""

    def __init__(self, ai_client=None):
        if ai_client is None:
            from ..api.ai_client import AIClientFactory
            self.ai_client = AIClientFactory.get_client("openai")
        else:
            self.ai_client = ai_client

        logger.info("Hashtag generator initialized")

    async def generate_hashtags(
        self,
        content: str,
        platform: str = "instagram",
        count: int = 30
    ) -> List[str]:
        """Generate relevant hashtags for content"""
        logger.info(f"Generating {count} hashtags for {platform}")

        prompt = f"""Generate {count} relevant hashtags for the following content on {platform}:

Content: {content}

Requirements:
- Mix of popular, moderately popular, and niche hashtags
- Relevant to the content
- Platform-appropriate
- Include trending hashtags if applicable

Return as JSON array: ["hashtag1", "hashtag2", ...]
(without # symbol)"""

        try:
            response = await self.ai_client.generate_text(
                prompt,
                temperature=0.7,
                max_tokens=500
            )

            hashtags = json.loads(response.content)
            return hashtags if isinstance(hashtags, list) else []

        except:
            # Fallback to basic extraction
            return ["viral", "trending", "fyp", "explore", "instagood"]

    async def analyze_hashtag_performance(
        self,
        hashtags: List[str],
        platform: str
    ) -> Dict[str, Any]:
        """Analyze hashtag performance potential"""
        logger.info(f"Analyzing {len(hashtags)} hashtags")

        # Mock analysis
        analysis = {
            "top_hashtags": hashtags[:5],
            "estimated_reach": {
                hashtag: {
                    "popularity": "high",
                    "competition": "medium",
                    "estimated_reach": 100000
                }
                for hashtag in hashtags
            },
            "recommendations": [
                "Mix popular and niche hashtags",
                "Use platform-specific trending tags",
                "Rotate hashtags regularly"
            ]
        }

        return analysis
