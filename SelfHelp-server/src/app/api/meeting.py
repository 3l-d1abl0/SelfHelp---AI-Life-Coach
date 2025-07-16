from fastapi import APIRouter, HTTPException, status, Depends, Request, Body
from datetime import datetime
from typing import List, Dict, Any, Optional
from pydantic import BaseModel
from app.config import settings
from app.logger import logger
from app.db.mongodb import db
import httpx

meeting_router = APIRouter(tags=["meeting"])

class MeetingCreate(BaseModel):
    transcript: str

@meeting_router.post("/meeting/new", status_code=status.HTTP_201_CREATED)
async def create_new_meeting(meeting_data: MeetingCreate) -> Dict[str, Any]:
    """
    Receives transcription/context for a new meeting and stores it in the database.
    
    Args:
        meeting_data (MeetingCreate): The meeting data containing the transcript.
        
    Returns:
        Dict[str, Any]: The ID of the newly created meeting document.
    """
    try:
        logger.error("___________________________________")
        meeting_collection = db.get_db()[settings.MONGODB_MEETINGS_COLLECTION]
        logger.error("___________________________________")
        
        # Prepare the document to insert
        meeting_doc = {
            "transcript": meeting_data.transcript,
            "created_at": datetime.utcnow()
        }
        
        # Insert the document
        result = meeting_collection.insert_one(meeting_doc)
        
        # Return the ID of the inserted document
        return {"id": str(result.inserted_id)}

    except Exception as e:
        logger.error(f"Error creating meeting: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to create meeting"
        )