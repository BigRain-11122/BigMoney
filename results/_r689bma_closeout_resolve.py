"""r689 bm-a closeout UU resolver (wave-3 merge, 15 UU faces).

Per-face classification:
- 13 S6 regen faces: per-face ts newer-wins (r440; r688 recipe).
- results/token_usage.json: per-key union leg attempted (r456 law); entries
  carry no per-key ts (r466 face) -> side_pick==0 asserted -> explicit
  whole-face freshness fallback (r456-legal).
- CODELY.md: handled separately (block-union r675/r479) -- NOT in this list.
"""
import json
import re
import subprocess

REGEN_FACES = [
    "docs/daily_report/REPORT-2026-10-04.json",
    "docs/daily_report/REPORT-2026-10-04.md",
    "docs/live_usage/LIVE-2026-10-04.json",
    "docs/live_usage/LIVE-2026-10-04.md",
    "docs/live_usage/LIVE-latest.json",
    "docs/live_usage/LIVE-latest.md",
    "results/_attrition_guard_scan.json",
    "results/compute_audit.json",
    "results/fundamental_b_layer_filter.json",
    "results/futures_update_status.json",
    "results/lhb_update_status.json",
    "results/regime_state.json",
    "results/update_status.json",
]


def side_bytes(ref, path):
    r = subprocess.run(["git", "show", ref + ":" + path], capture_output=True)
    return r.stdout if r.returncode == 0 else None


def norm(t):
    t = str(t).strip().replace("T", " ")
    return t[:19] if len(t) >= 19 else t


def ts_of(blob):
    if blob is None:
        return ""
    try:
        d = json.loads(blob.decode("utf-8"))
        for k in ("ts", "generated", "generated_at", "asof", "cutoff",
                  "written_at", "updated"):
            if isinstance(d, dict) and k in d:
                return str(d[k])
    except Exception:
        pass
    m = re.search(rb"20\d\d-\d\d-\d\d[T ]\d\d:\d\d(:\d\d)?", blob)
    return m.group(0).decode() if m else ""


resolved = 0
for path in REGEN_FACES:
    ours = side_bytes("HEAD", path)
    theirs = side_bytes("MERGE_HEAD", path)
    if ours is None or theirs is None:
        print("SKIP (missing side):", path)
        continue
    n_o, n_t = norm(ts_of(ours)), norm(ts_of(theirs))
    winner, side = (ours, "ours") if n_o >= n_t else (theirs, "theirs")
    with open(path, "wb") as f:
        f.write(winner)
    b = open(path, "rb").read()
    assert b.count(b"<<<<<<<") == 0 and b.count(b">>>>>>>") == 0, "markers left"
    if path.endswith(".json"):
        json.loads(b.decode("utf-8"))
    print("RESOLVED %s -> %s (ours=%s theirs=%s)" % (path, side, n_o, n_t))
    resolved += 1

# --- token_usage.json: r456 per-key union leg with side_pick assertion ---
path = "results/token_usage.json"
ours_b = side_bytes("HEAD", path)
theirs_b = side_bytes("MERGE_HEAD", path)
do_, dt_ = json.loads(ours_b.decode("utf-8")), json.loads(theirs_b.decode("utf-8"))
mo, mt = do_.get("machines", {}), dt_.get("machines", {})
side_pick = 0
merged = dict(mo)
for k, v in mt.items():
    ov = merged.get(k)
    ov_ts = norm(ov.get("ts", "")) if isinstance(ov, dict) else ""
    tv_ts = norm(v.get("ts", "")) if isinstance(v, dict) else ""
    if ov is None:
        merged[k] = v
        side_pick += 1
    elif ov_ts and tv_ts and tv_ts > ov_ts:
        merged[k] = v
        side_pick += 1
    # else keep ours
if side_pick == 0:
    # r456/r466: entries carry no per-key ts -> explicit whole-face freshness
    g_o, g_t = norm(do_.get("generated", "")), norm(dt_.get("generated", ""))
    winner, side = (do_, "ours") if g_o >= g_t else (dt_, "theirs")
    print("token_usage: per-key side_pick=0 -> whole-face freshness "
          "(ours=%s theirs=%s) -> %s" % (g_o, g_t, side))
else:
    winner, side = do_, "ours-union"
    winner["machines"] = merged
    print("token_usage: per-key union side_pick=%d" % side_pick)
out = json.dumps(winner, ensure_ascii=False, indent=1)
with open(path, "w", encoding="utf-8", newline="\n") as f:
    f.write(out)
b = open(path, "rb").read()
assert b.count(b"<<<<<<<") == 0
json.loads(b.decode("utf-8"))
print("RESOLVED %s -> %s" % (path, side))
resolved += 1

print("resolved:", resolved, "of", len(REGEN_FACES) + 1)
