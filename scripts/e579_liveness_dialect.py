# -*- coding: utf-8 -*-
"""E579 -- whether the liveness line would call a peer dead in the dialect it does not read.

E578 (r1606 bm-b) measured every reader of the round-row index and found that the module which
decides ALIVE / NO-EVIDENCE / DEAD for a machine -- ``Tools/lane_round_liveness.ledger_times_text``
-- sees 659 of 2,752 rows because a row must start with a pipe to be read at all.  E578 stopped at
the row count, and a row count is not a verdict.  This study re-runs the shipped verdict for every
machine under two dialects that differ in exactly one thing:

  strict   the module as shipped: a ledger row counts only if the line starts with ``|``
  wide     the same row shape with the leading pipe optional -- no other axis moves (same files,
           same text source, same state/heartbeat faces, same thresholds, same code path)

Per machine it publishes both verdicts, the three faces each one opens, the row counts, the last
row age, the rounds in 24h, and the 7 day gap summary.  A machine whose newest row carries no pipe
would be aged off the last pipe row and flip; that margin is published as ``invisible_rows_within_
alive_min`` rather than left to be discovered when it happens.

Classes of the comparison (first match wins, published per machine):

  flips_alive_under_the_wide_reader        shipped verdict is DEAD/NO-EVIDENCE, wide verdict ALIVE
  verdict_holds_but_the_disclosure_moves   same verdict, different rounds_24h or worst gap
  the_dialect_costs_nothing_here           every row the wide reader finds is also read strictly

Bounds published, not claimed: a peer's ledger is read through ``git show origin/main:<path>``
(the worktree mirror is hundreds of commits behind, r1243), bm-b through its own worktree file --
the source is named per machine.  Neither dialect can see a row that was never written, so an
agreement between them is agreement about this text, not proof that the lane ran.

Usage: python scripts/e579_liveness_dialect.py [build|check|verify|selftest]
"""
import importlib.util
import io
import json
import os
import re
import subprocess
import sys
from datetime import datetime, timedelta, timezone

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
OUTDIR = os.path.join(ROOT, "results", "state_tilt")
CUTOFF = "2026-11-09"
MACHINES = ("bm-a", "bm-b", "bm-c")

C_FLIP = "flips_alive_under_the_wide_reader"
C_MOVES = "verdict_holds_but_the_disclosure_moves"
C_LOST = "rows_are_lost_without_moving_a_published_number"
C_NOTHING = "the_dialect_costs_nothing_here"

#: the shipped reader's own row shape, minus the leading-pipe requirement.  Kept identical to
#: Tools/lane_round_liveness.TS_RE after the pipe so a difference cannot come from the stamp.
WIDE_TS_RE = re.compile(
    r"^\|?\s*(\d{4}-\d{2}-\d{2}T\d{2}:\d{2}(?::\d{2})?(?:[+-]\d{2}:\d{2})?)\s*"
)


def _mod(name, rel):
    path = os.path.join(ROOT, rel)
    spec = importlib.util.spec_from_file_location(name, path)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def lane():
    """The shipped liveness module, loaded from the tree (never re-implemented here)."""
    return _mod("lane_round_liveness_shipped", os.path.join("Tools", "lane_round_liveness.py"))


# --------------------------------------------------------------------------- #
# the two dialects
# --------------------------------------------------------------------------- #

def wide_times_text(text, mod):
    """Same rows the shipped reader takes, with the leading pipe optional."""
    out = []
    for line in text.splitlines():
        m = WIDE_TS_RE.match(line)
        if not m:
            continue
        try:
            out.append(mod.parse_ts(m.group(1)))
        except ValueError:
            continue
    return out


