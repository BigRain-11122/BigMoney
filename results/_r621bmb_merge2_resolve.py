"""r621 bm-b merge-2 resolver (vs true tip 61a5b34afc): direction flipped -> take-new(ours=15:1x, theirs=15:16-19) = THEIRS.
Recipes mirror round 1: 15 snapshots take-theirs byte-verbatim; lhb key-wise; compute_audit/regime_state history union + state take-theirs.
"""
import json, subprocess, sys, io

sys.stdout = io.open("results/_r621bmb_merge2_resolve.out", "w", encoding="utf-8")

def blob(stage, path):
    r = subprocess.run(["git", "show", ":%d:%s" % (stage, path)], capture_output=True)
    assert r.returncode == 0, (stage, path, r.stderr[:200])
    return r.stdout

receipt = {"round": 621, "machine": "bm-b", "merge2_head": "61a5b34afc", "files": {}}

SNAP = [
 "docs/daily_report/REPORT-2026-10-03.json",
 "docs/daily_report/REPORT-2026-10-03.md",
 "docs/live_usage/LIVE-2026-10-03.json",
 "docs/live_usage/LIVE-2026-10-03.md",
 "docs/live_usage/LIVE-latest.json",
 "docs/live_usage/LIVE-latest.md",
 "results/_attrition_guard_scan.json",
 "results/dashboard_status.js",
 "results/dashboard_status.json",
 "results/fundamental_b_layer_filter.json",
 "results/futures_update_status.json",
 "results/scorecard_v1.json",
 "results/strategy_scorecard.json",
 "results/token_usage.json",
 "results/update_status.json",
]
for p in SNAP:
    t = blob(3, p)
    if p.endswith(".json"):
        json.loads(t.decode("utf-8"))
    elif p.endswith(".js"):
        s = t.decode("utf-8")
        assert s.startswith("window.DASH_DATA = ") and s.rstrip().endswith(";"), "js wrapper broken"
        json.loads(s[s.index("=") + 1:s.rstrip().rindex(";")])
    open(p, "wb").write(t)
    receipt["files"][p] = {"recipe": "snapshot take-new(theirs)", "bytes": len(t)}
print("snapshots take-theirs: %d files, parse verified" % len(SNAP))

p = "results/lhb_update_status.json"
o, t = json.loads(blob(2, p).decode("utf-8")), json.loads(blob(3, p).decode("utf-8"))
added = {}
for k, v in o.items():
    if k not in t:
        t[k] = v; added[k] = True
open(p, "wb").write((json.dumps(t, ensure_ascii=False, indent=1) + "\n").encode("utf-8"))
receipt["files"][p] = {"recipe": "snapshot key-wise merge (theirs ts-newer + ours-only keys)", "ours_only_keys_kept": sorted(added)}
print("lhb_update_status: key-wise, kept ours-only keys=%s" % sorted(added))

def union_rows(a, b, label):
    assert isinstance(a, list) and isinstance(b, list), label
    seen = set(json.dumps(r, sort_keys=True, ensure_ascii=False) for r in a)
    extra = [r for r in b if json.dumps(r, sort_keys=True, ensure_ascii=False) not in seen]
    return a + extra

p = "results/compute_audit.json"
o, t = json.loads(blob(2, p).decode("utf-8")), json.loads(blob(3, p).decode("utf-8"))
assert set(o) == set(t) == {"history", "latest"}, "compute_audit shape drift"
merged = union_rows(o["history"], t["history"], "compute_audit.history")
ids = set(json.dumps(r, sort_keys=True, ensure_ascii=False) for r in merged)
assert len(merged) == len(ids), "union rows not unique"
t_ids = set(json.dumps(r, sort_keys=True, ensure_ascii=False) for r in t["history"])
o_ids = set(json.dumps(r, sort_keys=True, ensure_ascii=False) for r in o["history"])
assert t_ids <= ids and o_ids <= ids, "zero-loss violated"
o["history"] = merged
o["latest"] = t["latest"]
open(p, "wb").write((json.dumps(o, ensure_ascii=False, indent=1) + "\n").encode("utf-8"))
receipt["files"][p] = {"recipe": "rolling-ledger union history + latest take-new(theirs)", "history_ours": len(o_ids), "history_theirs": len(t_ids), "history_union": len(merged)}
print("compute_audit: history union |ours|=%d |theirs|=%d -> %d, latest=theirs" % (len(o_ids), len(t_ids), len(merged)))

p = "results/regime_state.json"
o, t = json.loads(blob(2, p).decode("utf-8")), json.loads(blob(3, p).decode("utf-8"))
for arr in ("history", "transitions"):
    if arr in o and arr in t:
        t[arr] = union_rows(t[arr], o[arr], "regime." + arr)
open(p, "wb").write((json.dumps(t, ensure_ascii=False, indent=1) + "\n").encode("utf-8"))
receipt["files"][p] = {"recipe": "rolling-ledger union history/transitions + state take-new(theirs)", "history": len(t["history"]), "transitions": len(t["transitions"]), "updated": t.get("updated")}
print("regime_state: union history=%d transitions=%d, state=theirs(updated=%s)" % (len(t["history"]), len(t["transitions"]), t.get("updated")))

json.dump(receipt, open("results/_r621bmb_merge2_resolve_receipt.json", "w", encoding="utf-8"), ensure_ascii=False, indent=1)
print("MERGE-2 ALL RESOLVED OK")
