# -*- coding: utf-8 -*-
"""Entrypoint shim for supervisor (uvicorn server:app)."""
from backend.app.main import app  # noqa: F401
if __name__ == "__main__":
    import seed_benalmadena
