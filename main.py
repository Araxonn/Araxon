"""
ARAXON Core Entry Point.

Initializes the ARAXON operating system, loads configuration,
and prepares all subsystems for operation.
"""

import sys
import asyncio
import time
import psutil
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
        "data/ingested",
    ]
    for d in dirs:
        Path(d).mkdir(parents=True, exist_ok=True)


# Create directories first before importing
ensure_directories()

from araxon.core.logger import logger
from araxon.core.config import settings
from araxon.automation import AutomationRouter
from araxon.internet import InternetRouter
from araxon.ai import ARAXONBrain
from araxon.ai.personality import get_greeting
from araxon.memory import FileIngester, LongTermMemory
from araxon.wake import WakeOrchestrator
from araxon.vision import VisionRouter
from araxon.voice import VoiceInputPipeline, VoiceOutputPipeline
from araxon.agent import AgentController
from araxon.ui import ARAxonWebSocketServer, UIBridge


def print_banner():
    """Print ARAXON ASCII art banner."""
    banner = (
        "+-----------------------------------------------------------+\n"
        "|                                                           |\n"
        "|                       ARAXON v0.1.0                       |\n"
        "|                                                           |\n"
        "|          A futuristic modular AI operating system        |\n"
        "|                   STEP 10 - VISION SYSTEM                |\n"
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

    # STEP 11: Initialize WebSocket server for UI communication
    websocket_server = ARAxonWebSocketServer()
    await websocket_server.start()
    ui_bridge = UIBridge(websocket_server)
    logger.info(f"UI ready at ws://{settings.UI_WEBSOCKET_HOST}:{settings.UI_WEBSOCKET_PORT}")

    logger.info("STEP 4: initializing voice input, voice output, and ARAXONBrain.")
    voice_input_pipeline = VoiceInputPipeline(ui_bridge=ui_bridge)
    voice_output_pipeline = VoiceOutputPipeline(voice_input_pipeline, ui_bridge=ui_bridge)
    long_term_memory = LongTermMemory()
    file_ingester = FileIngester(long_term_memory.vector_store)
    brain = ARAXONBrain(long_term_memory=long_term_memory, ui_bridge=ui_bridge)
    automation_router = AutomationRouter()
    # STEP 9: Initialize internet intelligence system
    internet_router = InternetRouter()
    await internet_router.initialize()
    # STEP 10: Initialize vision system
    vision_router = VisionRouter()
    await vision_router.initialize()
    # Initialize the autonomous AgentController and pass to the wake orchestrator.
    agent_controller = AgentController(voice_output_pipeline, ui_bridge=ui_bridge)
    wake_orchestrator = WakeOrchestrator(
        voice_input_pipeline, voice_output_pipeline, brain, automation_router, agent_controller, internet_router, vision_router
    )

    await brain.warmup()
    await automation_router.initialize()
    logger.info(await long_term_memory.get_stats())
    await wake_orchestrator.start()
    await voice_output_pipeline.speak(get_greeting())
    await voice_output_pipeline.speak("I can launch your MERN, Python, AI, or focus workspace.")
    logger.info("[ACTIVE] ARAXON is running. Press Ctrl+C to exit.")

    # STEP 11: Start system stats broadcaster task
    stats_task = asyncio.create_task(_broadcast_system_stats(ui_bridge))
    start_time = time.time()

    try:
        # STEP 8: autonomous agent connects here
        # STEP 9: internet intelligence connects here
        # STEP 10: vision system connects here
        # STEP 12: final integration here
        while True:
            heard_text = await voice_input_pipeline.listen_and_transcribe()
            if not heard_text:
                continue

            state_label = "STANDBY" if wake_orchestrator.is_standby else "ACTIVE"
            logger.info(f"[{state_label}] Heard by ARAXON: {heard_text}")

            handled_by_wake_system = await wake_orchestrator.process_transcription(heard_text)
            if handled_by_wake_system:
                continue

            normalized_text = heard_text.strip().lower()
            if normalized_text in {"exit", "quit", "goodbye"}:
                break

            if wake_orchestrator.is_standby:
                continue

            if "remember that" in normalized_text or "don't forget" in normalized_text:
                await long_term_memory.remember_fact(heard_text)
                await voice_output_pipeline.speak("Got it, I'll remember that.")
                wake_orchestrator.standby_manager.reset_sleep_timer()
                continue

            if "what do you remember" in normalized_text or normalized_text == "recall" or normalized_text.startswith("recall "):
                recall_text = await long_term_memory.recall(heard_text)
                await voice_output_pipeline.speak(recall_text or "I couldn't find anything relevant.")
                wake_orchestrator.standby_manager.reset_sleep_timer()
                continue

            if "ingest my files" in normalized_text:
                ingestion_results = await file_ingester.ingest_folder()
                files_count = len(ingestion_results)
                total_chunks = sum(ingestion_results.values())
                await voice_output_pipeline.speak(
                    f"I ingested {files_count} file(s) and stored {total_chunks} chunk(s)."
                )
                wake_orchestrator.standby_manager.reset_sleep_timer()
                continue

            await wake_orchestrator.run_conversation_turn(heard_text)
    finally:
        stats_task.cancel()
        await vision_router.shutdown()
        await internet_router.shutdown()
        await wake_orchestrator.stop()
        await websocket_server.stop()
        await voice_output_pipeline.speak("ARAXON shutting down. Goodbye.")
        await voice_output_pipeline.stop()
        voice_input_pipeline.stop()


async def _broadcast_system_stats(ui_bridge):
    """Periodically broadcast system statistics to the UI."""
    start_time = time.time()
    
    while True:
        try:
            # Collect system statistics
            stats = {
                "cpu": psutil.cpu_percent(interval=0.1),
                "ram": psutil.virtual_memory().percent,
                "disk": psutil.disk_usage("/").percent,
                "battery": psutil.sensors_battery().percent if psutil.sensors_battery() else 100,
            }
            
            # Add uptime
            uptime_seconds = int(time.time() - start_time)
            hours = uptime_seconds // 3600
            minutes = (uptime_seconds % 3600) // 60
            seconds = uptime_seconds % 60
            stats["uptime"] = f"{hours}h {minutes}m {seconds}s"
            
            # Try to get GPU and network stats (may fail on some systems)
            try:
                # Simple network stats (bytes sent/received)
                net_io = psutil.net_io_counters()
                stats["net"] = (net_io.bytes_sent + net_io.bytes_recv) / (1024 * 1024 * 1024)  # GB
            except:
                stats["net"] = 0
            
            stats["gpu"] = 0  # GPU stats would require additional libraries
            
            await ui_bridge.send_system_stats(stats)
            await asyncio.sleep(settings.UI_SYSTEM_STATS_UPDATE_INTERVAL)
        except asyncio.CancelledError:
            break
        except Exception as e:
            logger.error(f"Error broadcasting system stats: {e}")
            await asyncio.sleep(settings.UI_SYSTEM_STATS_UPDATE_INTERVAL)


if __name__ == "__main__":
    import asyncio

    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        logger.info("[ACTIVE] ARAXON shutting down...")
        logger.info("[ACTIVE] Goodbye!")
