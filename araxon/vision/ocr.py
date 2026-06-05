"""OCR text extraction from images for ARAXON vision."""

from __future__ import annotations

import asyncio
from pathlib import Path

from PIL import Image, ImageEnhance, ImageOps

from araxon.core.config import settings
from araxon.core.logger import logger


class OCREngine:
    """Text extraction from images using pytesseract."""

    def __init__(self) -> None:
        """Initialize OCR engine with Tesseract configuration."""
        self._tesseract_available = False
        self._initialize_tesseract()

    def _initialize_tesseract(self) -> None:
        """Configure pytesseract with Tesseract path."""
        try:
            import pytesseract
            
            # Set Tesseract executable path
            pytesseract.pytesseract.tesseract_cmd = settings.TESSERACT_PATH
            
            # Verify Tesseract is available by getting version
            version = pytesseract.get_tesseract_version()
            logger.info(
                f"[VISION] Tesseract OCR initialized: {version}, "
                f"Language: {settings.OCR_LANGUAGE}, "
                f"Min confidence: {settings.OCR_MIN_CONFIDENCE}%"
            )
            self._tesseract_available = True
        except ImportError:
            logger.warning(
                "[VISION] pytesseract not installed. "
                "Install with: pip install pytesseract"
            )
        except FileNotFoundError:
            logger.warning(
                f"[VISION] Tesseract not found at {settings.TESSERACT_PATH}. "
                "Please install from: "
                "https://github.com/UB-Mannheim/tesseract/wiki"
            )
        except Exception as exc:
            logger.warning(f"[VISION] Tesseract initialization failed: {exc}")

    def _check_tesseract(self) -> bool:
        """Check if Tesseract is available, log if not."""
        if not self._tesseract_available:
            logger.warning(
                "[VISION] Tesseract OCR is not installed. "
                "Please install from: "
                "https://github.com/UB-Mannheim/tesseract/wiki"
            )
            return False
        return True

    def preprocess_image(self, image: Image.Image) -> Image.Image:
        """Preprocess image for better OCR accuracy.
        
        - Converts to grayscale
        - Applies contrast enhancement
        - Resizes if too small (min 300px wide)
        
        Args:
            image: PIL Image to preprocess.
            
        Returns:
            Preprocessed PIL Image.
        """
        # Convert to grayscale
        image = ImageOps.grayscale(image)
        
        # Apply contrast enhancement
        enhancer = ImageEnhance.Contrast(image)
        image = enhancer.enhance(1.5)
        
        # Resize if too small for better OCR
        width, height = image.size
        if width < 300:
            scale = 300 / width
            new_size = (int(width * scale), int(height * scale))
            image = image.resize(new_size, Image.Resampling.LANCZOS)
            logger.debug(f"[VISION] Upscaled image to {new_size} for OCR")
        
        return image

    async def extract_text(self, image: Image.Image) -> str:
        """Run OCR on PIL image and extract text.
        
        Filters words below OCR_MIN_CONFIDENCE and cleans output.
        
        Args:
            image: PIL Image to extract text from.
            
        Returns:
            Cleaned extracted text string.
        """
        if not self._check_tesseract():
            return ""

        def _extract_text_sync() -> str:
            import pytesseract
            
            # Preprocess for better accuracy
            processed = self.preprocess_image(image)
            
            # Extract text
            text = pytesseract.image_to_string(
                processed,
                lang=settings.OCR_LANGUAGE,
            )
            
            # Clean output
            text = text.strip()
            text = " ".join(text.split())  # Normalize whitespace
            
            char_count = len(text)
            logger.info(f"[VISION] OCR extracted {char_count} characters")
            return text

        return await asyncio.to_thread(_extract_text_sync)

    async def extract_from_file(self, path: str) -> str:
        """Load image from file path and extract text.
        
        Args:
            path: File path to image.
            
        Returns:
            Extracted text string.
        """
        try:
            image = Image.open(path)
            text = await self.extract_text(image)
            logger.info(f"[VISION] Extracted text from file: {path}")
            return text
        except Exception as exc:
            logger.error(f"[VISION] Failed to extract text from {path}: {exc}")
            return ""

    async def extract_with_layout(self, image: Image.Image) -> dict:
        """Extract structured text data including layout information.
        
        Returns structured extraction with text, words, lines, and confidence.
        
        Args:
            image: PIL Image to extract from.
            
        Returns:
            Dict with keys: text, words, lines, confidence.
        """
        if not self._check_tesseract():
            return {"text": "", "words": [], "lines": [], "confidence": 0.0}

        def _extract_layout_sync() -> dict:
            import pytesseract
            
            # Preprocess for better accuracy
            processed = self.preprocess_image(image)
            
            # Get detailed data
            data = pytesseract.image_to_data(
                processed,
                lang=settings.OCR_LANGUAGE,
                output_type=pytesseract.Output.DICT,
            )
            
            # Extract full text
            text = pytesseract.image_to_string(processed, lang=settings.OCR_LANGUAGE)
            text = text.strip()
            
            # Filter words by confidence
            words = []
            for i, conf in enumerate(data['conf']):
                if int(conf) >= settings.OCR_MIN_CONFIDENCE:
                    word = data['text'][i].strip()
                    if word:
                        words.append(word)
            
            # Build lines
            lines = text.split('\n')
            lines = [line.strip() for line in lines if line.strip()]
            
            # Calculate average confidence
            confidences = [int(c) for c in data['conf'] if int(c) > 0]
            avg_confidence = sum(confidences) / len(confidences) if confidences else 0.0
            
            result = {
                "text": text,
                "words": words,
                "lines": lines,
                "confidence": avg_confidence / 100.0,  # Normalize to 0-1
            }
            
            logger.info(
                f"[VISION] Layout extraction: {len(words)} words, "
                f"{len(lines)} lines, {avg_confidence:.1f}% avg confidence"
            )
            return result

        return await asyncio.to_thread(_extract_layout_sync)

    async def find_text_location(
        self,
        image: Image.Image,
        search_text: str,
    ) -> dict | None:
        """Find where specific text appears in image.
        
        Args:
            image: PIL Image to search.
            search_text: Text to find.
            
        Returns:
            Dict with x, y, width, height, confidence or None if not found.
        """
        if not self._check_tesseract():
            return None

        def _find_text_sync() -> dict | None:
            import pytesseract
            
            # Preprocess for better accuracy
            processed = self.preprocess_image(image)
            
            # Get detailed data
            data = pytesseract.image_to_data(
                processed,
                lang=settings.OCR_LANGUAGE,
                output_type=pytesseract.Output.DICT,
            )
            
            search_lower = search_text.lower()
            
            # Search for matching text
            for i, text in enumerate(data['text']):
                if search_lower in text.lower():
                    confidence = int(data['conf'][i])
                    if confidence >= settings.OCR_MIN_CONFIDENCE:
                        result = {
                            "x": int(data['left'][i]),
                            "y": int(data['top'][i]),
                            "width": int(data['width'][i]),
                            "height": int(data['height'][i]),
                            "confidence": confidence / 100.0,
                            "text": text,
                        }
                        logger.info(
                            f"[VISION] Found '{search_text}' at "
                            f"({result['x']}, {result['y']}) "
                            f"{result['confidence']:.1%} confidence"
                        )
                        return result
            
            logger.info(f"[VISION] Text '{search_text}' not found in image")
            return None

        return await asyncio.to_thread(_find_text_sync)
