"""r621 bm-b merge resolver: 19 UU per bigmoney-conflict-resolve canon.
Recipes: snapshots=take-new(ours, newer S6 15:1x vs theirs 14:5x);
CODELY.md=3-hunk theirs (origin r420 archive wave; dropped lines verified in pit-* domain files);
compute_audit/regime_state=history union + state take-new; lhb=key-wise merge.
All output -> results/_r621bmb_merge_resolve.out (UTF-8). Receipt -> results/_r621bmb_merge_resolve_receipt.json
"""
import json, subprocess, sys, io

sys.stdout = io.open("results/_r621bmb_merge_resolve.out", "w", encoding="utf-8")

def blob(stage, path):
    r = subprocess.run(["git", "show", ":%d:%s" % (stage, path)], capture_output=True)
    assert r.returncode == 0, (stage, path, r.stderr[:200])
    return r.stdout

receipt = {"round": 621, "machine": "bm-b", "merge_head": "ab35cd73a", "files": {}}

# ---------- 1) CODELY.md: hunk-resolve -> theirs, with zero-loss verification ----------
raw = open("CODELY.md", "rb").read()
lines = raw.split(b"\n")
out, mode, hunks = [], None, []
ours_dropped = []
for ln in lines:
    s = ln.rstrip(b"\r")
    if s.startswith(b"<<<<<<< "):
        assert mode is None, "nested ours marker"
        mode = "ours"; hunks.append({"ours": [], "theirs": []}); continue
    if s == b"=======":
        assert mode == "ours", "stray ======= "
        mode = "theirs"; continue
    if s.startswith(b">>>>>>> "):
        assert mode == "theirs", "stray >>>>>>>"
        mode = None; continue
    if mode == "ours":
        hunks[-1]["ours"].append(ln); ours_dropped.append(s)
    elif mode == "theirs":
        hunks[-1]["theirs"].append(ln)
    else:
        out.append(ln)
assert mode is None, "unterminated conflict block"
assert len(hunks) == 3, "expected 3 hunks, got %d" % len(hunks)
for h in hunks:
    out.extend(h["theirs"])
# NOTE: theirs sections are appended after common prefix? No — rebuild properly:
# redo sequentially to preserve order (common lines interleaved with hunk theirs)
out, mode = [], None
for ln in lines:
    s = ln.rstrip(b"\r")
    if s.startswith(b"<<<<<<< "):
        mode = "ours"; continue
    if s == b"=======":
        mode = "theirs"; continue
    if s.startswith(b">>>>>>> "):
        mode = None; continue
    if mode == "theirs" or mode is None:
        out.append(ln)
new = b"\n".join(out)
assert b"<<<<<<<" not in new and b">>>>>>>" not in new and new.count(b"\n=======") == 0, "markers remain"
txt = new.decode("utf-8")
# our unique auto-merged entries must survive (r620 bm-b own entry is ours-only)
assert "r620 bm-b" in txt, "bm-b r620 entry lost"
assert "r618 bm-b" in txt and "r619 bm-b" in txt, "bm-b entries lost"
# dropped ours-side hunk lines: blocks 1/2 = evolved-prefix versions (theirs superset), block 3 = archived hot entries
pit = {}
for f in ("pit-git", "pit-pool", "pit-spawn", "pit-data", "pit-protocol", "pit-engine"):
    pit[f] = open("research/%s.md" % f, "rb").read().decode("utf-8", "replace")
pit_all = "\n".join(pit.values())
verified_in_pit = 0
for s in ours_dropped:
    t = s.decode("utf-8", "replace")
    if t.startswith(b"- ".decode()) and ("r624 bm-a" in t or "r625 bm-a" in t):
        # archived hot entry: verify key phrase migrated verbatim into a domain pit file
        key = t[:24]
        assert key in pit_all, "dropped hot entry NOT found in pit files: %s" % key
        verified_in_pit += 1
assert verified_in_pit == 3, "expected 3 archived hot entries verified in pit files, got %d" % verified_in_pit
open("CODELY.md", "wb").write(new)
receipt["files"]["CODELY.md"] = {"recipe": "memory-union/hunk-theirs (r420 archive wave)", "hunks": 3, "ours_lines_dropped": len(ours_dropped), "hot_entries_verified_in_pit_files": verified_in_pit, "bytes": len(new)}
print("CODELY.md resolved: 3 hunks -> theirs; %d dropped ours lines; %d hot entries verified in pit-* files; %d bytes" % (len(ours_dropped), verified_in_pit, len(new)))

