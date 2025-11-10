"""
Utility wrapper for AI features with graceful fallbacks
"""

import logging
from typing import Optional

logger = logging.getLogger(__name__)


def check_api_key_configured() -> bool:
    """Check if API key is configured"""
    try:
        from ..core.config import config
        api_key = config.get_secret('openai_api_key')
        return api_key is not None and len(api_key) > 0
    except:
        return False


def get_ai_client_safe(provider: str = "openai"):
    """Get AI client with error handling for missing API keys"""
    try:
        from ..api.ai_client import AIClientFactory
        from ..core.config import config

        # Get API key from config
        if provider == "openai":
            api_key = config.get_secret('openai_api_key')
        elif provider == "anthropic":
            api_key = config.get_secret('anthropic_api_key')
        else:
            api_key = None

        if not api_key:
            logger.warning(f"No API key configured for {provider}")
            return None

        return AIClientFactory.get_client(provider, api_key)

    except Exception as e:
        logger.error(f"Failed to initialize AI client: {e}")
        return None


def show_api_key_warning():
    """Show warning about missing API key"""
    from PyQt6.QtWidgets import QMessageBox

    msg = QMessageBox()
    msg.setIcon(QMessageBox.Icon.Warning)
    msg.setWindowTitle("API Key Required")
    msg.setText("AI features require an API key")
    msg.setInformativeText(
        "To use AI-powered features, please:\n\n"
        "1. Go to the Settings tab\n"
        "2. Enter your OpenAI API key\n"
        "3. Click 'Save Settings'\n\n"
        "Get your API key from:\nhttps://platform.openai.com/api-keys"
    )
    msg.setStandardButtons(QMessageBox.StandardButton.Ok)
    msg.exec()


def require_api_key(func):
    """Decorator to check for API key before executing AI features"""
    def wrapper(*args, **kwargs):
        if not check_api_key_configured():
            show_api_key_warning()
            return None
        return func(*args, **kwargs)
    return wrapper
