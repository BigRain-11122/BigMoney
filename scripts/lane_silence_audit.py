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
LANE_TASKS = {
    "bm-a": ["Bigmoney-IterationLoop", "Bigmoney-LoopWatchdog", "HQ-Patrol-BigMoney",
             "Bigmoney-SatEngine-bm-b"],
    "bm-b": ["Bigmoney-IterationLoop", "Bigmoney-LoopWatchdog", "Bigmoney-SatEngine-bm-b"],
    "bm-c": ["Bigmoney-IterationLoop", "Bigmoney-LoopWatchdog", "Bigmoney-SatEngine-bm-b"],
}
# "Absent" (r1217): a task the machine DECLARES but the scheduler has never heard of.
# Before this it collapsed into UNKNOWN -- the face said "I could not read the switch"
# about a switch that does not exist.  And the saturation engine (the ignition face of
# the compute lane) was outside LANE_TASKS entirely: on 2026-11-01 the engine was dead
# 49 min (heartbeat 2924s, task Disabled) while this leg still printed LANE_ENABLED.
TASK_STATES = ("Ready", "Running", "Disabled", "Absent")
ABSENT = "Absent"
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


PROBE_OK = "PROBE_OK"          # sentinel: proves the scheduler answered at all


def _query_task_states(names):
    """Task scheduler -> {name: state}.  CASE_NO_WINDOW: a probe must not flash a console.

    The sentinel line separates "these tasks are not registered" from "the scheduler
    never answered": both give an empty list of tasks, and reading the second as the
    first would turn a broken probe into a report of missing lane tasks.
    """
    import subprocess
    ps = ("$ProgressPreference='SilentlyContinue';"
          "Get-ScheduledTask -TaskName %s -ErrorAction SilentlyContinue | "
          "ForEach-Object { $_.TaskName + '=' + $_.State }; "
          "Write-Output '%s'"
          % (",".join("'%s'" % n for n in names), PROBE_OK))
    kw = {}
    if os.name == "nt":
        kw["creationflags"] = 0x08000000
    p = subprocess.run(["powershell", "-NoProfile", "-NonInteractive", "-Command", ps],
                       capture_output=True, text=True, timeout=120, **kw)
    lines = [ln.strip() for ln in (p.stdout or "").splitlines()]
    if p.returncode != 0 or PROBE_OK not in lines:
        raise RuntimeError("scheduler probe did not answer (rc=%s)" % p.returncode)
    out = {}
    for ln in lines:
        if "=" in ln:
            k, v = ln.split("=", 1)
            out[k.strip()] = v.strip()
    return out


def read_task_states(names, runner=None):
    """Are the lane's own scheduled tasks switched on?

    The scheduler is asked, never the ledger: a Disabled task and a task with nothing to
    do write the SAME round line, which is why this had to be found by hand three times
    in one day.  Three states, three different actions:
      Absent   -- the machine declares this task but it is not registered at all
                  (register it; nothing else can heal it)
      Disabled -- registered but switched off (enabling it is the whole fix)
      UNKNOWN  -- the scheduler did not answer; an unread switch is neither on nor off
                  (r98: unknown is not empty)
    """
    names = list(names or [])
    if not names:
        return {}
    runner = runner or _query_task_states
    try:
        got = runner(names) or {}
        answered = True
    except Exception:                                               # noqa: BLE001
        got, answered = {}, False
    out = {}
    for n in names:
        if got.get(n) in TASK_STATES:
            out[n] = got[n]
        elif answered and n not in got:
            out[n] = ABSENT
        else:
            out[n] = "UNKNOWN"
    return out


