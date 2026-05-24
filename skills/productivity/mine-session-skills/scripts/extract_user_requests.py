#!/usr/bin/env python3
"""Extract recent user requests from Claude, Codex, and Pi JSONL session logs.

Best-effort parser: handles several JSON shapes and prints timestamp, source, path,
and compacted user text. No network access. Skips obvious secrets/noisy blobs.
"""
from __future__ import annotations

import argparse
import glob
import json
import os
from pathlib import Path
from typing import Any, Iterable

HOME = Path.home()
PATTERNS = {
    "claude": [".claude/transcripts/*.jsonl", ".claude/projects/**/*.jsonl"],
    "codex": [".codex/history.jsonl", ".codex/sessions/**/*.jsonl"],
    "pi": [".pi/agent/sessions/**/*.jsonl"],
}

SECRET_MARKERS = ["BEGIN OPENSSH", "api_key", "apikey", "password", "token:", "secret"]


def files() -> list[tuple[str, Path]]:
    found: list[tuple[str, Path]] = []
    for source, patterns in PATTERNS.items():
        for pattern in patterns:
            for p in glob.glob(str(HOME / pattern), recursive=True):
                path = Path(p)
                if path.is_file():
                    found.append((source, path))
    return sorted(found, key=lambda item: item[1].stat().st_mtime, reverse=True)


def text_from_content(content: Any) -> str:
    if isinstance(content, str):
        return content
    if isinstance(content, list):
        parts = []
        for item in content:
            if isinstance(item, str):
                parts.append(item)
            elif isinstance(item, dict):
                if isinstance(item.get("text"), str):
                    parts.append(item["text"])
                elif isinstance(item.get("content"), str):
                    parts.append(item["content"])
        return "\n".join(parts)
    if isinstance(content, dict):
        for key in ("text", "content", "message"):
            if isinstance(content.get(key), str):
                return content[key]
    return ""


def user_text(obj: dict[str, Any]) -> str:
    # Common chat shapes
    if obj.get("role") == "user":
        return text_from_content(obj.get("content") or obj.get("message") or obj.get("text"))
    msg = obj.get("message")
    if isinstance(msg, dict) and msg.get("role") == "user":
        return text_from_content(msg.get("content") or msg.get("text"))
    if obj.get("type") in {"user", "user_message", "input"}:
        return text_from_content(obj.get("content") or obj.get("text") or obj.get("message"))
    # Codex history often has user text under item/content-ish fields.
    item = obj.get("item")
    if isinstance(item, dict) and item.get("role") == "user":
        return text_from_content(item.get("content") or item.get("text"))
    return ""


def timestamp(obj: dict[str, Any], path: Path) -> str:
    for key in ("timestamp", "created_at", "createdAt", "time", "ts"):
        val = obj.get(key)
        if val:
            return str(val)
    return str(int(path.stat().st_mtime))


def compact(s: str, max_chars: int) -> str:
    s = " ".join(s.split())
    if any(marker.lower() in s.lower() for marker in SECRET_MARKERS):
        return "[redacted possible secret-bearing request]"
    return s if len(s) <= max_chars else s[: max_chars - 1] + "…"


def iter_requests(limit_files: int, max_chars: int) -> Iterable[tuple[str, str, str, str]]:
    for source, path in files()[:limit_files]:
        try:
            with path.open("r", encoding="utf-8", errors="ignore") as f:
                for line in f:
                    line = line.strip()
                    if not line:
                        continue
                    try:
                        obj = json.loads(line)
                    except json.JSONDecodeError:
                        continue
                    if not isinstance(obj, dict):
                        continue
                    text = user_text(obj)
                    if text.strip():
                        yield timestamp(obj, path), source, str(path).replace(str(HOME), "~"), compact(text, max_chars)
        except OSError:
            continue


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--limit", type=int, default=80, help="number of recent files to scan")
    parser.add_argument("--max-chars", type=int, default=500, help="max chars per request")
    args = parser.parse_args()
    for ts, source, path, text in iter_requests(args.limit, args.max_chars):
        print(f"[{ts}] {source} {path}\n{text}\n")


if __name__ == "__main__":
    main()
