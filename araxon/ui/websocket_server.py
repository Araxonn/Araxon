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
        self.command_handler = None

    def set_command_handler(self, handler) -> None:
        """Attach the UI command handler used for inbound messages."""
        self.command_handler = handler

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

        try:
            if msg_type == "ping":
                await self.broadcast({
                    "type": "pong",
                    "data": {
                        "status": "online",
                        "timestamp": datetime.now().isoformat()
                    }
                })
                return

            if self.command_handler is not None:
                await self.command_handler.handle(msg_type, msg_data)
                return

            logger.warning(f"No command handler registered for UI message: {msg_type}")

        except Exception as e:
            logger.error(f"Error handling UI message type {msg_type}: {e}")

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

    # ===== Helper methods for sending specific message types =====

    async def send_state(self, state: str):
        """Send current araxon state (listening, executing, code, thinking)."""
        await self.broadcast({
            "type": "state",
            "data": {"state": state}
        })

    async def send_transcript(self, role: str, text: str):
        """Send a transcript entry (user or araxon message)."""
        await self.broadcast({
            "type": "transcript",
            "data": {"role": role, "text": text, "timestamp": datetime.now().isoformat()}
        })

    async def send_waveform(self, levels: list):
        """Send waveform levels for audio visualization."""
        await self.broadcast({
            "type": "waveform",
            "data": levels[:40]  # Send up to 40 levels
        })

    async def send_system_stats(self, cpu: float, ram: float, gpu: float, net: float, disk: float, battery: float):
        """Send system statistics."""
        await self.broadcast({
            "type": "system_stats",
            "data": {
                "cpu": int(cpu),
                "ram": int(ram),
                "gpu": int(gpu),
                "net": int(net),
                "disk": int(disk),
                "battery": int(battery)
            }
        })

    async def send_agent_step(self, index: int, title: str, status: str, percent: int = 0, result: str = ""):
        """Send agent step update (done, running, pending)."""
        await self.broadcast({
            "type": "agent_step",
            "data": {
                "index": index,
                "title": title,
                "status": status,
                "percent": percent,
                "result": result
            }
        })

    async def send_code_update(self, name: str, content: str, language: str = "js"):
        """Send code file update."""
        await self.broadcast({
            "type": "code_update",
            "data": {
                "name": name,
                "content": content,
                "language": language
            }
        })

    async def send_code_suggestion(self, title: str, description: str):
        """Send a code suggestion."""
        await self.broadcast({
            "type": "code_suggestion",
            "data": {
                "title": title,
                "description": description
            }
        })

    async def send_system_info(self, info: Dict[str, Any]):
        """Send system information."""
        await self.broadcast({
            "type": "system_info",
            "data": info
        })

    async def send_notification(self, title: str, message: str, notif_type: str = "info"):
        """Send a notification to display."""
        await self.broadcast({
            "type": "notification",
            "data": {
                "title": title,
                "message": message,
                "type": notif_type
            }
        })

    async def send_log_line(self, level: str, message: str, module: str = "", timestamp: str = None):
        """Send a log line to the Logs tab."""
        if timestamp is None:
            timestamp = datetime.now().isoformat()
        await self.broadcast({
            "type": "log_line",
            "data": {
                "level": level,
                "message": message,
                "module": module,
                "timestamp": timestamp
            }
        })

    async def send_memory_stats(self, total: int, files: int, session_turns: int, recent: list = None):
        """Send memory statistics."""
        if recent is None:
            recent = []
        await self.broadcast({
            "type": "memory_stats",
            "data": {
                "total": total,
                "files": files,
                "session_turns": session_turns,
                "recent": recent
            }
        })
