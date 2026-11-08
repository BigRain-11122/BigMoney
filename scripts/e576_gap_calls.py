# -*- coding: utf-8 -*-
"""E576 -- where do the chain executions that no round row follows actually sit?

E575 (r1603 bm-b) read 490 chain executions out of this host's session transcripts and found 38
that fell outside every round row of their machine inside the 6h tolerance.  It published them as
"unattributable" and stopped there, which means the per-round answer silently excludes whatever
ran in a gap between rounds: an interactive session, a manual rerun, a hung chain.

This study takes that same population -- re-derived live from the transcripts, never copied from
E575's card -- and publishes four things about each one:

  hour            the local hour of day it ran in (the "which hours" question)
  next_any        the first round row of ANY machine printed after it, and the gap in minutes;
                  the tolerance for this field is E575's own 6h, so "inside" / "beyond" / "none"
                  are three distinct answers rather than one number
  switch          whether the invocation carried `--only` (E575 carried this per execution)
  duplicate       whether the same command line already appears among the executions E575
                  attributed to a round.  A gap execution that is a duplicate must be published as
                  a duplicate -- counting it again would invent a run that did not happen twice.

Classes (first match wins, witness published with every row):

  a_duplicate_of_a_run_attributed_to_a_round
  a_row_of_another_machine_follows_inside_the_tolerance
  only_a_row_beyond_the_tolerance_follows
  no_row_of_any_machine_follows_it

Usage: python scripts/e576_gap_calls.py [build|check|check-fast|verify|selftest]
"""
import importlib.util
import io
import json
import os
import re
import sys
from datetime import datetime, timedelta

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
OUTDIR = os.path.join(ROOT, "results", "state_tilt")
CUTOFF = "2026-11-08"
ATTRIB_TOL = timedelta(hours=6)

C_DUP = "a_duplicate_of_a_run_attributed_to_a_round"
C_CROSS = "a_row_of_another_machine_follows_inside_the_tolerance"
C_LATE = "only_a_row_beyond_the_tolerance_follows"
C_NONE = "no_row_of_any_machine_follows_it"
CLASSES = (C_DUP, C_CROSS, C_LATE, C_NONE)


def _read_json(path):
    with io.open(path, encoding="utf-8") as fh:
        return json.load(fh)


def _e575():
    """Reuse E575's transcript corpus and attribution so a "gap call" means the same thing."""
    path = os.path.join(HERE, "e575_only_flag.py")
    spec = importlib.util.spec_from_file_location("e575_only_flag", path)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def norm_line(text):
    """One command line reduced to the form two invocations must share to be a duplicate."""
    return re.sub(r"\s+", " ", (text or "")).strip()


def next_row(rows, ts, machine=None):
    """The first row printed at or after `ts` (optionally of one machine)."""
    cands = [r for r in rows
             if r.get("ts") and r["ts"] >= ts and (machine is None or r.get("machine") == machine)]
    if not cands:
        return None
    return min(cands, key=lambda r: r["ts"])


def _row_brief(row, ts):
    return {"machine": row.get("machine"), "round": row.get("round"),
            "report": row.get("report"), "line": row.get("line"),
            "ts": row["ts"].strftime("%Y-%m-%dT%H:%M:%S"),
            "minutes": round((row["ts"] - ts).total_seconds() / 60.0, 1),
            "inside_tolerance": (row["ts"] - ts) <= ATTRIB_TOL}


def gap_facts(call, rows, attributed_by_line):
    """Everything this study publishes about one unattributed execution."""
    ts = call["ts"]
    line_norm = norm_line(call.get("line"))
    dup = attributed_by_line.get(line_norm)
    any_row = next_row(rows, ts)
    same_row = next_row(rows, ts, machine=call.get("machine"))
    facts = {
        "ts": ts.strftime("%Y-%m-%dT%H:%M:%S"),
        "date": ts.strftime("%Y-%m-%d"),
        "hour": ts.hour,
        "machine": call.get("machine"),
        "line": call.get("line"),
        "carries_the_switch": bool(call.get("carries_the_switch")),
        "flag_token": call.get("flag_token"),
        "snapshot": call.get("snapshot"),
        "next_row_any_machine": _row_brief(any_row, ts) if any_row else None,
        "next_row_same_machine": _row_brief(same_row, ts) if same_row else None,
        "duplicate_of": dup,
    }
    if dup:
        facts["class"] = C_DUP
        facts["decided_by"] = ("the same command line already runs inside round %s of %s"
                              % (dup.get("round"), dup.get("report")))
    elif any_row is not None and (any_row["ts"] - ts) <= ATTRIB_TOL:
        facts["class"] = C_CROSS
        facts["decided_by"] = ("a row of machine %s follows in %.1f min, inside the %s tolerance, "
                              "but the row of this command's own machine does not"
                              % (any_row.get("machine"),
                                 (any_row["ts"] - ts).total_seconds() / 60.0, ATTRIB_TOL))
    elif any_row is not None:
        facts["class"] = C_LATE
        facts["decided_by"] = ("the first row of any machine follows in %.1f min, beyond the %s "
                              "tolerance" % ((any_row["ts"] - ts).total_seconds() / 60.0,
                                             ATTRIB_TOL))
    else:
        facts["class"] = C_NONE
        facts["decided_by"] = "no round row of any machine is printed after this execution"
    return facts


