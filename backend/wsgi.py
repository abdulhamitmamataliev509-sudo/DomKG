"""Production WSGI entrypoint for gunicorn on Render.

Example start command (with Render root directory = "backend"):

    gunicorn wsgi:app --bind 0.0.0.0:$PORT --workers 2
"""
import os
import sys

# Make `app` and `config` importable regardless of the working directory.
# The `app` package and `config.py` live in this backend directory.
_BACKEND_DIR = os.path.dirname(os.path.abspath(__file__))
if _BACKEND_DIR not in sys.path:
    sys.path.insert(0, _BACKEND_DIR)

from app import create_app  # noqa: E402

app = create_app()