# ---------- 2) snapshots: take-new = ours, byte-verbatim ----------
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
    o = blob(2, p)
    if p.endswith(".json"):
        json.loads(o.decode("utf-8"))
    elif p.endswith(".js"):
        t = o.decode("utf-8")
        assert t.startswith("window.DASH_DATA = ") and t.rstrip().endswith(";"), "js wrapper broken"
        json.loads(t[t.index("=") + 1:t.rstrip().rindex(";")])
    open(p, "wb").write(o)
    receipt["files"][p] = {"recipe": "snapshot take-new(ours)", "bytes": len(o)}
print("snapshots take-ours: %d files, json/wrapper parse verified" % len(SNAP))

# ---------- 3) lhb_update_status.json: key-wise merge (ours base + theirs-only keys) ----------
p = "results/lhb_update_status.json"
o, t = json.loads(blob(2, p).decode("utf-8")), json.loads(blob(3, p).decode("utf-8"))
added = {}
for k, v in t.items():
    if k not in o:
        o[k] = v; added[k] = True
open(p, "wb").write((json.dumps(o, ensure_ascii=False, indent=1) + "\n").encode("utf-8"))
receipt["files"][p] = {"recipe": "snapshot key-wise merge (ours ts-newer + theirs-only keys)", "theirs_only_keys_added": sorted(added)}
print("lhb_update_status: key-wise, added theirs-only keys=%s" % sorted(added))

# ---------- 4) rolling-ledger unions ----------
def union_rows(a, b, label):
    if not isinstance(a, list) or not isinstance(b, list):
        raise AssertionError(label + " not list")
    if not a:
        return list(b)
    keycand = None
    for k in ("ts", "time", "generated_at", "generated", "datetime", "date", "asof"):
        if isinstance(a[0], dict) and k in a[0]:
            keycand = k; break
    if keycand:
        def kf(r):
            return json.dumps(r.get(keycand), sort_keys=True)
        seen = {kf(r): i for i, r in enumerate(a)}
        extra = [r for r in b if kf(r) not in seen]
        merged = a + extra
    else:
        seen = set(json.dumps(r, sort_keys=True, ensure_ascii=False) for r in a)
        extra = [r for r in b if json.dumps(r, sort_keys=True, ensure_ascii=False) not in seen]
        merged = a + extra
    return merged

p = "results/compute_audit.json"
o, t = json.loads(blob(2, p).decode("utf-8")), json.loads(blob(3, p).decode("utf-8"))
assert set(o) == set(t) == {"history", "latest"}, "compute_audit shape drift"
merged_hist = union_rows(o["history"], t["history"], "compute_audit.history")
n_ours, n_theirs = len(o["history"]), len(t["history"])
ids = set(json.dumps(r, sort_keys=True, ensure_ascii=False) for r in merged_hist)
assert len(merged_hist) == len(ids), "union rows not unique"
# zero-loss: every theirs row identity present
t_ids = set(json.dumps(r, sort_keys=True, ensure_ascii=False) for r in t["history"])
assert t_ids <= ids, "theirs history rows lost"
o["history"] = merged_hist
open(p, "wb").write((json.dumps(o, ensure_ascii=False, indent=1) + "\n").encode("utf-8"))
receipt["files"][p] = {"recipe": "rolling-ledger union history + latest take-new(ours)", "history_ours": n_ours, "history_theirs": n_theirs, "history_union": len(merged_hist)}
print("compute_audit: history union %d|%d -> %d (dedup by row identity), latest=ours" % (n_ours, n_theirs, len(merged_hist)))

p = "results/regime_state.json"
o, t = json.loads(blob(2, p).decode("utf-8")), json.loads(blob(3, p).decode("utf-8"))
for arr in ("history", "transitions"):
    if arr in o and arr in t:
        o[arr] = union_rows(o[arr], t[arr], "regime." + arr)
open(p, "wb").write((json.dumps(o, ensure_ascii=False, indent=1) + "\n").encode("utf-8"))
receipt["files"][p] = {"recipe": "rolling-ledger union history/transitions + state take-new(ours)", "history": len(o["history"]), "transitions": len(o["transitions"]), "updated": o.get("updated")}
print("regime_state: union history=%d transitions=%d, state fields=ours(updated=%s)" % (len(o["history"]), len(o["transitions"]), o.get("updated")))

json.dump(receipt, open("results/_r621bmb_merge_resolve_receipt.json", "w", encoding="utf-8"), ensure_ascii=False, indent=1)
print("ALL RESOLVED OK -> receipt written")
