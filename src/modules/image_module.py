"""
Image Module
AI-powered image generation, editing, and manipulation
"""

import logging
import asyncio
from pathlib import Path
from typing import Optional, Tuple, List, Dict, Any
from datetime import datetime
from PIL import Image, ImageEnhance, ImageFilter, ImageDraw, ImageFont
import numpy as np
import cv2
from io import BytesIO
import requests

logger = logging.getLogger(__name__)


class ImageEffects:
    """Image effects and filters"""

    @staticmethod
    def apply_blur(image: Image.Image, radius: int = 5) -> Image.Image:
        """Apply Gaussian blur"""
        return image.filter(ImageFilter.GaussianBlur(radius))

    @staticmethod
    def apply_sharpen(image: Image.Image) -> Image.Image:
        """Apply sharpen filter"""
        return image.filter(ImageFilter.SHARPEN)

    @staticmethod
    def apply_edge_enhance(image: Image.Image) -> Image.Image:
        """Enhance edges"""
        return image.filter(ImageFilter.EDGE_ENHANCE)

    @staticmethod
    def apply_emboss(image: Image.Image) -> Image.Image:
        """Apply emboss effect"""
        return image.filter(ImageFilter.EMBOSS)

    @staticmethod
    def adjust_brightness(image: Image.Image, factor: float = 1.5) -> Image.Image:
        """Adjust brightness (factor > 1 = brighter, < 1 = darker)"""
        enhancer = ImageEnhance.Brightness(image)
        return enhancer.enhance(factor)

    @staticmethod
    def adjust_contrast(image: Image.Image, factor: float = 1.5) -> Image.Image:
        """Adjust contrast"""
        enhancer = ImageEnhance.Contrast(image)
        return enhancer.enhance(factor)

    @staticmethod
    def adjust_saturation(image: Image.Image, factor: float = 1.5) -> Image.Image:
        """Adjust color saturation"""
        enhancer = ImageEnhance.Color(image)
        return enhancer.enhance(factor)

    @staticmethod
    def grayscale(image: Image.Image) -> Image.Image:
        """Convert to grayscale"""
        return image.convert('L').convert('RGB')

    @staticmethod
    def sepia(image: Image.Image) -> Image.Image:
        """Apply sepia tone"""
        img_array = np.array(image)
        sepia_filter = np.array([[0.393, 0.769, 0.189],
                                [0.349, 0.686, 0.168],
                                [0.272, 0.534, 0.131]])
        sepia_img = cv2.transform(img_array, sepia_filter)
        sepia_img = np.clip(sepia_img, 0, 255)
        return Image.fromarray(sepia_img.astype(np.uint8))

    @staticmethod
    def vignette(image: Image.Image, intensity: float = 0.5) -> Image.Image:
        """Apply vignette effect"""
        img_array = np.array(image)
        rows, cols = img_array.shape[:2]

        # Create vignette mask
        X_resultant_kernel = cv2.getGaussianKernel(cols, cols/2)
        Y_resultant_kernel = cv2.getGaussianKernel(rows, rows/2)
        kernel = Y_resultant_kernel * X_resultant_kernel.T
        mask = kernel / kernel.max()
        mask = np.stack([mask]*3, axis=2)

        # Apply vignette
        output = (img_array * (1 - intensity + intensity * mask)).astype(np.uint8)
        return Image.fromarray(output)

    @staticmethod
    def add_border(image: Image.Image, border_size: int = 20, color: Tuple[int, int, int] = (0, 0, 0)) -> Image.Image:
        """Add border to image"""
        width, height = image.size
        new_image = Image.new('RGB', (width + 2*border_size, height + 2*border_size), color)
        new_image.paste(image, (border_size, border_size))
        return new_image


