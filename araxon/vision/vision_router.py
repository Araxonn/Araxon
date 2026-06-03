"""Voice command router for ARAXON vision system."""

from __future__ import annotations

from araxon.core.logger import logger
from araxon.vision.vision_pipeline import VisionPipeline


class VisionRouter:
    """Routes vision-related voice commands to appropriate handlers."""

    def __init__(self, vision_pipeline: VisionPipeline | None = None) -> None:
        """Initialize vision router with optional pipeline.
        
        Args:
            vision_pipeline: Optional VisionPipeline instance. If None, creates new one.
        """
        self.vision_pipeline = vision_pipeline if vision_pipeline is not None else VisionPipeline()
        logger.info("[VISION] Vision router initialized")

    async def initialize(self) -> None:
        """Initialize the vision pipeline."""
        await self.vision_pipeline.initialize()
        logger.info("[VISION] Vision router online")

    async def shutdown(self) -> None:
        """Shutdown the vision pipeline."""
        await self.vision_pipeline.shutdown()
        logger.info("[VISION] Vision router offline")

    def _extract_target_from_command(self, text: str, trigger: str) -> str:
        """Extract target text after trigger phrase.
        
        Args:
            text: Full command text.
            trigger: Trigger phrase to look for.
            
        Returns:
            Text after trigger, or empty string if not found.
        """
        if trigger not in text:
            return ""
        
        # Split and get everything after the trigger
        parts = text.split(trigger, 1)
        if len(parts) > 1:
            return parts[1].strip()
        return ""

    async def route(self, text: str) -> str | None:
        """Route voice command to appropriate vision handler.
        
        Routing rules:
        
        WHAT DO YOU SEE:
          "what do you see", "what's on my screen", "what is on screen",
          "look at my screen", "analyze screen"
          → VisionPipeline.what_do_you_see()
        
        READ SCREEN:
          "read my screen", "read the screen", "read what's on screen",
          "read this page"
          → VisionPipeline.read_screen()
        
        SCREENSHOT:
          "take a screenshot", "screenshot", "capture screen",
          "take a picture of screen"
          → VisionPipeline.take_screenshot()
        
        ERROR ANALYSIS:
          "what's the error", "analyze the error", "what went wrong",
          "debug this", "fix this error"
          → VisionPipeline.analyze_error()
        
        FIND ON SCREEN:
          "find", "where is", "locate"
          Extract target and pass to VisionPipeline.find()
        
        QUESTION ABOUT SCREEN:
          "what file", "what tab", "what is open", "what am I looking at",
          "what's open"
          → VisionPipeline.capture_and_analyze(text)
        
        Args:
            text: Voice command text.
            
        Returns:
            Result string if handled, None if not a vision command.
        """
        if not text:
            return None

        text_lower = text.strip().lower()

        # WHAT DO YOU SEE
        what_see_triggers = [
            "what do you see",
            "what's on my screen",
            "what is on screen",
            "look at my screen",
            "analyze screen",
            "analyze my screen",
            "what's visible",
            "what do i see",
        ]
        if any(trigger in text_lower for trigger in what_see_triggers):
            logger.info("[VISION] Route: analyze screen")
            return await self.vision_pipeline.what_do_you_see()

        # READ SCREEN
        read_triggers = [
            "read my screen",
            "read the screen",
            "read what's on screen",
            "read this page",
            "read screen",
            "read to me",
        ]
        if any(trigger in text_lower for trigger in read_triggers):
            logger.info("[VISION] Route: read screen")
            return await self.vision_pipeline.read_screen()

        # SCREENSHOT
        screenshot_triggers = [
            "take a screenshot",
            "screenshot",
            "capture screen",
            "take a picture of screen",
            "take screenshot",
        ]
        if any(trigger in text_lower for trigger in screenshot_triggers):
            logger.info("[VISION] Route: take screenshot")
            return await self.vision_pipeline.take_screenshot()

        # ERROR ANALYSIS
        error_triggers = [
            "what's the error",
            "what is the error",
            "analyze the error",
            "what went wrong",
            "debug this",
            "fix this error",
            "error analysis",
            "there's an error",
            "there is an error",
        ]
        if any(trigger in text_lower for trigger in error_triggers):
            logger.info("[VISION] Route: analyze error")
            return await self.vision_pipeline.analyze_error()

        # FIND ON SCREEN
        find_triggers = ["find ", "where is ", "locate "]
        for trigger in find_triggers:
            if trigger in text_lower:
                target = self._extract_target_from_command(text_lower, trigger)
                if target:
                    logger.info(f"[VISION] Route: find '{target}'")
                    return await self.vision_pipeline.find(target)

        # QUESTION ABOUT SCREEN
        question_triggers = [
            "what file",
            "what tab",
            "what is open",
            "what am i looking at",
            "what's open",
            "what program",
            "what app",
        ]
        if any(trigger in text_lower for trigger in question_triggers):
            logger.info(f"[VISION] Route: answer question about screen")
            return await self.vision_pipeline.capture_and_analyze(text)

        # Not a vision command
        return None