def ledger_text(machine, mod):
    """The ledger text for a machine, with the source named the way the shipped module does."""
    path = mod.report_path(machine)
    rel = os.path.relpath(path, ROOT).replace("\\", "/")
    if machine != "bm-b":
        try:
            proc = subprocess.run(["git", "-C", ROOT, "show", "origin/main:%s" % rel],
                                  capture_output=True)
            if proc.returncode == 0 and proc.stdout:
                return proc.stdout.decode("utf-8", "replace"), "origin/main"
        except Exception:
            pass
    if os.path.exists(path):
        return io.open(path, encoding="utf-8", errors="replace").read(), "worktree"
    return "", "absent"


# --------------------------------------------------------------------------- #
# evidence + verdict, driven by an explicit row list
# --------------------------------------------------------------------------- #

def evidence(times, state, hb, now, mod):
    """The fields verdict_of() consumes, computed the shipped way from a given row list."""
    def age(ts):
        return None if ts is None else round((now - ts).total_seconds() / 60.0, 1)

    last_row = times[-1] if times else None
    recent = [t for t in times if now - t <= timedelta(days=7)]
    gaps = []
    for a, b in zip(recent, recent[1:]):
        if b < a:
            continue
        minutes = (b - a).total_seconds() / 60.0
        if minutes >= mod.GAP_MIN:
            gaps.append(round(minutes, 1))

    hb_ts = None
    for key in ("ts", "last_seen", "clock_read"):
        raw = hb.get(key)
        if isinstance(raw, str):
            try:
                hb_ts = mod.parse_ts(raw if "T" in raw else raw.replace(" ", "T"))
                break
            except ValueError:
                continue

    return {
        "last_row_age_min": age(last_row),
        "rows_total": len(times),
        "rows_7d": len(recent),
        "rounds_24h": len([t for t in times if now - t <= timedelta(hours=24)]),
        "gaps_7d": len(gaps),
        "worst_gap_7d_min": max(gaps) if gaps else 0.0,
        "state_round_no": state.get("round_no"),
        "hb_round_no": hb.get("round_no"),
        "hb_ts": hb_ts.isoformat() if hb_ts else None,
        "hb_age_min": age(hb_ts),
    }


def compare(machine, text, source, state, hb, now, mod, published=None):
    """Both dialects over one machine's text.  Pure: takes every input explicitly."""
    strict_times = mod.ledger_times_text(text)
    wide_times = wide_times_text(text, mod)
    strict = evidence(strict_times, state, hb, now, mod)
    wide = evidence(wide_times, state, hb, now, mod)
    strict_v = mod.verdict_of(strict)
    wide_v = mod.verdict_of(wide)

    strict_set = set(strict_times)
    invisible = [t for t in wide_times if t not in strict_set]
    newest_is_pipe = bool(wide_times) and wide_times[-1] in strict_set

    if strict_v["verdict"] != "ALIVE" and wide_v["verdict"] == "ALIVE":
        klass = C_FLIP
    elif (wide["rounds_24h"] != strict["rounds_24h"]
          or abs(wide["worst_gap_7d_min"] - strict["worst_gap_7d_min"]) > 1e-9):
        klass = C_MOVES
    elif len(wide_times) != len(strict_times):
        # rows vanish on this text without moving any number the module publishes, which is not
        # the same statement as "the dialect costs nothing here"
        klass = C_LOST
    else:
        klass = C_NOTHING

    row = {
        "machine": machine,
        "class": klass,
        "ledger_source": source,
        "ledger_lines": len(text.splitlines()),
        "strict": dict(strict, verdict=strict_v["verdict"], faces=strict_v["faces"],
                       faces_open=strict_v["faces_open"]),
        "wide": dict(wide, verdict=wide_v["verdict"], faces=wide_v["faces"],
                     faces_open=wide_v["faces_open"]),
        "verdict_flips": strict_v["verdict"] != wide_v["verdict"],
        "newest_row_has_a_pipe": newest_is_pipe,
        "rows_invisible_to_the_shipped_reader": len(invisible),
        "invisible_rows_within_alive_min": len(
            [t for t in invisible if (now - t).total_seconds() / 60.0 <= mod.ALIVE_MIN]),
        "invisible_rows_within_dead_min": len(
            [t for t in invisible if (now - t).total_seconds() / 60.0 <= mod.DEAD_MIN]),
        "rounds_24h_delta": wide["rounds_24h"] - strict["rounds_24h"],
        "worst_gap_7d_delta_min": round(
            strict["worst_gap_7d_min"] - wide["worst_gap_7d_min"], 1),
    }
    if published:
        row["published_face"] = {
            "verdict": published.get("verdict"),
            "generated": published.get("generated"),
            # a verdict face that carries no timestamp cannot be aged, so a reader cannot tell a
            # five minute old ALIVE from a three day old one -- published rather than assumed
            "has_a_timestamp": bool(published.get("generated") or published.get("generated_at")
                                    or published.get("ts")),
            "agrees_with_the_strict_recompute": published.get("verdict") == strict_v["verdict"],
        }
    return row


