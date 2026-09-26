# -*- coding: utf-8 -*-
"""R252 bm-a: ledger-chain break census (deterministic, read-only).

ledger_head() scans ONLY top-level "trials_ledger". Family runners that
embedded append_ledger() blocks under key "ledger" are INVISIBLE to the
chain -> their trials never entered N_eff, and every subsequent batch
chained from a stale head. This census enumerates:
  A) correct-key chain members (top-level trials_ledger dict with total);
  B) broken-key members (top-level "ledger" dict with prev/batch/total);
  C) chronological true-chain reconstruction (by block ts > file git mtime
     > file mtime), with per-batch stale-vs-true prev/total deltas.
"""
import glob
import json
import os
import subprocess

rows = []
for path in sorted(glob.glob(os.path.join("results", "**", "*.json"),
                             recursive=True)):
    try:
        with open(path, encoding="utf-8") as fh:
            d = json.load(fh)
    except Exception:
        continue
    if not isinstance(d, dict):
        continue
    tl = d.get("trials_ledger")
    lg = d.get("ledger")
    blk = None
    kind = None
    if isinstance(tl, dict) and "total" in tl:
        blk, kind = tl, "correct"
    elif isinstance(lg, dict) and {"prev_total", "batch_trials", "total"} <= set(lg):
        blk, kind = lg, "BROKEN_KEY"
    if blk is None:
        continue
    ts = blk.get("ts") or blk.get("as_of") or ""
    gt = ""
    try:
        r = subprocess.run(["git", "log", "-1", "--format=%cI", "--", path],
                           capture_output=True, text=True)
        gt = r.stdout.strip()[:19]
    except Exception:
        pass
    mt = os.path.getmtime(path)
    rows.append({
        "file": path.replace("\\", "/"),
        "kind": kind,
        "batch": blk.get("batch"),
        "prev": blk.get("prev_total"),
        "trials": blk.get("batch_trials"),
        "total": blk.get("total"),
        "block_ts": ts,
        "git_last": gt,
        "mtime": mt,
    })

rows.sort(key=lambda r: (r["block_ts"] or r["git_last"] or "", r["mtime"]))
true_prev = 0
true_chain = []
head_correct = 0
for r in rows:
    if r["kind"] == "correct" and r["total"] is not None:
        head_correct = max(head_correct, int(r["total"]))
for r in rows:
    tp = int(r["prev"] or 0)
    true_chain.append((r["file"], r["kind"], r["batch"], r["prev"], r["trials"],
                       r["total"], r["block_ts"] or r["git_last"]))
print(f"{'file':64s} {'kind':11s} {'batch':28s} prev->total trials ts")
for row in true_chain:
    print(f"{row[0]:64s} {row[1]:11s} {str(row[2]):28s} {row[3]}->{row[5]} +{row[4]} {row[6]}")
print()
print("max correct-key total (current scanner head):", head_correct)
