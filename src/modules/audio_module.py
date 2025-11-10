"""
Audio Module
Voice synthesis, audio editing, and processing
"""

import logging
import asyncio
from pathlib import Path
from typing import Optional, List, Dict, Any
from datetime import datetime
import pyttsx3
from pydub import AudioSegment
from pydub.effects import normalize, compress_dynamic_range
import numpy as np

logger = logging.getLogger(__name__)


class VoiceSynthesizer:
    """Text-to-speech voice synthesis"""

    def __init__(self):
        self.engine = pyttsx3.init()
        self.voices = self.engine.getProperty('voices')
        logger.info(f"Voice synthesizer initialized with {len(self.voices)} voices")

    def list_voices(self) -> List[Dict[str, str]]:
        """List available voices"""
        return [
            {
                "id": voice.id,
                "name": voice.name,
                "languages": voice.languages,
                "gender": getattr(voice, 'gender', 'unknown')
            }
            for voice in self.voices
        ]

    def set_voice(self, voice_id: Optional[str] = None, gender: Optional[str] = None):
        """Set voice by ID or gender"""
        if voice_id:
            self.engine.setProperty('voice', voice_id)
        elif gender:
            gender = gender.lower()
            for voice in self.voices:
                if gender in voice.name.lower() or (hasattr(voice, 'gender') and voice.gender == gender):
                    self.engine.setProperty('voice', voice.id)
                    break

    def set_rate(self, rate: int = 200):
        """Set speech rate (words per minute)"""
        self.engine.setProperty('rate', rate)

    def set_volume(self, volume: float = 1.0):
        """Set volume (0.0 to 1.0)"""
        self.engine.setProperty('volume', volume)

    async def synthesize(
        self,
        text: str,
        output_path: str,
        rate: int = 200,
        volume: float = 1.0
    ):
        """Synthesize text to audio file"""
        logger.info(f"Synthesizing text to audio: {len(text)} characters")

        self.set_rate(rate)
        self.set_volume(volume)

        def _save():
            self.engine.save_to_file(text, output_path)
            self.engine.runAndWait()

        await asyncio.to_thread(_save)
        logger.info(f"Audio synthesized: {output_path}")


