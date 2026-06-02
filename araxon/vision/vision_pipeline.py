"""Unified vision pipeline for ARAXON."""

from __future__ import annotations

from PIL import Image

from araxon.core.config import settings
from araxon.core.logger import logger
from araxon.ai.brain import ARAXONBrain
from araxon.vision.screenshot import ScreenshotCapture
from araxon.vision.ocr import OCREngine
from araxon.vision.analyzer import VisionAnalyzer


class VisionPipeline:
    """Master vision controller combining all vision components."""

    def __init__(self, brain: ARAXONBrain | None = None) -> None:
        """Initialize vision pipeline with all components.
        
        Args:
            brain: ARAXONBrain instance. If None, creates a new one.
        """
        self.screenshot_capture = ScreenshotCapture()
        self.ocr_engine = OCREngine()
        self.brain = brain if brain is not None else ARAXONBrain()
        self.analyzer = VisionAnalyzer(
            self.screenshot_capture,
            self.ocr_engine,
            self.brain,
        )
        logger.info("[VISION] Vision pipeline initialized")

    async def initialize(self) -> None:
        """Initialize all vision components and verify setup.
        
        - Verifies Tesseract is available
        - Creates screenshot directory
        - Logs vision system online
        """
        try:
            # Verify Tesseract is available (optional but logged)
            if not self.ocr_engine._tesseract_available:
                logger.warning(
                    "[VISION] Tesseract OCR not available. "
                    "Vision operations will work but OCR-dependent features "
                    "will be unavailable."
                )
            
            # Ensure screenshot directory exists
            self.screenshot_capture._ensure_screenshot_directory()
            
            logger.info("[VISION] Vision system online and ready")
        except Exception as exc:
            logger.error(f"[VISION] Vision initialization failed: {exc}")
            raise

    async def what_do_you_see(self) -> str:
        """Main voice command handler: describe current screen.
        
        Calls VisionAnalyzer.analyze_screen() to provide natural
        description of what's currently on the user's screen.
        
        Returns:
            Spoken description of current screen.
        """
        return await self.analyzer.analyze_screen()

    async def read_screen(self) -> str:
        """Read all visible text on screen aloud.
        
        Calls VisionAnalyzer.read_screen_aloud() to extract and return
        all readable text from the current screen.
        
        Returns:
            Text string for speaking.
        """
        return await self.analyzer.read_screen_aloud()

    async def take_screenshot(
        self,
        filename: str | None = None,
    ) -> str:
        """Capture and save screenshot.
        
        Args:
            filename: Optional custom filename.
            
        Returns:
            Confirmation message with path.
        """
        try:
            path = await self.screenshot_capture.capture_and_save(filename)
            logger.info(f"[VISION] Screenshot saved: {path}")
            return f"Screenshot saved to {path}"
        except Exception as exc:
            logger.error(f"[VISION] Screenshot capture failed: {exc}")
            return "Failed to capture screenshot."

    async def analyze_error(self) -> str:
        """Analyze visible error on screen and suggest fix.
        
        Returns:
            Fix suggestion string.
        """
        return await self.analyzer.analyze_error()

    async def find(self, target: str) -> str:
        """Find specific text or element on screen.
        
        Converts pixel coordinates to screen region names for
        natural spoken language response.
        
        Args:
            target: Text or element to find.
            
        Returns:
            Location description using natural language.
        """
        location = await self.analyzer.find_on_screen(target)
        
        if not location:
            return f"I couldn't find {target} on your screen."
        
        # Convert pixel coordinates to screen region names
        x = location.get("x", 0)
        y = location.get("y", 0)
        width = location.get("width", 0)
        height = location.get("height", 0)
        confidence = location.get("confidence", 0.0)
        
        # Simple screen region mapping
        # Assume common screen size ~1920x1080
        region_x = "left" if x < 640 else "center" if x < 1280 else "right"
        region_y = "top" if y < 360 else "middle" if y < 720 else "bottom"
        
        return (
            f"I found {target} in the {region_y} {region_x} area of your screen "
            f"({confidence:.0%} confidence)."
        )

    async def capture_and_analyze(
        self,
        question: str,
    ) -> str:
        """Capture screen and answer specific question about it.
        
        Example: "what file is open in VS Code?"
        
        Args:
            question: Question to answer about the screen.
            
        Returns:
            Answer string.
        """
        try:
            image = await self.screenshot_capture.capture()
            return await self.analyzer.analyze_image(image, question=question)
        except Exception as exc:
            logger.error(f"[VISION] Capture and analyze failed: {exc}")
            return "I encountered an error analyzing your screen."

    async def shutdown(self) -> None:
        """Clean shutdown of all vision components."""
        try:
            logger.info("[VISION] Vision system shutting down")
            # Vision components don't need explicit cleanup currently
        except Exception as exc:
            logger.error(f"[VISION] Shutdown failed: {exc}")
