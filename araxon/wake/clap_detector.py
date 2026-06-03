"""Double clap detection for ARAXON wake activation."""

from __future__ import annotations

import asyncio
import threading
import time
from datetime import datetime
from typing import Awaitable, Callable

from araxon.core.config import settings
from araxon.core.logger import logger

try:
	import numpy as np
except Exception:  # pragma: no cover - optional dependency guard
	np = None

try:
	import sounddevice as sd
except Exception:  # pragma: no cover - optional dependency guard
	sd = None


class ClapDetector:
	"""Monitor microphone energy and confirm double clap wake gestures."""

	def __init__(self) -> None:
		"""Initialize clap detection state and background control flags."""
		self._active = False
		self._paused = False
		self._stop_event = threading.Event()
		self._monitor_task: asyncio.Task | None = None
		self._loop: asyncio.AbstractEventLoop | None = None
		self._suppressed_until = 0.0
		self._last_candidate_at = 0.0
		self._last_candidate_energy = 0.0
		self._previously_suppressed = False
		self._lock = threading.Lock()

	@property
	def is_active(self) -> bool:
		"""Return whether the clap detector is currently running."""
		return self._active and not self._stop_event.is_set()

	@property
	def is_suppressed(self) -> bool:
		"""Return whether clap detection is inside the suppression window."""
		return time.monotonic() < self._suppressed_until

	def pause_clap_detection(self) -> None:
		"""Temporarily pause clap detection while ARAXON is speaking."""
		with self._lock:
			self._paused = True

	def resume_clap_detection(self) -> None:
		"""Resume clap detection after spoken output has finished."""
		with self._lock:
			self._paused = False
			self._last_candidate_at = 0.0
			self._last_candidate_energy = 0.0

	async def start(self, callback: Callable[[], Awaitable[None] | None]) -> None:
		"""Start background audio monitoring and invoke the callback on double clap."""
		if self.is_active:
			logger.info("[ACTIVE] Clap detector is already running.")
			return

		if np is None or sd is None:
			logger.error("[ACTIVE] Clap detector cannot start because numpy or sounddevice is unavailable.")
			return

		self._stop_event.clear()
		self._active = True
		self._loop = asyncio.get_running_loop()
		self._monitor_task = asyncio.create_task(self._monitor(callback))
		logger.info("[ACTIVE] Clap detector started.")

	async def _monitor(self, callback: Callable[[], Awaitable[None] | None]) -> None:
		"""Run the blocking clap monitoring loop in a worker thread."""
		try:
			await asyncio.to_thread(self._monitor_sync, callback)
		except asyncio.CancelledError:
			raise
		except Exception as exc:
			logger.error(f"[ACTIVE] Clap detector monitoring failed: {exc}")
		finally:
			self._active = False
			self._stop_event.set()
			logger.info("[ACTIVE] Clap detector stopped.")

	def _monitor_sync(self, callback: Callable[[], Awaitable[None] | None]) -> None:
		"""Synchronously read audio frames and confirm double clap events."""
		if np is None or sd is None:
			return

		frame_seconds = float(settings.CLAP_FRAME_DURATION_SECONDS)
		frame_samples = max(1, int(settings.SAMPLE_RATE * frame_seconds))
		minimum_gap = settings.CLAP_MIN_GAP_MS / 1000.0
		maximum_gap = settings.CLAP_MAX_GAP_MS / 1000.0
		suppression_window = settings.CLAP_SUPPRESSION_WINDOW_MS / 1000.0
		energy_threshold = settings.CLAP_ENERGY_THRESHOLD
		above_threshold = False

		with sd.InputStream(
			samplerate=settings.SAMPLE_RATE,
			channels=1,
			dtype="float32",
			blocksize=frame_samples,
		) as stream:
			while not self._stop_event.is_set():
				with self._lock:
					paused = self._paused

				data, overflowed = stream.read(frame_samples)
				if overflowed:
					logger.warning("[ACTIVE] Clap detector input buffer overflow detected.")

				if self._stop_event.is_set():
					break

				if paused:
					above_threshold = False
					continue

				if self.is_suppressed:
					if not self._previously_suppressed:
						self._previously_suppressed = True
					above_threshold = False
					continue

				if self._previously_suppressed and not self.is_suppressed:
					self._previously_suppressed = False
					logger.info("[ACTIVE] Clap detector suppression window ended.")

				chunk = np.asarray(data, dtype=np.float32).reshape(-1)
				if chunk.size == 0:
					continue

				energy = float(np.sqrt(np.mean(np.square(chunk))))
				now = time.monotonic()

				if energy <= energy_threshold:
					above_threshold = False
					continue

				if above_threshold:
					continue

				above_threshold = True
				if self._last_candidate_at <= 0.0:
					self._last_candidate_at = now
					self._last_candidate_energy = energy
					continue

				gap = now - self._last_candidate_at
				if gap < minimum_gap:
					self._last_candidate_at = now
					self._last_candidate_energy = energy
					continue

				if gap > maximum_gap:
					self._last_candidate_at = now
					self._last_candidate_energy = energy
					continue

				first_energy = self._last_candidate_energy
				second_energy = energy
				self._last_candidate_at = 0.0
				self._last_candidate_energy = 0.0
				self._suppressed_until = now + suppression_window
				self._previously_suppressed = True
				logger.info(
					f"[ACTIVE] Double clap confirmed at {datetime.now().isoformat(timespec='seconds')} "
					f"with energies {first_energy:.3f} -> {second_energy:.3f}."
				)
				logger.info(
					f"[ACTIVE] Clap detector suppression window started for {settings.CLAP_SUPPRESSION_WINDOW_MS}ms."
				)

				if self._loop is not None and not self._loop.is_closed():
					self._loop.call_soon_threadsafe(asyncio.create_task, self._invoke_callback(callback))

	async def _invoke_callback(self, callback: Callable[[], Awaitable[None] | None]) -> None:
		"""Invoke the clap callback safely inside the event loop."""
		try:
			result = callback()
			if asyncio.iscoroutine(result) or isinstance(result, asyncio.Future):
				await result
		except Exception as exc:
			logger.error(f"[ACTIVE] Clap detector callback failed: {exc}")

	def stop(self) -> None:
		"""Stop background clap monitoring and release its worker thread."""
		self._stop_event.set()
		self._active = False
		if self._loop is not None and self._monitor_task is not None and not self._monitor_task.done():
			self._loop.call_soon_threadsafe(self._monitor_task.cancel)