# -*- coding: utf-8 -*-
"""R290 bm-a rebase resolver batch-3 (e4f4742f replay onto bm-b 40b75d06):
S6-mirror conflict family. Recipes per SKILL.md:
  CODELY.md            -> memory-union (line-level union, dedupe)
  compute_audit.json   -> rolling-ledger: union history + take-new snapshot
  regime_state.json    -> rolling-ledger: union transitions/history + take-new state
  dashboard_status.js  -> js-wrapper-snapshot: take-side whole bytes (newer)
  *_status/token_usage/fundamental -> snapshot take-new by ts
  daily_report/scorecards (UNKNOWN->manual: deterministic derive-snapshots
                          regenerated each S6 run) -> take-new by embedded ts
Stage :2: = upstream (bm-b r291 face, ~03:13), :3: = mine (~03:19-03:21)."""
import json
import subprocess

def stage(n, path):
    return subprocess.run(["git", "show", f":{n}:{path}"],
                          capture_output=True).stdout.decode("utf-8",
                                                              errors="replace")

def w(path, text):
    with open(path, "w", encoding="utf-8", newline="") as fh:
        fh.write(text)

def ts_of(d, keys):
    for k in keys:
        v = d.get(k) if isinstance(d, dict) else None
        if v:
            return v
    return ""

SNAP_TS_KEYS = ["ts", "generated", "generated_at", "updated_at", "asof",
                "last_run", "written_at"]

# 1) CODELY.md memory-union
a = [l for l in stage(2, "CODELY.md").splitlines()]
b = [l for l in stage(3, "CODELY.md").splitlines()]
seen, union = set(), []
for l in a + b:
    if l not in seen:
        seen.add(l)
        union.append(l)
w("CODELY.md", "\n".join(union) + "\n")
print(f"CODELY.md union: {len(a)}+{len(b)} -> {len(union)} lines")

# 2) compute_audit.json rolling-ledger: union history rows + take-new fields
ca2, ca3 = json.loads(stage(2, "results/compute_audit.json")), \
           json.loads(stage(3, "results/compute_audit.json"))
h2 = ca2.get("history", [])
h3 = ca3.get("history", [])
hkeys = set()
hu = []
for r in h2 + h3:
    k = json.dumps(r, ensure_ascii=False, sort_keys=True)
    if k not in hkeys:
        hkeys.add(k)
        hu.append(r)
new = ca3 if ts_of(ca3, SNAP_TS_KEYS) >= ts_of(ca2, SNAP_TS_KEYS) else ca2
new["history"] = hu
out = json.dumps(new, ensure_ascii=False, indent=1) + "\n"
json.loads(out)
w("results/compute_audit.json", out)
print(f"compute_audit: history {len(h2)}+{len(h3)} -> {len(hu)}; snapshot ts={ts_of(new, SNAP_TS_KEYS)}")

# 3) regime_state.json rolling-ledger
r2, r3 = json.loads(stage(2, "results/regime_state.json")), \
          json.loads(stage(3, "results/regime_state.json"))
new = r3 if ts_of(r3, SNAP_TS_KEYS) >= ts_of(r2, SNAP_TS_KEYS) else r2
for lk in ("transitions", "history"):
    if lk in r2 or lk in r3:
        l2, l3 = r2.get(lk, []), r3.get(lk, [])
        lk_keys = set()
        lu = []
        for r in l2 + l3:
            k = json.dumps(r, ensure_ascii=False, sort_keys=True)
            if k not in lk_keys:
                lk_keys.add(k)
                lu.append(r)
        new[lk] = lu
        print(f"regime_state {lk}: {len(l2)}+{len(l3)} -> {len(lu)}")
out = json.dumps(new, ensure_ascii=False, indent=1) + "\n"
json.loads(out)
w("results/regime_state.json", out)

# 4) js-wrapper-snapshot: take-side whole bytes (mine newer)
js3 = stage(3, "results/dashboard_status.js")
assert js3.lstrip().startswith("window."), "wrapper must be preserved"
w("results/dashboard_status.js", js3)
print("dashboard_status.js: take mine (wrapper intact)")

# 5) snapshots + derived-snapshots: take-new by embedded ts
SNAPS = [
    ("results/dashboard_status.json", False),
    ("results/fundamental_b_layer_filter.json", False),
    ("results/futures_update_status.json", False),
    ("results/heat_update_status.json", False),
    ("results/lhb_update_status.json", False),
    ("results/token_usage.json", False),
    ("results/update_status.json", False),
    ("docs/daily_report/REPORT-2026-09-27.json", False),
    ("results/daily_scorecard.json", False),
    ("results/scorecard_v1.json", False),
    ("results/strategy_scorecard.json", False),
]
for path, _ in SNAPS:
    t2, t3 = stage(2, path), stage(3, path)
    try:
        d2, d3 = json.loads(t2), json.loads(t3)
        pick, side = (t3, "mine") if ts_of(d3, SNAP_TS_KEYS) >= ts_of(d2, SNAP_TS_KEYS) \
            else (t2, "upstream")
    except (ValueError, TypeError):
        pick, side = t3, "mine(raw)"
    w(path, pick)
    print(f"{path}: take-new -> {side}")
print("batch-3 resolve complete")
