"""r340 bm-c addendum rebase conflict resolver v2 (16 UU).

r505 law: same-day idempotent regen faces -> wall-clock-newest side.
r378/r513 law: host=bm-a single-writer faces (dashboard_status.*, scorecard_v1,
strategy_scorecard) -> take origin (:3:) unconditionally (bm-c non-host writes yield).
"""
import re
import subprocess
import sys

GIT = ["git", "-C", r"K:\Fluxgroup\FluxGroup\quant\bigmoney"]

HOST_OWNED = {
    "results/dashboard_status.js",
    "results/dashboard_status.json",
    "results/scorecard_v1.json",
    "results/strategy_scorecard.json",
}

UU = [
    "docs/daily_report/REPORT-2026-10-01.json",
    "docs/daily_report/REPORT-2026-10-01.md",
    "docs/live_usage/LIVE-2026-10-01.json",
    "docs/live_usage/LIVE-2026-10-01.md",
    "docs/live_usage/LIVE-latest.json",
    "docs/live_usage/LIVE-latest.md",
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

TS_RE = re.compile(
    rb"20\d{2}-\d{2}-\d{2}[T ]\d{2}:\d{2}:\d{2}(?:\.\d+)?(?:[+-]\d{2}:?\d{2}|Z)?"
)


def stage(no, path):
    return subprocess.check_output(GIT + ["show", f":{no}:{path}"])


def max_ts(b):
    hits = [m.group(0).decode("ascii", "replace") for m in TS_RE.finditer(b)]
    return max(hits) if hits else None


def main():
    for p in UU:
        ours, theirs = stage(2, p), stage(3, p)
        if p in HOST_OWNED:
            side, why = theirs, "host-owned(bm-a)-take-origin"
        else:
            to, tt = max_ts(ours), max_ts(theirs)
            if to is None and tt is None:
                side, why = theirs, "probe-empty-fallback-origin"
            elif tt is None or (to is not None and to >= tt):
                side, why = ours, f"ours-newer({to} >= {tt})"
            else:
                side, why = theirs, f"theirs-newer({tt} > {to})"
        with open(p, "wb") as f:
            f.write(side)
        subprocess.check_call(GIT + ["add", "--", p])
        print(f"{p}: {why}")
    bad = [p for p in UU if b"<<<<<<<" in open(p, "rb").read()]
    if bad:
        print("MARKERS LEFT:", bad)
        sys.exit(1)
    print("RESOLVE v2 OK", len(UU), "files")


if __name__ == "__main__":
    main()