def _verdict(summary):
    n = summary["machines"]
    if not n:
        return "no_machine_ledger_to_compare"
    if summary["machines_that_flip"]:
        return ("the_shipped_liveness_line_calls_%d_of_%d_machines_dead_that_the_pipe_tolerant"
                "_reader_calls_alive" % (summary["machines_that_flip"], n))
    if summary["machines_whose_disclosure_moves"]:
        return ("no_machine_flips_a_verdict_but_%d_of_%d_machines_publish_a_gap_or_round_count"
                "_the_wide_reader_does_not_reproduce"
                % (summary["machines_whose_disclosure_moves"], n))
    if summary.get("machines_whose_rows_are_lost_without_a_number_moving"):
        return ("no_published_number_moves_but_%d_of_%d_machines_still_lose_rows_to_the_dialect"
                % (summary["machines_whose_rows_are_lost_without_a_number_moving"], n))
    return "the_two_dialects_agree_on_every_machine_here"


def _verdict_line(summary):
    if summary["machines_that_flip"]:
        worst = summary["machines_that_flip"]
        return ("%d of %d machines are called dead or unevidenced by the shipped reader and alive "
                "by the pipe-tolerant one; %d rows inside the alive window are invisible to the "
                "shipped dialect." % (worst, summary["machines"],
                                      summary["invisible_rows_within_alive_min"]))
    if summary["machines_whose_disclosure_moves"]:
        return ("no machine flips between the dialects, yet %d of %d publish a disclosure the wide "
                "reader does not reproduce (largest 7 day gap overstated by %s minutes); "
                "%d of %d rows are invisible to the shipped reader."
                % (summary["machines_whose_disclosure_moves"], summary["machines"],
                   summary["largest_worst_gap_overstatement_min"],
                   summary["rows_invisible_to_the_shipped_reader"], summary["wide_rows_total"]))
    if summary["machines_whose_rows_are_lost_without_a_number_moving"]:
        return ("%d of %d machines lose rows to the dialect while every number the module "
                "publishes for them stays identical -- the loss is real and invisible in the "
                "face; %d of %d rows are unreadable to the shipped reader."
                % (summary["machines_whose_rows_are_lost_without_a_number_moving"],
                   summary["machines"],
                   summary["rows_invisible_to_the_shipped_reader"], summary["wide_rows_total"]))
    return ("every row the wide reader finds is also read strictly across %d machines; the "
            "dialect costs nothing on this text." % summary["machines"])


