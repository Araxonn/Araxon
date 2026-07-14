"""Unified wake system orchestration for ARAXON."""

from __future__ import annotations

import asyncio

from araxon.automation.automation_router import AutomationRouter
from araxon.internet.internet_router import InternetRouter
from araxon.vision.vision_router import VisionRouter
from araxon.ai.brain import ARAXONBrain
from araxon.core.config import settings
from araxon.core.logger import logger
from araxon.voice.voice_input import VoiceInputPipeline
from araxon.voice.voice_output import VoiceOutputPipeline
from araxon.agent.agent_controller import AgentController

from .clap_detector import ClapDetector
from .standby import StandbyManager
from .wake_word import WakeWordDetector


class WakeOrchestrator:
	"""Coordinate clap wake, wake words, standby, and spoken responses."""

	def __init__(
		self,
		voice_input: VoiceInputPipeline,
		voice_output: VoiceOutputPipeline,
		brain: ARAXONBrain,
		automation_router: AutomationRouter | None = None,
		agent_controller: AgentController | None = None,
		internet_router: InternetRouter | None = None,
		vision_router: VisionRouter | None = None,
	) -> None:
		"""Bind the voice pipelines, brain, and wake subsystem components."""
		self.voice_input = voice_input
		self.voice_output = voice_output
		self.brain = brain
		self.automation_router = automation_router
		self.internet_router = internet_router
		self.vision_router = vision_router
		self.clap_detector = ClapDetector()
		self.wake_word_detector = WakeWordDetector()
		self.standby_manager = StandbyManager()
		self.voice_output.set_clap_detector(self.clap_detector)
		self.agent_controller = agent_controller
		self._auto_sleep_task: asyncio.Task | None = None
		self._started = False

	@property
	def is_active(self) -> bool:
		"""Return True when ARAXON is actively listening and responding."""
		return self.standby_manager.is_active()

	@property
	def is_standby(self) -> bool:
		"""Return True when ARAXON is in standby mode."""
		return self.standby_manager.is_standby()

	async def start(self) -> None:
		"""Start clap monitoring, auto-sleep monitoring, and active wake state."""
		if self._started:
			logger.info("[ACTIVE] Wake orchestrator is already running.")
			return

		self.standby_manager.activate()
		await self.clap_detector.start(self.on_clap_detected)
		self._auto_sleep_task = asyncio.create_task(self.standby_manager.start_auto_sleep_monitor())
		self._started = True
		logger.info("[ACTIVE] Wake system online.")

	async def stop(self) -> None:
		"""Stop wake monitoring tasks and release their resources cleanly."""
		self.clap_detector.stop()
		self.standby_manager.stop()

		if self._auto_sleep_task is not None:
			self._auto_sleep_task.cancel()
			try:
				await self._auto_sleep_task
			except asyncio.CancelledError:
				pass
			finally:
				self._auto_sleep_task = None

		self._started = False
		logger.info(f"[{ 'STANDBY' if self.is_standby else 'ACTIVE' }] Wake system stopped.")

	async def on_clap_detected(self) -> None:
		"""Wake ARAXON from standby when the clap detector confirms a double clap."""
		try:
			if self.is_standby:
				await self._wake_up()
			else:
				logger.info("[ACTIVE] Clap detected but ARAXON is already active, ignoring.")
		except Exception as exc:
			logger.error(f"[ACTIVE] Clap wake handling failed: {exc}")

	async def _wake_up(self, command_text: str = "") -> None:
		"""Activate ARAXON, confirm wake, and optionally process a command."""
		self.standby_manager.activate()
		await self.voice_output.speak(settings.WAKE_CONFIRMATION_PHRASE)

		if command_text:
			await self.run_conversation_turn(command_text)
			return

		try:
			heard_text = await self.voice_input.listen_and_transcribe()
			if heard_text:
				await self.run_conversation_turn(heard_text)
			else:
				self.standby_manager.reset_sleep_timer()
		except Exception as exc:
			logger.error(f"[ACTIVE] Wake-up listen cycle failed: {exc}")

	async def process_transcription(self, text: str) -> bool:
		"""Handle wake commands, sleep commands, and reset commands from transcriptions."""
		try:
			if not text:
				return False

			if self.is_standby:
				if not self.wake_word_detector.check(text, state_label="[STANDBY]"):
					return False

				command_text = self.wake_word_detector.extract_command(text, state_label="[STANDBY]")
				await self._wake_up(command_text)
				return True

			# Interrupt voice commands (stop, cancel, abort, never mind)
			lowered = text.strip().lower()
			for trig in ("stop", "cancel", "abort", "never mind"):
				if trig in lowered:
					if self.agent_controller is not None:
						await self.agent_controller.interrupt()
						return True
					break

			if self.wake_word_detector.is_sleep_command(text):
				await self.voice_output.speak(settings.WAKE_SLEEP_PHRASE)
				self.standby_manager.sleep("sleep command")
				return True

			if self.wake_word_detector.is_reset_command(text):
				await self.brain.reset()
				await self.voice_output.speak("Memory cleared. Starting fresh.")
				return True

			return False
		except Exception as exc:
			logger.error(f"[ACTIVE] Wake transcription handling failed: {exc}")
			return False

	async def run_conversation_turn(self, text: str) -> None:
		"""Run one full think-and-speak response cycle and refresh sleep timing."""
		try:
			if self.brain.ui_bridge:
				await self.brain.ui_bridge.send_transcript("user", text)

			# If an AgentController exists, determine whether this text should
			# be handled by the autonomous agent instead of the automation router.
			if self.agent_controller is not None and await self.agent_controller.is_agent_task(text):
				await self.voice_output.speak("On it. Let me work on that.")
				# Run agent in background so the voice loop remains responsive
				asyncio.create_task(self.agent_controller.run(text))
				return

			if self.automation_router is not None:
				automation_result = await self.automation_router.route(text)
				if automation_result is not None:
					await self.voice_output.speak(automation_result)
					self.standby_manager.reset_sleep_timer()
					return

			# STEP 9: Internet intelligence routes here
			if self.internet_router is not None:
				internet_result = await self.internet_router.route(text)
				if internet_result is not None:
					await self.voice_output.speak(internet_result)
					self.standby_manager.reset_sleep_timer()
					return

			# STEP 10: Vision system routes here
			if self.vision_router is not None:
				vision_result = await self.vision_router.route(text)
				if vision_result is not None:
					await self.voice_output.speak(vision_result)
					self.standby_manager.reset_sleep_timer()
					return

			response_text = await self.brain.think(text)
			await self.voice_output.speak(response_text)
			self.standby_manager.reset_sleep_timer()
		except Exception as exc:
			logger.error(f"[ACTIVE] Conversation turn failed: {exc}")