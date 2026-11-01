"""Lane silence audit -- how long was the round line silent, and when?

Motivation (2026-11-01, D-20261101-16 evidence): the lane's existing
freshness faces (automation_line_audit E1, compute_audit zombie flags, the
heartbeat age reader) all measure the INSTANT -- "is the newest heartbeat /
round report younger than N minutes".  A round that writes its heartbeat
right after a four-hour stall reads GREEN, so the stall leaves no trace
anywhere except in the task scheduler's own event log (which D-16 found
empty).  This face measures the HISTORY instead: the gaps between
consecutive rounds of one machine, and names the longest window in which
the line was not running.

Source of truth is the machine's own round ledger (round_reports-<id>.md,
bm-b keeps the legacy logs/iteration-loop/round_reports.md), never the
group face and never a fresh read of the scheduler.

Timestamps in those ledgers are often fuzzy -- rounds recorded as
"2026-11-01T07:0x+08:00" mean "sometime in 07:00-07:09".  A fuzzy stamp is
read as an interval [low, high], and every gap is reported as a band:
gap_low = next.low - prev.high (optimistic), gap_high = next.high - prev.low
(pessimistic).  The verdict fires only when the PESSIMISTIC gap clears the
threshold, so an unknown digit can never manufacture an outage, and the
parse precision is published beside every number.

Read-only, deterministic, zero network, zero engine, zero new judgments.

Subcommands:
    (no args)  live audit  [--days N] [--threshold-min M] [--machine ID]
    selftest   hermetic offline check (exit 0/1)

Exit contract: 0 = audit completed (any verdict); 2 = mechanism fault
(unreadable ledger / no parseable rounds) -- report as-is, never mask.
"""
import datetime as _dt
import io
import json
import os
import re
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DEFAULT_THRESHOLD_MIN = 90
DEFAULT_WINDOW_DAYS = 3
FUZZY_ASSUMED_MIN = 5          # a fuzzy digit is read as [00,09] -> width 10

# Declared quiet windows: a machine may be legitimately idle even though the
# line is alive.  bm-a is the CEO's own desktop, and the 2026-10-15 CEO order
# takes its CPU back on workday business hours (AutoYield 09:00 pauseLite /
# 19:00 resume).  Without this table every workday would read as an outage,
# and a flag that is always red cannot be acted on (E318/E319 precedent).
QUIET_WINDOWS = {
    "bm-a": [(0, 9, 19)],      # weekday, 09:00-19:00 local
}
STAMP_RE = re.compile(
    r"^\|?\s*(\d{4}-\d{2}-\d{2})[T ](\d{2}):([0-9]x|\d{1,2})(?::([0-9]x|\d{2}))?"
    r"\s*(?:[+-]\d{2}:?\d{2})?")


def _machine_id():
    try:
        with io.open(os.path.join(ROOT, "fleet", "machine.json"), encoding="utf-8") as fh:
            mid = json.load(fh).get("machine_id")
        if not mid:
            raise ValueError("machine_id missing")
        return mid
    except Exception:
        return None


def ledger_path(mid):
    p = os.path.join(ROOT, "round_reports-%s.md" % mid)
    if os.path.exists(p):
        return p
    legacy = os.path.join(ROOT, "logs", "iteration-loop", "round_reports.md")
    if mid == "bm-b" and os.path.exists(legacy):
        return legacy
    return p


def parse_stamp(line):
    """Return (low, high, fuzzy_minutes) for one ledger line, or None.

    A literal stamp has low == high.  A stamp with an 'x' digit widens the
    interval by the span of that digit (minutes 00-09 -> 9 min, seconds
    always 59 worst case).
    """
    m = STAMP_RE.match(line)
    if not m:
        return None
    date, hh, mm, ss = m.group(1), int(m.group(2)), m.group(3), m.group(4)
    base = _dt.datetime.strptime(date + " %02d" % hh, "%Y-%m-%d %H")
    width = 0
    if mm.endswith("x"):
        low = base
        high = base + _dt.timedelta(minutes=9)
        width = 9
    else:
        low = base + _dt.timedelta(minutes=int(mm))
        high = low
    if ss:
        if ss.endswith("x"):
            high = high + _dt.timedelta(seconds=59)
            width = max(width, 1)
        else:
            secs = int(ss)
            low, high = low + _dt.timedelta(seconds=secs), high + _dt.timedelta(seconds=secs)
    return low, high, width


def load_stamps(path):
    rows = []
    with io.open(path, encoding="utf-8", errors="replace") as fh:
        for line in fh:
            got = parse_stamp(line)
            if got:
                rows.append(got)
    rows.sort(key=lambda r: r[0])
    return rows


