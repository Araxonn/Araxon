"""Smoke test for the ARAXON wake flow."""

from __future__ import annotations

import asyncio
import time

from araxon.core.config import settings
from araxon.core.logger import logger
from araxon.wake import WakeOrchestrator


class FakeVoiceInputPipeline:
	"""Minimal voice input stub for wake-flow smoke testing."""

	def __init__(self, transcripts: list[str]) -> None:
		"""Store transcripts that will be returned one by one."""
		self.transcripts = list(transcripts)
		self.is_speaking = False

	def set_speaking(self, value: bool) -> None:
		"""Record whether output playback is active."""
		self.is_speaking = bool(value)

	async def listen_and_transcribe(self) -> str:
		"""Return the next queued transcript or an empty string."""
		await asyncio.sleep(0)
		if self.transcripts:
			return self.transcripts.pop(0)
		return ""


class FakeVoiceOutputPipeline:
	"""Minimal voice output stub that captures spoken phrases."""

	def __init__(self) -> None:
		"""Initialize the phrase log."""
		self.spoken: list[str] = []
		self.clap_detector = None

	def set_clap_detector(self, clap_detector) -> None:
		"""Store the attached clap detector without using real audio."""
		self.clap_detector = clap_detector

	async def speak(self, text: str) -> None:
		"""Capture spoken output for later assertions."""
		self.spoken.append(text)
		await asyncio.sleep(0)

	async def stop(self) -> None:
		"""Provide the shutdown hook expected by the orchestrator."""
		await asyncio.sleep(0)


class FakeBrain:
	"""Minimal brain stub that returns a canned answer."""

	def __init__(self) -> None:
		"""Initialize call tracking."""
		self.thoughts: list[str] = []
		self.reset_called = False

	async def think(self, text: str) -> str:
		"""Record the request and return a deterministic response."""
		self.thoughts.append(text)
		await asyncio.sleep(0)
		if "capital of france" in text.lower():
			return "The capital of France is Paris."
		return "Test response."

	async def reset(self) -> None:
		"""Record that a reset was requested."""
		self.reset_called = True
		await asyncio.sleep(0)


class FakeClapDetector:
	"""Clap detector stub that avoids real microphone access."""

	def __init__(self) -> None:
		"""Initialize lifecycle flags."""
		self.started = False
		self.stopped = False
		self.paused = False

	async def start(self, callback) -> None:
		"""Pretend to start monitoring."""
		self.started = True
		self.callback = callback

	def stop(self) -> None:
		"""Pretend to stop monitoring."""
		self.stopped = True

	def pause_clap_detection(self) -> None:
		"""Pretend to pause monitoring during TTS."""
		self.paused = True

	def resume_clap_detection(self) -> None:
		"""Pretend to resume monitoring after TTS."""
		self.paused = False


async def main() -> None:
	"""Exercise the wake flow end to end with deterministic fakes."""
	original_timeout = settings.AUTO_SLEEP_TIMEOUT_SECONDS
	original_interval = settings.AUTO_SLEEP_CHECK_INTERVAL_SECONDS
	settings.AUTO_SLEEP_TIMEOUT_SECONDS = 1
	settings.AUTO_SLEEP_CHECK_INTERVAL_SECONDS = 0.05

	voice_input = FakeVoiceInputPipeline(["what is the capital of France?"])
	voice_output = FakeVoiceOutputPipeline()
	brain = FakeBrain()
	orchestrator = WakeOrchestrator(voice_input, voice_output, brain)
	fake_clap = FakeClapDetector()
	orchestrator.clap_detector = fake_clap
	voice_output.set_clap_detector(fake_clap)

	try:
		await orchestrator.start()
		assert orchestrator.is_active is True
		assert fake_clap.started is True

		handled = await orchestrator.process_transcription("go to sleep")
		assert handled is True
		assert orchestrator.is_standby is True
		assert settings.WAKE_SLEEP_PHRASE in voice_output.spoken

		await orchestrator.on_clap_detected()
		assert orchestrator.is_active is True
		assert voice_output.spoken[-2] == settings.WAKE_CONFIRMATION_PHRASE
		assert voice_output.spoken[-1] == "The capital of France is Paris."
		assert brain.thoughts[-1] == "what is the capital of France?"

		await orchestrator.process_transcription("standby")
		assert orchestrator.is_standby is True

		await orchestrator.process_transcription("hey araxon what is the capital of France?")
		assert orchestrator.is_active is True
		assert voice_output.spoken[-2] == settings.WAKE_CONFIRMATION_PHRASE
		assert voice_output.spoken[-1] == "The capital of France is Paris."

		orchestrator.standby_manager.reset_sleep_timer()
		orchestrator.standby_manager._last_interaction = time.monotonic() - 2
		await asyncio.sleep(0.15)
		assert orchestrator.is_standby is True

		logger.info("[ACTIVE] Wake flow smoke test passed.")
	finally:
		await orchestrator.stop()
		settings.AUTO_SLEEP_TIMEOUT_SECONDS = original_timeout
		settings.AUTO_SLEEP_CHECK_INTERVAL_SECONDS = original_interval


if __name__ == "__main__":
	asyncio.run(main())