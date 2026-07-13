"""Playwright browser automation for ARAXON."""

from __future__ import annotations

import asyncio
import sys
from contextlib import suppress
from datetime import datetime
from pathlib import Path
from urllib.parse import quote_plus

if sys.platform == "win32":
	asyncio.set_event_loop_policy(asyncio.WindowsProactorEventLoopPolicy())

from araxon.core.config import settings
from araxon.core.logger import logger

try:
	from playwright.async_api import async_playwright
except Exception:  # pragma: no cover - optional dependency fallback
	async_playwright = None


class BrowserAgent:
	"""Automate browser tasks with a persistent Chromium session."""

	def __init__(self) -> None:
		"""Initialize browser state without launching the browser."""
		self.browser = None
		self.context = None
		self.page = None
		self.playwright = None
		self._started = False
		self._start_lock = asyncio.Lock()

	def _ensure_log_directories(self) -> Path:
		"""Create the screenshot directory if it does not already exist."""
		screenshot_dir = Path("logs") / "screenshots"
		screenshot_dir.mkdir(parents=True, exist_ok=True)
		return screenshot_dir

	async def _ensure_started(self) -> bool:
		"""Auto-start the browser if it has not already been launched."""
		if self._started and self.browser is not None and self.page is not None:
			return True

		async with self._start_lock:
			if self._started and self.browser is not None and self.page is not None:
				return True
			await self.start()
			return self._started and self.browser is not None and self.page is not None

	async def start(self) -> None:
		"""Launch Chromium and keep the browser and page available for reuse."""
		if self._started and self.browser is not None and self.page is not None:
			return

		try:
			if async_playwright is None:
				raise RuntimeError("playwright is not installed")
			self.playwright = await async_playwright().start()
			self.browser = await self.playwright.chromium.launch(headless=settings.BROWSER_HEADLESS)
			self.context = await self.browser.new_context()
			self.page = await self.context.new_page()
			self._started = True
			logger.info("[ACTIVE] Browser agent started successfully.")
		except Exception as exc:
			logger.error(f"[ACTIVE] Browser start failed: {exc}")
			logger.warning("Browser automation unavailable. Install playwright: pip install playwright then: python -m playwright install chromium")
			self.browser = None
			self.context = None
			self.page = None
			self.playwright = None
			self._started = False

	async def stop(self) -> None:
		"""Close the browser session and release all Playwright resources."""
		with suppress(Exception):
			if self.context is not None:
				await self.context.close()
		with suppress(Exception):
			if self.browser is not None:
				await self.browser.close()
		with suppress(Exception):
			if self.playwright is not None:
				await self.playwright.stop()
		self.browser = None
		self.context = None
		self.page = None
		self.playwright = None
		self._started = False
		logger.info("[ACTIVE] Browser agent stopped.")

	async def navigate(self, url: str) -> str:
		"""Navigate to a URL and return the page title."""
		if not await self._ensure_started():
			return "Browser automation unavailable."
		if not self.page:
			return "Browser not available. Playwright not running."

		start_time = asyncio.get_event_loop().time()
		try:
			await self.page.goto(url, wait_until="load", timeout=settings.BROWSER_TIMEOUT_MS)
			title = await self.page.title()
			elapsed = asyncio.get_event_loop().time() - start_time
			logger.info(f"[ACTIVE] Navigated to {url} in {elapsed:.2f}s.")
			return title or "Page loaded."
		except Exception as exc:
			logger.error(f"[ACTIVE] Navigation failed for {url}: {exc}")
			return "Could not load page."

	async def search_google(self, query: str) -> str:
		"""Search Google and return the top three result titles and URLs."""
		if not await self._ensure_started():
			return "Browser automation unavailable."
		if not self.page:
			return "Browser not available. Playwright not running."

		start_time = asyncio.get_event_loop().time()
		search_url = f"https://www.google.com/search?q={quote_plus(query)}"
		try:
			await self.page.goto(search_url, wait_until="load", timeout=settings.BROWSER_TIMEOUT_MS)
			results: list[str] = []
			links = self.page.locator("a:has(h3)")
			limit = min(await links.count(), 3)
			for index in range(limit):
				link = links.nth(index)
				title = (await link.locator("h3").inner_text()).strip()
				href = (await link.get_attribute("href") or "").strip()
				if title:
					results.append(f"{title} - {href}")
			elapsed = asyncio.get_event_loop().time() - start_time
			logger.info(f"[ACTIVE] Google search for '{query}' completed in {elapsed:.2f}s.")
			if not results:
				return "No Google results found."
			return "Google results: " + "; ".join(results)
		except Exception as exc:
			logger.error(f"[ACTIVE] Google search failed for '{query}': {exc}")
			return "Could not search Google."

	async def search_youtube(self, query: str) -> str:
		"""Search YouTube and return the top three video titles."""
		if not await self._ensure_started():
			return "Browser automation unavailable."
		if not self.page:
			return "Browser not available. Playwright not running."

		start_time = asyncio.get_event_loop().time()
		search_url = f"https://www.youtube.com/results?search_query={quote_plus(query)}"
		try:
			await self.page.goto(search_url, wait_until="load", timeout=settings.BROWSER_TIMEOUT_MS)
			results: list[str] = []
			videos = self.page.locator("ytd-video-renderer a#video-title")
			limit = min(await videos.count(), 3)
			for index in range(limit):
				video = videos.nth(index)
				title = (await video.get_attribute("title") or await video.inner_text() or "").strip()
				if title:
					results.append(title)
			elapsed = asyncio.get_event_loop().time() - start_time
			logger.info(f"[ACTIVE] YouTube search for '{query}' completed in {elapsed:.2f}s.")
			if not results:
				return "No YouTube results found."
			return "YouTube results: " + "; ".join(results)
		except Exception as exc:
			logger.error(f"[ACTIVE] YouTube search failed for '{query}': {exc}")
			return "Could not search YouTube."

	async def get_page_summary(self, url: str) -> str:
		"""Load a URL and return a short text summary from the page body."""
		if not await self._ensure_started():
			return "Browser automation unavailable."
		if not self.page:
			return "Browser not available. Playwright not running."

		start_time = asyncio.get_event_loop().time()
		try:
			await self.page.goto(url, wait_until="load", timeout=settings.BROWSER_TIMEOUT_MS)
			body_text = (await self.page.locator("body").inner_text()).strip()
			summary = body_text[:500] if body_text else "No readable page text found."
			elapsed = asyncio.get_event_loop().time() - start_time
			logger.info(f"[ACTIVE] Summary captured for {url} in {elapsed:.2f}s.")
			return summary
		except Exception as exc:
			logger.error(f"[ACTIVE] Page summary failed for {url}: {exc}")
			return "Could not summarize page."

	async def take_screenshot(self, path: str | None = None) -> str:
		"""Take a screenshot of the current page and return the saved path."""
		if not await self._ensure_started():
			return "Browser automation unavailable."
		if not self.page:
			return "Browser not available. Playwright not running."

		start_time = asyncio.get_event_loop().time()
		try:
			if path is None:
				screenshot_dir = self._ensure_log_directories()
				timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
				path = str(screenshot_dir / f"screenshot_{timestamp}.png")
			else:
				Path(path).parent.mkdir(parents=True, exist_ok=True)

			await self.page.screenshot(path=path, full_page=True)
			elapsed = asyncio.get_event_loop().time() - start_time
			logger.info(f"[ACTIVE] Screenshot saved to {path} in {elapsed:.2f}s.")
			return path
		except Exception as exc:
			logger.error(f"[ACTIVE] Screenshot failed for {path}: {exc}")
			return "Could not take screenshot."
