# -*- coding: utf-8 -*-
"""E580 -- whether a judged verdict face can be aged at all from its own bytes.

Every published face under ``results/`` that carries a top-level ``verdict`` answers a question
about some period.  A reader who wants to know whether that answer is still current has only the
face itself, so this study asks each face one thing: *can your own bytes say what data you are
about?*  Three date signals are separated, because they are three different claims:

  cutoff  a declaration about the DATA  (evidence_cutoff / cutoff / asof / panel_cutoff ...)
          -> its age is the age of the answer; only this can age a verdict
  build   a declaration about the FILE  (generated / ts / updated / built_at ...)
          -> a build time says when someone last wrote the file, never what it covers; a face
             rebuilt from the same frozen panel this morning is still a verdict about that panel
  mtime   the checkout time of the working tree, published for completeness only.  r1472/E453
          measured this tree's mtime floor at ~21 days, so mtime is not evidence of freshness and
          is never used to age anything here.

Classes (first match wins, published per face):

  aged_by_its_own_cutoff                    a cutoff field parses -> the verdict is ageable
  the_cutoff_is_in_the_future               a cutoff parses but sits after today
  declares_a_cutoff_that_does_not_parse     a cutoff-shaped field exists, no value parses
  only_a_build_time                         a build time parses, no cutoff at all
  the_build_time_does_not_parse             a build field exists but holds a non-date word
                                            (e.g. generated = "deterministic")
  no_date_signal_at_all                     neither shape present

The refused inference is the point of the face: ``fresh`` is never printed for a face whose bytes
cannot state a data date, whatever its mtime says.

Usage: python scripts/e580_face_age.py [build|check|verify|selftest]
"""
import glob
import io
import json
import os
import re
import sys
from datetime import date, datetime

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
OUTDIR = os.path.join(ROOT, "results", "state_tilt")
CUTOFF = "2026-11-09"
STUDY = "E580_face_age"
SELF_FACES = ("FACEAGED-", "faceaged_latest.json")

C_AGED = "aged_by_its_own_cutoff"
C_FUTURE = "the_cutoff_is_in_the_future"
C_UNPARSEABLE = "declares_a_cutoff_that_does_not_parse"
C_BUILD = "only_a_build_time"
C_BUILD_BAD = "the_build_time_does_not_parse"
C_NONE = "no_date_signal_at_all"

#: fields that make a claim about the DATA.  Ordered: the first present one is the binding claim.
CUTOFF_KEYS = (
    "evidence_cutoff", "data_cutoff", "panel_cutoff", "bar_cutoff", "cutoff", "asof", "as_of",
    "asof_date", "data_asof", "panel_cutoff_date",
)
#: fields that make a claim about the FILE.
BUILD_KEYS = (
    "generated", "generated_at", "ts", "updated", "updated_at", "built_at", "built",
    "clock_read", "read_at", "written_at", "run_at",
)

ISO_RE = re.compile(r"^(\d{4})-(\d{2})-(\d{2})(?:[T ](\d{2}):(\d{2})(?::(\d{2}))?)?")
COMPACT_RE = re.compile(r"^(\d{4})(\d{2})(\d{2})$")
MONTH_RE = re.compile(r"^(\d{4})-(\d{2})$")

STALE_DAYS = 30
VERY_STALE_DAYS = 365


# --------------------------------------------------------------------------- #
# parsing -- pure, takes a value, returns (kind, value)
# --------------------------------------------------------------------------- #

def parse_stamp(raw):
    """Parse the date shapes this repo actually writes.  Returns (newest_date, how) or (None, why)."""
    if isinstance(raw, bool) or raw is None:
        return None, "not_a_date_value"
    if isinstance(raw, (int, float)):
        if raw >= 1_000_000_000:                      # unix seconds
            return datetime.fromtimestamp(raw).date(), "unix_seconds"
        return None, "a_number_that_is_not_a_unix_time"
    if not isinstance(raw, str):
        return None, "not_a_date_value"
    text = raw.strip()
    if not text:
        return None, "empty_string"
    m = ISO_RE.match(text)
    if m:
        y, mo, d = int(m.group(1)), int(m.group(2)), int(m.group(3))
        try:
            return date(y, mo, d), "iso_date" if not m.group(4) else "iso_datetime"
        except ValueError:
            return None, "iso_shaped_but_not_a_real_date"
    m = COMPACT_RE.match(text)
    if m:
        try:
            return date(int(m.group(1)), int(m.group(2)), int(m.group(3))), "compact_yyyymmdd"
        except ValueError:
            return None, "compact_shaped_but_not_a_real_date"
    m = MONTH_RE.match(text)
    if m:
        y, mo = int(m.group(1)), int(m.group(2))
        if 1 <= mo <= 12:
            return date(y, mo, 1), "month_only_resolved_to_the_first"
        return None, "month_shaped_but_out_of_range"
    return None, "no_known_date_shape"


