"""Production WSGI entrypoint for gunicorn.

Example start command (from the backend/ directory):

    gunicorn wsgi:app --bind 0.0.0.0:$PORT --workers 2

Бул — production'до бирден-бир чакыруу чекити. Dev: python run.py.
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