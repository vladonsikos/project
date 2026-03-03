from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.database import get_db
from app.models import Generation, Trend, Account
from app.schemas import GenerationCreate, GenerationResponse
from typing import Optional
from celery_worker import run_generation

router = APIRouter(prefix="/api/generations", tags=["generations"])


@router.post("", response_model=dict)
async def create_generation(
    gen_data: GenerationCreate,
    db: AsyncSession = Depends(get_db),
):
    """Start a generation task"""
    from sqlalchemy import update
    
    # Get trend
    result = await db.execute(select(Trend).where(Trend.id == gen_data.trend_id))
    trend = result.scalar_one_or_none()
    
    if not trend:
        raise HTTPException(status_code=404, detail="Trend not found")
    
    # Get account balance with row lock to prevent race condition
    result = await db.execute(
        select(Account).where(Account.id == 1).with_for_update()
    )
    account = result.scalar_one_or_none()
    
    if not account:
        raise HTTPException(status_code=500, detail="Account not found")
    
    # Check balance
    if account.balance < trend.price_tokens:
        raise HTTPException(
            status_code=400,
            detail=f"Insufficient balance. Required: {trend.price_tokens}, Available: {account.balance}",
        )
    
    # Atomically deduct tokens
    account.balance -= trend.price_tokens
    
    # Create generation record
    generation = Generation(
        trend_id=gen_data.trend_id,
        prompt=gen_data.prompt,
        materials=gen_data.materials,
        asset_ids=gen_data.asset_ids,
        status="pending",
        price_spent=trend.price_tokens,
    )
    
    db.add(generation)
    await db.commit()
    await db.refresh(generation)
    
    # Send to Celery
    run_generation.delay(generation.id)
    
    return {
        "id": generation.id,
        "status": generation.status,
        "message": "Generation started",
    }


@router.get("/{generation_id}", response_model=GenerationResponse)
async def get_generation(
    generation_id: int,
    db: AsyncSession = Depends(get_db),
):
    """Get generation status and result"""
    result = await db.execute(
        select(Generation).where(Generation.id == generation_id)
    )
    generation = result.scalar_one_or_none()
    
    if not generation:
        raise HTTPException(status_code=404, detail="Generation not found")
    
    return generation
