from datetime import datetime
from typing import List, Optional
from pydantic import BaseModel, Field


# Trend Schemas
class TrendBase(BaseModel):
    title: str
    type: str  # "photo" or "video"
    preview_url: Optional[str] = None
    tags: List[str] = Field(default_factory=list)
    is_popular: bool = False
    is_active: bool = True
    price_tokens: int = 10


class TrendCreate(TrendBase):
    pass


class TrendUpdate(BaseModel):
    title: Optional[str] = None
    type: Optional[str] = None
    preview_url: Optional[str] = None
    tags: Optional[List[str]] = None
    is_popular: Optional[bool] = None
    is_active: Optional[bool] = None
    price_tokens: Optional[int] = None


class TrendResponse(TrendBase):
    id: int
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


# Asset Schemas
class AssetResponse(BaseModel):
    id: int
    filename: str
    path: str
    content_type: str
    size: int
    uploaded_at: datetime

    class Config:
        from_attributes = True


# Generation Schemas
class GenerationCreate(BaseModel):
    trend_id: int
    prompt: str
    materials: Optional[str] = None
    asset_ids: List[int] = Field(default_factory=list)


class GenerationUpdate(BaseModel):
    status: Optional[str] = None
    result_text: Optional[str] = None
    result_assets: Optional[List[int]] = None
    price_spent: Optional[int] = None


class GenerationResponse(BaseModel):
    id: int
    trend_id: int
    prompt: str
    materials: Optional[str]
    asset_ids: List[int]
    status: str
    result_text: Optional[str]
    result_assets: List[int]
    price_spent: int
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


# Account Schemas
class AccountResponse(BaseModel):
    id: int
    balance: int

    class Config:
        from_attributes = True
