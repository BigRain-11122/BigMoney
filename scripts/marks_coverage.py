"""Marks lane coverage ledger -- which trading days have intraday evidence.

The T-35 open-fill verification joins each paper state's fill day against
``results/paper/marks/marks-<day>.jsonl`` (the 09:25-15:00 tick capture of
``scripts/update_intraday_marks.py``).  When that file is absent the leg
returns NO_EVIDENCE and rc=1 -- correct, but it cannot distinguish

  * a day whose capture was never possible (the marks task was Disabled,
    the machine was off, or the lane had not started yet) -- permanent, and
    re-running will never produce evidence, from
  * a day that is still being captured (today, before the 15:00 close), or
    a file that is merely late.

Read as a single rc=1 every session, a permanent hole looks exactly like a
transient miss, so the honest "unverifiable" verdict ages into noise.

This face classifies every trading day since the lane started:

  captured            marks file present (rows, traders, non-forced rows)
  missing_historical  a past trading day with no file -- permanent hole
  pending             today's file absent and the capture window is open
  missing_today       today's file absent after the 15:00 close
  (non-trading days are not rows at all)

Output: results/marks_coverage.json -- counters, coverage_pct over the
*closed* days only (today never counts against coverage while its window
is open), and the explicit ``holes`` list a reader can act on.

Usage:
    python scripts/marks_coverage.py            # re-derive the ledger
    python scripts/marks_coverage.py --selftest # offline self-check
"""
import datetime as dt
import json
import os
import sys
import tempfile

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from config import PATHS

MARKS_DIR = os.path.join(PATHS.results_dir, "paper", "marks")
CAL_PATH = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
                        "data", "exchange_calendar.csv")
OUT_PATH = os.path.join(PATHS.results_dir, "marks_coverage.json")
# The 09:25-15:00 capture window closes with the session; after this local
# time a missing file for today is a miss, not a pending capture.
WINDOW_CLOSE_HHMM = (15, 5)


def load_calendar(path: str = CAL_PATH) -> list:
    """Official trading days as ISO strings (E136 face; never derive a
    calendar from the panel it is meant to police)."""
    if not os.path.exists(path):
        return []
    out = []
    with open(path, "r", encoding="utf-8") as fh:
        for line in fh:
            s = line.strip().split(",")[0].strip()
            if not s or s == "date":
                continue
            out.append(s)
    return sorted(out)


def scan_marks(marks_dir: str = MARKS_DIR) -> dict:
    """{iso_date: {"rows": n, "non_forced": n, "traders": k}} for every
    marks-YYYYMMDD.jsonl on disk."""
    out = {}
    if not os.path.isdir(marks_dir):
        return out
    for fn in os.listdir(marks_dir):
        if not (fn.startswith("marks-") and fn.endswith(".jsonl")):
            continue
        dig = fn[len("marks-"):-len(".jsonl")]
        if len(dig) != 8 or not dig.isdigit():
            continue
        iso = f"{dig[:4]}-{dig[4:6]}-{dig[6:]}"
        rows = non_forced = 0
        traders = set()
        with open(os.path.join(marks_dir, fn), encoding="utf-8") as fh:
            for line in fh:
                line = line.strip()
                if not line:
                    continue
                rows += 1
                try:
                    rec = json.loads(line)
                except ValueError:
                    continue
                if isinstance(rec, dict):
                    if not rec.get("forced"):
                        non_forced += 1
                    if rec.get("trader"):
                        traders.add(rec["trader"])
        out[iso] = {"rows": rows, "non_forced": non_forced,
                    "traders": len(traders)}
    return out


def classify(calendar: list, marks: dict, now: dt.datetime) -> dict:
    """Per-trading-day status table. ``calendar`` = ISO days (sorted)."""
    today = now.strftime("%Y-%m-%d")
    closed_window = (now.hour, now.minute) >= WINDOW_CLOSE_HHMM
    days = [d for d in calendar if d <= today]
    # The lane starts at its first captured day; earlier trading days had
    # no capture lane at all and are not holes.
    if marks:
        lane_start = min(marks)
    else:
        lane_start = today
    rows = []
    for d in days:
        if d < lane_start:
            continue
        m = marks.get(d)
        if m:
            status = "captured"
        elif d < today:
            status = "missing_historical"
        elif closed_window:
            status = "missing_today"
        else:
            status = "pending"
        row = {"date": d, "status": status}
        if m:
            row.update(m)
        rows.append(row)
    closed = [r for r in rows if r["date"] != today]
    n_closed = len(closed)
    n_cap = sum(1 for r in closed if r["status"] == "captured")
    holes = [r["date"] for r in rows
             if r["status"] in ("missing_historical", "missing_today")]
    return {
        "as_of": now.strftime("%Y-%m-%dT%H:%M:%S"),
        "lane_start": lane_start,
        "first_trading_day_seen": days[0] if days else None,
        "last_trading_day_seen": days[-1] if days else None,
        "capture_window_open": not closed_window,
        "counters": {
            "trading_days_since_lane_start": len(rows),
            "closed_days": n_closed,
            "captured": n_cap,
            "holes": len(holes),
            "pending": sum(1 for r in rows if r["status"] == "pending"),
            "coverage_pct_closed": (round(100.0 * n_cap / n_closed, 2)
                                    if n_closed else None),
        },
        "holes": holes,
        "last_captured": max(marks) if marks else None,
        "verdict": ("complete" if not holes else
                    f"holes={len(holes)}"),
        "days": rows,
    }


