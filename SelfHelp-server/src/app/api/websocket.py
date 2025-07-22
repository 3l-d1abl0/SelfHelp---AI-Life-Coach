from fastapi import APIRouter, HTTPException, status, Depends, Request, WebSocket, WebSocketDisconnect
from typing import List, Dict, Any, Optional
from app.config import settings
from app.logger import logger
from datetime import datetime
import json
import requests
import base64
import google.generativeai as genai
from app.db.redis import redis_manager


#Websocket Router initialized
websocket_router = APIRouter(tags=["websocket"])

# Connection manager for WebSocket connections
class ConnectionManager:
    def __init__(self):
        self.active_connections: Dict[str, WebSocket] = {}
        self.sessions: Dict[str, Dict] = {}

    async def connect(self, websocket: WebSocket, session_id: str):
        await websocket.accept()
        self.active_connections[session_id] = websocket 

        #print("CONNECTED: ", websocket.session)
        print("CONNECTED: ", websocket)
        
        # Send welcome message
        await self.send_message(session_id, {
            "type": "conversation",
            "message": "Connected! I'm your AI nutrition and fitness assistant. How can I help you today?",
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



idx = 1
temp_session_id = "6877e77032a8114efc923014"


@websocket_router.websocket("/ws/{session_id}")
async def websocket_endpoint(websocket: WebSocket, session_id: str):
    await manager.connect(websocket, session_id)

    # Get a Redis client
    redis_client = await redis_manager.get_redis_client()

    # Use the client
    await redis_client.set("key", "value")
    chat_history = await redis_client.get(temp_session_id)
    #print(chat_history)

    if chat_history:
        chat_history = json.loads(chat_history)


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

            serializable_message = ""
            if message_data["type"] =="user_message":
                global idx
                idx+=2

                print("USER: ", message_data["message"])
                print("CHAT: ", chat_history[idx])

                serializable_parts = ""
                for part in chat_history[idx]["parts"]:
                    print('PART: ', part)
                    serializable_message += part["text"]
                    # if hasattr(part, 'text'):
                    #     serializable_parts.append({'text': part.text})


            reply = f"you Send : {data}"
            await manager.send_message(session_id, {
                "type": "conversation",
                "message": serializable_message,
                "session_id": temp_session_id
            })

                
    except WebSocketDisconnect:
        manager.disconnect(session_id)
    except Exception as e:
        logger.error(f"WebSocket error: {e}")
        manager.disconnect(session_id)


