# -*- coding: utf-8 -*-
"""r819 bm-a rebase conflict resolver: 17 twin/snapshot faces (post ALL_FACES
canonical resolve). Deep-ts probe per r311/D-20260927-09 + hardened r100
(normalize keys strip _/-, value shape ^20\\d{2}- + time-of-day per R350,
probe STAGED blobs :2:/:3: never working tree). Twins (.md/.js) byte-copy
from the SAME winning side (r329 md-not-JSON law; R209 js-wrapper law)."""
import json, re, subprocess, sys, io

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")

def stage_bytes(path, stage):
    r = subprocess.run(["git", "show", f":{stage}:{path}"], capture_output=True)
    if r.returncode != 0:
        raise RuntimeError(f"stage {stage} missing for {path}: {r.stderr[:120]}")
    return r.stdout

def probe_ts(obj, out, path="$"):
    """collect wall-clock candidates: str ^20.. with time-of-day, or unix epoch int (R350 shape law)."""
    if isinstance(obj, dict):
        for k, v in obj.items():
            nk = k.lower().replace("_", "").replace("-", "")
            if isinstance(v, str):
                if re.match(r"^20\d{2}-\d{2}-\d{2}[T ]\d{2}:\d{2}", v):
                    if any(s in nk for s in ("ts", "asof", "generated", "updated", "time", "date", "seen", "clock")):
                        out.append((path + "." + k, v))
            elif isinstance(v, (int, float)) and not isinstance(v, bool):
                if 1700000000 < v < 2000000000 and any(s in nk for s in ("epoch", "ts")):
                    out.append((path + "." + k, v))
            else:
                probe_ts(v, out, path + "." + k)
    elif isinstance(obj, list):
        for i, v in enumerate(obj[:50]):
            probe_ts(v, out, f"{path}[{i}]")

def side_max_ts(blob):
    try:
        obj = json.loads(blob.decode("utf-8"))
    except Exception:
        return None, "not-json"
    cands = []
    probe_ts(obj, cands)
    if not cands:
        return None, "no-ts-candidates"
    strs = [(p, v) for p, v in cands if isinstance(v, str)]
    if strs:
        best = max(strs, key=lambda x: x[1])
        return best[1], f"str@{best[0]}"
    return None, "only-int-cands"

def take_snapshot_pair(paths):
    """paths = [json_path, optional byte-copy twin paths...]; probe json side, take same side for all."""
    jp = paths[0]
    b2, b3 = stage_bytes(jp, 2), stage_bytes(jp, 3)
    if b2 == b3:
        for p in paths:
            open(p, "wb").write(b3)
        return f"{jp}: sides byte-identical -> local verbatim"
    t2, w2 = side_max_ts(b2)
    t3, w3 = side_max_ts(b3)
    if t3 is None and t2 is None:
        # deterministic face, no ts candidates: prefer local (host=bm-a guard + freshest chain run)
        for p in paths:
            open(p, "wb").write(b3)
        return f"{jp}: no-ts deterministic face -> LOCAL ({w3}; bytes {len(b2)} vs {len(b3)})"
    if t2 is None:
        side, blob = "local", b3
    elif t3 is None:
        side, blob = "origin", b2
    else:
        side, blob = ("local", b3) if t3 >= t2 else ("origin", b2)
    for p in paths:
        open(p, "wb").write(stage_bytes(p, 2) if side == "origin" else stage_bytes(p, 3))
    return f"{jp}: origin_ts={t2} ({w2}) local_ts={t3} ({w3}) -> {side.upper()} whole-side"

GROUPS = [
    [r"docs/daily_report/REPORT-2026-10-07.json", r"docs/daily_report/REPORT-2026-10-07.md"],
    [r"docs/live_usage/LIVE-2026-10-07.json", r"docs/live_usage/LIVE-2026-10-07.md"],
    [r"docs/live_usage/LIVE-latest.json", r"docs/live_usage/LIVE-latest.md"],
    [r"results/dashboard_status.json", r"results/dashboard_status.js"],
    [r"results/daily_scorecard.json"],
    [r"results/fundamental_b_layer_filter.json"],
    [r"results/paper_export/export-2026-09-30.json"],
    [r"results/paper_export/latest.json"],
    [r"results/prospect_paper/_summary.json"],
    [r"results/prospect_promotion/_summary.json"],
    [r"results/scorecard_v1.json"],
    [r"results/strategy_scorecard.json"],
    [r"results/_attrition_guard_scan.json"],
]

for grp in GROUPS:
    print(take_snapshot_pair(grp))

# parse-verify everything written
fails = []
for grp in GROUPS:
    for p in grp:
        raw = open(p, "rb").read()
        if p.endswith(".json"):
            try:
                json.loads(raw.decode("utf-8"))
            except Exception as e:
                fails.append((p, f"json parse: {e}"))
        elif p.endswith(".js"):
            if not (raw.lstrip().startswith(b"window.DASH_DATA") or b"window.DASH_DATA" in raw[:200]):
                fails.append((p, "js wrapper missing"))
        elif p.endswith(".md"):
            if len(raw) < 100:
                fails.append((p, f"md suspiciously small {len(raw)}B"))
if fails:
    print("VERIFY FAILS:", fails)
    sys.exit(1)
print("ALL 17 faces resolved + parse-verified (13 groups)")