def switch_face(states, silence_verdict, threshold_min):
    """Does the silence have a switch behind it?  Pure, so the selftest drives this."""
    states = states or {}
    disabled = [n for n, s in states.items() if s == "Disabled"]
    absent = [n for n, s in states.items() if s == ABSENT]
    known = [n for n, s in states.items() if s in TASK_STATES]
    quiet = silence_verdict in ("OPEN_SILENCE", "SILENT_GAP")
    if disabled and quiet:
        verdict = "LANE_SWITCHED_OFF"
        why = ("%d of the lane's own task(s) are Disabled while the round line is silent "
               "(%s); a switched-off lane is not a slow one, and re-enabling it is the "
               "whole fix" % (len(disabled), ", ".join(disabled)))
    elif disabled:
        verdict = "LANE_SWITCHED_OFF_IDLE"
        why = ("task(s) Disabled (%s) but no silence in this window -- the line stopped "
               "after the last round" % ", ".join(disabled))
    elif absent:
        # r1217: a declared ignition face that does not exist is red whether or not the
        # line happens to be quiet -- an absent task can never ring, so the next quiet
        # window is not idle, it is a dead lane that has not been noticed yet.
        verdict = "LANE_TASK_MISSING"
        why = ("%d declared lane task(s) are not registered at all (%s); an absent "
               "ignition face cannot be quiet, it can only be dead"
               % (len(absent), ", ".join(absent)))
    elif known:
        verdict = "LANE_ENABLED"
        why = "every probeable lane task is switched on; the silence (if any) is not a switch"
    else:
        verdict = "UNKNOWN"
        why = "the scheduler could not be read; an unread switch is neither on nor off"
    return {"states": states, "disabled": disabled, "absent": absent,
            "probeable": len(known), "threshold_min": threshold_min,
            "verdict": verdict, "why": why}


def _enable_task(name):
    """schtasks /change /enable -> (ok, detail).  Zero window: no console may flash."""
    import subprocess
    kw = {}
    if os.name == "nt":
        kw["creationflags"] = 0x08000000
    try:
        p = subprocess.run(["schtasks", "/change", "/tn", name, "/enable"],
                           capture_output=True, text=True, timeout=60, **kw)
    except Exception as e:                                          # noqa: BLE001
        return False, "enable raised: %s" % e
    if p.returncode != 0:
        return False, ("schtasks rc=%d: %s" % (p.returncode,
                                               (p.stderr or p.stdout or "").strip()[:200]))
    return True, ""


REGISTER_HINT = "Tools/register_satengine_task.ps1"   # absent engine task: re-register


def heal_lane_tasks(states, names=None, enabler=None, rechecker=None):
    """Turn the lane's switches back on, then READ THEM BACK.

    Only Disabled tasks are healed: re-enabling is a state change with no definition
    written.  An Absent task is never fabricated here (a task definition is an owner
    decision -- the register script does that), and an UNKNOWN state is not touched.
    Write-then-readback law: a heal is only reported as healed if the second probe
    agrees, otherwise it is reported as attempted-failed with the reason.
    """
    enabler = enabler or _enable_task
    states = states or {}
    acts = []
    for n, st in sorted(states.items()):
        if st == "Disabled":
            ok, detail = enabler(n)
            acts.append({"task": n, "action": "enabled" if ok else "enable_failed",
                         "detail": detail})
        elif st == ABSENT:
            acts.append({"task": n, "action": "absent_not_fabricated",
                         "detail": "register it explicitly: %s" % REGISTER_HINT})
        elif st == "UNKNOWN":
            acts.append({"task": n, "action": "unread_not_touched",
                         "detail": "the scheduler did not answer; not a switch we may flip"})
    healed = [a["task"] for a in acts if a["action"] == "enabled"]
    after = {}
    if healed:
        probe = rechecker or read_task_states
        try:
            after = probe(healed) or {}
        except Exception:                                           # noqa: BLE001
            after = {}
        for a in acts:
            if a["action"] != "enabled":
                continue
            now = after.get(a["task"])
            if now in ("Ready", "Running"):
                a["verified"] = True
            else:
                a["verified"] = False
                a["action"] = "enable_unverified"
                a["detail"] = "readback says %s, not Ready/Running" % (now or "no answer")
    return {"acts": acts, "healed": [a["task"] for a in acts
                                     if a.get("verified") is True],
            "readback": after}


