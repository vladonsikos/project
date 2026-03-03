import logging
from fastapi import FastAPI, Depends, HTTPException, Request
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
import os

from app.config import settings
from app.database import get_db, init_db, async_session_maker
from app.models import Trend, Generation, Account
from app.api import trends, generations, assets
from app.schemas import GenerationCreate
from app.auth import verify_admin

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Create FastAPI app
app = FastAPI(title="Trendsee", version="1.0.0")

# Setup templates
templates = Jinja2Templates(directory="app/templates")

# Mount static files
os.makedirs("app/static", exist_ok=True)
os.makedirs("app/static/css", exist_ok=True)
app.mount("/static", StaticFiles(directory="app/static"), name="static")

# Include routers
app.include_router(trends.router)
app.include_router(generations.router)
app.include_router(assets.router)


@app.on_event("startup")
async def startup_event():
    """Initialize database on startup"""
    await init_db()
    
    # Create default account if it doesn't exist
    async with async_session_maker() as db:
        result = await db.execute(select(Account).where(Account.id == 1))
        account = result.scalar_one_or_none()
        
        if not account:
            account = Account(id=1, balance=settings.initial_balance)
            db.add(account)
            await db.commit()


@app.get("/", response_class=HTMLResponse)
async def index(request: Request, db: AsyncSession = Depends(get_db)):
    """Home page with trends catalog"""
    result = await db.execute(select(Trend).where(Trend.is_active == True))
    trends_list = result.scalars().all()
    
    return templates.TemplateResponse(
        "index.html",
        {
            "request": request,
            "trends": trends_list,
        },
    )


@app.get("/trends", response_class=HTMLResponse)
async def trends_page(request: Request, db: AsyncSession = Depends(get_db)):
    """Trends catalog page"""
    result = await db.execute(select(Trend).where(Trend.is_active == True))
    trends_list = result.scalars().all()
    
    return templates.TemplateResponse(
        "index.html",
        {
            "request": request,
            "trends": trends_list,
        },
    )


@app.get("/trends/{trend_id}/generate", response_class=HTMLResponse)
async def generate_page(
    trend_id: int,
    request: Request,
    db: AsyncSession = Depends(get_db),
):
    """Generation page for a specific trend"""
    result = await db.execute(select(Trend).where(Trend.id == trend_id))
    trend = result.scalar_one_or_none()
    
    if not trend:
        raise HTTPException(status_code=404, detail="Trend not found")
    
    return templates.TemplateResponse(
        "generate.html",
        {
            "request": request,
            "trend": trend,
        },
    )


@app.get("/generations/{generation_id}", response_class=HTMLResponse)
async def generation_status_page(
    generation_id: int,
    request: Request,
    db: AsyncSession = Depends(get_db),
):
    """Generation status page"""
    result = await db.execute(
        select(Generation).where(Generation.id == generation_id)
    )
    generation = result.scalar_one_or_none()
    
    if not generation:
        raise HTTPException(status_code=404, detail="Generation not found")
    
    # Get trend info
    result = await db.execute(select(Trend).where(Trend.id == generation.trend_id))
    trend = result.scalar_one_or_none()
    
    return templates.TemplateResponse(
        "generation_status.html",
        {
            "request": request,
            "generation": generation,
            "trend": trend,
        },
    )


# Admin routes
@app.get("/admin/trends", response_class=HTMLResponse)
async def admin_trends_list(
    request: Request,
    db: AsyncSession = Depends(get_db),
    admin: str = Depends(verify_admin),
):
    """Admin trends management page"""
    result = await db.execute(select(Trend))
    trends_list = result.scalars().all()
    
    return templates.TemplateResponse(
        "admin/trends.html",
        {
            "request": request,
            "trends": trends_list,
        },
    )


@app.get("/admin/trends/create", response_class=HTMLResponse)
async def admin_create_trend(request: Request, admin: str = Depends(verify_admin)):
    """Admin trend creation form"""
    return templates.TemplateResponse(
        "admin/trend_form.html",
        {
            "request": request,
            "trend": None,
        },
    )


@app.get("/admin/trends/{trend_id}/edit", response_class=HTMLResponse)
async def admin_edit_trend(
    trend_id: int,
    request: Request,
    db: AsyncSession = Depends(get_db),
    admin: str = Depends(verify_admin),
):
    """Admin trend edit form"""
    result = await db.execute(select(Trend).where(Trend.id == trend_id))
    trend = result.scalar_one_or_none()
    
    if not trend:
        raise HTTPException(status_code=404, detail="Trend not found")
    
    return templates.TemplateResponse(
        "admin/trend_form.html",
        {
            "request": request,
            "trend": trend,
        },
    )


@app.get("/balance")
async def get_balance(db: AsyncSession = Depends(get_db)):
    """Get current token balance"""
    result = await db.execute(select(Account).where(Account.id == 1))
    account = result.scalar_one_or_none()
    
    if not account:
        raise HTTPException(status_code=500, detail="Account not found")
    
    return {"balance": account.balance}


if __name__ == "__main__":
    import uvicorn
    
    uvicorn.run(
        "app.main:app",
        host=settings.app_host,
        port=settings.app_port,
        reload=False,
    )
