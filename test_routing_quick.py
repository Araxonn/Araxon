"""Quick test of updated routing."""
import asyncio
from araxon.automation.automation_router import AutomationRouter


async def test_commands():
    router = AutomationRouter()
    
    print("Testing command routing...\n")
    
    # Test 1: Open Spotify
    result = await router.route("open spotify")
    print(f"Command: 'open spotify'")
    print(f"Result: {result}\n")
    
    # Test 2: MERN workspace
    result = await router.route("launch my mern workspace")
    print(f"Command: 'launch my mern workspace'")
    print(f"Result: {result[:80]}...\n" if result and len(result) > 80 else f"Result: {result}\n")
    
    # Test 3: Help
    result = await router.route("help")
    print(f"Command: 'help'")
    print(f"Result: {result[:100]}...\n")
    
    print("✓ All routing tests completed")


asyncio.run(test_commands())
