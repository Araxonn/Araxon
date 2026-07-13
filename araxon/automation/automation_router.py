"""Natural-language automation router for ARAXON."""

from __future__ import annotations

import re
from difflib import SequenceMatcher

from araxon.core.config import settings
from araxon.core.logger import logger

from .app_launcher import AppLauncher
from .browser_agent import BrowserAgent
from .command_runner import CommandRunner
from .web_launcher import WebLauncher
from .workspace_manager import WorkspaceManager


class AutomationRouter:
	"""Route spoken commands to the correct automation handler."""

	def __init__(self) -> None:
		"""Create the automation handlers used for routing voice commands."""
		self.app_launcher = AppLauncher()
		self.web_launcher = WebLauncher()
		self.browser_agent = BrowserAgent()
		self.command_runner = CommandRunner()
		self.workspace_manager = WorkspaceManager(self.app_launcher, self.web_launcher, self.command_runner)

	async def initialize(self) -> None:
		"""Prepare automation handlers for use at startup."""
		logger.info("[ACTIVE] Initializing automation handlers.")
		await self.browser_agent.start()

	async def shutdown(self) -> None:
		"""Stop automation handlers cleanly."""
		await self.browser_agent.stop()
		logger.info("[ACTIVE] Automation handlers shut down.")

	def _normalize_text(self, text: str) -> str:
		"""Normalize voice text so routing works with imperfect transcriptions."""
		return re.sub(r"[^a-z0-9]+", " ", text.lower()).strip()

	def _contains_any(self, text: str, terms: list[str]) -> str | None:
		"""Return the first matching term in the supplied text."""
		for term in terms:
			if term in text:
				return term
		return None

	def _find_best_match(self, text: str, candidates: list[str], minimum_score: float = 0.62) -> str | None:
		"""Find the closest known phrase for imperfect speech recognition."""
		normalized_text = self._normalize_text(text)
		if not normalized_text:
			return None

		for candidate in candidates:
			if not candidate:
				continue
			if self._normalize_text(candidate) in normalized_text:
				return candidate

		best_match: str | None = None
		best_score = 0.0
		for candidate in candidates:
			if not candidate:
				continue
			score = SequenceMatcher(None, normalized_text, self._normalize_text(candidate)).ratio()
			if score > best_score:
				best_score = score
				best_match = candidate

		if best_match is not None and best_score >= minimum_score:
			return best_match
		return None

	def _extract_command_tail(self, text: str, trigger: str) -> str:
		"""Extract the text after a trigger phrase for search commands."""
		if trigger in text:
			return text.split(trigger, 1)[1].strip()
		return text.strip()

	def _build_help_summary(self) -> str:
		"""Return a concise list of supported voice-driven actions."""
		workspace_names = ", ".join(sorted(settings.WORKSPACE_PROFILES.keys()))
		app_names = ", ".join(sorted(settings.APP_MAP.keys()))
		command_names = ", ".join(sorted(settings.COMMAND_MAP.keys()))
		return (
			"I can help with these voice commands: "
			f"Open Spotify, VS Code, Chrome, or other apps. "
			f"Launch a workspace profile such as {workspace_names}. "
			f"Open websites such as YouTube, GitHub, Google, and localhost. "
			f"Run quick commands such as {command_names}."
		)

	async def route(self, text: str) -> str | None:
		"""Route a voice command to automation or return None for normal chat."""
		normalized_text = text.strip().lower()
		if not normalized_text:
			return None

		if normalized_text in {"help", "commands", "what can you do", "what commands do you support"}:
			return self._build_help_summary()

		# STEP 7: workspace routing.
		for profile_name in settings.WORKSPACE_PROFILES:
			profile_aliases = [profile_name, f"{profile_name} workspace", f"my {profile_name} workspace"]
			if any(alias in normalized_text for alias in profile_aliases):
				return await self.workspace_manager.launch_profile(profile_name)
			if self._find_best_match(normalized_text, profile_aliases, minimum_score=0.6) is not None:
				return await self.workspace_manager.launch_profile(profile_name)

		# STEP 7: app routing.
		app_match = self._find_best_match(normalized_text, list(settings.APP_MAP.keys()))
		if any(verb in normalized_text for verb in ("open", "launch", "start", "run")) and app_match is not None:
			return await self.app_launcher.launch(app_match)
		if any(verb in normalized_text for verb in ("close", "quit", "shutdown")) and app_match is not None:
			return await self.app_launcher.close(app_match)

		# STEP 7: website routing.
		website_match = self._find_best_match(normalized_text, list(settings.WEBSITE_MAP.keys()))
		if normalized_text.startswith(("http://", "https://")):
			return await self.web_launcher.open(text.strip())
		if any(verb in normalized_text for verb in ("open", "launch", "go to", "navigate to", "visit")) and website_match is not None:
			return await self.web_launcher.open(website_match)
		if normalized_text.startswith("open ") and app_match is None:
			return await self.web_launcher.open(self._extract_command_tail(normalized_text, "open"))
		if "go to" in normalized_text or "navigate to" in normalized_text:
			if website_match is not None:
				return await self.web_launcher.open(website_match)
			return await self.web_launcher.open(self._extract_command_tail(normalized_text, "go to") or self._extract_command_tail(normalized_text, "navigate to"))

		# STEP 7: browser routing.
		if "search google" in normalized_text or "search for" in normalized_text:
			query = self._extract_command_tail(normalized_text, "search google") or self._extract_command_tail(normalized_text, "search for")
			return await self.browser_agent.search_google(query)
		if "search youtube" in normalized_text or "play on youtube" in normalized_text:
			query = self._extract_command_tail(normalized_text, "search youtube") or self._extract_command_tail(normalized_text, "play on youtube")
			return await self.browser_agent.search_youtube(query)
		if "take screenshot" in normalized_text:
			return await self.browser_agent.take_screenshot()

		# STEP 7: command routing.
		command_match = self._find_best_match(normalized_text, list(settings.COMMAND_MAP.keys()))
		if command_match is not None:
			return await self.command_runner.run(command_match)
		if normalized_text.startswith("run "):
			raw_command = normalized_text.removeprefix("run ").strip()
			if raw_command:
				return await self.command_runner.run(raw_command)

		return None
