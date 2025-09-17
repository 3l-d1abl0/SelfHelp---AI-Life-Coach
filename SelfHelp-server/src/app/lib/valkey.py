import json
from app.db.valkey import valkey_manager
from typing import List, Dict, Any, Optional
from app.logger import logger

async def save_session(meeting_id: str, chat_history: List[Any]) -> None:
    """
    Converts chat history to a JSON-serializable format and saves it to Valkey.
    
    Args:
        meeting_id (str): The unique meeting identifier.
        chat_history (list): The list of genai.types.Content objects from chat.history.
    """
    try:
        # List to hold the serializable message dictionaries
        serializable_history = []
        logger.debug(f"Processing chat history for meeting: {meeting_id}")
        
        # Iterate through the Content objects
        for message in chat_history:
            
            # Build the 'parts' list for the current message
            serializable_parts = []
            for part in message.parts:

                # Check for the existence of the 'text' attribute
                if hasattr(part, 'text'):
                    serializable_parts.append({'text': part.text})
            
            serializable_message = {
                "role": message.role,
                "parts": serializable_parts
            }
            
            serializable_history.append(serializable_message)

        logger.debug("Saving session to Valkey...")
        
        # Get Valkey client and save the session
        valkey_client = await valkey_manager.get_valkey_client()
        session_data = json.dumps(serializable_history)
        
        #await valkey_client.setex(meeting_id, 86400, session_data)  # 24 hours TTL
        await valkey_client.set(meeting_id, session_data)  # OK
        
        logger.info(f"Session for Meeting '{meeting_id}' saved successfully.")
        
    except Exception as e:
        logger.error(f"Error saving session for meeting '{meeting_id}': {str(e)}")
        raise


async def get_session(meeting_id: str) -> Optional[List[Dict[str, Any]]]:
    """
    Retrieves and deserializes chat history from Valkey.
    
    Args:
        meeting_id (str): The unique meeting identifier.
        
    Returns:
        Optional[List[Dict[str, Any]]]: The deserialized chat history, or None if not found.
    """
    try:
        logger.debug(f"Retrieving session for meeting: {meeting_id}")
        
        # Get Valkey client
        valkey_client = await valkey_manager.get_valkey_client()
        
        # Retrieve session data from Valkey
        session_data = await valkey_client.get(meeting_id)
        
        if session_data is None:
            logger.info(f"No session found for meeting '{meeting_id}'")
            return None
        
        # Valkey GLIDE returns bytes, so we need to decode
        if isinstance(session_data, bytes):
            session_data = session_data.decode('utf-8')
        
        # Deserialize JSON data
        chat_history = json.loads(session_data)
        
        logger.info(f"Session for meeting '{meeting_id}' retrieved successfully. Found {len(chat_history)} messages.")
        return chat_history
        
    except json.JSONDecodeError as e:
        logger.error(f"Error deserializing session data for meeting '{meeting_id}': {str(e)}")
        return None
    except Exception as e:
        logger.error(f"Error retrieving session for meeting '{meeting_id}': {str(e)}")
        raise


async def delete_session(meeting_id: str) -> bool:
    """
    Deletes a session from Valkey.
    
    Args:
        meeting_id (str): The unique meeting identifier.
        
    Returns:
        bool: True if session was deleted, False if it didn't exist.
    """
    try:
        logger.debug(f"Deleting session for meeting: {meeting_id}")
        
        # Get Valkey client
        valkey_client = await valkey_manager.get_valkey_client()
        
        # Delete the session
        result = await valkey_client.delete([meeting_id])
        
        if result > 0:
            logger.info(f"Session for meeting '{meeting_id}' deleted successfully.")
            return True
        else:
            logger.info(f"No session found to delete for meeting '{meeting_id}'")
            return False
            
    except Exception as e:
        logger.error(f"Error deleting session for meeting '{meeting_id}': {str(e)}")
        raise


async def session_exists(meeting_id: str) -> bool:
    """
    Checks if a session exists in Valkey.
    
    Args:
        meeting_id (str): The unique meeting identifier.
        
    Returns:
        bool: True if session exists, False otherwise.
    """
    try:
        logger.debug(f"Checking if session exists for meeting: {meeting_id}")
        
        # Get Valkey client
        valkey_client = await valkey_manager.get_valkey_client()
        
        # Check if key exists
        result = await valkey_client.exists([meeting_id])
        
        exists = result > 0
        logger.debug(f"Session exists for meeting '{meeting_id}': {exists}")
        return exists
        
    except Exception as e:
        logger.error(f"Error checking session existence for meeting '{meeting_id}': {str(e)}")
        return False


async def extend_session_ttl(meeting_id: str, ttl_seconds: int = 86400) -> bool:
    """
    Extends the TTL (time to live) of a session.
    
    Args:
        meeting_id (str): The unique meeting identifier.
        ttl_seconds (int): New TTL in seconds (default: 24 hours).
        
    Returns:
        bool: True if TTL was extended, False if session doesn't exist.
    """
    try:
        logger.debug(f"Extending TTL for session: {meeting_id}")
        
        # Get Valkey client
        valkey_client = await valkey_manager.get_valkey_client()
        
        # Extend TTL
        result = await valkey_client.expire(meeting_id, ttl_seconds)
        
        if result:
            logger.info(f"TTL extended for meeting '{meeting_id}' to {ttl_seconds} seconds.")
            return True
        else:
            logger.warning(f"Could not extend TTL for meeting '{meeting_id}' - session may not exist.")
            return False
            
    except Exception as e:
        logger.error(f"Error extending TTL for meeting '{meeting_id}': {str(e)}")
        return False