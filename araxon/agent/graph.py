"""A simplified ReAct-style agent loop that coordinates LLM actions and tool calls.

This implementation provides the required interface without mandating an installed
`langgraph` package; it respects `settings.AGENT_MAX_ITERATIONS` and returns
plain string results suitable for spoken feedback.
"""

from __future__ import annotations

import asyncio
import json
import time
from typing import Callable

from araxon.ai.brain import ARAXONBrain
from araxon.ai.personality import get_system_prompt
from araxon.agent.tools import ARAXON_TOOL_DICT
from araxon.core.config import settings
from araxon.core.logger import logger


class ARAxonAgentGraph:
    """Run a ReAct-like loop: ask the LLM what to do, execute tools, return final answer.

    This class intentionally avoids tight coupling to `langgraph` while providing
    the run/stream API the rest of ARAXON expects.
    """

    def __init__(self, brain: ARAXONBrain | None = None) -> None:
        """Create the agent graph bound to an `ARAXONBrain`."""
        self.brain = brain or ARAXONBrain()
        self._running = False

    async def run(self, goal: str, system_prompt: str | None = None) -> str:
        """Run the agent loop and return the final assistant answer as a string.

        The loop will perform at most `settings.AGENT_MAX_ITERATIONS` iterations.
        """
        logger.info("[GRAPH] Starting agent graph run.")
        self._running = True
        messages = []
        system_prompt = system_prompt or get_system_prompt()
        user_prompt = (
            f"You are ARAXON. Decide whether to call one of these tools or produce a final answer. "
            f"Tools: {', '.join(list(ARAXON_TOOL_DICT.keys()))}.\nGoal: {goal}\n\n"
            "If you want to call a tool, respond with a JSON object: {\"action\":\"tool_name\", \"input\":\"...\"}. "
            "If you want to finish, respond with a JSON object: {\"final\": \"text answer\"}."
        )

        loop_state = {"history": []}

        for iteration in range(settings.AGENT_MAX_ITERATIONS):
            if not self._running:
                logger.info("[GRAPH] Run stopped by external interrupt.")
                break

            prompt = system_prompt + "\n" + user_prompt + "\n" + json.dumps(loop_state)
            try:
                response = await self.brain.think(prompt)
            except Exception as exc:
                logger.error(f"[GRAPH] LLM failed: {exc}")
                return f"Agent error: {exc}"

            # Try parse JSON directive
            try:
                data = json.loads(response)
            except Exception:
                # If no JSON, treat response as final text
                logger.info("[GRAPH] LLM returned non-JSON, using as final answer.")
                return response

            if isinstance(data, dict) and data.get("final"):
                logger.info("[GRAPH] LLM provided final answer.")
                return data.get("final")

            action = data.get("action")
            action_input = data.get("input")
            if not action or action not in ARAXON_TOOL_DICT:
                logger.warning(f"[GRAPH] Invalid or unknown action: {action}")
                return "Agent provided an invalid action."

            tool = ARAXON_TOOL_DICT[action]
            start = time.monotonic()
            try:
                tool_result = await tool(action_input)
            except Exception as exc:
                tool_result = f"Tool execution error: {exc}"

            elapsed = time.monotonic() - start
            logger.info(f"[GRAPH] Tool {action} returned in {elapsed:.2f}s: {str(tool_result)[:200]}")

            # Append tool result into state and continue
            loop_state["history"].append({"action": action, "input": action_input, "result": str(tool_result)})

        self._running = False
        logger.warning("[GRAPH] Reached maximum iterations without final answer.")
        return "Agent reached iteration limit without a final answer."

    async def stream(self, goal: str, on_token: Callable | None = None) -> str:
        """Run the agent but stream token-like updates via `on_token` callback.

        Note: because ARAXONBrain currently does not support streaming, this emits
        sentence fragments as tokens for caller convenience.
        """
        result = await self.run(goal)
        if on_token:
            for part in result.split("."):
                token = part.strip()
                if token:
                    try:
                        on_token(token + ".")
                        await asyncio.sleep(0)
                    except Exception:
                        pass
        return result

    def stop(self) -> None:
        """Stop a running graph execution cleanly from another task."""
        logger.info("[GRAPH] Stop requested.")
        self._running = False
