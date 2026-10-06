"""r765 bm-a merge-conflict resolver (canonical recipes, skill bigmoney-conflict-resolve).

31 UU faces vs bm-c round 606 wave. Recipes:
- take-new snapshot (deep-ts normalized probe, r756 law): fundamental_b_layer_filter /
  scorecard_v1 / strategy_scorecard / _attrition_guard_scan / *_update_status (update/
  futures/heat-lhb lane) / token_usage / paper marks (6) / paper_export (2) / prospect
  summaries (2) / t35_open_fill_verify
- twin-regen-md: REPORT-2026-10-06.{json,md} + LIVE-2026-10-06.{json,md} + LIVE-latest.{json,md}
  (json face probes side, md faces byte-copy SAME side)
- ours-live-wins (bm-a single-writer guard faces, host resumed live): dashboard_status.{json,js}
  + daily_scorecard.json
- rolling-union: compute_audit (history rows identity-union + ts sort, latest take-new),
  regime_state (history rows if present else take-new), x2_watch_log.jsonl (line union +
  ts stable sort, r758 law)
Probe laws: r100/R350, mixed-separator normalization (r756 in-session heal), staged blobs
never the working tree.
"""
import json
import re
import subprocess
import sys
from datetime import datetime

TS_RE = re.compile(r"^20\d{2}-\d{2}-\d{2}[T ]\d{2}:\d{2}")


def norm_ts(s):
    s = s.replace(" ", "T")
    for fmt in ("%Y-%m-%dT%H:%M:%S%z", "%Y-%m-%dT%H:%M:%S"):
        try:
            return datetime.strptime(s, fmt).strftime("%Y%m%d%H%M%S")
        except ValueError:
            continue
    return None


def staged_bytes(path, stage):
    r = subprocess.run(["git", "show", f":{stage}:{path}"], capture_output=True)
    if r.returncode != 0:
        return None
    return r.stdout


def deep_ts(obj):
    best = None

    def walk(x):
        nonlocal best
        if isinstance(x, dict):
            for v in x.values():
                walk(v)
        elif isinstance(x, list):
            for v in x:
                walk(v)
        elif isinstance(x, str):
            if TS_RE.match(x):
                n = norm_ts(x)
                if n and (best is None or n > best):
                    best = n

    walk(obj)
    return best


def take_new_snapshot(path):
    a = staged_bytes(path, 2)
    b = staged_bytes(path, 3)
    if a is None and b is None:
        print(f"{path}: NO STAGED SIDES, skip")
        return False
    if a is None:
        open(path, "wb").write(b)
        print(f"{path}: origin missing -> local taken")
        return True
    if b is None:
        open(path, "wb").write(a)
        print(f"{path}: local missing -> origin taken")
        return True
    ta = deep_ts(json.loads(a.decode("utf-8")))
    tb = deep_ts(json.loads(b.decode("utf-8")))
    if ta is None and tb is None:
        print(f"{path}: NO ts either side -> FAIL-CLOSED, manual")
        return False
    if tb is None or (ta is not None and ta >= tb):
        win, side, ts = a, "origin", ta
    else:
        win, side, ts = b, "local", tb
    open(path, "wb").write(win)
    json.loads(open(path, "rb").read().decode("utf-8"))
    print(f"{path}: take-new -> {side} (ts={ts})")
    return True


def twin_resolve(json_path, md_paths):
    a = staged_bytes(json_path, 2)
    b = staged_bytes(json_path, 3)
    ta = deep_ts(json.loads(a.decode("utf-8"))) if a else None
    tb = deep_ts(json.loads(b.decode("utf-8"))) if b else None
    if tb is None or (ta is not None and ta >= tb):
        stage, side, ts = 2, "origin", ta
    else:
        stage, side, ts = 3, "local", tb
    jb = staged_bytes(json_path, stage)
    open(json_path, "wb").write(jb)
    json.loads(open(json_path, "rb").read().decode("utf-8"))
    print(f"{json_path}: twin side -> {side} (ts={ts})")
    for md in md_paths:
        mb = staged_bytes(md, stage)
        if mb is None:
            print(f"{md}: staged side missing, SKIP (manual)")
            return False
        open(md, "wb").write(mb)
        print(f"{md}: byte-copied from {side} side")
    return True