def _first(face, keys):
    """The first present key among ``keys`` with its raw value (presence is not truthiness)."""
    for k in keys:
        if k in face:
            return k, face.get(k)
    return None, None


def classify(face, today):
    """One face's date evidence.  Pure: today is passed in, nothing is read from the clock."""
    ck, cval = _first(face, CUTOFF_KEYS)
    bk, bval = _first(face, BUILD_KEYS)
    out = {
        "cutoff_field": ck,
        "cutoff_raw": None if cval is None else str(cval)[:40],
        "cutoff_date": None,
        "cutoff_how": None,
        "cutoff_age_days": None,
        "build_field": bk,
        "build_raw": None if bval is None else str(bval)[:40],
        "build_date": None,
        "build_how": None,
        "build_age_days": None,
    }
    if ck is not None:
        parsed, how = parse_stamp(cval)
        out["cutoff_how"] = how
        if parsed is not None:
            out["cutoff_date"] = parsed.isoformat()
            out["cutoff_age_days"] = (today - parsed).days
    if bk is not None:
        parsed, how = parse_stamp(bval)
        out["build_how"] = how
        if parsed is not None:
            out["build_date"] = parsed.isoformat()
            out["build_age_days"] = (today - parsed).days

    if ck is None:
        # a present build field holding a word like "deterministic" is a claim about the file
        # that cannot be aged -- a different fact from carrying no date field at all
        if out["build_date"]:
            out["class"] = C_BUILD
        elif bk is not None:
            out["class"] = C_BUILD_BAD
        else:
            out["class"] = C_NONE
    elif out["cutoff_date"] is None:
        out["class"] = C_UNPARSEABLE
    elif out["cutoff_age_days"] is not None and out["cutoff_age_days"] < 0:
        out["class"] = C_FUTURE
    else:
        out["class"] = C_AGED
    out["ageable"] = out["class"] == C_AGED
    return out


def freshness(age_days):
    """A freshness word exists only for an ageable face.  None otherwise -- never 'fresh'."""
    if age_days is None:
        return None
    if age_days <= 1:
        return "today"
    if age_days <= 7:
        return "this_week"
    if age_days <= STALE_DAYS:
        return "this_month"
    if age_days <= VERY_STALE_DAYS:
        return "stale"
    return "very_stale"


# --------------------------------------------------------------------------- #
# population
# --------------------------------------------------------------------------- #

def _excluded(name):
    base = os.path.basename(name)
    return any(base.startswith(p) for p in SELF_FACES)


def population(root=None):
    """Every results/**/*.json with a top-level verdict, minus this study's own faces."""
    root = root or ROOT
    rows = []
    skipped_self = 0
    unreadable = 0
    for path in sorted(glob.glob(os.path.join(root, "results", "**", "*.json"), recursive=True)):
        if _excluded(path):
            skipped_self += 1
            continue
        try:
            face = json.load(io.open(path, encoding="utf-8"))
        except Exception:
            unreadable += 1
            continue
        if not isinstance(face, dict) or "verdict" not in face:
            continue
        rows.append((os.path.relpath(path, root).replace("\\", "/"), face))
    return rows, skipped_self, unreadable


def mtime_floor(root=None):
    """How usable file mtimes are at all (r1472/E453 law) -- published, never used to age a face."""
    root = root or ROOT
    days = {}
    total = 0
    for path in glob.glob(os.path.join(root, "results", "**", "*.json"), recursive=True):
        try:
            day = datetime.fromtimestamp(os.path.getmtime(path)).date().isoformat()
        except OSError:
            continue
        days[day] = days.get(day, 0) + 1
        total += 1
    if not total:
        return {"files": 0, "distinct_mtime_days": 0, "oldest": None, "newest": None,
                "max_identifiable_age_days": 0, "usable_as_freshness_evidence": False}
    ordered = sorted(days)
    return {
        "files": total,
        "distinct_mtime_days": len(ordered),
        "oldest": ordered[0],
        "newest": ordered[-1],
        "busiest_day": max(days.items(), key=lambda kv: kv[1])[0],
        "busiest_day_files": max(days.values()),
        # r1472/E453: this tree's mtimes are one bulk checkout, so an age above the span between
        # the oldest and newest mtime is not identifiable from them at all
        "max_identifiable_age_days": (date.fromisoformat(ordered[-1])
                                      - date.fromisoformat(ordered[0])).days,
        "usable_as_freshness_evidence": (date.fromisoformat(ordered[-1])
                                         - date.fromisoformat(ordered[0])).days >= STALE_DAYS,
    }


