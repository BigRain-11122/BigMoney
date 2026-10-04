# -*- coding: utf-8 -*-
# r668 bm-b merge resolver (17 UU push-race closeout; r667 lineage recipe full set)
# Recipes: CODELY.md append-only exact-line dedup union (r453 law, keep-first);
#          rolling-ledger (compute_audit/regime_state): (ts,canon) union zero-loss + take-new scalars;
#          token_usage per-key machines union by entry ts (r456 side-pick>0 law);
#          snapshots take-side by embedded ts (ts_norm r461 law, tie->ours r140);
#          dashboard js twin follows json side (exact blob bytes).
# Laws: r657(2) HEAD:/MERGE_HEAD: direct blob take; r185 reparse before add;
#       r664 marker check content-based line-start; r656 canon-set containment.
import json, subprocess, io, os, sys

os.chdir(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

def blob(ref, path):
    p = subprocess.run(["git", "show", ref + ":" + path], capture_output=True)
    assert p.returncode == 0, ("blob fail", ref, path)
    return p.stdout

def ts_norm(v):
    return str(v).replace("T", " ")[:19]

def canon(row):
    return json.dumps(row, sort_keys=True, ensure_ascii=False)

def take_side(path, side):
    ref = "HEAD" if side == "ours" else "MERGE_HEAD"
    data = blob(ref, path)
    with io.open(path, "wb") as f:
        f.write(data)
    return data

def snap_side(path):
    o = json.loads(blob("HEAD", path).decode("utf-8", "replace"))
    t = json.loads(blob("MERGE_HEAD", path).decode("utf-8", "replace"))
    ko = next((k for k in ("updated", "generated", "generated_at", "ts", "now") if k in o), None)
    no, nt = ts_norm(o.get(ko, "")), ts_norm(t.get(ko, ""))
    return ("ours" if no >= nt else "theirs"), ko, no, nt

report = {"probe": "r668bmb_merge_resolve", "faces": {}, "verify": {}}

# --- sanity: UU set exactly the expected 17 (full porcelain count, no tail-window) ---
p = subprocess.run(["git", "status", "--porcelain"], capture_output=True)
uu = sorted(l[3:].strip() for l in p.stdout.decode("utf-8", "replace").splitlines()
           if l[:2] in ("UU", "AA"))
expect = sorted([
    "CODELY.md",
    "docs/daily_report/REPORT-2026-10-04.json", "docs/daily_report/REPORT-2026-10-04.md",
    "docs/live_usage/LIVE-2026-10-04.json", "docs/live_usage/LIVE-2026-10-04.md",
    "docs/live_usage/LIVE-latest.json", "docs/live_usage/LIVE-latest.md",
    "results/_attrition_guard_scan.json", "results/compute_audit.json",
    "results/dashboard_status.js", "results/dashboard_status.json",
    "results/fundamental_b_layer_filter.json", "results/futures_update_status.json",
    "results/lhb_update_status.json", "results/regime_state.json",
    "results/token_usage.json", "results/update_status.json"])
assert uu == expect, "UU set drifted: %s" % (uu,)

# --- CODELY.md: append-only exact-line dedup union (keep-first) ---
ho = blob("HEAD", "CODELY.md")
th = blob("MERGE_HEAD", "CODELY.md")
ho_ls = ho.split(b"\n")
th_ls = th.split(b"\n")
seen = set(ho_ls)
new_from_theirs = [l for l in th_ls if l not in seen]
# guard: theirs-new block must be small tail entries (append-only assumption)
assert len(new_from_theirs) < 60, ("theirs-new suspiciously large", len(new_from_theirs))
union = ho_ls + new_from_theirs
while union and union[-1] == b"":
    union.pop()
data = b"\n".join(union) + b"\n"
with io.open("CODELY.md", "wb") as f:
    f.write(data)
assert data.count(b"[2026-10-04 12:0x r668 bm-b]") == 1, "r668 entry marker count != 1"
report["faces"]["CODELY.md"] = "exact-line dedup union: HEAD %d + theirs-new %d lines" % (
    len(ho_ls), len(new_from_theirs))

# --- snapshot json faces: derive side from live blobs, take, record ---
SNAP_JSON = [
    "results/_attrition_guard_scan.json", "results/fundamental_b_layer_filter.json",
    "results/futures_update_status.json", "results/lhb_update_status.json",
    "results/update_status.json",
    "docs/daily_report/REPORT-2026-10-04.json",
    "docs/live_usage/LIVE-2026-10-04.json", "docs/live_usage/LIVE-latest.json",
    "results/dashboard_status.json",
]
dash_side = None
for path in SNAP_JSON:
    side, ko, no, nt = snap_side(path)
    take_side(path, side)
    report["faces"][path] = "take-%s (%s: ours %s vs theirs %s)" % (side, ko, no, nt)
    if path == "results/dashboard_status.json":
        dash_side = side

# --- md/js twins follow their json side (exact blob bytes) ---
for jp, tp in [("docs/daily_report/REPORT-2026-10-04.json", "docs/daily_report/REPORT-2026-10-04.md"),
               ("docs/live_usage/LIVE-2026-10-04.json", "docs/live_usage/LIVE-2026-10-04.md"),
               ("docs/live_usage/LIVE-latest.json", "docs/live_usage/LIVE-latest.md"),
               ("results/dashboard_status.json", "results/dashboard_status.js")]:
    js = json.loads(io.open(jp, encoding="utf-8").read())
    # side already decided at take time; re-derive to stay consistent
    side, ko, no, nt = snap_side(jp)
    assert (io.open(jp, "rb").read() == blob("HEAD" if side == "ours" else "MERGE_HEAD", jp)), (
        "json side drift", jp)
    take_side(tp, side)
    report["faces"][tp] = "twin take-%s (follows json)" % side

# --- compute_audit: history (ts,canon) union zero-loss + latest take-new ---
o = json.loads(blob("HEAD", "results/compute_audit.json").decode("utf-8", "replace"))
t = json.loads(blob("MERGE_HEAD", "results/compute_audit.json").decode("utf-8", "replace"))
seen, union = set(), []
for row in sorted(o["history"] + t["history"], key=lambda x: str(x.get("ts", ""))):
    k = (str(row.get("ts", "")), canon(row))
    if k in seen:
        continue
    seen.add(k)
    union.append(row)
o_set = {(str(r.get("ts", "")), canon(r)) for r in o["history"]}
t_set = {(str(r.get("ts", "")), canon(r)) for r in t["history"]}
u_set = {(str(r.get("ts", "")), canon(r)) for r in union}
assert len(o_set - u_set) == 0 and len(t_set - u_set) == 0, "audit zero-loss violated"
base = o if ts_norm(o["latest"].get("ts", "")) >= ts_norm(t["latest"].get("ts", "")) else t
with io.open("results/compute_audit.json", "w", encoding="utf-8", newline="\n") as f:
    json.dump({"history": union[-400:], "latest": base["latest"]}, f,
              ensure_ascii=False, indent=1)
report["faces"]["results/compute_audit.json"] = (
    "union history %d+%d->%d lost=0, latest from %s"
    % (len(o["history"]), len(t["history"]), len(union),
       "ours" if base is o else "theirs"))

# --- regime_state: history union + scalars take-new by updated ---
o = json.loads(blob("HEAD", "results/regime_state.json").decode("utf-8", "replace"))
t = json.loads(blob("MERGE_HEAD", "results/regime_state.json").decode("utf-8", "replace"))
seen, union = set(), []
for row in sorted((o.get("history") or []) + (t.get("history") or []),
                  key=lambda x: str(x.get("ts", x.get("updated", "")))):
    k = canon(row)
    if k in seen:
        continue
    seen.add(k)
    union.append(row)
o_set = {canon(r) for r in (o.get("history") or [])}
t_set = {canon(r) for r in (t.get("history") or [])}
assert len(o_set - seen) == 0 and len(t_set - seen) == 0, "regime history zero-loss"
sc = o if ts_norm(o.get("updated", "")) >= ts_norm(t.get("updated", "")) else t
sc["history"] = union
with io.open("results/regime_state.json", "w", encoding="utf-8", newline="\n") as f:
    json.dump(sc, f, ensure_ascii=False, indent=1)
report["faces"]["results/regime_state.json"] = (
    "history union %d lost=0, scalars from %s (updated %s)"
    % (len(union), "ours" if sc is o else "theirs", sc.get("updated")))

# --- token_usage: per-key machines union by entry ts (r456 law) + scalars take-new ---
o = json.loads(blob("HEAD", "results/token_usage.json").decode("utf-8", "replace"))
t = json.loads(blob("MERGE_HEAD", "results/token_usage.json").decode("utf-8", "replace"))
side_pick = {"ours": 0, "theirs": 0}
machines = {}
def entry_ts(e):
    return ts_norm(e.get("updated", e.get("ts", e.get("generated", ""))))
for k in sorted(set(o["machines"].keys()) | set(t["machines"].keys())):
    oe, te = o["machines"].get(k), t["machines"].get(k)
    if oe is None:
        machines[k], side_pick["theirs"] = te, side_pick["theirs"] + 1
        continue
    if te is None:
        machines[k], side_pick["ours"] = oe, side_pick["ours"] + 1
        continue
    if entry_ts(oe) >= entry_ts(te):
        machines[k] = oe
        side_pick["ours"] += 1
    else:
        machines[k] = te
        side_pick["theirs"] += 1
assert side_pick["ours"] > 0, "r456 side-pick zero on ours leg -- whole-face fallback needed"
sc = o if ts_norm(o.get("generated", "")) >= ts_norm(t.get("generated", "")) else t
sc["machines"] = machines
with io.open("results/token_usage.json", "w", encoding="utf-8", newline="\n") as f:
    json.dump(sc, f, ensure_ascii=False, indent=1)
report["faces"]["results/token_usage.json"] = (
    "per-key union side_pick=%s keyset=%d, scalars from %s (gen %s)"
    % (side_pick, len(machines), "ours" if sc is o else "theirs", sc.get("generated")))

# --- reparse gate (r185) on all resolved json faces ---
for path in [f for f in expect if f.endswith(".json")]:
    json.loads(io.open(path, encoding="utf-8").read())
report["verify"]["reparse"] = "PASS %d json faces" % len([f for f in expect if f.endswith(".json")])

# --- marker residue check (content-based, line-start only, r664/r657/r453) ---
bad = []
for f in expect:
    for i, line in enumerate(io.open(f, "rb").read().split(b"\n")):
        if line.startswith(b"<<<<<<<") or line.startswith(b">>>>>>>") or line.startswith(b"======="):
            bad.append((f, i + 1))
assert not bad, ("marker residue", bad[:3])
report["verify"]["markers"] = "none"

# --- auto-merged append-only faces: zero-loss containment (canon line-set, r656) ---
for f in ("results/fund_value_p1/nulls.jsonl", "results/fund_quality_p1/nulls.jsonl",
          "results/fund_divlowvol_p1/nulls.jsonl"):
    wt = set(l for l in io.open(f, "rb").read().split(b"\n") if l.strip())
    ho = set(l for l in blob("HEAD", f).split(b"\n") if l.strip())
    th = set(l for l in blob("MERGE_HEAD", f).split(b"\n") if l.strip())
    assert len(ho - wt) == 0, ("HEAD line loss", f, len(ho - wt))
    assert len(th - wt) == 0, ("MERGE_HEAD line loss", f, len(th - wt))
    report["verify"][f] = "wt=%d HEAD-lost=0 MERGE_HEAD-lost=0" % len(wt)

# --- state/heartbeat/rr survived auto-merge intact (round 668 face) ---
st = json.loads(io.open("state.json", encoding="utf-8").read())
assert st["round_no"] == 668 and isinstance(st["round_no"], int)
hb = json.loads(io.open("fleet/machines/bm-b.json", encoding="utf-8").read())
assert isinstance(hb["heartbeat_epoch_utc"], int) and hb["round_no"] == 668
rr = io.open("logs/iteration-loop/round_reports.md", "rb").read()
cnt = rr.decode("utf-8", "replace").count("round 668 | bm-b")
assert cnt == 1, ("round report r668 entry count", cnt)
report["verify"]["state-heartbeat-rr"] = "PASS (round 668, epoch int, rr count 1)"

# --- pool flip survived auto-merge intact ---
pool = json.loads(io.open("results/runnable_pool.json", encoding="utf-8").read())
e = [x for x in pool["entries"] if x["id"] == "THEME-JUDGE-P1"][0]
assert e["status"] == "done" and e["shards"][0]["status"] == "done", "pool flip lost in merge"
report["verify"]["pool-flip"] = "THEME-JUDGE-P1 entry+shard done survived"

with io.open("results/_r668bmb_merge_resolve.json", "w", encoding="utf-8") as f:
    json.dump(report, f, ensure_ascii=False, indent=1)
print("RESOLVE_DONE faces=%d verify=%s" % (len(report["faces"]), sorted(report["verify"].keys())))
print("snapshots:", {k: v for k, v in report["faces"].items() if "take-" in v})
