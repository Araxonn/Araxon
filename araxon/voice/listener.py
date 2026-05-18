"""Microphone capture and voice activity detection for ARAXON."""

from __future__ import annotations

import asyncio
import inspect
import threading
from typing import Awaitable, Callable, Optional

try:
    import numpy as np
except ImportError:  # pragma: no cover - optional dependency fallback
    np = None  # type: ignore[assignment]

try:
    import sounddevice as sd
except ImportError:  # pragma: no cover - optional dependency fallback
    sd = None  # type: ignore[assignment]

try:
    import torch
except ImportError:  # pragma: no cover - optional dependency fallback
    torch = None  # type: ignore[assignment]

from araxon.core.config import settings
from araxon.core.logger import logger


class MicrophoneListener:
    """Capture microphone audio and segment it into speech utterances."""

    _vad_model = None
    _vad_lock = threading.Lock()

    def __init__(self) -> None:
        """Initialize the microphone listener and runtime state."""
        self.sample_rate = settings.SAMPLE_RATE
        self.vad_threshold = settings.VAD_THRESHOLD
        self.silence_duration = settings.SILENCE_DURATION
        self.min_speech_duration = settings.MIN_SPEECH_DURATION
        self.chunk_duration = settings.VOICE_CHUNK_DURATION
        self.chunk_frames = max(1, int(self.sample_rate * self.chunk_duration))
        self.is_speaking = False
        self._stop_event = threading.Event()

    @classmethod
    def _ensure_vad_model_sync(cls) -> bool:
        """Load the Silero VAD model once and cache it at the class level."""
        if cls._vad_model is not None:
            return True

        if torch is None:
            logger.error("Torch is not installed, so voice activity detection is unavailable.")
            return False

        with cls._vad_lock:
            if cls._vad_model is not None:
                return True

            logger.info("Loading Silero VAD model for microphone listener...")
            try:
                model, _utils = torch.hub.load(
                    repo_or_dir="snakers4/silero-vad",
                    model="silero_vad",
                    trust_repo=True,
                )
                model.eval()
                cls._vad_model = model
                logger.info("Silero VAD model loaded successfully.")
                return True
            except Exception as exc:
                logger.error(f"Failed to load Silero VAD model: {exc}")
                return False

    def _speech_probability_sync(self, audio_chunk) -> float:
        """Return the Silero VAD speech probability for a single chunk."""
        if self._vad_model is None or torch is None or np is None:
            return 0.0

        audio_tensor = torch.from_numpy(np.asarray(audio_chunk, dtype=np.float32)).flatten()
        with torch.no_grad():
            speech_probability = self._vad_model(audio_tensor, self.sample_rate).item()
        return float(speech_probability)

    def _listen_once_sync(self):
        """Synchronously capture one speech segment from the default microphone."""
        if np is None:
            logger.error("NumPy is not installed, so microphone capture cannot run.")
            return None

        if sd is None:
            logger.error("sounddevice is not installed, so microphone capture cannot run.")
            return None

        if not self._ensure_vad_model_sync():
            return None

        if self._stop_event.is_set():
            return None

        logger.info("Listening started.")
        audio_chunks = []
        speech_started = False
        silence_elapsed = 0.0
        chunk_seconds = self.chunk_frames / float(self.sample_rate)

        try:
            with sd.InputStream(
                samplerate=self.sample_rate,
                channels=1,
                dtype="float32",
                blocksize=self.chunk_frames,
            ) as stream:
                while not self._stop_event.is_set():
                    data, overflowed = stream.read(self.chunk_frames)
                    if overflowed:
                        logger.warning("Microphone buffer overflow detected.")

                    chunk = np.asarray(data, dtype=np.float32).reshape(-1)
                    if chunk.size == 0:
                        continue

                    if self.is_speaking:
                        speech_started = False
                        silence_elapsed = 0.0
                        audio_chunks.clear()
                        continue

                    speech_probability = self._speech_probability_sync(chunk)

                    if not speech_started:
                        if speech_probability >= self.vad_threshold:
                            speech_started = True
                            audio_chunks.append(chunk)
                            logger.info("Speech detected.")
                        continue

                    audio_chunks.append(chunk)

                    if speech_probability >= self.vad_threshold:
                        silence_elapsed = 0.0
                    else:
                        silence_elapsed += chunk_seconds
                        if silence_elapsed >= self.silence_duration:
                            logger.info("Speech ended.")
                            break
        except Exception as exc:
            message = str(exc).lower()
            if "input device" in message or "no default input device" in message or "error querying device -1" in message:
                logger.error("No microphone input device was found. Please connect or select a microphone and try again.")
            else:
                logger.error(f"Microphone capture failed: {exc}")
            return None

        if not speech_started:
            logger.info("Silence timeout reached without capturing speech.")
            return None

        audio = np.concatenate(audio_chunks).astype(np.float32) if audio_chunks else np.array([], dtype=np.float32)
        duration_seconds = len(audio) / float(self.sample_rate)

        if duration_seconds < self.min_speech_duration:
            logger.info(
                f"Ignored speech clip shorter than the minimum duration ({duration_seconds:.2f}s < {self.min_speech_duration:.2f}s)."
            )
            return None

        logger.info(f"Captured speech segment: {duration_seconds:.2f}s")
        return audio

    async def listen_once(self) -> Optional["np.ndarray"]:
        """Listen until one speech segment is captured and return it as an array."""
        return await asyncio.to_thread(self._listen_once_sync)

    async def start_continuous(
        self,
        callback: Callable[["np.ndarray"], Awaitable[None] | None],
    ) -> None:
        """Continuously capture utterances and forward each one to a callback."""
        logger.info("Continuous microphone listening started.")
        self._stop_event.clear()

        while not self._stop_event.is_set():
            audio = await self.listen_once()
            if self._stop_event.is_set():
                break
            if audio is None:
                continue

            try:
                result = callback(audio)
                if inspect.isawaitable(result):
                    await result
            except Exception as exc:
                logger.error(f"Microphone callback failed: {exc}")

        logger.info("Continuous microphone listening stopped.")

    def stop(self) -> None:
        """Request a safe shutdown of the microphone listener."""
        self._stop_event.set()
        logger.info("Microphone listener stop requested.")