"""r340 bm-c S0: resolve S6 shared-derive-face conflicts by wall-clock-newest side (r505 law).

13 UU files from ride r339c rebase onto origin (bm-a r526 S6 outputs).
Law: same-day idempotent regen faces forbid union; take wall-clock-newest side.
Timestamp probe: max ISO-8601-like ts found in each stage's raw bytes.
Fallback if probe empty both sides: take :3: (origin) and record honest note.
"""
import re
import subprocess
import sys

GIT = ["git", "-C", r"K:\Fluxgroup\FluxGroup\quant\bigmoney"]

UU = [
    "docs/daily_report/REPORT-2026-10-01.json",
    "docs/daily_report/REPORT-2026-10-01.md",
    "docs/live_usage/LIVE-2026-10-01.json",
    "docs/live_usage/LIVE-2026-10-01.md",
    "docs/live_usage/LIVE-latest.json",
    "docs/live_usage/LIVE-latest.md",
    "results/_attrition_guard_scan.json",
    "results/compute_audit.json",
    "results/fundamental_b_layer_filter.json",
    "results/futures_update_status.json",
    "results/lhb_update_status.json",
    "results/regime_state.json",
    "results/token_usage.json",
    "results/update_status.json",
]

TS_RE = re.compile(
    rb"20\d{2}-\d{2}-\d{2}[T ]\d{2}:\d{2}:\d{2}(?:\.\d+)?(?:[+-]\d{2}:?\d{2}|Z)?"
)


def stage(stage_no: int, path: str) -> bytes:
    return subprocess.check_output(
        GIT + ["show", f":{stage_no}:{path}"]
    )


def max_ts(b: bytes):
    hits = [m.group(0).decode("ascii", "replace") for m in TS_RE.finditer(b)]
    return max(hits) if hits else None


def main():
    picks = []
    for p in UU:
        ours = stage(2, p)
        theirs = stage(3, p)
        t_ours, t_theirs = max_ts(ours), max_ts(theirs)
        if t_ours is None and t_theirs is None:
            side, why = theirs, "both-empty-probe-fallback-origin"
        elif t_theirs is None or (t_ours is not None and t_ours >= t_theirs):
            side, why = ours, f"ours-newer({t_ours} >= {t_theirs})"
        else:
            side, why = theirs, f"theirs-newer({t_theirs} > {t_ours})"
        with open(p, "wb") as f:
            f.write(side)
        subprocess.check_call(GIT + ["add", "--", p])
        picks.append((p, why))
    for p, why in picks:
        print(f"{p}: {why}")
    # marker sweep assertion (r312): zero conflict markers left in tree
    bad = []
    for p in UU:
        with open(p, "rb") as f:
            if b"<<<<<<<" in f.read():
                bad.append(p)
    if bad:
        print("MARKERS LEFT:", bad)
        sys.exit(1)
    print("RESOLVE OK", len(UU), "files")


if __name__ == "__main__":
    main()
