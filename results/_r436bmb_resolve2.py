"""r436 bm-b second rebase resolver (6 UU vs bm-c r231 GATE-TIMING-PRESCREEN-A158 window).

Freshness probe: theirs(my) chain 18:00:26-18:01:21 fresher than ours(origin bm-c) 17:51:47-17:53:22.
Recipes:
- gate_attrition.json: append-ledger union by (batch, ts), chronological sort (both sides have unique rows:
  ours=A158@18:01:57, theirs=W9_SCREEN@17:10:14+W9_JUDGE@17:47:46)
- compute_audit.json: rolling-ledger history union by ts; latest=take-new (theirs 18:00:26)
- regime_state.json: snapshot take-theirs after history-identity check (union if diverged)
- scorecard_v1/strategy_scorecard/update_status: snapshot take-theirs (fresher)
"""
import json
import subprocess

TAKE_THEIRS = [
    "results/scorecard_v1.json",
    "results/strategy_scorecard.json",
    "results/update_status.json",
]


def blob(stage, path):
    r = subprocess.run(["git", "show", f":{stage}:{path}"], capture_output=True)
    if r.returncode != 0:
        raise SystemExit(f"blob read fail {stage}:{path}: {r.stderr.decode()[:200]}")
    return json.loads(r.stdout)


# --- gate_attrition union (append-ledger) ---
p = "results/gate_attrition.json"
ours, theirs = blob(2, p), blob(3, p)
rows = {}
for r in theirs["history"] + ours["history"]:
    rows[(r["batch"], r["ts"])] = r
union = sorted(rows.values(), key=lambda r: r["ts"])
ts_u = set((r["batch"], r["ts"]) for r in union)
assert ts_u >= set((r["batch"], r["ts"]) for r in ours["history"])
assert ts_u >= set((r["batch"], r["ts"]) for r in theirs["history"])
out = dict(theirs)
out["history"] = union
json.dump(out, open(p, "w", encoding="utf-8"), ensure_ascii=False, indent=1)
print(f"gate_attrition union: |ours|={len(ours['history'])} |theirs|={len(theirs['history'])} -> {len(union)} "
      f"(+{[r['batch'] for r in union if (r['batch'], r['ts']) not in set((x['batch'], x['ts']) for x in theirs['history'])]})")

# --- compute_audit union (rolling-ledger) ---
p = "results/compute_audit.json"
ours, theirs = blob(2, p), blob(3, p)
rows = {}
for r in ours["history"] + theirs["history"]:
    rows[r["ts"]] = r
union = sorted(rows.values(), key=lambda r: r["ts"])
out = dict(theirs)  # latest take-new = theirs (18:00:26 > 17:51:47)
out["history"] = union
assert set(r["ts"] for r in union) >= set(r["ts"] for r in ours["history"])
assert set(r["ts"] for r in union) >= set(r["ts"] for r in theirs["history"])
json.dump(out, open(p, "w", encoding="utf-8"), ensure_ascii=False, indent=1)
print(f"compute_audit union: |ours|={len(ours['history'])} |theirs|={len(theirs['history'])} -> {len(union)} latest.ts={out['latest']['ts']}")

# --- regime_state: history check then take-theirs snapshot ---
p = "results/regime_state.json"
ours, theirs = blob(2, p), blob(3, p)
if ours["history"] != theirs["history"] or ours.get("transitions") != theirs.get("transitions"):
    merged = {}
    for r in theirs["history"] + ours["history"]:
        merged[(r.get("asof"), r.get("state"))] = r
    out = dict(theirs)
    out["history"] = sorted(merged.values(), key=lambda r: r.get("asof", ""))
    json.dump(out, open(p, "w", encoding="utf-8"), ensure_ascii=False, indent=1)
    print("regime_state: history DIVERGED -> union", len(out["history"]))
else:
    subprocess.run(["git", "checkout", "--theirs", p], check=True)
    print("regime_state: histories identical -> take-theirs (18:00:34 fresher)")

# --- snapshots take-theirs ---
for p in TAKE_THEIRS:
    subprocess.run(["git", "checkout", "--theirs", p], check=True)

# validate + add
for p in ["results/gate_attrition.json", "results/compute_audit.json", "results/regime_state.json"] + TAKE_THEIRS:
    json.load(open(p, encoding="utf-8"))
subprocess.run(["git", "add", "results/gate_attrition.json", "results/compute_audit.json",
                "results/regime_state.json"] + TAKE_THEIRS, check=True)
print("resolved+added 6 files; all JSON validated")
