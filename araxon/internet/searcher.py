"""DuckDuckGo-powered web search for ARAXON."""

from __future__ import annotations

import asyncio
import time
from typing import Optional

from duckduckgo_search import DDGS

from araxon.core.logger import logger
from araxon.core.config import settings


class WebSearcher:
	"""Free web search using DuckDuckGo API with async support."""

	def __init__(self) -> None:
		"""Initialize the web searcher with DuckDuckGo client."""
		self._last_search_time: float = 0.0
		self._last_search_query: str = ""
		self._last_search_results: list[dict] | None = None

	async def search(self, query: str) -> list[dict]:
		"""Search DuckDuckGo for a query and return top results.

		Args:
			query: Search query string.

		Returns:
			List of dicts: {title, url, snippet}

		Implements rate limiting to avoid DuckDuckGo throttling.
		"""
		try:
			logger.info(f"[SEARCH] Starting search: '{query}'")
			start_time = time.time()

			# Check cache for duplicate queries within 60 seconds
			if query == self._last_search_query and self._last_search_results:
				elapsed = time.time() - self._last_search_time
				if elapsed < 60:
					logger.info(f"[SEARCH] Cache hit for '{query}' ({len(self._last_search_results)} results)")
					return self._last_search_results

			# Rate limit: enforce 1 second gap between searches
			time_since_last = time.time() - self._last_search_time
			if time_since_last < 1.0:
				await asyncio.sleep(1.0 - time_since_last)

			# Run search in thread pool to not block event loop
			results = await asyncio.to_thread(
				self._do_search,
				query,
				settings.SEARCH_MAX_RESULTS,
				settings.SEARCH_REGION,
				settings.SEARCH_SAFE_MODE,
			)

			# Cache results
			self._last_search_time = time.time()
			self._last_search_query = query
			self._last_search_results = results

			elapsed = time.time() - start_time
			logger.info(f"[SEARCH] Completed '{query}': {len(results)} results in {elapsed:.2f}s")
			return results

		except Exception as exc:
			logger.error(f"[SEARCH] Failed for '{query}': {exc}")
			return []

	@staticmethod
	def _do_search(query: str, max_results: int, region: str, safe_mode: bool) -> list[dict]:
		"""Synchronous search wrapper for asyncio.to_thread."""
		try:
			ddgs = DDGS()
			raw_results = ddgs.text(
				query,
				max_results=max_results,
				region=region,
				safesearch="on" if safe_mode else "off",
			)
			# Convert generator to list and extract needed fields
			results = []
			for item in raw_results:
				results.append({
					"title": item.get("title", ""),
					"url": item.get("href", ""),
					"snippet": item.get("body", ""),
				})
			return results
		except Exception as exc:
			logger.error(f"[SEARCH] DuckDuckGo query failed: {exc}")
			return []

	async def search_news(self, query: str) -> list[dict]:
		"""Search DuckDuckGo for latest news on a topic.

		Args:
			query: News search query.

		Returns:
			List of dicts: {title, url, snippet, date, source}
		"""
		try:
			logger.info(f"[NEWS_SEARCH] Starting: '{query}'")
			start_time = time.time()

			# Rate limit
			time_since_last = time.time() - self._last_search_time
			if time_since_last < 1.0:
				await asyncio.sleep(1.0 - time_since_last)

			# Run in thread pool
			results = await asyncio.to_thread(
				self._do_news_search,
				query,
				settings.NEWS_MAX_ARTICLES,
			)

			self._last_search_time = time.time()
			elapsed = time.time() - start_time
			logger.info(f"[NEWS_SEARCH] Completed '{query}': {len(results)} articles in {elapsed:.2f}s")
			return results

		except Exception as exc:
			logger.error(f"[NEWS_SEARCH] Failed for '{query}': {exc}")
			return []

	@staticmethod
	def _do_news_search(query: str, max_results: int) -> list[dict]:
		"""Synchronous news search wrapper."""
		try:
			ddgs = DDGS()
			raw_results = ddgs.news(query, max_results=max_results)
			results = []
			for item in raw_results:
				results.append({
					"title": item.get("title", ""),
					"url": item.get("url", ""),
					"snippet": item.get("body", ""),
					"date": item.get("date", ""),
					"source": item.get("source", ""),
				})
			return results
		except Exception as exc:
			logger.error(f"[NEWS_SEARCH] DuckDuckGo news query failed: {exc}")
			return []

	async def search_images(self, query: str) -> list[dict]:
		"""Search DuckDuckGo for images.

		Args:
			query: Image search query.

		Returns:
			List of dicts: {title, url, thumbnail}
		"""
		try:
			logger.info(f"[IMAGE_SEARCH] Starting: '{query}'")
			start_time = time.time()

			# Rate limit
			time_since_last = time.time() - self._last_search_time
			if time_since_last < 1.0:
				await asyncio.sleep(1.0 - time_since_last)

			# Run in thread pool
			results = await asyncio.to_thread(
				self._do_image_search,
				query,
				max_results=3,
			)

			self._last_search_time = time.time()
			elapsed = time.time() - start_time
			logger.info(f"[IMAGE_SEARCH] Completed '{query}': {len(results)} images in {elapsed:.2f}s")
			return results

		except Exception as exc:
			logger.error(f"[IMAGE_SEARCH] Failed for '{query}': {exc}")
			return []

	@staticmethod
	def _do_image_search(query: str, max_results: int) -> list[dict]:
		"""Synchronous image search wrapper."""
		try:
			ddgs = DDGS()
			raw_results = ddgs.images(query, max_results=max_results)
			results = []
			for item in raw_results:
				results.append({
					"title": item.get("title", ""),
					"url": item.get("image", ""),
					"thumbnail": item.get("thumbnail", ""),
				})
			return results
		except Exception as exc:
			logger.error(f"[IMAGE_SEARCH] DuckDuckGo images query failed: {exc}")
			return []

	@staticmethod
	def format_results_for_speech(results: list[dict]) -> str:
		"""Format search results into natural spoken summary.

		Args:
			results: List of search result dicts.

		Returns:
			Spoken-friendly summary string without raw URLs.
		"""
		if not results:
			return "I found no results for that search."

		count = len(results)
		summary_parts = [f"I found {count} result{'s' if count != 1 else ''}."]

		for idx, result in enumerate(results[:3], 1):
			title = result.get("title", "Unknown").strip()
			url = result.get("url", "").strip()
			snippet = result.get("snippet", "").strip()

			# Extract domain from URL for spoken format
			domain = _extract_domain_for_speech(url)

			if idx == 1:
				summary_parts.append(f"The top result is from {domain}, titled {title}.")
			else:
				summary_parts.append(f"Result {idx} is from {domain}, titled {title}.")

			if snippet:
				# Limit snippet length for speech
				snippet_short = snippet[:150]
				if len(snippet) > 150:
					snippet_short += "..."
				summary_parts.append(f"It says: {snippet_short}")

		return " ".join(summary_parts)


def _extract_domain_for_speech(url: str) -> str:
	"""Extract domain name from URL for natural speech.

	Args:
		url: Full URL string.

	Returns:
		Domain name only, e.g. 'python dot org' from 'https://python.org/docs'.
	"""
	if not url:
		return "a website"

	# Remove protocol
	domain = url.replace("https://", "").replace("http://", "")
	# Remove www
	domain = domain.replace("www.", "")
	# Take first part before slash
	domain = domain.split("/")[0]
	# Replace dots with "dot" for natural speech
	domain = domain.replace(".", " dot ")

	return domain if domain else "a website"
