#!/usr/bin/env python3
"""Create or verify an explicit SHA-256 file manifest without following symlinks."""
import argparse
import hashlib
import json
from pathlib import Path, PurePosixPath
import stat
import sys


def is_link(path):
    # Windows junction detection also works on Python versions before Path.is_junction.
    attrs = getattr(path.lstat(), "st_file_attributes", 0)
    return path.is_symlink() or bool(attrs & getattr(stat, "FILE_ATTRIBUTE_REPARSE_POINT", 0))


def safe_file(root, relative):
    if not isinstance(relative, str):
        raise ValueError("Manifest paths must be strings")
    rel = PurePosixPath(relative)
    if not relative or rel.is_absolute() or ".." in rel.parts or "\\" in relative or ":" in relative:
        raise ValueError("Use a safe relative POSIX path: " + relative)
    candidate = root.joinpath(*rel.parts)
    current = root
    for part in rel.parts:
        current = current / part
        if is_link(current):
            raise ValueError("Links/junctions are not accepted: " + relative)
    try:
        candidate.resolve().relative_to(root)
    except ValueError:
        raise ValueError("File escapes root: " + relative)
    if not candidate.is_file():
        raise ValueError("Missing or non-regular file: " + relative)
    return candidate


def digest(path):
    result = hashlib.sha256()
    with path.open("rb") as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b""):
            result.update(chunk)
    return result.hexdigest()


def create(root, files, output):
    if not files:
        raise ValueError("Provide at least one --file")
    records = []
    seen = set()
    for relative in sorted(files):
        path = safe_file(root, relative)
        normalized = path.relative_to(root).as_posix()
        if normalized in seen or path.resolve() == output.resolve():
            raise ValueError("Duplicate file or self-inclusion: " + relative)
        seen.add(normalized)
        before = path.stat()
        sha = digest(path)
        after = path.stat()
        if (before.st_size, before.st_mtime_ns) != (after.st_size, after.st_mtime_ns):
            raise ValueError("File changed while hashing: " + relative)
        records.append({"path": normalized, "size_bytes": after.st_size, "sha256": sha})
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(json.dumps({"schema_version": 1, "algorithm": "sha256", "files": records},
                                 ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    return {"status": "ok", "files": len(records), "manifest": str(output)}


def verify(root, manifest):
    data = json.loads(manifest.read_text(encoding="utf-8"))
    if not isinstance(data, dict) or data.get("schema_version") != 1 or data.get("algorithm") != "sha256" or not isinstance(data.get("files"), list) or not data["files"]:
        raise ValueError("Unsupported or empty manifest")
    failures = []
    seen = set()
    for record in data["files"]:
        if not isinstance(record, dict) or not {"path", "size_bytes", "sha256"} <= record.keys():
            raise ValueError("Invalid manifest record")
        relative = record["path"]
        try:
            path = safe_file(root, relative)
            normalized = path.relative_to(root).as_posix()
            if normalized in seen:
                raise ValueError("Duplicate manifest entry")
            seen.add(normalized)
            if path.stat().st_size != record["size_bytes"] or digest(path) != record["sha256"]:
                raise ValueError("Size or SHA-256 mismatch")
        except (ValueError, OSError) as exc:
            failures.append({"path": relative, "error": str(exc)})
    return {"status": "failed" if failures else "ok", "files": len(data["files"]), "failures": failures,
            "scope": "Listed files only; additional files are not examined"}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    sub = parser.add_subparsers(dest="command", required=True)
    create_parser = sub.add_parser("create")
    create_parser.add_argument("--root", type=Path, required=True)
    create_parser.add_argument("--file", action="append", required=True)
    create_parser.add_argument("--output", type=Path, required=True)
    verify_parser = sub.add_parser("verify")
    verify_parser.add_argument("--root", type=Path, required=True)
    verify_parser.add_argument("--manifest", type=Path, required=True)
    args = parser.parse_args()
    try:
        root = args.root.resolve(strict=True)
        if not root.is_dir():
            raise ValueError("Root must be a directory")
        result = create(root, args.file, args.output) if args.command == "create" else verify(root, args.manifest)
        print(json.dumps(result, ensure_ascii=False))
        return 0 if result["status"] == "ok" else 1
    except (OSError, ValueError, KeyError, TypeError) as exc:
        print(json.dumps({"status": "error", "error": str(exc)}, ensure_ascii=False), file=sys.stderr)
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
