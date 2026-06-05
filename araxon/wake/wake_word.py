"""Wake word and standby phrase matching for ARAXON."""

from __future__ import annotations

import re
from dataclasses import dataclass

from araxon.core.config import settings
from araxon.core.logger import logger


@dataclass(frozen=True)
class _MatchResult:
	"""Internal helper describing a matched phrase span."""

	phrase: str
	start: int
	end: int


class WakeWordDetector:
	"""Perform fast wake phrase, sleep phrase, and reset phrase detection."""

	def __init__(self) -> None:
		"""Initialize normalized phrase lists for quick text matching."""
		self._wake_phrases = tuple(self._normalize_phrase(phrase) for phrase in settings.WAKE_PHRASES)
		self._sleep_phrases = tuple(self._normalize_phrase(phrase) for phrase in settings.SLEEP_PHRASES)
		self._reset_phrases = tuple(self._normalize_phrase(phrase) for phrase in settings.RESET_PHRASES)

	def _normalize_text(self, text: str) -> str:
		"""Lowercase text and strip punctuation for matching."""
		clean_text = re.sub(r"[^\w\s]", " ", text.lower())
		return re.sub(r"\s+", " ", clean_text).strip()

	def _normalize_phrase(self, phrase: str) -> str:
		"""Normalize a phrase using the same rules as transcription text."""
		return self._normalize_text(phrase)

	def _edit_distance_at_most_one(self, left: str, right: str) -> bool:
		"""Return True when two strings are identical or differ by one edit."""
		if left == right:
			return True

		left_length = len(left)
		right_length = len(right)
		if abs(left_length - right_length) > 1:
			return False

		index_left = 0
		index_right = 0
		differences = 0

		while index_left < left_length and index_right < right_length:
			if left[index_left] == right[index_right]:
				index_left += 1
				index_right += 1
				continue

			differences += 1
			if differences > 1:
				return False

			if left_length > right_length:
				index_left += 1
			elif right_length > left_length:
				index_right += 1
			else:
				index_left += 1
				index_right += 1

		if index_left < left_length or index_right < right_length:
			differences += 1

		return differences <= 1

	def _find_match(self, text: str, phrases: tuple[str, ...]) -> _MatchResult | None:
		"""Find the first exact or fuzzy phrase match in the supplied text."""
		normalized_text = self._normalize_text(text)
		if not normalized_text:
			return None

		for phrase in phrases:
			if not phrase:
				continue
			if phrase in normalized_text:
				start = normalized_text.index(phrase)
				return _MatchResult(phrase=phrase, start=start, end=start + len(phrase))

			window_length = len(phrase)
			for start in range(0, len(normalized_text) - window_length + 1):
				candidate = normalized_text[start : start + window_length]
				if self._edit_distance_at_most_one(candidate, phrase):
					return _MatchResult(phrase=phrase, start=start, end=start + window_length)

		return None

	def check(self, text: str, state_label: str = "[ACTIVE]") -> bool:
		"""Return True when a wake phrase is present in the supplied text."""
		if not settings.WAKE_WORD_ENABLED:
			return False

		match = self._find_match(text, self._wake_phrases)
		if match is None:
			return False

		logger.info(f"{state_label} Wake word detected with phrase '{match.phrase}'.")
		return True

	def extract_command(self, text: str, state_label: str = "[ACTIVE]") -> str:
		"""Return the command text that follows a wake phrase, if any."""
		if not settings.WAKE_WORD_ENABLED:
			return ""

		normalized_text = self._normalize_text(text)
		match = self._find_match(normalized_text, self._wake_phrases)
		if match is None:
			return ""

		command_text = normalized_text[match.end :].strip()
		logger.info(f"{state_label} Wake word matched '{match.phrase}' with command '{command_text or '[none]'}'.")
		return command_text

	def is_sleep_command(self, text: str) -> bool:
		"""Return True when the text requests standby or sleep mode."""
		match = self._find_match(text, self._sleep_phrases)
		return match is not None

	def is_reset_command(self, text: str) -> bool:
		"""Return True when the text requests a memory reset."""
		match = self._find_match(text, self._reset_phrases)
		return match is not None