def run() -> int:
    cal = load_calendar()
    if not cal:
        print("marks_coverage: exchange calendar missing -- cannot classify "
              "(exit 2)")
        return 2
    marks = scan_marks()
    if not os.path.isdir(MARKS_DIR):
        print(f"marks_coverage: marks dir absent {MARKS_DIR} (exit 2)")
        return 2
    rep = classify(cal, marks, dt.datetime.now())
    with open(OUT_PATH, "w", encoding="utf-8") as fh:
        json.dump(rep, fh, ensure_ascii=False, indent=1)
    c = rep["counters"]
    print(f"marks_coverage: {rep['verdict']} "
          f"captured {c['captured']}/{c['closed_days']} closed days "
          f"({c['coverage_pct_closed']}%), pending {c['pending']}, "
          f"last captured {rep['last_captured']} -> {OUT_PATH}")
    if rep["holes"]:
        print(f"  permanent holes: {', '.join(rep['holes'])}")
    return 0


def _selftest() -> bool:
    ok = True

    def check(name, cond):
        nonlocal ok
        ok &= bool(cond)
        print(f"[{'PASS' if cond else 'FAIL'}] {name}")

    cal = ["2026-10-19", "2026-10-20", "2026-10-21", "2026-10-22",
           "2026-10-23", "2026-10-26", "2026-10-27"]
    with tempfile.TemporaryDirectory() as td:
        marks_dir = os.path.join(td, "marks")
        os.makedirs(marks_dir)
        for dig in ("20261019", "20261020", "20261021"):
            with open(os.path.join(marks_dir, f"marks-{dig}.jsonl"), "w",
                      encoding="utf-8") as fh:
                fh.write('{"trader": "T-A", "ts": "2026-10-19T09:25:00"}\n')
                fh.write('{"trader": "T-A", "forced": true, '
                         '"ts": "2026-10-19T12:00:00"}\n')
                fh.write('{"trader": "T-B", "ts": "2026-10-19T09:26:00"}\n')
        marks = scan_marks(marks_dir)
        check("scan finds 3 files, ignores nothing valid", len(marks) == 3)
        check("scan counts rows/non-forced/traders",
              marks["2026-10-19"] == {"rows": 3, "non_forced": 2,
                                      "traders": 2})
        os.makedirs(os.path.join(marks_dir, "subdir"), exist_ok=True)
        with open(os.path.join(marks_dir, "notes.txt"), "w") as fh:
            fh.write("x")
        check("non-marks files ignored", len(scan_marks(marks_dir)) == 3)

        # (1) mid-session on 10-27: today missing = pending, closed holes
        rep = classify(cal, marks, dt.datetime(2026, 10, 27, 10, 0))
        st = {r["date"]: r["status"] for r in rep["days"]}
        check("today missing before the close is pending, not a hole",
              st["2026-10-27"] == "pending")
        check("past trading day without a file is a permanent hole",
              st["2026-10-22"] == "missing_historical"
              and st["2026-10-23"] == "missing_historical")
        check("captured days are captured",
              st["2026-10-19"] == "captured" and st["2026-10-21"] == "captured")
        check("holes list is exactly the un-captured past days",
              rep["holes"] == ["2026-10-22", "2026-10-23", "2026-10-26"])
        check("coverage counts closed days only (3/6 => 50.0%)",
              rep["counters"]["closed_days"] == 6
              and rep["counters"]["coverage_pct_closed"] == 50.0)
        check("verdict names the hole count", rep["verdict"] == "holes=3")

        # (2) after the close with today still missing -> today is a hole
        rep2 = classify(cal, marks, dt.datetime(2026, 10, 27, 15, 30))
        st2 = {r["date"]: r["status"] for r in rep2["days"]}
        check("today missing after the close is a hole",
              st2["2026-10-27"] == "missing_today"
              and "2026-10-27" in rep2["holes"])
        check("today after the close joins the holes but not the closed denominator",
              rep2["counters"]["closed_days"] == 6
              and len(rep2["holes"]) == 4)

        # (3) nothing captured at all -> lane starts today, no phantom holes
        rep3 = classify(cal, {}, dt.datetime(2026, 10, 27, 10, 0))
        check("no captures at all => zero holes, not a fake 6-day hole",
              rep3["holes"] == [] and rep3["lane_start"] == "2026-10-27"
              and rep3["counters"]["closed_days"] == 0)

        # (4) weekend days are not rows
        check("non-trading calendar days never appear as rows",
              all(r["date"] in cal for r in rep["days"])
              and "2026-10-24" not in {r["date"] for r in rep["days"]})

    # (5) a real calendar must exist and be sorted/parseable
    real = load_calendar()
    check("real exchange calendar loads", len(real) > 100)
    check("real calendar is sorted and ISO", real == sorted(real)
          and len(real[0]) == 10)
    return ok


def main(argv=None) -> int:
    argv = sys.argv[1:] if argv is None else argv
    if "--selftest" in argv:
        ok = _selftest()
        print(f"selftest: {'PASS' if ok else 'FAIL'}")
        return 0 if ok else 1
    return run()


if __name__ == "__main__":
    sys.exit(main())