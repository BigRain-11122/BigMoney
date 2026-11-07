"""Divergence report: is this checkout's work visible to the fleet, or stranded?

Motivation (bm-a r1268): 28 local commits had accumulated that were neither on
origin/main nor patch-equivalent to anything upstream.  Every prior round had
committed fine; the only failing step was the integration (non-fast-forward),
and nothing on the machine said so in a machine-readable way.  This tool answers
three questions with git plumbing only (no network, no tree mutation):

  1. how far apart are HEAD and origin/main (ahead/behind),
  2. are the local commits *unique* work or patch-twins of upstream commits
     (``git cherry``: '-' = equivalent patch already upstream, '+' = not),
  3. if we tried to integrate today, which paths would collide
     (``git merge-tree --write-tree --name-only`` in a temp object space).

Exit codes: 0 = in sync or replayed-cleanly, 1 = integration hits conflicts,
2 = stranded unique commits but no conflict preview available.

Usage:
  python scripts/git_divergence_report.py [--remote-branch origin/main] [--json path]
  python scripts/git_divergence_report.py --selftest
"""

from __future__ import annotations

import argparse
import json
import os
import subprocess
import sys
import time

DEFAULT_OUT = os.path.join("results", "git_divergence_report.json")


def git(*args: str, cwd: str | None = None, check: bool = False) -> subprocess.CompletedProcess:
    p = subprocess.run(["git", *args], cwd=cwd, capture_output=True, text=True,
                       encoding="utf-8", errors="replace")
    if check and p.returncode != 0:
        raise RuntimeError(f"git {' '.join(args)} failed: {p.stderr.strip()[:400]}")
    return p


def repo_root() -> str:
    p = git("rev-parse", "--show-toplevel", check=True)
    return p.stdout.strip()


def ahead_behind(root: str, remote_branch: str, head: str = "HEAD") -> tuple[int, int]:
    p = git("rev-list", "--left-right", "--count", f"{remote_branch}...{head}", cwd=root)
    if p.returncode != 0:
        return (-1, -1)
    behind, ahead = p.stdout.split()
    return int(ahead), int(behind)


def cherry(root: str, remote_branch: str, head: str = "HEAD") -> tuple[int, int, list[str]]:
    """Return (unique, already_upstream, sample_unique_subjects)."""
    p = git("cherry", remote_branch, head, cwd=root)
    if p.returncode != 0:
        return (-1, -1, [])
    unique = already = 0
    sample: list[str] = []
    for line in p.stdout.splitlines():
        if not line.strip():
            continue
        kind, sha = line[0], line[2:].strip()
        if kind == "+":
            unique += 1
            if len(sample) < 5:
                s = git("log", "-1", "--format=%s", sha, cwd=root).stdout.strip()
                sample.append(f"{sha[:10]} {s}")
        elif kind == "-":
            already += 1
    return unique, already, sample


def conflict_preview(root: str, remote_branch: str, head: str = "HEAD") -> dict:
    """Paths that a rebase/merge onto remote_branch would leave conflicted."""
    p = git("merge-tree", "--write-tree", "--name-only", remote_branch, head, cwd=root)
    if p.returncode == 0:
        return {"status": "clean", "paths": []}
    if p.returncode == 1:
        # rc1 == conflicts; first line is the tree oid, remaining lines are the
        # "Auto-merging ..." / "CONFLICT (...) ..." chatter followed by raw paths
        lines = [ln.strip() for ln in p.stdout.splitlines() if ln.strip()]
        paths = sorted({ln for ln in lines[1:]
                        if not ln.startswith(("Auto-merging", "CONFLICT", "changed in"))
                        and ("/" in ln or "." in ln)})
        return {"status": "conflicted", "paths": paths[:60], "n_paths": len(paths)}
    return {"status": "unsupported", "paths": [], "stderr": p.stderr.strip()[:300]}


def build(root: str, remote_branch: str) -> dict:
    head_sha = git("rev-parse", "HEAD", cwd=root).stdout.strip()
    remote_sha = git("rev-parse", remote_branch, cwd=root).stdout.strip()
    ahead, behind = ahead_behind(root, remote_branch)
    unique, already, sample = cherry(root, remote_branch)
    preview = conflict_preview(root, remote_branch)

    if ahead == 0:
        verdict = "IN_SYNC"
    elif unique == 0:
        verdict = "TWINS_ONLY"          # everything local is already upstream: reset is safe
    elif preview["status"] == "conflicted":
        verdict = "STRANDED_CONFLICTS"  # unique work that cannot replay cleanly today
    elif preview["status"] == "clean":
        verdict = "STRANDED_REPLAYABLE"  # unique work that would rebase cleanly
    else:
        verdict = "STRANDED_UNKNOWN"

    return {
        "generated_at": time.strftime("%Y-%m-%dT%H:%M:%S%z"),
        "machine_id": _machine_id(root),
        "head": head_sha,
        "remote_branch": remote_branch,
        "remote_sha": remote_sha,
        "ahead": ahead,
        "behind": behind,
        "unique_commits": unique,
        "already_upstream_commits": already,
        "unique_sample": sample,
        "conflict_preview": preview,
        "verdict": verdict,
        "read": _read(verdict, ahead, behind, unique, already, preview),
    }


def _machine_id(root: str) -> str:
    p = os.path.join(root, "fleet", "machine.json")
    try:
        with open(p, encoding="utf-8") as fh:
            return str(json.load(fh).get("machine_id") or "unknown")
    except (OSError, ValueError):
        return "unknown"


