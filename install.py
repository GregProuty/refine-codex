#!/usr/bin/env python3
"""Install this skill into the current user's Codex skill directory."""
from pathlib import Path
import os
import shutil
import sys

SOURCE = Path(__file__).resolve().parent
HOME = Path(os.environ.get("CODEX_HOME", Path.home() / ".codex"))
DEST = HOME / "skills" / "refine"

if DEST.is_symlink():
    print(f"Refusing to write through symlink: {DEST}", file=sys.stderr)
    sys.exit(1)
if DEST.exists() and "--update" not in sys.argv[1:]:
    print(f"Refusing to replace existing skill: {DEST} (pass --update to refresh)", file=sys.stderr)
    sys.exit(1)

shutil.copytree(SOURCE, DEST, dirs_exist_ok=True,
                ignore=shutil.ignore_patterns(".git", ".tmp", "__pycache__", "*.pyc"))
print(f"Installed: {DEST}")
