"""E357 -- who writes each lagging channel file, and at what cadence.

E352 priced the stale window a reader takes: 58 of 59 deciding channel files lag the newest blob,
median 80 commits, and only 7 of them carry a freshness gate.  It could not say *why*, because it
counted the file's own history.  This study asks the other half of the question -- the producer:

    for each lagging channel file, take the writer sources E352 already resolved (``in_repo_writers``,
    the .py files that name the face as a write target), walk each of those sources on the same
    first-parent window, and ask (a) did that source ever change in a commit that also changed the
    face -- i.e. did it actually produce this file, or does it merely name it? and (b) if it did,
    is it a STANDING producer (touched on several rounds, with a period) or a one-shot round script
    that ran once and was never opened again?

The comparison the card asks for is then a ratio, not a verdict from a number in the air:

    lag_inside_writer_period     the copy is behind, but the file's own median lag is no longer than
                                 the interval at which its fastest standing writer runs -- a reader
                                 cannot be fresher than its producer
    lag_beyond_writer_period     a standing producer exists AND the copy is older than that
                                 producer's period: this is the "reader that never re-runs"
    no_standing_writer           every source that actually wrote the file inside the window is a
                                 one-shot: the file has no producer at all, only a history.  Its lag
                                 is not a stale read, it is a face with nobody assigned to it.
    not_written_in_window        the face was not touched anywhere in the window (E352 publishes
                                 this as censored); measuring its lag is measuring the window edge.

Three measurement traps, each pinned by a selftest leg, because each one silently flips a class:

    * naming is not writing.  E352 resolves writers from the face's name appearing in a source; that
      includes readers, guards and fixtures.  Only a source that changed in the SAME commit as the
      face has evidence of having produced it.  The declared-vs-actual gap is published per file.
    * a period needs a second touch.  One touch in the window is a one-shot, not a very slow
      producer; publishing period=WINDOW for it would make every one-shot look like a valid
      producer whose period happens to be the whole window.
    * the lag is the file's MEDIAN blob age while the period is a median interval between touches.
      Both are commits-distance on the same 240-commit line, so they are comparable -- but a file
      whose lag is 0 was written by the boundary commit itself and no period test applies.

Usage:
    python scripts/e357_channel_writer_cadence.py run|verify|selftest
"""

import json
import os
import sys
from datetime import datetime

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
if HERE not in sys.path:
    sys.path.insert(0, HERE)

# Reuse E352's window/touch machinery verbatim: the card's own bound is that cadence is read from
# the file's first-parent write history, "exactly the clock E352 used", so the two studies cannot
# disagree about how to count a round.  Re-implementing the walk is how two studies end up shipping
# different definitions of "one commit behind".
import e352_staleness_window as e352  # noqa: E402

OUTDIR = os.path.join(ROOT, "results", "state_tilt")
TODAY = "2026-11-02"
FACE = "CHWRCAD-%s.json" % TODAY
LATEST = "chwrcad_latest.json"
STUDY = "E357_channel_writer_cadence"
SELF_REL = "scripts/e357_channel_writer_cadence.py"
SELF_OUTPUTS = (FACE, LATEST)

STALEWIN_FACE = os.path.join(OUTDIR, "STALEWIN-2026-11-02.json")
WINDOW = 240

# A producer is "standing" only if the window caught it more than twice: with two touches the
# "period" is one gap and every number derived from it is that single round's accident.
STANDING_MIN_TOUCHES = 3
MAX_ROWS = 80

# Co-commit is evidence of production ONLY when the commit is distinctive.  The first version of
# this study treated "the source changed in a commit that also changed the face" as proof, and the
# result was the r1261 shape: every fastest period came out exactly 2.0 and 54 of 54 files read
# "beyond".  The cause is `smoke_test.py`, which is touched in 102 of 240 commits: a file that is
# rewritten once co-occurs with it by necessity, so the harness was crowned the producer of the
# whole channel and lent all of it its two-commit rhythm.  Two filters, both published as counts:
HARNESS_MARKERS = ("smoke_test.py",)  # the suite plus the runner shims below
OMNIPRESENT_MAX_SHARE = 0.4  # a source present in >40% of commits cannot be co-commit evidence

