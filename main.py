"""
ARAXON Core Entry Point.

Initializes the ARAXON operating system, loads configuration,
and prepares all subsystems for operation.
"""

import sys
import asyncio
import time
from pathlib import Path

# Ensure project root is in path
sys.path.insert(0, str(Path(__file__).parent))

# First, create all necessary directories
def ensure_directories():
    """Ensure all required directories exist."""
    dirs = [
        "araxon/core",
        "araxon/ai",
        "araxon/voice",
        "araxon/memory",
        "araxon/vision",
        "araxon/automation",
        "araxon/agent",
        "araxon/internet",
        "araxon/ui",
        "config",
        "logs",
        "models",
        "data",
    ]
    for d in dirs:
        Path(d).mkdir(parents=True, exist_ok=True)


# Create directories first before importing
ensure_directories()

from araxon.core.logger import logger
from araxon.core.config import settings
from araxon.voice import VoiceInputPipeline, VoiceOutputPipeline


def print_banner():
    """Print ARAXON ASCII art banner."""
    banner = (
        "+-----------------------------------------------------------+\n"
        "|                                                           |\n"
        "|                       ARAXON v0.1.0                       |\n"
        "|                                                           |\n"
        "|          A futuristic modular AI operating system        |\n"
        "|                   STEP 1 - Foundation                    |\n"
        "|                                                           |\n"
        "+-----------------------------------------------------------+"
    )
    logger.info(banner)


def print_config_summary():
    """Print loaded configuration summary."""
    logger.info("Configuration Summary")
    logger.info(f"App Name: {settings.APP_NAME}")
    logger.info(f"Debug Mode: {settings.DEBUG_MODE}")
    logger.info(f"Log Level: {settings.LOG_LEVEL}")
    logger.info(f"Ollama Base URL: {settings.OLLAMA_BASE_URL}")
    logger.info(f"Wake Word: {settings.WAKE_WORD}")
    logger.info(f"Chroma DB Path: {settings.CHROMA_DB_PATH}")


async def main():
    """Main entry point for ARAXON."""
    print_banner()
    print_config_summary()

    logger.info("ARAXON core initialized successfully")
    logger.info(f"Application: {settings.APP_NAME} v0.1.0")
    logger.info(f"Debug mode: {settings.DEBUG_MODE}")

    logger.info("STEP 2: initializing voice input pipeline for a live microphone test.")
    voice_input_pipeline = VoiceInputPipeline()
    voice_output_pipeline = VoiceOutputPipeline(voice_input_pipeline)

    await voice_output_pipeline.speak("ARAXON voice systems online. Say something.")

    round_trip_start = time.monotonic()
    heard_text = await voice_input_pipeline.listen_and_transcribe()
    logger.info(f"Heard by ARAXON: {heard_text or '[no speech detected]'}")

    # STEP 4: replace echo with AI brain response here
    await voice_output_pipeline.speak(f"I heard you say: {heard_text}")

    round_trip_elapsed = time.monotonic() - round_trip_start
    logger.info(f"Voice round trip completed in {round_trip_elapsed:.2f}s.")

    # STEP 3: send transcribed text to TTS and AI brain here
    # STEP 4: vision pipeline will initialize here
    # STEP 5: memory system will initialize here
    # STEP 6: automation engine will initialize here
    # STEP 7: agent system will initialize here
    # STEP 8: internet integration will initialize here
    # STEP 9: UI system will initialize here

    logger.info("All systems ready. Awaiting commands...")

    logger.info("ARAXON is running. Press Ctrl+C to exit.")


if __name__ == "__main__":
    import asyncio

    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        logger.info("ARAXON shutting down...")
        logger.info("Goodbye!")
