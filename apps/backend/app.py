"""Vercel ASGI entrypoint; also usable via uvicorn app:app."""
import sys
from pathlib import Path
sys.path.insert(0,str(Path(__file__).parent/"src"))
from economy_swing.api import app  # noqa: E402,F401