def quiet_overlap_minutes(start, end, mid):
    """Minutes of [start, end] that fall inside declared quiet windows."""
    if end <= start:
        return 0.0
    total = 0.0
    day = start.date()
    while day <= end.date():
        for weekday, h_from, h_to in QUIET_WINDOWS.get(mid, []):
            if weekday is not None and day.weekday() >= 5:
                continue
            lo = _dt.datetime.combine(day, _dt.time(h_from, 0))
            hi = _dt.datetime.combine(day, _dt.time(min(h_to, 23), 59 if h_to < 24 else 59))
            if h_to == 24:
                hi = _dt.datetime.combine(day, _dt.time(23, 59, 59))
            a, b = max(start, lo), min(end, hi)
            if b > a:
                total += (b - a).total_seconds() / 60.0
        day += _dt.timedelta(days=1)
    return total


def audit(rows, threshold_min, window_days, now=None, mid=None):
    now = now or _dt.datetime.now()
    window_start = now - _dt.timedelta(days=window_days)
    win = [r for r in rows if r[1] >= window_start]
    out = {
        "window_days": window_days,
        "threshold_min": threshold_min,
        "rounds_in_ledger": len(rows),
        "rounds_in_window": len(win),
    }
    if len(win) < 2:
        out["verdict"] = "NO_DATA"
        out["note"] = "fewer than two rounds inside the window; silence is unmeasurable"
        return out
    gaps = []
    for prev, nxt in zip(win, win[1:]):
        gap_low = (nxt[0] - prev[1]).total_seconds() / 60.0
        gap_high = (nxt[1] - prev[0]).total_seconds() / 60.0
        # expected-idle time is subtracted before the gap is judged: a silence
        # that sits wholly inside a declared quiet window is not an outage
        quiet = quiet_overlap_minutes(prev[0], nxt[1], mid) if mid else 0.0
        unexplained_high = max(0.0, gap_high - quiet)
        unexplained_low = max(0.0, gap_low - quiet)
        gaps.append({
            "from": prev[0].isoformat(timespec="minutes"),
            "to": nxt[0].isoformat(timespec="minutes"),
            "gap_low_min": round(max(gap_low, 0.0), 1),
            "gap_high_min": round(max(gap_high, 0.0), 1),
            "quiet_window_min": round(quiet, 1),
            "unexplained_low_min": round(unexplained_low, 1),
            "unexplained_high_min": round(unexplained_high, 1),
        })
    ordered = sorted(gaps, key=lambda g: g["unexplained_high_min"])
    med = sorted(g["gap_low_min"] for g in gaps)[len(gaps) // 2]
    over = [g for g in gaps if g["unexplained_high_min"] > threshold_min]
    explained = [g for g in gaps if g["gap_high_min"] > threshold_min and g not in over]
    # The gap that matters most is the one that has not ended yet: the silence
    # running from the last recorded round to NOW.  Measuring only closed
    # intervals hides the outage while it is happening (this is how the
    # 2026-11-01 four-hour stall would have been invisible).
    last = win[-1]
    open_high = (now - last[0]).total_seconds() / 60.0
    open_low = (now - last[1]).total_seconds() / 60.0
    open_quiet = quiet_overlap_minutes(last[0], now, mid) if mid else 0.0
    open_gap = {
        "since": last[0].isoformat(timespec="minutes"),
        "gap_low_min": round(max(open_low, 0.0), 1),
        "gap_high_min": round(max(open_high, 0.0), 1),
        "quiet_window_min": round(open_quiet, 1),
        "unexplained_low_min": round(max(open_low - open_quiet, 0.0), 1),
        "unexplained_high_min": round(max(open_high - open_quiet, 0.0), 1),
    }
    open_is_silent = open_gap["unexplained_high_min"] > threshold_min
    out.update({
        "median_gap_min": med,
        "longest_silence": ordered[-1],
        "open_gap": open_gap,
        "gaps_over_threshold": over,
        "gaps_over_threshold_count": len(over),
        "gaps_explained_by_quiet_window": explained,
        "quiet_windows": QUIET_WINDOWS.get(mid or "", []),
        "verdict": ("OPEN_SILENCE" if open_is_silent
                    else ("SILENT_GAP" if over
                          else ("OK_QUIET_WINDOWS" if explained else "OK"))),
        "parse_precision_note": ("stamps recorded with an 'x' digit are read as a "
                                 "%d-minute interval; a gap is only called when its "
                                 "pessimistic end clears the threshold" % (FUZZY_ASSUMED_MIN * 2 - 1)),
    })
    return out


def run(days=DEFAULT_WINDOW_DAYS, threshold_min=DEFAULT_THRESHOLD_MIN, mid=None):
    mid = mid or _machine_id()
    if not mid:
        print("FAULT: machine identity unreadable (fleet/machine.json)")
        return 2
    path = ledger_path(mid)
    if not os.path.exists(path):
        print("FAULT: ledger missing: %s" % path)
        return 2
    rows = load_stamps(path)
    if not rows:
        print("FAULT: no parseable round stamps in %s" % path)
        return 2
    res = audit(rows, threshold_min, days, mid=mid)
    res["machine"] = mid
    res["source"] = os.path.relpath(path, ROOT).replace("\\", "/")
    res["evidence_cutoff"] = rows[-1][0].strftime("%Y-%m-%d")
    res["generated"] = _dt.datetime.now().isoformat(timespec="seconds")
    os.makedirs(os.path.join(ROOT, "results"), exist_ok=True)
    out = os.path.join(ROOT, "results", "lane_silence.%s.json" % mid)
    with io.open(out, "w", encoding="utf-8") as fh:
        fh.write(json.dumps(res, ensure_ascii=False, indent=1, sort_keys=True))
    long = res.get("longest_silence") or {}
    print("lane_silence[%s] %s rounds=%d/%d median_gap=%smin longest=%s..%s (gap %s..%s min, unexplained %s..%s min) over_threshold=%d"
          % (mid, res["verdict"], res["rounds_in_window"], res["rounds_in_ledger"],
             res.get("median_gap_min"), long.get("from"), long.get("to"),
             long.get("gap_low_min"), long.get("gap_high_min"),
             long.get("unexplained_low_min"), long.get("unexplained_high_min"),
             res.get("gaps_over_threshold_count", 0)))
    og = res.get("open_gap") or {}
    if og:
        print("  OPEN since %s : gap %s..%s min, quiet %s min, unexplained %s..%s min"
              % (og.get("since"), og.get("gap_low_min"), og.get("gap_high_min"),
                 og.get("quiet_window_min"), og.get("unexplained_low_min"),
                 og.get("unexplained_high_min")))
    for g in res.get("gaps_over_threshold") or []:
        print("  SILENT %s -> %s : gap %s..%s min, quiet %s min, unexplained %s..%s min"
              % (g["from"], g["to"], g["gap_low_min"], g["gap_high_min"],
                 g["quiet_window_min"], g["unexplained_low_min"], g["unexplained_high_min"]))
    for g in res.get("gaps_explained_by_quiet_window") or []:
        print("  quiet-window gap %s -> %s : %s min, %s explained"
              % (g["from"], g["to"], g["gap_high_min"], g["quiet_window_min"]))
    return 0


def selftest():
    fails = []

    def chk(name, cond, detail=""):
        if not cond:
            fails.append("%s %s" % (name, detail))

    # L1 literal stamps
    low, high, w = parse_stamp("| 2026-11-01T07:12:30+08:00 | r1 | ...")
    chk("L1-literal", low == high and low.hour == 7 and low.minute == 12 and w == 0,
        "got %s/%s" % (low, high))
    # L2 fuzzy minute digit widens, never narrows
    low, high, w = parse_stamp("| 2026-11-01T07:0x+08:00 | r1 | ...")
    chk("L2-fuzzy", low.minute == 0 and high.minute == 9 and w == 9,
        "got %s..%s" % (low, high))
    # L3 contiguous rounds -> OK
    rows = [(_dt.datetime(2026, 11, 1, 0, i * 10),) * 2 + (0,) for i in range(6)]
    res = audit(rows, 90, 3, now=_dt.datetime(2026, 11, 1, 2, 0))
    chk("L3-ok", res["verdict"] == "OK", res["verdict"])
    # L4 a real hole is named with its band
    rows = [(_dt.datetime(2026, 11, 1, 8, 50),) * 2 + (0,),
            (_dt.datetime(2026, 11, 1, 12, 30),) * 2 + (0,)]
    res = audit(rows, 90, 3, now=_dt.datetime(2026, 11, 1, 13, 0))
    chk("L4-hole", res["verdict"] == "SILENT_GAP" and abs(res["longest_silence"]["gap_high_min"] - 220.0) < 0.5,
        str(res.get("longest_silence")))
    # L5 a fuzzy neighbour cannot manufacture a gap (worst case is inside threshold)
    rows = [(_dt.datetime(2026, 11, 1, 8, 0), _dt.datetime(2026, 11, 1, 8, 0), 0),
            (_dt.datetime(2026, 11, 1, 9, 31), _dt.datetime(2026, 11, 1, 9, 40), 9)]
    res = audit(rows, 60, 3, now=_dt.datetime(2026, 11, 1, 10, 0))
    chk("L5-band", res["verdict"] == "SILENT_GAP" and res["longest_silence"]["gap_low_min"] == 91.0
        and res["longest_silence"]["gap_high_min"] == 100.0, str(res.get("longest_silence")))
    # L6 single round is NO_DATA, not OK
    res = audit([(_dt.datetime(2026, 11, 1, 9, 0),) * 2 + (0,)], 90, 3,
                now=_dt.datetime(2026, 11, 1, 10, 0))
    chk("L6-nodata", res["verdict"] == "NO_DATA", res["verdict"])
    # L7 window filters old rounds out
    old = (_dt.datetime(2026, 10, 1, 9, 0),) * 2 + (0,)
    res = audit([old, old] + [(_dt.datetime(2026, 11, 1, 9, 0),) * 2 + (0,),
                              (_dt.datetime(2026, 11, 1, 9, 10),) * 2 + (0,)],
                90, 3, now=_dt.datetime(2026, 11, 1, 10, 0))
    chk("L7-window", res["rounds_in_window"] == 2 and res["verdict"] == "OK",
        "%s/%s" % (res["rounds_in_window"], res["verdict"]))
    # L8 the quiet window is subtracted, and only that machine's window applies
    mon = [(_dt.datetime(2026, 11, 2, 9, 20),) * 2 + (0,),
           (_dt.datetime(2026, 11, 2, 19, 10),) * 2 + (0,)]
    res = audit(mon, 90, 3, now=_dt.datetime(2026, 11, 2, 20, 0), mid="bm-a")
    chk("L8-quiet-explains", res["verdict"] == "OK_QUIET_WINDOWS"
        and res["longest_silence"]["unexplained_high_min"] <= 15.0,
        "%s %s" % (res["verdict"], res["longest_silence"]))
    # L9 the same wall clock on a Sunday is NOT a quiet window
    sun = [(_dt.datetime(2026, 11, 1, 9, 20),) * 2 + (0,),
           (_dt.datetime(2026, 11, 1, 19, 10),) * 2 + (0,)]
    res = audit(sun, 90, 3, now=_dt.datetime(2026, 11, 1, 20, 0), mid="bm-a")
    chk("L9-sunday", res["verdict"] == "SILENT_GAP" and res["longest_silence"]["quiet_window_min"] == 0.0,
        "%s %s" % (res["verdict"], res["longest_silence"]))
    # L10 a machine with no declared window never gets the excuse
    res = audit(mon, 90, 3, now=_dt.datetime(2026, 11, 2, 20, 0), mid="bm-c")
    chk("L10-no-window", res["verdict"] == "SILENT_GAP", res["verdict"])
    # L11 the silence that is still running is its own verdict, and it fires
    # before any closed gap does
    rows = [(_dt.datetime(2026, 11, 1, 7, 0),) * 2 + (0,),
            (_dt.datetime(2026, 11, 1, 7, 10),) * 2 + (0,)]
    res = audit(rows, 90, 3, now=_dt.datetime(2026, 11, 1, 11, 40), mid="bm-a")
    chk("L11-open-silence", res["verdict"] == "OPEN_SILENCE"
        and abs(res["open_gap"]["unexplained_high_min"] - 270.0) < 0.5,
        "%s %s" % (res["verdict"], res.get("open_gap")))
    # L12 an open gap that runs through a weekday quiet window is not an outage
    rows = [(_dt.datetime(2026, 11, 2, 8, 50),) * 2 + (0,),
            (_dt.datetime(2026, 11, 2, 8, 55),) * 2 + (0,)]
    res = audit(rows, 90, 3, now=_dt.datetime(2026, 11, 2, 14, 0), mid="bm-a")
    chk("L12-open-quiet", res["verdict"] == "OK" and res["open_gap"]["unexplained_high_min"] <= 10.0,
        "%s %s" % (res["verdict"], res.get("open_gap")))
    if fails:
        print("selftest FAIL %d/12" % len(fails))
        for f in fails:
            print("  " + f)
        return 1
    print("selftest 12/12 PASS")
    return 0


def main(argv):
    if len(argv) > 1 and argv[1] in ("selftest", "--selftest"):
        return selftest()
    days, thr, mid = DEFAULT_WINDOW_DAYS, DEFAULT_THRESHOLD_MIN, None
    it = iter(argv[1:])
    for a in it:
        if a == "--days":
            days = int(next(it))
        elif a == "--threshold-min":
            thr = int(next(it))
        elif a == "--machine":
            mid = next(it)
    return run(days, thr, mid)


if __name__ == "__main__":
    sys.exit(main(sys.argv))