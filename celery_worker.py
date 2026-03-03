import logging
import os
import sys
from celery import Celery
from sqlalchemy import create_engine, select
from sqlalchemy.orm import sessionmaker

# Add project to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app.config import settings
from app.models import Generation, Account, Base
from app.services.openrouter import call_openrouter

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Create Celery app
app = Celery(
    "trendsee",
    broker=settings.celery_broker_url,
    backend=settings.celery_result_backend,
)

# Configure Celery
app.conf.update(
    task_serializer="json",
    accept_content=["json"],
    result_serializer="json",
    timezone="UTC",
    enable_utc=True,
    task_track_started=True,
)

# Setup synchronous SQLAlchemy for Celery tasks
engine = create_engine(settings.sync_database_url, echo=False)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


@app.task(bind=True, max_retries=3)
def run_generation(self, generation_id: int):
    """Celery task to run generation"""
    session = SessionLocal()
    try:
        logger.info(f"Starting generation {generation_id}")
        
        # Get generation record
        generation = session.query(Generation).filter(Generation.id == generation_id).first()
        
        if not generation:
            logger.error(f"Generation {generation_id} not found")
            return
        
        # Update status to processing
        generation.status = "processing"
        session.commit()
        
        # Call OpenRouter
        try:
            logger.info(f"Calling OpenRouter for generation {generation_id}")
            result_text = call_openrouter_sync(generation.prompt, generation.materials, generation.asset_ids)
            generation.status = "completed"
            generation.result_text = result_text
            logger.info(f"Generation {generation_id} completed successfully")
        except Exception as e:
            generation.status = "failed"
            generation.result_text = f"Error: {str(e)}"
            logger.error(f"Generation {generation_id} failed: {str(e)}")
            
            # Refund tokens on failure
            try:
                account = session.query(Account).filter(Account.id == 1).first()
                if account and generation.price_spent > 0:
                    account.balance += generation.price_spent
                    logger.info(f"Refunded {generation.price_spent} tokens to account")
            except Exception as refund_error:
                logger.error(f"Failed to refund tokens: {str(refund_error)}")
        
        session.commit()
        
    except Exception as e:
        logger.error(f"Unexpected error in run_generation: {str(e)}")
        # Retry with exponential backoff
        raise self.retry(exc=e, countdown=60)
    finally:
        session.close()


def call_openrouter_sync(prompt: str, materials: str = None, asset_ids: list = None) -> str:
    """Synchronous wrapper for OpenRouter API call"""
    import aiohttp
    import asyncio
    
    async def _call():
        if not settings.openrouter_api_key:
            raise ValueError("OPENROUTER_API_KEY is not set")
        
        # Combine prompt and materials
        full_prompt = prompt
        if materials:
            full_prompt = f"{prompt}\n\nAdditional materials:\n{materials}"
        
        # Add note about uploaded files if any
        if asset_ids and len(asset_ids) > 0:
            full_prompt += f"\n\nNote: User uploaded {len(asset_ids)} file(s) (IDs: {', '.join(map(str, asset_ids))})"
        
        headers = {
            "Authorization": f"Bearer {settings.openrouter_api_key}",
            "HTTP-Referer": "http://localhost:8000",
            "X-Title": "Trendsee",
            "Content-Type": "application/json",
        }
        
        payload = {
            "model": settings.openrouter_model,
            "messages": [
                {
                    "role": "user",
                    "content": full_prompt
                }
            ],
            "temperature": 0.7,
            "max_tokens": 2000,
        }
        
        try:
            async with aiohttp.ClientSession() as session:
                async with session.post(
                    "https://openrouter.ai/api/v1/chat/completions",
                    headers=headers,
                    json=payload,
                    timeout=aiohttp.ClientTimeout(total=60),
                ) as response:
                    if response.status != 200:
                        error_text = await response.text()
                        logger.error(f"OpenRouter API error: {response.status} - {error_text}")
                        raise Exception(f"OpenRouter API error: {response.status}")
                    
                    data = await response.json()
                    
                    if "choices" not in data or len(data["choices"]) == 0:
                        raise Exception("No choices in OpenRouter response")
                    
                    result = data["choices"][0]["message"]["content"]
                    return result
        except Exception as e:
            logger.error(f"Error calling OpenRouter: {str(e)}")
            raise
    
    # Run async function in a new event loop
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    try:
        return loop.run_until_complete(_call())
    finally:
        loop.close()


if __name__ == "__main__":
    app.start()
