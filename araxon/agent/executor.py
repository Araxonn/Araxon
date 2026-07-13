"""Execute planned steps using ARAXON tools with optional narration."""

from __future__ import annotations

import asyncio
import time
from typing import Callable, List

from araxon.agent.tools import ARAXON_TOOL_DICT
from araxon.voice.voice_output import VoiceOutputPipeline
from araxon.core.config import settings
from araxon.core.logger import logger


class TaskExecutor:
    """Execute a sequence of steps using registered ARAXON tools.

    Each step is a dict with at least: step_number, tool_name, input, reason.
    The executor populates each step with a `result` key after running the tool.
    """

    def __init__(self, voice_output: VoiceOutputPipeline, ui_bridge=None) -> None:
        """Create a TaskExecutor bound to a `VoiceOutputPipeline`.

        Args:
            voice_output: voice pipeline for narration.
            ui_bridge: UI bridge for sending agent steps to frontend.
        """
        self.voice_output = voice_output
        self.ui_bridge = ui_bridge
        self._interrupted = False
        self._is_running = False

    async def execute(self, steps: List[dict], on_step_complete: Callable = None) -> List[dict]:
        """Execute the provided steps sequentially and return completed steps.

        Calls `on_step_complete(step)` after each step if provided.
        Respects `settings.AGENT_NARRATE_STEPS` and `settings.AGENT_STEP_DELAY_SECONDS`.
        """
        self._interrupted = False
        self._is_running = True
        completed: List[dict] = []

        for step in steps:
            if self._interrupted:
                logger.info("[EXECUTOR] Interrupted before starting next step.")
                break

            step_num = step.get("step_number")
            tool_name = step.get("tool_name")
            input_data = step.get("input")
            reason = step.get("reason")

            start_time = time.monotonic()
            logger.info(f"[EXECUTOR] Starting step {step_num}: tool={tool_name}, reason={reason}")

            # STEP 11: Send agent step running status to UI
            if self.ui_bridge:
                await self.ui_bridge.send_agent_step({
                    "step_number": step_num,
                    "description": reason,
                    "status": "running",
                    "done": False,
                    "percent": 25,
                })

            if settings.AGENT_NARRATE_STEPS:
                try:
                    await self.voice_output.speak(f"Step {step_num}: {reason}")
                except Exception as exc:
                    logger.warning(f"Voice narration failed: {exc}")

            tool = ARAXON_TOOL_DICT.get(tool_name)
            result = "Tool not found."
            if tool:
                try:
                    # All tools are async callables
                    result = await tool(input_data)
                except Exception as exc:
                    logger.error(f"[EXECUTOR] Tool {tool_name} raised: {exc}")
                    result = f"Error executing tool {tool_name}: {exc}"

            elapsed = time.monotonic() - start_time
            step["result"] = result
            step["elapsed_seconds"] = elapsed
            completed.append(step)
            logger.info(f"[EXECUTOR] Completed step {step_num}: result={str(result)[:200]} in {elapsed:.2f}s")

            # STEP 11: Send agent step done status to UI
            if self.ui_bridge:
                await self.ui_bridge.send_agent_step({
                    "step_number": step_num,
                    "description": reason,
                    "status": "done",
                    "done": True,
                    "percent": 100,
                    "result": str(result)[:500],
                })

            if on_step_complete:
                try:
                    await asyncio.sleep(0)
                    on_step_complete(step)
                except Exception:
                    pass

            # Delay between steps and interruption check
            await asyncio.sleep(settings.AGENT_STEP_DELAY_SECONDS)
            if self._interrupted:
                logger.info("[EXECUTOR] Interrupted after completing step, stopping.")
                break

        self._is_running = False
        return completed

    def interrupt(self) -> None:
        """Signal the executor to stop after the current step completes."""
        logger.info("[EXECUTOR] Interrupt requested.")
        self._interrupted = True

    def reset(self) -> None:
        """Reset the internal interrupted flag to allow new executions."""
        self._interrupted = False

    @property
    def is_running(self) -> bool:
        """Return True while the executor is actively running steps."""
        return self._is_running
