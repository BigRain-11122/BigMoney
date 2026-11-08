# -*- coding: utf-8 -*-
"""E577 -- what actually happened inside the gaps that E576 published as "beyond the tolerance".

E576 (r1604 bm-b) found 31 chain executions whose first following round row of any machine sits
more than 6h later, and stopped at the distance.  A distance is not an explanation: the same
number covers an overnight batch nobody wrote down, a session that hung, and the ordinary pause
between one round's last row and the next round's first row.  This study asks, per gap:

  span                  the gap in hours, the hour of day it starts and ends, and whether it
                        crosses midnight (the "is this overnight work" question)
  receipts              how many S6 chain receipts on disk carry an internal ts inside the gap
  heartbeat             how many commits touched that machine's heartbeat face inside the gap
  boundary              whether the gap ends at the FIRST row of a round, i.e. it is the pause
                        between rounds rather than work that ran without a row

Classes (first match wins, witness published with every row):

  the_pause_between_two_rounds        ends at the first row of a round and nothing on disk ran
                                      inside it (no receipt, no heartbeat commit)
  work_ran_and_left_a_trace           a receipt or a heartbeat commit sits inside the gap
  a_gap_that_ends_mid_round           the closing row is not its round's first row
  nothing_identifiable_in_the_gap     none of the above, published as unidentified rather than
                                      as empty

Bounds published, not claimed: receipts are read from this host's disk, so a receipt gitignored
and never committed is invisible here (E574's 187 vanishing runs are exactly that population)
and a gap that shows no trace is therefore "no trace on disk", never "nothing ran".
Heartbeat history is read from git commits touching fleet/machines/<machine>.json, not from the
live face, and a round that wrote its heartbeat inside the same commit as its rows cannot be
separated from it.

Usage: python scripts/e577_night_gap.py [build|check|verify|selftest]
"""
import glob
import importlib.util
import io
import json
import os
import re
import subprocess
import sys
from datetime import datetime, timedelta

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
OUTDIR = os.path.join(ROOT, "results", "state_tilt")
CUTOFF = "2026-11-08"
LATE = "only_a_row_beyond_the_tolerance_follows"

C_PARSE = "a_row_the_index_cannot_read_closes_this_gap"
C_PAUSE = "the_pause_between_two_rounds"
C_TRACE = "work_ran_and_left_a_trace"
C_MID = "a_gap_that_ends_mid_round"
C_UNKNOWN = "nothing_identifiable_in_the_gap"
CLASSES = (C_PARSE, C_PAUSE, C_TRACE, C_MID, C_UNKNOWN)

# E573's ROW_TS requires the row to start with "|".  A row printed without that leading pipe is
# a row of the same shape whose own round never enters the index, so every consumer of the index
# silently loses it.  This study reads both forms and publishes the difference as a class.
ROW_ANY = re.compile(r"^\|?\s*(\d{4}-\d{2}-\d{2})T(\d{2}):(\d{2})(?::(\d{2}))?")
ROUND_ANY = re.compile(r"\br(\d{1,4})(?!\d)", re.I)
STRICT_TOL_HOURS = 6.0

MACHINE_FILE = {"a": "bm-a", "b": "bm-b", "c": "bm-c"}


def _read_json(path):
    with io.open(path, encoding="utf-8") as fh:
        return json.load(fh)


def _mod(name, filename):
    path = os.path.join(HERE, filename)
    spec = importlib.util.spec_from_file_location(name, path)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def _parse(ts):
    for fmt in ("%Y-%m-%dT%H:%M:%S", "%Y-%m-%d %H:%M:%S"):
        try:
            return datetime.strptime(ts, fmt)
        except (TypeError, ValueError):
            continue
    return None


def receipt_times(rows=None):
    """(receipt ts, path) for every S6 chain receipt on disk that prints its own ts.

    mtime is deliberately unused: this tree's mtimes are checkout times (E453), so only the ts
    the receipt itself carries can place a receipt inside a wall-clock gap.
    """
    out, unparsed = [], 0
    for path in sorted(glob.glob(os.path.join(ROOT, "results", "_r*s6_chain*.json"))):
        try:
            face = _read_json(path)
        except Exception:
            unparsed += 1
            continue
        ts = _parse(face.get("ts")) if isinstance(face, dict) else None
        if ts is None:
            unparsed += 1
            continue
        rnd = str(face.get("round") or "").strip() or None
        out.append((ts, os.path.relpath(path, ROOT).replace("\\", "/"), rnd))
    out.sort()
    return out, unparsed


