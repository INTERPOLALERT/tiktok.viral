# CreatorStudio AI - Technical Documentation

## Table of Contents
1. [Architecture Overview](#architecture-overview)
2. [Module Documentation](#module-documentation)
3. [API Reference](#api-reference)
4. [Database Schema](#database-schema)
5. [Configuration](#configuration)
6. [Development Guide](#development-guide)

---

## Architecture Overview

### System Design

CreatorStudio AI follows a modular architecture with clear separation of concerns:

```
┌─────────────────────────────────────────────┐
│           User Interface (PyQt6)            │
│          src/ui/main_window.py              │
└────────────────┬────────────────────────────┘
                 │
┌────────────────┴────────────────────────────┐
│           Core Application Layer            │
│         src/core/{config,logger}            │
└────────────────┬────────────────────────────┘
                 │
┌────────────────┴────────────────────────────┐
│              Module Layer                   │
│  ┌──────────┬──────────┬──────────┬───────┐│
│  │  Video   │  Image   │  Script  │ Audio ││
│  ├──────────┼──────────┼──────────┼───────┤│
│  │ Social   │Analytics │ Trends   │Project││
│  └──────────┴──────────┴──────────┴───────┘│
└────────────────┬────────────────────────────┘
                 │
┌────────────────┴────────────────────────────┐
│          Data & External Services           │
│    ┌──────────┬──────────┬──────────┐      │
│    │ Database │ AI APIs  │ File I/O │      │
│    └──────────┴──────────┴──────────┘      │
└─────────────────────────────────────────────┘
```

### Design Patterns

1. **Factory Pattern**: AIClientFactory for creating AI client instances
2. **Singleton Pattern**: ConfigManager, DatabaseManager
3. **Repository Pattern**: Database models and session management
4. **Observer Pattern**: Logging system
5. **Strategy Pattern**: Different AI providers

### Technology Stack

#### Frontend
- **PyQt6**: Modern Qt bindings for Python
- **Custom Styling**: Dark/Light theme support

#### Backend
- **Python 3.9+**: Core language
- **AsyncIO**: Asynchronous operations
- **SQLAlchemy**: ORM for database

#### Processing Libraries
- **MoviePy**: Video processing
- **OpenCV**: Image processing
- **Pillow**: Image manipulation
- **pydub**: Audio processing

#### AI Integration
- **OpenAI API**: GPT-4, DALL-E
- **Anthropic API**: Claude (optional)

---

## Module Documentation

### 1. Video Module (`src/modules/video_module.py`)

#### VideoGenerator Class

**Purpose**: Handle video creation, editing, and processing

**Key Methods**:

```python
async def create_video_from_images(
    image_paths: List[str],
    duration_per_image: float = 3.0,
    transition: str = "fade",
    audio_path: Optional[str] = None,
    resolution: Tuple[int, int] = (1920, 1080),
    fps: int = 30
) -> str
```
Creates video from image sequence with transitions.

```python
async def add_text_overlay(
    video_path: str,
    text: str,
    position: Tuple[int, int],
    font_size: int = 50,
    color: str = 'white',
    duration: Optional[float] = None
) -> str
```
Adds text overlay to video.

```python
async def apply_filter(
    video_path: str,
    filter_type: str,
    output_name: Optional[str] = None
) -> str
```
Applies visual filters: grayscale, sepia, blur, vignette.

**Supported Transitions**:
- Fade in/out
- Crossfade
- Zoom effects

**Output Formats**: MP4, MOV, AVI, WEBM

---

### 2. Image Module (`src/modules/image_module.py`)

#### ImageGenerator Class

**Purpose**: AI image generation and manipulation

**Key Methods**:

```python
async def generate_ai_image(
    prompt: str,
    size: str = "1024x1024",
    quality: str = "hd",
    api_client = None
) -> str
```
Generates image using AI (DALL-E).

```python
async def apply_filter(
    image_path: str,
    filter_type: str,
    **kwargs
) -> str
```
Applies image filters.

**Available Filters**:
- blur, sharpen, edge_enhance, emboss
- grayscale, sepia, vignette
- brightness, contrast, saturation

```python
async def optimize_for_platform(
    image_path: str,
    platform: str
) -> str
```
Optimizes image for social media platforms.

**Platform Specs**:
- Instagram Post: 1080x1080
- Instagram Story: 1080x1920
- TikTok: 1080x1920
- YouTube Thumbnail: 1280x720
- Twitter: 1200x675

---

### 3. Script Module (`src/modules/script_module.py`)

#### ScriptGenerator Class

**Purpose**: AI-powered content writing and optimization

**Key Methods**:

```python
async def generate_video_script(
    topic: str,
    duration: int = 60,
    style: str = "engaging",
    target_audience: str = "general"
) -> Dict[str, Any]
```
Generates structured video script with hooks, content, CTA.

```python
async def generate_social_post(
    topic: str,
    platform: str = "instagram",
    tone: str = "casual"
) -> Dict[str, Any]
```
Creates platform-optimized social media posts.

```python
async def optimize_for_seo(
    content: str,
    keywords: List[str]
) -> Dict[str, Any]
```
SEO optimization with keyword analysis.

**Features**:
- Sentiment analysis
- Readability scoring
- Headline generation
- Content variations

---

### 4. Audio Module (`src/modules/audio_module.py`)

#### AudioProcessor Class

**Purpose**: Voice synthesis and audio editing

**Key Methods**:

```python
async def text_to_speech(
    text: str,
    voice: str = "default",
    rate: int = 200
) -> str
```
Converts text to speech.

```python
async def merge_audio(
    audio_paths: List[str]
) -> str
```
Merges multiple audio files.

```python
async def add_background_music(
    voice_path: str,
    music_path: str,
    music_volume_reduction_db: float = 20
) -> str
```
Adds background music to voice track.

**Audio Effects**:
- Trim, merge, volume adjustment
- Fade in/out
- Speed control
- Normalization
- Format conversion

---

### 5. Social Media Module (`src/modules/social_media_module.py`)

#### SocialMediaScheduler Class

**Purpose**: Multi-platform content scheduling

**Key Methods**:

```python
async def schedule_post(
    platform: str,
    content: str,
    media_paths: List[str],
    scheduled_time: datetime
) -> Dict[str, Any]
```
Schedules post with validation.

```python
async def suggest_best_time(
    platform: str,
    target_audience: str = "general"
) -> List[datetime]
```
AI-powered posting time suggestions.

**Platform Support**:
- TikTok
- Instagram (Feed, Stories, Reels)
- YouTube (Videos, Shorts)
- Twitter
- Facebook

---

### 6. Analytics Module (`src/modules/analytics_module.py`)

#### AnalyticsEngine Class

**Purpose**: Performance tracking and insights

**Key Methods**:

```python
async def get_performance_overview() -> Dict[str, Any]
```
Comprehensive performance metrics.

```python
async def predict_performance(
    content_description: str,
    platform: str,
    planned_post_time: datetime
) -> Dict[str, Any]
```
AI-powered performance prediction.

```python
async def analyze_audience() -> Dict[str, Any]
```
Detailed audience demographics and behavior.

**Metrics Tracked**:
- Views, likes, comments, shares
- Engagement rate
- Follower growth
- ROI calculations

---

### 7. Trends Module (`src/modules/trends_module.py`)

#### TrendAnalyzer Class

**Purpose**: Real-time trend detection and analysis

**Key Methods**:

```python
async def get_trending_topics(
    platform: str = "all",
    limit: int = 20
) -> List[Dict[str, Any]]
```
Fetches current trending topics.

```python
async def predict_trend(
    keyword: str,
    time_horizon: int = 7
) -> Dict[str, Any]
```
Predicts trend trajectory.

```python
async def get_content_ideas_from_trends(
    category: str,
    count: int = 10
) -> List[Dict[str, Any]]
```
Generates content ideas from trends.

---

### 8. Project Module (`src/modules/project_module.py`)

#### ProjectManager Class

**Purpose**: Content project organization

**Key Methods**:

```python
async def create_project(
    name: str,
    description: str,
    project_type: str = "video"
) -> Dict[str, Any]
```
Creates new project with directory structure.

```python
async def export_project(
    project_name: str,
    export_format: str = "zip"
) -> str
```
Exports project as archive.

**Project Structure**:
```
project_name/
├── project.json
├── videos/
├── images/
├── audio/
└── scripts/
```

---

## API Reference

### AI Client (`src/api/ai_client.py`)

#### AIClient Class

```python
class AIClient:
    def __init__(self, provider: str = "openai", api_key: Optional[str] = None)

    async def generate_text(
        self,
        prompt: str,
        model: Optional[str] = None,
        temperature: float = 0.7,
        max_tokens: int = 2000,
        system_prompt: Optional[str] = None
    ) -> AIResponse

    async def generate_image_prompt(
        self,
        description: str,
        size: str = "1024x1024"
    ) -> str
```

**Supported Providers**:
- OpenAI (GPT-4, DALL-E)
- Anthropic (Claude)

---

## Database Schema

### Tables

#### Projects
```sql
CREATE TABLE projects (
    id INTEGER PRIMARY KEY,
    name VARCHAR(255) NOT NULL,
    description TEXT,
    type VARCHAR(50),
    status VARCHAR(50),
    created_at DATETIME,
    updated_at DATETIME,
    metadata JSON
);
```

#### Videos
```sql
CREATE TABLE videos (
    id INTEGER PRIMARY KEY,
    project_id INTEGER REFERENCES projects(id),
    name VARCHAR(255) NOT NULL,
    file_path VARCHAR(500),
    duration FLOAT,
    resolution VARCHAR(20),
    fps INTEGER,
    ai_generated BOOLEAN,
    created_at DATETIME
);
```

#### Analytics
```sql
CREATE TABLE analytics (
    id INTEGER PRIMARY KEY,
    platform VARCHAR(50),
    post_id VARCHAR(255),
    metric_type VARCHAR(50),
    value FLOAT,
    recorded_at DATETIME
);
```

**Full Schema**: See `src/database/models.py`

---

## Configuration

### Configuration File Structure

```json
{
  "app": {
    "name": "CreatorStudio AI",
    "version": "1.0.0",
    "theme": "dark",
    "auto_save": true
  },
  "ai": {
    "provider": "openai",
    "model": "gpt-4-turbo-preview",
    "temperature": 0.7,
    "max_tokens": 4000
  },
  "video": {
    "default_resolution": "1920x1080",
    "default_fps": 30,
    "hardware_acceleration": true
  }
}
```

### Environment Variables

```bash
# Optional: Set API keys via environment
OPENAI_API_KEY=your_key_here
ANTHROPIC_API_KEY=your_key_here
```

---

## Development Guide

### Setting Up Development Environment

```bash
# Clone repository
git clone <repo-url>
cd tiktok.viral

# Create virtual environment
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Install dev dependencies
pip install black pytest mypy

# Run application
python main.py
```

### Code Style

- **Formatter**: Black (line length: 100)
- **Type Hints**: Required for all functions
- **Docstrings**: Google style
- **Imports**: Organized (stdlib, third-party, local)

### Testing

```bash
# Run tests
pytest tests/

# Run with coverage
pytest --cov=src tests/

# Type checking
mypy src/
```

### Adding a New Module

1. Create module file in `src/modules/`
2. Define class with async methods
3. Add imports to `__init__.py`
4. Update UI to integrate module
5. Add tests
6. Document in README and this file

### Logging

```python
import logging
logger = logging.getLogger(__name__)

logger.debug("Debug message")
logger.info("Info message")
logger.warning("Warning message")
logger.error("Error message")
logger.critical("Critical message")
```

### Error Handling

```python
try:
    result = await some_async_operation()
except Exception as e:
    logger.error(f"Operation failed: {e}")
    raise  # Re-raise if caller should handle
```

---

## Performance Considerations

### Optimization Tips

1. **Async Operations**: Use `asyncio.to_thread()` for blocking I/O
2. **Caching**: Cache expensive operations (trends, AI responses)
3. **Batch Processing**: Process multiple items together
4. **Resource Management**: Clean up temporary files
5. **Database**: Use indexes, batch inserts

### Resource Limits

- Max video resolution: 4K (3840x2160)
- Max video duration: Limited by memory
- Max image size: 10000x10000 pixels
- Max concurrent operations: 4 (configurable)

---

## Troubleshooting

### Common Issues

**Import Errors**
```bash
# Ensure PYTHONPATH includes src/
export PYTHONPATH="${PYTHONPATH}:./src"
```

**Database Lock**
```python
# Close all sessions before exit
session.close()
```

**Memory Issues**
- Reduce video resolution
- Process in smaller batches
- Clear cache regularly

---

## Future Enhancements

### Planned Features
- Real-time collaboration
- Cloud sync
- Mobile companion app
- Plugin system
- Custom AI model fine-tuning

### API Expansion
- RESTful API for external integrations
- Webhook support
- CLI interface
- Batch processing API

---

**Last Updated**: 2024
**Version**: 1.0.0
