"""Master agent controller coordinating planning, execution, and graph agent."""

from __future__ import annotations

import asyncio
from typing import List

from araxon.agent.planner import TaskPlanner
from araxon.agent.executor import TaskExecutor
from araxon.agent.graph import ARAxonAgentGraph
from araxon.core.config import settings
from araxon.core.logger import logger
from araxon.voice.voice_output import VoiceOutputPipeline


class AgentController:
    """Top-level controller ARAXON uses to run autonomous tasks.

    It supports three modes via `settings.AGENT_MODE`: "graph", "plan", and "auto".
    """

    def __init__(self, voice_output: VoiceOutputPipeline, ui_bridge=None) -> None:
        """Create controller and bind planner, executor, and optional graph.

        Args:
            voice_output: voice pipeline used for narration and notifications.
            ui_bridge: UI bridge for sending agent steps to frontend.
        """
        self.voice_output = voice_output
        self.ui_bridge = ui_bridge
        self.planner = TaskPlanner()
        self.executor = TaskExecutor(voice_output, ui_bridge)
        self.graph = ARAxonAgentGraph()
        self._running_task: asyncio.Task | None = None

    async def run(self, goal: str) -> str:
        """Run the agent according to `settings.AGENT_MODE` and return final text.

        This method is async but callers should schedule it with
        `asyncio.create_task()` to avoid blocking the voice loop.
        """
        mode = settings.AGENT_MODE or "graph"
        logger.info(f"[CONTROLLER] Agent run requested in mode={mode} for goal: {goal}")

        if mode == "graph":
            result = await self.graph.run(goal)
            await self.voice_output.speak("Task complete.")
            return result

        if mode == "plan":
            steps = await self.planner.plan(goal)
            summary = self.planner.format_plan_for_speech(steps)
            await self.voice_output.speak(summary)
            completed = await self.executor.execute(steps)
            await self.voice_output.speak("Task complete.")
            return "; ".join([s.get("result", "") for s in completed])

        # auto mode: decide based on planner heuristics
        if mode == "auto":
            steps = await self.planner.plan(goal)
            if len(steps) >= 3:
                result = await self.graph.run(goal)
                await self.voice_output.speak("Task complete.")
                return result
            else:
                summary = self.planner.format_plan_for_speech(steps)
                await self.voice_output.speak(summary)
                completed = await self.executor.execute(steps)
                await self.voice_output.speak("Task complete.")
                return "; ".join([s.get("result", "") for s in completed])

        # Fallback to graph
        result = await self.graph.run(goal)
        await self.voice_output.speak("Task complete.")
        return result

    async def interrupt(self) -> None:
        """Interrupt any currently running execution or graph loop."""
        logger.info("[CONTROLLER] Interrupt requested.")
        try:
            self.executor.interrupt()
        except Exception:
            pass
        try:
            self.graph.stop()
        except Exception:
            pass
        await self.voice_output.speak("Stopping current task.")

    async def is_agent_task(self, text: str) -> bool:
        """Return True when a text is likely an agent task; delegates to planner."""
        return await self.planner.is_agent_task(text)

    @property
    def is_running(self) -> bool:
        """Return True when an internal executor is running a task."""
        return self.executor.is_running
