import aiohttp
import json
import logging
from app.config import settings

logger = logging.getLogger(__name__)


async def call_openrouter(prompt: str, materials: str = None, asset_ids: list = None) -> str:
    """
    Call OpenRouter API to generate content
    
    Args:
        prompt: Main prompt for generation
        materials: Additional materials/links (optional)
    
    Returns:
        Generated text from the API
    
    Raises:
        Exception: If API call fails
    """
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
                
    except aiohttp.ClientError as e:
        logger.error(f"Network error calling OpenRouter: {str(e)}")
        raise Exception(f"Network error: {str(e)}")
    except json.JSONDecodeError as e:
        logger.error(f"JSON decode error from OpenRouter: {str(e)}")
        raise Exception(f"Invalid response format: {str(e)}")
    except Exception as e:
        logger.error(f"Error calling OpenRouter: {str(e)}")
        raise
