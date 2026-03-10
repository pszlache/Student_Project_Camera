# Default command
default: run

# -------------------------
# Setup environment
# -------------------------

venv:
    python -m venv .venv

install:
    pip install -r requirements.txt

setup: venv install

# -------------------------
# Run application
# -------------------------

run:
    python main.py

web:
    python -m src.web.stream

# -------------------------
# Testing
# -------------------------

test:
    pytest tests

# -------------------------
# Development tools
# -------------------------

format:
    black src tests

lint:
    flake8 src

# -------------------------
# Utilities
# -------------------------

clean:
    find . -type d -name "__pycache__" -exec rm -r {} +

tree:
    tree -L 2