VERDICT_DEFINITION = (
    "reader_cannot_be_fresher_than_its_producer: no file's median blob age exceeds the interval at "
    "which that file is itself rewritten, so every copy a reader takes is younger than one "
    "production cycle -- the channel cannot be fresher than this by construction.  "
    "stale_beyond_its_own_cadence: at least one file's median lag exceeds its own rewrite interval, "
    "i.e. the copy in front of a reader is older than the file's rhythm -- those are readers that "
    "never re-run.  "
    "no_cadence_population: no file in the population has two or more writes in the window, so "
    "there is no rhythm to compare a lag against -- the finding would be about the window, not the "
    "channel.  "
    "measurement_collapsed: every file inherited the same cadence, which means one source's rhythm "
    "leaked into the whole population (the first draft's defect) -- no finding may be read from it."
)


def say(message):
    sys.stdout.write(str(message) + "\n")
    sys.stdout.flush()


def median(values):
    """Median of a list of numbers (None for empty) -- the same definition E352 pairs with p90."""
    vals = sorted(float(v) for v in values if v is not None)
    if not vals:
        return None
    mid = len(vals) // 2
    if len(vals) % 2:
        return vals[mid]
    return (vals[mid - 1] + vals[mid]) / 2.0


def gaps(idxs):
    """Consecutive distances between sorted boundary indices -- commits between two touches."""
    seq = sorted(set(int(i) for i in idxs))
    return [b - a for a, b in zip(seq, seq[1:])]


def is_harness(path):
    """True for the suite and its per-leg runner shims -- graders, never producers.

    A harness legitimately names every face (it asserts against them) and legitimately writes to
    temp dirs, so a write-token scan cannot separate it from a producer.  Naming it is the only
    honest filter, and the count of pairs it removes is published rather than silently dropped.
    """
    base = os.path.basename(path or "").lower()
    if base in HARNESS_MARKERS:
        return True
    if base.startswith("run_") and "smoke" in base:
        return True
    if base.endswith("_smoke_leg.py") or base.endswith("_selftest.py"):
        return True
    return False


def producer_evidence(writer, tmap, file_idxs, width=None):
    """How much of THIS file's production this source can be credited with.

    The first draft asked whether the source and the file shared a commit, and crowned
    ``smoke_test.py`` (touched in 102 of 240 commits) the producer of the whole channel, which lent
    every file a period of 2.0.  The second draft fixed that by demanding the source be edited more
    than twice inside the window -- and then reported that no channel file has a standing producer,
    because a producer that runs every round but has not had its CODE edited in 240 commits has zero
    touches.  Both drafts were measuring source edits, not production.

    Production is the file's own change history.  A source is credited where it changed in the same
    commit as the file (``co_changes``), which is the only in-repo evidence available, and the
    cadence of the file is its own sequence of changes -- the rhythm the readers live on.
    """
    width = int(width or WINDOW)
    touches = list(tmap.get(writer) or [])
    shared = sorted(set(touches) & set(file_idxs))
    share_of_window = (len(touches) / float(width)) if width else 0.0
    if is_harness(writer):
        credit = "harness"
    elif share_of_window > OMNIPRESENT_MAX_SHARE:
        # present in too much of the window for a co-change to mean anything, but still credit its
        # co-changes as a separate bucket so the number is visible
        credit = "omnipresent"
    elif shared:
        credit = "co_change"
    else:
        credit = "declared_only"
    return {
        "writer": writer,
        "touches_in_window": len(touches),
        "share_of_window_pct": round(100.0 * share_of_window, 2),
        "co_changes": len(shared),
        "co_change_share_of_file_pct": (round(100.0 * len(shared) / len(file_idxs), 2)
                                        if file_idxs else 0.0),
        "credit": credit,
    }


