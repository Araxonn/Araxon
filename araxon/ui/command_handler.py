"""Handle inbound WebSocket messages from the ARAXON UI."""

from __future__ import annotations

import asyncio
import platform
import sys
import tempfile
from datetime import datetime
from pathlib import Path
from typing import Any, Optional

from araxon.core.config import settings
from araxon.core.logger import logger


class UICommandHandler:
    """Route UI WebSocket messages into ARAXON subsystems."""

    MODE_MAP = {
        "observe mode": ("standby", "Observe Mode"),
        "assist mode": ("listening", "Assist Mode"),
        "execute mode": ("executing", "Execute Mode"),
        "autonomous mode": ("executing", "Autonomous Mode"),
        "code mode": ("code", "Code Mode"),
    }

    ROUTINE_MAP = {
        "morning": "morning",
        "morning routine": "morning",
        "coding": "coding",
        "coding setup": "coding",
        "study": "study",
        "study mode": "study",
        "gaming": "gaming",
        "gaming mode": "gaming",
    }

    def __init__(
        self,
        wake_orchestrator,
        long_term_memory,
        file_ingester,
        brain,
        voice_input,
        voice_output,
        ui_bridge,
        automation_router=None,
        agent_controller=None,
    ) -> None:
        self.wake_orchestrator = wake_orchestrator
        self.long_term_memory = long_term_memory
        self.file_ingester = file_ingester
        self.brain = brain
        self.voice_input = voice_input
        self.voice_output = voice_output
        self.ui_bridge = ui_bridge
        self.automation_router = automation_router
        self.agent_controller = agent_controller
        self._lock = asyncio.Lock()
        self.active_ui_mode = "Assist Mode"

    async def handle(self, msg_type: str, msg_data: dict[str, Any]) -> None:
        """Dispatch a UI message to the appropriate handler."""
        handlers = {
            "command": self._handle_command,
            "routine": self._handle_routine,
            "ingest_file": self._handle_ingest_file,
            "mic_toggle": self._handle_mic_toggle,
            "voice_toggle": self._handle_voice_toggle,
            "settings_update": self._handle_settings_update,
            "nav_change": self._handle_nav_change,
        }
        handler = handlers.get(msg_type)
        if handler is None:
            logger.warning(f"Unknown UI message type: {msg_type}")
            return

        asyncio.create_task(self._run_safe(handler, msg_data))

    async def _run_safe(self, handler, msg_data: dict[str, Any]) -> None:
        async with self._lock:
            try:
                await handler(msg_data)
            except Exception as exc:
                logger.error(f"UI handler error: {exc}")
                await self.ui_bridge.send_notification(
                    "Command Failed",
                    str(exc),
                    "error",
                )

    async def _handle_command(self, msg_data: dict[str, Any]) -> None:
        text = str(msg_data.get("text", "")).strip()
        if not text:
            return

        normalized = text.lower()

        if normalized.endswith(" mode"):
            await self._handle_mode(normalized)
            return

        if self.wake_orchestrator.is_standby:
            self.wake_orchestrator.standby_manager.activate()
            await self.ui_bridge.send_state("listening")

        if await self.wake_orchestrator.process_transcription(text):
            return

        if "remember that" in normalized or "don't forget" in normalized:
            await self.ui_bridge.send_transcript("user", text)
            await self.long_term_memory.remember_fact(text)
            await self._respond("Got it, I'll remember that.")
            await self._broadcast_memory_stats()
            return

        if (
            "what do you remember" in normalized
            or normalized == "recall"
            or normalized.startswith("recall ")
        ):
            await self.ui_bridge.send_transcript("user", text)
            recall_text = await self.long_term_memory.recall(text)
            await self._respond(recall_text or "I couldn't find anything relevant.")
            await self._broadcast_memory_stats()
            return

        if "ingest my files" in normalized:
            await self.ui_bridge.send_transcript("user", text)
            results = await self.file_ingester.ingest_folder()
            files_count = len(results)
            total_chunks = sum(results.values())
            await self._respond(
                f"I ingested {files_count} file(s) and stored {total_chunks} chunk(s)."
            )
            await self._broadcast_memory_stats()
            await self._broadcast_ingested_files()
            return

        if normalized in {"clear memory", "clear all memories"}:
            await self.ui_bridge.send_transcript("user", text)
            await self.long_term_memory.clear_all(confirmed=True)
            await self.brain.reset()
            await self._respond("All memories cleared.")
            await self._broadcast_memory_stats()
            return

        if normalized.startswith("run "):
            await self.ui_bridge.send_transcript("user", text)
            await self._run_terminal_command(text[4:].strip())
            return

        if normalized.startswith("list ingested files"):
            await self._broadcast_ingested_files()
            return

        if normalized.startswith("create routine:"):
            await self.ui_bridge.send_transcript("user", text)
            await self._handle_create_routine(text)
            return

        await self._run_conversation(text)

    async def _handle_routine(self, msg_data: dict[str, Any]) -> None:
        name = str(msg_data.get("name", "")).strip().lower()
        routine = self.ROUTINE_MAP.get(name, name.replace(" routine", "").strip())
        await self._run_conversation(f"launch {routine} workspace")

    async def _handle_ingest_file(self, msg_data: dict[str, Any]) -> None:
        content = str(msg_data.get("content", ""))
        name = str(msg_data.get("name", "upload.txt"))
        if not content.strip():
            await self.ui_bridge.send_notification(
                "File Ingestion",
                "File was empty.",
                "warning",
            )
            return

        suffix = Path(name).suffix.lower() or ".txt"
        with tempfile.NamedTemporaryFile(
            mode="w",
            encoding="utf-8",
            suffix=suffix,
            delete=False,
        ) as tmp:
            tmp.write(content)
            tmp_path = tmp.name

        try:
            chunks = await self.file_ingester.ingest_file(tmp_path)
            if suffix in {".jsx", ".tsx", ".js", ".ts", ".py"}:
                await self.ui_bridge.send_code_update(
                    name,
                    content,
                    suffix.lstrip("."),
                )
            await self.ui_bridge.send_notification(
                "File Ingested",
                f"{name}: {chunks} chunk(s) stored.",
                "success",
            )
            await self._broadcast_memory_stats()
            await self._broadcast_ingested_files()
        finally:
            Path(tmp_path).unlink(missing_ok=True)

    async def _handle_mic_toggle(self, msg_data: dict[str, Any]) -> None:
        enabled = bool(msg_data.get("enabled", True))
        self.voice_input.set_mic_enabled(enabled)
        await self.ui_bridge.send_notification(
            "Microphone",
            f"Microphone {'enabled' if enabled else 'disabled'}.",
            "info",
        )

    async def _handle_voice_toggle(self, msg_data: dict[str, Any]) -> None:
        enabled = bool(msg_data.get("enabled", True))
        self.voice_output.set_voice_enabled(enabled)
        await self.ui_bridge.send_notification(
            "Voice Output",
            f"Voice output {'enabled' if enabled else 'disabled'}.",
            "info",
        )

    async def _handle_settings_update(self, msg_data: dict[str, Any]) -> None:
        mapping = {
            "whisper_model": "WHISPER_MODEL",
            "tts_voice": "TTS_VOICE",
            "tts_speed": "TTS_SPEED",
            "preferred_backend": "PREFERRED_BACKEND",
            "temperature": "TEMPERATURE",
            "max_tokens": "MAX_TOKENS",
            "wake_word": "WAKE_WORD",
            "auto_sleep_timeout": "AUTO_SLEEP_TIMEOUT",
            "wake_confirmation_phrase": "WAKE_CONFIRMATION_PHRASE",
            "agent_mode": "AGENT_MODE",
            "max_steps": "AGENT_MAX_STEPS",
            "narrate_steps": "AGENT_NARRATE_STEPS",
            "step_delay": "AGENT_STEP_DELAY_SECONDS",
        }

        for key, attr in mapping.items():
            if key in msg_data and hasattr(settings, attr):
                setattr(settings, attr, msg_data[key])

        if "groq_api_key" in msg_data and msg_data["groq_api_key"]:
            settings.GROQ_API_KEY = msg_data["groq_api_key"]

        if "ollama_url" in msg_data and msg_data["ollama_url"]:
            settings.OLLAMA_BASE_URL = msg_data["ollama_url"]

        await self.ui_bridge.send_notification(
            "Settings Updated",
            "Configuration applied for this session.",
            "success",
        )
        await self.ui_bridge.send_system_info(await self.build_system_info())

    async def _handle_nav_change(self, msg_data: dict[str, Any]) -> None:
        nav = str(msg_data.get("nav", "")).strip().lower()
        if nav == "memory":
            await self._broadcast_memory_stats()
        elif nav == "files":
            await self._broadcast_ingested_files()
        elif nav == "automation":
            await self._broadcast_automation_processes()
        elif nav in {"agents", "terminal"}:
            await self.ui_bridge.send_log_line(
                "INFO",
                f"Navigation: {nav}",
                "ui",
            )

    async def _handle_create_routine(self, text: str) -> None:
        import json

        payload = text.split(":", 1)[1].strip()
        try:
            routine = json.loads(payload)
        except json.JSONDecodeError:
            await self._respond("I couldn't parse that routine definition.")
            return

        name = routine.get("name", "Custom Routine")
        steps = routine.get("steps", [])
        if not steps:
            await self._respond("That routine has no steps.")
            return

        await self.ui_bridge.send_state("executing")
        await self.ui_bridge.send_transcript("assistant", f"Running routine: {name}")

        for step in steps:
            step_type = step.get("type", "open_app")
            step_text = str(step.get("text", "")).strip()
            if not step_text:
                continue

            if step_type == "open_app":
                command = f"open {step_text}"
            elif step_type == "open_website":
                command = f"open {step_text}"
            elif step_type == "run_command":
                command = f"run {step_text}"
            elif step_type == "speak":
                await self._respond(step_text)
                continue
            else:
                command = step_text

            if self.automation_router is not None:
                result = await self.automation_router.route(command)
                if result:
                    await self.ui_bridge.send_transcript("assistant", result)

        await self._respond(f"Routine '{name}' completed.")
        await self.ui_bridge.send_state("listening")

    async def _handle_mode(self, mode_text: str) -> None:
        state, label = self.MODE_MAP.get(mode_text, ("listening", "Assist Mode"))
        self.active_ui_mode = label

        if mode_text == "observe mode":
            self.wake_orchestrator.standby_manager.sleep("observe mode")
            await self.ui_bridge.send_state("standby")
            await self._respond("Observe mode enabled. I'm watching quietly.")
            return

        self.wake_orchestrator.standby_manager.activate()

        if mode_text == "execute mode":
            settings.AGENT_MODE = "plan"
        elif mode_text == "autonomous mode":
            settings.AGENT_MODE = "auto"
        elif mode_text == "code mode":
            settings.AGENT_MODE = "graph"
            await self.ui_bridge.send_state("code")
            await self._respond("Code mode active. Share a file or ask about your code.")
            return

        await self.ui_bridge.send_state(state)
        await self._respond(f"{label} activated.")

    async def _run_conversation(self, text: str) -> None:
        await self.ui_bridge.send_state("executing")
        try:
            if (
                self.active_ui_mode in {"Execute Mode", "Autonomous Mode"}
                and self.agent_controller is not None
            ):
                await self.ui_bridge.send_transcript("user", text)
                await self.agent_controller.run(text)
                return

            await self.wake_orchestrator.run_conversation_turn(text)
        finally:
            if self.active_ui_mode == "Code Mode":
                await self.ui_bridge.send_state("code")
            elif not self.wake_orchestrator.is_standby:
                await self.ui_bridge.send_state("listening")

    async def _run_terminal_command(self, command: str) -> None:
        if not command:
            return

        await self.ui_bridge.send_log_line("INFO", f"$ {command}", "terminal")
        await self.ui_bridge.send_state("executing")

        try:
            from araxon.agent.tools import run_terminal_command

            result = await run_terminal_command(command)
            await self.ui_bridge.send_log_line("SUCCESS", str(result), "terminal")
            await self.ui_bridge.send_transcript("assistant", str(result))
            if self.voice_output.voice_enabled:
                await self.voice_output.speak(str(result)[:500])
        except Exception as exc:
            await self.ui_bridge.send_log_line("ERROR", str(exc), "terminal")
            await self.ui_bridge.send_notification("Terminal Error", str(exc), "error")
        finally:
            await self.ui_bridge.send_state("listening")

    async def _respond(self, text: str) -> None:
        await self.ui_bridge.send_transcript("assistant", text)
        if self.voice_output.voice_enabled:
            await self.voice_output.speak(text)

    async def build_system_info(self) -> dict[str, Any]:
        return {
            "app_name": settings.APP_NAME,
            "version": "0.1.0",
            "python": sys.version.split()[0],
            "platform": platform.platform(),
            "agent_mode": settings.AGENT_MODE,
            "wake_word": settings.WAKE_WORD,
            "ui_mode": self.active_ui_mode,
        }

    async def _broadcast_memory_stats(self) -> None:
        stats = await self.long_term_memory.vector_store.get_collection_stats()
        recent = await self._get_recent_memories()
        session_turns = len(getattr(self.brain.memory, "_history", [])) // 2

        await self.ui_bridge.send_memory_stats(
            total=stats.get("conversations_count", 0),
            files=stats.get("files_count", 0),
            session_turns=session_turns,
            recent=recent,
        )

    async def _get_recent_memories(self, limit: int = 8) -> list[dict[str, Any]]:
        store = self.long_term_memory.vector_store
        collection = store._conversations
        if collection is None:
            return []

        try:
            payload = await asyncio.to_thread(
                collection.get,
                include=["documents", "metadatas"],
            )
            documents = payload.get("documents") or []
            metadatas = payload.get("metadatas") or []
            items = []

            for doc, meta in zip(documents, metadatas):
                if not doc:
                    continue
                items.append(
                    {
                        "title": (meta or {}).get("topic", "Memory"),
                        "content": doc[:240],
                        "timestamp": (meta or {}).get("timestamp", ""),
                    }
                )

            items.sort(key=lambda item: item.get("timestamp", ""), reverse=True)
            return items[:limit]
        except Exception as exc:
            logger.warning(f"Failed to fetch recent memories: {exc}")
            return []

    async def _broadcast_ingested_files(self) -> None:
        filenames = await self.file_ingester.list_ingested_files()
        files = [
            {
                "name": name,
                "size": 0,
                "date": datetime.now().isoformat(),
            }
            for name in filenames
        ]
        await self.ui_bridge.send_ingested_files(files)

    async def _broadcast_automation_processes(self) -> None:
        import psutil

        processes = []
        for proc in psutil.process_iter(["pid", "name", "cpu_percent", "memory_percent"]):
            try:
                info = proc.info
                cpu = info.get("cpu_percent") or 0
                memory = info.get("memory_percent") or 0
                if cpu < 0.5 and memory < 0.5:
                    continue
                processes.append(
                    {
                        "pid": info.get("pid"),
                        "name": info.get("name", "unknown"),
                        "cpu": round(cpu, 1),
                        "memory": round(memory, 1),
                    }
                )
            except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess):
                continue

        processes.sort(key=lambda item: item.get("cpu", 0), reverse=True)
        await self.ui_bridge.send_automation_processes(processes[:15])

    async def broadcast_initial_state(self) -> None:
        await self.ui_bridge.send_state("listening")
        await self.ui_bridge.send_system_info(await self.build_system_info())
        await self._broadcast_memory_stats()
        await self._broadcast_ingested_files()
