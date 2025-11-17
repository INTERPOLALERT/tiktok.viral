"""
Database Models
SQLAlchemy models for data persistence
"""

from datetime import datetime
from pathlib import Path
from sqlalchemy import create_engine, Column, Integer, String, Text, DateTime, Float, Boolean, JSON, ForeignKey
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, relationship
import logging

logger = logging.getLogger(__name__)

Base = declarative_base()


class Project(Base):
    """Content creation project"""
    __tablename__ = 'projects'

    id = Column(Integer, primary_key=True)
    name = Column(String(255), nullable=False)
    description = Column(Text)
    type = Column(String(50))  # video, image, audio, script
    status = Column(String(50), default='active')  # active, archived, completed
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    meta_data = Column(JSON)

    # Relationships
    videos = relationship("Video", back_populates="project", cascade="all, delete-orphan")
    images = relationship("Image", back_populates="project", cascade="all, delete-orphan")
    scripts = relationship("Script", back_populates="project", cascade="all, delete-orphan")
    audio_files = relationship("AudioFile", back_populates="project", cascade="all, delete-orphan")


class Video(Base):
    """Video content"""
    __tablename__ = 'videos'

    id = Column(Integer, primary_key=True)
    project_id = Column(Integer, ForeignKey('projects.id'))
    name = Column(String(255), nullable=False)
    file_path = Column(String(500))
    duration = Column(Float)
    resolution = Column(String(20))
    fps = Column(Integer)
    format = Column(String(10))
    size_bytes = Column(Integer)
    thumbnail_path = Column(String(500))
    ai_generated = Column(Boolean, default=False)
    ai_prompt = Column(Text)
    created_at = Column(DateTime, default=datetime.utcnow)
    meta_data = Column(JSON)

    project = relationship("Project", back_populates="videos")


class Image(Base):
    """Image content"""
    __tablename__ = 'images'

    id = Column(Integer, primary_key=True)
    project_id = Column(Integer, ForeignKey('projects.id'))
    name = Column(String(255), nullable=False)
    file_path = Column(String(500))
    width = Column(Integer)
    height = Column(Integer)
    format = Column(String(10))
    size_bytes = Column(Integer)
    ai_generated = Column(Boolean, default=False)
    ai_prompt = Column(Text)
    created_at = Column(DateTime, default=datetime.utcnow)
    meta_data = Column(JSON)

    project = relationship("Project", back_populates="images")


class Script(Base):
    """Script/Content text"""
    __tablename__ = 'scripts'

    id = Column(Integer, primary_key=True)
    project_id = Column(Integer, ForeignKey('projects.id'))
    name = Column(String(255), nullable=False)
    content = Column(Text)
    type = Column(String(50))  # video_script, social_post, article, etc.
    word_count = Column(Integer)
    ai_generated = Column(Boolean, default=False)
    ai_prompt = Column(Text)
    seo_score = Column(Float)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    meta_data = Column(JSON)

    project = relationship("Project", back_populates="scripts")


class AudioFile(Base):
    """Audio content"""
    __tablename__ = 'audio_files'

    id = Column(Integer, primary_key=True)
    project_id = Column(Integer, ForeignKey('projects.id'))
    name = Column(String(255), nullable=False)
    file_path = Column(String(500))
    duration = Column(Float)
    format = Column(String(10))
    bitrate = Column(Integer)
    sample_rate = Column(Integer)
    size_bytes = Column(Integer)
    ai_generated = Column(Boolean, default=False)
    voice_model = Column(String(100))
    created_at = Column(DateTime, default=datetime.utcnow)
    meta_data = Column(JSON)

    project = relationship("Project", back_populates="audio_files")


class SocialMediaPost(Base):
    """Social media post scheduling and tracking"""
    __tablename__ = 'social_media_posts'

    id = Column(Integer, primary_key=True)
    platform = Column(String(50), nullable=False)  # tiktok, instagram, youtube, etc.
    content = Column(Text)
    media_paths = Column(JSON)  # List of media file paths
    status = Column(String(50))  # draft, scheduled, posted, failed
    scheduled_time = Column(DateTime)
    posted_time = Column(DateTime)
    post_id = Column(String(255))  # Platform-specific post ID
    engagement = Column(JSON)  # likes, comments, shares, views
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    meta_data = Column(JSON)


class Analytics(Base):
    """Analytics and performance tracking"""
    __tablename__ = 'analytics'

    id = Column(Integer, primary_key=True)
    platform = Column(String(50))
    post_id = Column(String(255))
    metric_type = Column(String(50))  # views, likes, shares, comments, etc.
    value = Column(Float)
    recorded_at = Column(DateTime, default=datetime.utcnow)
    meta_data = Column(JSON)


class Trend(Base):
    """Trending topics and hashtags"""
    __tablename__ = 'trends'

    id = Column(Integer, primary_key=True)
    platform = Column(String(50))
    keyword = Column(String(255))
    hashtag = Column(String(255))
    score = Column(Float)
    category = Column(String(100))
    detected_at = Column(DateTime, default=datetime.utcnow)
    meta_data = Column(JSON)


class Template(Base):
    """Reusable templates"""
    __tablename__ = 'templates'

    id = Column(Integer, primary_key=True)
    name = Column(String(255), nullable=False)
    type = Column(String(50))  # video, image, script
    content = Column(JSON)
    thumbnail_path = Column(String(500))
    usage_count = Column(Integer, default=0)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    meta_data = Column(JSON)


class APIKey(Base):
    """API keys for external services"""
    __tablename__ = 'api_keys'

    id = Column(Integer, primary_key=True)
    service = Column(String(100), nullable=False)  # openai, anthropic, etc.
    key_encrypted = Column(Text)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    last_used = Column(DateTime)
    usage_count = Column(Integer, default=0)


class DatabaseManager:
    """Manages database connections and operations"""

    def __init__(self, db_path: str = None):
        if db_path is None:
            base_dir = Path(__file__).parent.parent.parent
            data_dir = base_dir / "data"
            data_dir.mkdir(exist_ok=True)
            db_path = str(data_dir / "creatorstudio.db")

        self.engine = create_engine(f'sqlite:///{db_path}', echo=False)
        Base.metadata.create_all(self.engine)

        self.Session = sessionmaker(bind=self.engine)
        logger.info(f"Database initialized at: {db_path}")

    def get_session(self):
        """Get a new database session"""
        return self.Session()

    def create_all_tables(self):
        """Create all database tables"""
        Base.metadata.create_all(self.engine)
        logger.info("All database tables created")

    def drop_all_tables(self):
        """Drop all database tables (use with caution!)"""
        Base.metadata.drop_all(self.engine)
        logger.warning("All database tables dropped")


# Global database instance
db_manager = None


def get_db_manager() -> DatabaseManager:
    """Get the global database manager instance"""
    global db_manager
    if db_manager is None:
        db_manager = DatabaseManager()
    return db_manager
