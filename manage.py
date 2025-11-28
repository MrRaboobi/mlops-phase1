"""
Windows-friendly management script for HEARTSIGHT MLOps project.
Replaces Makefile commands for Windows users.

Usage:
    python manage.py train      # Run training pipeline
    python manage.py dev         # Start FastAPI dev server
    python manage.py test        # Run tests
    python manage.py lint        # Run linters
    python manage.py format      # Format code
"""

import sys
import subprocess


def run_command(cmd, description):
    """Execute a shell command and handle errors."""
    print(f"\n{'='*60}")
    print(f"Running: {description}")
    print(f"Command: {cmd}")
    print(f"{'='*60}\n")

    result = subprocess.run(cmd, shell=True)
    if result.returncode != 0:
        print(f"\n❌ Error: {description} failed with exit code {result.returncode}")
        sys.exit(1)
    else:
        print(f"\n✅ {description} completed successfully")


def main():
    if len(sys.argv) < 2:
        print(__doc__)
        sys.exit(1)

    command = sys.argv[1]

    commands = {
        "train": {"cmd": "python src/pipeline/train.py", "desc": "Training Pipeline"},
        "dev": {
            "cmd": "uvicorn src.api.main:app --reload",
            "desc": "FastAPI Development Server",
        },
        "test": {"cmd": "pytest -v", "desc": "Test Suite"},
        "lint": {"cmd": "ruff check . && black --check .", "desc": "Code Linting"},
        "format": {"cmd": "black .", "desc": "Code Formatting"},
        "clean": {
            "cmd": "python -c \"import shutil; import glob; [shutil.rmtree(d) for d in glob.glob('**/__pycache__', recursive=True)]; [shutil.rmtree(d) for d in glob.glob('**/.pytest_cache', recursive=True)]\"",
            "desc": "Clean Cache Files",
        },
        "check": {"cmd": "pre-commit run --all-files", "desc": "Pre-commit Hooks"},
        "evidently": {
            "cmd": "python src/monitoring/evidently_server.py",
            "desc": "Start Evidently Dashboard Server (port 7000)",
        },
    }

    if command not in commands:
        print(f"❌ Unknown command: {command}")
        print(__doc__)
        sys.exit(1)

    run_command(commands[command]["cmd"], commands[command]["desc"])


if __name__ == "__main__":
    main()
