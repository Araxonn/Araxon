"""AI-powered visual analysis for ARAXON vision."""

from __future__ import annotations

import asyncio
import time

from PIL import Image

from araxon.core.config import settings
from araxon.core.logger import logger
from araxon.core.utils import sanitize_text
from araxon.ai.brain import ARAXONBrain
from araxon.vision.screenshot import ScreenshotCapture
from araxon.vision.ocr import OCREngine


class VisionAnalyzer:
    """AI-powered analysis of screenshots using ARAXONBrain."""

    def __init__(
        self,
        screenshot_capture: ScreenshotCapture,
        ocr_engine: OCREngine,
        brain: ARAXONBrain,
    ) -> None:
        """Initialize analyzer with vision components and brain.
        
        Args:
            screenshot_capture: ScreenshotCapture instance for capturing.
            ocr_engine: OCREngine instance for text extraction.
            brain: ARAXONBrain instance for AI analysis.
        """
        self.screenshot_capture = screenshot_capture
        self.ocr_engine = ocr_engine
        self.brain = brain
        logger.info(
            "[VISION] Vision analyzer initialized. "
            f"Max text chars: {settings.VISION_MAX_TEXT_CHARS}"
        )

    async def analyze_screen(self) -> str:
        """Full vision pipeline analysis of current screen.
        
        Process:
        1. Capture screenshot via ScreenshotCapture
        2. Extract text via OCREngine.extract_text()
        3. Trim to VISION_MAX_TEXT_CHARS
        4. Send to ARAXONBrain.think() with analysis prompt
        5. Return AI description string
        
        Returns:
            Natural language description of screen content.
        """
        start_time = time.time()
        try:
            # 1. Capture screenshot
            logger.debug("[VISION] Capturing screenshot for analysis...")
            image = await self.screenshot_capture.capture()
            
            # 2. Extract text via OCR
            logger.debug("[VISION] Extracting text via OCR...")
            ocr_text = await self.ocr_engine.extract_text(image)
            
            # 3. Trim text to max chars
            if len(ocr_text) > settings.VISION_MAX_TEXT_CHARS:
                ocr_text = ocr_text[:settings.VISION_MAX_TEXT_CHARS]
                logger.debug(
                    f"[VISION] Trimmed OCR text to {settings.VISION_MAX_TEXT_CHARS} chars"
                )
            
            # Sanitize text for LiteLLM
            ocr_text = sanitize_text(ocr_text)
            
            if not ocr_text:
                logger.warning("[VISION] No OCR text extracted from screen")
                return "I couldn't read any text from your screen at the moment."
            
            # 4. Send to brain for analysis with timeout
            prompt = (
                f"You are ARAXON analyzing the user's screen. "
                f"Here is the text currently visible on screen:\n\n{ocr_text}\n\n"
                f"Describe what the user is working on in 2-3 natural spoken sentences. "
                f"Be specific and helpful. Start speaking immediately."
            )
            
            # Wrap brain.think with timeout
            try:
                response = await asyncio.wait_for(
                    self.brain.think(prompt),
                    timeout=10.0,
                )
            except asyncio.TimeoutError:
                logger.warning("[VISION] Screen analysis timed out")
                return "Screen analysis is taking too long. Try again."
            
            elapsed = time.time() - start_time
            logger.info(
                f"[VISION] Screen analysis complete in {elapsed:.2f}s. "
                f"OCR text: {len(ocr_text)} chars"
            )
            return response

        except Exception as exc:
            logger.error(f"[VISION] Screen analysis failed: {exc}")
            return "I encountered an error analyzing your screen."

    async def analyze_image(
        self,
        image: Image.Image,
        question: str | None = None,
    ) -> str:
        """Analyze a specific image with optional question.
        
        If question provided: answer specific question about image.
        Otherwise: general description of what is in image.
        
        Args:
            image: PIL Image to analyze.
            question: Optional specific question about the image.
            
        Returns:
            Analysis response string.
        """
        start_time = time.time()
        try:
            # Extract text from image
            logger.debug("[VISION] Extracting text from image for analysis...")
            ocr_text = await self.ocr_engine.extract_text(image)
            
            if len(ocr_text) > settings.VISION_MAX_TEXT_CHARS:
                ocr_text = ocr_text[:settings.VISION_MAX_TEXT_CHARS]
            
            ocr_text = sanitize_text(ocr_text)
            
            # Build prompt
            if question:
                prompt = (
                    f"You are ARAXON. The user is asking you about an image. "
                    f"Here is the text visible in the image:\n\n{ocr_text}\n\n"
                    f"User's question: {question}\n\n"
                    f"Answer the question in 1-2 sentences."
                )
            else:
                prompt = (
                    f"You are ARAXON. Describe what is in this image in 2-3 "
                    f"natural sentences. Here is the text visible: {ocr_text}"
                )
            
            # Get analysis
            response = await asyncio.wait_for(
                self.brain.think(prompt),
                timeout=10.0,
            )
            
            elapsed = time.time() - start_time
            logger.info(f"[VISION] Image analysis complete in {elapsed:.2f}s")
            return response

        except asyncio.TimeoutError:
            logger.warning("[VISION] Image analysis timed out")
            return "Analysis is taking too long. Try again."
        except Exception as exc:
            logger.error(f"[VISION] Image analysis failed: {exc}")
            return "I encountered an error analyzing the image."

    async def find_on_screen(self, target: str) -> dict | None:
        """Search screen for specific text or UI element.
        
        Args:
            target: Text or element to find.
            
        Returns:
            Location dict or None if not found.
        """
        try:
            logger.debug(f"[VISION] Searching screen for '{target}'...")
            
            # Capture and get OCR layout
            image = await self.screenshot_capture.capture()
            location = await self.ocr_engine.find_text_location(image, target)
            
            if location:
                logger.info(f"[VISION] Found '{target}' on screen")
                return location
            else:
                logger.info(f"[VISION] '{target}' not found on screen")
                return None

        except Exception as exc:
            logger.error(f"[VISION] Screen search failed: {exc}")
            return None

    async def read_screen_aloud(self) -> str:
        """Capture screen and extract all visible text.
        
        Returns clean readable version of all text on screen.
        Useful for accessibility — reading documents, articles.
        
        Returns:
            All readable text from screen.
        """
        try:
            logger.debug("[VISION] Reading all text from screen...")
            image = await self.screenshot_capture.capture()
            text = await self.ocr_engine.extract_text(image)
            
            if not text:
                logger.warning("[VISION] No text found on screen")
                return "I couldn't find any readable text on your screen."
            
            logger.info(f"[VISION] Read {len(text)} characters from screen")
            return text

        except Exception as exc:
            logger.error(f"[VISION] Screen read failed: {exc}")
            return "I encountered an error reading your screen."

    async def analyze_error(self) -> str:
        """Specialized analysis for error on screen.
        
        Process:
        1. Capture screen
        2. Extract text
        3. Ask brain specifically about error and fix
        
        Returns:
            Error analysis and fix suggestion string.
        """
        start_time = time.time()
        try:
            logger.debug("[VISION] Analyzing error on screen...")
            
            # Capture and extract
            image = await self.screenshot_capture.capture()
            ocr_text = await self.ocr_engine.extract_text(image)
            
            if len(ocr_text) > settings.VISION_MAX_TEXT_CHARS:
                ocr_text = ocr_text[:settings.VISION_MAX_TEXT_CHARS]
            
            ocr_text = sanitize_text(ocr_text)
            
            if not ocr_text:
                return "I couldn't read any error message from your screen."
            
            # Ask brain for error analysis
            prompt = (
                f"You are ARAXON analyzing an error on the user's screen. "
                f"Here is the text visible on screen:\n\n{ocr_text}\n\n"
                f"If there is an error or problem visible, identify it and suggest "
                f"a fix in 2 sentences. If no error is visible, say so."
            )
            
            response = await asyncio.wait_for(
                self.brain.think(prompt),
                timeout=10.0,
            )
            
            elapsed = time.time() - start_time
            logger.info(f"[VISION] Error analysis complete in {elapsed:.2f}s")
            return response

        except asyncio.TimeoutError:
            logger.warning("[VISION] Error analysis timed out")
            return "Analysis is taking too long. Try again."
        except Exception as exc:
            logger.error(f"[VISION] Error analysis failed: {exc}")
            return "I encountered an error analyzing the screen."

    async def compare_screenshots(
        self,
        image1: Image.Image,
        image2: Image.Image,
    ) -> str:
        """Describe what changed between two screenshots.
        
        Args:
            image1: First screenshot (before).
            image2: Second screenshot (after).
            
        Returns:
            Description of changes.
        """
        try:
            logger.debug("[VISION] Comparing screenshots...")
            
            # Extract text from both images
            text1 = await self.ocr_engine.extract_text(image1)
            text2 = await self.ocr_engine.extract_text(image2)
            
            if len(text1) > settings.VISION_MAX_TEXT_CHARS:
                text1 = text1[:settings.VISION_MAX_TEXT_CHARS]
            if len(text2) > settings.VISION_MAX_TEXT_CHARS:
                text2 = text2[:settings.VISION_MAX_TEXT_CHARS]
            
            text1 = sanitize_text(text1)
            text2 = sanitize_text(text2)
            
            # Ask brain to compare
            prompt = (
                f"You are ARAXON. Compare these two screen snapshots and describe "
                f"what changed between them in 2-3 sentences.\n\n"
                f"BEFORE:\n{text1}\n\nAFTER:\n{text2}"
            )
            
            response = await asyncio.wait_for(
                self.brain.think(prompt),
                timeout=10.0,
            )
            
            logger.info("[VISION] Screenshot comparison complete")
            return response

        except asyncio.TimeoutError:
            logger.warning("[VISION] Screenshot comparison timed out")
            return "Comparison is taking too long. Try again."
        except Exception as exc:
            logger.error(f"[VISION] Screenshot comparison failed: {exc}")
            return "I encountered an error comparing the screenshots."
