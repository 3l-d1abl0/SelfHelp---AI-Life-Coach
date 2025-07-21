from fastapi import APIRouter, HTTPException, status, Depends, Request, Body
from datetime import datetime
from typing import List, Dict, Any, Optional
from pydantic import BaseModel
from app.config import settings
from app.logger import logger
from app.db.mongodb import db
import httpx
from bson.objectid import ObjectId

meeting_router = APIRouter(tags=["meeting"])

class MeetingCreate(BaseModel):
    transcript: str

class MeetingData(BaseModel):
    meetingId: str

class MeetingStopResponse(BaseModel):
    status: str
    message: str

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
            "created_at": datetime.utcnow(),
            "status": "SCHEDULED"
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


@meeting_router.post("/meeting/start", status_code=status.HTTP_200_OK)
async def start_new_meeting(meeting_data: MeetingData) -> Dict[str, Any]:
    """
    Receives meeting id for a meeting and starts a response with the System.
    
    Args:
        meeting_data (MeetingData): The meeting data containing the meeting id.
        
    Returns:
        Dict[str, Any]: Returns the updated meeting status and relevant message.
    """
    try:
        meeting_collection = db.get_db()[settings.MONGODB_MEETINGS_COLLECTION]
        
        # Find the meeting by ID
        meeting = meeting_collection.find_one({"_id": ObjectId(meeting_data.meetingId)})
        if not meeting:
            raise HTTPException(status_code=404, detail="Meeting not found")
        
        current_time = datetime.utcnow()
        update_data = {}
        response = {}
        
        if meeting.get("status") == "SCHEDULED":
            update_data = {
                "status": "ONGOING",
                "starting_time": current_time
            }
            response = {
                "status": "meeting_started",
                "message": "Meeting has been started successfully"
            }
            
        elif meeting.get("status") == "ONGOING":
            starting_time = meeting.get("starting_time")
            if not starting_time:
                # If for some reason starting_time is not set, update it to now
                starting_time = current_time
                update_data["starting_time"] = current_time
                
            time_difference = (current_time - starting_time).total_seconds()
            
            if time_difference >= 600:
                update_data["status"] = "OVER"
                update_data["end_time"] = current_time
                response = {
                    "status": "meeting_ended",
                    "message": "Meeting has ended as it exceeded the 10-minute duration"
                }
            else:
                remaining_seconds = 600 - time_difference
                response = {
                    "status": "meeting_ongoing",
                    "message": f"Meeting is ongoing. {remaining_seconds} seconds remaining.",
                    "remaining_seconds": remaining_seconds
                }
                
        elif meeting.get("status") == "OVER":
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="Meeting has already ended"
            )
        
        else:
            logger.error(f"Error: meeting with no status: {str(e)}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="An error occurred while processing the meeting"
            )    
        
        # Update the meeting in MongoDB if there are changes
        if update_data:
            meeting_collection.update_one(
                {"_id": ObjectId(meeting_data.meetingId)},
                {"$set": update_data}
            )
        
        return response
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error in {str(meeting_data.meetingId)} /meeting/start: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An error occurred while processing the meeting"
        )

@meeting_router.post("/meeting/stop", response_model=MeetingStopResponse, status_code=status.HTTP_200_OK)
async def stop_meeting(meeting_data: MeetingData) -> Dict[str, Any]:
    """
    Stops an ongoing meeting by updating its status to OVER and setting the ending time.
    
    Args:
        meeting_data (MeetingData): The meeting data containing the meeting id.
        
    Returns:
        Dict[str, Any]: Returns the updated meeting status and relevant message.
    """
    try:
        meeting_collection = db.get_db()[settings.MONGODB_MEETINGS_COLLECTION]
        
        # Find the meeting by ID
        meeting = meeting_collection.find_one({"_id": ObjectId(meeting_data.meetingId)})
        if not meeting:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Meeting not found"
            )
        
        # Check if meeting is already over
        if meeting.get("status") == "OVER":
            return {
                "status": "already_ended",
                "message": "Meeting has already ended"
            }
            
        # Check if meeting is in a valid state to be stopped
        if meeting.get("status") != "ONGOING":
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Cannot stop a meeting that is {meeting.get('status', 'not started')}"
            )
        
        # Update the meeting status to OVER and set ending time
        current_time = datetime.utcnow()
        meeting_collection.update_one(
            {"_id": ObjectId(meeting_data.meetingId)},
            {
                "$set": {
                    "status": "OVER",
                    "ending_time": current_time
                }
            }
        )
        
        return {
            "status": "meeting_ended",
            "message": "Meeting has been successfully ended"
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error in {str(meeting_data.meetingId)} /meeting/stop: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An error occurred while stopping the meeting"
        )