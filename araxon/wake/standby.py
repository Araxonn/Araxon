"""Standby state management for ARAXON."""

from __future__ import annotations

import asyncio
import time

from araxon.core.config import settings
from araxon.core.logger import logger


class StandbyManager:
	"""Track whether ARAXON is active or sleeping and enforce auto-sleep."""

	def __init__(self) -> None:
		"""Initialize the standby state machine in the active state."""
		self._state = "ACTIVE"
		self._last_interaction = time.monotonic()
		self._activation_time = self._last_interaction
		self._stop_event = asyncio.Event()
		self._monitor_task: asyncio.Task | None = None

	def _prefix(self) -> str:
		"""Return the log prefix that reflects the current standby state."""
		return f"[{self._state}]"

	def activate(self) -> None:
		"""Switch ARAXON to active mode and reset the sleep timer."""
		self._state = "ACTIVE"
		self._activation_time = time.monotonic()
		self.reset_sleep_timer()
		logger.info(f"{self._prefix()} Standby manager activated.")

	def sleep(self, reason: str = "manual") -> None:
		"""Switch ARAXON to standby mode and log the sleep reason."""
		self._state = "STANDBY"
		logger.info(f"{self._prefix()} Standby manager entered standby mode. Reason: {reason}.")

	def is_active(self) -> bool:
		"""Return True when ARAXON is in the active state."""
		return self._state == "ACTIVE"

	def is_standby(self) -> bool:
		"""Return True when ARAXON is in standby mode."""
		return self._state == "STANDBY"

	def reset_sleep_timer(self) -> None:
		"""Reset the auto-sleep countdown after a successful interaction."""
		self._last_interaction = time.monotonic()
		logger.info(f"{self._prefix()} Sleep timer reset.")

	async def start_auto_sleep_monitor(self) -> None:
		"""Periodically transition ARAXON to standby after inactivity."""
		if not settings.STANDBY_MODE_ENABLED:
			logger.info(f"{self._prefix()} Standby mode is disabled, auto-sleep monitor will not start.")
			return

		self._stop_event.clear()
		self._monitor_task = asyncio.current_task()
		logger.info(f"{self._prefix()} Auto-sleep monitor started.")

		try:
			while not self._stop_event.is_set():
				await asyncio.sleep(settings.AUTO_SLEEP_CHECK_INTERVAL_SECONDS)
				if not self.is_active():
					continue

				elapsed_seconds = time.monotonic() - self._last_interaction
				if elapsed_seconds >= settings.AUTO_SLEEP_TIMEOUT_SECONDS:
					logger.info(
						f"{self._prefix()} Auto-sleep triggered after {elapsed_seconds:.0f}s of inactivity."
					)
					self.sleep("inactivity timeout")
		finally:
			logger.info(f"{self._prefix()} Auto-sleep monitor stopped.")
			self._monitor_task = None

	def stop(self) -> None:
		"""Stop the auto-sleep monitor on the next checkpoint."""
		self._stop_event.set()
		if self._monitor_task is not None:
			self._monitor_task.cancel()

	def get_status_string(self) -> str:
		"""Return a human-readable status string for the wake system."""
		if self.is_standby():
			return "STANDBY — sleeping"

		elapsed_seconds = int(time.monotonic() - self._last_interaction)
		return f"ACTIVE — last interaction {elapsed_seconds} seconds ago"