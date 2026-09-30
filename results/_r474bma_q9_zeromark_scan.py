"""Q9 (D-20260930-31) acceptance probe: full-snapshot zero-mark scan.

The audit tool's Q9 finding (20 zero-mark rows in the 09:35 tick, 150
records) predates the r473 P0 fix (update_intraday_marks fallback chain +
_check_no_silent_zero write gate, live-fired 13:15 tick clean).

D-31 Q9 acceptance: "修后断言：全量快照零标价行 = 0". This probe scans the
CURRENT day marks file at position-record level (not envelope level) and
splits by fix phase (pre/post the 13:15 deployment). Post-fix phase must
show zero-mark records == 0. Pre-fix rows are preserved audit evidence
(r473 push-log: 20 zero-price evidence rows preserved on purpose) and are
reported, not repaired (no history rewrite -- r444/A7 discipline).

Read-only, deterministic, zero network. Exit 0 = post-fix assertion holds
(+ honest pre-fix evidence count); exit 2 = post-fix zero-mark found
(machine check failed -- DO NOT mask, report as-is).
"""
import json
import os
import sys
from datetime import datetime, timezone

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
MARKS = os.path.join(ROOT, "results", "paper", "marks", "marks-20260930.jsonl")
OUT = os.path.join(ROOT, "results", "_r474bma_q9_zeromark_scan.json")
FIX_TS = "2026-09-30T13:15"  # r473 fix live-fire tick (deployment boundary)


def scan():
    pre_zero, post_zero = [], []
    pos_total = 0
    ticks = 0
    with open(MARKS, encoding="utf-8") as fh:
        for line in fh:
            line = line.strip()
            if not line:
                continue
            row = json.loads(line)
            ts = str(row.get("ts", ""))
            ticks += 1
            phase = "post" if ts >= FIX_TS else "pre"
            for tid, t in (row.get("traders") or {}).items():
                for p in (t.get("positions") or []):
                    pos_total += 1
                    mark = p.get("mark")
                    mv = p.get("market_value_cny")
                    if mark in (0, 0.0, None) or mv in (0, 0.0, None):
                        rec = {"tick": ts, "trader": tid, "symbol": p.get("symbol"),
                               "mark": mark, "mv": mv}
                        (post_zero if phase == "post" else pre_zero).append(rec)
    return pre_zero, post_zero, pos_total, ticks


def main():
    pre_zero, post_zero, pos_total, ticks = scan()
    out = {
        "probe": "q9_full_snapshot_zero_mark_scan",
        "decision": "D-20260930-31 Q9 (513100 fix acceptance)",
        "fix_boundary": FIX_TS,
        "generated_utc": datetime.now(timezone.utc).isoformat(),
        "ticks_scanned": ticks,
        "position_records": pos_total,
        "pre_fix_zero_mark_records": len(pre_zero),
        "post_fix_zero_mark_records": len(post_zero),
        "pre_fix_examples": pre_zero[:5],
        "post_fix_examples": post_zero[:5],
        "verdict": "PASS" if not post_zero else "FAIL",
        "note": ("pre-fix zero-mark rows are preserved audit evidence (no history "
                 "rewrite); post-fix phase is the acceptance face per D-31 Q9."),
    }
    with open(OUT, "w", encoding="utf-8") as fh:
        json.dump(out, fh, ensure_ascii=False, indent=1)
    print(f"q9 scan: ticks={ticks} position_records={pos_total} "
          f"pre_fix_zero={len(pre_zero)} post_fix_zero={len(post_zero)} "
          f"verdict={out['verdict']}")
    print(f"evidence -> {os.path.relpath(OUT, ROOT)}")
    if post_zero:
        sys.exit(2)


if __name__ == "__main__":
    main()
