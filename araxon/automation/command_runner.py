"""Command execution utilities for ARAXON."""

from __future__ import annotations

import asyncio
import os
import shlex
import subprocess

from araxon.core.config import settings
from araxon.core.logger import logger


class CommandRunner:
	"""Execute terminal commands with safety checks and output trimming."""

	def __init__(self) -> None:
		"""Initialize the runner with command policy from settings."""
		self._command_map = settings.COMMAND_MAP
		self._allowed_commands = set(settings.ALLOWED_COMMANDS)
		self._timeout_seconds = settings.COMMAND_TIMEOUT_SECONDS

	def _first_word(self, command: str) -> str:
		"""Return the first shell token from a command string."""
		stripped_command = command.strip()
		if not stripped_command:
			return ""
		try:
			return shlex.split(stripped_command, posix=os.name != "nt")[0]
		except Exception:
			return stripped_command.split()[0]

	def _trim_output(self, output: str) -> str:
		"""Keep command output short enough for spoken feedback."""
		clean_output = output.strip()
		if not clean_output:
			return "Command finished."
		return clean_output[-200:]

	def is_safe(self, command: str) -> bool:
		"""Return True when the command begins with an allowed executable."""
		return self._first_word(command) in self._allowed_commands

	async def _execute(self, command: str) -> str:
		"""Run a shell command and return a trimmed summary of its output."""
		logger.info(f"[ACTIVE] Executing command: {command}")
		stripped_command = command.strip()
		if stripped_command.startswith("start cmd"):
			subprocess.Popen(
				stripped_command,
				shell=True,
				creationflags=subprocess.CREATE_NEW_CONSOLE if os.name == "nt" else 0,
			)
			return "Terminal opened successfully."

		if stripped_command == "code .":
			try:
				os.system(stripped_command)
				return "VS Code opened"
			except Exception as exc:
				logger.warning(f"[ACTIVE] os.system fallback failed for code .: {exc}")

		process = await asyncio.create_subprocess_shell(
			stripped_command,
			stdout=asyncio.subprocess.PIPE,
			stderr=asyncio.subprocess.PIPE,
			shell=True,
		)
		try:
			stdout, stderr = await asyncio.wait_for(process.communicate(), timeout=self._timeout_seconds)
		except asyncio.TimeoutError:
			process.kill()
			await process.communicate()
			logger.warning(f"[ACTIVE] Command timed out after {self._timeout_seconds}s: {command}")
			return "Command timed out."

		combined_output = "\n".join(
			part.decode(errors="ignore")
			for part in (stdout, stderr)
			if part
		)
		logger.info(f"[ACTIVE] Command exited with code {process.returncode}.")
		logger.info(f"[ACTIVE] Command output summary: {self._trim_output(combined_output)}")
		return self._trim_output(combined_output)

	async def run(self, command: str) -> str:
		"""Run a command only when it matches the configured safety policy."""
		normalized_command = command.strip()
		translated_command = self._command_map.get(normalized_command.lower(), normalized_command)
		if not self.is_safe(translated_command):
			logger.warning(f"[ACTIVE] Blocked unsafe command: {normalized_command}")
			return "That command is not permitted."
		return await self._execute(translated_command)

	async def run_raw(self, command: str) -> str:
		"""Run a command without restriction for workspace profile orchestration."""
		logger.warning(f"[ACTIVE] Running unrestricted command: {command}")
		return await self._execute(command)