def heartbeat_commits(machine_id):
    """Commit timestamps touching that machine's heartbeat face -- the only history it has."""
    try:
        raw = subprocess.check_output(
            ["git", "-C", ROOT, "log", "--format=%ad", "--date=format:%Y-%m-%dT%H:%M:%S",
             "--", "fleet/machines/%s.json" % machine_id],
            stderr=subprocess.DEVNULL).decode("utf-8", "replace")
    except Exception:
        return None
    out = []
    for line in raw.splitlines():
        ts = _parse(line.strip())
        if ts:
            out.append(ts)
    return sorted(out)


def lenient_index(e573, reports):
    """Every round row on those report files, read with or without a leading pipe.

    Returns (rows, no_pipe_count) where a row is the same shape e575.round_index publishes, so
    the two indexes differ in exactly one respect: which lines they can see.
    """
    rows, no_pipe = [], 0
    for report in reports:
        machine = _machine_of(report)
        for i, line in enumerate(e573.lines_of(report) or []):
            m = ROW_ANY.match(line or "")
            if not m:
                continue
            parts = [x.strip() for x in (line or "").split("|")]
            has_pipe = (line or "").lstrip().startswith("|")
            # a pipe row puts the timestamp in parts[1] and the round token in parts[2]; a row
            # printed without the leading pipe puts them one slot earlier
            tok = None
            for slot in ((2, 3) if has_pipe else (1, 2)):
                if slot < len(parts) and ROUND_ANY.search(parts[slot]):
                    tok = ROUND_ANY.search(parts[slot])
                    break
            if tok is None:
                continue
            try:
                ts = datetime.strptime("%sT%s:%s:%s" % (m.group(1), m.group(2), m.group(3),
                                                        m.group(4) or "00"),
                                       "%Y-%m-%dT%H:%M:%S")
            except ValueError:
                continue
            if not has_pipe:
                no_pipe += 1
            rows.append({"report": report, "line": i + 1, "round": int(tok.group(1)),
                         "ts": ts, "machine": machine, "leading_pipe": has_pipe})
    rows.sort(key=lambda r: r["ts"])
    return rows, no_pipe


def _machine_of(report):
    if "bm-a" in report:
        return "a"
    if "bm-c" in report:
        return "c"
    return "b"


def next_row_any(rows, ts):
    cands = [r for r in rows if r.get("ts") and r["ts"] >= ts]
    return min(cands, key=lambda r: r["ts"]) if cands else None