# --------------------------------------------------------------------------- #
# rows, summary, verdict
# --------------------------------------------------------------------------- #

def row_for(rel, face, today):
    c = classify(face, today)
    verdict = face.get("verdict")
    verdict_text = verdict if isinstance(verdict, str) else json.dumps(verdict, ensure_ascii=False)
    r = {"path": rel, "class": c["class"], "ageable": c["ageable"],
         "verdict_text": verdict_text[:120], "verdict_type": type(verdict).__name__}
    r.update({k: v for k, v in c.items() if k not in ("class", "ageable")})
    r["freshness"] = freshness(c["cutoff_age_days"]) if c["ageable"] else None
    return r


def summarise(rows):
    def count(pred):
        return len([r for r in rows if pred(r)])

    aged = [r for r in rows if r["ageable"]]
    ages = sorted(r["cutoff_age_days"] for r in aged)
    s = {
        "faces": len(rows),
        "aged_by_their_own_cutoff": count(lambda r: r["class"] == C_AGED),
        "cutoff_in_the_future": count(lambda r: r["class"] == C_FUTURE),
        "declares_a_cutoff_that_does_not_parse": count(lambda r: r["class"] == C_UNPARSEABLE),
        "only_a_build_time": count(lambda r: r["class"] == C_BUILD),
        "build_time_does_not_parse": count(lambda r: r["class"] == C_BUILD_BAD),
        "no_date_signal_at_all": count(lambda r: r["class"] == C_NONE),
        "faces_a_reader_cannot_age": count(lambda r: not r["ageable"]),
        "faces_carrying_a_cutoff_shaped_field_at_all": count(
            lambda r: r["cutoff_field"] is not None),
        "faces_carrying_a_build_time_at_all": count(lambda r: r["build_field"] is not None),
        "faces_whose_cutoff_does_not_parse": count(
            lambda r: r["cutoff_field"] is not None and r["cutoff_date"] is None),
        "cutoff_age_days_median": ages[len(ages) // 2] if ages else None,
        "cutoff_age_days_max": ages[-1] if ages else None,
        "cutoff_age_days_min": ages[0] if ages else None,
        "aged_faces_stale_beyond_30d": count(
            lambda r: r["ageable"] and r["cutoff_age_days"] > STALE_DAYS),
        "aged_faces_stale_beyond_365d": count(
            lambda r: r["ageable"] and r["cutoff_age_days"] > VERY_STALE_DAYS),
        "aged_faces_declaring_today_or_yesterday": count(
            lambda r: r["ageable"] and r["cutoff_age_days"] <= 1),
        "build_time_is_newer_than_the_cutoff": count(
            lambda r: r["ageable"] and r["build_date"] and r["build_age_days"] is not None
            and r["build_age_days"] < r["cutoff_age_days"]),
    }
    return s


def oldest(rows, n=5):
    aged = [r for r in rows if r["ageable"]]
    aged.sort(key=lambda r: -(r["cutoff_age_days"] or 0))
    return [{"path": r["path"], "cutoff": r["cutoff_date"], "age_days": r["cutoff_age_days"]}
            for r in aged[:n]]


def _verdict_line(s):
    return ("%d of %d judged faces carry a cutoff a reader could age (%d hold only a build time, "
            "%d carry a build field that is not a date, %d carry nothing, %d declare a cutoff "
            "that does not parse, %d are dated in the future); the oldest ageable verdict is "
            "%s days old."
            % (s["aged_by_their_own_cutoff"], s["faces"], s["only_a_build_time"],
               s["build_time_does_not_parse"], s["no_date_signal_at_all"],
               s["declares_a_cutoff_that_does_not_parse"],
               s["cutoff_in_the_future"], s["cutoff_age_days_max"]))


def _verdict(s):
    if s["faces"] == 0:
        return "no_judged_faces_in_the_population"
    if s["faces_a_reader_cannot_age"] * 2 > s["faces"]:
        return "most_judged_faces_cannot_be_aged_from_their_own_bytes"
    if s["faces_a_reader_cannot_age"]:
        return "some_judged_faces_cannot_be_aged_from_their_own_bytes"
    return "every_judged_face_states_the_date_its_answer_is_about"


# --------------------------------------------------------------------------- #
# build / check / verify
# --------------------------------------------------------------------------- #

def build(write=True, root=None):
    root = root or ROOT
    today = date.fromisoformat(CUTOFF)
    faces, skipped_self, unreadable = population(root)
    rows = [row_for(rel, face, today) for rel, face in faces]
    summary = summarise(rows)
    face = {
        "study": STUDY,
        "generated_by": "scripts/e580_face_age.py",
        "machine": "bm-b",
        "dept": "research",
        "evidence_cutoff": CUTOFF,
        "generated": datetime.now().isoformat(timespec="seconds"),
        "rule": ("cutoff fields age the verdict; build fields age the file only; mtime is "
                 "published as unusable (r1472/E453) and never used. First match wins: "
                 + " > ".join([C_AGED, C_FUTURE, C_UNPARSEABLE, C_BUILD, C_BUILD_BAD,
                               C_NONE])),
        "population_note": ("every results/**/*.json with a top-level 'verdict' key, minus this "
                            "study's own two faces"),
        "population": {"faces": len(rows), "skipped_own_faces": skipped_self,
                       "files_that_do_not_parse_as_json": unreadable},
        "mtime_floor": mtime_floor(root),
        "rows": rows,
        "summary": summary,
        "oldest_ageable_faces": oldest(rows),
        "verdict": _verdict(summary),
        "verdict_line": _verdict_line(summary),
    }
    if write:
        os.makedirs(os.path.join(root, "results", "state_tilt"), exist_ok=True)
        body = json.dumps(face, ensure_ascii=False, indent=1, sort_keys=True) + "\n"
        for name in ("FACEAGED-%s.json" % CUTOFF, "faceaged_latest.json"):
            io.open(os.path.join(root, "results", "state_tilt", name), "w",
                    encoding="utf-8", newline="\n").write(body)
    return face


def face_problems(face):
    p = []
    rows = face.get("rows")
    if not isinstance(rows, list) or not rows:
        return ["the face carries no rows"]
    for r in rows:
        if r.get("class") not in (C_AGED, C_FUTURE, C_UNPARSEABLE, C_BUILD, C_BUILD_BAD,
                                  C_NONE):
            p.append("%s: class %r is not one of the five" % (r.get("path"), r.get("class")))
            continue
        if r["class"] == C_AGED:
            if r.get("cutoff_age_days") is None:
                p.append("%s: aged class with no derivable age" % r.get("path"))
            elif r["cutoff_age_days"] < 0:
                p.append("%s: aged class on a future cutoff" % r.get("path"))
            elif r.get("freshness") is None:
                p.append("%s: aged class with no freshness word" % r.get("path"))
        else:
            if r.get("freshness") is not None:
                p.append("%s: a freshness word on a face no cutoff can age" % r.get("path"))
            if r.get("ageable"):
                p.append("%s: published unageable but flagged ageable" % r.get("path"))
        if r["class"] == C_NONE and (r.get("cutoff_field") or r.get("build_field")):
            p.append("%s: no-date class beside a date-shaped field" % r.get("path"))
        if r["class"] == C_BUILD and not (r.get("build_field") and r.get("build_date")):
            p.append("%s: build-time class without a parsed build time" % r.get("path"))
        if r["class"] == C_UNPARSEABLE and not r.get("cutoff_field"):
            p.append("%s: unparseable class without a cutoff-shaped field" % r.get("path"))
        if r["class"] == C_BUILD_BAD and not (r.get("build_field")
                                              and r.get("build_date") is None):
            p.append("%s: unparseable build class without an unparseable build field"
                     % r.get("path"))
        if r["class"] == C_FUTURE and (r.get("cutoff_age_days") or 0) >= 0:
            p.append("%s: future class on a non-future cutoff" % r.get("path"))
    recomputed = summarise(rows)
    for key, value in (face.get("summary") or {}).items():
        if recomputed.get(key) != value:
            p.append("summary.%s does not re-derive from the rows (%r vs %r)"
                     % (key, value, recomputed.get(key)))
    s = face.get("summary") or {}
    if sum([s.get("aged_by_their_own_cutoff", 0), s.get("cutoff_in_the_future", 0),
            s.get("declares_a_cutoff_that_does_not_parse", 0), s.get("only_a_build_time", 0),
            s.get("build_time_does_not_parse", 0),
            s.get("no_date_signal_at_all", 0)]) != s.get("faces"):
        p.append("the six classes do not sum to the population")
    if face.get("verdict") != _verdict(s):
        p.append("the verdict does not re-derive from the summary")
    if face.get("verdict_line") != _verdict_line(s):
        p.append("the verdict line does not re-derive from the summary")
    if not face.get("evidence_cutoff"):
        p.append("the face declares no evidence_cutoff")
    pop = face.get("population") or {}
    if pop.get("faces") is not None and pop["faces"] != len(rows):
        p.append("population.faces does not equal the row count")
    mt = face.get("mtime_floor") or {}
    if mt.get("usable_as_freshness_evidence"):
        p.append("mtime is published as usable freshness evidence; r1472/E453 says it is not")
    return p


def _read_json(path):
    if not os.path.exists(path):
        return {}
    try:
        return json.load(io.open(path, encoding="utf-8"))
    except Exception:
        return {}


def check():
    face = _read_json(os.path.join(OUTDIR, "faceaged_latest.json"))
    problems = face_problems(face)
    for p in problems:
        print("CHECK FAIL %s" % p)
    if not problems:
        print("CHECK PASS %s" % face.get("verdict_line"))
    return 0 if not problems else 1


def verify():
    published = _read_json(os.path.join(OUTDIR, "faceaged_latest.json"))
    fresh = build(write=False)
    problems = face_problems(published)
    # population.skipped_own_faces is deliberately NOT compared: the published face is written
    # after the population was read, so a rebuild always sees two more files to skip. That is
    # growth of the corpus by this study's own hand, ruled not-drift in the E180/E207 family.
    for key in ("verdict", "verdict_line", "summary", "oldest_ageable_faces"):
        if fresh.get(key) != published.get(key):
            problems.append("%s drifted between the published face and a live rebuild" % key)
    by_path = {r["path"]: r for r in published.get("rows") or []}
    for r in fresh.get("rows") or []:
        old = by_path.get(r["path"])
        if old is None:
            problems.append("%s appeared on a live rebuild" % r["path"])
        elif old.get("class") != r["class"]:
            problems.append("%s: the class changed on a live rebuild" % r["path"])
    for p in problems:
        print("VERIFY FAIL %s" % p)
    if not problems:
        print("VERIFY PASS %d faces re-derived" % len(fresh.get("rows") or []))
    return 0 if not problems else 1


# --------------------------------------------------------------------------- #
# selftest -- hermetic: fixtures only, no disk reads beyond this module's own helpers
# --------------------------------------------------------------------------- #

def selftest():
    ok = []

    def eq(name, got, want):
        ok.append((name, got == want, "got %r want %r" % (got, want)))

    today = date(2026, 11, 9)

    # S1 parsing
    eq("iso date parses", parse_stamp("2026-11-08")[0], date(2026, 11, 8))
    eq("iso datetime parses to its date", parse_stamp("2026-11-08T16:18:14+08:00")[0],
       date(2026, 11, 8))
    eq("a space-separated datetime still parses", parse_stamp("2026-11-08 16:18")[0],
       date(2026, 11, 8))
    eq("compact yyyymmdd parses", parse_stamp("20261108")[0], date(2026, 11, 8))
    eq("a month resolves to its first day and says so",
       parse_stamp("2026-11"), (date(2026, 11, 1), "month_only_resolved_to_the_first"))
    eq("a panel sentence is not a date", parse_stamp("panel 2026-11-08 (bars due 15:30)")[0], None)
    eq("an integer below unix range is refused, not coerced",
       parse_stamp(20261108)[0], None)
    # the day itself depends on the local zone, so pin the shape and a two-day window instead
    epoch_day, epoch_how = parse_stamp(1_791_000_000)
    eq("unix seconds parse as a date", epoch_how, "unix_seconds")
    eq("unix seconds land in the right week", abs((epoch_day - date(2026, 10, 3)).days) <= 1, True)

    # S2 classes
    aged = classify({"verdict": "x", "evidence_cutoff": "2026-11-08", "generated": "2026-11-09T01:00"},
                    today)
    eq("a cutoff ages the face", (aged["class"], aged["ageable"], aged["cutoff_age_days"]),
       (C_AGED, True, 1))
    buildonly = classify({"verdict": "x", "generated": "2026-11-09T01:00"}, today)
    eq("a build time alone does not age the verdict", (buildonly["class"], buildonly["ageable"]),
       (C_BUILD, False))
    nothing = classify({"verdict": "x"}, today)
    eq("no date field at all", (nothing["class"], nothing["ageable"]), (C_NONE, False))
    bad = classify({"verdict": "x", "evidence_cutoff": "panel 2026-11-08 (bars due)"}, today)
    eq("a present-but-unparseable cutoff is its own class", bad["class"], C_UNPARSEABLE)
    future = classify({"verdict": "x", "cutoff": "2026-12-01"}, today)
    eq("a future cutoff is its own class", (future["class"], future["ageable"]),
       (C_FUTURE, False))
    # presence is not truthiness: a cutoff field holding None must not be read as a build-only face
    nullcut = classify({"verdict": "x", "evidence_cutoff": None, "generated": "2026-11-09"}, today)
    eq("a null cutoff field is still a cutoff claim", nullcut["class"], C_UNPARSEABLE)
    # a build field holding a word is a claim about the file that cannot be aged; it is not
    # the same fact as carrying no date field at all
    wordbuild = classify({"verdict": "x", "generated": "deterministic"}, today)
    eq("a build field that is not a date has its own class", wordbuild["class"], C_BUILD_BAD)
    eq("a non-date build field cannot age the verdict", wordbuild["ageable"], False)

    # S3 freshness never exists without a cutoff
    eq("no freshness word without a cutoff", freshness(None), None)
    eq("a one-day-old cutoff is today", freshness(1), "today")
    eq("a 31 day old cutoff is stale", freshness(31), "stale")
    eq("a 400 day old cutoff is very stale", freshness(400), "very_stale")

    # S4 rows + summary + verdict re-derive
    rows = [row_for("results/a.json", {"verdict": "ok", "evidence_cutoff": "2026-11-08"}, today),
            row_for("results/b.json", {"verdict": "ok", "generated": "2026-11-09"}, today),
            row_for("results/c.json", {"verdict": "ok"}, today)]
    s = summarise(rows)
    eq("the summary counts one ageable face", s["aged_by_their_own_cutoff"], 1)
    eq("the summary counts one build-only face", s["only_a_build_time"], 1)
    eq("the summary counts one undated face", s["no_date_signal_at_all"], 1)
    eq("six classes sum to the population",
       sum([s["aged_by_their_own_cutoff"], s["cutoff_in_the_future"],
            s["declares_a_cutoff_that_does_not_parse"], s["only_a_build_time"],
            s["build_time_does_not_parse"], s["no_date_signal_at_all"]]), s["faces"])
    eq("two of three cannot be aged", s["faces_a_reader_cannot_age"], 2)
    eq("the majority rule fires", _verdict(s),
       "most_judged_faces_cannot_be_aged_from_their_own_bytes")
    eq("the verdict line names the split", "1 of 3 judged faces" in _verdict_line(s), True)

    # S5 face checks refuse a doctored face
    base = {"rows": rows, "summary": s, "verdict": _verdict(s), "verdict_line": _verdict_line(s),
            "evidence_cutoff": CUTOFF, "population": {"faces": 3},
            "mtime_floor": {"usable_as_freshness_evidence": False}}
    eq("a clean face passes", face_problems(base), [])
    d1 = json.loads(json.dumps(base))
    d1["summary"]["aged_by_their_own_cutoff"] = 3
    eq("a summary that does not re-derive is refused", bool(face_problems(d1)), True)
    d2 = json.loads(json.dumps(base))
    d2["rows"][2]["freshness"] = "today"
    eq("a freshness word on an undated face is refused", bool(face_problems(d2)), True)
    d3 = json.loads(json.dumps(base))
    d3["mtime_floor"]["usable_as_freshness_evidence"] = True
    eq("mtime claimed usable is refused", bool(face_problems(d3)), True)
    d4 = json.loads(json.dumps(base))
    d4["population"]["faces"] = 4
    eq("a population count that differs from the rows is refused",
       bool(face_problems(d4)), True)

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