def summarise(rows):
    def count(pred):
        return len([r for r in rows if pred(r)])

    s = {
        "machines": len(rows),
        "machines_that_flip": count(lambda r: r["class"] == C_FLIP),
        "machines_whose_disclosure_moves": count(lambda r: r["class"] == C_MOVES),
        "machines_the_dialect_costs_nothing": count(lambda r: r["class"] == C_NOTHING),
        "machines_whose_rows_are_lost_without_a_number_moving": count(
            lambda r: r["class"] == C_LOST),
        "strict_rows_total": sum(r["strict"]["rows_total"] for r in rows),
        "wide_rows_total": sum(r["wide"]["rows_total"] for r in rows),
        "rows_invisible_to_the_shipped_reader": sum(
            r["rows_invisible_to_the_shipped_reader"] for r in rows),
        "invisible_rows_within_alive_min": sum(
            r["invisible_rows_within_alive_min"] for r in rows),
        "invisible_rows_within_dead_min": sum(
            r["invisible_rows_within_dead_min"] for r in rows),
        "rounds_24h_delta_total": sum(r["rounds_24h_delta"] for r in rows),
        "largest_worst_gap_overstatement_min": max(
            [r["worst_gap_7d_delta_min"] for r in rows] or [0.0]),
        "machines_whose_newest_row_has_a_pipe": count(lambda r: r["newest_row_has_a_pipe"]),
        "machines_with_a_published_face": count(lambda r: "published_face" in r),
        "published_faces_agreeing_with_the_strict_recompute": count(
            lambda r: (r.get("published_face") or {}).get("agrees_with_the_strict_recompute")),
        "published_faces_without_a_timestamp": count(
            lambda r: (r.get("published_face") or {}).get("has_a_timestamp") is False),
        "thresholds_from_the_shipped_module": {"alive_min": None, "dead_min": None,
                                               "gap_min": None},
    }
    return s


# --------------------------------------------------------------------------- #
# build
# --------------------------------------------------------------------------- #

def build(write=True):
    mod = lane()
    now = datetime.now(timezone.utc).astimezone()
    rows = []
    for machine in MACHINES:
        text, source = ledger_text(machine, mod)
        state, _ = mod.read_json_origin(os.path.join(ROOT, "state-%s.json" % machine))
        hb, _ = mod.read_json_origin(
            os.path.join(ROOT, "fleet", "machines", "%s.json" % machine))
        face_path = os.path.join(ROOT, "results", "lane_liveness.%s.json" % machine)
        published = mod.read_json(face_path) if os.path.exists(face_path) else None
        rows.append(compare(machine, text, source, state, hb, now, mod, published))

    summary = summarise(rows)
    summary["thresholds_from_the_shipped_module"] = {
        "alive_min": mod.ALIVE_MIN, "dead_min": mod.DEAD_MIN, "gap_min": mod.GAP_MIN}
    face = {
        "study": "E579_liveness_dialect",
        "generated_by": "scripts/e579_liveness_dialect.py",
        "machine": "bm-b",
        "dept": "research+engineering",
        "evidence_cutoff": CUTOFF,
        "generated": now.isoformat(timespec="seconds"),
        "rule": ("strict = Tools/lane_round_liveness.ledger_times_text as shipped; "
                 "wide = the same row shape with the leading pipe optional; every other "
                 "input and threshold is shared"),
        "rows": rows,
        "summary": summary,
        "verdict": _verdict(summary),
        "verdict_line": _verdict_line(summary),
    }
    if write:
        os.makedirs(OUTDIR, exist_ok=True)
        name = "LIVENESSDIALECT-%s.json" % CUTOFF
        body = json.dumps(face, ensure_ascii=False, indent=1, sort_keys=True) + "\n"
        io.open(os.path.join(OUTDIR, name), "w", encoding="utf-8", newline="\n").write(body)
        io.open(os.path.join(OUTDIR, "livenessdialect_latest.json"), "w", encoding="utf-8",
                newline="\n").write(body)
    return face


# --------------------------------------------------------------------------- #
# face checks
# --------------------------------------------------------------------------- #

