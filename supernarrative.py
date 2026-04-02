#!/usr/bin/env python3
"""
SuperNarrative — Persistent narrative memory for long-form fiction.
Treats your novel like software: with state, dependencies, and verification.

Unified CLI entry point.
"""

import argparse
import os
import subprocess
import sys

VERSION = "0.1.0"
SCRIPTS_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "scripts")
DEFAULT_DB = os.path.join(os.path.dirname(os.path.abspath(__file__)), "db", "supernarrative.db")


def find_db():
    """Auto-detect database file."""
    if os.path.exists(DEFAULT_DB):
        return DEFAULT_DB
    # Try any .db file in db/
    db_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "db")
    if os.path.exists(db_dir):
        for f in os.listdir(db_dir):
            if f.endswith(".db") and not f.endswith(".bak"):
                return os.path.join(db_dir, f)
    return DEFAULT_DB  # Will be created on init


COMMANDS = {
    "init": {
        "script": "init_project.py",
        "help": "Initialize a new novel project",
        "example": 'supernarrative init --name "My Novel" --genre thriller',
    },
    "import": {
        "script": "import_existing.py",
        "help": "Import an existing novel (bible, chapters, continuity)",
        "example": "supernarrative import --bible bible.docx --chapters-dir chapters/",
    },
    "context": {
        "script": "context.py",
        "help": "Generate context package before writing a chapter",
        "example": "supernarrative context --chapter 5",
    },
    "analyze": {
        "script": "analyze.py",
        "help": "Analyze a written chapter and extract narrative data",
        "example": "supernarrative analyze --chapter 5 --analysis-json analysis.json",
    },
    "update": {
        "script": "update.py",
        "help": "Apply confirmed analysis to the database",
        "example": "supernarrative update --chapter 5 --confirm",
    },
    "verify": {
        "script": "verify.py",
        "help": "Check for consistency issues (epistemic violations, plot holes, timeline errors)",
        "example": "supernarrative verify --chapter 5",
    },
    "dashboard": {
        "script": "dashboard.py",
        "help": "Show project status (threads, clues, tension curve, characters)",
        "example": "supernarrative dashboard --format terminal",
    },
    "search": {
        "script": "search.py",
        "help": "Search the narrative database (who knows what, where is X, etc.)",
        "example": 'supernarrative search --action who_knows --query "secret identity"',
    },
    "snapshot": {
        "script": "snapshot.py",
        "help": "Create/list/restore database backups",
        "example": "supernarrative snapshot",
    },
    "ops": {
        "script": "db_ops.py",
        "help": "Direct database operations (add characters, facts, threads, etc.)",
        "example": "supernarrative ops --action add_character --data '{...}'",
    },
}


def print_banner():
    print(f"""
  \033[1m\033[36mSuperNarrative\033[0m v{VERSION}
  \033[2mPersistent narrative memory for long-form fiction\033[0m
  \033[2mTreats your novel like software.\033[0m
""")


def print_help():
    print_banner()
    print("  \033[1mUsage:\033[0m supernarrative <command> [options]\n")
    print("  \033[1mCommands:\033[0m")

    # Group commands by workflow phase
    phases = [
        ("Setup", ["init", "import"]),
        ("Writing", ["context", "analyze", "update", "verify"]),
        ("Monitoring", ["dashboard", "search"]),
        ("Maintenance", ["snapshot", "ops"]),
    ]

    for phase_name, cmds in phases:
        print(f"\n    \033[33m{phase_name}\033[0m")
        for cmd in cmds:
            info = COMMANDS[cmd]
            print(f"      \033[1m{cmd:12s}\033[0m {info['help']}")

    print(f"\n  \033[1mWorkflow:\033[0m")
    print("    init → import → [context → write → analyze → update → verify] → dashboard")
    print(f"\n  \033[1mExamples:\033[0m")
    print('    supernarrative init --name "My Novel" --genre thriller')
    print("    supernarrative context --chapter 5")
    print("    supernarrative dashboard --format terminal")
    print('    supernarrative search --action who_knows --query "the murder"')
    print("    supernarrative verify")
    print()


def main():
    if len(sys.argv) < 2 or sys.argv[1] in ("-h", "--help", "help"):
        print_help()
        sys.exit(0)

    if sys.argv[1] in ("-v", "--version", "version"):
        print(f"SuperNarrative v{VERSION}")
        sys.exit(0)

    command = sys.argv[1]

    if command not in COMMANDS:
        print(f"\033[31mUnknown command: {command}\033[0m")
        print(f"Run 'supernarrative --help' for available commands.")
        sys.exit(1)

    script = os.path.join(SCRIPTS_DIR, COMMANDS[command]["script"])

    if not os.path.exists(script):
        print(f"\033[31mScript not found: {script}\033[0m")
        sys.exit(1)

    # Build args: pass through everything after the command name
    remaining_args = sys.argv[2:]

    # Auto-inject --db if not provided
    if "--db" not in remaining_args:
        db_path = find_db()
        remaining_args = ["--db", db_path] + remaining_args

    cmd = [sys.executable, script] + remaining_args

    try:
        result = subprocess.run(cmd, capture_output=False)
        sys.exit(result.returncode)
    except KeyboardInterrupt:
        sys.exit(130)


if __name__ == "__main__":
    main()
