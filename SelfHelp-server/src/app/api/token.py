from fastapi import APIRouter, HTTPException, status, Depends, Request
from typing import List, Dict, Any, Optional
from app.config import settings
from app.logger import logger
import httpx

token_router = APIRouter(tags=["token"])


@token_router.post("/assemblyaiToken", status_code=status.HTTP_200_OK)
async def get_assembly_token() -> Dict[str, Any]:
    """
    Get AssemblyAI token for client-side use
    
    Returns:
        Dict: Token information
    """
    if not settings.ASSEMBLYAI_API_KEY:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="AssemblyAI API key not configured"
        )


    try:
        url = "https://streaming.assemblyai.com/v3/token"
        headers = { "authorization": settings.ASSEMBLYAI_API_KEY }
        params = {
            "expires_in_seconds": 600,
            "max_session_duration_seconds": 600
        }

        async with httpx.AsyncClient() as client:
            response = await client.get(url, headers=headers, params=params)
            response.raise_for_status()#Raise Httpx error if not 200
            return response.json()
            
    except httpx.HTTPStatusError as e:
        error_msg = f"Error from AssemblyAI API: {e.response.text}"
        logger.info("ERROR: get_assembly_token %s", error_msg)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=error_msg
        )

@token_router.post("/heygenToken", status_code=status.HTTP_200_OK)
async def get_heygen_token() -> Dict[str, Any]:
    """
    Get Heygen token for client-side use
    
    Returns:
        Dict: Token information
    """
    if not settings.HEYGEN_API_KEY:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Heygen API key not configured"
        )


    try:
        url = "https://api.heygen.com/v1/streaming.create_token"
        payload = {}
        headers = {
            "accept": "application/json",
            "content-type": "application/json",
            "x-api-key": settings.HEYGEN_API_KEY
        }

        async with httpx.AsyncClient() as client:
            response = await client.post(url, headers=headers, params=payload)
            response.raise_for_status()#Raise Httpx error if not 200
            response_data = response.json()
            #print(response_data["data"])
            return response_data["data"]
            
    except httpx.HTTPStatusError as e:
        error_msg = f"Error from HeyGen API: {e.response.text}"
        logger.info("ERROR: get_heygen_token %s", error_msg)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=error_msg
        )
    