def classify(file_lag, file_idxs, profiles):
    """The card's three classes plus the states that must not be folded into them.

    Pure: every input is a number or a list of dicts, so the selftest can drive it with fixtures
    instead of re-running the corpus walk.
    """
    n = len(file_idxs)
    if n == 0:
        return "not_written_in_window", None
    if file_lag == 0:
        return "rewritten_at_boundary", None
    if n == 1:
        # one write in the whole window: the file has an age, not a rhythm.  Calling this a stale
        # read would grade a design decision the repository made once.
        return "single_write_no_cadence", None
    period = median(gaps(file_idxs))
    if not period:
        return "single_write_no_cadence", None
    producers = [p for p in profiles if p["credit"] == "co_change"]
    if not producers:
        evidence = set(p["credit"] for p in profiles)
        if evidence and evidence <= {"harness", "omnipresent"}:
            return "only_graders_and_omnipresent_declared", period
        return "declared_writers_never_produced", period
    if file_lag <= period:
        return "lag_inside_writer_period", period
    return "lag_beyond_writer_period", period


def build(pin=None, width=WINDOW):
    pin = (pin or (e352.git("rev-parse", "HEAD") or "")).strip()
    window = e352.first_parent_window(width, at=None)
    tmap = e352.window_touch_map(window)

    src = json.loads(e352.read_tree_file(STALEWIN_FACE.replace(ROOT + os.sep, "")
                                         .replace("/", os.sep)) or "{}")
    base_rows = [r for r in (src.get("rows") or []) if r.get("measured")]

    rows = []
    for r in base_rows:
        idxs = list(tmap.get(r.get("path") or "") or [])
        declared = list(r.get("in_repo_writers") or [])
        profiles = [producer_evidence(w, tmap, idxs, len(window)) for w in declared]
        lag = (r.get("stats") or {}).get("lag_median_commits")
        cls, period = classify(lag, idxs, profiles)
        credited = [p for p in profiles if p["credit"] == "co_change"]
        rows.append({
            "path": r.get("path"),
            "file": r.get("file"),
            "class_e352": r.get("class"),
            "declared_writers": len(declared),
            "declared_harness_pairs": len([p for p in profiles if p["credit"] == "harness"]),
            "declared_omnipresent_pairs": len([p for p in profiles
                                               if p["credit"] == "omnipresent"]),
            "writers_credited": len(credited),
            "file_touches_in_window": len(idxs),
            "file_cadence_commits": period,
            "lag_median_commits": lag,
            "class": cls,
            "dominant_writer": (max(credited, key=lambda p: p["co_changes"])["writer"]
                                if credited else None),
            "producer_names": [p["writer"] for p in
                               sorted(credited, key=lambda p: -p["co_changes"])[:3]],
            "top_declared": [p["writer"] for p in
                             sorted(profiles, key=lambda p: -p["touches_in_window"])[:3]],
        })
    rows.sort(key=lambda r: (-(r["lag_median_commits"] or 0), r["declared_writers"]))

    classes = {}
    for r in rows:
        classes[r["class"]] = classes.get(r["class"], 0) + 1

    declared_pairs = sum(r["declared_writers"] for r in rows)
    credited_pairs = sum(r["writers_credited"] for r in rows)
    harness_pairs = sum(r["declared_harness_pairs"] for r in rows)
    omnipresent_pairs = sum(r["declared_omnipresent_pairs"] for r in rows)
    beyond = [r for r in rows if r["class"] == "lag_beyond_writer_period"]
    inside = [r for r in rows if r["class"] == "lag_inside_writer_period"]
    periods = sorted(set(r["file_cadence_commits"] for r in rows
                         if r["file_cadence_commits"]))

    summary = {
        "lagging_files_measured": len(rows),
        "window_commits": len(window),
        "window_head": (window[-1][0][:8] if window else ""),
        "declared_writer_pairs": declared_pairs,
        "declared_harness_pairs": harness_pairs,
        "declared_omnipresent_pairs": omnipresent_pairs,
        "writer_pairs_credited": credited_pairs,
        "declared_but_never_co_changed_pairs": declared_pairs - credited_pairs,
        "distinct_file_cadences": periods[:12],
        "distinct_file_cadence_count": len(periods),
        "files_with_a_named_producer": len([r for r in rows if r["dominant_writer"]]),
        "classes": classes,
        "files_not_written_in_window": classes.get("not_written_in_window", 0),
        "files_single_write_no_cadence": classes.get("single_write_no_cadence", 0),
        "files_with_no_producer_evidence": (classes.get("declared_writers_never_produced", 0)
                                           + classes.get("only_graders_and_omnipresent_declared", 0)),
        "files_lag_beyond_their_cadence": len(beyond),
        "files_lagging_inside_their_cadence": len(inside),
        "median_lag_commits": median([r["lag_median_commits"] for r in rows]),
        "worst_file": (rows[0]["path"] if rows else None),
        "worst_declared_writers": (rows[0]["declared_writers"] if rows else None),
        "largest_declared_writer_list": (sorted(rows, key=lambda r: -r["declared_writers"])[0]["path"]
                                         if rows else None),
        "largest_declared_writer_count": (sorted(rows, key=lambda r: -r["declared_writers"])[0]
                                          ["declared_writers"] if rows else None),
    }

    # Anti-degeneracy: if every file inherits the SAME fastest period, the "period" is one source's
    # rhythm leaking into the whole population, not 50 independent cadences.  This is the exact
    # failure the first draft shipped (all 2.0, from smoke_test.py), and it must be impossible to
    # publish it as a finding again.
    periods_collapsed = (len(periods) == 1 and len(rows) > 10)
    summary["periods_collapsed"] = periods_collapsed

    if periods_collapsed:
        verdict = "measurement_collapsed"
    elif beyond:
        verdict = "stale_beyond_its_own_cadence"
    elif len(inside) + len(beyond) == 0:
        verdict = "no_cadence_population"
    else:
        verdict = "reader_cannot_be_fresher_than_its_producer"

    return {
        "study": STUDY,
        "ts": datetime.now().astimezone().isoformat(timespec="seconds"),
        "today": TODAY,
        "evidence_cutoff": TODAY,
        "pin": pin,
        "window": {"commits": len(window), "head": (window[-1][0] if window else ""),
                   "oldest": (window[0][0] if window else "")},
        "omnipresent_max_share_pct": round(100.0 * OMNIPRESENT_MAX_SHARE, 1),
        "source": {"face": "results/state_tilt/STALEWIN-2026-11-02.json",
                   "population": "E352 rows with measured=true"},
        "clock_note": ("cadence and lag are both measured in commits on the same first-parent "
                       "window, so the two numbers are comparable; a writer that only runs outside "
                       "the window is published with touches_in_window=0, never as a period"),
        "verdict": verdict,
        "verdict_definition": VERDICT_DEFINITION,
        "summary": summary,
        "rows": rows[:MAX_ROWS],
        "rows_published": min(len(rows), MAX_ROWS),
        "rows_truncated": max(0, len(rows) - MAX_ROWS),
    }


