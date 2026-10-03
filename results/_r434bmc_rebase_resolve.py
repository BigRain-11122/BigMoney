# -*- coding: utf-8 -*-
"""r434 bm-c rebase pick1 conflict resolver (r433 recipe: ts-newer-wins for
json snapshot faces + take-ours for same-day md doc faces per r432 precedent
+ MSG-0612 owner_since-newer-wins for the shared pool face).
Rebase side inversion: ours-marker = origin base, theirs-marker = my commit.
Gates: all resolved json parse + zero conflict markers + receipt.
"""
import json
import os
import re
import subprocess
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CREATE = 0x08000000

TAKE_MINE = [  # ts-newer-wins (my S6 22:53-57 > origin 22:35-49)
    "docs/daily_report/REPORT-2026-10-03.json",
    "docs/live_usage/LIVE-2026-10-03.json",
    "docs/live_usage/LIVE-latest.json",
    "results/_attrition_guard_scan.json",
    "results/compute_audit.json",
    "results/dashboard_status.js",
    "results/dashboard_status.json",
    "results/fundamental_b_layer_filter.json",
    "results/futures_update_status.json",
    "results/lhb_update_status.json",
    "results/regime_state.json",
    "results/scorecard_v1.json",
    "results/strategy_scorecard.json",
    "results/token_usage.json",
    "results/update_status.json",
]
TAKE_ORIGIN = [  # md same-day doc faces (r432 take-ours precedent) + pool (MSG-0612)
    "docs/daily_report/REPORT-2026-10-03.md",
    "docs/live_usage/LIVE-2026-10-03.md",
    "docs/live_usage/LIVE-latest.md",
    "results/runnable_pool.json",
]
WHY = {
    "docs/daily_report/REPORT-2026-10-03.json": "mine ts 22:56:44 > 22:49:09",
    "docs/live_usage/LIVE-2026-10-03.json": "mine S6 render newer (ceo_live_usage 22:57)",
    "docs/live_usage/LIVE-latest.json": "twin of LIVE-2026-10-03.json",
    "results/_attrition_guard_scan.json": "mine ts 22:57:43 > 22:49:47",
    "results/compute_audit.json": "mine ts 22:53:57 > 22:46:53",
    "results/dashboard_status.js": "twin, mine generated_at 22:57:03 > 22:49:24",
    "results/dashboard_status.json": "mine generated_at 22:57:03 > 22:49:24",
    "results/fundamental_b_layer_filter.json": "mine S6 b_layer_filter later run",
    "results/futures_update_status.json": "mine ts 22:56:09 > 22:48:49",
    "results/lhb_update_status.json": "mine S6 fetch 22:53 later than origin no-op face",
    "results/regime_state.json": "mine S6 market_regime 22:54 later run",
    "results/scorecard_v1.json": "mine stale-takeover derive 22:54 (O-2100 s2.4)",
    "results/strategy_scorecard.json": "mine stale-takeover derive 22:54 (O-2100 s2.4)",
    "results/token_usage.json": "mine generated 22:57:04 > 22:49:26",
    "results/update_status.json": "mine S6 update_daily 22:53 later run",
    "docs/daily_report/REPORT-2026-10-03.md": "same-day doc face, r432 take-ours precedent (r433 receipt)",
    "docs/live_usage/LIVE-2026-10-03.md": "same-day doc face, r432 take-ours precedent (r433 receipt)",
    "docs/live_usage/LIVE-latest.md": "same-day doc face, r432 take-ours precedent (r433 receipt)",
    "results/runnable_pool.json": "MSG-0612 owner_since newer-wins: origin 22:54:12 > mine 22:44:12 "
                                  "(stale-settle family; post-rebase sync_face settle follows)",
}


def git(*a):
    p = subprocess.run(["git"] + list(a), capture_output=True, creationflags=CREATE, cwd=ROOT)
    return p.returncode, (p.stdout or b"") + (p.stderr or b"")


def main():
    receipt = {"round": "r434 bm-c", "pick": "1/2 (dbbad0d28 replay)", "faces": [], "ok": True}
    porc = git("status", "--porcelain")[1].decode("utf-8", "replace")
    uu = [l[3:] for l in porc.splitlines() if l.startswith("UU")]
    expect = TAKE_MINE + TAKE_ORIGIN
    assert sorted(uu) == sorted(expect), "UU set drift: %r" % (uu,)
    for f in TAKE_MINE:
        rc, _ = git("checkout", "--theirs", "--", f)
        assert rc == 0, "checkout --theirs failed " + f
        receipt["faces"].append({"path": f, "side": "theirs(mine)", "why": WHY[f],
                                 "bytes": os.path.getsize(os.path.join(ROOT, f))})
    for f in TAKE_ORIGIN:
        rc, _ = git("checkout", "--ours", "--", f)
        assert rc == 0, "checkout --ours failed " + f
        receipt["faces"].append({"path": f, "side": "ours(origin)", "why": WHY[f],
                                 "bytes": os.path.getsize(os.path.join(ROOT, f))})
    # gates: zero markers + json parseable (js faces skip parse gate)
    bad_markers, bad_json = [], []
    for f in expect:
        raw = open(os.path.join(ROOT, f), "rb").read()
        if re.search(rb"^(<{7}|={7}|>{7}|\|{7})", raw, re.M):
            bad_markers.append(f)
        if f.endswith(".json"):
            try:
                json.loads(raw.decode("utf-8"))
            except Exception as e:
                bad_json.append("%s (%s)" % (f, e))
    receipt["zero_marker_gate"] = bad_markers
    receipt["json_parse_gate"] = bad_json
    if bad_markers or bad_json:
        receipt["ok"] = False
    # pool owner_since winner check (the claw's flagged face)
    pool = json.load(open(os.path.join(ROOT, "results", "runnable_pool.json"), encoding="utf-8"))
    since = set()
    for sh in pool.get("shards", []):
        if sh.get("pool_id", "").startswith(("FUND-VALUE-P1-NULLS", "FUND-DIVLOWVOL-P1-NULLS")) or \
           "fund-value-p1-nulls" in str(sh.get("pool_id", "")) or "fund-divlowvol-p1-nulls" in str(sh.get("pool_id", "")):
            since.add(sh.get("owner_since"))
    receipt["pool_owner_since_after"] = sorted(since)
    out = os.path.join(ROOT, "results", "_r434bmc_rebase_resolve.json")
    with open(out, "w", encoding="utf-8") as fobj:
        json.dump(receipt, fobj, ensure_ascii=False, indent=1)
    print("resolver receipt ->", os.path.relpath(out, ROOT))
    print("markers:", bad_markers or "ZERO", "| json-parse:", bad_json or "ALL-OK",
          "| pool owner_since:", sorted(since))
    print("RESULT:", "OK" if receipt["ok"] else "FAIL")
    return 0 if receipt["ok"] else 1


if __name__ == "__main__":
    sys.exit(main())
