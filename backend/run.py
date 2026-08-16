import os
import sys

# Ensure the directory containing the `app` package (and `config.py`)
# is on sys.path, so `from app import create_app` works no matter how
# or from where this entry point is launched (e.g. Render, Docker, CLI).
_BACKEND_DIR = os.path.dirname(os.path.abspath(__file__))
if _BACKEND_DIR not in sys.path:
    sys.path.insert(0, _BACKEND_DIR)

from app import create_app  # noqa: E402

app = create_app()

if __name__ == "__main__":
    port = int(os.getenv("PORT", "5000"))
    # Production runs are served by gunicorn (wsgi.py); run.py is for
    # local development. debug stays off so it is safe on Render too.
    app.run(host="0.0.0.0", port=port, debug=False)