def gap_facts(row, first_row_of_round, prev_same_machine, receipts, beats, row_rounds=None,
              lenient_rows=None):
    start = _parse(row.get("ts"))
    nxt = row.get("next_row_any_machine") or {}
    end = _parse(nxt.get("ts"))
    hours = round((end - start).total_seconds() / 3600.0, 2) if end else None
    inside = [(ts, p, r) for ts, p, r in receipts if end and start <= ts <= end]
    beat_inside = [b for b in (beats or []) if end and start <= b <= end]
    rounds_inside = sorted({r for _, _, r in inside if r})
    seen = row_rounds or set()
    ends_at_first_row = bool(first_row_of_round)
    lenient_next = next_row_any(lenient_rows, start) if (lenient_rows and start) else None
    lenient_minutes = (round((lenient_next["ts"] - start).total_seconds() / 60.0, 1)
                       if lenient_next else None)
    own_lenient = next_row_any([r for r in (lenient_rows or [])
                                if r.get("machine") == row.get("machine")], start) \
        if (lenient_rows and start) else None
    own_minutes = (round((own_lenient["ts"] - start).total_seconds() / 60.0, 1)
                   if own_lenient else None)
    facts = {
        "ts": row.get("ts"),
        "date": row.get("date"),
        "hour": row.get("hour"),
        "machine": row.get("machine"),
        "line": row.get("line"),
        "gap_end_ts": nxt.get("ts"),
        "gap_end_round": nxt.get("round"),
        "gap_hours": hours,
        "hour_of_day_span": [start.hour if start else None, end.hour if end else None],
        "crosses_midnight": bool(start and end and end.date() > start.date()),
        "previous_row_same_machine_minutes": prev_same_machine,
        "receipts_inside": len(inside),
        "receipt_names": [p for _, p, _ in inside][:5],
        "receipt_rounds_inside": rounds_inside,
        "receipt_rounds_whose_row_exists": [r for r in rounds_inside if r in seen],
        "receipt_rounds_with_no_row_anywhere": [r for r in rounds_inside if r not in seen],
        "heartbeat_commits_inside": len(beat_inside)
        if beats is not None else None,
        "gap_ends_at_first_row_of_round": ends_at_first_row,
        "heartbeat_history_available": beats is not None,
        "next_row_under_the_lenient_index_minutes": lenient_minutes,
        "next_row_under_the_lenient_index_round": lenient_next["round"] if lenient_next else None,
        "next_row_under_the_lenient_index_has_leading_pipe": (
            lenient_next["leading_pipe"] if lenient_next else None),
        "closes_inside_the_tolerance_under_the_lenient_index": bool(
            lenient_minutes is not None and lenient_minutes / 60.0 <= STRICT_TOL_HOURS),
        "own_machine_row_under_the_lenient_index_minutes": own_minutes,
        "attributed_by_its_own_machine_under_the_lenient_index": bool(
            own_minutes is not None and own_minutes / 60.0 <= STRICT_TOL_HOURS),
    }
    if facts["attributed_by_its_own_machine_under_the_lenient_index"]:
        facts["class"] = C_PARSE
        facts["decided_by"] = ("round %s of %s prints a row %.1f min later that the strict "
                              "index cannot read (leading pipe=%s)"
                              % (own_lenient["round"], own_lenient["machine"], own_minutes,
                                 own_lenient["leading_pipe"]))
        return facts
    if ends_at_first_row and not inside and beats is None:
        facts["class"] = C_UNKNOWN
        facts["decided_by"] = ("the gap closes on the first row of round %s with no receipt inside "
                              "and an unreadable heartbeat history, so silence is not identifiable"
                              % nxt.get("round"))
    elif ends_at_first_row and not inside and not beat_inside:
        facts["class"] = C_PAUSE
        facts["decided_by"] = ("the gap closes on the first row of round %s and no receipt or "
                              "heartbeat commit on disk falls inside it" % nxt.get("round"))
    elif inside or beat_inside:
        facts["class"] = C_TRACE
        facts["decided_by"] = ("%d receipt(s) and %d heartbeat commit(s) carry a timestamp "
                              "inside the gap" % (len(inside), len(beat_inside)))
    elif not ends_at_first_row:
        facts["class"] = C_MID
        facts["decided_by"] = ("the closing row is not the first row of round %s, so the gap "
                              "ends in the middle of a round's reporting" % nxt.get("round"))
    else:
        facts["class"] = C_UNKNOWN
        facts["decided_by"] = ("the gap closes on the first row of a round but the heartbeat "
                              "history could not be read, so silence is not identifiable")
    return facts


