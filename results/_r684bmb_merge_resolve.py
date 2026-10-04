# r684 bm-b: merge resolver for the 14-UU S6 regen wave (r681 lineage recipe,
# r440 per-face ts newer-wins; r456 token_usage per-key union + side_pick
# assertion; compute_audit history row-union by ts; _attrition scan take-new).
import io
import json
import subprocess

def show(rev, path):
    r = subprocess.run(["git", "show", "%s:%s" % (rev, path)],
                       capture_output=True)
    if r.returncode != 0:
        return None
    return json.loads(r.stdout.decode("utf-8", "replace"))

def w(path, doc):
    with io.open(path, "w", encoding="utf-8", newline="") as f:
        f.write(json.dumps(doc, ensure_ascii=False, indent=1) + "\n")
    json.loads(io.open(path, encoding="utf-8").read())   # reparse gate

# ---- 12 plain regen faces: take-ours (ours 17:55-17:58 > theirs 17:41)
OURS_FACES = [
    "docs/daily_report/REPORT-2026-10-04.json",
    "docs/daily_report/REPORT-2026-10-04.md",
    "docs/live_usage/LIVE-2026-10-04.json",
    "docs/live_usage/LIVE-2026-10-04.md",
    "docs/live_usage/LIVE-latest.json",
    "docs/live_usage/LIVE-latest.md",
    "results/_attrition_guard_scan.json",
    "results/fundamental_b_layer_filter.json",
    "results/futures_update_status.json",
    "results/lhb_update_status.json",
    "results/regime_state.json",
    "results/update_status.json",
]
for p in OURS_FACES:
    r = subprocess.run(["git", "checkout", "--ours", p], capture_output=True)
    assert r.returncode == 0, (p, r.stderr)
    # marker sanity (r657 law: no conflict markers survive)
    raw = io.open(p, "rb").read()
    assert b"<<<<<<<" not in raw and b">>>>>>>" not in raw, p
print("take-ours: %d faces clean" % len(OURS_FACES))

# ---- compute_audit.json: history row-union by ts (r681 201+201->203 face)
ours = show("HEAD", "results/compute_audit.json")
theirs = show("MERGE_HEAD", "results/compute_audit.json")
ho = {row["ts"]: row for row in ours["history"]}
ht = {row["ts"]: row for row in theirs["history"]}
union = dict(ho)
n_theirs_new = 0
for k, row in ht.items():
    if k not in union:
        union[k] = row
        n_theirs_new += 1
merged_hist = [union[k] for k in sorted(union)]
latest_ts = max(ours["latest"]["ts"], theirs["latest"]["ts"])
latest = ours["latest"] if ours["latest"]["ts"] >= theirs["latest"]["ts"] \
    else theirs["latest"]
doc = {"latest": latest, "history": merged_hist}
w("results/compute_audit.json", doc)
print("compute_audit: ours %d + theirs-new %d = %d rows; latest ts %s"
      % (len(ho), n_theirs_new, len(merged_hist), latest_ts))

# ---- token_usage.json: machines per-key union (r456) with side_pick count
tu_o = show("HEAD", "results/token_usage.json")
tu_t = show("MERGE_HEAD", "results/token_usage.json")
mo, mt = tu_o["machines"], tu_t["machines"]
assert set(mo) == set(mt), (set(mo) ^ set(mt))
side_pick = 0
mach = {}
for k in sorted(mo):
    if mo[k] == mt[k]:
        mach[k] = mo[k]
        continue
    side_pick += 1
    # per-key freshness: compare embedded ts fields (str keys may vary)
    ts_o = str(mo[k].get("ts") or mo[k].get("last_seen") or mo[k].get("updated") or "")
    ts_t = str(mt[k].get("ts") or mt[k].get("last_seen") or mt[k].get("updated") or "")
    if ts_o and ts_t and ts_o != ts_t:
        mach[k] = mo[k] if ts_o > ts_t else mt[k]
    else:
        # no comparable per-key ts face -> r466 explicit whole-face freshness
        mach[k] = mo[k] if str(tu_o.get("generated")) >= \
            str(tu_t.get("generated")) else mt[k]
assert side_pick > 0, "r456: per-key zero-hit needs explicit fresh-key route"
doc = dict(tu_o)
if str(tu_t.get("generated")) > str(tu_o.get("generated")):
    doc = dict(tu_t)
doc["machines"] = mach
w("results/token_usage.json", doc)
print("token_usage: per-key union side_pick=%d; generated=%s"
      % (side_pick, doc.get("generated")))

# ---- stage all 14
import subprocess as sp
for p in OURS_FACES + ["results/compute_audit.json",
                       "results/token_usage.json"]:
    r = sp.run(["git", "add", p], capture_output=True)
    assert r.returncode == 0, (p, r.stderr)
print("staged 14 resolved faces")
