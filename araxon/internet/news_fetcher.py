"""Latest news fetcher for ARAXON."""

from __future__ import annotations

import time

from araxon.internet.searcher import WebSearcher
from araxon.ai.brain import ARAXONBrain
from araxon.core.logger import logger
from araxon.core.config import settings
from araxon.core.utils import sanitize_text


class NewsFetcher:
	"""Fetch and summarize latest news on any topic."""

	def __init__(self) -> None:
		"""Initialize the news fetcher."""
		self.searcher = WebSearcher()
		self.brain = ARAXONBrain()

	async def get_news(self, topic: str | None = None) -> str:
		"""Get latest news headlines on a topic.

		Args:
			topic: News topic. Defaults to NEWS_DEFAULT_TOPIC if not provided.

		Returns:
			Spoken summary of top headlines.
		"""
		try:
			topic = topic or settings.NEWS_DEFAULT_TOPIC
			logger.info(f"[NEWS] Fetching headlines for: '{topic}'")
			start_time = time.time()

			# Get news
			news_results = await self.searcher.search_news(topic)
			if not news_results:
				return f"I couldn't find recent news about {topic}."

			# Limit to MAX_ARTICLES
			news_results = news_results[:settings.NEWS_MAX_ARTICLES]

			# Format headlines for speech
			summary_parts = [f"Here are the latest headlines on {topic}."]

			for idx, article in enumerate(news_results, 1):
				title = article.get("title", "Unknown").strip()
				source = article.get("source", "a news source").strip()
				date = article.get("date", "").strip()

				if idx == 1:
					summary_parts.append(f"First: {title} from {source}.")
				else:
					summary_parts.append(f"Number {idx}: {title} from {source}.")

			summary = " ".join(summary_parts)

			elapsed = time.time() - start_time
			logger.info(
				f"[NEWS] Completed '{topic}': {len(news_results)} articles in {elapsed:.2f}s"
			)

			return sanitize_text(summary)

		except Exception as exc:
			logger.error(f"[NEWS] Failed for '{topic}': {exc}")
			return f"I encountered an error fetching news about {topic}."

	async def get_tech_news(self) -> str:
		"""Get latest technology and AI news.

		Returns:
			Spoken summary of tech headlines.
		"""
		logger.info("[NEWS] Fetching tech news")
		return await self.get_news("technology AI programming")

	async def get_top_headline(self) -> str:
		"""Get just the single top news headline.

		Returns:
			Single headline as one sentence.
		"""
		try:
			logger.info("[NEWS] Fetching top headline")

			news_results = await self.searcher.search_news(settings.NEWS_DEFAULT_TOPIC)
			if not news_results:
				return "I couldn't find any recent news."

			top = news_results[0]
			title = top.get("title", "Unknown")
			source = top.get("source", "a news source")

			headline = f"The latest headline is: {title} from {source}."

			logger.info(f"[NEWS] Top headline: {title}")
			return sanitize_text(headline)

		except Exception as exc:
			logger.error(f"[NEWS] Failed to fetch top headline: {exc}")
			return "I couldn't fetch the latest headline."
