"""r295 bm-b 5x ledger real-read scan: unified trials chain audit (v2).

Checks every results batch file carrying a trials_ledger block:
- per-file internal balance: prev_total + batch_trials == total
- duplicate batch ids with DIFFERING (prev,total) = double-count face
- chain continuity by prev_total walk; head = max int total
Prints tail links for the 5x reconciliation record.
"""
import glob
import json
import os

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SKIP = ("/paper/", "/t22/", "/aggr_paper/", "/alloc_paper/", "/grid_paper/",
        "/prospect_g2/", "/market_clock/", "/ext_slots_pull_status")

rows = []
for path in glob.glob(os.path.join(ROOT, "results", "**", "*.json"), recursive=True):
    rel = os.path.relpath(path, ROOT).replace("\\", "/")
    if rel.startswith("data/") or any(s in rel for s in SKIP):
        continue
    try:
        with open(path, "r", encoding="utf-8-sig") as fh:
            obj = json.load(fh)
    except Exception:
        continue
    if not isinstance(obj, dict):
        continue
    led = obj.get("trials_ledger")
    if not isinstance(led, dict) or "total" not in led:
        continue
    rows.append({
        "file": rel,
        "batch": led.get("batch"),
        "prev": led.get("prev_total"),
        "delta": led.get("batch_trials"),
        "total": led.get("total"),
    })

rows.sort(key=lambda r: (r["prev"] if isinstance(r["prev"], int) else -1, r["file"]))
ints = [r for r in rows if isinstance(r["total"], int)]
print("N_BATCH_FILES=%d (int-total=%d)" % (len(rows), len(ints)))
bad = [r for r in rows if isinstance(r.get("prev"), int) and isinstance(r.get("delta"), int)
       and r["prev"] + r["delta"] != r["total"]]
print("INTERNAL_BALANCE_FAIL=%d" % len(bad))
for r in bad:
    print("  BAD:", r["file"], r["prev"], r["delta"], r["total"])

seen = {}
dups = []
for r in rows:
    key = r.get("batch")
    if not key:
        continue
    sig = (r.get("prev"), r.get("total"))
    if key in seen and seen[key] != sig:
        dups.append((key, seen[key], sig))
    seen[key] = sig
print("DUP_BATCH_CONFLICTS=%d" % len(dups))
for key, sa, sb in dups:
    print("  DUP: %s %s vs %s" % (key, sa, sb))

head = max(ints, key=lambda r: r["total"])
print("HEAD=%s total=%d (file=%s prev=%s delta=%s)" % (
    head["batch"], head["total"], head["file"], head["prev"], head["delta"]))

# continuity walk over int rows sorted by prev
run = None
gaps = []
for r in ints:
    if run is not None and isinstance(r["prev"], int) and r["prev"] != run:
        gaps.append((run, r["prev"], r["batch"], r["file"]))
    run = r["total"]
print("CHAIN_GAPS=%d" % len(gaps))
for g in gaps:
    print("  GAP: running=%d -> next prev=%d (%s %s)" % (g[0], g[1], g[2] or "?", g[3]))

print("TAIL:")
for r in rows[-7:]:
    print("  %s | %s | prev=%s +%s = %s" % (r["file"], r["batch"] or "?", r["prev"], r["delta"], r["total"]))
