import json
from app.db.redis import redis_manager

async def save_session(meeting_id, chat_history):
    """
    Converts chat history to a JSON-serializable format and saves it.
    
    Args:
        user_id (str): The unique user identifier.
        chat_history (list): The list of genai.types.Content objects from chat.history.
    """
    # Create a list to hold the serializable message dictionaries
    serializable_history = []
    print("Chat History !!!!")
    # Iterate through the Content objects
    for message in chat_history:
        # Each Content object has 'role' and 'parts' attributes
        # The 'parts' are also custom objects, so we need to extract their text
        
        # Build the 'parts' list for the current message
        serializable_parts = []
        for part in message.parts:
            # Check for the existence of the 'text' attribute
            if hasattr(part, 'text'):
                serializable_parts.append({'text': part.text})
            # You might need to handle other part types like 'file_data' or 'function_call'
            # based on your application's needs
        
        # Build the full serializable message dictionary
        serializable_message = {
            "role": message.role,
            "parts": serializable_parts
        }
        
        serializable_history.append(serializable_message)

    print("Redies ....")
    redis_client = await redis_manager.get_redis_client()
    await redis_client.set(meeting_id, json.dumps(serializable_history))
    print("Redies !!!!!!")
    
    print(f"Session for Meeting '{meeting_id}' saved successfully.")