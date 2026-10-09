# r910 bm-a rebase conflict resolver (r907 bloodline _r907bma_resolve.py rolled)
# 33 UU batch: 7 ALL_FACES already resolved via merge_lane_views.py (sanctioned).
# This script resolves the remaining 26: 3 twin pairs (json+md same-side),
# 18 snapshots (deep-ts probe take-new, r100/R350 hardened), 2 append-logs (line union).
# Stage law r351: :2: = origin/base side (HEAD during rebase), :3: = replay/mine side.
# Tie law r140: same-second tie -> HEAD side (:2:).
import json, subprocess, re, sys

ROOT = r"C:\Users\sjs20\Desktop\FluxGroup\quant\bigmoney"
GIT = r"C:\Program Files\Git\cmd\git.exe"

def staged_blob(stage, path):
    r = subprocess.run([GIT, "show", f":{stage}:{path}"], capture_output=True, cwd=ROOT)
    if r.returncode != 0:
        return None
    return r.stdout

# r100/R350 hardened probe: collect ALL wall-clock-shaped values (date-only values
# must NOT feed the max); no key-exclude lists; value-shape gate only.
WALLCLOCK_RE = re.compile(r"^20\d{2}-\d{2}-\d{2}[T ]\d{2}:\d{2}")

def collect_wallclock(obj, out):
    if isinstance(obj, dict):
        for v in obj.values():
            collect_wallclock(v, out)
    elif isinstance(obj, list):
        for v in obj:
            collect_wallclock(v, out)
    elif isinstance(obj, str):
        if WALLCLOCK_RE.match(obj):
            out.append(obj)

def probe_max(path, blob):
    if blob is None:
        return None
    try:
        obj = json.loads(blob)
    except Exception:
        return None
    vals = []
    collect_wallclock(obj, vals)
    if not vals:
        return None
    return max(vals)

log = []

def decide_side(json_path, extra_json_paths=None):
    """Probe :2: and :3: staged blobs of json face(s); newer wins; tie -> :2: (HEAD law r140)."""
    paths = [json_path] + (extra_json_paths or [])
    best = {2: None, 3: None}
    for p in paths:
        b2, b3 = staged_blob(2, p), staged_blob(3, p)
        t2, t3 = probe_max(p, b2), probe_max(p, b3)
        if t2 and (not best[2] or t2 > best[2]):
            best[2] = t2
        if t3 and (not best[3] or t3 > best[3]):
            best[3] = t3
    if best[3] and (not best[2] or best[3] > best[2]):
        side = 3
    elif best[2]:
        side = 2
    else:
        side = 2  # both sides probe-miss -> HEAD side
    log.append(f"  {json_path}: :2: max-ts={best[2]} :3: max-ts={best[3]} -> side {side} ({'replay/mine' if side==3 else 'origin/HEAD'})")
    return side

def write_blob(path, blob, verify_json):
    if verify_json:
        json.loads(blob)  # parse-verify before write (r185 law)
    full = ROOT + "\\" + path.replace("/", "\\")
    with open(full, "wb") as f:
        f.write(blob)

def resolve_twin_group(group_name, json_md_pairs):
    """json_md_pairs: list of (json_path, md_path). One side decision for the whole group."""
    json_paths = [p[0] for p in json_md_pairs]
    side = decide_side(json_paths[0], extra_json_paths=json_paths[1:])
    for jp, mp in json_md_pairs:
        jb = staged_blob(side, jp)
        mb = staged_blob(side, mp)
        assert jb is not None, f"missing staged blob {side}:{jp}"
        assert mb is not None, f"missing staged blob {side}:{mp}"
        write_blob(jp, jb, verify_json=True)
        write_blob(mp, mb, verify_json=False)
    log.append(f"[twin-group {group_name}] side {side} applied to {len(json_md_pairs)} pairs")

def resolve_snapshot(path, side=None, verify_json=True):
    if side is None:
        side = decide_side(path)
    b = staged_blob(side, path)
    assert b is not None, f"missing staged blob {side}:{path}"
    write_blob(path, b, verify_json=verify_json)
    log.append(f"[snapshot] {path} -> side {side}")

def resolve_union_jsonl(path):
    b2, b3 = staged_blob(2, path), staged_blob(3, path)
    assert b2 is not None and b3 is not None, f"missing staged blobs for {path}"
    lines2 = [l for l in b2.split(b"\n") if l.strip()]
    lines3 = [l for l in b3.split(b"\n") if l.strip()]
    seen = set()
    merged = []
    for l in lines2 + lines3:
        if l not in seen:
            seen.add(l)
            merged.append(l)
    assert len(merged) == len(set(lines2) | set(lines3)), f"union count mismatch {path}"
    out = b"\n".join(merged) + b"\n"
    full = ROOT + "\\" + path.replace("/", "\\")
    with open(full, "wb") as f:
        f.write(out)
    log.append(f"[append-union] {path}: |A|={len(lines2)} |B|={len(lines3)} -> |A u B|={len(merged)} zero-loss asserted")

# --- 3 twin groups (json drives decision; md byte-copied same side; r98/r99/r100 twin law) ---
resolve_twin_group("daily_report-2026-10-09",
    [("docs/daily_report/REPORT-2026-10-09.json", "docs/daily_report/REPORT-2026-10-09.md")])
resolve_twin_group("live_usage-2026-10-09+latest",
    [("docs/live_usage/LIVE-2026-10-09.json", "docs/live_usage/LIVE-2026-10-09.md"),
     ("docs/live_usage/LIVE-latest.json", "docs/live_usage/LIVE-latest.md")])

# --- 18 snapshots ---
snapshots = [
    "results/_attrition_guard_scan.json",
    "results/daily_scorecard.json",
    "results/fundamental_b_layer_filter.json",
    "results/paper/COMPOSITE-CE-01_paper.json",
    "results/paper/COMPOSITE-CE-02_paper.json",
    "results/paper/DROUGHT-CE-01_paper.json",
    "results/paper/ENGULF-CE-01_paper.json",
    "results/paper/NEEDLE-DE-01_paper.json",
    "results/paper/VOLATILITY-CE-01_paper.json",
    "results/paper_export/export-2026-10-08.json",
    "results/paper_export/latest.json",
    "results/prospect_paper/_summary.json",
    "results/prospect_promotion/_summary.json",
    "results/scorecard_v1.json",
    "results/strategy_scorecard.json",
    "results/t35_open_fill_verify.json",
]
for p in snapshots:
    resolve_snapshot(p)
# dashboard_status.json decides; .js byte-copied SAME side (R209 wrapper law: take-side whole bytes)
dash_side = decide_side("results/dashboard_status.json")
resolve_snapshot("results/dashboard_status.json", side=dash_side)
resolve_snapshot("results/dashboard_status.js", side=dash_side, verify_json=False)

# --- 2 append-logs (line-level union zero-loss r188/r217) ---
resolve_union_jsonl("results/pool_core_samples.jsonl")
resolve_union_jsonl("results/x2_watch_log.jsonl")

print("RESOLVER LOG (r910 bm-a, 26 faces):")
print("\n".join(log))
print("ALL 26 RESOLVED; parse-verified where json; zero-loss asserted for unions")
