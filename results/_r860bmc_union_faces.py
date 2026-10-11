# -*- coding: utf-8 -*-
# _r860bmc_union_faces.py - resolve 14 stash-pop UU faces per face law:
#   append-history ledger (compute_audit) = UNION dedupe-by-ts, latest=newer (r856/r859 law)
#   monotonic snapshots (token_usage/attrition/11 daily faces) = newer side wins (mine 08:06-08:10 > bm-b 07:39-07:58)
# Then git add all resolved.
import json, subprocess, io

ROOT = r"K:\Fluxgroup\FluxGroup\quant\bigmoney"

def stage(n, path):
    out = subprocess.run(["git", "show", ":%d:%s" % (n, path)], capture_output=True, cwd=ROOT)
    assert out.returncode == 0, (n, path, out.stderr[:200])
    return json.loads(out.stdout.decode("utf-8"))

def write(path, obj):
    with io.open(ROOT + "\\" + path, "w", encoding="utf-8", newline="") as f:
        json.dump(obj, f, ensure_ascii=False, indent=1)
        f.write("\n")

# 1) compute_audit.json: UNION
p = "results/compute_audit.json"
ours, theirs = stage(2, p), stage(3, p)
o_ts = {r["ts"]: r for r in ours["history"]}
t_ts = {r["ts"]: r for r in theirs["history"]}
common_identical = all(o_ts[k] == t_ts[k] for k in (set(o_ts) & set(t_ts)))
union = sorted({**o_ts, **t_ts}.values(), key=lambda r: r["ts"])
latest = theirs["latest"] if theirs["latest"]["ts"] >= ours["latest"]["ts"] else ours["latest"]
write(p, {"latest": latest, "history": union})
print("compute_audit UNION: rows=%d (ours %d + theirs %d, common %d identical=%s), latest ts=%s" % (
    len(union), len(o_ts), len(t_ts), len(set(o_ts) & set(t_ts)), common_identical, latest["ts"]))
assert len(union) == len(set(o_ts) | set(t_ts)), "union not superset-consistent"

# 2) monotonic snapshot faces: newer-side-wins (check ts field per face)
SNAP_FACES = [
    "results/token_usage.json",
    "results/_attrition_guard_scan.json",
    "docs/daily_report/REPORT-2026-10-11.json",
    "docs/live_usage/LIVE-2026-10-11.json",
    "docs/live_usage/LIVE-latest.json",
]
TS_KEYS = ("generated", "ts", "updated_at", "updated", "scan_ts", "last_scan", "asof", "generated_at")
def face_ts(d):
    for k in TS_KEYS:
        if isinstance(d, dict) and d.get(k):
            return str(d[k])
    return ""

for p in SNAP_FACES:
    ours, theirs = stage(2, p), stage(3, p)
    ot, tt = face_ts(ours), face_ts(theirs)
    win, side = (theirs, "stash-mine") if tt >= ot else (ours, "ours-bmb")
    write(p, win)
    print("%s -> %s (ours %s vs stash %s)" % (p, side, ot, tt))

# 3) whole-file text faces (md daily outputs + small json faces with md twins): newer-side-wins by content ts inside
TEXT_FACES = [
    "docs/daily_report/REPORT-2026-10-11.md",
    "docs/live_usage/LIVE-2026-10-11.md",
    "docs/live_usage/LIVE-latest.md",
    "results/fundamental_b_layer_filter.json",
    "results/futures_update_status.json",
    "results/lhb_update_status.json",
    "results/queue_head_collision_probe.json",
    "results/regime_state.json",
    "results/update_status.json",
]
import re
def stage_raw(n, path):
    out = subprocess.run(["git", "show", ":%d:%s" % (n, path)], capture_output=True, cwd=ROOT)
    assert out.returncode == 0, (n, path, out.stderr[:200])
    return out.stdout.decode("utf-8", errors="replace")

def raw_ts(b):
    m = re.search(r"20\d\d-\d\d-\d\d[ T]\d\d:\d\d:\d\d", b[:4000])
    return m.group(0) if m else ""

for p in TEXT_FACES:
    o_b, t_b = stage_raw(2, p), stage_raw(3, p)
    ot, tt = raw_ts(o_b), raw_ts(t_b)
    win_b, side = (t_b, "stash-mine") if tt >= ot else (o_b, "ours-bmb")
    with io.open(ROOT + "\\" + p, "w", encoding="utf-8", newline="") as f:
        f.write(win_b)
    print("%s -> %s (ours %s vs stash %s)" % (p, side, ot, tt))

# 4) git add all resolved
add = subprocess.run(["git", "add"] + ["results/compute_audit.json"] + SNAP_FACES + TEXT_FACES,
                     capture_output=True, cwd=ROOT)
assert add.returncode == 0, add.stderr[:300]
rem = subprocess.run(["git", "diff", "--name-only", "--diff-filter=U"], capture_output=True, cwd=ROOT)
print("remaining UU:", rem.stdout.decode().strip() or "NONE")
print("RESOLVE-DONE")
