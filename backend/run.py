"""DomKG local development runner.

Usage:
    python run.py            # backend/ ичинде туруп

Иштелүү серверин иштетет (host 0.0.0.0, port $PORT|5000).
Production үчүн wsgi.py + gunicorn колдонулат.
"""
import os
import sys

# `app` пакети жана `config.py` ушул backend/ папкасында —
# кайсы каталогдон ишке кирсе да import табылсын үчүн.
_BACKEND_DIR = os.path.dirname(os.path.abspath(__file__))
if _BACKEND_DIR not in sys.path:
    sys.path.insert(0, _BACKEND_DIR)

from app import create_app  # noqa: E402

app = create_app()

if __name__ == "__main__":
    port = int(os.getenv("PORT", "5000"))
    # DEBUG config'тен алынат (dev: True, prod: False — эч качан чейин)
    app.run(host="0.0.0.0", port=port, debug=app.config.get("DEBUG", False))