def run(days=DEFAULT_WINDOW_DAYS, threshold_min=DEFAULT_THRESHOLD_MIN, mid=None,
        heal=False):
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
    # r1216b: ask the scheduler whether the lane is off.  A measured silence verdict
    # stays as measured; a switched-off task replaces it (the more specific cause).
    res["silence_verdict"] = res["verdict"]
    names = LANE_TASKS.get(mid) or []
    res["lane_tasks"] = switch_face(read_task_states(names),
                                    res["silence_verdict"], threshold_min)
    # r1217: --heal flips only Disabled switches, then reads them back.  The switch face
    # is rebuilt from the readback, so a "healed" line can never be printed from intent.
    if heal:
        before = list(res["lane_tasks"].get("disabled") or [])
        heal_block = heal_lane_tasks(res["lane_tasks"]["states"], names)
        res["lane_tasks"] = switch_face(read_task_states(names),
                                        res["silence_verdict"], threshold_min)
        res["lane_tasks"]["heal"] = heal_block
        res["lane_tasks"]["disabled_before_heal"] = before
    if res["lane_tasks"]["verdict"] == "LANE_SWITCHED_OFF":
        res["verdict"] = "LANE_SWITCHED_OFF"
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
    lt = res.get("lane_tasks") or {}
    print("  lane tasks: %s -> %s"
          % (", ".join("%s=%s" % (k, v) for k, v in sorted(lt.get("states", {}).items()))
             or "(none declared for this machine)", lt.get("verdict")))
    if str(lt.get("verdict") or "").startswith("LANE_SWITCHED_OFF"):
        print("  WHY: %s" % lt.get("why"))
    elif lt.get("verdict") == "LANE_TASK_MISSING":
        print("  WHY: %s" % lt.get("why"))
    hb = lt.get("heal") or {}
    if hb:
        for a in hb.get("acts") or []:
            print("  HEAL %s: %s%s"
                  % (a.get("task"), a.get("action"),
                     ("" if not a.get("detail") else " (%s)" % a.get("detail"))))
        print("  HEAL readback: healed=%s"
              % (", ".join(hb.get("healed") or []) or "(none)"))
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
    # L13 the sentence is generated from the numbers and names the open gap
    res = audit([(_dt.datetime(2026, 11, 1, 7, 0),) * 2 + (0,),
                 (_dt.datetime(2026, 11, 1, 7, 10),) * 2 + (0,)],
                90, 3, now=_dt.datetime(2026, 11, 1, 11, 40), mid="bm-a")
    res["machine"] = "bm-a"
    s = sentence(res)
    chk("L13-sentence", isinstance(s, str) and s.endswith(".")
        and "OPEN_SILENCE" not in s and "still open since 2026-11-01T07:10" in s,
        str(s))
    # L14 a face without a verdict has no sentence, and the reader refuses it
    chk("L14-no-verdict", sentence({"machine": "bm-a"}) is None
        and read_published("bm-a", root="/nonexistent")["present"] is False,
        "verdict-less face produced a sentence")
    # L15 the reader quotes the published artifact (never a fresh derivation)
    import tempfile
    tmp = tempfile.mkdtemp()
    os.makedirs(os.path.join(tmp, "results"))
    doc = {"machine": "bm-a", "verdict": "SILENT_GAP", "threshold_min": 90,
           "window_days": 3, "median_gap_min": 10.0, "rounds_in_window": 5,
           "gaps_over_threshold_count": 1,
           "longest_silence": {"from": "2026-11-01T01:00", "to": "2026-11-01T03:00",
                               "gap_low_min": 111.0, "gap_high_min": 129.0,
                               "quiet_window_min": 0.0}}
    with io.open(os.path.join(tmp, "results", "lane_silence.bm-a.json"), "w",
                 encoding="utf-8") as fh:
        json.dump(doc, fh)
    pub = read_published("bm-a", root=tmp)
    chk("L15-reader", pub["present"] is True and pub["verdict"] == "SILENT_GAP"
        and "111.0-129.0 min" in (pub["sentence"] or ""),
        str(pub.get("sentence")))
    # L16-L21 (r1216b): the switch behind the silence.  A Disabled task while the line
    # is silent is named as the cause; a task that cannot be read is never called
    # either on or off, and the probe normalises whatever the scheduler prints.
    _sw_dis = switch_face({"Bigmoney-IterationLoop": "Disabled",
                           "Bigmoney-LoopWatchdog": "Ready"}, "OPEN_SILENCE", 90)
    chk("L16-switched-off", _sw_dis["verdict"] == "LANE_SWITCHED_OFF"
        and _sw_dis["disabled"] == ["Bigmoney-IterationLoop"], str(_sw_dis))
    _sw_unk = switch_face({"Bigmoney-IterationLoop": "UNKNOWN"}, "OPEN_SILENCE", 90)
    _sw_none = switch_face({}, "OPEN_SILENCE", 90)
    chk("L17-unknown-never-off", _sw_unk["verdict"] == "UNKNOWN"
        and _sw_none["verdict"] == "UNKNOWN", "%s/%s" % (_sw_unk, _sw_none))
    _sw_on = switch_face({"Bigmoney-IterationLoop": "Ready"}, "SILENT_GAP", 90)
    chk("L18-enabled-is-not-blamed", _sw_on["verdict"] == "LANE_ENABLED"
        and not _sw_on["disabled"], str(_sw_on))
    _sw_idle = switch_face({"Bigmoney-IterationLoop": "Disabled"}, "OK", 90)
    chk("L19-off-but-no-silence", _sw_idle["verdict"] == "LANE_SWITCHED_OFF_IDLE",
        str(_sw_idle))
    _probe = read_task_states(["A", "B"], runner=lambda names: {"A": "Ready",
                                                               "B": "Exploded"})
    chk("L20-probe-normalises", _probe == {"A": "Ready", "B": "UNKNOWN"}, str(_probe))
    def _boom(names):
        raise RuntimeError("boom")
    _probe2 = read_task_states(["A"], runner=_boom)
    chk("L21-probe-failure-is-unknown", _probe2 == {"A": "UNKNOWN"}, str(_probe2))
    # L22-L27 (r1217): absence is not "on" and not "unreadable"; a heal must be read back.
    _probe3 = read_task_states(["A", "B"], runner=lambda names: {"A": "Ready"})
    chk("L22-absent-named", _probe3 == {"A": "Ready", "B": ABSENT}, str(_probe3))
    _sw_miss = switch_face({"Bigmoney-SatEngine-bm-b": ABSENT,
                            "Bigmoney-IterationLoop": "Ready"}, "OK", 90)
    chk("L23-absent-is-red-even-when-quiet",
        _sw_miss["verdict"] == "LANE_TASK_MISSING"
        and _sw_miss["absent"] == ["Bigmoney-SatEngine-bm-b"], str(_sw_miss))
    _sw_dis_miss = switch_face({"A": "Disabled", "B": ABSENT}, "OPEN_SILENCE", 90)
    chk("L24-switched-off-outranks-missing",
        _sw_dis_miss["verdict"] == "LANE_SWITCHED_OFF", str(_sw_dis_miss))
    _sw_unk_absent = switch_face({"A": "UNKNOWN", "B": ABSENT}, "OK", 90)
    chk("L25-one-absent-still-named", _sw_unk_absent["verdict"] == "LANE_TASK_MISSING",
        str(_sw_unk_absent))
    _calls = []
    _heal = heal_lane_tasks(
        {"A": "Disabled", "B": ABSENT, "C": "UNKNOWN"},
        enabler=lambda n: (_calls.append(n), (True, ""))[1],
        rechecker=lambda names: {"A": "Ready"})
    chk("L26-heal-touches-only-disabled",
        _calls == ["A"] and _heal["healed"] == ["A"]
        and [a["action"] for a in _heal["acts"] if a["task"] == "B"] == ["absent_not_fabricated"]
        and [a["action"] for a in _heal["acts"] if a["task"] == "C"] == ["unread_not_touched"],
        "%s / %s" % (_calls, _heal["acts"]))
    _heal2 = heal_lane_tasks({"A": "Disabled"}, enabler=lambda n: (True, ""),
                             rechecker=lambda names: {"A": "Disabled"})
    chk("L27-heal-needs-its-readback",
        _heal2["healed"] == [] and _heal2["acts"][0]["action"] == "enable_unverified",
        str(_heal2))
    chk("L28-engine-in-every-lane-registry",
        all("Bigmoney-SatEngine-bm-b" in (LANE_TASKS.get(m) or [])
            for m in ("bm-a", "bm-b", "bm-c")), str(LANE_TASKS))
    if fails:
        print("selftest FAIL %d/28" % len(fails))
        for f in fails:
            print("  " + f)
        return 1
    print("selftest 28/28 PASS")
    return 0