class ImageGenerator:
    """AI-powered image generation and manipulation"""

    def __init__(self, output_dir: Optional[Path] = None):
        if output_dir is None:
            self.output_dir = Path(__file__).parent.parent.parent / "data" / "exports" / "images"
        else:
            self.output_dir = Path(output_dir)

        self.output_dir.mkdir(parents=True, exist_ok=True)
        logger.info(f"Image generator initialized. Output: {self.output_dir}")

    async def generate_ai_image(
        self,
        prompt: str,
        size: str = "1024x1024",
        quality: str = "hd",
        output_name: Optional[str] = None,
        api_client = None
    ) -> str:
        """Generate image using AI (DALL-E)"""
        logger.info(f"Generating AI image: {prompt}")

        try:
            if api_client is None:
                from ..api.ai_client import AIClientFactory
                api_client = AIClientFactory.get_client("openai")

            # Generate image URL
            image_url = await api_client.generate_image_prompt(prompt, size=size)

            # Download image
            response = await asyncio.to_thread(requests.get, image_url)
            image = Image.open(BytesIO(response.content))

            # Save image
            if output_name is None:
                output_name = f"ai_gen_{datetime.now().strftime('%Y%m%d_%H%M%S')}.png"

            output_path = self.output_dir / output_name
            await asyncio.to_thread(image.save, str(output_path), quality=95)

            logger.info(f"AI image generated: {output_path}")
            return str(output_path)

        except Exception as e:
            logger.error(f"Failed to generate AI image: {e}")
            raise

    async def resize_image(
        self,
        image_path: str,
        size: Tuple[int, int],
        maintain_aspect: bool = True,
        output_name: Optional[str] = None
    ) -> str:
        """Resize image"""
        logger.info(f"Resizing image to {size}")

        try:
            image = Image.open(image_path)

            if maintain_aspect:
                image.thumbnail(size, Image.Resampling.LANCZOS)
            else:
                image = image.resize(size, Image.Resampling.LANCZOS)

            if output_name is None:
                output_name = f"resized_{datetime.now().strftime('%Y%m%d_%H%M%S')}.png"

            output_path = self.output_dir / output_name
            await asyncio.to_thread(image.save, str(output_path), quality=95)

            logger.info(f"Image resized: {output_path}")
            return str(output_path)

        except Exception as e:
            logger.error(f"Failed to resize image: {e}")
            raise

    async def crop_image(
        self,
        image_path: str,
        box: Tuple[int, int, int, int],
        output_name: Optional[str] = None
    ) -> str:
        """Crop image (left, top, right, bottom)"""
        logger.info(f"Cropping image: {box}")

        try:
            image = Image.open(image_path)
            cropped = image.crop(box)

            if output_name is None:
                output_name = f"cropped_{datetime.now().strftime('%Y%m%d_%H%M%S')}.png"

            output_path = self.output_dir / output_name
            await asyncio.to_thread(cropped.save, str(output_path), quality=95)

            logger.info(f"Image cropped: {output_path}")
            return str(output_path)

        except Exception as e:
            logger.error(f"Failed to crop image: {e}")
            raise

    async def apply_filter(
        self,
        image_path: str,
        filter_type: str,
        output_name: Optional[str] = None,
        **kwargs
    ) -> str:
        """Apply filter to image"""
        logger.info(f"Applying {filter_type} filter")

        try:
            image = Image.open(image_path)

            filter_map = {
                "blur": lambda img: ImageEffects.apply_blur(img, kwargs.get('radius', 5)),
                "sharpen": ImageEffects.apply_sharpen,
                "edge_enhance": ImageEffects.apply_edge_enhance,
                "emboss": ImageEffects.apply_emboss,
                "grayscale": ImageEffects.grayscale,
                "sepia": ImageEffects.sepia,
                "vignette": lambda img: ImageEffects.vignette(img, kwargs.get('intensity', 0.5)),
                "brightness": lambda img: ImageEffects.adjust_brightness(img, kwargs.get('factor', 1.5)),
                "contrast": lambda img: ImageEffects.adjust_contrast(img, kwargs.get('factor', 1.5)),
                "saturation": lambda img: ImageEffects.adjust_saturation(img, kwargs.get('factor', 1.5))
            }

            if filter_type in filter_map:
                image = filter_map[filter_type](image)
            else:
                raise ValueError(f"Unknown filter type: {filter_type}")

            if output_name is None:
                output_name = f"{filter_type}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.png"

            output_path = self.output_dir / output_name
            await asyncio.to_thread(image.save, str(output_path), quality=95)

            logger.info(f"Filter applied: {output_path}")
            return str(output_path)

        except Exception as e:
            logger.error(f"Failed to apply filter: {e}")
            raise

    async def add_text(
        self,
        image_path: str,
        text: str,
        position: Tuple[int, int] = (50, 50),
        font_size: int = 40,
        color: Tuple[int, int, int] = (255, 255, 255),
        output_name: Optional[str] = None
    ) -> str:
        """Add text to image"""
        logger.info(f"Adding text to image: {text}")

        try:
            image = Image.open(image_path)
            draw = ImageDraw.Draw(image)

            # Try to use a nice font, fall back to default
            try:
                font = ImageFont.truetype("arial.ttf", font_size)
            except:
                font = ImageFont.load_default()

            draw.text(position, text, fill=color, font=font)

            if output_name is None:
                output_name = f"text_{datetime.now().strftime('%Y%m%d_%H%M%S')}.png"

            output_path = self.output_dir / output_name
            await asyncio.to_thread(image.save, str(output_path), quality=95)

            logger.info(f"Text added: {output_path}")
            return str(output_path)

        except Exception as e:
            logger.error(f"Failed to add text: {e}")
            raise

    async def create_collage(
        self,
        image_paths: List[str],
        grid_size: Tuple[int, int],
        output_size: Tuple[int, int] = (1920, 1080),
        output_name: Optional[str] = None
    ) -> str:
        """Create image collage"""
        logger.info(f"Creating collage with {len(image_paths)} images")

        try:
            rows, cols = grid_size
            cell_width = output_size[0] // cols
            cell_height = output_size[1] // rows

            collage = Image.new('RGB', output_size, (255, 255, 255))

            for idx, img_path in enumerate(image_paths[:rows * cols]):
                row = idx // cols
                col = idx % cols

                img = Image.open(img_path)
                img.thumbnail((cell_width, cell_height), Image.Resampling.LANCZOS)

                x = col * cell_width + (cell_width - img.width) // 2
                y = row * cell_height + (cell_height - img.height) // 2

                collage.paste(img, (x, y))

            if output_name is None:
                output_name = f"collage_{datetime.now().strftime('%Y%m%d_%H%M%S')}.png"

            output_path = self.output_dir / output_name
            await asyncio.to_thread(collage.save, str(output_path), quality=95)

            logger.info(f"Collage created: {output_path}")
            return str(output_path)

        except Exception as e:
            logger.error(f"Failed to create collage: {e}")
            raise

    async def remove_background(
        self,
        image_path: str,
        output_name: Optional[str] = None
    ) -> str:
        """Remove background (simplified version using edge detection)"""
        logger.info(f"Removing background from image")

        try:
            # Load image
            image = cv2.imread(image_path)
            gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)

            # Create mask using GrabCut
            mask = np.zeros(image.shape[:2], np.uint8)
            bgd_model = np.zeros((1, 65), np.float64)
            fgd_model = np.zeros((1, 65), np.float64)

            height, width = image.shape[:2]
            rect = (10, 10, width-10, height-10)

            cv2.grabCut(image, mask, rect, bgd_model, fgd_model, 5, cv2.GC_INIT_WITH_RECT)

            mask2 = np.where((mask == 2) | (mask == 0), 0, 1).astype('uint8')
            result = image * mask2[:, :, np.newaxis]

            # Convert to PIL Image with transparency
            result_rgba = cv2.cvtColor(result, cv2.COLOR_BGR2RGBA)
            result_rgba[:, :, 3] = mask2 * 255

            result_image = Image.fromarray(result_rgba)

            if output_name is None:
                output_name = f"nobg_{datetime.now().strftime('%Y%m%d_%H%M%S')}.png"

            output_path = self.output_dir / output_name
            await asyncio.to_thread(result_image.save, str(output_path))

            logger.info(f"Background removed: {output_path}")
            return str(output_path)

        except Exception as e:
            logger.error(f"Failed to remove background: {e}")
            raise

    async def get_image_info(self, image_path: str) -> Dict[str, Any]:
        """Get image information"""
        try:
            image = Image.open(image_path)

            return {
                "size": image.size,
                "width": image.width,
                "height": image.height,
                "format": image.format,
                "mode": image.mode,
                "file_size": Path(image_path).stat().st_size
            }

        except Exception as e:
            logger.error(f"Failed to get image info: {e}")
            return {}

    async def optimize_for_platform(
        self,
        image_path: str,
        platform: str,
        output_name: Optional[str] = None
    ) -> str:
        """Optimize image for specific social media platform"""
        logger.info(f"Optimizing image for {platform}")

        platform_specs = {
            "instagram_post": (1080, 1080),
            "instagram_story": (1080, 1920),
            "tiktok": (1080, 1920),
            "youtube_thumbnail": (1280, 720),
            "twitter_post": (1200, 675),
            "facebook_post": (1200, 630)
        }

        try:
            if platform not in platform_specs:
                raise ValueError(f"Unknown platform: {platform}")

            size = platform_specs[platform]
            image = Image.open(image_path)

            # Resize to platform specs
            image.thumbnail(size, Image.Resampling.LANCZOS)

            # Create canvas of exact size
            canvas = Image.new('RGB', size, (255, 255, 255))
            offset_x = (size[0] - image.width) // 2
            offset_y = (size[1] - image.height) // 2
            canvas.paste(image, (offset_x, offset_y))

            if output_name is None:
                output_name = f"{platform}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.jpg"

            output_path = self.output_dir / output_name
            await asyncio.to_thread(canvas.save, str(output_path), quality=95)

            logger.info(f"Image optimized for {platform}: {output_path}")
            return str(output_path)

        except Exception as e:
            logger.error(f"Failed to optimize image: {e}")
            raise
