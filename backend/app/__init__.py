"""TruthShield AI backend package."""
import sys
from pathlib import Path

# Make the repo-level `ai` package importable when running from the repo (not needed in Docker).
_root = Path(__file__).resolve().parents[2]
if (_root / "ai").is_dir() and str(_root) not in sys.path:
    sys.path.append(str(_root))
