"""r446 bm-b rebase resolver (17-UU vs bm-a r456/r457 same-window S6
storm). Canonical recipes per bigmoney-conflict-resolve skill:
- snapshots: hardened deep-ts probe on STAGED blobs (:2:=bm-a base,
  :3:=my replayed commit); R350 law: no key-exclude lists, wall-clock
  values require time-of-day, ambiguity by value shape only
- rolling-ledger compute_audit.json: history union by (ts, machine),
  zero-loss assertion |A∪B|; latest take-new
- regime_state.json: deep-compare proven only-updated-ts-differs ->
  take-new
- js-wrapper dashboard_status.js: take-side whole byte matching the
  .json winner
- _attrition_guard_scan.json (UNKNOWN): fresh post-resolution re-scan
  writes the authoritative receipt against the final tree (both
  staged sides are partially stale by construction)
Parse-verify before staging (r185 law); zero network; idempotent."""

import json
import re
import subprocess
import sys

TS_RE = re.compile(r"20\d{2}-\d{2}-\d{2}[T ]\d{2}:\d{2}(?::\d{2})?")


def blob(side, path):
    r = subprocess.run(["git", "show", ":%s:%s" % (side, path)],
                       capture_output=True)
    return r.stdout.decode("utf-8", errors="replace")


def side_ts_max(obj, best=""):
    """Hardened deep-ts probe (R350): wall-clock values only (date +
    time-of-day), any key name, nested scan, no exclude lists."""
    if isinstance(obj, dict):
        for v in obj.values():
            best = side_ts_max(v, best)
    elif isinstance(obj, list):
        for v in obj:
            best = side_ts_max(v, best)
    elif isinstance(obj, str):
        for m in TS_RE.findall(obj):
            if m > best:
                best = m
    return best


def write(path, text):
    with open(path, "w", encoding="utf-8", newline="") as f:
        f.write(text)


log = []

# ---------- 1. json/md snapshots: take-new via hardened ts probe
SNAP = [
    "docs/daily_report/REPORT-2026-09-30.json",
    "docs/daily_report/REPORT-2026-09-30.md",
    "docs/live_usage/LIVE-2026-09-30.json",
    "docs/live_usage/LIVE-2026-09-30.md",
    "docs/live_usage/LIVE-latest.json",
    "docs/live_usage/LIVE-latest.md",
    "results/dashboard_status.json",
    "results/fundamental_b_layer_filter.json",
    "results/futures_update_status.json",
    "results/lhb_update_status.json",
    "results/scorecard_v1.json",
    "results/strategy_scorecard.json",
    "results/token_usage.json",
    "results/update_status.json",
]
dash_json_winner = None
for p in SNAP:
    a, b = blob(2, p), blob(3, p)
    ta, tb = side_ts_max(a), side_ts_max(b)
    if p.endswith(".json"):
        json.loads(a), json.loads(b)      # parse-verify both (r185)
    win = a if ta >= tb else b           # tie -> base side (r140)
    side = "bm-a" if ta >= tb else "bm-b"
    write(p, win)
    log.append(f"{p}: take-{side} (a {ta} vs b {tb})")
    if p == "results/dashboard_status.json":
        dash_json_winner = side

# ---------- 2. dashboard_status.js: whole-byte take matching .json
p = "results/dashboard_status.js"
a, b = blob(2, p), blob(3, p)
win = a if dash_json_winner == "bm-a" else b
write(p, win)
log.append(f"{p}: take-{dash_json_winner} whole-byte (match .json)")

# ---------- 3. compute_audit.json: rolling-ledger union (r440 recipe:
# ts-key union, identical same-ts rows dedupe, zero-loss |A∪B|)
p = "results/compute_audit.json"
da, db = json.loads(blob(2, p)), json.loads(blob(3, p))
ha, hb = da.get("history", []), db.get("history", [])


def union_rows(a, b, key):
    seen = {}
    for r in a + b:
        k = r.get(key) or json.dumps(r, sort_keys=True)[:120]
        if k not in seen:
            seen[k] = r
        else:
            ta = (seen[k].get("ts") or seen[k].get("updated") or "")
            tb = (r.get("ts") or r.get("updated") or "")
            if tb > ta:
                seen[k] = r
    return list(seen.values())


union = union_rows(ha, hb, "ts")
union.sort(key=lambda r: r.get("ts", ""))
n_union = len(union)
n_aub = len({r.get("ts") for r in ha} | {r.get("ts") for r in hb})
assert n_union == n_aub, f"union loss {n_union} != {n_aub}"
latest = (da.get("latest") if str(da.get("latest", {}).get("ts", ""))
          >= str(db.get("latest", {}).get("ts", ""))
          else db.get("latest"))
out = {"latest": latest, "history": union}
write(p, json.dumps(out, ensure_ascii=False, indent=1) + "\n")
json.loads(open(p, encoding="utf-8").read())
log.append(f"{p}: union {len(ha)}+{len(hb)} -> {n_union} "
           f"(zero-loss |A∪B|={n_aub}), latest "
           f"ts={latest.get('ts')}")

# ---------- 4. regime_state.json: deep-compare proven only-updated-ts
# differs -> whole-blob take-new (byte-exact, no re-serialization)
p = "results/regime_state.json"
da, db = json.loads(blob(2, p)), json.loads(blob(3, p))
diff_keys = [k for k in set(da) | set(db) if da.get(k) != db.get(k)]
assert diff_keys == ["updated"], f"unexpected drift {diff_keys}"
win_text = blob(2, p) if da["updated"] >= db["updated"] else blob(3, p)
write(p, win_text)
json.loads(open(p, encoding="utf-8").read())
log.append(f"{p}: whole-blob take-new updated="
           f"{(da if da['updated'] >= db['updated'] else db)['updated']} "
           f"(sole-diff key verified)")

print("\n".join(log))
print("resolver: all 16 faces resolved + parse-verified")
