# r819 bm-b rebase conflict resolver (19 UU, bm-a r944 wave 06:11-06:17 vs
# bm-b S6 06:19-06:20 same-window re-derive collisions).
# Skill: bigmoney-conflict-resolve. Classifier: 9 classified + 10 UNKNOWN
# manually adjudicated here as same-window idempotent re-derive twins
# (REPORT/LIVE same-day twins r818 precedent; attrition probe evidence
# take-new r818; scorecard faces re-derived per round R216 family).
# Recipes: rolling-ledger union zero-loss (r188/R208), snapshot take-new
# by content max-ts (R208/R216), js-wrapper whole-side bytes (R209).
import json
import re
import subprocess
import sys

ORIGIN = sys.argv[1] if len(sys.argv) > 2 else "f2f770b62"
MINE = sys.argv[2] if len(sys.argv) > 2 else "d42d6c1b2"
TS_RE = re.compile(r"20\d{2}-\d{2}-\d{2}[T ]\d{2}:\d{2}:\d{2}")


def blob(rev, path):
    r = subprocess.run(["git", "show", "%s:%s" % (rev, path)],
                       capture_output=True)
    if r.returncode != 0:
        raise RuntimeError("show %s:%s rc=%d" % (rev, path, r.returncode))
    return r.stdout


def max_ts(text):
    m = TS_RE.findall(text.decode("utf-8", "replace") if isinstance(text, bytes) else text)
    return max(m) if m else ""


def take_new(path, prefer_mine_on_tie=True):
    a, b = blob(ORIGIN, path), blob(MINE, path)
    ta, tb = max_ts(a), max_ts(b)
    pick = MINE if (tb >= ta if prefer_mine_on_tie else tb > ta) else ORIGIN
    data = blob(pick, path)
    # r185 parse-validation gate (shape-appropriate per extension)
    if path.endswith(".json"):
        json.loads(data.decode("utf-8"))
    elif path.endswith(".js"):
        assert data.startswith(b"window.DASH_DATA") and data.rstrip().endswith(b";"), \
            "js wrapper shape lost (R209)"
    open(path, "wb").write(data)
    return {"path": path, "recipe": "take_new", "origin_ts": ta,
            "mine_ts": tb, "picked": pick}


def take_new_md(path):
    a, b = blob(ORIGIN, path), blob(MINE, path)
    ta, tb = max_ts(a), max_ts(b)
    pick = MINE if tb >= ta else ORIGIN
    open(path, "wb").write(blob(pick, path))
    return {"path": path, "recipe": "take_new_md", "origin_ts": ta,
            "mine_ts": tb, "picked": pick}


def js_wrapper_take_side(path):
    # R209: never re-emit; whole-side raw bytes chosen by content max-ts
    return {**take_new(path), "recipe": "js_wrapper_whole_side"}


def union_ledger(path, ledger_key, idempotence="row"):
    a = json.loads(blob(ORIGIN, path).decode("utf-8"))
    b = json.loads(blob(MINE, path).decode("utf-8"))
    la, lb = a.get(ledger_key, []), b.get(ledger_key, [])
    seen, union = set(), []
    for row in la + lb:
        key = json.dumps(row, sort_keys=True, ensure_ascii=False)
        if key not in seen:
            seen.add(key)
            union.append(row)
    def _sk(r):
        return str(r.get("ts") or r.get("asof") or r.get("date") or "")
    union.sort(key=_sk)
    # zero-loss assertion (r188): union >= both sides
    assert len(union) >= max(len(la), len(lb)), "union lost rows"
    merged = dict(b)  # newest state fields = mine (replayed later run)
    merged[ledger_key] = union
    json.loads(json.dumps(merged))  # r185 parse gate
    with open(path, "w", encoding="utf-8") as f:
        json.dump(merged, f, ensure_ascii=False, indent=1)
    return {"path": path, "recipe": "union_%s" % ledger_key,
            "origin_rows": len(la), "mine_rows": len(lb),
            "union_rows": len(union), "state_side": MINE}


out = {"orphan_side_note": "onto=%s (bm-a r944), replayed=%s (bm-b r819)" % (ORIGIN, MINE),
       "resolved": []}

# rolling-ledger unions (classifier recipes r188/R208)
out["resolved"].append(union_ledger("results/compute_audit.json", "history"))
out["resolved"].append(union_ledger("results/regime_state.json", "history"))

# js-wrapper snapshot (R209)
out["resolved"].append(js_wrapper_take_side("results/dashboard_status.js"))

# snapshots / re-derive take-new (R208/R216)
for p in (
    "results/dashboard_status.json",
    "results/fundamental_b_layer_filter.json",
    "results/futures_update_status.json",
    "results/lhb_update_status.json",
    "results/token_usage.json",
    "results/update_status.json",
    "results/_attrition_guard_scan.json",
    "results/daily_scorecard.json",
    "results/scorecard_v1.json",
    "results/strategy_scorecard.json",
    "docs/daily_report/REPORT-2026-10-10.json",
    "docs/live_usage/LIVE-2026-10-10.json",
    "docs/live_usage/LIVE-latest.json",
):
    out["resolved"].append(take_new(p))

# markdown same-day idempotent twins (r818 precedent)
for p in (
    "docs/daily_report/REPORT-2026-10-10.md",
    "docs/live_usage/LIVE-2026-10-10.md",
    "docs/live_usage/LIVE-latest.md",
):
    out["resolved"].append(take_new_md(p))

# conflict-marker zero-residue assertion over every resolved path
for r in out["resolved"]:
    body = open(r["path"], "rb").read()
    assert b"<<<<<<<" not in body and b">>>>>>>" not in body, \
        "markers left in %s" % r["path"]

print(json.dumps(out, indent=1))
with open("results/_r819bmb_resolve_out.json", "w", encoding="utf-8") as f:
    json.dump(out, f, ensure_ascii=True, indent=1)
print("RESOLVE_OK %d files" % len(out["resolved"]))
