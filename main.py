#!/usr/bin/env python3
"""
Launcher script for Agentic Bookkeeper application.

This script serves as a convenient entry point in the project root directory.
It imports and runs the main application from the package.
"""

import sys
from pathlib import Path

# Add src directory to path
src_path = Path(__file__).parent / "src"
sys.path.insert(0, str(src_path))

# Import and run main application
from agentic_bookkeeper.main import main

if __name__ == "__main__":
    sys.exit(main())