def hour_hist(entries):
    hist = {}
    for e in entries:
        h = e.get("hour")
        if h is None:
            continue
        hist[str(h)] = hist.get(str(h), 0) + 1
    return hist


def build(write=True):
    e575 = _e575()
    e573 = e575._e573()
    calls, mentions, snapshots = e575.command_corpus()
    rows_index = e575.round_index(e573)
    calls, unassigned_ref = e575.attribute(calls, rows_index)
    unattr = [c for c in calls if c.get("round") is None]

    attributed_by_line = {}
    for c in calls:
        if c.get("round") is None:
            continue
        attributed_by_line.setdefault(norm_line(c.get("line")), {
            "round": c.get("round"), "report": c.get("report"),
            "ts": c["ts"].strftime("%Y-%m-%dT%H:%M:%S")})

    rows = [gap_facts(c, rows_index, attributed_by_line) for c in unattr]
    rows.sort(key=lambda r: r["ts"])
    by_class = {k: sum(1 for r in rows if r["class"] == k) for k in CLASSES}
    hist = hour_hist(rows)
    late_minutes = [r["next_row_any_machine"]["minutes"] for r in rows
                    if r["class"] == C_LATE and r.get("next_row_any_machine")]
    summary = {
        "rows": len(rows),
        "by_class": by_class,
        "by_hour": hist,
        "hours_hit": len(hist),
        "executions_carrying_the_switch": sum(1 for r in rows if r["carries_the_switch"]),
        "duplicates_of_attributed_runs": by_class[C_DUP],
        "cross_machine_inside_tolerance": by_class[C_CROSS],
        "beyond_tolerance": by_class[C_LATE],
        "no_later_row_at_all": by_class[C_NONE],
        "late_gap_minutes_min": min(late_minutes) if late_minutes else None,
        "late_gap_minutes_max": max(late_minutes) if late_minutes else None,
        "corpus_executions": len(calls),
        "corpus_unattributed": len(unattr),
        "e575_unattributed_again": len(unassigned_ref),
        "population_agrees_with_e575": len(unattr) == len(unassigned_ref),
        "snapshots_parsed": snapshots,
        "attribution_rule": ("E575's: a command belongs to the first row of the same machine "
                             "printed at or after it, within %s" % ATTRIB_TOL),
        "unnamed_witnesses": ["who_typed_the_gap_command"],
    }
    out = {
        "study": "E576_gap_calls",
        "card": "E576",
        "dept": "research",
        "machine": "bm-b",
        "evidence_cutoff": CUTOFF,
        "population": ("every executed chain invocation in this host's transcripts that E575's "
                       "attribution rule leaves without a following row of its own machine "
                       "inside %s; re-derived live, compared to E575's own count" % ATTRIB_TOL),
        "rule": ("duplicate of an attributed run -> duplicate; else the first row of any machine "
                 "after it decides: inside the tolerance -> another machine's window, beyond -> "
                 "late, absent -> nothing follows"),
        "summary": summary,
        "verdict": _verdict(summary),
        "verdict_line": _verdict_line(summary),
        "rows": rows,
    }
    if write:
        if not os.path.isdir(OUTDIR):
            os.makedirs(OUTDIR)
        for path in (os.path.join(OUTDIR, "GAPCALLS-%s.json" % CUTOFF),
                     os.path.join(OUTDIR, "gapcalls_latest.json")):
            with io.open(path, "w", encoding="utf-8", newline="\n") as fh:
                json.dump(out, fh, ensure_ascii=False, indent=1, sort_keys=True)
    return out