def _read(verdict: str, ahead: int, behind: int, unique: int, already: int,
          preview: dict) -> str:
    if verdict == "IN_SYNC":
        return "this checkout is the same commit as the remote branch"
    if verdict == "TWINS_ONLY":
        return (f"{ahead} commit(s) ahead but {already} carry patches already upstream -- "
                "nothing unique would be lost by resetting to the remote tip")
    if verdict == "STRANDED_CONFLICTS":
        return (f"{unique} commit(s) of unique work cannot replay cleanly onto the remote: "
                f"{preview.get('n_paths', len(preview['paths']))} path(s) collide -- "
                "preserve on a machine branch, then integrate with a canon recipe; "
                "do not force-push and do not discard")
    if verdict == "STRANDED_REPLAYABLE":
        return (f"{unique} commit(s) of unique work would rebase cleanly onto the remote "
                f"({behind} commit(s) behind) -- integration is available")
    return (f"{unique} commit(s) of unique work, {behind} behind; conflict preview "
            "unavailable on this git build (needs merge-tree --write-tree, git>=2.38)")


def _selftest() -> int:
    import tempfile
    checks: list[tuple[str, bool]] = []

    with tempfile.TemporaryDirectory() as tmp:
        git("init", "-q", "-b", "main", cwd=tmp)
        git("config", "user.email", "t@t", cwd=tmp)
        git("config", "user.name", "t", cwd=tmp)
        with open(os.path.join(tmp, "a.txt"), "w", encoding="utf-8") as fh:
            fh.write("one\n")
        git("add", "a.txt", cwd=tmp)
        git("commit", "-qm", "base", cwd=tmp)
        base = git("rev-parse", "HEAD", cwd=tmp).stdout.strip()
        git("branch", "remote/main", cwd=tmp)  # simulate origin/main at base

        checks.append(("in-sync reads IN_SYNC", build(tmp, "remote/main")["verdict"] == "IN_SYNC"))

        # twin: same patch content committed again locally
        with open(os.path.join(tmp, "a.txt"), "w", encoding="utf-8") as fh:
            fh.write("two\n")
        git("commit", "-qam", "local change", cwd=tmp)
        # replay the identical patch onto remote/main as a separate commit
        git("checkout", "-q", "remote/main", cwd=tmp)
        with open(os.path.join(tmp, "a.txt"), "w", encoding="utf-8") as fh:
            fh.write("two\n")
        git("commit", "-qam", "upstream change", cwd=tmp)
        git("checkout", "-q", "main", cwd=tmp)
        d = build(tmp, "remote/main")
        checks.append(("patch-identical commit reads TWINS_ONLY", d["verdict"] == "TWINS_ONLY"))

        # both sides rewrite the same line relative to the base -> unique + conflict
        git("checkout", "-q", "-B", "main", base, cwd=tmp)
        with open(os.path.join(tmp, "a.txt"), "w", encoding="utf-8") as fh:
            fh.write("local rewrite\n")
        git("commit", "-qam", "unique local", cwd=tmp)
        git("checkout", "-q", "remote/main", cwd=tmp)
        with open(os.path.join(tmp, "a.txt"), "w", encoding="utf-8") as fh:
            fh.write("remote rewrite\n")
        git("commit", "-qam", "upstream rewrite", cwd=tmp)
        git("checkout", "-q", "main", cwd=tmp)
        d = build(tmp, "remote/main")
        checks.append(("unique conflicting work reads STRANDED_CONFLICTS",
                       d["verdict"] == "STRANDED_CONFLICTS"))
        checks.append(("conflict preview names the colliding path",
                       "a.txt" in d["conflict_preview"]["paths"]))
        checks.append(("ahead/behind counted", d["ahead"] == 1 and d["behind"] == 2))

        # unique but non-overlapping -> replayable
        git("checkout", "-q", "-B", "main", "remote/main", cwd=tmp)
        with open(os.path.join(tmp, "b.txt"), "w", encoding="utf-8") as fh:
            fh.write("mine\n")
        git("add", "b.txt", cwd=tmp)
        git("commit", "-qm", "unique add", cwd=tmp)
        d = build(tmp, "remote/main")
        checks.append(("non-overlapping unique work reads STRANDED_REPLAYABLE",
                       d["verdict"] == "STRANDED_REPLAYABLE"))

    failed = [n for n, ok in checks if not ok]
    for name, ok in checks:
        print(f"{'PASS' if ok else 'FAIL'} {name}")
    print(f"selftest {len(checks) - len(failed)}/{len(checks)}")
    return 0 if not failed else 1


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--remote-branch", default="origin/main")
    ap.add_argument("--json", default=DEFAULT_OUT)
    ap.add_argument("--selftest", action="store_true")
    args = ap.parse_args(argv)

    if args.selftest:
        return _selftest()

    root = repo_root()
    if git("rev-parse", "--verify", args.remote_branch, cwd=root).returncode != 0:
        print(f"[ERROR] remote branch ref {args.remote_branch} not found -- fetch first",
              file=sys.stderr)
        return 2

    rep = build(root, args.remote_branch)
    out = args.json if os.path.isabs(args.json) else os.path.join(root, args.json)
    os.makedirs(os.path.dirname(out), exist_ok=True)
    with open(out, "w", encoding="utf-8") as fh:
        json.dump(rep, fh, ensure_ascii=False, indent=1, sort_keys=True)
        fh.write("\n")

    print(f"verdict={rep['verdict']} ahead={rep['ahead']} behind={rep['behind']} "
          f"unique={rep['unique_commits']} twins={rep['already_upstream_commits']}")
    print(f"read: {rep['read']}")
    print(f"face: {out}")

    if rep["verdict"] in ("IN_SYNC", "TWINS_ONLY", "STRANDED_REPLAYABLE"):
        return 0
    if rep["verdict"] == "STRANDED_CONFLICTS":
        return 1
    return 2


if __name__ == "__main__":
    raise SystemExit(main())