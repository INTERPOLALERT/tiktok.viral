"""
CreatorStudio AI - Main Entry Point
Professional Content Creation Suite

Run this file to start the application.
"""

import sys
import os
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent))

from src.core.logger import log_manager, get_logger
from src.core.config import config
from src.database.models import get_db_manager
from src.ui.main_window import launch_app

logger = get_logger(__name__)


def initialize_application():
    """Initialize application components"""
    logger.info("Initializing CreatorStudio AI...")

    try:
        # Initialize configuration
        logger.info(f"Loading configuration...")
        app_config = config.get_all()
        logger.info(f"Configuration loaded: {len(app_config)} settings")

        # Initialize database
        logger.info("Initializing database...")
        db = get_db_manager()
        logger.info("Database initialized successfully")

        # Create necessary directories
        base_dir = Path(__file__).parent
        for directory in ['data', 'data/projects', 'data/exports', 'data/cache', 'logs']:
            (base_dir / directory).mkdir(parents=True, exist_ok=True)

        logger.info("Application initialization complete")
        return True

    except Exception as e:
        logger.error(f"Application initialization failed: {e}")
        return False


def main():
    """Main application entry point"""
    logger.info("=" * 80)
    logger.info("CreatorStudio AI - Professional Content Creation Suite")
    logger.info("Version: 1.0.0")
    logger.info("=" * 80)

    # Initialize
    if not initialize_application():
        logger.error("Failed to initialize application. Exiting.")
        sys.exit(1)

    # Display welcome message
    print("\n" + "=" * 80)
    print("CreatorStudio AI - Professional Content Creation Suite".center(80))
    print("Version 1.0.0".center(80))
    print("=" * 80)
    print("\nAI-Powered Tools:")
    print("  • Video Generation & Editing")
    print("  • Image Creation & Manipulation")
    print("  • Script Writing & Optimization")
    print("  • Voice Synthesis & Audio Processing")
    print("  • Social Media Management & Scheduling")
    print("  • Advanced Analytics & Insights")
    print("  • Real-Time Trend Analysis")
    print("  • Project Management & Workflows")

    # Check if API keys are configured
    api_key = config.get_secret('openai_api_key')
    if not api_key:
        print("\n" + "⚠" * 40)
        print("  NOTE: AI features require API key configuration")
        print("  Go to Settings tab to add your OpenAI API key")
        print("  You can still explore the app and use non-AI features!")
        print("⚠" * 40)

    print("\nLaunching application...")
    print("=" * 80 + "\n")

    try:
        # Launch GUI
        logger.info("Launching GUI application...")
        launch_app()

    except KeyboardInterrupt:
        logger.info("Application interrupted by user")
        print("\n\nApplication closed by user.")

    except Exception as e:
        logger.error(f"Application error: {e}", exc_info=True)
        print(f"\n\nError: {e}")
        sys.exit(1)

    finally:
        logger.info("Application shutdown complete")
        print("\nThank you for using CreatorStudio AI!")


if __name__ == "__main__":
    main()
