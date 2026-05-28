"""Webpage content extraction for ARAXON."""

from __future__ import annotations

import asyncio
from typing import Optional

from bs4 import BeautifulSoup
import httpx

try:
	from newspaper import Article
	NEWSPAPER_AVAILABLE = True
except ImportError:
	NEWSPAPER_AVAILABLE = False

from araxon.core.logger import logger
from araxon.core.config import settings
from araxon.core.utils import sanitize_text


class ContentExtractor:
	"""Extract clean, readable content from webpages."""

	def __init__(self) -> None:
		"""Initialize the content extractor."""
		self._client: Optional[httpx.AsyncClient] = None

	async def _get_client(self) -> httpx.AsyncClient:
		"""Lazily initialize httpx client."""
		if self._client is None:
			self._client = httpx.AsyncClient(
				timeout=settings.EXTRACTOR_TIMEOUT_SECONDS,
				headers={
					"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
				},
			)
		return self._client

	async def extract(self, url: str) -> dict:
		"""Extract main content from a webpage.

		Args:
			url: URL to extract from.

		Returns:
			Dict with {title, text, authors, publish_date, url} or
			{title, text, url} if newspaper3k unavailable.
		"""
		try:
			logger.info(f"[EXTRACT] Starting extraction: {url}")

			# Try newspaper3k first if available
			if NEWSPAPER_AVAILABLE:
				result = await self._extract_with_newspaper(url)
				if result:
					return result
				logger.info(f"[EXTRACT] Newspaper3k failed, falling back to BeautifulSoup")

			# Fallback to BeautifulSoup
			result = await self._extract_with_bs4(url)
			return result

		except asyncio.TimeoutError:
			logger.error(f"[EXTRACT] Timeout extracting {url}")
			return {"title": "", "text": "", "url": url}
		except Exception as exc:
			logger.error(f"[EXTRACT] Failed to extract {url}: {exc}")
			return {"title": "", "text": "", "url": url}

	async def _extract_with_newspaper(self, url: str) -> Optional[dict]:
		"""Try extracting content using newspaper3k."""
		try:
			# Run in thread pool since newspaper3k is blocking
			def _newspaper_extract() -> dict:
				article = Article(url)
				article.download()
				article.parse()

				text = sanitize_text(article.text)[:settings.EXTRACTOR_MAX_CHARS]

				return {
					"title": article.title or "",
					"text": text,
					"authors": article.authors or [],
					"publish_date": article.publish_date or "",
					"url": url,
				}

			result = await asyncio.to_thread(_newspaper_extract)
			logger.info(f"[EXTRACT] Newspaper3k extracted {len(result['text'])} chars from {url}")
			return result

		except Exception as exc:
			logger.debug(f"[EXTRACT] Newspaper3k failed for {url}: {exc}")
			return None

	async def _extract_with_bs4(self, url: str) -> dict:
		"""Fallback extraction using BeautifulSoup."""
		try:
			client = await self._get_client()

			# Fetch page
			try:
				response = await asyncio.wait_for(
					client.get(url),
					timeout=settings.EXTRACTOR_TIMEOUT_SECONDS,
				)
				response.raise_for_status()
			except asyncio.TimeoutError:
				logger.warning(f"[EXTRACT] BS4 timeout fetching {url}")
				return {"title": "", "text": "", "url": url}

			# Parse HTML
			soup = BeautifulSoup(response.text, "lxml")

			# Extract title
			title = ""
			if soup.title:
				title = soup.title.string or ""
			elif soup.find("h1"):
				title = soup.find("h1").get_text(strip=True)

			# Extract body text from paragraphs
			text_parts = []
			for p in soup.find_all("p")[:20]:  # Limit to first 20 paragraphs
				text = p.get_text(strip=True)
				if text:
					text_parts.append(text)

			text = sanitize_text(" ".join(text_parts))[:settings.EXTRACTOR_MAX_CHARS]

			logger.info(f"[EXTRACT] BS4 extracted {len(text)} chars from {url}")

			return {
				"title": title,
				"text": text,
				"url": url,
			}

		except Exception as exc:
			logger.error(f"[EXTRACT] BS4 extraction failed for {url}: {exc}")
			return {"title": "", "text": "", "url": url}

	async def extract_summary(self, url: str) -> str:
		"""Extract content and create a brief summary using AI.

		Args:
			url: URL to extract and summarize.

		Returns:
			Spoken-friendly summary string.
		"""
		try:
			logger.info(f"[EXTRACT_SUMMARY] Starting: {url}")

			# Extract content
			extracted = await self.extract(url)
			text = extracted.get("text", "")

			if not text:
				return f"I couldn't extract content from {url}. The page may be empty or blocked."

			# Import here to avoid circular dependency
			from araxon.ai.brain import ARAXONBrain
			brain = ARAXONBrain()

			# Ask brain to summarize
			summary = await brain.think(
				f"Summarize this in 2-3 spoken sentences: {text}"
			)

			logger.info(f"[EXTRACT_SUMMARY] Completed {url}: {len(summary)} char summary")
			return summary

		except Exception as exc:
			logger.error(f"[EXTRACT_SUMMARY] Failed for {url}: {exc}")
			return f"I couldn't summarize {url}."

	async def extract_code_blocks(self, url: str) -> list[str]:
		"""Extract all code blocks from a webpage.

		Args:
			url: URL to extract code from.

		Returns:
			List of code block strings.
		"""
		try:
			logger.info(f"[EXTRACT_CODE] Starting: {url}")
			client = await self._get_client()

			try:
				response = await asyncio.wait_for(
					client.get(url),
					timeout=settings.EXTRACTOR_TIMEOUT_SECONDS,
				)
				response.raise_for_status()
			except asyncio.TimeoutError:
				logger.warning(f"[EXTRACT_CODE] Timeout fetching {url}")
				return []

			soup = BeautifulSoup(response.text, "lxml")

			code_blocks = []
			for tag in soup.find_all(["code", "pre"]):
				code_text = tag.get_text(strip=True)
				if code_text:
					code_blocks.append(code_text)

			logger.info(f"[EXTRACT_CODE] Found {len(code_blocks)} code blocks in {url}")
			return code_blocks

		except Exception as exc:
			logger.error(f"[EXTRACT_CODE] Failed for {url}: {exc}")
			return []

	async def close(self) -> None:
		"""Close the httpx client."""
		if self._client:
			await self._client.aclose()
			self._client = None
