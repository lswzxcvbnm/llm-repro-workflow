#!/usr/bin/env python3
"""Verify and install this portable skill without overwriting an existing skill."""
import argparse
import json
import os
from pathlib import Path
import runpy
import shutil
import sys


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--skills-dir", type=Path, help="Parent discovery directory; override for .agents/skills or another host")
    parser.add_argument("--verify-only", action="store_true", help="Verify bundle without installing")
    args = parser.parse_args()
    source = Path(__file__).resolve().parents[1]
    manifest = source / "bundle-manifest.json"
    try:
        helper = runpy.run_path(str(source / "scripts" / "artifact_manifest.py"))
        result = helper["verify"](source, manifest)
        if result["status"] != "ok":
            print(json.dumps(result, ensure_ascii=False), file=sys.stderr)
            return 1
        entries = json.loads(manifest.read_text(encoding="utf-8"))["files"]
        expected = {entry["path"] for entry in entries} | {"bundle-manifest.json"}
        actual = set()
        for path in source.rglob("*"):
            if helper["is_link"](path):
                raise ValueError("Bundle contains a link/junction: " + str(path.relative_to(source)))
            if path.is_file():
                actual.add(path.relative_to(source).as_posix())
        if actual != expected:
            raise ValueError("Unexpected/missing files: " + str(sorted(actual ^ expected)))
        if args.verify_only:
            print(json.dumps({"status": "verified", "files": len(entries)}, ensure_ascii=False))
            return 0
        codex_root = Path(os.environ.get("CODEX_HOME") or (Path.home() / ".codex"))
        skills_dir = (args.skills_dir or (codex_root / "skills")).expanduser().resolve()
        destination = skills_dir / "llm-repro-workflow"
        if destination.exists() or destination.is_symlink():
            raise ValueError("Destination already exists; no files changed: " + str(destination))
        # Reject a nested destination before creating anything (avoids recursive self-copy).
        try:
            destination.relative_to(source)
        except ValueError:
            pass
        else:
            raise ValueError("Destination must not be inside the source bundle")
        skills_dir.mkdir(parents=True, exist_ok=True)
        shutil.copytree(source, destination)
        installed = helper["verify"](destination, destination / "bundle-manifest.json")
        if installed["status"] != "ok":
            raise ValueError("Installed files failed verification; inspect destination")
        print(json.dumps({"status": "installed", "path": str(destination),
                          "next": "Open a new session; restart host if the skill is not discovered"}, ensure_ascii=False))
        return 0
    except (OSError, ValueError, KeyError, TypeError) as exc:
        print(json.dumps({"status": "error", "error": str(exc)}, ensure_ascii=False), file=sys.stderr)
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
