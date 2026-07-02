from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
import httpx
from ..config import get_settings

router = APIRouter()
settings = get_settings()

class OllamaGenerateRequest(BaseModel):
    prompt: str
    model: str = "gemma:2b"
    stream: bool = False
    context: list[int] | None = None
    options: dict | None = None

class OllamaGenerateResponse(BaseModel):
    model: str
    created_at: str
    response: str
    done: bool
    context: list[int] | None = None
    total_duration: int | None = None
    load_duration: int | None = None
    prompt_eval_count: int | None = None
    prompt_eval_duration: int | None = None
    eval_count: int | None = None
    eval_duration: int | None = None

class OllamaModelInfo(BaseModel):
    name: str
    model: str
    modified_at: str
    size: int
    digest: str
    details: dict

class OllamaModelsResponse(BaseModel):
    models: list[OllamaModelInfo]

@router.post("/generate", response_model=OllamaGenerateResponse)
async def generate_text(request: OllamaGenerateRequest):
    """Generate text using Ollama model"""
    try:
        async with httpx.AsyncClient() as client:
            response = await client.post(
                f"{settings.OLLAMA_URL}/api/generate",
                json={
                    "model": request.model,
                    "prompt": request.prompt,
                    "stream": request.stream,
                    "context": request.context,
                    "options": request.options
                },
                timeout=120.0
            )
            response.raise_for_status()
            return response.json()
    except httpx.HTTPStatusError as e:
        raise HTTPException(status_code=e.response.status_code, detail=f"Ollama error: {e.response.text}")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/models", response_model=OllamaModelsResponse)
async def list_models():
    """List available Ollama models"""
    try:
        async with httpx.AsyncClient() as client:
            response = await client.get(f"{settings.OLLAMA_URL}/api/tags")
            response.raise_for_status()
            return response.json()
    except httpx.HTTPStatusError as e:
        raise HTTPException(status_code=e.response.status_code, detail=f"Ollama error: {e.response.text}")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/chat")
async def chat_completion(request: dict):
    """Chat completion endpoint (OpenAI-compatible format)"""
    try:
        # Convert OpenAI-like request to Ollama format
        model = request.get("model", "gemma:2b")
        messages = request.get("messages", [])
        # For simplicity, we'll just concatenate messages into a prompt
        # In a more advanced implementation, you'd use Ollama's chat API
        prompt = "\n".join([f"{msg.get('role', 'user')}: {msg.get('content', '')}" for msg in messages])
        
        async with httpx.AsyncClient() as client:
            response = await client.post(
                f"{settings.OLLAMA_URL}/api/generate",
                json={
                    "model": model,
                    "prompt": prompt,
                    "stream": request.get("stream", False)
                },
                timeout=120.0
            )
            response.raise_for_status()
            return response.json()
    except httpx.HTTPStatusError as e:
        raise HTTPException(status_code=e.response.status_code, detail=f"Ollama error: {e.response.text}")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))