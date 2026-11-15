"""Reject outdated deployment artifacts, including retries of older workflow jobs."""
from __future__ import annotations

import argparse
import json
import os
import re
import subprocess
import time
import urllib.error
import urllib.request
from datetime import datetime, timezone
from pathlib import Path
from urllib.parse import urlencode, urlsplit


class ReleaseError(RuntimeError):
    pass


def metadata(raw: bytes, label: str) -> tuple[dict, datetime]:
    try:
        value = json.loads(raw)
        if not isinstance(value, dict) or not re.fullmatch(r"[0-9a-f]{40}|[0-9a-f]{64}", value.get("commit", "")):
            raise ValueError("invalid commit")
        stamp = value["built_at"]
        if not isinstance(stamp, str):
            raise ValueError("invalid timestamp")
        built_at = datetime.fromisoformat(stamp.replace("Z", "+00:00"))
        if built_at.tzinfo is None:
            raise ValueError("timestamp needs a timezone")
        return value, built_at.astimezone(timezone.utc)
    except (ValueError, TypeError, KeyError):
        raise ReleaseError(f"{label} has invalid build metadata (commit and ISO built_at with timezone are required)") from None


def current_main() -> str:
    try:
        result = subprocess.run(
            ["git", "ls-remote", "origin", "refs/heads/main"],
            check=True, capture_output=True, text=True, timeout=30,
            env={**os.environ, "GIT_TERMINAL_PROMPT": "0"},
        )
    except (OSError, subprocess.SubprocessError):
        # Git's stderr can include a credential-bearing remote URL; never print it.
        raise ReleaseError("Could not resolve the current origin/main HEAD") from None
    lines = result.stdout.strip().splitlines()
    if len(lines) != 1 or not re.fullmatch(r"(?:[0-9a-f]{40}|[0-9a-f]{64})\s+refs/heads/main", lines[0]):
        raise ReleaseError("origin/main did not return one valid HEAD")
    return lines[0].split()[0]


def check(build_dir: Path, target: str) -> None:
    try:
        local, built_at = metadata((build_dir / "build-info.json").read_bytes(), "Local artifact")
    except OSError:
        raise ReleaseError("Local artifact is missing build-info.json") from None
    if local["commit"] != current_main():
        raise ReleaseError("Artifact commit is no longer the current origin/main HEAD; build the current main before deploying")

    url = urlsplit(target)
    if url.scheme not in {"https", "http"} or not url.netloc or url.query or url.fragment or url.username or url.password:
        raise ReleaseError("Deployment target must be an HTTP(S) site URL without credentials, query or fragment")
    request = urllib.request.Request(
        target.rstrip("/") + "/build-info.json?" + urlencode({"freshness": time.time_ns()}),
        headers={"Cache-Control": "no-cache", "Accept": "application/json"},
    )
    try:
        with urllib.request.urlopen(request, timeout=30) as response:
            if response.status != 200:
                raise ReleaseError(f"Could not inspect deployed build metadata: HTTP {response.status}")
            raw = response.read(65_537)
    except urllib.error.HTTPError as error:
        if error.code == 404:
            print("Current main verified; target has no build metadata (first migration)")
            return
        raise ReleaseError(f"Could not inspect deployed build metadata: HTTP {error.code}") from None
    except (urllib.error.URLError, OSError):
        raise ReleaseError("Could not inspect deployed build metadata: network request failed") from None
    if len(raw) > 65_536:
        raise ReleaseError("Deployed build metadata exceeds the expected size")
    deployed, deployed_at = metadata(raw, "Deployed site")
    if built_at < deployed_at:
        raise ReleaseError(f"Artifact was built before the deployed site ({local['built_at']} < {deployed['built_at']}); refusing to overwrite a newer build")
    print(f"Current main and build freshness verified: {local['commit']} at {local['built_at']}")


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("build_dir", type=Path)
    parser.add_argument("target")
    args = parser.parse_args()
    try:
        check(args.build_dir, args.target)
    except ReleaseError as error:
        raise SystemExit(f"Refusing deployment: {error}") from None


if __name__ == "__main__":
    main()
