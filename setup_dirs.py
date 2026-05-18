#!/usr/bin/env python3
"""
Bootstrap script for ARAXON project setup.
Creates all necessary directories and files.
"""

import os
import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).parent.resolve()

def setup_project():
    """Setup complete ARAXON project structure."""
    
    # Change to project directory
    os.chdir(PROJECT_ROOT)
    
    # Create all directories
    directories = [
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
    
    print("📁 Creating directories...")
    for directory in directories:
        Path(directory).mkdir(parents=True, exist_ok=True)
        print(f"   ✓ {directory}")
    
    print("\n✅ Project structure created successfully!")
    print(f"   Root: {PROJECT_ROOT}")
    
    return 0

if __name__ == "__main__":
    sys.exit(setup_project())
