import os
import aiofiles
from fastapi import APIRouter, Depends, UploadFile, File, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.database import get_db
from app.models import Asset
from app.schemas import AssetResponse
from typing import List
from datetime import datetime

router = APIRouter(prefix="/api/assets", tags=["assets"])

UPLOAD_DIR = "uploads"
MAX_FILE_SIZE = 10 * 1024 * 1024  # 10 MB
ALLOWED_MIME_TYPES = {
    "image/jpeg", "image/png", "image/gif", "image/webp",
    "video/mp4", "video/webm", "video/quicktime",
    "application/pdf", "text/plain"
}

# Create uploads directory if it doesn't exist
os.makedirs(UPLOAD_DIR, exist_ok=True)


@router.post("/upload", response_model=List[AssetResponse])
async def upload_assets(
    files: List[UploadFile] = File(...),
    db: AsyncSession = Depends(get_db),
):
    """Upload one or multiple files"""
    uploaded_assets = []
    
    for file in files:
        try:
            # Validate MIME type
            mime_type = file.content_type or "application/octet-stream"
            if mime_type not in ALLOWED_MIME_TYPES:
                raise HTTPException(
                    status_code=400,
                    detail=f"File type {mime_type} not allowed. Allowed types: {', '.join(ALLOWED_MIME_TYPES)}"
                )
            
            # Read file content
            content = await file.read()
            
            # Validate file size
            if len(content) > MAX_FILE_SIZE:
                raise HTTPException(
                    status_code=400,
                    detail=f"File {file.filename} exceeds maximum size of {MAX_FILE_SIZE / 1024 / 1024} MB"
                )
            
            # Generate unique filename
            timestamp = datetime.utcnow().timestamp()
            filename = f"{timestamp}_{file.filename}"
            file_path = os.path.join(UPLOAD_DIR, filename)
            
            # Save file
            async with aiofiles.open(file_path, "wb") as f:
                await f.write(content)
            
            # Create asset record
            asset = Asset(
                filename=file.filename,
                path=filename,
                content_type=mime_type,
                size=len(content),
            )
            
            db.add(asset)
            await db.flush()  # Flush to get the ID
            uploaded_assets.append(asset)
            
        except HTTPException:
            await db.rollback()
            raise
        except Exception as e:
            await db.rollback()
            raise HTTPException(status_code=400, detail=f"Error uploading file: {str(e)}")
    
    await db.commit()
    
    # Refresh all assets to get their IDs
    for asset in uploaded_assets:
        await db.refresh(asset)
    
    return uploaded_assets
