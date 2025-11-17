#!/usr/bin/env python3
"""
Test script to validate all non-GUI imports and core functionality
"""
import sys
import traceback

print("=" * 80)
print("Testing CreatorStudio AI Core Components")
print("=" * 80)

errors = []
successes = []

# Test 1: Core config
print("\n1. Testing core configuration...")
try:
    from src.core.config import ConfigManager
    config = ConfigManager()
    successes.append("✓ Core config module (ConfigManager)")
except Exception as e:
    errors.append(f"✗ Core config: {e}")
    traceback.print_exc()

# Test 2: Core logger
print("\n2. Testing core logger...")
try:
    from src.core.logger import LogManager
    log_mgr = LogManager()
    successes.append("✓ Core logger module (LogManager)")
except Exception as e:
    errors.append(f"✗ Core logger: {e}")
    traceback.print_exc()

# Test 3: Database models
print("\n3. Testing database models...")
try:
    from src.database.models import (
        Project, Video, Image, Script, AudioFile,
        SocialMediaPost, Analytics, Trend, Template, APIKey,
        DatabaseManager
    )
    # Verify metadata was renamed to meta_data
    assert hasattr(Project, 'meta_data'), "Project should have meta_data attribute"
    successes.append("✓ Database models (metadata fix verified)")
except Exception as e:
    errors.append(f"✗ Database models: {e}")
    traceback.print_exc()

# Test 4: Database connection
print("\n4. Testing database connection...")
try:
    from src.database.models import DatabaseManager
    db = DatabaseManager()
    session = db.get_session()
    session.close()
    successes.append("✓ Database connection and session")
except Exception as e:
    errors.append(f"✗ Database connection: {e}")
    traceback.print_exc()

# Test 5: AI helpers
print("\n5. Testing AI helpers...")
try:
    from src.utils.ai_helpers import check_api_key_configured, get_ai_client_safe
    successes.append("✓ AI helpers module")
except Exception as e:
    errors.append(f"✗ AI helpers: {e}")
    traceback.print_exc()

# Test 6: All module imports (non-GUI)
print("\n6. Testing module imports...")
try:
    from src.modules.video_module import VideoGenerator
    successes.append("✓ Video module (VideoGenerator)")
except Exception as e:
    errors.append(f"✗ Video module: {e}")

try:
    from src.modules.image_module import ImageGenerator
    successes.append("✓ Image module (ImageGenerator)")
except Exception as e:
    errors.append(f"✗ Image module: {e}")

try:
    from src.modules.script_module import ScriptGenerator
    successes.append("✓ Script module (ScriptGenerator)")
except Exception as e:
    errors.append(f"✗ Script module: {e}")

try:
    from src.modules.audio_module import AudioProcessor
    successes.append("✓ Audio module (AudioProcessor)")
except Exception as e:
    errors.append(f"✗ Audio module: {e}")

try:
    from src.modules.social_media_module import SocialMediaScheduler
    successes.append("✓ Social Media module (SocialMediaScheduler)")
except Exception as e:
    errors.append(f"✗ Social Media module: {e}")

try:
    from src.modules.analytics_module import AnalyticsEngine
    successes.append("✓ Analytics module (AnalyticsEngine)")
except Exception as e:
    errors.append(f"✗ Analytics module: {e}")

try:
    from src.modules.trends_module import TrendAnalyzer
    successes.append("✓ Trends module (TrendAnalyzer)")
except Exception as e:
    errors.append(f"✗ Trends module: {e}")

try:
    from src.modules.project_module import ProjectManager
    successes.append("✓ Project module (ProjectManager)")
except Exception as e:
    errors.append(f"✗ Project module: {e}")

# Summary
print("\n" + "=" * 80)
print("TEST SUMMARY")
print("=" * 80)
print(f"\nSuccesses: {len(successes)}")
for s in successes:
    print(f"  {s}")

if errors:
    print(f"\nErrors: {len(errors)}")
    for e in errors:
        print(f"  {e}")
    print("\n❌ Some tests failed")
    sys.exit(1)
else:
    print("\n✅ All core components working correctly!")
    print("\nNote: GUI components (PyQt6) require system libraries (libEGL.so.1, etc.)")
    print("      that are not available in this headless Linux environment.")
    print("      The application is designed for Windows 11 with full GUI support.")
    sys.exit(0)