def build(write=True):
    e576 = _mod("e576_gap_calls", "e576_gap_calls.py")
    e575 = e576._e575()
    e573 = e575._e573()

    face576 = e576.build(write=False)
    late = [r for r in face576["rows"] if r.get("class") == LATE]

    rows_index = e575.round_index(e573)
    first_line = {}
    for r in rows_index:
        if not r.get("ts"):
            continue
        key = (r["report"], r["round"])
        first_line[key] = min(first_line.get(key, r["line"]), r["line"])

    receipts, unparsed = receipt_times()
    beats = {m: heartbeat_commits(mid) for m, mid in MACHINE_FILE.items()}
    strict_rounds = {str(r["round"]) for r in rows_index if r.get("round") is not None}
    lenient_rows, no_pipe = lenient_index(e573, e575.REPORTS)
    row_rounds = strict_rounds | {str(r["round"]) for r in lenient_rows}

    out_rows = []
    for r in late:
        nxt = r.get("next_row_any_machine") or {}
        key = (nxt.get("report"), nxt.get("round"))
        is_first = bool(nxt) and first_line.get(key) == nxt.get("line")
        machine = r.get("machine")
        start = _parse(r.get("ts"))
        prev = [x for x in rows_index
                if x.get("machine") == machine and x.get("ts") and start and x["ts"] <= start]
        prev_minutes = (round((start - max(x["ts"] for x in prev)).total_seconds() / 60.0, 1)
                        if prev else None)
        out_rows.append(gap_facts(r, is_first, prev_minutes, receipts,
                                  beats.get(machine), row_rounds, lenient_rows))
    out_rows.sort(key=lambda x: x["ts"])

    by_class = {k: sum(1 for x in out_rows if x["class"] == k) for k in CLASSES}
    hours = {}
    for x in out_rows:
        hours[str(x["hour"])] = hours.get(str(x["hour"]), 0) + 1
    spans = [x["gap_hours"] for x in out_rows if x["gap_hours"] is not None]
    summary = {
        "rows": len(out_rows),
        "by_class": by_class,
        "by_start_hour": hours,
        "hours_hit": len(hours),
        "crosses_midnight": sum(1 for x in out_rows if x["crosses_midnight"]),
        "gap_hours_min": min(spans) if spans else None,
        "gap_hours_max": max(spans) if spans else None,
        "gap_hours_median": (sorted(spans)[len(spans) // 2] if spans else None),
        "receipts_on_disk": len(receipts),
        "receipts_without_a_parsable_ts": unparsed,
        "rows_with_a_receipt_inside": sum(1 for x in out_rows if x["receipts_inside"]),
        "receipt_rounds_named_inside_gaps": len({r for x in out_rows
                                                 for r in x["receipt_rounds_inside"]}),
        "receipt_rounds_with_no_row_anywhere": sorted(
            {r for x in out_rows for r in x["receipt_rounds_with_no_row_anywhere"]}),
        "rows_whose_receipts_all_have_a_row": sum(
            1 for x in out_rows if x["receipt_rounds_inside"]
            and not x["receipt_rounds_with_no_row_anywhere"]),
        "rows_ending_at_the_first_row_of_a_round": sum(
            1 for x in out_rows if x["gap_ends_at_first_row_of_round"]),
        "rows_closed_inside_the_tolerance_by_a_row_the_strict_index_cannot_read": sum(
            1 for x in out_rows
            if x["closes_inside_the_tolerance_under_the_lenient_index"]),
        "rows_attributed_by_their_own_machine_under_the_lenient_index": sum(
            1 for x in out_rows
            if x["attributed_by_its_own_machine_under_the_lenient_index"]),
        "strict_rows_indexed": len([r for r in rows_index if r.get("ts")]),
        "lenient_rows_indexed": len(lenient_rows),
        "rows_without_a_leading_pipe": no_pipe,
        "row_form_rule": ("E573's ROW_TS requires a leading pipe; this study also reads the same "
                          "row shape without one and publishes the difference as its own class"),
        "rows_with_a_heartbeat_commit_inside": sum(
            1 for x in out_rows if (x["heartbeat_commits_inside"] or 0) > 0),
        "rows_whose_heartbeat_history_is_unreadable": sum(
            1 for x in out_rows if not x["heartbeat_history_available"]),
        "e576_late_rows_again": len(late),
        "population_agrees_with_e576": len(late) == len(
            [r for r in face576["rows"] if r.get("class") == LATE]),
        "receipt_clock": "the ts the receipt prints, never mtime (E453: mtimes are checkouts)",
        "bound": ("a receipt gitignored and never committed is invisible here (E574: 187 such "
                  "runs), so an empty gap is 'no trace on disk', never 'nothing ran'"),
    }
    out = {
        "study": "E577_night_gap",
        "card": "E577",
        "dept": "research",
        "machine": "bm-b",
        "evidence_cutoff": CUTOFF,
        "population": ("the %d executions E576 classed %s, re-derived live from E576's own "
                       "build" % (len(late), LATE)),
        "rule": ("ends at a round's first row with no trace -> the pause between rounds; any "
                 "receipt or heartbeat commit inside -> work ran and left a trace; ends "
                 "mid-round -> a gap that ends mid-round; else unidentified"),
        "summary": summary,
        "verdict": _verdict(summary),
        "verdict_line": _verdict_line(summary),
        "rows": out_rows,
    }
    if write:
        if not os.path.isdir(OUTDIR):
            os.makedirs(OUTDIR)
        for path in (os.path.join(OUTDIR, "NIGHTGAP-%s.json" % CUTOFF),
                     os.path.join(OUTDIR, "nightgap_latest.json")):
            with io.open(path, "w", encoding="utf-8", newline="\n") as fh:
                json.dump(out, fh, ensure_ascii=False, indent=1, sort_keys=True)
    return out


def _verdict(s):
    by = s.get("by_class") or {}
    n = s.get("rows") or 0
    if not n:
        return "no_gap_to_explain"
    if by.get(C_PARSE, 0) == n:
        return "every_gap_is_closed_by_a_row_the_strict_index_cannot_read"
    if by.get(C_PAUSE, 0) == n:
        return "every_gap_is_the_pause_between_two_rounds_and_no_work_left_a_trace"
    if by.get(C_TRACE, 0) == n:
        return "every_gap_contains_work_that_left_a_trace"
    parts = []
    if by.get(C_PARSE):
        parts.append("%d_closed_by_a_row_the_index_cannot_read" % by[C_PARSE])
    if by.get(C_PAUSE):
        parts.append("%d_pause_between_rounds" % by[C_PAUSE])
    if by.get(C_TRACE):
        parts.append("%d_with_a_trace_inside" % by[C_TRACE])
    if by.get(C_MID):
        parts.append("%d_ending_mid_round" % by[C_MID])
    if by.get(C_UNKNOWN):
        parts.append("%d_unidentified" % by[C_UNKNOWN])
    return "the_gaps_split_%d_ways: %s" % (sum(1 for k in CLASSES if by.get(k)),
                                           " + ".join(parts))


def _verdict_line(s):
    by = s.get("by_class") or {}
    return ("gaps=%d unreadable_row_closes=%d pause=%d with_trace=%d mid_round=%d unidentified=%d "
            "| overnight=%d hours_hit=%d gap_h_min=%s gap_h_median=%s gap_h_max=%s "
            "| strict_rows=%d lenient_rows=%d no_leading_pipe=%d "
            "| receipts=%d unparsable=%d rows_with_receipt=%d rows_with_heartbeat_commit=%d "
            "receipt_rounds=%d with_no_row_anywhere=%d | e576_again=%d agree=%s"
            % (s.get("rows", 0),
               s.get("rows_closed_inside_the_tolerance_by_a_row_the_strict_index_cannot_read", 0),
               by.get(C_PAUSE, 0), by.get(C_TRACE, 0), by.get(C_MID, 0),
               by.get(C_UNKNOWN, 0), s.get("crosses_midnight", 0), s.get("hours_hit", 0),
               s.get("gap_hours_min"), s.get("gap_hours_median"), s.get("gap_hours_max"),
               s.get("strict_rows_indexed", 0), s.get("lenient_rows_indexed", 0),
               s.get("rows_without_a_leading_pipe", 0),
               s.get("receipts_on_disk", 0), s.get("receipts_without_a_parsable_ts", 0),
               s.get("rows_with_a_receipt_inside", 0),
               s.get("rows_with_a_heartbeat_commit_inside", 0),
               s.get("receipt_rounds_named_inside_gaps", 0),
               len(s.get("receipt_rounds_with_no_row_anywhere") or []),
               s.get("e576_late_rows_again", 0), s.get("population_agrees_with_e576")))


def face_problems(face):
    problems = []
    rows = face.get("rows") or []
    s = face.get("summary") or {}
    if face.get("verdict") != _verdict(s):
        problems.append("the verdict does not re-derive from the summary")
    if face.get("verdict_line") != _verdict_line(s):
        problems.append("the verdict line does not re-derive from the summary")
    if s.get("rows") != len(rows):
        problems.append("summary.rows does not equal the rows")
    counts = {k: sum(1 for r in rows if r.get("class") == k) for k in CLASSES}
    for k, v in counts.items():
        if (s.get("by_class") or {}).get(k) != v:
            problems.append("by_class.%s does not re-derive from the rows" % k)
    hist = {}
    for r in rows:
        if r.get("hour") is None:
            continue
        hist[str(r["hour"])] = hist.get(str(r["hour"]), 0) + 1
    if s.get("by_start_hour") != hist:
        problems.append("by_start_hour does not re-derive from the rows")
    if s.get("hours_hit") != len(hist):
        problems.append("hours_hit does not equal the start-hour histogram")
    if s.get("crosses_midnight") != sum(1 for r in rows if r.get("crosses_midnight")):
        problems.append("crosses_midnight does not re-derive from the rows")
    if s.get("rows_with_a_receipt_inside") != sum(1 for r in rows if r.get("receipts_inside")):
        problems.append("rows_with_a_receipt_inside does not re-derive from the rows")
    if s.get("receipt_rounds_named_inside_gaps") != len(
            {r for x in rows for r in (x.get("receipt_rounds_inside") or [])}):
        problems.append("receipt_rounds_named_inside_gaps does not re-derive")
    if sorted(s.get("receipt_rounds_with_no_row_anywhere") or []) != sorted(
            {r for x in rows for r in (x.get("receipt_rounds_with_no_row_anywhere") or [])}):
        problems.append("receipt_rounds_with_no_row_anywhere does not re-derive")
    if any(set((x.get("receipt_rounds_inside") or []))
           != set((x.get("receipt_rounds_whose_row_exists") or []))
           | set((x.get("receipt_rounds_with_no_row_anywhere") or [])) for x in rows):
        problems.append("a row's receipt rounds are not split into seen and unseen")
    if s.get("rows_ending_at_the_first_row_of_a_round") != sum(
            1 for r in rows if r.get("gap_ends_at_first_row_of_round")):
        problems.append("rows_ending_at_the_first_row_of_a_round does not re-derive")
    if s.get("rows_closed_inside_the_tolerance_by_a_row_the_strict_index_cannot_read") != sum(
            1 for r in rows if r.get("closes_inside_the_tolerance_under_the_lenient_index")):
        problems.append("the unreadable-row count does not re-derive from the rows")
    if s.get("rows_attributed_by_their_own_machine_under_the_lenient_index") != sum(
            1 for r in rows if r.get("attributed_by_its_own_machine_under_the_lenient_index")):
        problems.append("the own-machine attribution count does not re-derive from the rows")
    if s.get("rows_without_a_leading_pipe") is not None and \
            s.get("lenient_rows_indexed", 0) < s.get("strict_rows_indexed", 0):
        problems.append("the lenient index is smaller than the strict one")
    for r in rows:
        if r.get("class") == C_PARSE and not r.get(
                "attributed_by_its_own_machine_under_the_lenient_index"):
            problems.append("an unreadable-row row is not attributed by its own machine")
            break
        if r.get("class") != C_PARSE and r.get(
                "attributed_by_its_own_machine_under_the_lenient_index"):
            problems.append("a row its own machine attributes is published under another class")
            break
    if s.get("rows_with_a_heartbeat_commit_inside") != sum(
            1 for r in rows if (r.get("heartbeat_commits_inside") or 0) > 0):
        problems.append("rows_with_a_heartbeat_commit_inside does not re-derive")
    if sum(1 for r in rows if r.get("receipts_inside")) > s.get("receipts_on_disk", 0) \
            and s.get("receipts_on_disk"):
        problems.append("more rows carry a receipt than there are receipts on disk")
    if any(r.get("class") not in CLASSES for r in rows):
        problems.append("a row carries a class outside the vocabulary")
    if any(not r.get("decided_by") for r in rows):
        problems.append("a row carries no witness sentence")
    for r in rows:
        if r.get("class") == C_PAUSE and (r.get("receipts_inside")
                                         or (r.get("heartbeat_commits_inside") or 0) > 0):
            problems.append("a pause row carries a trace inside it")
            break
        if r.get("class") == C_PAUSE and not r.get("gap_ends_at_first_row_of_round"):
            problems.append("a pause row does not end at its round's first row")
            break
        if r.get("class") == C_TRACE and not (r.get("receipts_inside")
                                             or (r.get("heartbeat_commits_inside") or 0) > 0):
            problems.append("a trace row carries no trace")
            break
        if r.get("class") == C_MID and r.get("gap_ends_at_first_row_of_round"):
            problems.append("a mid-round row claims to end at the round's first row")
            break
        if r.get("gap_hours") is not None and r["gap_hours"] <= 0:
            problems.append("a gap has non-positive length")
            break
    if s.get("population_agrees_with_e576") is False:
        problems.append("the re-derived population disagrees with E576's own class count")
    return problems


def selftest():
    ok = []

    def eq(name, got, want):
        ok.append((name, got == want, "got %r want %r" % (got, want)))

    base = datetime(2026, 11, 8, 22, 0, 0)
    row = {"ts": "2026-11-08T22:00:00", "date": "2026-11-08", "hour": 22, "machine": "b",
           "line": 1,
           "next_row_any_machine": {"ts": "2026-11-09T08:00:00", "round": 12,
                                    "line": 40, "report": "r.md", "machine": "b"}}
    receipts = [(datetime(2026, 11, 9, 3, 0, 0), "results/_r1_s6_chain.json", "11")]
    beats = [datetime(2026, 11, 8, 21, 0, 0), datetime(2026, 11, 9, 9, 0, 0)]

    f = gap_facts(row, True, 30.0, receipts, beats)
    eq("a_receipt_inside_is_a_trace", f["class"], C_TRACE)
    eq("the_gap_length_is_published", f["gap_hours"], 10.0)
    eq("the_gap_crosses_midnight", f["crosses_midnight"], True)
    eq("the_span_is_start_and_end_hour", f["hour_of_day_span"], [22, 8])

    quiet = gap_facts(row, True, 30.0, [], beats)
    eq("a_quiet_pause_ending_at_a_first_row_is_the_pause", quiet["class"], C_PAUSE)
    eq("a_pause_publishes_no_receipt", quiet["receipts_inside"], 0)

    mid = gap_facts(row, False, 30.0, [], beats)
    eq("closing_mid_round_is_not_a_pause", mid["class"], C_MID)

    unknown = gap_facts(row, True, 30.0, [], None)
    eq("an_unreadable_heartbeat_history_is_unidentified", unknown["class"], C_UNKNOWN)
    eq("unreadable_history_is_published_as_null", unknown["heartbeat_commits_inside"], None)

    no_end = dict(row)
    no_end["next_row_any_machine"] = None
    f2 = gap_facts(no_end, True, 30.0, receipts, beats)
    eq("a_gap_with_no_closing_row_has_no_length", f2["gap_hours"], None)

    eq("a_receipt_before_the_gap_is_not_inside",
       gap_facts(row, True, 30.0,
                 [(datetime(2026, 11, 8, 12, 0, 0), "x", "9")], [])["receipts_inside"], 0)
    eq("a_receipt_after_the_gap_is_not_inside",
       gap_facts(row, True, 30.0,
                 [(datetime(2026, 11, 9, 12, 0, 0), "x", "9")], [])["receipts_inside"], 0)

    seen = gap_facts(row, True, 30.0, receipts, beats, row_rounds={"11"})
    eq("a_receipt_round_with_a_row_is_split_into_seen", seen["receipt_rounds_with_no_row_anywhere"],
       [])
    unseen = gap_facts(row, True, 30.0, receipts, beats, row_rounds=set())
    eq("a_receipt_round_with_no_row_anywhere_is_named",
       unseen["receipt_rounds_with_no_row_anywhere"], ["11"])

    pipefree = [{"machine": "b", "round": 13, "report": "r.md", "line": 41,
                 "ts": datetime(2026, 11, 8, 23, 0, 0), "leading_pipe": False}]
    closed = gap_facts(row, True, 30.0, [], beats, set(), pipefree)
    eq("a_row_the_strict_index_cannot_read_wins_over_the_trace_class", closed["class"], C_PARSE)
    eq("the_lenient_distance_is_published",
       closed["next_row_under_the_lenient_index_minutes"], 60.0)
    eq("the_lenient_row_names_whether_it_has_a_pipe",
       closed["next_row_under_the_lenient_index_has_leading_pipe"], False)
    far = gap_facts(row, True, 30.0, receipts, beats, {"11"},
                    [{"machine": "b", "round": 13, "report": "r.md", "line": 41,
                      "ts": datetime(2026, 11, 9, 20, 0, 0), "leading_pipe": False}])
    eq("a_lenient_row_beyond_the_tolerance_does_not_close_the_gap", far["class"], C_TRACE)

    s = {"rows": 3, "by_class": {C_PAUSE: 3, C_TRACE: 0, C_MID: 0, C_UNKNOWN: 0}}
    eq("all_pauses_has_its_own_verdict", _verdict(s),
       "every_gap_is_the_pause_between_two_rounds_and_no_work_left_a_trace")
    eq("an_empty_population_says_so", _verdict({"rows": 0}), "no_gap_to_explain")
    v = _verdict({"rows": 4, "by_class": {C_PAUSE: 2, C_TRACE: 1, C_MID: 1, C_UNKNOWN: 0}})
    eq("a_split_verdict_names_three_classes",
       all(t in v for t in ("pause_between_rounds", "with_a_trace_inside",
                            "ending_mid_round")), True)

    good = {"rows": [{"class": C_TRACE, "hour": 22, "crosses_midnight": True,
                      "receipts_inside": 1, "heartbeat_commits_inside": 0,
                      "receipt_rounds_inside": ["11"],
                      "receipt_rounds_whose_row_exists": ["11"],
                      "receipt_rounds_with_no_row_anywhere": [],
                      "gap_ends_at_first_row_of_round": True, "gap_hours": 10.0,
                      "decided_by": "x"}],
            "summary": {"rows": 1, "by_class": {C_PARSE: 0, C_PAUSE: 0, C_TRACE: 1, C_MID: 0,
                                            C_UNKNOWN: 0},
                        "by_start_hour": {"22": 1}, "hours_hit": 1, "crosses_midnight": 1,
                        "rows_with_a_receipt_inside": 1,
                        "rows_with_a_heartbeat_commit_inside": 0,
                        "receipts_on_disk": 5, "receipts_without_a_parsable_ts": 0,
                        "receipt_rounds_named_inside_gaps": 1,
                        "receipt_rounds_with_no_row_anywhere": [],
                        "rows_ending_at_the_first_row_of_a_round": 1,
                        "rows_attributed_by_their_own_machine_under_the_lenient_index": 0,
                        "rows_closed_inside_the_tolerance_by_a_row_the_strict_index_cannot_read": 0,
                        "strict_rows_indexed": 10, "lenient_rows_indexed": 12,
                        "rows_without_a_leading_pipe": 2,
                        "e576_late_rows_again": 1, "population_agrees_with_e576": True}}
    good["verdict"] = _verdict(good["summary"])
    good["verdict_line"] = _verdict_line(good["summary"])
    eq("a_clean_face_passes", face_problems(good), [])

    bad = json.loads(json.dumps(good))
    bad["rows"][0]["class"] = C_PAUSE
    eq("a_pause_carrying_a_trace_is_refused", bool(face_problems(bad)), True)

    bad2 = json.loads(json.dumps(good))
    bad2["summary"]["by_start_hour"] = {"22": 7}
    eq("a_histogram_that_does_not_re_derive_is_refused", bool(face_problems(bad2)), True)

    bad3 = json.loads(json.dumps(good))
    bad3["summary"]["population_agrees_with_e576"] = False
    eq("a_population_that_disagrees_with_e576_is_refused", bool(face_problems(bad3)), True)

    failed = [n for n, g, _ in ok if not g]
    for n, g, detail in ok:
        print("  %s %s%s" % ("PASS" if g else "FAIL", n, "" if g else "  <- " + detail))
    print("selftest %d/%d" % (len(ok) - len(failed), len(ok)))
    return 0 if not failed else 1


def _check(face, label):
    problems = face_problems(face)
    if problems:
        for p in problems:
            print("%s FAIL %s" % (label, p))
        return 1
    print("%s PASS %s" % (label, face.get("verdict_line")))
    return 0


def check():
    return _check(_read_json(os.path.join(OUTDIR, "nightgap_latest.json")), "CHECK")


def verify():
    fresh = build(write=False)
    published = _read_json(os.path.join(OUTDIR, "nightgap_latest.json"))
    problems = face_problems(published)
    for key in ("verdict", "verdict_line", "summary"):
        if fresh.get(key) != published.get(key):
            problems.append("%s drifted between the published face and a live rebuild" % key)
    if [(r.get("class"), r.get("ts"), r.get("line")) for r in fresh.get("rows") or []] != \
            [(r.get("class"), r.get("ts"), r.get("line")) for r in published.get("rows") or []]:
        problems.append("a row's class changed between the published face and a live rebuild")
    for p in problems:
        print("VERIFY FAIL %s" % p)
    if not problems:
        print("VERIFY PASS %d rows re-derived" % len(published.get("rows") or []))
    return 0 if not problems else 1


def main(argv=None):
    argv = argv or sys.argv[1:]
    cmd = argv[0] if argv else "build"
    if cmd == "selftest":
        return selftest()
    if cmd == "build":
        face = build(write=True)
        print("BUILT %s | %s" % (face["verdict"], face["verdict_line"]))
        return 0
    if cmd == "check":
        return check()
    if cmd == "verify":
        return verify()
    print("unknown command %r" % cmd)
    return 2


if __name__ == "__main__":
    sys.exit(main())