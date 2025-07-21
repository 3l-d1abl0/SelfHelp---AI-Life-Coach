from fastapi import APIRouter, HTTPException, status, Depends, Request, WebSocket, WebSocketDisconnect
from typing import List, Dict, Any, Optional
from app.config import settings
from app.logger import logger
from datetime import datetime
import json
import requests
import base64
import google.generativeai as genai
import redis


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
            "type": "welcome",
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

@websocket_router.websocket("/ws/{session_id}")
async def websocket_endpoint(websocket: WebSocket, session_id: str):
    await manager.connect(websocket, session_id)

    
    try:
        while True:
            # Receive message from client
            data = await websocket.receive_text()
            print("data: ", data)
            message_data = json.loads(data)
            print("REC: ", message_data)
            if message_data["type"] == "user_message":
                user_message = message_data["message"]

                # Send typing indicator
                await manager.send_message(session_id, {
                    "recieved": user_message,
                    "timestamp": datetime.now().isoformat()
                })
                
                
            elif message_data["type"] == "ping":
                # Handle ping/pong for connection keepalive
                await manager.send_message(session_id, {
                    "type": "pong",
                    "timestamp": datetime.now().isoformat()
                })



            reply = f"you Send : {data}"
            await manager.send_message(session_id, {
                "type": "conversation",
                "message": reply,
                "session_id": session_id
            })

                
    except WebSocketDisconnect:
        manager.disconnect(session_id)
    except Exception as e:
        logger.error(f"WebSocket error: {e}")
        manager.disconnect(session_id)