def face_problems(face):
    p = []
    rows = face.get("rows")
    if not isinstance(rows, list) or not rows:
        return ["the face carries no machine rows"]
    for r in rows:
        for side in ("strict", "wide"):
            if not isinstance(r.get(side), dict):
                p.append("%s: the %s reading is missing" % (r.get("machine"), side))
        st, wd = r.get("strict") or {}, r.get("wide") or {}
        if st.get("rows_total") is not None and wd.get("rows_total") is not None:
            if wd["rows_total"] < st["rows_total"]:
                p.append("%s: the wide reader sees fewer rows than the strict one"
                         % r.get("machine"))
            if (wd["rows_total"] - st["rows_total"]
                    != r.get("rows_invisible_to_the_shipped_reader")):
                p.append("%s: invisible row count does not re-derive from the two totals"
                         % r.get("machine"))
        if (r.get("class") == C_FLIP) != (
                st.get("verdict") != "ALIVE" and wd.get("verdict") == "ALIVE"):
            p.append("%s: the flip class does not follow the two verdicts" % r.get("machine"))
        if r.get("class") == C_MOVES and not (
                st.get("rounds_24h") != wd.get("rounds_24h")
                or abs((st.get("worst_gap_7d_min") or 0) - (wd.get("worst_gap_7d_min") or 0)) > 1e-9):
            p.append("%s: a disclosure that did not move is published as having moved"
                     % r.get("machine"))
        if r.get("class") == C_NOTHING and st.get("rows_total") != wd.get("rows_total"):
            p.append("%s: rows differ while the class says the dialect costs nothing"
                     % r.get("machine"))
        if r.get("class") == C_LOST and st.get("rows_total") == wd.get("rows_total"):
            p.append("%s: a class of lost rows is published where no row differs"
                     % r.get("machine"))
        for side in ("strict", "wide"):
            ev = r.get(side) or {}
            if ev.get("verdict") not in ("ALIVE", "NO-EVIDENCE", "DEAD"):
                p.append("%s: %s verdict %r is not one of the three states"
                         % (r.get("machine"), side, ev.get("verdict")))
            if ev.get("verdict") == "ALIVE" and ev.get("last_row_age_min") is not None:
                if not (ev["last_row_age_min"] <= ev.get("alive_min", 25.0)
                        or (ev.get("hb_age_min") is not None
                            and ev["hb_age_min"] <= ev.get("alive_min", 25.0))):
                    p.append("%s: %s is ALIVE with no fresh product or instance face"
                             % (r.get("machine"), side))
    recomputed = summarise(rows)
    for key, value in face.get("summary", {}).items():
        if key == "thresholds_from_the_shipped_module":
            continue
        if recomputed.get(key) != value:
            p.append("summary.%s does not re-derive from the rows (%r vs %r)"
                     % (key, value, recomputed.get(key)))
    if face.get("verdict") != _verdict(face.get("summary") or {}):
        p.append("the verdict does not re-derive from the summary")
    if face.get("verdict_line") != _verdict_line(face.get("summary") or {}):
        p.append("the verdict line does not re-derive from the summary")
    if not face.get("evidence_cutoff"):
        p.append("the face declares no evidence_cutoff")
    return p


def _read_json(path):
    if not os.path.exists(path):
        return {}
    try:
        return json.load(io.open(path, encoding="utf-8"))
    except Exception:
        return {}


def check():
    face = _read_json(os.path.join(OUTDIR, "livenessdialect_latest.json"))
    problems = face_problems(face)
    for p in problems:
        print("CHECK FAIL %s" % p)
    if not problems:
        print("CHECK PASS %s" % face.get("verdict_line"))
    return 0 if not problems else 1


def verify():
    published = _read_json(os.path.join(OUTDIR, "livenessdialect_latest.json"))
    fresh = build(write=False)
    problems = face_problems(published)
    for key in ("verdict", "verdict_line"):
        if fresh.get(key) != published.get(key):
            problems.append("%s drifted between the published face and a live rebuild" % key)
    for a, b in zip(fresh.get("rows") or [], published.get("rows") or []):
        if (a.get("machine"), a.get("class"), a.get("strict", {}).get("rows_total"),
                a.get("wide", {}).get("rows_total")) != (
                b.get("machine"), b.get("class"), b.get("strict", {}).get("rows_total"),
                b.get("wide", {}).get("rows_total")):
            problems.append("%s: the class or a row count changed on a live rebuild"
                            % a.get("machine"))
    for p in problems:
        print("VERIFY FAIL %s" % p)
    if not problems:
        print("VERIFY PASS %d machines re-derived" % len(published.get("rows") or []))
    return 0 if not problems else 1


