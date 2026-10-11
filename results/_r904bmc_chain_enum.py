"""r904: trials-ledger chain enumeration probe (read-only) -- r518 fork detection.

Scans results/**/*.json (skipping _quarantine per r685 law) for ledger blocks
in both nested science_gates.ledger (r459) and top-level trials_ledger faces,
prints the chain tail sorted by total, flags same-prev multi-child forks.
"""
import glob
import json
import os

blocks = []
skip = os.sep + "_quarantine" + os.sep
for path in glob.glob(r"results\**\*.json", recursive=True):
    if skip in path:
        continue
    try:
        with open(path, encoding="utf-8") as f:
            d = json.load(f)
    except Exception:
        continue
    if not isinstance(d, dict):
        continue
    cand = []
    sg = d.get("science_gates")
    if isinstance(sg, dict) and isinstance(sg.get("ledger"), dict):
        cand.append(sg["ledger"])
    if isinstance(d.get("trials_ledger"), dict):
        cand.append(d["trials_ledger"])
    for b in cand:
        if isinstance(b.get("prev_total"), int) and isinstance(b.get("total"), int):
            blocks.append({
                "file": path.replace("results" + os.sep, "").replace(os.sep, "/"),
                "batch": b.get("batch"),
                "prev": b["prev_total"],
                "trials": b.get("batch_trials"),
                "total": b["total"],
            })

blocks.sort(key=lambda x: x["total"])
print("total blocks:", len(blocks))
for b in blocks[-14:]:
    print(f"  total={b['total']:>9} prev={b['prev']:>9} trials={b['trials']:>5} {b['batch']} <- {b['file']}")

heads = max(b["total"] for b in blocks)
print("ledger_head (max total):", heads)

by_prev = {}
for b in blocks:
    by_prev.setdefault(b["prev"], []).append(b)
forks = {p: kids for p, kids in by_prev.items() if len(kids) > 1}
print("FORKS (same prev, multi-child):", len(forks))
for p, kids in forks.items():
    print(f"  prev={p}:")
    for k in kids:
        print(f"    -> total={k['total']} trials={k['trials']} {k['batch']} ({k['file']})")
