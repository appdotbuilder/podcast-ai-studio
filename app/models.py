from sqlmodel import SQLModel, Field, Relationship, JSON, Column
from datetime import datetime
from typing import Optional, List, Dict, Any
from decimal import Decimal
from enum import Enum


class UserTier(str, Enum):
    FREE = "free"
    PREMIUM = "premium"
    PROFESSIONAL = "professional"


class ProjectStatus(str, Enum):
    DRAFT = "draft"
    SCRIPT_READY = "script_ready"
    AUDIO_GENERATED = "audio_generated"
    ENHANCED = "enhanced"
    PUBLISHED = "published"


class ScriptStatus(str, Enum):
    DRAFT = "draft"
    AI_GENERATED = "ai_generated"
    USER_EDITED = "user_edited"
    FINAL = "final"


class AudioStatus(str, Enum):
    PENDING = "pending"
    PROCESSING = "processing"
    COMPLETED = "completed"
    FAILED = "failed"


class VoiceType(str, Enum):
    MALE_PROFESSIONAL = "male_professional"
    FEMALE_PROFESSIONAL = "female_professional"
    MALE_CASUAL = "male_casual"
    FEMALE_CASUAL = "female_casual"
    NARRATOR = "narrator"
    CUSTOM = "custom"


# Persistent models (stored in database)
class User(SQLModel, table=True):
    __tablename__ = "users"  # type: ignore[assignment]

    id: Optional[int] = Field(default=None, primary_key=True)
    email: str = Field(unique=True, max_length=255, regex=r"^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$")
    username: str = Field(unique=True, max_length=50)
    full_name: str = Field(max_length=100)
    password_hash: str = Field(max_length=255)
    tier: UserTier = Field(default=UserTier.FREE)
    is_active: bool = Field(default=True)
    created_at: datetime = Field(default_factory=datetime.utcnow)
    last_login: Optional[datetime] = Field(default=None)

    # Usage tracking for free tier limits
    monthly_projects_created: int = Field(default=0)
    monthly_audio_minutes: Decimal = Field(default=Decimal("0"))
    monthly_reset_date: datetime = Field(default_factory=datetime.utcnow)

    # Preferences
    default_voice_type: VoiceType = Field(default=VoiceType.MALE_PROFESSIONAL)
    preferences: Dict[str, Any] = Field(default={}, sa_column=Column(JSON))

    # Relationships
    projects: List["Project"] = Relationship(back_populates="user")
    subscriptions: List["Subscription"] = Relationship(back_populates="user")


class TopicSuggestion(SQLModel, table=True):
    __tablename__ = "topic_suggestions"  # type: ignore[assignment]

    id: Optional[int] = Field(default=None, primary_key=True)
    title: str = Field(max_length=200)
    description: str = Field(max_length=1000)
    category: str = Field(max_length=100)
    tags: List[str] = Field(default=[], sa_column=Column(JSON))
    popularity_score: Decimal = Field(default=Decimal("0"))
    ai_generated: bool = Field(default=True)
    created_at: datetime = Field(default_factory=datetime.utcnow)

    # Relationships
    projects: List["Project"] = Relationship(back_populates="topic_suggestion")


class Project(SQLModel, table=True):
    __tablename__ = "projects"  # type: ignore[assignment]

    id: Optional[int] = Field(default=None, primary_key=True)
    title: str = Field(max_length=200)
    description: str = Field(default="", max_length=2000)
    status: ProjectStatus = Field(default=ProjectStatus.DRAFT)
    category: str = Field(max_length=100)
    tags: List[str] = Field(default=[], sa_column=Column(JSON))

    # Foreign keys
    user_id: int = Field(foreign_key="users.id")
    topic_suggestion_id: Optional[int] = Field(foreign_key="topic_suggestions.id", default=None)

    # Metadata
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
    published_at: Optional[datetime] = Field(default=None)

    # Project settings
    target_duration_minutes: Optional[int] = Field(default=None)
    voice_type: VoiceType = Field(default=VoiceType.MALE_PROFESSIONAL)
    custom_voice_settings: Dict[str, Any] = Field(default={}, sa_column=Column(JSON))

    # Relationships
    user: User = Relationship(back_populates="projects")
    topic_suggestion: Optional[TopicSuggestion] = Relationship(back_populates="projects")
    scripts: List["Script"] = Relationship(back_populates="project")
    audio_files: List["AudioFile"] = Relationship(back_populates="project")


