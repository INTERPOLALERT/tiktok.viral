"""
Video Module
AI-powered video generation, editing, and processing
"""

import logging
import asyncio
from pathlib import Path
from typing import List, Optional, Dict, Any, Tuple
from datetime import datetime
import cv2
import numpy as np
# MoviePy 2.x imports
try:
    from moviepy.video.io.VideoFileClip import VideoFileClip
    from moviepy.video.VideoClip import ImageClip, TextClip, ColorClip
    from moviepy.video.compositing.CompositeVideoClip import CompositeVideoClip, concatenate_videoclips
    from moviepy.audio.io.AudioFileClip import AudioFileClip
except ImportError:
    # Fallback to moviepy 1.x imports
    from moviepy.editor import (
        VideoFileClip, ImageClip, concatenate_videoclips,
        CompositeVideoClip, TextClip, AudioFileClip, ColorClip
    )
from PIL import Image
import json

logger = logging.getLogger(__name__)


class VideoEffect:
    """Video effects and transitions"""

    @staticmethod
    def fade_in(clip, duration: float = 1.0):
        """Fade in effect"""
        return clip.fadein(duration)

    @staticmethod
    def fade_out(clip, duration: float = 1.0):
        """Fade out effect"""
        return clip.fadeout(duration)

    @staticmethod
    def crossfade(clip1, clip2, duration: float = 1.0):
        """Crossfade between two clips"""
        return concatenate_videoclips([clip1, clip2], method="compose", padding=-duration)

    @staticmethod
    def zoom_in(clip, zoom_ratio: float = 1.5):
        """Zoom in effect"""
        def zoom(t):
            factor = 1 + (zoom_ratio - 1) * (t / clip.duration)
            return factor
        return clip.resize(zoom)

    @staticmethod
    def blur_effect(frame, intensity: int = 15):
        """Apply blur effect to frame"""
        return cv2.GaussianBlur(frame, (intensity, intensity), 0)

    @staticmethod
    def grayscale(frame):
        """Convert frame to grayscale"""
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        return cv2.cvtColor(gray, cv2.COLOR_GRAY2BGR)

    @staticmethod
    def sepia(frame):
        """Apply sepia tone effect"""
        kernel = np.array([[0.272, 0.534, 0.131],
                          [0.349, 0.686, 0.168],
                          [0.393, 0.769, 0.189]])
        return cv2.transform(frame, kernel)

    @staticmethod
    def vignette(frame, intensity: float = 0.5):
        """Apply vignette effect"""
        rows, cols = frame.shape[:2]
        X_resultant_kernel = cv2.getGaussianKernel(cols, cols/2)
        Y_resultant_kernel = cv2.getGaussianKernel(rows, rows/2)
        kernel = Y_resultant_kernel * X_resultant_kernel.T
        mask = kernel / kernel.max()
        mask = np.stack([mask]*3, axis=2)
        return (frame * (1 - intensity + intensity * mask)).astype(np.uint8)


