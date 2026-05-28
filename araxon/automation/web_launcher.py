"""Website launcher for ARAXON."""

from __future__ import annotations

import asyncio
from urllib.parse import quote_plus, urlparse
import webbrowser

from araxon.core.config import settings
from araxon.core.logger import logger


class WebLauncher:
	"""Open websites and URLs in the user's default browser."""

	def __init__(self) -> None:
		"""Initialize the launcher with the configured website map."""
		self._website_map = settings.WEBSITE_MAP

	def get_available_sites(self) -> list[str]:
		"""Return the list of known website aliases."""
		return list(self._website_map.keys())

	def _resolve_url(self, site_name_or_url: str) -> tuple[str, str]:
		"""Resolve an input string to a target URL and a spoken-friendly label."""
		normalized = site_name_or_url.strip()
		lowered = normalized.lower()
		if lowered.startswith(("http://", "https://")):
			return normalized, normalized

		mapped_url = self._website_map.get(lowered)
		if mapped_url is not None:
			return mapped_url, lowered

		search_url = f"https://www.google.com/search?q={quote_plus(normalized)}"
		return search_url, normalized

	async def open(self, site_name_or_url: str) -> str:
		"""Open a website, URL, or Google search for the supplied text."""
		url, label = self._resolve_url(site_name_or_url)
		method = "direct-url" if label == site_name_or_url.strip() and label.lower().startswith(("http://", "https://")) else "mapped-site"
		if url.startswith("https://www.google.com/search?q="):
			method = "google-search"
			logger.info(f"[ACTIVE] Opening search URL via {method}: {url}")
			await asyncio.to_thread(webbrowser.open, url)
			return f"Searching for {label}"

		logger.info(f"[ACTIVE] Opening URL via {method}: {url}")
		await asyncio.to_thread(webbrowser.open, url)
		return f"Opened {label}"