class Script(SQLModel, table=True):
    __tablename__ = "scripts"  # type: ignore[assignment]

    id: Optional[int] = Field(default=None, primary_key=True)
    title: str = Field(max_length=200)
    content: str = Field(max_length=50000)  # Large text field for script content
    status: ScriptStatus = Field(default=ScriptStatus.DRAFT)
    version: int = Field(default=1)
    is_current: bool = Field(default=True)

    # AI generation metadata
    ai_generated: bool = Field(default=False)
    ai_prompt: Optional[str] = Field(default=None, max_length=2000)
    ai_model_used: Optional[str] = Field(default=None, max_length=100)

    # Script structure
    estimated_duration_minutes: Optional[Decimal] = Field(default=None)
    word_count: int = Field(default=0)
    sections: List[Dict[str, Any]] = Field(default=[], sa_column=Column(JSON))  # For script structure

    # Foreign keys
    project_id: int = Field(foreign_key="projects.id")

    # Metadata
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)

    # Relationships
    project: Project = Relationship(back_populates="scripts")
    audio_files: List["AudioFile"] = Relationship(back_populates="script")


class AudioFile(SQLModel, table=True):
    __tablename__ = "audio_files"  # type: ignore[assignment]

    id: Optional[int] = Field(default=None, primary_key=True)
    filename: str = Field(max_length=255)
    file_path: str = Field(max_length=500)
    file_size_bytes: int = Field(default=0)
    duration_seconds: Optional[Decimal] = Field(default=None)
    status: AudioStatus = Field(default=AudioStatus.PENDING)

    # Audio specifications
    format: str = Field(max_length=10, default="mp3")  # mp3, wav, m4a, etc.
    bitrate: Optional[int] = Field(default=None)
    sample_rate: Optional[int] = Field(default=None)
    channels: int = Field(default=1)  # mono by default

    # Voice synthesis settings
    voice_type: VoiceType = Field(default=VoiceType.MALE_PROFESSIONAL)
    voice_speed: Decimal = Field(default=Decimal("1.0"))
    voice_pitch: Decimal = Field(default=Decimal("1.0"))
    voice_settings: Dict[str, Any] = Field(default={}, sa_column=Column(JSON))

    # Enhancement settings
    is_enhanced: bool = Field(default=False)
    enhancement_settings: Dict[str, Any] = Field(default={}, sa_column=Column(JSON))
    original_file_id: Optional[int] = Field(foreign_key="audio_files.id", default=None)

    # Processing metadata
    processing_started_at: Optional[datetime] = Field(default=None)
    processing_completed_at: Optional[datetime] = Field(default=None)
    error_message: Optional[str] = Field(default=None, max_length=1000)

    # Foreign keys
    project_id: int = Field(foreign_key="projects.id")
    script_id: Optional[int] = Field(foreign_key="scripts.id", default=None)

    # Metadata
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)

    # Relationships
    project: Project = Relationship(back_populates="audio_files")
    script: Optional[Script] = Relationship(back_populates="audio_files")
    original_file: Optional["AudioFile"] = Relationship(
        back_populates="enhanced_versions", sa_relationship_kwargs={"remote_side": "AudioFile.id"}
    )
    enhanced_versions: List["AudioFile"] = Relationship(back_populates="original_file")


class Subscription(SQLModel, table=True):
    __tablename__ = "subscriptions"  # type: ignore[assignment]

    id: Optional[int] = Field(default=None, primary_key=True)
    tier: UserTier = Field(default=UserTier.FREE)
    is_active: bool = Field(default=True)

    # Billing
    price_monthly: Decimal = Field(default=Decimal("0"))
    currency: str = Field(default="USD", max_length=3)
    payment_provider: Optional[str] = Field(default=None, max_length=50)
    payment_provider_subscription_id: Optional[str] = Field(default=None, max_length=255)

    # Subscription period
    started_at: datetime = Field(default_factory=datetime.utcnow)
    expires_at: Optional[datetime] = Field(default=None)
    cancelled_at: Optional[datetime] = Field(default=None)

    # Usage limits
    monthly_project_limit: int = Field(default=5)  # Free tier default
    monthly_audio_minutes_limit: Decimal = Field(default=Decimal("60"))  # Free tier default

    # Foreign keys
    user_id: int = Field(foreign_key="users.id")

    # Metadata
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)

    # Relationships
    user: User = Relationship(back_populates="subscriptions")


