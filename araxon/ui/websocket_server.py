"""
WebSocket server for real-time UI communication with ARAXON frontend.

STEP 11: This module handles WebSocket connections from the Tauri/React UI,
broadcasting system state, transcripts, waveforms, and agent steps in real-time.
"""

import asyncio
import json
from datetime import datetime
from typing import Set, Dict, Any, Optional
import websockets
from websockets.server import WebSocketServerProtocol
from loguru import logger

from araxon.core.config import settings


class ARAxonWebSocketServer:
    """
    WebSocket server for ARAXON UI communication.
    
    Maintains connections from Tauri frontend and broadcasts:
    - Transcript messages
    - System state changes
    - Audio waveforms
    - System statistics
    - Agent execution steps
    - System information
    - Notifications
    """

    def __init__(self):
        """Initialize the WebSocket server."""
        self.host = settings.UI_WEBSOCKET_HOST
        self.port = settings.UI_WEBSOCKET_PORT
        self.connected_clients: Set[WebSocketServerProtocol] = set()
        self.server: Optional[Any] = None
        self.running = False

    async def start(self):
        """Start the WebSocket server as a background task."""
        if not settings.UI_ENABLED:
            logger.info("UI system disabled in config")
            return

        try:
            self.server = await websockets.serve(
                self._handle_client,
                self.host,
                self.port,
                ping_interval=20,
                ping_timeout=20,
            )
            self.running = True
            logger.info(
                f"UI WebSocket server started at ws://{self.host}:{self.port}"
            )
        except Exception as e:
            logger.error(f"Failed to start WebSocket server: {e}")
            raise

    async def stop(self):
        """Stop the WebSocket server."""
        self.running = False
        if self.server:
            self.server.close()
            await self.server.wait_closed()
            logger.info("UI WebSocket server stopped")

    async def _handle_client(self, websocket: WebSocketServerProtocol, path: str):
        """
        Handle a new WebSocket client connection.
        
        Args:
            websocket: The WebSocket connection
            path: The connection path (unused)
        """
        self.connected_clients.add(websocket)
        client_ip = websocket.remote_address[0] if websocket.remote_address else "unknown"
        logger.info(f"UI client connected from {client_ip}. Total: {len(self.connected_clients)}")

        try:
            # Send initial connection confirmation
            await websocket.send(
                json.dumps({
                    "type": "connection",
                    "data": {"status": "connected", "timestamp": datetime.now().isoformat()},
                })
            )

            # Handle incoming messages from the frontend
            async for message in websocket:
                try:
                    data = json.loads(message)
                    await self._handle_message(data)
                except json.JSONDecodeError:
                    logger.warning(f"Invalid JSON from UI client: {message}")
                except Exception as e:
                    logger.error(f"Error handling UI message: {e}")

        except websockets.exceptions.ConnectionClosed:
            logger.info(f"UI client disconnected from {client_ip}")
        except Exception as e:
            logger.error(f"WebSocket client error: {e}")
        finally:
            self.connected_clients.discard(websocket)
            logger.info(f"Client removed. Total: {len(self.connected_clients)}")

    async def _handle_message(self, data: Dict[str, Any]):
        """
        Handle incoming messages from UI clients.
        
        Args:
            data: The message data {type, data, ...}
        """
        msg_type = data.get("type")
        msg_data = data.get("data", {})

        if msg_type == "command":
            # Frontend sends a text command
            logger.info(f"UI command received: {msg_data.get('text')}")
            # Will be handled by main.py's voice_input_pipeline
            # message queued for processing

        elif msg_type == "routine":
            # Frontend requests a routine launch
            routine_name = msg_data.get("name")
            logger.info(f"UI routine requested: {routine_name}")

        elif msg_type == "settings_update":
            # Frontend updates settings
            setting_name = msg_data.get("name")
            setting_value = msg_data.get("value")
            logger.info(f"UI settings update: {setting_name} = {setting_value}")

        elif msg_type == "nav_change":
            # Frontend navigation changed (for logging)
            nav_section = msg_data.get("section")
            logger.info(f"UI navigation: {nav_section}")

        elif msg_type == "ping":
            # Frontend ping request
            await self._send_to_client(
                websocket=None,  # Will broadcast
                message={"type": "pong", "data": {"status": "online", "timestamp": datetime.now().isoformat()}},
            )

    async def broadcast(self, message: Dict[str, Any]):
        """
        Broadcast a message to all connected UI clients.
        
        Args:
            message: The message dict with {type, data, timestamp}
        """
        if not self.connected_clients:
            return

        # Ensure timestamp is present
        if "timestamp" not in message:
            message["timestamp"] = datetime.now().isoformat()

        payload = json.dumps(message)
        disconnected = set()

        for client in self.connected_clients:
            try:
                await client.send(payload)
            except websockets.exceptions.ConnectionClosed:
                disconnected.add(client)
            except Exception as e:
                logger.error(f"Error broadcasting to client: {e}")
                disconnected.add(client)

        # Clean up disconnected clients
        self.connected_clients -= disconnected

    async def _send_to_client(self, websocket: Optional[WebSocketServerProtocol], message: Dict[str, Any]):
        """
        Send a message to a specific client or broadcast if websocket is None.
        
        Args:
            websocket: The client websocket (None = broadcast to all)
            message: The message dict
        """
        if websocket is None:
            await self.broadcast(message)
        else:
            try:
                await websocket.send(json.dumps(message))
            except Exception as e:
                logger.error(f"Error sending to client: {e}")