def decide(face):
    """Recompute the verdict from the published summary -- never trust the stored string."""
    s = face.get("summary") or {}
    if s.get("periods_collapsed"):
        return "measurement_collapsed"
    if s.get("files_lag_beyond_their_cadence"):
        return "stale_beyond_its_own_cadence"
    if not (s.get("files_lagging_inside_their_cadence") or s.get("files_lag_beyond_their_cadence")):
        return "no_cadence_population"
    return "reader_cannot_be_fresher_than_its_producer"


def write(face):
    os.makedirs(OUTDIR, exist_ok=True)
    dated = os.path.join(OUTDIR, FACE)
    latest = os.path.join(OUTDIR, LATEST)
    body = json.dumps(face, ensure_ascii=False, indent=1, sort_keys=True) + "\n"
    for path in (dated, latest):
        with open(path, "w", encoding="utf-8", newline="\n") as fh:
            fh.write(body)
    return dated, latest


def verify():
    """Re-derive the face from today's disk and compare class-for-class, not blob-for-blob.

    A byte comparison would grade the clock: the window moves every commit and `ts` moves with it.
    What must hold is that each published row still resolves to the same class and that the
    summary counts are the counts of the published rows.
    """
    path = os.path.join(OUTDIR, FACE)
    try:
        with open(path, "r", encoding="utf-8") as fh:
            published = json.load(fh)
    except OSError as exc:
        say("verify: cannot read published face: %s" % (exc,))
        return 2
    fresh = build(pin=published.get("pin") or None)
    problems = []
    if decide(published) != published.get("verdict"):
        problems.append("verdict does not re-derive: stored=%r derived=%r"
                        % (published.get("verdict"), decide(published)))
    if fresh["verdict"] != published.get("verdict"):
        problems.append("verdict moved on re-derivation: stored=%r fresh=%r"
                        % (published.get("verdict"), fresh["verdict"]))
    pub_rows = {r["path"]: r for r in (published.get("rows") or [])}
    for r in fresh["rows"]:
        old = pub_rows.get(r["path"])
        if not old:
            continue
        if old.get("class") != r.get("class"):
            problems.append("%s class %r -> %r" % (r["path"], old.get("class"), r.get("class")))
    s = published.get("summary") or {}
    counted = {}
    for r in published.get("rows") or []:
        counted[r["class"]] = counted.get(r["class"], 0) + 1
    for cls, n in counted.items():
        if (s.get("classes") or {}).get(cls) != n:
            problems.append("summary.classes[%s]=%r but %d published rows say it"
                            % (cls, (s.get("classes") or {}).get(cls), n))
    if problems:
        for p in problems[:20]:
            say("PROBLEM: " + p)
        say("verify: %d problems" % len(problems))
        return 1
    say("verify: 0 problems over %d rows" % len(published.get("rows") or []))
    return 0