class AudioProcessor:
    """Audio editing and processing"""

    def __init__(self, output_dir: Optional[Path] = None):
        if output_dir is None:
            self.output_dir = Path(__file__).parent.parent.parent / "data" / "exports" / "audio"
        else:
            self.output_dir = Path(output_dir)

        self.output_dir.mkdir(parents=True, exist_ok=True)
        self.synthesizer = VoiceSynthesizer()
        logger.info(f"Audio processor initialized. Output: {self.output_dir}")

    async def text_to_speech(
        self,
        text: str,
        voice: str = "default",
        rate: int = 200,
        output_name: Optional[str] = None
    ) -> str:
        """Convert text to speech"""
        logger.info("Converting text to speech")

        try:
            if output_name is None:
                output_name = f"tts_{datetime.now().strftime('%Y%m%d_%H%M%S')}.mp3"

            output_path = self.output_dir / output_name

            # Synthesize speech
            temp_wav = self.output_dir / "temp.wav"
            await self.synthesizer.synthesize(text, str(temp_wav), rate)

            # Convert to MP3
            audio = AudioSegment.from_wav(str(temp_wav))
            await asyncio.to_thread(audio.export, str(output_path), format="mp3", bitrate="320k")

            # Clean up temp file
            temp_wav.unlink(missing_ok=True)

            logger.info(f"Text-to-speech complete: {output_path}")
            return str(output_path)

        except Exception as e:
            logger.error(f"Failed to convert text to speech: {e}")
            raise

    async def merge_audio(
        self,
        audio_paths: List[str],
        output_name: Optional[str] = None
    ) -> str:
        """Merge multiple audio files"""
        logger.info(f"Merging {len(audio_paths)} audio files")

        try:
            combined = AudioSegment.empty()

            for path in audio_paths:
                audio = AudioSegment.from_file(path)
                combined += audio

            if output_name is None:
                output_name = f"merged_{datetime.now().strftime('%Y%m%d_%H%M%S')}.mp3"

            output_path = self.output_dir / output_name
            await asyncio.to_thread(combined.export, str(output_path), format="mp3", bitrate="320k")

            logger.info(f"Audio merged: {output_path}")
            return str(output_path)

        except Exception as e:
            logger.error(f"Failed to merge audio: {e}")
            raise

    async def trim_audio(
        self,
        audio_path: str,
        start_ms: int,
        end_ms: int,
        output_name: Optional[str] = None
    ) -> str:
        """Trim audio to specific time range"""
        logger.info(f"Trimming audio from {start_ms}ms to {end_ms}ms")

        try:
            audio = AudioSegment.from_file(audio_path)
            trimmed = audio[start_ms:end_ms]

            if output_name is None:
                output_name = f"trimmed_{datetime.now().strftime('%Y%m%d_%H%M%S')}.mp3"

            output_path = self.output_dir / output_name
            await asyncio.to_thread(trimmed.export, str(output_path), format="mp3", bitrate="320k")

            logger.info(f"Audio trimmed: {output_path}")
            return str(output_path)

        except Exception as e:
            logger.error(f"Failed to trim audio: {e}")
            raise

    async def adjust_volume(
        self,
        audio_path: str,
        gain_db: float,
        output_name: Optional[str] = None
    ) -> str:
        """Adjust audio volume"""
        logger.info(f"Adjusting volume by {gain_db}dB")

        try:
            audio = AudioSegment.from_file(audio_path)
            adjusted = audio + gain_db

            if output_name is None:
                output_name = f"volume_{datetime.now().strftime('%Y%m%d_%H%M%S')}.mp3"

            output_path = self.output_dir / output_name
            await asyncio.to_thread(adjusted.export, str(output_path), format="mp3", bitrate="320k")

            logger.info(f"Volume adjusted: {output_path}")
            return str(output_path)

        except Exception as e:
            logger.error(f"Failed to adjust volume: {e}")
            raise

    async def normalize_audio(
        self,
        audio_path: str,
        output_name: Optional[str] = None
    ) -> str:
        """Normalize audio levels"""
        logger.info("Normalizing audio")

        try:
            audio = AudioSegment.from_file(audio_path)
            normalized = normalize(audio)

            if output_name is None:
                output_name = f"normalized_{datetime.now().strftime('%Y%m%d_%H%M%S')}.mp3"

            output_path = self.output_dir / output_name
            await asyncio.to_thread(normalized.export, str(output_path), format="mp3", bitrate="320k")

            logger.info(f"Audio normalized: {output_path}")
            return str(output_path)

        except Exception as e:
            logger.error(f"Failed to normalize audio: {e}")
            raise

    async def apply_fade(
        self,
        audio_path: str,
        fade_in_ms: int = 1000,
        fade_out_ms: int = 1000,
        output_name: Optional[str] = None
    ) -> str:
        """Apply fade in/out effects"""
        logger.info(f"Applying fade: in={fade_in_ms}ms, out={fade_out_ms}ms")

        try:
            audio = AudioSegment.from_file(audio_path)
            faded = audio.fade_in(fade_in_ms).fade_out(fade_out_ms)

            if output_name is None:
                output_name = f"faded_{datetime.now().strftime('%Y%m%d_%H%M%S')}.mp3"

            output_path = self.output_dir / output_name
            await asyncio.to_thread(faded.export, str(output_path), format="mp3", bitrate="320k")

            logger.info(f"Fade applied: {output_path}")
            return str(output_path)

        except Exception as e:
            logger.error(f"Failed to apply fade: {e}")
            raise

    async def change_speed(
        self,
        audio_path: str,
        speed_factor: float = 1.0,
        output_name: Optional[str] = None
    ) -> str:
        """Change audio playback speed"""
        logger.info(f"Changing speed by factor {speed_factor}")

        try:
            audio = AudioSegment.from_file(audio_path)

            # Change frame rate to adjust speed
            new_sample_rate = int(audio.frame_rate * speed_factor)
            adjusted = audio._spawn(audio.raw_data, overrides={'frame_rate': new_sample_rate})
            adjusted = adjusted.set_frame_rate(audio.frame_rate)

            if output_name is None:
                output_name = f"speed_{datetime.now().strftime('%Y%m%d_%H%M%S')}.mp3"

            output_path = self.output_dir / output_name
            await asyncio.to_thread(adjusted.export, str(output_path), format="mp3", bitrate="320k")

            logger.info(f"Speed changed: {output_path}")
            return str(output_path)

        except Exception as e:
            logger.error(f"Failed to change speed: {e}")
            raise

    async def add_background_music(
        self,
        voice_path: str,
        music_path: str,
        music_volume_reduction_db: float = 20,
        output_name: Optional[str] = None
    ) -> str:
        """Add background music to voice track"""
        logger.info("Adding background music")

        try:
            voice = AudioSegment.from_file(voice_path)
            music = AudioSegment.from_file(music_path)

            # Reduce music volume
            music = music - music_volume_reduction_db

            # Loop music if shorter than voice
            if len(music) < len(voice):
                repetitions = (len(voice) // len(music)) + 1
                music = music * repetitions

            # Trim music to voice length
            music = music[:len(voice)]

            # Overlay voice on music
            combined = music.overlay(voice)

            if output_name is None:
                output_name = f"with_music_{datetime.now().strftime('%Y%m%d_%H%M%S')}.mp3"

            output_path = self.output_dir / output_name
            await asyncio.to_thread(combined.export, str(output_path), format="mp3", bitrate="320k")

            logger.info(f"Background music added: {output_path}")
            return str(output_path)

        except Exception as e:
            logger.error(f"Failed to add background music: {e}")
            raise

    async def convert_format(
        self,
        audio_path: str,
        output_format: str = "mp3",
        bitrate: str = "320k",
        output_name: Optional[str] = None
    ) -> str:
        """Convert audio to different format"""
        logger.info(f"Converting audio to {output_format}")

        try:
            audio = AudioSegment.from_file(audio_path)

            if output_name is None:
                output_name = f"converted_{datetime.now().strftime('%Y%m%d_%H%M%S')}.{output_format}"

            output_path = self.output_dir / output_name
            await asyncio.to_thread(
                audio.export,
                str(output_path),
                format=output_format,
                bitrate=bitrate
            )

            logger.info(f"Format converted: {output_path}")
            return str(output_path)

        except Exception as e:
            logger.error(f"Failed to convert format: {e}")
            raise

    async def get_audio_info(self, audio_path: str) -> Dict[str, Any]:
        """Get audio file information"""
        try:
            audio = AudioSegment.from_file(audio_path)

            return {
                "duration_ms": len(audio),
                "duration_seconds": len(audio) / 1000,
                "channels": audio.channels,
                "sample_width": audio.sample_width,
                "frame_rate": audio.frame_rate,
                "frame_width": audio.frame_width,
                "file_size": Path(audio_path).stat().st_size
            }

        except Exception as e:
            logger.error(f"Failed to get audio info: {e}")
            return {}

    async def extract_audio_from_video(
        self,
        video_path: str,
        output_name: Optional[str] = None
    ) -> str:
        """Extract audio from video file"""
        logger.info(f"Extracting audio from video: {video_path}")

        try:
            from moviepy.editor import VideoFileClip

            video = VideoFileClip(video_path)

            if output_name is None:
                output_name = f"extracted_{datetime.now().strftime('%Y%m%d_%H%M%S')}.mp3"

            output_path = self.output_dir / output_name
            await asyncio.to_thread(video.audio.write_audiofile, str(output_path), logger=None)

            logger.info(f"Audio extracted: {output_path}")
            return str(output_path)

        except Exception as e:
            logger.error(f"Failed to extract audio: {e}")
            raise

    def list_available_voices(self) -> List[Dict[str, str]]:
        """List all available TTS voices"""
        return self.synthesizer.list_voices()
