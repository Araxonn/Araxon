"""Queued audio playback for ARAXON."""

from __future__ import annotations

import asyncio
import threading
from typing import Optional

try:
    import numpy as np
except ImportError:  # pragma: no cover - optional dependency fallback
    np = None  # type: ignore[assignment]

try:
    import sounddevice as sd
except ImportError:  # pragma: no cover - optional dependency fallback
    sd = None  # type: ignore[assignment]

from araxon.core.config import settings
from araxon.core.logger import logger


class AudioPlayer:
    """Play queued NumPy audio buffers sequentially without blocking the event loop."""

    def __init__(self) -> None:
        """Initialize the playback queue and runtime state."""
        self.sample_rate = settings.TTS_SAMPLE_RATE
        self._queue: asyncio.Queue = asyncio.Queue()
        self._stop_event = asyncio.Event()
        self._is_playing = False
        self._playback_task: Optional[asyncio.Task] = None
        self._chunk_counter = 0
        self._played_chunks = 0
        self._expected_total_chunks = 0
        self._state_lock = threading.Lock()

    @property
    def is_playing(self) -> bool:
        """Return whether audio is actively playing right now."""
        return self._is_playing

    def begin_session(self, total_chunks: int) -> None:
        """Reset playback counters for a new speaking session."""
        with self._state_lock:
            self._chunk_counter = 0
            self._played_chunks = 0
            self._expected_total_chunks = max(0, int(total_chunks))

    def _normalize_audio(self, audio):
        """Convert incoming audio to a one-dimensional float32 NumPy array."""
        if np is None:
            return None

        audio_array = np.asarray(audio, dtype=np.float32).reshape(-1)
        if audio_array.size == 0:
            return None
        return audio_array

    async def enqueue(self, audio):
        """Add an audio buffer to the playback queue."""
        audio_array = self._normalize_audio(audio)
        if audio_array is None:
            logger.info("Skipping empty audio chunk.")
            return

        with self._state_lock:
            self._chunk_counter += 1

        await self._queue.put(audio_array)

    def _play_audio_sync(self, audio_array) -> None:
        """Play a single audio buffer synchronously using sounddevice."""
        if sd is None:
            logger.error("sounddevice is not installed, so audio playback is unavailable.")
            return

        sd.play(audio_array, samplerate=self.sample_rate)
        sd.wait()

    async def start_playback_loop(self) -> None:
        """Run the background playback loop until stop is requested."""
        if self._playback_task is not None and not self._playback_task.done():
            if self._playback_task is not asyncio.current_task():
                logger.info("Audio playback loop is already running.")
                return

        self._playback_task = asyncio.current_task()
        logger.info("Audio playback loop started.")

        try:
            while not self._stop_event.is_set():
                try:
                    audio_array = await asyncio.wait_for(self._queue.get(), timeout=0.25)
                except asyncio.TimeoutError:
                    continue

                if audio_array is None:
                    self._queue.task_done()
                    break

                try:
                    with self._state_lock:
                        self._played_chunks += 1
                        played_index = self._played_chunks
                        total_chunks = self._expected_total_chunks or self._chunk_counter
                    duration_seconds = len(audio_array) / float(self.sample_rate)
                    self._is_playing = True
                    logger.info(
                        f"Playing chunk {max(1, played_index)} of {max(1, total_chunks)} ({duration_seconds:.2f}s)."
                    )
                    await asyncio.to_thread(self._play_audio_sync, audio_array)
                except Exception as exc:
                    logger.error(f"Audio playback failed: {exc}")
                finally:
                    self._is_playing = False
                    self._queue.task_done()

                if self._stop_event.is_set():
                    break
        finally:
            self._is_playing = False
            logger.info("Audio playback loop stopped.")

    async def wait_until_idle(self) -> None:
        """Wait until all queued audio chunks have finished playing."""
        await self._queue.join()

    async def stop(self) -> None:
        """Stop playback, clear the queue, and shut down the background loop."""
        self._stop_event.set()

        while True:
            try:
                self._queue.get_nowait()
            except asyncio.QueueEmpty:
                break
            else:
                self._queue.task_done()

        if sd is not None:
            try:
                await asyncio.to_thread(sd.stop)
            except Exception as exc:
                logger.error(f"Failed to stop audio playback cleanly: {exc}")

        current_task = asyncio.current_task()
        if self._playback_task is not None and not self._playback_task.done():
            if self._playback_task is not current_task:
                self._playback_task.cancel()
                try:
                    await self._playback_task
                except asyncio.CancelledError:
                    pass
                except Exception as exc:
                    logger.error(f"Audio playback loop shutdown failed: {exc}")

        self._playback_task = None
        self._is_playing = False
        logger.info("Audio player stopped.")