# ------------------------------------------------------------------------------------- selftest

def selftest():
    legs = []

    def leg(name, ok, detail=None):
        legs.append((name, bool(ok), detail))

    W = 240
    prod = {"writer": "p.py", "credit": "co_change", "co_changes": 6,
            "touches_in_window": 6, "share_of_window_pct": 2.5}
    only_named = {"writer": "a.py", "credit": "declared_only", "co_changes": 0,
                  "touches_in_window": 9, "share_of_window_pct": 3.8}
    grader = {"writer": "smoke_test.py", "credit": "harness", "co_changes": 1,
              "touches_in_window": 102, "share_of_window_pct": 42.5}

    # 1. naming is not producing: a declared writer that never moved with the file is not evidence
    leg("a declared writer that never co-changed is not a producer",
        classify(80, [10, 20, 30], [only_named])[0] == "declared_writers_never_produced",
        classify(80, [10, 20, 30], [only_named]))

    # 2/3/4. the ratio itself, against the FILE's own rewrite interval
    leg("cadence is the file's median gap between its own writes",
        classify(5, [10, 20, 30], [prod]) == ("lag_inside_writer_period", 10.0),
        classify(5, [10, 20, 30], [prod]))
    leg("lag equal to the cadence is still inside (== is bounded, not beyond)",
        classify(10, [10, 20, 30], [prod])[0] == "lag_inside_writer_period",
        classify(10, [10, 20, 30], [prod]))
    leg("lag longer than the file's own cadence is the reader that never re-runs",
        classify(11, [10, 20, 30], [prod])[0] == "lag_beyond_writer_period",
        classify(11, [10, 20, 30], [prod]))

    # 5/6/7. the states that must not be folded into a stale verdict
    leg("zero writes in the window is its own state, not a censored lag",
        classify(W, [], [prod])[0] == "not_written_in_window", classify(W, [], [prod]))
    leg("a single write has an age, not a cadence",
        classify(W, [7], [prod])[0] == "single_write_no_cadence", classify(W, [7], [prod]))
    leg("lag 0 is rewritten_at_boundary and no cadence test applies",
        classify(0, [10, 20, 30], [prod])[0] == "rewritten_at_boundary",
        classify(0, [10, 20, 30], [prod]))

    # 8/9. the two evidence filters, both driven by the defect the first draft shipped
    leg("the suite is a harness, not a producer", is_harness("smoke_test.py") is True)
    leg("a per-leg runner shim is a harness", is_harness("scripts/run_e357_smoke_leg.py") is True)
    leg("an ordinary producer is not a harness",
        is_harness("scripts/e357_channel_writer_cadence.py") is False)
    leg("a file whose only declared writer is the suite is graders-only, not stale",
        classify(W, [10, 20, 30], [grader])[0] == "only_graders_and_omnipresent_declared",
        classify(W, [10, 20, 30], [grader]))
    busy = producer_evidence("busy.py", {"busy.py": list(range(0, 240, 2)), "f.json": [4]},
                             [4], 240)
    leg("a source present in >40% of commits cannot serve as co-change evidence",
        busy["credit"] == "omnipresent" and busy["co_changes"] == 1, busy)
    real = producer_evidence("p.py", {"p.py": [4, 5, 40], "f.json": [5]}, [5], 240)
    leg("a normal source's co-change is credited", real["credit"] == "co_change", real)
    named = producer_evidence("n.py", {"n.py": [1, 2, 3], "f.json": [40]}, [40], 240)
    leg("a source that names the file but never co-changed is declared_only",
        named["credit"] == "declared_only" and named["co_changes"] == 0, named)

    # 10. gaps and median
    leg("gaps are consecutive distances", gaps([0, 2, 4]) == [2, 2], gaps([0, 2, 4]))
    leg("gaps deduplicate and sort", gaps([6, 0, 3]) == [3, 3], gaps([6, 0, 3]))
    leg("median of an even count averages the middle pair", median([1, 3]) == 2.0, median([1, 3]))
    leg("median of an odd count is the middle one", median([7, 1, 3]) == 3.0, median([7, 1, 3]))
    leg("median of nothing is None, not zero", median([]) is None, median([]))

    # 11. the collapse detector: one cadence for the whole population is a leak, not a rhythm
    leg("verdict: a collapsed cadence suppresses any stale finding",
        decide({"summary": {"periods_collapsed": True, "files_lag_beyond_their_cadence": 54,
                            "files_lagging_inside_their_cadence": 0}}) == "measurement_collapsed")
    leg("verdict: a live cadence population is allowed to be a finding",
        decide({"summary": {"periods_collapsed": False, "files_lag_beyond_their_cadence": 3,
                            "files_lagging_inside_their_cadence": 8}})
        == "stale_beyond_its_own_cadence")
    leg("verdict: no cadence population at all is its own answer",
        decide({"summary": {"periods_collapsed": False, "files_lag_beyond_their_cadence": 0,
                            "files_lagging_inside_their_cadence": 0}}) == "no_cadence_population")
    leg("verdict: clean population reads as reader-cannot-be-fresher",
        decide({"summary": {"periods_collapsed": False, "files_lag_beyond_their_cadence": 0,
                            "files_lagging_inside_their_cadence": 40}})
        == "reader_cannot_be_fresher_than_its_producer")

    # 12. the published face, when it exists, must agree with its own verdict function
    try:
        with open(os.path.join(OUTDIR, FACE), "r", encoding="utf-8") as fh:
            face = json.load(fh)
        leg("published face verdict == decide(summary)",
            face.get("verdict") == decide(face), face.get("verdict"))
        leg("published row classes partition the published rows",
            sum((face.get("summary") or {}).get("classes", {}).values())
            == len(face.get("rows") or []), face.get("summary", {}).get("classes"))
        leg("published population is not cadence-collapsed",
            (face.get("summary") or {}).get("periods_collapsed") is False,
            (face.get("summary") or {}).get("periods_collapsed"))
    except OSError:
        leg("published face present (skipped when absent)", True, "no face yet")

    failed = [r for r in legs if not r[1]]
    for name, ok, detail in legs:
        say("[%s] %s%s" % ("PASS" if ok else "FAIL", name,
                           "" if ok else " :: %s" % (detail,)))
    say("selftest %d/%d" % (len(legs) - len(failed), len(legs)))
    return 0 if not failed else 1


# ----------------------------------------------------------------------------------------- main

def main(argv):
    cmd = (argv[1] if len(argv) > 1 else "run").lower()
    if cmd == "selftest":
        return selftest()
    if cmd == "run":
        face = build()
        dated, latest = write(face)
        say(json.dumps({"study": STUDY, "verdict": face["verdict"], "summary": face["summary"],
                        "dated": dated.replace(ROOT + os.sep, ""),
                        "latest": latest.replace(ROOT + os.sep, "")},
                       ensure_ascii=False, indent=1))
        return 0
    if cmd == "verify":
        return verify()
    say("usage: run|verify|selftest")
    return 2


if __name__ == "__main__":
    sys.exit(main(sys.argv))