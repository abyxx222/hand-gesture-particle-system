"""Make the source package importable when pytest is run from repository root."""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parents[1]))
