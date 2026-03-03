from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, and_
from app.database import get_db
from app.models import Trend
from app.schemas import TrendCreate, TrendUpdate, TrendResponse
from app.auth import verify_admin
from typing import List, Optional

router = APIRouter(prefix="/api/trends", tags=["trends"])


@router.get("", response_model=List[TrendResponse])
async def list_trends(
    active: Optional[bool] = None,
    type: Optional[str] = None,
    db: AsyncSession = Depends(get_db),
):
    """Get list of trends with optional filters"""
    query = select(Trend)
    
    conditions = []
    if active is not None:
        conditions.append(Trend.is_active == active)
    if type:
        conditions.append(Trend.type == type)
    
    if conditions:
        query = query.where(and_(*conditions))
    
    result = await db.execute(query)
    trends = result.scalars().all()
    return trends


@router.get("/{trend_id}", response_model=TrendResponse)
async def get_trend(
    trend_id: int,
    db: AsyncSession = Depends(get_db),
):
    """Get trend details"""
    result = await db.execute(select(Trend).where(Trend.id == trend_id))
    trend = result.scalar_one_or_none()
    
    if not trend:
        raise HTTPException(status_code=404, detail="Trend not found")
    
    return trend


@router.post("", response_model=TrendResponse)
async def create_trend(
    trend_data: TrendCreate,
    db: AsyncSession = Depends(get_db),
    admin: str = Depends(verify_admin),
):
    """Create a new trend (admin only)"""
    trend = Trend(
        title=trend_data.title,
        type=trend_data.type,
        preview_url=trend_data.preview_url,
        tags=trend_data.tags,
        is_popular=trend_data.is_popular,
        is_active=trend_data.is_active,
        price_tokens=trend_data.price_tokens,
    )
    
    db.add(trend)
    await db.commit()
    await db.refresh(trend)
    
    return trend


@router.patch("/{trend_id}", response_model=TrendResponse)
async def update_trend(
    trend_id: int,
    trend_data: TrendUpdate,
    db: AsyncSession = Depends(get_db),
    admin: str = Depends(verify_admin),
):
    """Update trend (admin only)"""
    result = await db.execute(select(Trend).where(Trend.id == trend_id))
    trend = result.scalar_one_or_none()
    
    if not trend:
        raise HTTPException(status_code=404, detail="Trend not found")
    
    # Update only provided fields
    update_data = trend_data.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(trend, field, value)
    
    await db.commit()
    await db.refresh(trend)
    
    return trend


@router.delete("/{trend_id}")
async def delete_trend(
    trend_id: int,
    db: AsyncSession = Depends(get_db),
    admin: str = Depends(verify_admin),
):
    """Delete trend (admin only)"""
    result = await db.execute(select(Trend).where(Trend.id == trend_id))
    trend = result.scalar_one_or_none()
    
    if not trend:
        raise HTTPException(status_code=404, detail="Trend not found")
    
    await db.delete(trend)
    await db.commit()
    
    return {"message": "Trend deleted successfully"}
