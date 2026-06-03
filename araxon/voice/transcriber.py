"""Speech transcription utilities for ARAXON."""

from __future__ import annotations

import os
import asyncio
import math
import re
import threading
import time
from pathlib import Path
from typing import Optional

os.environ.setdefault("KMP_DUPLICATE_LIB_OK", "TRUE")

try:
    import numpy as np
except ImportError:  # pragma: no cover - optional dependency fallback
    np = None  # type: ignore[assignment]

try:
    import torch
except ImportError:  # pragma: no cover - optional dependency fallback
    torch = None  # type: ignore[assignment]

try:
    from faster_whisper import WhisperModel
except ImportError:  # pragma: no cover - optional dependency fallback
    WhisperModel = None  # type: ignore[assignment]

from araxon.core.config import settings
from araxon.core.logger import logger


class WhisperTranscriber:
    """Transcribe audio using a cached faster-whisper model."""

    _model = None
    _model_lock = threading.Lock()
    _model_signature: Optional[tuple[str, str, str]] = None

    def __init__(self) -> None:
        """Initialize the transcriber and prepare model storage paths."""
        self.model_size = settings.WHISPER_MODEL_SIZE
        self.language = settings.WHISPER_LANGUAGE
        self.models_dir = Path(settings.MODEL_DIR)
        self.models_dir.mkdir(parents=True, exist_ok=True)

    @classmethod
    def _resolve_device_and_compute_type(cls) -> tuple[str, str]:
        """Choose the best available Whisper device and compute type."""
        if torch is not None and torch.cuda.is_available():
            return "cuda", "float16"
        return "cpu", "int8"

    @classmethod
    def _ensure_model_sync(cls):
        """Load the Whisper model once and cache it for reuse."""
        if WhisperModel is None:
            logger.error("faster-whisper is not installed, so transcription is unavailable.")
            return None

        device, compute_type = cls._resolve_device_and_compute_type()
        signature = (settings.WHISPER_MODEL_SIZE, device, compute_type)

        if cls._model is not None and cls._model_signature == signature:
            return cls._model

        with cls._model_lock:
            if cls._model is not None and cls._model_signature == signature:
                return cls._model

            logger.info(
                f"Loading faster-whisper model '{settings.WHISPER_MODEL_SIZE}' on {device} ({compute_type})."
            )
            try:
                cls._model = WhisperModel(
                    settings.WHISPER_MODEL_SIZE,
                    device=device,
                    compute_type=compute_type,
                    download_root=str(Path(settings.MODEL_DIR)),
                )
                cls._model_signature = signature
                logger.info("faster-whisper model loaded successfully.")
                return cls._model
            except Exception as exc:
                if device != "cpu":
                    logger.warning(f"Whisper model load failed on {device}, retrying on CPU: {exc}")
                    try:
                        cls._model = WhisperModel(
                            settings.WHISPER_MODEL_SIZE,
                            device="cpu",
                            compute_type="int8",
                            download_root=str(Path(settings.MODEL_DIR)),
                        )
                        cls._model_signature = (settings.WHISPER_MODEL_SIZE, "cpu", "int8")
                        logger.info("faster-whisper model loaded on CPU fallback.")
                        return cls._model
                    except Exception as fallback_exc:
                        logger.error(f"Failed to load faster-whisper model on CPU fallback: {fallback_exc}")
                        return None

                logger.error(f"Failed to load faster-whisper model: {exc}")
                return None

    @staticmethod
    def _remove_fillers(text: str) -> str:
        """Strip common filler words and normalize spacing."""
        cleaned_text = re.sub(r"\b(?:um|uh|hmm)\b[\s,]*", " ", text, flags=re.IGNORECASE)
        cleaned_text = re.sub(r"\s+", " ", cleaned_text).strip()
        return cleaned_text

    def _transcribe_source_sync(self, source) -> str:
        """Transcribe a NumPy audio buffer or audio file path synchronously."""
        if source is None:
            return ""

        if isinstance(source, str):
            if not Path(source).exists():
                logger.error(f"Audio file not found: {source}")
                return ""
        elif np is not None:
            audio_array = np.asarray(source, dtype=np.float32).flatten()
            if audio_array.size == 0:
                logger.info("Empty audio buffer received, skipping transcription.")
                return ""
            source = audio_array

        model = self._ensure_model_sync()
        if model is None:
            return ""

        start_time = time.monotonic()
        try:
            segments, info = model.transcribe(
                source,
                language=self.language,
                task="transcribe",
                vad_filter=False,
                beam_size=5,
            )
        except Exception as exc:
            logger.error(f"Whisper transcription failed: {exc}")
            return ""

        segment_texts = []
        confidence_values = []
        for segment in segments:
            text = segment.text.strip()
            if text:
                segment_texts.append(text)

            avg_logprob = getattr(segment, "avg_logprob", None)
            if avg_logprob is not None:
                confidence_values.append(max(0.0, min(1.0, math.exp(float(avg_logprob)))))

        raw_text = " ".join(segment_texts)
        cleaned_text = self._remove_fillers(raw_text)
        elapsed_seconds = time.monotonic() - start_time

        if confidence_values:
            confidence = sum(confidence_values) / len(confidence_values)
        else:
            confidence = float(getattr(info, "language_probability", 0.0) or 0.0)

        if cleaned_text:
            logger.info(
                f"Transcription completed in {elapsed_seconds:.2f}s with confidence {confidence:.2f}: {cleaned_text}"
            )
        else:
            logger.info(f"Transcription completed in {elapsed_seconds:.2f}s with no recognized speech.")

        return cleaned_text

    async def transcribe(self, audio: "np.ndarray") -> str:
        """Transcribe an in-memory audio array into clean text."""
        if np is None:
            logger.error("NumPy is not installed, so audio transcription cannot run.")
            return ""

        if audio is None:
            return ""

        audio_array = np.asarray(audio, dtype=np.float32).flatten()
        if audio_array.size == 0:
            logger.info("Empty audio buffer received, skipping transcription.")
            return ""

        return await asyncio.to_thread(self._transcribe_source_sync, audio_array)

    async def transcribe_file(self, path: str) -> str:
        """Transcribe a .wav file from disk into clean text."""
        return await asyncio.to_thread(self._transcribe_source_sync, path)

    def shutdown(self) -> None:
        """Release the cached Whisper model for a clean pipeline shutdown."""
        with self._model_lock:
            self.__class__._model = None
            self.__class__._model_signature = None
        logger.info("Whisper transcriber cache cleared.")