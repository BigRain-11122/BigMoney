# -*- coding: utf-8 -*-
"""r757 bm-c S0 probe: round-start dirty classification, fetch, ahead/behind,
marks-lane row count (lunch-break window; 13:00 review-window rows expected
next rounds per r756 next-pointer), receipt to results/_r757bmc_s0_probe.json.
Hand-written fresh per boot self-clone pit law (r753 -> pit-lineage.md):
NEVER clone a previous-round boot/S0 script."""
import datetime
import json
import os
import subprocess

ROOT = r"K:\Fluxgroup\FluxGroup\quant\bigmoney"
CF = 0x08000000  # CREATE_NO_WINDOW


def git(args):
    p = subprocess.run(["git", "-C", ROOT] + args, capture_output=True,
                       creationflags=CF)
    return (p.returncode, p.stdout.decode("utf-8", "replace"),
            p.stderr.decode("utf-8", "replace"))


probe = {"ts": datetime.datetime.now().astimezone().isoformat(timespec="seconds")}
rc, out, err = git(["status", "--porcelain"])
dirty = [ln for ln in out.splitlines() if ln.strip()]
probe["dirty_count"] = len(dirty)
probe["dirty"] = dirty
rc, out, err = git(["fetch", "origin"])
probe["fetch_rc"] = rc
if rc != 0:
    probe["fetch_err"] = err[:300]
rc, out, err = git(["rev-list", "--left-right", "--count", "HEAD...origin/main"])
probe["ahead_behind"] = out.strip()
rc, out, err = git(["log", "-1", "--format=%h %s"])
probe["head"] = out.strip()

marks_path = os.path.join(ROOT, "results", "paper", "marks", "marks-20261008.jsonl")
rows = []
if os.path.exists(marks_path):
    with open(marks_path, encoding="utf-8", errors="replace") as fh:
        rows = [ln.strip() for ln in fh if ln.strip()]
probe["marks_rows"] = len(rows)
probe["marks_last"] = rows[-1][:220] if rows else ""
probe["marks_all_ts"] = [r[:40] for r in rows]

out_path = os.path.join(ROOT, "results", "_r757bmc_s0_probe.json")
with open(out_path, "w", encoding="utf-8") as fh:
    json.dump(probe, fh, indent=1, ensure_ascii=False)
print(json.dumps(probe, indent=1, ensure_ascii=False))
