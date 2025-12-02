"""
Database models and setup for DeepCheck MH
"""
from sqlalchemy import create_engine, Column, Integer, String, Text, Float, DateTime, Boolean, JSON
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from datetime import datetime
from src.config import settings

Base = declarative_base()


class Source(Base):
    """Content sources being monitored"""
    __tablename__ = "sources"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(255), unique=True, nullable=False)
    source_type = Column(String(50), nullable=False)  # 'rss', 'news_api', 'reddit', 'twitter'
    url = Column(String(500))
    is_active = Column(Boolean, default=True)
    last_checked = Column(DateTime, default=datetime.utcnow)
    created_at = Column(DateTime, default=datetime.utcnow)


class Claim(Base):
    """Detected claims from content streams"""
    __tablename__ = "claims"
    
    id = Column(Integer, primary_key=True, index=True)
    text = Column(Text, nullable=False)
    source_id = Column(Integer, nullable=True)
    source_url = Column(String(500))
    source_title = Column(String(500))
    
    # Crisis context
    crisis_type = Column(String(100))  # 'pandemic', 'conflict', 'climate', etc.
    urgency_score = Column(Float, default=0.0)  # 0-1 scale
    
    # Entities and topics
    entities = Column(JSON)  # List of named entities
    topics = Column(JSON)  # List of topics/keywords
    
    # Verification status
    verification_status = Column(String(50), default='pending')  # 'pending', 'verified', 'false', 'mixed'
    credibility_score = Column(Float, default=0.0)  # 0-1 scale
    
    # Timestamps
    detected_at = Column(DateTime, default=datetime.utcnow)
    verified_at = Column(DateTime, nullable=True)
    
    # Metadata
    claim_metadata = Column(JSON)  # Additional context


class Verification(Base):
    """Fact-check results for claims"""
    __tablename__ = "verifications"
    
    id = Column(Integer, primary_key=True, index=True)
    claim_id = Column(Integer, nullable=False)
    
    # AI Model used
    model_name = Column(String(100))  # 'gemini', 'openai', 'consensus'
    
    # Verification result
    verdict = Column(String(50))  # 'true', 'false', 'mixed', 'unverifiable'
    confidence = Column(Float)  # 0-1 scale
    
    # Evidence
    supporting_sources = Column(JSON)  # List of supporting sources
    contradicting_sources = Column(JSON)  # List of contradicting sources
    
    # Analysis
    reasoning = Column(Text)  # Detailed reasoning
    
    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow)


class Explanation(Base):
    """Generated explanations for claims"""
    __tablename__ = "explanations"
    
    id = Column(Integer, primary_key=True, index=True)
    claim_id = Column(Integer, nullable=False)
    verification_id = Column(Integer, nullable=True)
    
    # Audience targeting
    audience_level = Column(String(50), default='general')  # 'simple', 'general', 'expert'
    
    # Content
    title = Column(String(500))
    summary = Column(Text)  # Brief summary
    detailed_explanation = Column(Text)  # Full explanation
    
    # Evidence citations
    citations = Column(JSON)  # List of source citations
    
    # Actionable guidance
    what_to_do = Column(Text, nullable=True)
    what_to_avoid = Column(Text, nullable=True)
    
    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow)


class Media(Base):
    """Uploaded media files for deepfake detection"""
    __tablename__ = "media"
    
    id = Column(Integer, primary_key=True, index=True)
    filename = Column(String(500), nullable=False)
    file_path = Column(String(1000), nullable=False)
    file_type = Column(String(50), nullable=False)  # 'image', 'video', 'audio'
    file_size = Column(Integer)  # bytes
    
    # Deepfake analysis
    is_deepfake = Column(Boolean, default=None)  # None = pending, True/False = analyzed
    deepfake_confidence = Column(Float, default=0.0)  # 0-1 scale
    analysis_status = Column(String(50), default='pending')  # 'pending', 'analyzing', 'completed', 'failed'
    
    # Analysis results
    artifacts_detected = Column(JSON)  # List of detected artifacts
    metadata_analysis = Column(JSON)  # EXIF and metadata findings
    frame_analysis = Column(JSON)  # For videos: per-frame analysis
    
    # AI model results
    gemini_verdict = Column(String(50))  # 'real', 'fake', 'uncertain'
    gemini_confidence = Column(Float)
    openai_verdict = Column(String(50))
    openai_confidence = Column(Float)
    consensus_verdict = Column(String(50))
    
    # Detailed report
    analysis_report = Column(Text)  # Human-readable explanation
    technical_details = Column(JSON)  # Technical analysis data
    
    # Timestamps
    uploaded_at = Column(DateTime, default=datetime.utcnow)
    analyzed_at = Column(DateTime, nullable=True)
    
    # User context
    user_description = Column(Text, nullable=True)  # User's description of the media


class Feedback(Base):
    """User feedback for active learning"""
    __tablename__ = "feedback"
    
    id = Column(Integer, primary_key=True, index=True)
    
    # Link to verification or deepfake analysis
    claim_id = Column(Integer, nullable=True)
    media_id = Column(Integer, nullable=True)
    
    # Feedback content
    is_correct = Column(Boolean, nullable=False)  # True = Model was right, False = Model was wrong
    correction_text = Column(Text, nullable=True)  # User's correction/explanation
    
    # Metadata
    created_at = Column(DateTime, default=datetime.utcnow)


# Database setup
engine = create_engine(
    settings.database_url,
    connect_args={"check_same_thread": False} if "sqlite" in settings.database_url else {}
)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


def init_db():
    """Initialize database tables"""
    Base.metadata.create_all(bind=engine)


def get_db():
    """Get database session"""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
