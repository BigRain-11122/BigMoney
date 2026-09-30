"""r278 bm-c rebase wave-2 resolver (18-UU, mine 16:09-16:13 vs bm-a r479 16:06-16:08).

Replay of round-278 commit 36ddee15f onto merged base (origin r479 + replayed r277).
All 18 faces = shared snapshot family (F-20260927-06 structural face).
Mechanism VERBATIM reuse via import of the r271 canon resolver (禁重写律):
deep_ts probe (r100 value-shape gate + r311 deep scan + R350 no-key-excludes),
take-whole-blob, union_ledger (r459 |A u B| >= max assertion), twin same-side
with tie->stage2 (r140). Rebase stages: 2 = merged-base side, 3 = mine.
"""
import os
import subprocess
import sys

sys.path.insert(0, os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "results"))
import _r271bmc_rebase_resolver as canon  # noqa: E402

try:
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
except Exception:
    pass


def main() -> int:
    log = []
    twin_groups = {
        "REPORT": ["docs/daily_report/REPORT-2026-09-30.json",
                   "docs/daily_report/REPORT-2026-09-30.md"],
        "LIVE": ["docs/live_usage/LIVE-2026-09-30.json",
                 "docs/live_usage/LIVE-2026-09-30.md",
                 "docs/live_usage/LIVE-latest.json",
                 "docs/live_usage/LIVE-latest.md"],
        "DASH": ["results/dashboard_status.json", "results/dashboard_status.js"],
        "SCORECARD": ["results/strategy_scorecard.json", "results/scorecard_v1.json"],
    }
    for gname, paths in twin_groups.items():
        t2, t3 = canon.probe(2, paths[0]), canon.probe(3, paths[0])
        side = 3 if t3 > t2 else 2  # tie -> HEAD/ours stage2 (r140)
        for p in paths:
            canon.take(p, side)
        log.append(f"twin-{gname}: s2={t2} s3={t3} -> take-s{side} x{len(paths)}")
    snaps = [
        "results/_attrition_guard_scan.json",
        "results/fundamental_b_layer_filter.json",
        "results/futures_update_status.json",
        "results/lhb_update_status.json",
        "results/token_usage.json",
        "results/update_status.json",
    ]
    for p in snaps:
        t2, t3 = canon.probe(2, p), canon.probe(3, p)
        assert canon.TS_FULL_RE.match(t2) and canon.TS_FULL_RE.match(t3), f"{p}: probe not ts-shaped ({t2!r} vs {t3!r})"
        side = 3 if t3 > t2 else 2
        canon.take(p, side)
        log.append(f"{p}: s2={t2} s3={t3} -> take-s{side}")
    t2, t3 = canon.probe(2, "results/compute_audit.json"), canon.probe(3, "results/compute_audit.json")
    newer = 3 if t3 > t2 else 2
    log.append("compute_audit: union[" + canon.union_ledger(
        "results/compute_audit.json", ["history"],
        lambda e: e.get("ts") or "", newer) + f"] latest-take-s{newer} (s2={t2} s3={t3})")
    t2, t3 = canon.probe(2, "results/regime_state.json"), canon.probe(3, "results/regime_state.json")
    newer = 3 if t3 > t2 else 2
    log.append("regime_state: union[" + canon.union_ledger(
        "results/regime_state.json", ["transitions", "history"],
        lambda e: __import__("json").dumps(e, ensure_ascii=False, sort_keys=True), newer) + f"] top-take-s{newer} (s2={t2} s3={t3})")
    for line in log:
        print(line)
    leftover = subprocess.run(["git", "ls-files", "-u"], capture_output=True, text=True).stdout.strip()
    print("leftover-UU:", leftover or "NONE")
    return 0 if not leftover else 2


if __name__ == "__main__":
    sys.exit(main())
