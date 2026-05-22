"""LangChain-style tools wrapping ARAXON capabilities for autonomous agents.

All tools are async-compatible, catch exceptions and return strings (never raise),
and are exported in `ARAXON_TOOLS` as callable tool objects.
"""

from __future__ import annotations

import asyncio
import json
from typing import Optional

from langchain_core.tools import tool

from araxon.automation.browser_agent import BrowserAgent
from araxon.automation.command_runner import CommandRunner
from araxon.automation.app_launcher import AppLauncher
from araxon.automation.web_launcher import WebLauncher
from araxon.memory.long_term_memory import LongTermMemory
from araxon.internet.researcher import WebResearcher
from araxon.internet.news_fetcher import NewsFetcher
from araxon.internet.wiki_lookup import WikiLookup
from araxon.core.logger import logger
from araxon.core.config import settings


# Instantiate local agents/tools on import to be self-contained
_browser = BrowserAgent()
_cmd = CommandRunner()
_app = AppLauncher()
_web = WebLauncher()
_memory = LongTermMemory()
_researcher = WebResearcher()
_news_fetcher = NewsFetcher()
_wiki_lookup = WikiLookup()


def _log_call(tool_name: str, input_summary: str, result_summary: str) -> None:
    logger.info(f"[AGENT_TOOL] {tool_name} called. input={input_summary}; result={result_summary}")


@tool
async def web_search(query: str) -> str:
    """Search the web for information and return a rich answer with source context."""
    try:
        input_summary = (query or "").strip()[:150]
        result = await _researcher.quick_answer(query)
        _log_call("web_search", input_summary, result[:150])
        return result
    except Exception as exc:
        logger.error(f"web_search failed: {exc}")
        return f"Error in web_search: {exc}"


@tool
async def research_topic(topic: str) -> str:
    """Research a topic from multiple web sources and summarize findings."""
    try:
        input_summary = (topic or "").strip()[:150]
        result = await _researcher.research(topic)
        _log_call("research_topic", input_summary, result[:150])
        return result
    except Exception as exc:
        logger.error(f"research_topic failed: {exc}")
        return f"Error in research_topic: {exc}"


@tool
async def get_latest_news(topic: str = None) -> str:
    """Get latest news headlines on a topic."""
    try:
        input_summary = (topic or settings.NEWS_DEFAULT_TOPIC)[:150]
        result = await _news_fetcher.get_news(topic)
        _log_call("get_latest_news", input_summary, result[:150])
        return result
    except Exception as exc:
        logger.error(f"get_latest_news failed: {exc}")
        return f"Error in get_latest_news: {exc}"


@tool
async def wikipedia_lookup(topic: str) -> str:
    """Look up a topic on Wikipedia for quick facts."""
    try:
        input_summary = (topic or "").strip()[:150]
        result = await _wiki_lookup.lookup(topic)
        _log_call("wikipedia_lookup", input_summary, result[:150])
        return result
    except Exception as exc:
        logger.error(f"wikipedia_lookup failed: {exc}")
        return f"Error in wikipedia_lookup: {exc}"


@tool
async def open_website(site: str) -> str:
    """Open a website or URL in the browser."""
    try:
        input_summary = (site or "").strip()[:150]
        result = await _web.open(site)
        _log_call("open_website", input_summary, result[:150])
        return result
    except Exception as exc:
        logger.error(f"open_website failed: {exc}")
        return f"Error in open_website: {exc}"


@tool
async def open_application(app_name: str) -> str:
    """Open a desktop application by name."""
    try:
        input_summary = (app_name or "").strip()[:150]
        result = await _app.launch(app_name)
        _log_call("open_application", input_summary, result[:150])
        return result
    except Exception as exc:
        logger.error(f"open_application failed: {exc}")
        return f"Error in open_application: {exc}"


@tool
async def run_terminal_command(command: str) -> str:
    """Run a safe terminal command and return output."""
    try:
        input_summary = (command or "").strip()[:200]
        result = await _cmd.run(command)
        _log_call("run_terminal_command", input_summary, result[:150])
        return result
    except Exception as exc:
        logger.error(f"run_terminal_command failed: {exc}")
        return f"Error in run_terminal_command: {exc}"


@tool
async def read_file(path: str) -> str:
    """Read the contents of a file by path."""
    try:
        input_summary = (path or "").strip()
        loop = asyncio.get_event_loop()
        try:
            content = await loop.run_in_executor(None, lambda: open(input_summary, "r", encoding="utf-8").read())
        except FileNotFoundError:
            _log_call("read_file", input_summary, "not found")
            return "Error: file not found."
        except Exception as exc:
            logger.error(f"read_file I/O failed: {exc}")
            return f"Error reading file: {exc}"

        short = content[:1000]
        _log_call("read_file", input_summary, f"read {len(short)} chars")
        return short
    except Exception as exc:
        logger.error(f"read_file failed: {exc}")
        return f"Error in read_file: {exc}"


@tool
async def write_file(payload: str) -> str:
    """Write or append content to a file."""
    try:
        data = json.loads(payload)
        path = data.get("path")
        content = data.get("content", "")
        mode = data.get("mode", "write")
        if not path:
            return "Error: missing path in payload"

        write_mode = "w" if mode == "write" else "a"
        loop = asyncio.get_event_loop()
        def _do_write():
            with open(path, write_mode, encoding="utf-8") as fh:
                fh.write(content)
        await loop.run_in_executor(None, _do_write)
        _log_call("write_file", path, f"wrote {len(content)} chars")
        return f"Wrote to {path}"
    except json.JSONDecodeError:
        return "Error: payload must be valid JSON with keys path, content, mode"
    except Exception as exc:
        logger.error(f"write_file failed: {exc}")
        return f"Error in write_file: {exc}"


@tool
async def remember_fact(fact: str) -> str:
    """Store an important fact or note in long-term memory."""
    try:
        await _memory.remember_fact(fact)
        _log_call("remember_fact", fact[:150], "remembered")
        return f"Remembered: {fact}"
    except Exception as exc:
        logger.error(f"remember_fact failed: {exc}")
        return f"Error in remember_fact: {exc}"


@tool
async def recall_memory(query: str) -> str:
    """Search long-term memory for relevant information."""
    try:
        result = await _memory.recall(query)
        _log_call("recall_memory", query[:150], (result or "(no result)")[:150])
        return result
    except Exception as exc:
        logger.error(f"recall_memory failed: {exc}")
        return f"Error in recall_memory: {exc}"


@tool
async def take_screenshot(filename: Optional[str] = None) -> str:
    """Take a screenshot of the current screen."""
    try:
        result = await _browser.take_screenshot(path=filename)
        _log_call("take_screenshot", (filename or "default"), result[:200])
        return result
    except Exception as exc:
        logger.error(f"take_screenshot failed: {exc}")
        return f"Error in take_screenshot: {exc}"


@tool
async def get_page_content(url: str) -> str:
    """Get the text content of a webpage by URL."""
    try:
        result = await _browser.get_page_summary(url)
        _log_call("get_page_content", url[:150], result[:150])
        return result
    except Exception as exc:
        logger.error(f"get_page_content failed: {exc}")
        return f"Error in get_page_content: {exc}"


# Export a list and a dict for lookup by name
ARAXON_TOOLS = [
    web_search,
    research_topic,
    get_latest_news,
    wikipedia_lookup,
    open_website,
    open_application,
    run_terminal_command,
    read_file,
    write_file,
    remember_fact,
    recall_memory,
    take_screenshot,
    get_page_content,
]

ARAXON_TOOL_DICT = {t.name: t for t in ARAXON_TOOLS}
