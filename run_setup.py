#!/usr/bin/env python3
"""Quick setup runner."""
import subprocess
import sys

if __name__ == "__main__":
    # Run the bootstrap setup
    result = subprocess.run([sys.executable, "bootstrap.py"], cwd=r"c:\Users\lucky\OneDrive\Desktop\Araxon.worktrees\agents-project-setup-foundation-structure")
    sys.exit(result.returncode)
