import asyncio

from araxon.automation.automation_router import AutomationRouter


def test_launch_command_routes_to_app_launcher_for_fuzzy_names() -> None:
    router = AutomationRouter()
    calls = []

    async def fake_launch(app_name: str) -> str:
        calls.append(app_name)
        return "Opened spotify"

    router.app_launcher.launch = fake_launch  # type: ignore[assignment]

    result = asyncio.run(router.route("launch spootify"))

    assert result == "Opened spotify"
    assert calls == ["spotify"]


def test_help_command_returns_supported_commands_summary() -> None:
    router = AutomationRouter()

    result = asyncio.run(router.route("help"))

    assert result is not None
    assert "MERN" in result
    assert "Spotify" in result
