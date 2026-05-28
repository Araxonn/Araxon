"""Wikipedia fast fact lookup for ARAXON."""

from __future__ import annotations

import asyncio

try:
	import wikipediaapi
except ImportError:
	try:
		import Wikipedia_API as wikipediaapi
	except ImportError:
		# Fallback to standard wikipedia package
		import wikipedia
		wikipediaapi = None

from araxon.core.logger import logger
from araxon.core.config import settings
from araxon.core.utils import sanitize_text


class WikiLookup:
	"""Fast Wikipedia fact lookup and article retrieval."""

	def __init__(self) -> None:
		"""Initialize the Wikipedia lookup client."""
		if wikipediaapi is not None:
			self.wiki = wikipediaapi.Wikipedia(language=settings.WIKI_LANGUAGE, user_agent=settings.WIKI_USER_AGENT)
		else:
			wikipedia.set_lang(settings.WIKI_LANGUAGE)
			self.wiki = None

	async def lookup(self, topic: str) -> str:
		"""Look up a topic on Wikipedia.

		Args:
			topic: Topic to look up.

		Returns:
			Spoken-friendly Wikipedia summary.
		"""
		try:
			logger.info(f"[WIKI] Looking up: '{topic}'")

			# Run in thread pool since Wikipedia API can be slow
			page = await asyncio.to_thread(self.wiki.page, topic)

			if not page.exists():
				logger.info(f"[WIKI] Page not found for '{topic}'")
				return (
					f"I couldn't find a Wikipedia page for {topic}. "
					f"Want me to search the web instead?"
				)

			# Get summary and trim
			summary = page.summary or ""
			summary = sanitize_text(summary)[:settings.WIKI_MAX_CHARS]

			if not summary:
				return f"The Wikipedia page for {topic} exists but has no summary."

			logger.info(f"[WIKI] Found '{topic}': {len(summary)} chars")
			return summary

		except Exception as exc:
			logger.error(f"[WIKI] Lookup failed for '{topic}': {exc}")
			return f"I encountered an error looking up {topic}."

	async def lookup_section(self, topic: str, section: str) -> str:
		"""Look up a specific section of a Wikipedia article.

		Args:
			topic: Article topic.
			section: Section name within the article.

		Returns:
			Section text trimmed to WIKI_MAX_CHARS.
		"""
		try:
			logger.info(f"[WIKI] Looking up section '{section}' in '{topic}'")

			page = await asyncio.to_thread(self.wiki.page, topic)

			if not page.exists():
				return f"I couldn't find a Wikipedia page for {topic}."

			# Try to find the section
			section_text = ""
			for section_obj in page.sections:
				if section.lower() in section_obj.title.lower():
					section_text = await asyncio.to_thread(
						lambda: section_obj.text
					)
					break

			if not section_text:
				return f"I couldn't find a section titled '{section}' in the {topic} article."

			section_text = sanitize_text(section_text)[:settings.WIKI_MAX_CHARS]

			logger.info(f"[WIKI] Section '{section}': {len(section_text)} chars")
			return section_text

		except Exception as exc:
			logger.error(f"[WIKI] Section lookup failed for '{topic}.{section}': {exc}")
			return f"I encountered an error looking up that section."

	async def get_quick_fact(self, topic: str) -> str:
		"""Get just the first 2 sentences from Wikipedia summary.

		Args:
			topic: Topic to get facts about.

		Returns:
			First 2 sentences of Wikipedia summary only.
		"""
		try:
			logger.info(f"[WIKI] Quick fact lookup: '{topic}'")

			page = await asyncio.to_thread(self.wiki.page, topic)

			if not page.exists():
				return f"I couldn't find information about {topic}."

			summary = page.summary or ""
			summary = sanitize_text(summary)

			# Extract first 2 sentences
			sentences = summary.split(".")
			fact = ".".join(sentences[:2]).strip()

			if not fact:
				return f"I found the {topic} page but couldn't extract a fact."

			# Ensure it ends with period
			if not fact.endswith("."):
				fact += "."

			logger.info(f"[WIKI] Quick fact: {len(fact)} chars")
			return fact

		except Exception as exc:
			logger.error(f"[WIKI] Quick fact lookup failed for '{topic}': {exc}")
			return f"I encountered an error."
