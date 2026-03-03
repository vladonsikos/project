import logging
from sqlalchemy.orm import sessionmaker
from sqlalchemy import select
from app.models import Generation, Trend, Account
from app.config import settings
from app.services.openrouter import call_openrouter

logger = logging.getLogger(__name__)


async def run_generation_async(generation_id: int, db_session) -> None:
    """
    Run generation task asynchronously
    
    Args:
        generation_id: ID of generation record
        db_session: Database session
    """
    try:
        # Get generation record
        result = await db_session.execute(
            select(Generation).where(Generation.id == generation_id)
        )
        generation = result.scalar_one_or_none()
        
        if not generation:
            logger.error(f"Generation {generation_id} not found")
            return
        
        # Update status to processing
        generation.status = "processing"
        await db_session.commit()
        
        # Call OpenRouter
        try:
            result_text = await call_openrouter(generation.prompt, generation.materials)
            generation.status = "completed"
            generation.result_text = result_text
        except Exception as e:
            generation.status = "failed"
            generation.result_text = f"Error: {str(e)}"
            logger.error(f"Generation {generation_id} failed: {str(e)}")
        
        await db_session.commit()
        
    except Exception as e:
        logger.error(f"Unexpected error in run_generation_async: {str(e)}")
        raise
