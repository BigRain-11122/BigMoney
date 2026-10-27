#!/usr/bin/env python
"""Read-only mirror of chosen path scopes from a remote ref (partial-clone friendly).

Why: this clone is a blob:none promisor clone.  `git fetch` re-downloads the whole
object graph (222k objects at ~40 KiB/s = days) and `git ls-tree -l` / plain
checkout lazily fetch big data blobs one by one, so the local main cannot simply
fast-forward.  Reading upstream *code and research* faces needs ~300 small blobs
only; this tool materialises exactly those into a mirror directory outside the
working tree and never touches HEAD, the index or the work tree.

Usage:
    python Tools/upstream_mirror.py                 # default scopes, default dest
    python Tools/upstream_mirror.py --paths scripts research --dest D:\\tmp\\up
    python Tools/upstream_mirror.py --ref origin/main --json

Exit codes: 0 ok, 2 mechanism failure (git archive / extract), 3 empty result.
"""

from __future__ import annotations

import argparse
import io
import json
import os
import subprocess
import sys
import tarfile
import time

REPO_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DEFAULT_DEST = os.path.join(os.path.dirname(REPO_ROOT), "_upstream_mirror")
DEFAULT_PATHS = ["scripts", "Tools", "firm", "docs", "research", "fleet"]
MANIFEST = "UPSTREAM-MIRROR.json"


def _git(args: list[str], timeout: int = 1800) -> subprocess.CompletedProcess:
    return subprocess.run(
        ["git"] + args,
        cwd=REPO_ROOT,
        capture_output=True,
        timeout=timeout,
    )


def _resolve(ref: str) -> str:
    proc = _git(["rev-parse", "--verify", ref])
    if proc.returncode != 0:
        raise SystemExit(f"cannot resolve {ref}: {proc.stderr.decode('utf-8', 'replace').strip()}")
    return proc.stdout.decode().strip()


def _archive(ref: str, paths: list[str]) -> bytes:
    """git archive into memory; promisor lazy-fetches only the blobs it needs."""
    proc = subprocess.run(
        ["git", "archive", "--format=tar", ref] + paths,
        cwd=REPO_ROOT,
        capture_output=True,
        timeout=3600,
    )
    if proc.returncode != 0:
        sys.stdout.write(
            json.dumps({"status": "FAIL", "stage": "archive",
                        "rc": proc.returncode,
                        "err": proc.stderr.decode("utf-8", "replace")[-800:]}) + "\n"
        )
        raise SystemExit(2)
    if not proc.stdout:
        raise SystemExit(3)
    return proc.stdout


def _extract(blob: bytes, dest: str) -> dict:
    per_scope: dict[str, dict] = {}
    with tarfile.open(fileobj=io.BytesIO(blob), mode="r:") as tf:
        for member in tf.getmembers():
            tf.extract(member, dest)
            if not member.isfile():
                continue
            scope = member.name.split("/", 1)[0]
            row = per_scope.setdefault(scope, {"files": 0, "bytes": 0})
            row["files"] += 1
            row["bytes"] += member.size
    return per_scope


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--ref", default="origin/main")
    ap.add_argument("--paths", nargs="+", default=DEFAULT_PATHS)
    ap.add_argument("--dest", default=DEFAULT_DEST)
    ap.add_argument("--json", action="store_true")
    args = ap.parse_args(argv)

    started = time.time()
    sha = _resolve(args.ref)
    blob = _archive(args.ref, args.paths)
    os.makedirs(args.dest, exist_ok=True)
    per_scope = _extract(blob, args.dest)

    receipt = {
        "status": "OK",
        "ref": args.ref,
        "sha": sha,
        "dest": args.dest,
        "paths": args.paths,
        "scopes": per_scope,
        "tar_bytes": len(blob),
        "elapsed_sec": round(time.time() - started, 1),
        "generated": time.strftime("%Y-%m-%dT%H:%M:%S%z"),
        "note": "read-only mirror; HEAD/index/work tree untouched",
    }
    with open(os.path.join(args.dest, MANIFEST), "w", encoding="utf-8") as fh:
        json.dump(receipt, fh, indent=1, sort_keys=True)
        fh.write("\n")
    print(json.dumps(receipt, sort_keys=True) if args.json else
          " ".join(f"{k}={v['files']}" for k, v in sorted(per_scope.items()))
          + f" tar_MB={len(blob)/1048576:.1f} sec={receipt['elapsed_sec']} sha={sha[:9]}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())