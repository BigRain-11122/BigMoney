# -*- coding: utf-8 -*-
"""r810 bm-a rebase-conflict resolver (bigmoney-conflict-resolve skill canon).
Stage law r351: rebase :2: = origin side, :3: = local (my commit) side.
Faces:
  - ALL_FACES A/B family (4): compute_audit DONE via merge_lane_views; here:
    update_status (origin blob POLLUTED with conflict markers -- take local clean),
    lhb_update_status, futures_update_status (take-new deep-ts probe)
  - twin-regen-md: REPORT json+md (same side), LIVE json+md x2 pairs (same side)
  - js-wrapper-snapshot: dashboard_status.js (host=bm-a single-writer per r378
    -> take LOCAL whole bytes), dashboard_status.json (take-new ts)
  - snapshots: fundamental_b_layer_filter (updated ts), scorecard_v1 +
    strategy_scorecard (deep-ts probe r100/R350 hardened: key normalized
    prefix match, value must be ^20\\d{2}- shaped WITH time-of-day, no
    key-exclude lists), _attrition_guard_scan (UNKNOWN->manual: scan-evidence
    snapshot, take-new by scan ts deep probe)."""
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


print("[1] snapshot / status faces")
take_new_json("results/update_status.json")
take_new_json("results/lhb_update_status.json")
take_new_json("results/futures_update_status.json")
take_new_json("results/fundamental_b_layer_filter.json")
take_new_json("results/scorecard_v1.json")
take_new_json("results/strategy_scorecard.json")
take_new_json("results/dashboard_status.json")
take_new_json("results/_attrition_guard_scan.json")

print("[2] js-wrapper-snapshot: dashboard_status.js (host=bm-a single-writer r378 -> local side)")
take_bytes("results/dashboard_status.js", 3)
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

print("RESOLVER DONE: all faces written + parse-verified; next: git add -> rebase --continue")