def ours_live(path):
    b = staged_bytes(path, 3)
    if b is None:
        print(f"{path}: local side missing, SKIP")
        return False
    open(path, "wb").write(b)
    if path.endswith(".json"):
        json.loads(open(path, "rb").read().decode("utf-8"))
    print(f"{path}: ours-live-wins (bm-a guard face)")
    return True


def union_jsonl_ts(path):
    a = (staged_bytes(path, 2) or b"").decode("utf-8").strip().splitlines()
    b = (staged_bytes(path, 3) or b"").decode("utf-8").strip().splitlines()
    seen = {}
    for ln in a + b:
        if ln.strip():
            seen[ln] = True
    rows = []
    for ln in seen:
        try:
            d = json.loads(ln)
            ts = norm_ts(str(d.get("ts", "")))
        except Exception:
            ts = None
        rows.append((ts or "", ln))
    rows.sort(key=lambda x: x[0])
    out = "\n".join(r[1] for r in rows) + "\n"
    open(path, "w", encoding="utf-8", newline="\n").write(out)
    print(f"{path}: union {len(a)}+{len(b)} -> {len(rows)} lines zero-loss (ts-stable)")
    return True


def _row_key(d):
    for k in ("ts", "time", "at", "datetime", "epoch"):
        if isinstance(d, dict) and k in d:
            return norm_ts(str(d[k])) or str(d[k])
    return ""


def union_history_face(path):
    a = staged_bytes(path, 2)
    b = staged_bytes(path, 3)
    da = json.loads(a.decode("utf-8"))
    db = json.loads(b.decode("utf-8"))
    if "history" in da and "history" in db:
        ha, hb = da["history"], db["history"]
        ids = {}
        for row in ha + hb:
            ids[json.dumps(row, sort_keys=True, ensure_ascii=False)] = row
        merged = sorted(ids.values(), key=lambda r: _row_key(r) if isinstance(r, dict) else "")
        ta = deep_ts(da)
        tb = deep_ts(db)
        base = db if (ta is None or (tb is not None and tb >= ta)) else da
        merged_doc = dict(base)
        merged_doc["history"] = merged
        open(path, "wb").write(json.dumps(merged_doc, indent=1, ensure_ascii=False).encode("utf-8"))
        json.loads(open(path, "rb").read().decode("utf-8"))
        print(f"{path}: history union {len(ha)}+{len(hb)} -> {len(merged)} rows zero-loss + top-level take-new side")
        return True
    return take_new_snapshot(path)


ok = True
TAKE_NEW = [
    "results/fundamental_b_layer_filter.json",
    "results/scorecard_v1.json",
    "results/strategy_scorecard.json",
    "results/_attrition_guard_scan.json",
    "results/update_status.json",
    "results/futures_update_status.json",
    "results/lhb_update_status.json",
    "results/token_usage.json",
    "results/t35_open_fill_verify.json",
    "results/paper/COMPOSITE-CE-01_paper.json",
    "results/paper/COMPOSITE-CE-02_paper.json",
    "results/paper/DROUGHT-CE-01_paper.json",
    "results/paper/ENGULF-CE-01_paper.json",
    "results/paper/NEEDLE-DE-01_paper.json",
    "results/paper/VOLATILITY-CE-01_paper.json",
    "results/paper_export/export-2026-09-30.json",
    "results/paper_export/latest.json",
    "results/prospect_paper/_summary.json",
    "results/prospect_promotion/_summary.json",
]
for f in TAKE_NEW:
    ok = take_new_snapshot(f) and ok

ok = twin_resolve(
    "docs/daily_report/REPORT-2026-10-06.json",
    ["docs/daily_report/REPORT-2026-10-06.md"],
) and ok
ok = twin_resolve(
    "docs/live_usage/LIVE-2026-10-06.json",
    ["docs/live_usage/LIVE-2026-10-06.md",
     "docs/live_usage/LIVE-latest.json",
     "docs/live_usage/LIVE-latest.md"],
) and ok

for f in [
    "results/dashboard_status.json",
    "results/dashboard_status.js",
    "results/daily_scorecard.json",
]:
    ok = ours_live(f) and ok

ok = union_history_face("results/compute_audit.json") and ok
ok = union_history_face("results/regime_state.json") and ok
ok = union_jsonl_ts("results/x2_watch_log.jsonl") and ok

sys.exit(0 if ok else 2)
