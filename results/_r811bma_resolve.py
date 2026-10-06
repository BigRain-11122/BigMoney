# -*- coding: utf-8 -*-
"""r811 bm-a rebase-conflict resolver (bigmoney-conflict-resolve skill canon).
Stage law r351: rebase :2: = origin side, :3: = local (my commit) side.
ALL_FACES 4 (update_status/lhb_update_status/futures_update_status/token_usage):
  merge_lane_views resolve fail-closed (marker-polluted side blobs, JSONDecodeError)
  -> r810-precedent fallback: take_new_json with marker checks.
Manual adjudication (this round, fail-closed UNKNOWN handled by hand first):
  _attrition_guard_scan UNKNOWN->snapshot: scan-evidence face (ts/rc/files),
  origin 05:42:10 vs local 05:52:59 -> take-new by deep ts.
  scorecard_v1/strategy_scorecard: origin 05:20 vs local 05:51 regens -> take-new.
Improvement over r810 asset: dashboard .js bound to SAME side as .json (pair
coherence; r810 took js local unconditionally).
"""
import subprocess, json, re, io, sys

sys.stdout.reconfigure(encoding="utf-8", errors="replace")
MARKERS = ("<<<<<<<", ">>>>>>>", "=======")


def stage(path, n):
    r = subprocess.run(["git", "show", f":{n}:{path}"], capture_output=True)
    assert r.returncode == 0, (path, n, r.stderr[:200])
    return r.stdout


def probe_ts(obj, best=""):
    """Deep-scan for wall-clock ts values (r311 nested + r100 value shape)."""
    if isinstance(obj, dict):
        for k, v in obj.items():
            if isinstance(v, str) and re.match(r"^20\d{2}-\d{2}-\d{2}[T ]\d{2}:\d{2}", v):
                if v > best:
                    best = v
            else:
                best = probe_ts(v, best)
    elif isinstance(obj, list):
        for v in obj:
            best = probe_ts(v, best)
    return best


def take_bytes(path, side):
    b = stage(path, side)
    for m in MARKERS:
        assert m.encode() not in b, f"{path}: side {side} carries conflict marker {m}"
    io.open(path, "wb").write(b)
    print(f"  {path}: took {'origin(:2:)' if side == 2 else 'local(:3:)'} whole bytes ({len(b)}B)")


def take_new_json(path):
    b2, b3 = stage(path, 2), stage(path, 3)
    p2 = not any(m.encode() in b2 for m in MARKERS)
    p3 = not any(m.encode() in b3 for m in MARKERS)
    j2 = json.loads(b2) if p2 else None
    j3 = json.loads(b3) if p3 else None
    t2 = probe_ts(j2) if j2 is not None else ""
    t3 = probe_ts(j3) if j3 is not None else ""
    print(f"  {path}: origin ts={t2!r} (clean={p2}) local ts={t3!r} (clean={p3})")
    if not p2 and p3:
        side = 3
    elif not p3 and p2:
        side = 2
    else:
        assert t2 and t3, f"{path}: ts probe empty both sides"
        side = 3 if t3 >= t2 else 2
    take_bytes(path, side)
    json.load(io.open(path, encoding="utf-8"))  # parse-verify law r185
    return side


print("[1] snapshot / status faces (ALL_FACES 4 via marker-checked take-new fallback)")
take_new_json("results/update_status.json")
take_new_json("results/lhb_update_status.json")
take_new_json("results/futures_update_status.json")
take_new_json("results/token_usage.json")
take_new_json("results/fundamental_b_layer_filter.json")
take_new_json("results/scorecard_v1.json")
take_new_json("results/strategy_scorecard.json")
take_new_json("results/_attrition_guard_scan.json")

print("[2] js-wrapper-snapshot: dashboard pair SAME-side coupling (json ts decides, js follows)")
dash_side = take_new_json("results/dashboard_status.json")
take_bytes("results/dashboard_status.js", dash_side)
js = io.open("results/dashboard_status.js", encoding="utf-8").read()
assert js.startswith("window.DASH_DATA =") and js.rstrip().endswith(";"), "js wrapper format broken (R209)"

print("[3] twin-regen-md: REPORT pair (same side both)")
rep_side = take_new_json("docs/daily_report/REPORT-2026-10-07.json")
take_bytes("docs/daily_report/REPORT-2026-10-07.md", rep_side)

print("[4] twin-regen-md: LIVE quartet (same side all 4)")
live_side = take_new_json("docs/live_usage/LIVE-2026-10-07.json")
take_bytes("docs/live_usage/LIVE-2026-10-07.md", live_side)
take_bytes("docs/live_usage/LIVE-latest.json", live_side)
take_bytes("docs/live_usage/LIVE-latest.md", live_side)

print("RESOLVER DONE: all 16 faces written + parse-verified; next: git add -> rebase --continue")