# --------------------------------------------------------------------------- #
# selftest
# --------------------------------------------------------------------------- #

def selftest():
    mod = lane()
    ok = []

    def eq(name, got, want):
        ok.append((name, got == want, "%r != %r" % (got, want)))

    now = datetime(2026, 11, 9, 6, 0, 0, tzinfo=timezone(timedelta(hours=8)))

    def stamp(minutes_ago, pipe=True):
        ts = (now - timedelta(minutes=minutes_ago)).isoformat()
        return ("| %s | r1 | dept:x |" % ts) if pipe else ("%s | r1 | dept:x |" % ts)

    state = {"round_no": 10}
    hb = {"round_no": 10, "ts": (now - timedelta(minutes=3)).isoformat()}

    # S1 the two dialects differ on exactly the pipe
    text = "\n".join([stamp(5), stamp(15, pipe=False), stamp(25)])
    strict = mod.ledger_times_text(text)
    wide = wide_times_text(text, mod)
    eq("a pipe-less row is read by the wide dialect only", (len(strict), len(wide)), (2, 3))

    # S2 a newest row without a pipe flips a machine from dead to alive
    only_recent_without_pipe = "\n".join([stamp(900), stamp(5, pipe=False)])
    state_old = {"round_no": 10}
    hb_old = {"round_no": 9, "ts": (now - timedelta(minutes=900)).isoformat()}
    flip = compare("bm-x", only_recent_without_pipe, "worktree", state_old, hb_old, now, mod)
    eq("a pipe-less newest row flips the shipped verdict", flip["class"], C_FLIP)
    eq("the flip names the two verdicts",
       (flip["strict"]["verdict"] == "DEAD", flip["wide"]["verdict"] == "ALIVE"), (True, True))
    eq("the flip is counted inside the alive window",
       flip["invisible_rows_within_alive_min"], 1)
    eq("the newest row is published as pipe-less", flip["newest_row_has_a_pipe"], False)

    # S3 older pipe-less rows move the disclosure without touching the verdict
    # chronological, the way a ledger is written: oldest first
    text3 = "\n".join(stamp(m, pipe) for m, pipe in
                      ((500, False), (400, True), (300, False), (200, True), (100, False),
                       (5, True)))
    moves = compare("bm-y", text3, "worktree", state, hb, now, mod)
    eq("unread rows inside the window move the disclosure class", moves["class"], C_MOVES)
    eq("the verdict itself holds", moves["verdict_flips"], False)
    eq("the rounds in 24h are under-counted by the shipped reader",
       moves["rounds_24h_delta"], 3)
    eq("the fabricated 7 day gap is published as an overstatement",
       moves["worst_gap_7d_delta_min"], 100.0)

    # S4 a fully piped ledger costs nothing
    plain = "\n".join([stamp(5), stamp(15), stamp(25)])
    same = compare("bm-z", plain, "worktree", state, hb, now, mod)
    eq("a piped ledger is classed as costing nothing", same["class"], C_NOTHING)
    eq("and nothing is invisible", same["rows_invisible_to_the_shipped_reader"], 0)

    # S4b rows can vanish from the population without moving any number the module publishes:
    # an unread row older than the 7 day window is lost from rows_total and from nothing else.
    # This is not the same statement as "the dialect costs nothing", and a face that said so
    # would be publishing a loss as an absence of one.
    old_hidden = "\n".join([stamp(20000, pipe=False), stamp(900), stamp(400)])
    lost = compare("bm-w", old_hidden, "worktree", state, hb, now, mod)
    eq("an unread row outside the window is classed as a lost row, not as no cost",
       lost["class"], C_LOST)
    eq("and the numbers it does not move are named by their absence",
       (lost["rounds_24h_delta"], lost["worst_gap_7d_delta_min"]), (0, 0.0))
    eq("while the row count still moves",
       lost["rows_invisible_to_the_shipped_reader"], 1)
    mislabelled = json.loads(json.dumps(lost))
    mislabelled["class"] = C_NOTHING
    eq("calling that ledger free is refused by the face check",
       bool([x for x in face_problems({"rows": [mislabelled], "summary": summarise([mislabelled]),
                                       "verdict": _verdict(summarise([mislabelled])),
                                       "verdict_line": _verdict_line(summarise([mislabelled])),
                                       "evidence_cutoff": CUTOFF}) if "costs nothing" in x]),
       True)

    # S4c a published verdict face with no timestamp cannot be aged
    no_ts = compare("bm-v", plain, "worktree", state, hb, now, mod, {"verdict": "ALIVE"})
    eq("a published face without a timestamp is counted, not assumed fresh",
       no_ts["published_face"]["has_a_timestamp"], False)
    with_ts = compare("bm-v", plain, "worktree", state, hb, now, mod,
                      {"verdict": "ALIVE", "generated": now.isoformat()})
    eq("a timestamped face is not counted against it",
       with_ts["published_face"]["has_a_timestamp"], True)
    eq("and an agreement is published only when the verdicts match",
       (no_ts["published_face"]["agrees_with_the_strict_recompute"],
        compare("bm-v", plain, "worktree", state, hb, now, mod,
                {"verdict": "DEAD"})["published_face"]["agrees_with_the_strict_recompute"]),
       (True, False))

    # S5 summaries re-derive and the verdict names the count
    rows = [flip, moves, same]
    s = summarise(rows)
    eq("the summary counts one flip", s["machines_that_flip"], 1)
    eq("the summary counts one disclosure move", s["machines_whose_disclosure_moves"], 1)
    eq("the two totals difference is published as invisible rows",
       s["rows_invisible_to_the_shipped_reader"],
       s["wide_rows_total"] - s["strict_rows_total"])
    eq("a flip outranks a disclosure move in the verdict",
       "calls_1_of_3_machines_dead" in _verdict(s), True)
    eq("the verdict line reports the invisible rows inside the alive window",
       "1 rows inside the alive window" in _verdict_line(s), True)

    # S6 the thresholds are the shipped module's, not re-declared here
    eq("thresholds are inherited, not redefined",
       (mod.ALIVE_MIN, mod.DEAD_MIN, mod.GAP_MIN), (25.0, 360.0, 90.0))

    # S7 face checks refuse a doctored summary and a doctored class
    face = {"rows": rows, "summary": dict(s, machines_that_flip=3),
            "verdict": _verdict(s), "verdict_line": _verdict_line(s),
            "evidence_cutoff": CUTOFF}
    eq("a summary that does not re-derive is refused", bool(face_problems(face)), True)
    good = {"rows": rows, "summary": s, "verdict": _verdict(s),
            "verdict_line": _verdict_line(s), "evidence_cutoff": CUTOFF}
    eq("a clean face passes", face_problems(good), [])
    doctored = json.loads(json.dumps(good))
    doctored["rows"][2]["class"] = C_FLIP
    eq("a flip class that the verdicts do not support is refused",
       bool(face_problems(doctored)), True)

    failed = [n for n, g, _ in ok if not g]
    for n, g, detail in ok:
        print("  %s %s%s" % ("PASS" if g else "FAIL", n, "" if g else "  <- " + detail))
    print("selftest %d/%d" % (len(ok) - len(failed), len(ok)))
    return 0 if not failed else 1


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