#!/usr/bin/env python3
"""Direct directory setup using Path.mkdir."""

from pathlib import Path

root = Path("c:/Users/lucky/OneDrive/Desktop/Araxon.worktrees/agents-project-setup-foundation-structure")
root.mkdir(parents=True, exist_ok=True)

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
    (root / d).mkdir(parents=True, exist_ok=True)
    print(f"Created: {d}")

print("Done!")
