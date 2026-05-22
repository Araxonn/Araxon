"""Task planner for ARAXON: breaks goals into ordered tool-using steps."""

from __future__ import annotations

import json
import asyncio
from typing import List

from araxon.ai.brain import ARAXONBrain
from araxon.ai.personality import get_system_prompt
from araxon.core.config import settings
from araxon.core.logger import logger


class TaskPlanner:
    """Break complex goals into a concise sequence of steps using ARAXON's LLM.

    Each step must specify a `step_number`, `tool_name`, `input`, and `reason`.
    """

    def __init__(self, brain: ARAXONBrain | None = None) -> None:
        """Create a TaskPlanner bound to an `ARAXONBrain` instance.

        Args:
            brain: optional ARAXONBrain; if omitted a new instance will be created.
        """
        self.brain = brain or ARAXONBrain()

    async def plan(self, goal: str) -> List[dict]:
        """Return a list of step dicts parsed from the LLM's JSON output.

        The LLM is instructed to use at most `settings.AGENT_MAX_STEPS` steps and
        to only reference a single tool per step.
        """
        system_prompt = get_system_prompt()
        planner_prompt = (
            f"You are a task planner for ARAXON AI OS. Break the following goal into clear sequential steps. "
            f"Each step must use exactly one of these tools: web_search, open_website, open_application, "
            f"run_terminal_command, read_file, write_file, remember_fact, recall_memory, take_screenshot, get_page_content. "
            f"Return a JSON list of steps, each with: step_number, tool_name, input, reason. "
            f"Maximum {settings.AGENT_MAX_STEPS} steps. Be concise and practical.\n\nGoal: {goal}"
        )

        prompt = system_prompt + "\n" + planner_prompt

        logger.info(f"[PLANNER] Generating plan for goal: {goal}")
        response = await self.brain.think(prompt)

        # Try parse JSON, retry once if malformed
        for attempt in range(2):
            try:
                parsed = json.loads(response)
                if isinstance(parsed, list):
                    logger.info(f"[PLANNER] Plan parsed with {len(parsed)} steps.")
                    return parsed
                else:
                    raise ValueError("Parsed plan is not a list")
            except Exception as exc:
                logger.warning(f"[PLANNER] Failed to parse plan (attempt {attempt+1}): {exc}")
                if attempt == 0:
                    # ask the model to return only JSON
                    response = await self.brain.think(system_prompt + "\nPlease return ONLY the JSON list of steps.")
                else:
                    logger.error("[PLANNER] Giving up parsing plan; returning empty list.")
                    return []

    async def is_agent_task(self, text: str) -> bool:
        """Return True when the input text looks like it needs multi-step autonomous work."""
        if not text:
            return False
        lowered = text.lower()
        triggers = [
            "create a",
            "build me",
            "set up",
            "research and",
            "find and",
            "go to",
            "automatically",
            "for me",
            "can you do",
            "i need you to",
        ]
        for t in triggers:
            if t in lowered:
                return True
        return False

    def format_plan_for_speech(self, steps: List[dict]) -> str:
        """Return a short spoken summary of the plan steps."""
        if not steps:
            return "I don't have any steps planned."
        count = len(steps)
        parts = [f"I'll do this in {count} steps."]
        first_actions = []
        for i, s in enumerate(steps[:3], start=1):
            reason = s.get("reason") or s.get("tool_name") or "perform a step"
            first_actions.append(f"Step {i}: {reason}")
        parts.append(" then ".join(first_actions))
        summary = " ".join(parts)
        logger.info(f"[PLANNER] Plan summary: {summary}")
        return summary
