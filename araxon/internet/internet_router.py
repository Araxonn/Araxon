"""Voice command router for ARAXON internet intelligence."""

from __future__ import annotations

import re

from araxon.internet.searcher import WebSearcher
from araxon.internet.extractor import ContentExtractor
from araxon.internet.researcher import WebResearcher
from araxon.internet.news_fetcher import NewsFetcher
from araxon.internet.wiki_lookup import WikiLookup
from araxon.core.logger import logger


class InternetRouter:
	"""Route voice commands to the correct internet intelligence tool."""

	def __init__(self) -> None:
		"""Initialize all internet handlers."""
		self.searcher = WebSearcher()
		self.extractor = ContentExtractor()
		self.researcher = WebResearcher()
		self.news_fetcher = NewsFetcher()
		self.wiki_lookup = WikiLookup()
		self._initialized = False

	async def initialize(self) -> None:
		"""Initialize all internet handlers."""
		self._initialized = True
		logger.info("[INTERNET] Internet intelligence system online")

	async def shutdown(self) -> None:
		"""Clean shutdown of all handlers."""
		await self.extractor.close()
		await self.researcher.close()
		logger.info("[INTERNET] Internet intelligence system offline")

	async def route(self, text: str) -> str | None:
		"""Route voice command to appropriate internet tool.

		Args:
			text: Voice command text.

		Returns:
			Result string if handled, None if not internet command.
		"""
		if not text:
			return None

		text_lower = text.strip().lower()

		# NEWS commands: "news", "headlines", "what's happening"
		if any(word in text_lower for word in ["news", "headlines", "what's happening"]):
			topic = self._extract_topic_after_keywords(text_lower, ["news about", "headlines on"])
			logger.info(f"[ROUTE] NEWS command: topic='{topic}'")
			if topic:
				return await self.news_fetcher.get_news(topic)
			else:
				return await self.news_fetcher.get_news()

		# WIKIPEDIA commands: "wikipedia", "who is", "what is", "tell me about", "define"
		if any(word in text_lower for word in ["wikipedia", "who is", "what is", "tell me about", "define"]):
			subject = self._extract_subject_from_question(text_lower)
			logger.info(f"[ROUTE] WIKI command: subject='{subject}'")
			if subject:
				return await self.wiki_lookup.lookup(subject)
			return None

		# RESEARCH commands: "research", "find out about", "look into", "investigate"
		if any(word in text_lower for word in ["research", "find out about", "look into", "investigate"]):
			topic = self._extract_topic_after_keywords(
				text_lower, ["research", "find out about", "look into", "investigate"]
			)
			logger.info(f"[ROUTE] RESEARCH command: topic='{topic}'")
			if topic:
				return await self.researcher.research(topic)
			return None

		# COMPARE commands: "compare", "difference between", "versus", "vs"
		if any(word in text_lower for word in ["compare", "difference between", "versus", " vs "]):
			topics = self._extract_two_topics(text_lower)
			logger.info(f"[ROUTE] COMPARE command: topics={topics}")
			if len(topics) == 2:
				return await self.researcher.compare(topics[0], topics[1])
			return None

		# EXTRACT commands: URL detection (starts with http)
		if "http://" in text_lower or "https://" in text_lower:
			url = self._extract_url(text_lower)
			logger.info(f"[ROUTE] EXTRACT command: url='{url}'")
			if url:
				return await self.extractor.extract_summary(url)
			return None

		# QUICK ANSWER commands: "search for", "look up", "find", "google", "what is the"
		if any(word in text_lower for word in ["search for", "look up", "find", "google", "what is the"]):
			query = self._extract_query_after_keywords(
				text_lower, ["search for", "look up", "find", "google"]
			)
			logger.info(f"[ROUTE] QUICK_ANSWER command: query='{query}'")
			if query:
				return await self.researcher.quick_answer(query)
			return None

		# Not an internet command
		return None

	@staticmethod
	def _extract_topic_after_keywords(text: str, keywords: list[str]) -> str:
		"""Extract topic after a keyword.

		Example: "news about bitcoin" → "bitcoin"
		"""
		for keyword in keywords:
			if keyword in text:
				after = text.split(keyword, 1)[1].strip()
				# Clean up punctuation
				after = re.sub(r"[.!?]*$", "", after)
				return after
		return ""

	@staticmethod
	def _extract_subject_from_question(text: str) -> str:
		"""Extract subject from question phrases.

		Examples:
			"what is python" → "python"
			"who is elon musk" → "elon musk"
			"tell me about ai" → "ai"
		"""
		# Remove question marks and common phrases
		text = text.replace("?", "").strip()

		for pattern in ["what is", "who is", "tell me about", "define"]:
			if pattern in text:
				subject = text.split(pattern, 1)[1].strip()
				return subject

		return ""

	@staticmethod
	def _extract_two_topics(text: str) -> list[str]:
		"""Extract two topics from comparison phrase.

		Examples:
			"compare python and javascript" → ["python", "javascript"]
			"difference between cats and dogs" → ["cats", "dogs"]
		"""
		separators = [" and ", " vs ", " versus "]

		for sep in separators:
			if sep in text:
				parts = text.split(sep)
				if len(parts) >= 2:
					# Clean first topic (remove leading words)
					first = parts[0].strip()
					for prefix in ["compare", "difference between", "compare the", "the"]:
						first = first.replace(prefix, "").strip()
					first = re.sub(r"^(the|a|an)\s+", "", first)

					# Clean second topic
					second = parts[1].strip()
					second = re.sub(r"[.!?]*$", "", second)

					return [first, second]

		return []

	@staticmethod
	def _extract_url(text: str) -> str:
		"""Extract URL from text."""
		# Find first URL
		urls = re.findall(r"https?://[^\s]+", text)
		return urls[0] if urls else ""

	@staticmethod
	def _extract_query_after_keywords(text: str, keywords: list[str]) -> str:
		"""Extract query after keyword.

		Examples:
			"search for python" → "python"
			"google how to code" → "how to code"
		"""
		for keyword in keywords:
			if keyword in text:
				query = text.split(keyword, 1)[1].strip()
				query = re.sub(r"[.!?]*$", "", query)
				return query
		return ""
