"""Unified neural voice output pipeline for ARAXON."""

from __future__ import annotations

import asyncio
import time
from typing import TYPE_CHECKING

from araxon.core.config import settings
from araxon.core.logger import logger
from araxon.core.utils import chunk_text, sanitize_text

if TYPE_CHECKING:
    from araxon.wake.clap_detector import ClapDetector

from .audio_player import AudioPlayer
from .synthesizer import KokoroSynthesizer
from .voice_input import VoiceInputPipeline


class VoiceOutputPipeline:
    """Coordinate Kokoro synthesis and sequential audio playback."""

    def __init__(self, voice_input_pipeline: VoiceInputPipeline, clap_detector: "ClapDetector" | None = None, ui_bridge=None) -> None:
        """Initialize the voice output stack and bind the input pipeline."""
        self.voice_input_pipeline = voice_input_pipeline
        self.clap_detector = clap_detector
        self.synthesizer = KokoroSynthesizer()
        self.audio_player = AudioPlayer()
        self._is_speaking = False
        self._speak_lock = asyncio.Lock()
        self._playback_task: asyncio.Task | None = None
        self.ui_bridge = ui_bridge

    @property
    def is_speaking(self) -> bool:
        """Return whether ARAXON is currently speaking."""
        return self._is_speaking

    def _ensure_playback_task(self) -> None:
        """Start the background playback loop if it is not already running."""
        if self._playback_task is not None and not self._playback_task.done():
            return

        self._playback_task = asyncio.create_task(self.audio_player.start_playback_loop())

    def set_clap_detector(self, clap_detector: "ClapDetector" | None) -> None:
        """Attach or detach the clap detector used to mute self-triggered wake events."""
        self.clap_detector = clap_detector

    async def speak(self, text: str) -> None:
        """Mute the microphone, synthesize text, play it, and then unmute the microphone."""
        async with self._speak_lock:
            start_time = time.monotonic()
            self._is_speaking = True
            self.voice_input_pipeline.set_speaking(True)
            
            # STEP 11: Send speaking state to UI
            if self.ui_bridge:
                await self.ui_bridge.send_state("speaking")
            
            if self.clap_detector is not None:
                self.clap_detector.pause_clap_detection()

            try:
                sanitized_text = sanitize_text(text)
                if not sanitized_text:
                    logger.info("Voice output received empty text, nothing to speak.")
                    return

                chunks = chunk_text(sanitized_text, size=settings.TTS_CHUNK_SIZE)
                self.audio_player.begin_session(len(chunks))
                self._ensure_playback_task()

                for chunk in chunks:
                    audio = await self.synthesizer.synthesize(chunk)
                    if audio is None:
                        continue
                    if getattr(audio, "size", 0):
                        await self.audio_player.enqueue(audio)

                await self.audio_player.wait_until_idle()
                elapsed_seconds = time.monotonic() - start_time
                logger.info(f"Voice output completed in {elapsed_seconds:.2f}s.")
            finally:
                if self.clap_detector is not None:
                    self.clap_detector.resume_clap_detection()
                self.voice_input_pipeline.set_speaking(False)
                self._is_speaking = False
                
                # STEP 11: Send listening state to UI after speaking
                if self.ui_bridge:
                    await self.ui_bridge.send_state("listening")

    async def stop(self) -> None:
        """Stop playback immediately and restore microphone input."""
        try:
            await self.audio_player.stop()
        finally:
            if self.clap_detector is not None:
                self.clap_detector.resume_clap_detection()
            self.voice_input_pipeline.set_speaking(False)
            self._is_speaking = False

    # STEP 4: AI brain will call voice_output.speak(response)