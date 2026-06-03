"""Kokoro text-to-speech synthesis for ARAXON."""

from __future__ import annotations

import asyncio
import threading
import time
import wave
from pathlib import Path
from typing import Optional

try:
    import numpy as np
except ImportError:  # pragma: no cover - optional dependency fallback
    np = None  # type: ignore[assignment]

try:
    import soundfile as sf
except ImportError:  # pragma: no cover - optional dependency fallback
    sf = None  # type: ignore[assignment]

try:
    from kokoro import KPipeline
except ImportError:  # pragma: no cover - optional dependency fallback
    KPipeline = None  # type: ignore[assignment]

from araxon.core.config import settings
from araxon.core.logger import logger
from araxon.core.utils import chunk_text, sanitize_text


class KokoroSynthesizer:
    """Synthesize speech audio with a cached Kokoro pipeline."""

    _pipeline = None
    _pipeline_lock = threading.Lock()
    _pipeline_signature: Optional[tuple[str, str, float, int]] = None

    # Available voices: af_heart, af_bella, af_sarah, am_adam, am_michael
    # bf_emma, bf_isabella, bm_george, bm_lewis

    def __init__(self) -> None:
        """Initialize the synthesizer and load the cached Kokoro pipeline."""
        self.voice = settings.TTS_VOICE
        self.speed = settings.TTS_SPEED
        self.sample_rate = settings.TTS_SAMPLE_RATE
        self.chunk_size = settings.TTS_CHUNK_SIZE
        self._lang_code = self.voice[:1].lower() if self.voice else "a"
        self._ensure_pipeline_sync()

    @classmethod
    def _ensure_pipeline_sync(cls):
        """Load the Kokoro pipeline once and reuse it for the process lifetime."""
        if cls._pipeline is not None:
            return cls._pipeline

        if KPipeline is None:
            logger.error(
                "Kokoro is not installed, so TTS is unavailable. Install it with: pip install kokoro==0.9.4 soundfile==0.12.1"
            )
            return None

        with cls._pipeline_lock:
            if cls._pipeline is not None:
                return cls._pipeline

            logger.info("Loading Kokoro TTS pipeline for ARAXON...")
            try:
                cls._pipeline = KPipeline(lang_code=settings.TTS_VOICE[:1].lower() if settings.TTS_VOICE else "a")
                cls._pipeline_signature = (
                    settings.TTS_VOICE,
                    settings.LOG_LEVEL,
                    float(settings.TTS_SPEED),
                    int(settings.TTS_SAMPLE_RATE),
                )
                logger.info("Kokoro TTS pipeline loaded successfully.")
                return cls._pipeline
            except Exception as exc:
                logger.error(
                    f"Failed to load Kokoro TTS pipeline: {exc}. Install Kokoro with: pip install kokoro==0.9.4 soundfile==0.12.1"
                )
                return None

    def _iter_tts_chunks(self, text: str) -> list[str]:
        """Split sanitized text into Kokoro-sized synthesis chunks."""
        sanitized_text = sanitize_text(text)
        if not sanitized_text:
            return []

        chunks = chunk_text(sanitized_text, size=self.chunk_size)
        normalized_chunks: list[str] = []
        for chunk in chunks:
            if len(chunk) <= self.chunk_size:
                normalized_chunks.append(chunk)
                continue

            start = 0
            while start < len(chunk):
                end = min(start + self.chunk_size, len(chunk))
                if end < len(chunk):
                    split_at = chunk.rfind(" ", start, end)
                    if split_at > start:
                        end = split_at
                piece = chunk[start:end].strip()
                if piece:
                    normalized_chunks.append(piece)
                start = end + 1 if end < len(chunk) and chunk[end:end + 1] == " " else end

        return normalized_chunks

    def _extract_audio_array(self, synthesis_result):
        """Extract a NumPy audio array from a Kokoro synthesis result."""
        if synthesis_result is None or np is None:
            return None

        if isinstance(synthesis_result, (tuple, list)) and synthesis_result:
            audio = synthesis_result[-1]
        else:
            audio = getattr(synthesis_result, "audio", None)

        if audio is None:
            return None

        audio_array = np.asarray(audio, dtype=np.float32).reshape(-1)
        if audio_array.size == 0:
            return None
        return audio_array

    def _synthesize_chunk_sync(self, chunk: str):
        """Synchronously synthesize one chunk of text into a NumPy audio array."""
        pipeline = self._ensure_pipeline_sync()
        if pipeline is None or np is None:
            return np.array([], dtype=np.float32) if np is not None else None

        start_time = time.monotonic()
        try:
            generator = pipeline(chunk, voice=self.voice, speed=self.speed, split_pattern=r"\n+")
            audio_parts = []
            for synthesis_result in generator:
                audio = self._extract_audio_array(synthesis_result)
                if audio is not None and audio.size:
                    audio_parts.append(audio)

            if not audio_parts:
                logger.info("Kokoro synthesis produced no audio for this chunk.")
                return np.array([], dtype=np.float32)

            combined_audio = np.concatenate(audio_parts).astype(np.float32, copy=False)
            elapsed_seconds = time.monotonic() - start_time
            logger.info(f"Kokoro synthesized chunk in {elapsed_seconds:.2f}s ({len(chunk)} characters).")
            return combined_audio
        except Exception as exc:
            logger.error(f"Kokoro synthesis failed for a chunk: {exc}")
            return np.array([], dtype=np.float32)

    async def synthesize(self, text: str):
        """Synthesize cleaned text into a single NumPy audio buffer."""
        if np is None:
            logger.error("NumPy is not installed, so TTS synthesis cannot run.")
            return None

        if not text or not str(text).strip():
            logger.info("Empty TTS input received, skipping synthesis.")
            return np.array([], dtype=np.float32)

        normalized_chunks = self._iter_tts_chunks(text)
        if not normalized_chunks:
            logger.info("No valid TTS chunks were produced after sanitizing input.")
            return np.array([], dtype=np.float32)

        audio_parts = []
        for chunk in normalized_chunks:
            audio = await asyncio.to_thread(self._synthesize_chunk_sync, chunk)
            if audio is not None and audio.size:
                audio_parts.append(audio)

        if not audio_parts:
            return np.array([], dtype=np.float32)

        return np.concatenate(audio_parts).astype(np.float32, copy=False)

    def _write_wave_file_sync(self, path: str, audio_array):
        """Write a NumPy audio buffer to disk as a WAV file."""
        output_path = Path(path)
        output_path.parent.mkdir(parents=True, exist_ok=True)

        if np is None:
            return str(output_path)

        if sf is not None:
            sf.write(str(output_path), audio_array, self.sample_rate)
            return str(output_path)

        pcm_audio = np.asarray(audio_array, dtype=np.float32).reshape(-1)
        pcm_audio = np.clip(pcm_audio, -1.0, 1.0)
        pcm_audio = (pcm_audio * 32767.0).astype("<i2", copy=False)

        with wave.open(str(output_path), "wb") as wav_file:
            wav_file.setnchannels(1)
            wav_file.setsampwidth(2)
            wav_file.setframerate(self.sample_rate)
            wav_file.writeframes(pcm_audio.tobytes())
        return str(output_path)

    async def synthesize_to_file(self, text: str, path: str) -> str:
        """Synthesize text and save the resulting audio to a WAV file."""
        audio = await self.synthesize(text)
        if np is None:
            logger.error("NumPy is not installed, so WAV output cannot be created.")
            return path

        if audio is None:
            audio = np.array([], dtype=np.float32)

        try:
            return await asyncio.to_thread(self._write_wave_file_sync, path, audio)
        except Exception as exc:
            logger.error(f"Failed to save Kokoro audio to file: {exc}")
            return path