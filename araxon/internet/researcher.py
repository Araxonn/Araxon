"""Multi-source web research for ARAXON."""

from __future__ import annotations

import asyncio
import time

from araxon.internet.searcher import WebSearcher
from araxon.internet.extractor import ContentExtractor
from araxon.ai.brain import ARAXONBrain
from araxon.memory.long_term_memory import LongTermMemory
from araxon.core.logger import logger
from araxon.core.config import settings
from araxon.core.utils import sanitize_text


class WebResearcher:
	"""Multi-source research combining search, extraction, and AI summarization."""

	def __init__(self) -> None:
		"""Initialize the web researcher with its dependencies."""
		self.searcher = WebSearcher()
		self.extractor = ContentExtractor()
		self.brain = ARAXONBrain()
		self.memory = LongTermMemory()

	async def research(self, topic: str) -> str:
		"""Perform full research pipeline on a topic.

		Args:
			topic: Topic to research.

		Returns:
			Spoken-friendly research summary.
		"""
		try:
			logger.info(f"[RESEARCH] Starting full research on: '{topic}'")
			start_time = time.time()

			# Step 1: Search for topic
			search_results = await self.searcher.search(topic)
			if not search_results:
				return f"I couldn't find any information about {topic}."

			# Step 2: Take top N URLs
			top_urls = [r["url"] for r in search_results[:settings.RESEARCH_MAX_SOURCES]]

			# Step 3: Extract content from each URL concurrently
			extract_tasks = [self.extractor.extract(url) for url in top_urls]
			extractions = await asyncio.gather(*extract_tasks)

			# Step 4: Combine all extracted text
			combined_text_parts = []
			for extraction in extractions:
				text = extraction.get("text", "").strip()
				if text:
					combined_text_parts.append(text)

			combined_text = " ".join(combined_text_parts)[:3000]

			if not combined_text:
				return f"I found results about {topic}, but couldn't extract readable content."

			# Step 5: Send to brain for summarization
			summary = await self.brain.think(
				f"You are ARAXON. Summarize this research into 3-4 natural spoken "
				f"sentences a user can understand. No bullet points. No markdown. "
				f"Research: {combined_text}"
			)

			# Step 6: Save to memory if enabled
			if settings.RESEARCH_SAVE_TO_MEMORY:
				try:
					source_domains = [r.get("url", "").split("/")[2] for r in extractions if r.get("url")]
					source_domain = source_domains[0] if source_domains else "web"

					await self.memory.remember_fact(
						fact=summary,
						metadata={
							"source": source_domain,
							"topic": topic,
							"type": "research",
						}
					)
					logger.info(f"[RESEARCH] Saved summary to memory for '{topic}'")
				except Exception as exc:
					logger.warning(f"[RESEARCH] Failed to save to memory: {exc}")

			elapsed = time.time() - start_time
			total_chars = sum(len(e.get("text", "")) for e in extractions)
			logger.info(
				f"[RESEARCH] Completed '{topic}': {len(top_urls)} sources, "
				f"{total_chars} chars, {elapsed:.2f}s"
			)

			return sanitize_text(summary)

		except Exception as exc:
			logger.error(f"[RESEARCH] Failed for '{topic}': {exc}")
			return f"I encountered an error while researching {topic}."

	async def compare(self, topic_a: str, topic_b: str) -> str:
		"""Compare two topics through research and AI analysis.

		Args:
			topic_a: First topic.
			topic_b: Second topic.

		Returns:
			Spoken comparison string.
		"""
		try:
			logger.info(f"[COMPARE] Starting comparison: '{topic_a}' vs '{topic_b}'")

			# Research both topics concurrently
			summary_a, summary_b = await asyncio.gather(
				self.research(topic_a),
				self.research(topic_b),
			)

			if not summary_a or not summary_b:
				return f"I couldn't find enough information to compare {topic_a} and {topic_b}."

			# Send both summaries to brain for comparison
			comparison = await self.brain.think(
				f"Compare these two topics for a user. Keep it to 2-3 spoken sentences. "
				f"Topic A ({topic_a}): {summary_a} "
				f"Topic B ({topic_b}): {summary_b}"
			)

			logger.info(f"[COMPARE] Completed: '{topic_a}' vs '{topic_b}'")
			return sanitize_text(comparison)

		except Exception as exc:
			logger.error(f"[COMPARE] Failed comparing '{topic_a}' and '{topic_b}': {exc}")
			return f"I encountered an error comparing {topic_a} and {topic_b}."

	async def quick_answer(self, question: str) -> str:
		"""Quick factual answer using single search and top result.

		Args:
			question: Factual question.

		Returns:
			One to two sentence answer string.
		"""
		try:
			logger.info(f"[QUICK_ANSWER] Starting: '{question}'")
			start_time = time.time()

			# Single search
			search_results = await self.searcher.search(question)
			if not search_results:
				return f"I couldn't find an answer to {question}."

			# Extract top result
			top_url = search_results[0]["url"]
			extraction = await self.extractor.extract(top_url)
			text = extraction.get("text", "").strip()

			if not text:
				return f"I found a result, but couldn't extract the content."

			# Quick AI answer (one to two sentences)
			answer = await self.brain.think(
				f"Answer this question in 1-2 spoken sentences based on this text. "
				f"Question: {question} "
				f"Text: {text[:500]}"
			)

			elapsed = time.time() - start_time
			logger.info(f"[QUICK_ANSWER] Completed '{question}' in {elapsed:.2f}s")

			return sanitize_text(answer)

		except Exception as exc:
			logger.error(f"[QUICK_ANSWER] Failed for '{question}': {exc}")
			return f"I couldn't answer {question}."

	async def close(self) -> None:
		"""Cleanup resources."""
		await self.extractor.close()
