# -*- coding: utf-8 -*-
"""R246 bm-a rebase-replay resolver (25-file UU batch, 11th collision family run).

Rebase face: :2 = origin/bm-b side (HEAD), :3 = my replayed commit (bm-a, newer
12:46-12:48 vs bm-b 12:44-12:47 per probe _r246bma_probe.py).
Recipes per skill canon:
- rolling-ledger (compute_audit, regime_state): union history/transitions both
  blobs zero loss (line/row identity dedup, |A u B| anchor), state fields take-new.
- append-log (x2_watch_log.jsonl): line-level union zero loss.
- snapshots/twins/deterministic-regen (all 22 others): take :3 whole bytes
  (mine newest per embedded ts; js wrapper preserved by whole-byte take, R209;
  daily_report md follows its json twin side; paper_export/daily_scorecard
  deterministic regen take-mine per R236 precedent).
Fail-closed: every resolved json parse-verified, js wrapper asserted, ledger
union anchors asserted BEFORE git add. Exit 0 = safe to add+continue.
"""
import io
import json
import subprocess
import sys

def blob(rev):
    p = subprocess.run(["git", "show", rev], capture_output=True)
    if p.returncode != 0:
        sys.exit(f"FATAL: git show {rev} rc={p.returncode}")
    return p.stdout

TAKE3 = [
    "results/dashboard_status.js", "results/dashboard_status.json",
    "results/fundamental_b_layer_filter.json", "results/futures_update_status.json",
    "results/heat_update_status.json", "results/lhb_update_status.json",
    "results/token_usage.json", "results/update_status.json",
    "docs/daily_report/REPORT-2026-09-26.json", "docs/daily_report/REPORT-2026-09-26.md",
    "results/daily_scorecard.json",
    "results/paper/COMPOSITE-CE-01_paper.json", "results/paper/COMPOSITE-CE-02_paper.json",
    "results/paper/DROUGHT-CE-01_paper.json", "results/paper/ENGULF-CE-01_paper.json",
    "results/paper/NEEDLE-DE-01_paper.json", "results/paper/VOLATILITY-CE-01_paper.json",
    "results/paper_export/export-2026-09-24.json", "results/paper_export/latest.json",
    "results/prospect_paper/_summary.json", "results/prospect_promotion/_summary.json",
    "results/t35_open_fill_verify.json",
]
ANCHORS = {}

def write(path, data):
    io.open(path, "wb").write(data)

# ---- 1) take-:3 whole bytes (snapshots/twins/deterministic) ----
for f in TAKE3:
    b3 = blob(f":3:{f}")
    b2 = blob(f":2:{f}")
    assert b3, f"empty :3 for {f}"
    write(f, b3)
    if f.endswith(".json"):
        j = json.loads(b3)          # parse-verify before add (r185)
        assert isinstance(j, dict) or isinstance(j, list), f
    if f == "results/dashboard_status.js":
        assert b3.startswith(b"window.DASH_DATA") or b"window.DASH_DATA" in b3[:200], \
            "js wrapper stripped (R209)"
    # twin side coherence: daily_report md takes :3 alongside its json twin (same side by law)
ANCHORS["take3_count"] = len(TAKE3)

# ---- 2) compute_audit.json: rolling-ledger union + state take-new ----
f = "results/compute_audit.json"
a2 = json.loads(blob(f":2:{f}"))
a3 = json.loads(blob(f":3:{f}"))
h2 = a2.get("history", [])
h3 = a3.get("history", [])
rows = {json.dumps(r, sort_keys=True, ensure_ascii=False): r for r in h2}
for r in h3:
    rows.setdefault(json.dumps(r, sort_keys=True, ensure_ascii=False), r)
union = list(rows.values())
union.sort(key=lambda r: r.get("ts", ""))          # ts-ascending producer order (R215 order-face law)
merged = dict(a3)                                   # my state face newer (ts probe)
merged["history"] = union
write(f, json.dumps(merged, ensure_ascii=False, indent=2).encode("utf-8"))
json.loads(io.open(f, encoding="utf-8").read())     # re-parse verify
ANCHORS["compute_audit_union"] = {"|A|": len(h2), "|B|": len(h3), "|AuB|": len(union),
                                  "zero_loss": len(union) >= max(len(h2), len(h3)),
                                  "state_ts": a3.get("ts"), "other_ts": a2.get("ts")}
assert len(union) >= max(len(h2), len(h3)), "history union lost rows"

# ---- 3) regime_state.json: rolling-ledger union + state take-new ----
f = "results/regime_state.json"
a2 = json.loads(blob(f":2:{f}"))
a3 = json.loads(blob(f":3:{f}"))
for key in ("history", "transitions"):
    h2 = a2.get(key, [])
    h3 = a3.get(key, [])
    rows = {json.dumps(r, sort_keys=True, ensure_ascii=False): r for r in h2}
    for r in h3:
        rows.setdefault(json.dumps(r, sort_keys=True, ensure_ascii=False), r)
    union = list(rows.values())
    a3[key] = union
    ANCHORS[f"regime_{key}"] = {"|A|": len(h2), "|B|": len(h3), "|AuB|": len(union)}
    assert len(union) >= max(len(h2), len(h3)), f"regime {key} union lost rows"
write(f, json.dumps(a3, ensure_ascii=False, indent=1).encode("utf-8"))
json.loads(io.open(f, encoding="utf-8").read())

# ---- 4) x2_watch_log.jsonl: line-level union zero loss ----
f = "results/x2_watch_log.jsonl"
l2 = blob(f":2:{f}").decode("utf-8").splitlines()
l3 = blob(f":3:{f}").decode("utf-8").splitlines()
seen = set()
union = []
for ln in l2 + l3:
    if ln not in seen:
        seen.add(ln)
        union.append(ln)
write(f, ("\n".join(union) + "\n").encode("utf-8"))
ANCHORS["x2_union"] = {"|A|": len(l2), "|B|": len(l3), "|AuB|": len(union)}
assert len(union) >= max(len(l2), len(l3)), "x2 union lost lines"

# ---- 5) conflict-marker fail-closed scan on all resolved files ----
ALL = TAKE3 + ["results/compute_audit.json", "results/regime_state.json",
               "results/x2_watch_log.jsonl"]
for f in ALL:
    body = io.open(f, "rb").read()
    assert b"<<<<<<<" not in body and b">>>>>>>" not in body, f"markers left in {f}"

print(json.dumps({"resolved": len(ALL), "anchors": ANCHORS,
                  "verdict": "OK: parse-verified, unions zero-loss, wrapper intact"},
                 ensure_ascii=False, indent=1))
