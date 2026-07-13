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
    """Bridge to send UI events to the WebSocket server."""

    STATE_MAP = {
        "speaking": "executing",
        "processing": "executing",
        "active": "listening",
        "standby": "listening",
    }

    def __init__(self, websocket_server):
        self.websocket_server = websocket_server

    def _map_state(self, state: str) -> str:
        return self.STATE_MAP.get(state, state)

    def _format_timestamp(self) -> str:
        return datetime.now().strftime("%I:%M %p").lstrip("0")

    async def send_transcript(self, speaker: str, text: str):
        if not settings.UI_ENABLED:
            return

        role = "user" if speaker in {"user", "you"} else "assistant"
        try:
            await self.websocket_server.broadcast({
                "type": "transcript",
                "data": {
                    "role": role,
                    "text": text,
                    "timestamp": self._format_timestamp(),
                },
            })
        except Exception as e:
            logger.error(f"Error sending transcript to UI: {e}")

    async def send_state(self, state: str):
        if not settings.UI_ENABLED:
            return

        try:
            await self.websocket_server.broadcast({
                "type": "state",
                "data": {
                    "state": self._map_state(state),
                    "timestamp": datetime.now().isoformat(),
                },
            })
        except Exception as e:
            logger.error(f"Error sending state to UI: {e}")

    async def send_waveform(self, levels: List[float]):
        if not settings.UI_ENABLED:
            return

        try:
            normalized_levels = levels[:48]
            if len(normalized_levels) < 48:
                normalized_levels.extend([0.0] * (48 - len(normalized_levels)))

            await self.websocket_server.broadcast({
                "type": "waveform",
                "data": [
                    float(min(1.0, max(0.0, level)))
                    for level in normalized_levels
                ],
            })
        except Exception as e:
            logger.error(f"Error sending waveform to UI: {e}")

    async def send_system_stats(self, stats: Dict[str, Any]):
        if not settings.UI_ENABLED:
            return

        try:
            await self.websocket_server.broadcast({
                "type": "system_stats",
                "data": {
                    "cpu": round(float(stats.get("cpu", 0))),
                    "ram": round(float(stats.get("ram", 0))),
                    "gpu": round(float(stats.get("gpu", 0))),
                    "net": round(float(stats.get("net", 0)), 1),
                    "disk": round(float(stats.get("disk", 0))),
                    "battery": round(float(stats.get("battery", 100))),
                    "uptime": stats.get("uptime", ""),
                    "timestamp": datetime.now().isoformat(),
                },
            })
        except Exception as e:
            logger.error(f"Error sending system stats to UI: {e}")

    async def send_agent_step(self, step: Dict[str, Any]):
        if not settings.UI_ENABLED:
            return

        step_number = int(step.get("step_number", 0))
        status = step.get("status", "running")
        mapped_status = {
            "done": "done",
            "running": "running",
            "error": "pending",
            "pending": "pending",
        }.get(status, "running")

        try:
            await self.websocket_server.broadcast({
                "type": "agent_step",
                "data": {
                    "index": max(0, step_number - 1),
                    "title": step.get("description", f"Step {step_number}"),
                    "status": mapped_status,
                    "percent": 100 if mapped_status == "done" else step.get("percent", 75),
                    "result": step.get("result") or step.get("error_message") or "",
                },
            })
        except Exception as e:
            logger.error(f"Error sending agent step to UI: {e}")

    async def set_agent_steps(self, steps: List[Dict[str, Any]]):
        if not settings.UI_ENABLED:
            return

        mapped = []
        for step in steps:
            step_number = int(step.get("step_number", len(mapped) + 1))
            mapped.append({
                "index": step_number - 1,
                "title": step.get("description", f"Step {step_number}"),
                "status": "pending",
                "percent": 0,
                "result": "",
            })

        await self.websocket_server.broadcast({
            "type": "agent_steps",
            "data": mapped,
        })

    async def send_system_info(self, info: Dict[str, Any]):
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
        if not settings.UI_ENABLED:
            return

        try:
            await self.websocket_server.broadcast({
                "type": "notification",
                "data": {
                    "title": title,
                    "message": message,
                    "type": level,
                    "timestamp": datetime.now().isoformat(),
                },
            })
        except Exception as e:
            logger.error(f"Error sending notification to UI: {e}")

    async def send_log_line(self, level: str, message: str, module: str = ""):
        if not settings.UI_ENABLED:
            return

        try:
            await self.websocket_server.broadcast({
                "type": "log_line",
                "data": {
                    "level": level,
                    "message": message,
                    "module": module,
                    "timestamp": datetime.now().strftime("%H:%M:%S"),
                },
            })
        except Exception as e:
            logger.error(f"Error sending log line to UI: {e}")

    async def send_memory_stats(
        self,
        total: int,
        files: int,
        session_turns: int,
        recent: list | None = None,
    ):
        if not settings.UI_ENABLED:
            return

        try:
            await self.websocket_server.broadcast({
                "type": "memory_stats",
                "data": {
                    "total": total,
                    "files": files,
                    "session_turns": session_turns,
                    "recent": recent or [],
                },
            })
        except Exception as e:
            logger.error(f"Error sending memory stats to UI: {e}")

    async def send_code_update(self, name: str, content: str, language: str = "js"):
        if not settings.UI_ENABLED:
            return

        try:
            await self.websocket_server.broadcast({
                "type": "code_update",
                "data": {
                    "name": name,
                    "content": content,
                    "language": language,
                },
            })
        except Exception as e:
            logger.error(f"Error sending code update to UI: {e}")

    async def send_code_suggestion(self, title: str, description: str):
        if not settings.UI_ENABLED:
            return

        try:
            await self.websocket_server.broadcast({
                "type": "code_suggestion",
                "data": {
                    "title": title,
                    "description": description,
                },
            })
        except Exception as e:
            logger.error(f"Error sending code suggestion to UI: {e}")

    async def send_ingested_files(self, files: list[dict[str, Any]]):
        if not settings.UI_ENABLED:
            return

        try:
            await self.websocket_server.broadcast({
                "type": "ingested_files",
                "data": {"files": files},
            })
        except Exception as e:
            logger.error(f"Error sending ingested files to UI: {e}")

    async def send_automation_processes(self, processes: list[dict[str, Any]]):
        if not settings.UI_ENABLED:
            return

        try:
            await self.websocket_server.broadcast({
                "type": "automation_processes",
                "data": {"processes": processes},
            })
        except Exception as e:
            logger.error(f"Error sending automation processes to UI: {e}")

    async def send_execution_progress(self, percent: int):
        if not settings.UI_ENABLED:
            return

        try:
            await self.websocket_server.broadcast({
                "type": "execution_progress",
                "data": {"percent": max(0, min(100, int(percent)))},
            })
        except Exception as e:
            logger.error(f"Error sending execution progress to UI: {e}")
