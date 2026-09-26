# -*- coding: utf-8 -*-
"""R247 bm-a rebase-replay resolver (24-file UU batch, 12th collision family run).

Take-sides are PROBE-DERIVED this round (results/_r247bma_probe.py), not
assumed: every ts-probed file shows :3 (bm-a 13:33-13:35) strictly newer than
:2 (bm-b 13:22-13:23) -- daily_report 13:34:49>13:23:15, futures 13:33:59,
heat 13:33:59, lhb 13:33:51, update_status 13:33:37, token 13:34:51,
t35_open_fill 13:34:25, prospect twins 13:34:2x/3x, paper x6 13:34:2x,
fundamental_blf 13:34:21, regime 13:33:38, autofill last_tick 13:30:01
> 13:20:01. Byte-blind files (scorecard/dashboard twins/paper_export twins:
no top-level ts keys) are byte-compared; a real diff -> take :3 per R236
deterministic-regen take-mine precedent (later run consumed fresher inputs),
identity -> either side.

Recipes per skill canon:
- memory-union CODELY.md: :2 lines + :3-unique non-empty lines (both machines'
  new entries kept, dedupe identical).
- mixed-dict+ledger autofill_state.json: base :3 (newer last_tick),
  launches = union dedupe -> ts-desc cap 50 -> write-back ts-ASCENDING
  (r244/r245 cap-vs-format law), isinstance(last_tick, dict) assert.
- rolling-ledger compute_audit.json: history union zero-loss ts-ascending,
  state face :3 (newer run).
- rolling-ledger regime_state.json: history/transitions union zero-loss,
  state :3.
- append-log x2_watch_log.jsonl: line-level union zero loss.
- snapshots/twins/deterministic-regen (rest): take :3 whole bytes (probe-
  verified newest; js wrapper asserted intact, R209; md twin follows its
  json twin side).
Fail-closed: every json parse-verified, js wrapper asserted, union anchors
asserted, conflict-marker scan, BEFORE git add. Exit 0 = safe to add+continue.
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


def write(path, data):
    io.open(path, "wb").write(data)


ANCHORS = {}

TAKE3 = [
    "docs/daily_report/REPORT-2026-09-26.json",
    "docs/daily_report/REPORT-2026-09-26.md",
    "results/daily_scorecard.json",
    "results/dashboard_status.js", "results/dashboard_status.json",
    "results/fundamental_b_layer_filter.json",
    "results/futures_update_status.json", "results/heat_update_status.json",
    "results/lhb_update_status.json", "results/update_status.json",
    "results/token_usage.json", "results/t35_open_fill_verify.json",
    "results/prospect_paper/_summary.json",
    "results/prospect_promotion/_summary.json",
    "results/paper_export/export-2026-09-24.json",
    "results/paper_export/latest.json",
    "results/paper/COMPOSITE-CE-01_paper.json",
    "results/paper/COMPOSITE-CE-02_paper.json",
    "results/paper/DROUGHT-CE-01_paper.json",
    "results/paper/ENGULF-CE-01_paper.json",
    "results/paper/NEEDLE-DE-01_paper.json",
    "results/paper/VOLATILITY-CE-01_paper.json",
]

# ---- 1) take-:3 whole bytes (probe-verified newest side) ----
for f in TAKE3:
    b3, b2 = blob(f":3:{f}"), blob(f":2:{f}")
    assert b3, f"empty :3 for {f}"
    identical = (b3 == b2)
    write(f, b3)
    if f.endswith(".json"):
        json.loads(b3)                     # parse-verify before add (r185)
    if f == "results/dashboard_status.js":
        assert b"window.DASH_DATA" in b3[:200], "js wrapper stripped (R209)"
    ANCHORS[f] = {"take": ":3", "byte_identical": bool(identical)}

# ---- 2) CODELY.md memory-union: :2 + :3-unique non-empty lines ----
f = "CODELY.md"
l2 = blob(f":2:{f}").decode("utf-8").splitlines()
l3 = blob(f":3:{f}").decode("utf-8").splitlines()
s2 = set(l2)
uniq3 = [ln for ln in l3 if ln not in s2 and ln.strip()]
union = l2 + uniq3
body = "\n".join(union) + "\n"
write(f, body.encode("utf-8"))
ANCHORS["codely_union"] = {"|L2|": len(l2), "|L3|": len(l3),
                          "kept_bm-b_side": len(l2),
                          "appended_mine": len(uniq3),
                          "appended_heads": [ln[:48] for ln in uniq3]}
assert uniq3, "CODELY union lost my new entry"

# ---- 3) autofill_state.json: mixed-dict+ledger ----
f = "results/autofill_state.json"
a2 = json.loads(blob(f":2:{f}"))
a3 = json.loads(blob(f":3:{f}"))
lt2 = a2.get("last_tick", {}).get("ts")
lt3 = a3.get("last_tick", {}).get("ts")
assert lt3 and lt2 and lt3 > lt2, f"last_tick ts probe unexpected: {lt2} vs {lt3}"
rows = {json.dumps(r, sort_keys=True, ensure_ascii=False): r
        for r in a2.get("launches", [])}
for r in a3.get("launches", []):
    rows.setdefault(json.dumps(r, sort_keys=True, ensure_ascii=False), r)
union_rows = list(rows.values())
union_rows.sort(key=lambda r: r.get("ts", ""), reverse=True)
capped = union_rows[:50]
capped.sort(key=lambda r: r.get("ts", ""))     # write-back ts-ascending (r245 law)
merged = dict(a3)                              # newer last_tick side
merged["launches"] = capped
write(f, json.dumps(merged, ensure_ascii=False, indent=1).encode("utf-8"))
chk = json.loads(io.open(f, encoding="utf-8").read())
assert isinstance(chk["last_tick"], dict), "last_tick not dict (r220)"
ANCHORS["autofill"] = {"launches_2": len(a2.get("launches", [])),
                       "launches_3": len(a3.get("launches", [])),
                       "union": len(union_rows), "capped": len(capped),
                       "last_tick_2": lt2, "last_tick_3": lt3}

# ---- 4) compute_audit.json: rolling-ledger union + state :3 ----
f = "results/compute_audit.json"
a2 = json.loads(blob(f":2:{f}"))
a3 = json.loads(blob(f":3:{f}"))
h2, h3 = a2.get("history", []), a3.get("history", [])
rows = {json.dumps(r, sort_keys=True, ensure_ascii=False): r for r in h2}
for r in h3:
    rows.setdefault(json.dumps(r, sort_keys=True, ensure_ascii=False), r)
union = list(rows.values())
union.sort(key=lambda r: r.get("ts", ""))       # ts-ascending producer order
merged = dict(a3)
merged["history"] = union
write(f, json.dumps(merged, ensure_ascii=False, indent=2).encode("utf-8"))
json.loads(io.open(f, encoding="utf-8").read())
ANCHORS["compute_audit_union"] = {"|A|": len(h2), "|B|": len(h3),
                                 "|AuB|": len(union)}
assert len(union) >= max(len(h2), len(h3)), "history union lost rows"

# ---- 5) regime_state.json: rolling-ledger union + state :3 ----
f = "results/regime_state.json"
a2 = json.loads(blob(f":2:{f}"))
a3 = json.loads(blob(f":3:{f}"))
for key in ("history", "transitions"):
    h2, h3 = a2.get(key, []), a3.get(key, [])
    rows = {json.dumps(r, sort_keys=True, ensure_ascii=False): r for r in h2}
    for r in h3:
        rows.setdefault(json.dumps(r, sort_keys=True, ensure_ascii=False), r)
    a3[key] = list(rows.values())
    ANCHORS[f"regime_{key}"] = {"|A|": len(h2), "|B|": len(h3),
                                "|AuB|": len(a3[key])}
    assert len(a3[key]) >= max(len(h2), len(h3)), f"regime {key} union lost"
write(f, json.dumps(a3, ensure_ascii=False, indent=1).encode("utf-8"))
json.loads(io.open(f, encoding="utf-8").read())

# ---- 6) x2_watch_log.jsonl: line-level union zero loss ----
f = "results/x2_watch_log.jsonl"
l2 = blob(f":2:{f}").decode("utf-8").splitlines()
l3 = blob(f":3:{f}").decode("utf-8").splitlines()
seen, union = set(), []
for ln in l2 + l3:
    if ln not in seen:
        seen.add(ln)
        union.append(ln)
write(f, ("\n".join(union) + "\n").encode("utf-8"))
ANCHORS["x2_union"] = {"|A|": len(l2), "|B|": len(l3), "|AuB|": len(union)}
assert len(union) >= max(len(l2), len(l3)), "x2 union lost lines"

# ---- 7) conflict-marker fail-closed scan on all resolved files ----
ALL = TAKE3 + ["CODELY.md", "results/autofill_state.json",
               "results/compute_audit.json", "results/regime_state.json",
               "results/x2_watch_log.jsonl"]
for f in ALL:
    body = io.open(f, "rb").read()
    assert b"<<<<<<<" not in body and b">>>>>>>" not in body, \
        f"markers left in {f}"

print(json.dumps({"resolved": len(ALL), "anchors": ANCHORS,
                  "verdict": "OK: probe-derived take-:3 (newest) for all "
                             "ts-probed snapshots, CODELY true union both "
                             "machines, ledgers zero-loss, wrapper intact, "
                             "parse-verified"},
                 ensure_ascii=False, indent=1))