def _verdict(s):
    by = s.get("by_class") or {}
    n = s.get("rows") or 0
    if not n:
        return "no_gap_execution_to_price"
    if by.get(C_DUP, 0) == n:
        return "every_gap_execution_is_a_duplicate_of_an_attributed_run"
    if by.get(C_NONE, 0) == n:
        return "no_row_of_any_machine_ever_follows_a_gap_execution"
    parts = []
    if by.get(C_DUP):
        parts.append("%d_duplicate_of_an_attributed_run" % by[C_DUP])
    if by.get(C_CROSS):
        parts.append("%d_inside_another_machine_s_window" % by[C_CROSS])
    if by.get(C_LATE):
        parts.append("%d_after_a_gap_beyond_the_tolerance" % by[C_LATE])
    if by.get(C_NONE):
        parts.append("%d_with_nothing_after_them" % by[C_NONE])
    return ("the_gap_executions_split_%d_ways: %s"
            % (sum(1 for k in CLASSES if by.get(k)), " + ".join(parts)))


def _verdict_line(s):
    by = s.get("by_class") or {}
    return ("gap_executions=%d duplicate=%d cross_machine_inside=%d beyond_tolerance=%d "
            "nothing_follows=%d | hours_hit=%d with_switch=%d | corpus=%d e575_again=%d "
            "agree=%s | snapshots=%d"
            % (s.get("rows", 0), by.get(C_DUP, 0), by.get(C_CROSS, 0), by.get(C_LATE, 0),
               by.get(C_NONE, 0), s.get("hours_hit", 0),
               s.get("executions_carrying_the_switch", 0), s.get("corpus_executions", 0),
               s.get("e575_unattributed_again", 0),
               s.get("population_agrees_with_e575"), s.get("snapshots_parsed", 0)))


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
    if s.get("by_hour") != hour_hist(rows):
        problems.append("by_hour does not re-derive from the rows")
    if s.get("hours_hit") != len(s.get("by_hour") or {}):
        problems.append("hours_hit does not equal the hour histogram's size")
    if s.get("executions_carrying_the_switch") != sum(
            1 for r in rows if r.get("carries_the_switch")):
        problems.append("executions_carrying_the_switch does not re-derive from the rows")
    if s.get("duplicates_of_attributed_runs") != counts[C_DUP]:
        problems.append("duplicates_of_attributed_runs does not equal by_class")
    if sum(1 for r in rows if r.get("class") == C_DUP and r.get("duplicate_of")) != counts[C_DUP]:
        problems.append("a row is published as a duplicate without naming what it duplicates")
    if any(r.get("class") not in CLASSES for r in rows):
        problems.append("a row carries a class outside the vocabulary")
    if any(r.get("class") == C_DUP and not r.get("decided_by") for r in rows):
        problems.append("a decided row carries no witness sentence")
    if s.get("corpus_unattributed", 0) > s.get("corpus_executions", 0):
        problems.append("the unattributed count is larger than the corpus it is drawn from")
    if s.get("population_agrees_with_e575") is False:
        problems.append("the re-derived population disagrees with E575's own count")
    for r in rows:
        any_row = r.get("next_row_any_machine")
        if r.get("class") == C_CROSS and not (any_row and any_row.get("inside_tolerance")):
            problems.append("a cross-machine row has no row inside the tolerance")
            break
        if r.get("class") == C_LATE and not (any_row and not any_row.get("inside_tolerance")):
            problems.append("a late row names a row inside the tolerance")
            break
        if r.get("class") == C_NONE and any_row:
            problems.append("a nothing-follows row names a following row")
            break
    return problems


