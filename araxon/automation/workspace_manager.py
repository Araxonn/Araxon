"""Workspace profile orchestration for ARAXON."""

from __future__ import annotations

import asyncio

from araxon.core.config import settings
from araxon.core.logger import logger

from .app_launcher import AppLauncher
from .command_runner import CommandRunner
from .web_launcher import WebLauncher


class WorkspaceManager:
	"""Launch complete development environment profiles."""

	def __init__(self, app_launcher: AppLauncher | None = None, web_launcher: WebLauncher | None = None, command_runner: CommandRunner | None = None) -> None:
		"""Bind the automation handlers used by workspace profiles."""
		self.app_launcher = app_launcher or AppLauncher()
		self.web_launcher = web_launcher or WebLauncher()
		self.command_runner = command_runner or CommandRunner()

	def get_available_profiles(self) -> list[str]:
		"""Return the configured workspace profile names."""
		return list(settings.WORKSPACE_PROFILES.keys())

	def _step_summary(self, step: str, result: str) -> str:
		"""Convert a profile step into a short spoken-friendly summary."""
		lower_step = step.strip().lower()
		if lower_step.startswith(("http://", "https://")):
			return "opened localhost"
		if lower_step in settings.APP_MAP:
			return f"opened {lower_step}"
		if "npm run dev" in lower_step:
			return "started dev server"
		if "python main.py" in lower_step:
			return "started Python app"
		if "ollama serve" in lower_step:
			return "started AI server"
		if lower_step.startswith("code"):
			return "opened VS Code"
		return result.strip()[:60] if result.strip() else lower_step

	async def launch_profile(self, profile_name: str) -> str:
		"""Launch a workspace profile step by step."""
		normalized_profile = profile_name.strip().lower()
		profile_steps = settings.WORKSPACE_PROFILES.get(normalized_profile)
		if profile_steps is None:
			logger.warning(f"[ACTIVE] Unknown workspace profile requested: {normalized_profile}")
			return f"Could not launch {normalized_profile} workspace."

		spoken_steps: list[str] = []
		for index, step in enumerate(profile_steps):
			try:
				logger.info(f"[ACTIVE] Launching workspace '{normalized_profile}' step {index + 1}: {step}")
				lower_step = step.strip().lower()
				if lower_step.startswith(("http://", "https://")):
					result = await self.web_launcher.open(step)
				elif lower_step in settings.APP_MAP:
					result = await self.app_launcher.launch(lower_step)
				else:
					result = await self.command_runner.run_raw(step)
				spoken_steps.append(self._step_summary(step, result))
				logger.info(f"[ACTIVE] Workspace '{normalized_profile}' step result: {result}")
			except Exception as exc:
				logger.error(f"[ACTIVE] Workspace '{normalized_profile}' step failed for '{step}': {exc}")
				spoken_steps.append("one step failed")
			finally:
				if index < len(profile_steps) - 1:
					await asyncio.sleep(1)

		profile_label = normalized_profile.upper() if normalized_profile != "focus" else "focus"
		joined_steps = ", ".join(spoken_steps) if spoken_steps else "nothing happened"
		return f"Launched {profile_label} workspace: {joined_steps}"