class VideoGenerator:
    """AI-powered video generation and editing"""

    def __init__(self, output_dir: Optional[Path] = None):
        if output_dir is None:
            self.output_dir = Path(__file__).parent.parent.parent / "data" / "exports" / "videos"
        else:
            self.output_dir = Path(output_dir)

        self.output_dir.mkdir(parents=True, exist_ok=True)
        logger.info(f"Video generator initialized. Output: {self.output_dir}")

    async def create_video_from_images(
        self,
        image_paths: List[str],
        duration_per_image: float = 3.0,
        transition: str = "fade",
        transition_duration: float = 1.0,
        audio_path: Optional[str] = None,
        output_name: Optional[str] = None,
        resolution: Tuple[int, int] = (1920, 1080),
        fps: int = 30
    ) -> str:
        """Create video from series of images"""
        logger.info(f"Creating video from {len(image_paths)} images")

        try:
            clips = []
            for img_path in image_paths:
                clip = ImageClip(img_path, duration=duration_per_image)
                clip = clip.resize(resolution)

                if transition == "fade":
                    clip = VideoEffect.fade_in(clip, transition_duration / 2)
                    clip = VideoEffect.fade_out(clip, transition_duration / 2)

                clips.append(clip)

            # Concatenate clips
            if transition == "crossfade":
                final_clip = clips[0]
                for clip in clips[1:]:
                    final_clip = VideoEffect.crossfade(final_clip, clip, transition_duration)
            else:
                final_clip = concatenate_videoclips(clips, method="compose")

            # Add audio if provided
            if audio_path:
                audio = AudioFileClip(audio_path)
                final_clip = final_clip.set_audio(audio)

            # Generate output filename
            if output_name is None:
                output_name = f"video_{datetime.now().strftime('%Y%m%d_%H%M%S')}.mp4"

            output_path = self.output_dir / output_name

            # Write video file
            await asyncio.to_thread(
                final_clip.write_videofile,
                str(output_path),
                fps=fps,
                codec='libx264',
                audio_codec='aac',
                preset='medium',
                logger=None  # Suppress moviepy logs
            )

            logger.info(f"Video created successfully: {output_path}")
            return str(output_path)

        except Exception as e:
            logger.error(f"Failed to create video: {e}")
            raise

    async def add_text_overlay(
        self,
        video_path: str,
        text: str,
        position: Tuple[int, int] = (100, 100),
        font_size: int = 50,
        color: str = 'white',
        duration: Optional[float] = None,
        output_name: Optional[str] = None
    ) -> str:
        """Add text overlay to video"""
        logger.info(f"Adding text overlay to {video_path}")

        try:
            video = VideoFileClip(video_path)

            if duration is None:
                duration = video.duration

            # Create text clip
            txt_clip = TextClip(
                text,
                fontsize=font_size,
                color=color,
                font='Arial-Bold'
            ).set_position(position).set_duration(duration)

            # Composite video with text
            final_clip = CompositeVideoClip([video, txt_clip])

            # Generate output filename
            if output_name is None:
                output_name = f"text_overlay_{datetime.now().strftime('%Y%m%d_%H%M%S')}.mp4"

            output_path = self.output_dir / output_name

            # Write video file
            await asyncio.to_thread(
                final_clip.write_videofile,
                str(output_path),
                codec='libx264',
                audio_codec='aac',
                logger=None
            )

            logger.info(f"Text overlay added successfully: {output_path}")
            return str(output_path)

        except Exception as e:
            logger.error(f"Failed to add text overlay: {e}")
            raise

    async def apply_filter(
        self,
        video_path: str,
        filter_type: str = "none",
        output_name: Optional[str] = None
    ) -> str:
        """Apply filter to video"""
        logger.info(f"Applying {filter_type} filter to {video_path}")

        try:
            video = VideoFileClip(video_path)

            filter_map = {
                "grayscale": VideoEffect.grayscale,
                "sepia": VideoEffect.sepia,
                "blur": lambda f: VideoEffect.blur_effect(f, 15),
                "vignette": lambda f: VideoEffect.vignette(f, 0.5)
            }

            if filter_type in filter_map:
                video = video.fl_image(filter_map[filter_type])

            # Generate output filename
            if output_name is None:
                output_name = f"{filter_type}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.mp4"

            output_path = self.output_dir / output_name

            # Write video file
            await asyncio.to_thread(
                video.write_videofile,
                str(output_path),
                codec='libx264',
                audio_codec='aac',
                logger=None
            )

            logger.info(f"Filter applied successfully: {output_path}")
            return str(output_path)

        except Exception as e:
            logger.error(f"Failed to apply filter: {e}")
            raise

    async def trim_video(
        self,
        video_path: str,
        start_time: float,
        end_time: float,
        output_name: Optional[str] = None
    ) -> str:
        """Trim video to specific time range"""
        logger.info(f"Trimming video from {start_time}s to {end_time}s")

        try:
            video = VideoFileClip(video_path).subclip(start_time, end_time)

            if output_name is None:
                output_name = f"trimmed_{datetime.now().strftime('%Y%m%d_%H%M%S')}.mp4"

            output_path = self.output_dir / output_name

            await asyncio.to_thread(
                video.write_videofile,
                str(output_path),
                codec='libx264',
                audio_codec='aac',
                logger=None
            )

            logger.info(f"Video trimmed successfully: {output_path}")
            return str(output_path)

        except Exception as e:
            logger.error(f"Failed to trim video: {e}")
            raise

    async def merge_videos(
        self,
        video_paths: List[str],
        output_name: Optional[str] = None
    ) -> str:
        """Merge multiple videos"""
        logger.info(f"Merging {len(video_paths)} videos")

        try:
            clips = [VideoFileClip(path) for path in video_paths]
            final_clip = concatenate_videoclips(clips)

            if output_name is None:
                output_name = f"merged_{datetime.now().strftime('%Y%m%d_%H%M%S')}.mp4"

            output_path = self.output_dir / output_name

            await asyncio.to_thread(
                final_clip.write_videofile,
                str(output_path),
                codec='libx264',
                audio_codec='aac',
                logger=None
            )

            logger.info(f"Videos merged successfully: {output_path}")
            return str(output_path)

        except Exception as e:
            logger.error(f"Failed to merge videos: {e}")
            raise

    async def extract_thumbnail(
        self,
        video_path: str,
        time_position: float = 1.0,
        output_name: Optional[str] = None
    ) -> str:
        """Extract thumbnail from video"""
        logger.info(f"Extracting thumbnail from {video_path}")

        try:
            video = VideoFileClip(video_path)
            frame = video.get_frame(time_position)

            if output_name is None:
                output_name = f"thumb_{datetime.now().strftime('%Y%m%d_%H%M%S')}.jpg"

            output_path = self.output_dir.parent / "images" / output_name
            output_path.parent.mkdir(parents=True, exist_ok=True)

            Image.fromarray(frame).save(output_path, quality=95)

            logger.info(f"Thumbnail extracted: {output_path}")
            return str(output_path)

        except Exception as e:
            logger.error(f"Failed to extract thumbnail: {e}")
            raise

    async def get_video_info(self, video_path: str) -> Dict[str, Any]:
        """Get video information"""
        try:
            video = VideoFileClip(video_path)

            info = {
                "duration": video.duration,
                "fps": video.fps,
                "size": video.size,
                "resolution": f"{video.w}x{video.h}",
                "has_audio": video.audio is not None,
                "file_size": Path(video_path).stat().st_size
            }

            video.close()
            return info

        except Exception as e:
            logger.error(f"Failed to get video info: {e}")
            return {}

    async def create_intro_video(
        self,
        title: str,
        subtitle: Optional[str] = None,
        duration: float = 5.0,
        background_color: Tuple[int, int, int] = (0, 0, 0),
        output_name: Optional[str] = None
    ) -> str:
        """Create intro video with text"""
        logger.info(f"Creating intro video: {title}")

        try:
            # Create background
            bg = ColorClip(size=(1920, 1080), color=background_color, duration=duration)

            # Create title
            title_clip = TextClip(
                title,
                fontsize=80,
                color='white',
                font='Arial-Bold'
            ).set_position('center').set_duration(duration)

            clips = [bg, title_clip]

            # Add subtitle if provided
            if subtitle:
                subtitle_clip = TextClip(
                    subtitle,
                    fontsize=40,
                    color='white',
                    font='Arial'
                ).set_position(('center', 700)).set_duration(duration)
                clips.append(subtitle_clip)

            final_clip = CompositeVideoClip(clips)

            if output_name is None:
                output_name = f"intro_{datetime.now().strftime('%Y%m%d_%H%M%S')}.mp4"

            output_path = self.output_dir / output_name

            await asyncio.to_thread(
                final_clip.write_videofile,
                str(output_path),
                fps=30,
                codec='libx264',
                logger=None
            )

            logger.info(f"Intro video created: {output_path}")
            return str(output_path)

        except Exception as e:
            logger.error(f"Failed to create intro video: {e}")
            raise
