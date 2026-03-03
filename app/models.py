from datetime import datetime
from sqlalchemy import Column, Integer, String, Boolean, DateTime, Text, ForeignKey, JSON
from sqlalchemy.orm import relationship
from app.database import Base


class Trend(Base):
    __tablename__ = "trends"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String(255), nullable=False, index=True)
    type = Column(String(50), nullable=False)  # "photo" or "video"
    preview_url = Column(String(500), nullable=True)
    tags = Column(JSON, default=list, nullable=False)
    is_popular = Column(Boolean, default=False, nullable=False)
    is_active = Column(Boolean, default=True, nullable=False)
    price_tokens = Column(Integer, default=10, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)

    generations = relationship("Generation", back_populates="trend", cascade="all, delete-orphan")


class Asset(Base):
    __tablename__ = "assets"

    id = Column(Integer, primary_key=True, index=True)
    filename = Column(String(255), nullable=False)
    path = Column(String(500), nullable=False)
    content_type = Column(String(100), nullable=False)
    size = Column(Integer, nullable=False)
    uploaded_at = Column(DateTime, default=datetime.utcnow, nullable=False)


class Generation(Base):
    __tablename__ = "generations"

    id = Column(Integer, primary_key=True, index=True)
    trend_id = Column(Integer, ForeignKey("trends.id"), nullable=False)
    prompt = Column(Text, nullable=False)
    materials = Column(Text, nullable=True)
    asset_ids = Column(JSON, default=list, nullable=False)
    status = Column(String(50), default="pending", nullable=False)  # pending, processing, completed, failed
    result_text = Column(Text, nullable=True)
    result_assets = Column(JSON, default=list, nullable=False)
    price_spent = Column(Integer, default=0, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)

    trend = relationship("Trend", back_populates="generations")


class Account(Base):
    __tablename__ = "accounts"

    id = Column(Integer, primary_key=True, index=True)
    balance = Column(Integer, default=1000, nullable=False)
