"""Screen capture system for ARAXON vision."""

from __future__ import annotations

import asyncio
import base64
import io
from datetime import datetime
from pathlib import Path

from PIL import Image

from araxon.core.config import settings
from araxon.core.logger import logger


class ScreenshotCapture:
    """Fast screen capture using mss library with async support."""

    def __init__(self) -> None:
        """Initialize screen capture with directory creation."""
        self._ensure_screenshot_directory()
        logger.info(
            f"[VISION] Screenshot capture initialized. "
            f"Monitor index: {settings.VISION_MONITOR_INDEX}, "
            f"Format: {settings.SCREENSHOT_FORMAT}, "
            f"Quality: {settings.SCREENSHOT_QUALITY}"
        )

    def _ensure_screenshot_directory(self) -> None:
        """Create screenshot save directory if it doesn't exist."""
        save_path = Path(settings.SCREENSHOT_SAVE_PATH)
        save_path.mkdir(parents=True, exist_ok=True)

    async def capture(self) -> Image.Image:
        """Capture full primary monitor screenshot.
        
        Uses asyncio.to_thread for blocking mss call to avoid blocking
        the async event loop.
        
        Returns:
            PIL Image object of the screen capture.
        """
        def _capture_sync() -> Image.Image:
            try:
                import mss
                
                with mss.mss() as sct:
                    # Monitor index: 1 = primary monitor, 0 = all monitors combined
                    monitor = sct.monitors[settings.VISION_MONITOR_INDEX]
                    screenshot = sct.grab(monitor)
                    # Convert mss screenshot to PIL Image
                    img = Image.frombytes('RGB', screenshot.size, screenshot.rgb)
                    
                    width, height = img.size
                    logger.info(
                        f"[VISION] Captured full screen: {width}x{height} "
                        f"from monitor {settings.VISION_MONITOR_INDEX}"
                    )
                    return img
            except IndexError:
                logger.warning(
                    f"[VISION] Monitor {settings.VISION_MONITOR_INDEX} not found. "
                    f"Falling back to monitor 1."
                )
                import mss
                with mss.mss() as sct:
                    monitor = sct.monitors[1]
                    screenshot = sct.grab(monitor)
                    img = Image.frombytes('RGB', screenshot.size, screenshot.rgb)
                    width, height = img.size
                    logger.info(f"[VISION] Captured full screen: {width}x{height}")
                    return img

        return await asyncio.to_thread(_capture_sync)

    async def capture_region(
        self,
        x: int,
        y: int,
        width: int,
        height: int,
    ) -> Image.Image:
        """Capture specific screen region.
        
        Args:
            x: Left coordinate
            y: Top coordinate
            width: Width of region
            height: Height of region
            
        Returns:
            PIL Image object of the captured region.
        """
        def _capture_region_sync() -> Image.Image:
            import mss
            
            with mss.mss() as sct:
                monitor = {
                    "left": x,
                    "top": y,
                    "width": width,
                    "height": height,
                }
                screenshot = sct.grab(monitor)
                img = Image.frombytes('RGB', screenshot.size, screenshot.rgb)
                logger.info(
                    f"[VISION] Captured region: ({x}, {y}) "
                    f"{width}x{height}"
                )
                return img

        return await asyncio.to_thread(_capture_region_sync)

    async def capture_and_save(
        self,
        filename: str | None = None,
    ) -> str:
        """Capture screen and save to SCREENSHOT_SAVE_PATH.
        
        Auto-generates filename if not provided with format:
        screenshot_{timestamp}.png
        
        Args:
            filename: Optional filename. If not provided, auto-generates.
            
        Returns:
            Path string of saved screenshot.
        """
        if filename is None:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S_%f")[:-3]
            filename = f"screenshot_{timestamp}.{settings.SCREENSHOT_FORMAT}"

        image = await self.capture()
        save_path = Path(settings.SCREENSHOT_SAVE_PATH) / filename
        
        # Save with specified quality if JPEG, else PNG defaults
        if settings.SCREENSHOT_FORMAT.lower() in {"jpg", "jpeg"}:
            image.save(
                save_path,
                format="JPEG",
                quality=settings.SCREENSHOT_QUALITY,
            )
        else:
            image.save(save_path, format="PNG")

        logger.info(f"[VISION] Screenshot saved: {save_path}")
        return str(save_path)

    async def capture_window(
        self,
        window_title: str,
    ) -> Image.Image | None:
        """Attempt to find and capture specific window by title.
        
        Uses pyautogui.getWindowsWithTitle() to locate window.
        Falls back to full screen if window not found.
        
        Args:
            window_title: Title of window to capture.
            
        Returns:
            PIL Image of window or None if capture failed.
        """
        def _capture_window_sync() -> Image.Image | None:
            try:
                import pyautogui
                
                windows = pyautogui.getWindowsWithTitle(window_title)
                if not windows:
                    logger.warning(
                        f"[VISION] Window '{window_title}' not found. "
                        f"Falling back to full screen."
                    )
                    return None

                window = windows[0]
                x, y, width, height = window.left, window.top, window.width, window.height
                
                logger.info(
                    f"[VISION] Found window '{window_title}' at "
                    f"({x}, {y}) {width}x{height}"
                )

                import mss
                with mss.mss() as sct:
                    monitor = {
                        "left": x,
                        "top": y,
                        "width": width,
                        "height": height,
                    }
                    screenshot = sct.grab(monitor)
                    img = Image.frombytes('RGB', screenshot.size, screenshot.rgb)
                    return img

            except Exception as exc:
                logger.error(f"[VISION] Window capture failed: {exc}")
                return None

        return await asyncio.to_thread(_capture_window_sync)

    @staticmethod
    def image_to_base64(image: Image.Image) -> str:
        """Convert PIL Image to base64 string.
        
        Used for sending to vision AI models.
        
        Args:
            image: PIL Image object.
            
        Returns:
            Base64 encoded string of image.
        """
        buffer = io.BytesIO()
        image.save(buffer, format="PNG")
        buffer.seek(0)
        base64_string = base64.b64encode(buffer.getvalue()).decode('utf-8')
        logger.debug(f"[VISION] Converted image to base64 ({len(base64_string)} chars)")
        return base64_string
