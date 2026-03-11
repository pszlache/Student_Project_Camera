default: run

# -------------------------
# Environment setup
# -------------------------

venv:
    python3 -m venv .venv

install:
    .venv/bin/pip install --upgrade pip
    .venv/bin/pip install -e .
    .venv/bin/pip install -e ".[dev]"

setup: venv install

# -------------------------
# Run application
# -------------------------

run:
    .venv/bin/python main.py

# -------------------------
# Testing
# -------------------------

test:
    .venv/bin/pytest

# -------------------------
# Code quality
# -------------------------

lint:
    .venv/bin/ruff check src

format:
    .venv/bin/black src
    .venv/bin/isort src

# -------------------------
# Utilities
# -------------------------

clean:
    find . -type d -name "__pycache__" -exec rm -r {} +

tree:
    tree -L 2