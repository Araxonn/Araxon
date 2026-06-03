"""Unified voice input pipeline for ARAXON."""

from __future__ import annotations

import inspect
import threading
from typing import Awaitable, Callable

from araxon.core.logger import logger

from .listener import MicrophoneListener
from .transcriber import WhisperTranscriber


class VoiceInputPipeline:
    """Combine microphone listening and Whisper transcription into one pipeline."""

    def __init__(self, ui_bridge=None) -> None:
        """Initialize the microphone listener, transcriber, and pipeline state."""
        self.listener = MicrophoneListener()
        self.transcriber = WhisperTranscriber()
        self.is_speaking = False
        self._stop_event = threading.Event()
        self.ui_bridge = ui_bridge

    def set_speaking(self, value: bool) -> None:
        """Toggle the anti-self-hearing flag from outside the pipeline."""
        self.is_speaking = bool(value)
        self.listener.is_speaking = self.is_speaking
        logger.info(f"Voice pipeline speaking flag set to {self.is_speaking}.")

    async def listen_and_transcribe(self) -> str:
        """Listen for one speech segment and return its cleaned transcription."""
        if self.is_speaking:
            logger.info("Voice pipeline is muted because ARAXON is currently speaking.")
            return ""

        audio = await self.listener.listen_once()
        if audio is None:
            logger.info("No audible speech segment was captured.")
            return ""

        text = await self.transcriber.transcribe(audio)
        logger.info(f"Voice input pipeline result: {text or '[no transcription]'}")
        return text

    async def start(self, callback: Callable[[str], Awaitable[None] | None]) -> None:
        """Continuously listen, transcribe, and forward each result to a callback."""
        logger.info("Voice input pipeline continuous mode started.")
        self._stop_event.clear()

        while not self._stop_event.is_set():
            text = await self.listen_and_transcribe()
            if self._stop_event.is_set():
                break
            if not text:
                continue

            try:
                result = callback(text)
                if inspect.isawaitable(result):
                    await result
            except Exception as exc:
                logger.error(f"Voice input callback failed: {exc}")

        logger.info("Voice input pipeline continuous mode stopped.")

    def stop(self) -> None:
        """Stop voice capture and release cached transcription resources."""
        self._stop_event.set()
        self.listener.stop()
        self.transcriber.shutdown()
        logger.info("Voice input pipeline stopped.")