def selftest():
    ok = []
    base = datetime(2026, 11, 8, 1, 0, 0)

    def eq(name, got, want):
        ok.append((name, got == want, "got %r want %r" % (got, want)))

    rows = [{"machine": "b", "round": 10, "report": "r-b", "line": 1,
             "ts": base + timedelta(hours=2)},
            {"machine": "a", "round": 11, "report": "r-a", "line": 2,
             "ts": base + timedelta(hours=9)},
            {"machine": "a", "round": 12, "report": "r-a", "line": 3,
             "ts": base + timedelta(hours=20)}]
    call = {"ts": base, "machine": "b", "line": "python Tools/s6_chain_bmb.py run",
            "carries_the_switch": False}

    facts = gap_facts(call, rows, {})
    eq("a_row_2h_later_inside_tolerance_is_cross", facts["class"], C_CROSS)
    eq("the_next_row_is_the_nearest_one", facts["next_row_any_machine"]["round"], 10)
    eq("minutes_are_published", facts["next_row_any_machine"]["minutes"], 120.0)
    eq("the_same_machine_row_is_also_published", facts["next_row_same_machine"]["round"], 10)
    eq("hour_is_the_local_hour", facts["hour"], 1)

    late = gap_facts(call, rows[1:], {})
    eq("a_row_9h_later_is_beyond_tolerance", late["class"], C_LATE)
    eq("beyond_tolerance_flag_is_false", late["next_row_any_machine"]["inside_tolerance"], False)

    none = gap_facts(call, [], {})
    eq("no_rows_at_all_is_nothing_follows", none["class"], C_NONE)
    eq("nothing_follows_publishes_no_row", none["next_row_any_machine"], None)

    dup = gap_facts(call, rows[1:], {norm_line(call["line"]): {"round": 9, "report": "r-b",
                                                              "ts": "2026-11-07T23:00:00"}})
    eq("a_duplicate_wins_over_the_late_class", dup["class"], C_DUP)
    eq("a_duplicate_names_the_round_it_repeats", dup["duplicate_of"]["round"], 9)

    eq("whitespace_does_not_make_two_commands", norm_line("  a   b "), norm_line("a b"))
    eq("different_commands_stay_different",
       norm_line("a b") == norm_line("a c"), False)

    h = hour_hist([{"hour": 1}, {"hour": 1}, {"hour": 22}])
    eq("hour_histogram_counts_repeats", h, {"1": 2, "22": 1})
    eq("the_histogram_size_is_the_hours_hit", len(h), 2)

    s = {"rows": 3, "by_class": {C_DUP: 3, C_CROSS: 0, C_LATE: 0, C_NONE: 0}}
    eq("all_duplicates_has_its_own_verdict", _verdict(s),
       "every_gap_execution_is_a_duplicate_of_an_attributed_run")
    s2 = {"rows": 2, "by_class": {C_DUP: 0, C_CROSS: 0, C_LATE: 0, C_NONE: 2}}
    eq("nothing_follows_has_its_own_verdict", _verdict(s2),
       "no_row_of_any_machine_ever_follows_a_gap_execution")
    s3 = {"rows": 4, "by_class": {C_DUP: 1, C_CROSS: 2, C_LATE: 1, C_NONE: 0}}
    v = _verdict(s3)
    eq("a_split_verdict_names_all_three_classes",
       all(t in v for t in ("duplicate", "another_machine_s_window",
                            "beyond_the_tolerance")), True)

    good = {"rows": [{"class": C_CROSS, "hour": 1,
                      "next_row_any_machine": {"inside_tolerance": True},
                      "decided_by": "x", "carries_the_switch": True}],
            "summary": {"rows": 1, "by_class": {C_DUP: 0, C_CROSS: 1, C_LATE: 0, C_NONE: 0},
                        "by_hour": {"1": 1}, "hours_hit": 1,
                        "executions_carrying_the_switch": 1,
                        "duplicates_of_attributed_runs": 0, "cross_machine_inside_tolerance": 1,
                        "beyond_tolerance": 0, "no_later_row_at_all": 0,
                        "corpus_executions": 1, "corpus_unattributed": 1,
                        "population_agrees_with_e575": True}}
    good["verdict"] = _verdict(good["summary"])
    good["verdict_line"] = _verdict_line(good["summary"])
    eq("a_clean_face_passes", face_problems(good), [])

    bad = json.loads(json.dumps(good))
    bad["summary"]["by_hour"] = {"1": 5}
    eq("a_histogram_that_does_not_re_derive_is_refused", bool(face_problems(bad)), True)

    bad2 = json.loads(json.dumps(good))
    bad2["rows"][0]["class"] = C_LATE
    eq("a_class_that_contradicts_its_own_row_is_refused", bool(face_problems(bad2)), True)

    bad3 = json.loads(json.dumps(good))
    bad3["verdict"] = "something_else"
    eq("a_verdict_that_does_not_re_derive_is_refused", bool(face_problems(bad3)), True)

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
    return _check(_read_json(os.path.join(OUTDIR, "gapcalls_latest.json")), "CHECK")


def check_fast():
    return check()


def verify():
    fresh = build(write=False)
    published = _read_json(os.path.join(OUTDIR, "gapcalls_latest.json"))
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
    if cmd == "check-fast":
        return check_fast()
    if cmd == "verify":
        return verify()
    print("unknown command %r" % cmd)
    return 2


if __name__ == "__main__":
    sys.exit(main())