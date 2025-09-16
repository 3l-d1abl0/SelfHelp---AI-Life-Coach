from fastapi import APIRouter, HTTPException, status, Depends, Request, WebSocket, WebSocketDisconnect
from typing import List, Dict, Any, Optional
from app.logger import logger
from datetime import datetime
import json
from app.models.gemini import geminiai
from app.lib.valkey import save_session, get_session

#Websocket Router initialized
websocket_router = APIRouter(tags=["websocket"])


def get_recent_mentor_message(conversation_data):

    for entry in reversed(conversation_data):
        if entry.get("role") == "model":
            if entry.get("parts") and isinstance(entry["parts"], list) and len(entry["parts"]) > 0:
                # Assuming the 'text' is in the first part of the 'parts' list
                message = ""
                for part in entry["parts"]:
                    message +=part.get("text")
                

                return message
    return None


# Connection manager for WebSocket connections
class ConnectionManager:
    def __init__(self):
        self.active_connections: Dict[str, WebSocket] = {}
        self.sessions: Dict[str, Dict] = {}

    async def connect(self, websocket: WebSocket, session_id: str):
        await websocket.accept()
        self.active_connections[session_id] = websocket 
        #print("CONNECTED: ", session_id, websocket)
        
        chat_history = chat_history = await get_session(session_id)

        mentor_message = get_recent_mentor_message(chat_history)
        
        # Send welcome message
        await self.send_message(session_id, {
            "type": "initiation",
            "message": mentor_message,
            "session_id": session_id
        })

    def disconnect(self, session_id: str):
        if session_id in self.active_connections:
            del self.active_connections[session_id]
        logger.info(f"WebSocket disconnected: {session_id}")

    async def send_message(self, session_id: str, data: dict):
        if session_id in self.active_connections:
            try:
                print("sending .... ")
                await self.active_connections[session_id].send_text(json.dumps(data))
            except Exception as e:
                logger.error(f"Error sending message to {session_id}: {e}")
                self.disconnect(session_id)


manager = ConnectionManager()


@websocket_router.websocket("/ws/{session_id}")
async def websocket_endpoint(websocket: WebSocket, session_id: str):
    await manager.connect(websocket, session_id)

    # Get a Redis client
    chat_history = await get_session(session_id)

    chat = geminiai.model.start_chat(history=chat_history)

    try:
        while True:
            # Receive message from client
            data = await websocket.receive_text()
            print("data: ", data)
            message_data = json.loads(data)
            print("REC: ", message_data)
            # if message_data["type"] == "user_message":
            #     user_message = message_data["message"]

            #     # Send typing indicator
            #     await manager.send_message(session_id, {
            #         "recieved": user_message,
            #         "timestamp": datetime.now().isoformat()
            #     })
                
                
            # elif message_data["type"] == "ping":
            #     # Handle ping/pong for connection keepalive
            #     await manager.send_message(session_id, {
            #         "type": "pong",
            #         "timestamp": datetime.now().isoformat()
            #     })

            response = chat.send_message(message_data["message"])
            updated_history = chat.history
            await save_session(str(session_id), updated_history)# OK

            await manager.send_message(session_id, {
                "type": "conversation",
                "message": response.text,
                "session_id": session_id
            })

                
    except WebSocketDisconnect:
        manager.disconnect(session_id)
    except Exception as e:
        logger.error(f"WebSocket error: {e}")
        manager.disconnect(session_id)


