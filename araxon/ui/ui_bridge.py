"""
UI Bridge for sending system events to the ARAXON frontend via WebSocket.

This module provides a singleton interface for all ARAXON subsystems
to communicate with the frontend UI without blocking operations.
"""

import asyncio
from datetime import datetime
from typing import Optional, List, Dict, Any
from loguru import logger

from araxon.core.config import settings


class UIBridge:
    """
    Bridge to send UI events to the WebSocket server.
    
    All methods are non-blocking async. Messages are queued and sent
    via WebSocket without blocking the main pipeline.
    
    Usage:
        ui_bridge = UIBridge(websocket_server)
        await ui_bridge.send_transcript("user", "hello araxon")
        await ui_bridge.send_state("listening")
    """

    def __init__(self, websocket_server):
        """
        Initialize the UI bridge.
        
        Args:
            websocket_server: ARAxonWebSocketServer instance
        """
        self.websocket_server = websocket_server

    async def send_transcript(self, speaker: str, text: str):
        """
        Send a transcript message to the UI.
        
        Args:
            speaker: "user" or "araxon"
            text: The spoken/transcribed text
        """
        if not settings.UI_ENABLED:
            return

        try:
            await self.websocket_server.broadcast({
                "type": "transcript",
                "data": {
                    "speaker": speaker,
                    "text": text,
                    "timestamp": datetime.now().isoformat(),
                },
            })
        except Exception as e:
            logger.error(f"Error sending transcript to UI: {e}")

    async def send_state(self, state: str):
        """
        Send system state update to the UI.
        
        Valid states:
        - "listening": Waiting for user input
        - "thinking": Processing the request
        - "speaking": Speaking response
        - "standby": In sleep mode
        - "active": Active and ready
        - "processing": Performing agent task
        
        Args:
            state: The current state label
        """
        if not settings.UI_ENABLED:
            return

        try:
            await self.websocket_server.broadcast({
                "type": "state",
                "data": {
                    "state": state,
                    "timestamp": datetime.now().isoformat(),
                },
            })
        except Exception as e:
            logger.error(f"Error sending state to UI: {e}")

    async def send_waveform(self, levels: List[float]):
        """
        Send audio waveform levels to the UI.
        
        Args:
            levels: List of 32 float values (0.0-1.0) representing audio levels
        """
        if not settings.UI_ENABLED:
            return

        try:
            # Ensure exactly 32 levels, normalize to 0.0-1.0
            normalized_levels = levels[:32]
            if len(normalized_levels) < 32:
                normalized_levels.extend([0.0] * (32 - len(normalized_levels)))

            await self.websocket_server.broadcast({
                "type": "waveform",
                "data": {
                    "levels": [float(min(1.0, max(0.0, level))) for level in normalized_levels],
                    "timestamp": datetime.now().isoformat(),
                },
            })
        except Exception as e:
            logger.error(f"Error sending waveform to UI: {e}")

    async def send_system_stats(self, stats: Dict[str, Any]):
        """
        Send system statistics to the UI.
        
        Args:
            stats: Dict with keys: cpu, ram, gpu, net, disk, battery
                   Values should be floats 0.0-100.0 (or appropriate units)
        """
        if not settings.UI_ENABLED:
            return

        try:
            await self.websocket_server.broadcast({
                "type": "system_stats",
                "data": {
                    "cpu": stats.get("cpu", 0),
                    "ram": stats.get("ram", 0),
                    "gpu": stats.get("gpu", 0),
                    "net": stats.get("net", 0),
                    "disk": stats.get("disk", 0),
                    "battery": stats.get("battery", 0),
                    "timestamp": datetime.now().isoformat(),
                },
            })
        except Exception as e:
            logger.error(f"Error sending system stats to UI: {e}")

    async def send_agent_step(self, step: Dict[str, Any]):
        """
        Send an agent execution step update to the UI.
        
        Args:
            step: Dict with keys:
                - step_number: int (1-based)
                - description: str (what the step does)
                - status: "running" | "done" | "error"
                - done: bool (True if step completed)
                - error_message: str (optional, if status=="error")
        """
        if not settings.UI_ENABLED:
            return

        try:
            await self.websocket_server.broadcast({
                "type": "agent_step",
                "data": {
                    "step_number": step.get("step_number", 0),
                    "description": step.get("description", ""),
                    "status": step.get("status", "running"),
                    "done": step.get("done", False),
                    "error_message": step.get("error_message"),
                    "timestamp": datetime.now().isoformat(),
                },
            })
        except Exception as e:
            logger.error(f"Error sending agent step to UI: {e}")

    async def send_system_info(self, info: Dict[str, Any]):
        """
        Send system information to the UI.
        
        Args:
            info: Dict with system information (uptime, os, version, etc.)
        """
        if not settings.UI_ENABLED:
            return

        try:
            await self.websocket_server.broadcast({
                "type": "system_info",
                "data": info,
            })
        except Exception as e:
            logger.error(f"Error sending system info to UI: {e}")

    async def send_notification(self, title: str, message: str, level: str = "info"):
        """
        Send a notification to the UI.
        
        Args:
            title: Notification title
            message: Notification message
            level: "info" | "success" | "warning" | "error"
        """
        if not settings.UI_ENABLED:
            return

        try:
            await self.websocket_server.broadcast({
                "type": "notification",
                "data": {
                    "title": title,
                    "message": message,
                    "level": level,
                    "timestamp": datetime.now().isoformat(),
                },
            })
        except Exception as e:
            logger.error(f"Error sending notification to UI: {e}")
