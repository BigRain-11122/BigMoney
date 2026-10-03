#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""r639 bm-b main-worktree post-merge sync, take 2 (r630 net path tail).

Adopted from _r639bmb_wtsync.py (dead-session tool, reuse-not-rewrite):
OLD_HEAD is now the pre-merge autofill commit 375368771; new HEAD is the
pushed merge 758fd3eed. Same live-face exclusions and mtime guards.
NOTE (pit entry ①, this round): git checkout --pathspec-from-file=<f>
must be called WITHOUT a preceding `--`.
"""
import os
import subprocess
import sys
import time

REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OLD_HEAD = "375368771"

LIVE_FACES = {
    "results/autofill_state.bm-b.json",
    "results/fund_divlowvol_p1/nulls.jsonl",
    "results/fund_quality_p1/nulls.jsonl",
    "results/fund_value_p1/nulls.jsonl",
    "results/p1d_gates.json",
    "results/saturation_engine/face_bm-b.json",
    "results/saturation_engine/history_bm-b.jsonl",
    "results/saturation_engine/state_bm-b.json",
}
MTIME_GUARDED = {
    "results/crash_fuse.json",
    "results/x2_watch_log.jsonl",
    "results/gate_attrition.json",
}


def git(*args):
    r = subprocess.run(["git", "-C", REPO] + list(args),
                       capture_output=True, text=True, encoding="utf-8")
    if r.returncode != 0:
        raise RuntimeError("git %s rc=%s\n%s" % (args, r.returncode, r.stderr))
    return r.stdout


def main():
    changed = git("diff", "--name-only", OLD_HEAD, "HEAD").split()
    now = time.time()
    skipped, checkout = [], []
    for p in changed:
        if p in LIVE_FACES:
            skipped.append((p, "live daemon face"))
            continue
        if p in MTIME_GUARDED:
            fp = os.path.join(REPO, *p.split("/"))
            if os.path.exists(fp) and (now - os.path.getmtime(fp)) < 900:
                skipped.append((p, "mtime-guarded live (%.0fs ago)" % (now - os.path.getmtime(fp))))
                continue
        checkout.append(p)
    spec = os.path.join(REPO, "results", "_r639bmb_wtsync2_paths.txt")
    with open(spec, "w", encoding="utf-8", newline="\n") as f:
        f.write("\n".join(checkout) + "\n")
    git("checkout", "--pathspec-from-file=" + spec)
    report = {"checkout_count": len(checkout), "skipped": skipped,
              "checkout": checkout}
    import json
    out = os.path.join(REPO, "results", "_r639bmb_wtsync2_report.json")
    with open(out, "w", encoding="utf-8", newline="\n") as f:
        json.dump(report, f, ensure_ascii=False, indent=1)
    print("checked out %d files; skipped %d live faces" % (len(checkout), len(skipped)))
    for p, why in skipped:
        print("SKIP %s (%s)" % (p, why))


if __name__ == "__main__":
    main()
