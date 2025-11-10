"""
Helper utilities
Common utility functions used across the application
"""

import os
import hashlib
import json
from pathlib import Path
from typing import Any, Dict, List, Optional
from datetime import datetime
import logging

logger = logging.getLogger(__name__)


def ensure_dir(directory: str) -> Path:
    """Ensure directory exists"""
    path = Path(directory)
    path.mkdir(parents=True, exist_ok=True)
    return path


def get_file_hash(file_path: str) -> str:
    """Calculate file hash"""
    hasher = hashlib.sha256()
    with open(file_path, 'rb') as f:
        for chunk in iter(lambda: f.read(4096), b''):
            hasher.update(chunk)
    return hasher.hexdigest()


def format_file_size(size_bytes: int) -> str:
    """Format file size to human readable"""
    for unit in ['B', 'KB', 'MB', 'GB', 'TB']:
        if size_bytes < 1024.0:
            return f"{size_bytes:.1f} {unit}"
        size_bytes /= 1024.0
    return f"{size_bytes:.1f} PB"


def format_duration(seconds: float) -> str:
    """Format duration to MM:SS"""
    mins, secs = divmod(int(seconds), 60)
    return f"{mins:02d}:{secs:02d}"


def sanitize_filename(filename: str) -> str:
    """Sanitize filename for safe file system usage"""
    invalid_chars = '<>:"/\\|?*'
    for char in invalid_chars:
        filename = filename.replace(char, '_')
    return filename


def load_json(file_path: str) -> Dict[str, Any]:
    """Load JSON file"""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            return json.load(f)
    except Exception as e:
        logger.error(f"Failed to load JSON from {file_path}: {e}")
        return {}


def save_json(data: Dict[str, Any], file_path: str) -> bool:
    """Save data to JSON file"""
    try:
        with open(file_path, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2)
        return True
    except Exception as e:
        logger.error(f"Failed to save JSON to {file_path}: {e}")
        return False


def timestamp() -> str:
    """Get current timestamp string"""
    return datetime.now().strftime('%Y%m%d_%H%M%S')


def is_valid_url(url: str) -> bool:
    """Check if string is valid URL"""
    import re
    url_pattern = re.compile(
        r'^https?://'  # http:// or https://
        r'(?:(?:[A-Z0-9](?:[A-Z0-9-]{0,61}[A-Z0-9])?\.)+[A-Z]{2,6}\.?|'  # domain...
        r'localhost|'  # localhost...
        r'\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3})'  # ...or ip
        r'(?::\d+)?'  # optional port
        r'(?:/?|[/?]\S+)$', re.IGNORECASE)
    return url_pattern.match(url) is not None


def truncate_text(text: str, max_length: int = 100, suffix: str = "...") -> str:
    """Truncate text to max length"""
    if len(text) <= max_length:
        return text
    return text[:max_length - len(suffix)] + suffix


def parse_resolution(resolution: str) -> tuple:
    """Parse resolution string to (width, height)"""
    try:
        width, height = resolution.split('x')
        return int(width), int(height)
    except:
        return 1920, 1080  # Default


def calculate_aspect_ratio(width: int, height: int) -> str:
    """Calculate aspect ratio"""
    from math import gcd
    divisor = gcd(width, height)
    return f"{width//divisor}:{height//divisor}"


class Timer:
    """Simple timer context manager"""

    def __init__(self, name: str = "Operation"):
        self.name = name
        self.start_time = None

    def __enter__(self):
        self.start_time = datetime.now()
        logger.debug(f"{self.name} started")
        return self

    def __exit__(self, *args):
        duration = (datetime.now() - self.start_time).total_seconds()
        logger.debug(f"{self.name} completed in {duration:.2f}s")


def batch_process(items: List[Any], batch_size: int = 10):
    """Generator for batch processing"""
    for i in range(0, len(items), batch_size):
        yield items[i:i + batch_size]