# --------------------------------- reader (r1206 bm-a)
def sentence(res):
    """One sentence, generated from the numbers, never hand-written.

    Consumers print THIS so a report and a page cannot drift into two
    statements about the same ledger (r1290).  A face without a verdict
    yields None -- the caller must say "unreadable", not print a blank.
    """
    if not isinstance(res, dict) or not res.get("verdict"):
        return None
    bits = ["%s: %d rounds in %sd, median gap %s min, %d unexplained gap(s) "
            "over %s min"
            % (res.get("machine"), res.get("rounds_in_window") or 0,
               res.get("window_days"), res.get("median_gap_min"),
               res.get("gaps_over_threshold_count") or 0, res.get("threshold_min"))]
    long = res.get("longest_silence") or {}
    if long:
        bits.append("longest silence %s -> %s (%s-%s min, %s explained by its "
                    "quiet window)"
                    % (long.get("from"), long.get("to"), long.get("gap_low_min"),
                       long.get("gap_high_min"), long.get("quiet_window_min")))
    og = res.get("open_gap") or {}
    if og:
        bits.append("still open since %s (%s-%s min unexplained)"
                    % (og.get("since"), og.get("unexplained_low_min"),
                       og.get("unexplained_high_min")))
    lt = res.get("lane_tasks") or {}
    if lt.get("verdict") == "LANE_SWITCHED_OFF":
        bits.append("the lane task itself is Disabled (%s), so the silence is a switch, "
                    "not a slow round" % ", ".join(lt.get("disabled") or []))
    elif lt.get("verdict") == "UNKNOWN":
        bits.append("the scheduler could not be read, so whether the lane is switched "
                    "off is unknown")
    return "; ".join(bits) + "."


