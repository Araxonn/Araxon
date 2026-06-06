"""Quick test of vision router functionality."""
import asyncio
from araxon.vision.vision_router import VisionRouter


async def test_router():
    """Test vision router command routing."""
    router = VisionRouter()
    await router.initialize()
    
    # Test routing with various commands
    test_commands = [
        ("what do you see", "HANDLED"),
        ("read my screen", "HANDLED"),
        ("take a screenshot", "HANDLED"),
        ("what's the error", "HANDLED"),
        ("find button on screen", "HANDLED"),
        ("what file is open", "HANDLED"),
        ("hello there", "NOT HANDLED"),  # Should not be handled
    ]
    
    print("[VISION] Testing router with sample commands:\n")
    for cmd, expected in test_commands:
        result = await router.route(cmd)
        status = "✓" if (result is None and expected == "NOT HANDLED") or (result is not None and expected == "HANDLED") else "✗"
        actual = "HANDLED" if result else "NOT HANDLED"
        print(f"{status} '{cmd}' → {actual} (expected {expected})")
    
    await router.shutdown()
    print("\n[VISION] Router test complete")


if __name__ == "__main__":
    asyncio.run(test_router())