class UsageLog(SQLModel, table=True):
    __tablename__ = "usage_logs"  # type: ignore[assignment]

    id: Optional[int] = Field(default=None, primary_key=True)
    user_id: int = Field(foreign_key="users.id")
    action: str = Field(max_length=100)  # e.g., "project_created", "audio_generated", "audio_enhanced"
    resource_type: str = Field(max_length=50)  # e.g., "project", "audio_file"
    resource_id: Optional[int] = Field(default=None)

    # Usage metrics
    audio_minutes_used: Optional[Decimal] = Field(default=None)
    credits_used: Optional[int] = Field(default=None)

    # Metadata
    log_metadata: Dict[str, Any] = Field(default={}, sa_column=Column(JSON))
    created_at: datetime = Field(default_factory=datetime.utcnow)


# Non-persistent schemas (for validation, forms, API requests/responses)
class UserCreate(SQLModel, table=False):
    email: str = Field(max_length=255, regex=r"^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$")
    username: str = Field(max_length=50)
    full_name: str = Field(max_length=100)
    password: str = Field(min_length=8, max_length=100)


class UserUpdate(SQLModel, table=False):
    full_name: Optional[str] = Field(default=None, max_length=100)
    default_voice_type: Optional[VoiceType] = Field(default=None)
    preferences: Optional[Dict[str, Any]] = Field(default=None)


class ProjectCreate(SQLModel, table=False):
    title: str = Field(max_length=200)
    description: str = Field(default="", max_length=2000)
    category: str = Field(max_length=100)
    tags: List[str] = Field(default=[])
    topic_suggestion_id: Optional[int] = Field(default=None)
    target_duration_minutes: Optional[int] = Field(default=None)
    voice_type: VoiceType = Field(default=VoiceType.MALE_PROFESSIONAL)


class ProjectUpdate(SQLModel, table=False):
    title: Optional[str] = Field(default=None, max_length=200)
    description: Optional[str] = Field(default=None, max_length=2000)
    status: Optional[ProjectStatus] = Field(default=None)
    category: Optional[str] = Field(default=None, max_length=100)
    tags: Optional[List[str]] = Field(default=None)
    target_duration_minutes: Optional[int] = Field(default=None)
    voice_type: Optional[VoiceType] = Field(default=None)


class ScriptCreate(SQLModel, table=False):
    title: str = Field(max_length=200)
    content: str = Field(max_length=50000)
    project_id: int
    ai_prompt: Optional[str] = Field(default=None, max_length=2000)


class ScriptUpdate(SQLModel, table=False):
    title: Optional[str] = Field(default=None, max_length=200)
    content: Optional[str] = Field(default=None, max_length=50000)
    status: Optional[ScriptStatus] = Field(default=None)


class AudioFileCreate(SQLModel, table=False):
    filename: str = Field(max_length=255)
    project_id: int
    script_id: Optional[int] = Field(default=None)
    voice_type: VoiceType = Field(default=VoiceType.MALE_PROFESSIONAL)
    voice_speed: Decimal = Field(default=Decimal("1.0"))
    voice_pitch: Decimal = Field(default=Decimal("1.0"))


class AudioFileUpdate(SQLModel, table=False):
    status: Optional[AudioStatus] = Field(default=None)
    duration_seconds: Optional[Decimal] = Field(default=None)
    file_size_bytes: Optional[int] = Field(default=None)
    is_enhanced: Optional[bool] = Field(default=None)
    error_message: Optional[str] = Field(default=None, max_length=1000)


class TopicSuggestionCreate(SQLModel, table=False):
    title: str = Field(max_length=200)
    description: str = Field(max_length=1000)
    category: str = Field(max_length=100)
    tags: List[str] = Field(default=[])
    ai_generated: bool = Field(default=True)


class SubscriptionCreate(SQLModel, table=False):
    user_id: int
    tier: UserTier
    price_monthly: Decimal
    monthly_project_limit: int
    monthly_audio_minutes_limit: Decimal
    expires_at: Optional[datetime] = Field(default=None)