def read_published(mid=None, root=None):
    """Single reader for every consumer (daily_report, the CEO page).

    Reads the published artifact only.  Absent / unreadable / verdict-less all
    come back as present=False with a note -- a missing face must never read
    as "the line was fine".
    """
    root = root or ROOT
    mid = mid or _machine_id()
    if not mid:
        return {"present": False, "note": "machine identity unreadable "
                                          "(fleet/machine.json)"}
    path = os.path.join(root, "results", "lane_silence.%s.json" % mid)
    try:
        with io.open(path, encoding="utf-8") as fh:
            res = json.load(fh)
    except FileNotFoundError:
        return {"present": False, "machine": mid,
                "note": "no lane_silence face for %s yet" % mid}
    except Exception as exc:                                        # noqa: BLE001
        return {"present": False, "machine": mid,
                "note": "lane_silence face unreadable: %s" % str(exc)[:120]}
    if not isinstance(res, dict) or not res.get("verdict"):
        return {"present": False, "machine": mid,
                "note": "lane_silence face carries no verdict"}
    return {"present": True,
            "machine": res.get("machine"),
            "verdict": res.get("verdict"),
            "threshold_min": res.get("threshold_min"),
            "window_days": res.get("window_days"),
            "median_gap_min": res.get("median_gap_min"),
            "rounds_in_window": res.get("rounds_in_window"),
            "rounds_in_ledger": res.get("rounds_in_ledger"),
            "gaps_over_threshold_count": res.get("gaps_over_threshold_count"),
            "longest_silence": res.get("longest_silence"),
            "open_gap": res.get("open_gap"),
            "gaps_over_threshold": res.get("gaps_over_threshold") or [],
            "evidence_cutoff": res.get("evidence_cutoff"),
            "generated": res.get("generated"),
            "silence_verdict": res.get("silence_verdict") or (
                res.get("verdict") if res.get("lane_tasks") is None else None),
            "lane_tasks": res.get("lane_tasks"),
            "sentence": sentence(res)}



def main(argv):
    if len(argv) > 1 and argv[1] in ("selftest", "--selftest"):
        return selftest()
    days, thr, mid = DEFAULT_WINDOW_DAYS, DEFAULT_THRESHOLD_MIN, None
    heal = False
    it = iter(argv[1:])
    for a in it:
        if a == "--days":
            days = int(next(it))
        elif a == "--threshold-min":
            thr = int(next(it))
        elif a == "--machine":
            mid = next(it)
        elif a == "--heal":
            heal = True
    return run(days, thr, mid, heal)


if __name__ == "__main__":
    sys.exit(main(sys.argv))