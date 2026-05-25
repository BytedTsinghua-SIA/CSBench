"""Pytest configuration file."""
import sys
from pathlib import Path

# Add parent directory to Python path to allow importing process_simulator
parent_dir = Path(__file__).parent.parent
if str(parent_dir) not in sys.path:
    sys.path.insert(0, str(parent_dir))

