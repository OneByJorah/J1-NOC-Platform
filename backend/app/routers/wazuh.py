from fastapi import APIRouter, HTTPException
from fastapi.responses import JSONResponse
import os
import urllib.parse
from typing import Optional, Dict, Any

import requests
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry

router = APIRouter()

WAZUH_API_URL = os.getenv("WAZUH_API_URL", "https://localhost:55000").rstrip("/")
WAZUH_USERNAME = os.getenv("WAZUH_USERNAME", "wazuh")
WAZUH_PASSWORD = os.getenv("WAZUH_PASSWORD", "wazuh")
OLLAMA_API_URL = os.getenv("OLLAMA_HOST", "http://localhost:11434").rstrip("/")

def _session() -> requests.Session:
    session = requests.Session()
    retries = Retry(total=2, backoff_factor=0.5, status_forcelist=[502, 503, 504])
    session.mount("https://", HTTPAdapter(max_retries=retries))
    session.mount("http://", HTTPAdapter(max_retries=retries))
    return session


def get_wazuh_token() -> Optional[str]:
    """Get authentication token for Wazuh API"""
    try:
        with _session() as session:
            response = session.post(
                urllib.parse.urljoin(WAZUH_API_URL, "/security/user/authenticate"),
                auth=(WAZUH_USERNAME, WAZUH_PASSWORD),
                verify=False,
                timeout=10,
            )
        if response.status_code == 200:
            return response.json()["data"]["token"]
        return None
    except Exception:
        return None

@router.get("/wazuh/status")
def get_wazuh_status():
    """Get Wazuh service status"""
    try:
        token = get_wazuh_token()
        if not token:
            return JSONResponse({"status": "Disconnected", "error": "Authentication failed"})

        headers = {"Authorization": f"Bearer {token}"}
        with _session() as session:
            response = session.get(
                urllib.parse.urljoin(WAZUH_API_URL, "/manager/status"),
                headers=headers,
                verify=False,
                timeout=10,
            )

        if response.status_code == 200:
            return JSONResponse({"status": "Connected", "data": response.json()})
        return JSONResponse({"status": "Disconnected", "error": f"API returned {response.status_code}"})
    except Exception as e:
        return JSONResponse({"status": "Disconnected", "error": str(e)})


@router.get("/wazuh/agents")
def get_wazuh_agents():
    """Get list of Wazuh agents"""
    try:
        token = get_wazuh_token()
        if not token:
            raise HTTPException(status_code=401, detail="Authentication failed")

        headers = {"Authorization": f"Bearer {token}"}
        with _session() as session:
            response = session.get(
                urllib.parse.urljoin(WAZUH_API_URL, "/agents"),
                headers=headers,
                verify=False,
                timeout=10,
            )

        if response.status_code == 200:
            return JSONResponse(response.json())
        raise HTTPException(status_code=response.status_code, detail=f"API returned {response.status_code}")
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/wazuh/alerts")
def get_wazuh_alerts(limit: int = 50, offset: int = 0):
    """Get recent Wazuh alerts"""
    try:
        token = get_wazuh_token()
        if not token:
            raise HTTPException(status_code=401, detail="Authentication failed")

        headers = {"Authorization": f"Bearer {token}"}
        params = {
            "limit": limit,
            "offset": offset,
            "sort": "-timestamp",
        }
        with _session() as session:
            response = session.get(
                urllib.parse.urljoin(WAZUH_API_URL, "/alerts"),
                headers=headers,
                params=params,
                verify=False,
                timeout=10,
            )

        if response.status_code == 200:
            return JSONResponse(response.json())
        raise HTTPException(status_code=response.status_code, detail=f"API returned {response.status_code}")
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/wazuh/overview")
def get_wazuh_overview():
    """Get Wazuh system overview"""
    try:
        token = get_wazuh_token()
        if not token:
            raise HTTPException(status_code=401, detail="Authentication failed")

        headers = {"Authorization": f"Bearer {token}"}

        # Get manager info
        with _session() as session:
            manager_response = session.get(
                urllib.parse.urljoin(WAZUH_API_URL, "/manager/info"),
                headers=headers,
                verify=False,
                timeout=10,
            )

            # Get agents summary
            agents_response = session.get(
                urllib.parse.urljoin(WAZUH_API_URL, "/agents/summary/status"),
                headers=headers,
                verify=False,
                timeout=10,
            )

            # Get alerts summary
            alerts_response = session.get(
                urllib.parse.urljoin(WAZUH_API_URL, "/overview/alerts"),
                headers=headers,
                verify=False,
                timeout=10,
            )

        overview = {
            "manager": manager_response.json() if manager_response.status_code == 200 else {},
            "agents": agents_response.json() if agents_response.status_code == 200 else {},
            "alerts": alerts_response.json() if alerts_response.status_code == 200 else {},
        }

        return JSONResponse(overview)
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/ollama/status")
def get_ollama_status():
    """Get Ollama service status"""
    try:
        with _session() as session:
            response = session.get(
                urllib.parse.urljoin(OLLAMA_API_URL, "/api/tags"),
                timeout=10,
            )
        if response.status_code == 200:
            return JSONResponse({"status": "Connected", "models": response.json().get("models", [])})
        return JSONResponse({"status": "Disconnected", "error": f"API returned {response.status_code}"})
    except Exception as e:
        return JSONResponse({"status": "Disconnected", "error": str(e)})


@router.post("/ollama/chat")
def chat_with_ollama(payload: Dict[str, Any]):
    """Chat with Ollama model"""
    try:
        model = payload.get("model", "llama3.2:1b")
        prompt = payload.get("prompt", "")

        if not prompt:
            raise HTTPException(status_code=400, detail="Prompt is required")

        with _session() as session:
            response = session.post(
                urllib.parse.urljoin(OLLAMA_API_URL, "/api/generate"),
                json={
                    "model": model,
                    "prompt": prompt,
                    "stream": False,
                },
                timeout=120,
            )

        if response.status_code == 200:
            return JSONResponse(response.json())
        raise HTTPException(status_code=response.status_code, detail=f"Ollama API returned {response.status_code}")
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))