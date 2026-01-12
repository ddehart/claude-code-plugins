#!/usr/bin/env python3
"""Minimal script for atomic observation storage operations."""

import argparse
import json
import os
import sys
from datetime import date
from pathlib import Path
import tempfile


def get_storage_path():
    """Resolve XDG-compliant storage path."""
    xdg_data = os.environ.get("XDG_DATA_HOME", str(Path.home() / ".local" / "share"))
    return Path(xdg_data) / "claude-plugins" / "self-documentation" / "observations.json"


STORAGE_PATH = get_storage_path()


def load_observations():
    """Load observations, returning empty structure if file doesn't exist."""
    if not STORAGE_PATH.exists():
        return {"version": 1, "observations": [], "last_updated": None}
    try:
        return json.loads(STORAGE_PATH.read_text())
    except json.JSONDecodeError:
        print("⚠ Warning: Corrupted storage file. Starting fresh.", file=sys.stderr)
        return {"version": 1, "observations": [], "last_updated": None}


def save_observations(data):
    """Atomic save via temp file + rename."""
    STORAGE_PATH.parent.mkdir(parents=True, exist_ok=True)
    data["last_updated"] = date.today().isoformat()

    # Write to temp file, then rename (atomic on POSIX)
    fd, temp_path = tempfile.mkstemp(dir=STORAGE_PATH.parent, suffix=".json")
    try:
        os.write(fd, json.dumps(data, indent=2).encode())
        os.close(fd)
        os.rename(temp_path, STORAGE_PATH)
    except:
        os.unlink(temp_path)
        raise


def generate_id(observations):
    """Generate next observation ID for today."""
    today = date.today().strftime("%Y%m%d")
    existing = [o["id"] for o in observations if o["id"].startswith(f"obs-{today}")]
    next_num = len(existing) + 1
    return f"obs-{today}-{next_num:03d}"


def cmd_list(args):
    data = load_observations()
    print(json.dumps(data["observations"], indent=2))


def cmd_add(args):
    data = load_observations()
    obs = {
        "id": generate_id(data["observations"]),
        "description": args.description,
        "feature_area": args.feature_area,
        "context": args.context or "",
        "discovered": date.today().isoformat(),
        "status": "submitted" if args.issue_url else "new",
        "issue_url": args.issue_url or None
    }
    data["observations"].append(obs)
    save_observations(data)
    print(json.dumps(obs, indent=2))


def cmd_remove(args):
    data = load_observations()
    original_len = len(data["observations"])
    data["observations"] = [o for o in data["observations"] if o["id"] != args.id]
    if len(data["observations"]) == original_len:
        print(f"✗ Observation {args.id} not found", file=sys.stderr)
        sys.exit(1)
    save_observations(data)
    print(f"✓ Removed {args.id}")


def cmd_get(args):
    data = load_observations()
    for obs in data["observations"]:
        if obs["id"] == args.id:
            print(json.dumps(obs, indent=2))
            return
    print(f"✗ Observation {args.id} not found", file=sys.stderr)
    sys.exit(1)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Manage self-documentation observations"
    )
    subparsers = parser.add_subparsers(dest="command", required=True)

    subparsers.add_parser("list", help="List all observations")

    add_p = subparsers.add_parser("add", help="Add a new observation")
    add_p.add_argument("--description", required=True, help="Description of the observed behavior")
    add_p.add_argument("--feature-area", required=True,
                       choices=["tools", "skills", "agents", "mcp", "config", "other"],
                       help="Feature area category")
    add_p.add_argument("--context", help="Context of how it was discovered")
    add_p.add_argument("--issue-url", help="GitHub issue URL if submitted")

    remove_p = subparsers.add_parser("remove", help="Remove an observation by ID")
    remove_p.add_argument("id", help="Observation ID to remove")

    get_p = subparsers.add_parser("get", help="Get a single observation by ID")
    get_p.add_argument("id", help="Observation ID to retrieve")

    args = parser.parse_args()
    {"list": cmd_list, "add": cmd_add, "remove": cmd_remove, "get": cmd_get}[args.command](args)
