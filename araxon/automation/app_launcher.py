"""Desktop application launcher for ARAXON."""

from __future__ import annotations

import asyncio
import os

try:
	import psutil
except Exception:  # pragma: no cover - optional dependency fallback
	psutil = None

from araxon.core.config import settings
from araxon.core.logger import logger


class AppLauncher:
	"""Launch, inspect, and close desktop applications by name."""

	def __init__(self) -> None:
		"""Initialize the launcher with the configured application map."""
		self._app_map = settings.APP_MAP

	def get_available_apps(self) -> list[str]:
		"""Return the list of app names ARAXON can open directly."""
		return list(self._app_map.keys())

	def _resolve_command(self, app_name: str) -> str:
		"""Resolve an app name to its launch command or return the raw name."""
		normalized_name = app_name.strip().lower()
		return self._app_map.get(normalized_name, normalized_name)

	def _matches_process(self, process_name: str, app_name: str) -> bool:
		"""Check whether a process name matches the requested application."""
		normalized_process = process_name.lower().replace(".exe", "")
		normalized_target = app_name.lower().replace(".exe", "")
		resolved_target = self._resolve_command(app_name).lower().replace(".exe", "")
		return any(
			match and match in normalized_process
			for match in {normalized_target, resolved_target}
		)

	async def is_running(self, app_name: str) -> bool:
		"""Return True when a matching process is already running."""
		if psutil is None:
			return False

		try:
			for proc in psutil.process_iter(["name"]):
				process_name = proc.info.get("name") or ""
				if process_name and self._matches_process(process_name, app_name):
					return True
		except Exception as exc:
			logger.warning(f"[ACTIVE] App running check failed for {app_name}: {exc}")
		return False

	async def launch(self, app_name: str) -> str:
		"""Launch a desktop application by name using subprocess."""
		normalized_name = app_name.strip().lower()
		command = self._resolve_command(normalized_name)
		logger.info(f"[ACTIVE] Launch request received for app '{normalized_name}'.")

		if await self.is_running(normalized_name):
			logger.info(f"[ACTIVE] App '{normalized_name}' is already running.")
			return f"{normalized_name} is already open"

		try:
			if os.name == "nt":
				process = await asyncio.create_subprocess_shell(command)
			else:
				process = await asyncio.create_subprocess_shell(command)
			logger.info(f"[ACTIVE] App launch succeeded for '{normalized_name}' with pid={process.pid}.")
			return f"Opened {normalized_name}"
		except Exception as exc:
			logger.error(f"[ACTIVE] App launch failed for '{normalized_name}': {exc}")
			return f"Could not open {normalized_name}"

	async def close(self, app_name: str) -> str:
		"""Close a running application by terminating matching processes."""
		normalized_name = app_name.strip().lower()
		logger.info(f"[ACTIVE] Close request received for app '{normalized_name}'.")

		if psutil is None:
			logger.warning(f"[ACTIVE] psutil is unavailable; cannot close '{normalized_name}'.")
			return f"Could not close {normalized_name}"

		closed_any = False
		try:
			for proc in psutil.process_iter(["pid", "name"]):
				process_name = proc.info.get("name") or ""
				if not process_name or not self._matches_process(process_name, normalized_name):
					continue

				try:
					proc.terminate()
					proc.wait(timeout=5)
					closed_any = True
					logger.info(f"[ACTIVE] Closed '{normalized_name}' with pid={proc.info.get('pid')}.")
				except Exception:
					try:
						proc.kill()
						proc.wait(timeout=5)
						closed_any = True
						logger.info(f"[ACTIVE] Killed '{normalized_name}' with pid={proc.info.get('pid')}.")
					except Exception as exc:
						logger.warning(f"[ACTIVE] Failed closing process for '{normalized_name}': {exc}")
		except Exception as exc:
			logger.error(f"[ACTIVE] App close failed for '{normalized_name}': {exc}")

		if closed_any:
			return f"Closed {normalized_name}"
		logger.info(f"[ACTIVE] No running process matched '{normalized_name}'.")
		return f"Could not close {normalized_name}"
