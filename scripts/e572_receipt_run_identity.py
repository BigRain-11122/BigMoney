# -*- coding: utf-8 -*-
"""E572 -- which of E569's three receipt-vs-sentence disagreements is a different run?

E569 joined 38 receipts to the sentence a round report printed and found 3 where the printed
numerator differs from a recount of the receipt's own rows.  It published the difference and
declined to say which side was wrong, because a numerator can disagree for three different
reasons: the prose counted wrong, the prose quoted a family run against a receipt that holds a
subset, or the receipt on disk belongs to a later run than the sentence describes.

This study decides each of the three from the file's own bytes plus git, and publishes which
witness decided it.  The rule is mechanical, and the case it cannot decide is published as
undecidable rather than guessed -- the file name alone is explicitly not a witness.

Witnesses carried per file (all machine-readable, the gate re-derives every one):
  receipt_ts            the timestamp the receipt writes about itself (three dialects seen)
  receipt_mtime         the bytes on disk; equal to receipt_ts means nobody rewrote it since
  receipt_tracked       whether git has the file at all (an untracked receipt cannot be rewritten
                        by a later commit, which is itself evidence)
  round_first_commit    the earliest commit whose message names the round (ct + sha + subject)
  cites_this_receipt    whether the sentence names this receipt's own log token
  absence_claim         whether the sentence asserts the file did not exist
  subset_marker         whether the sentence labels itself a subset (--only / family / ...)
  table                 the round's leg count as E568 recovered it from git (None when not
                        recovered: a count, not a list of names, so a name-prefix arm is not
                        claimed -- see 'unnamed_witnesses' in the face)

Classification order (first match wins, published in the face with the witness that fired):
  wrong_count_in_the_prose              the sentence cites this receipt's own log and differs
  receipt_rewritten_after_the_sentence  the sentence says the file was absent, but it is here
  family_sentence_against_a_subset_receipt  the sentence labels a subset and names its family
  undecidable                           no witness fires

Usage: python scripts/e572_receipt_run_identity.py [build|check|verify|selftest]
"""
import io
import json
import os
import re
import subprocess
import sys
import time

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
OUTDIR = os.path.join(ROOT, "results", "state_tilt")
E569_FACE = os.path.join(OUTDIR, "chainnumerator_latest.json")
E568_FACE = os.path.join(OUTDIR, "oldchaintable_latest.json")
CUTOFF = "2026-11-08"

C_WRONG = "wrong_count_in_the_prose"
C_REWRITTEN = "receipt_rewritten_after_the_sentence"
C_FAMILY = "family_sentence_against_a_subset_receipt"
C_UNDECIDED = "undecidable"
CLASSES = (C_WRONG, C_REWRITTEN, C_FAMILY, C_UNDECIDED)

SUBSET_MARKERS = ("--only", "only ", "family", "subset", "partial")
ABSENCE_MARKERS = ("json absent", "absent", "died", "diED", "killed", "did not run", "never ran")


def _read_json(path):
    with io.open(path, encoding="utf-8") as fh:
        return json.load(fh)


def _git(args, timeout=180):
    try:
        out = subprocess.run(["git"] + args, cwd=ROOT, stdout=subprocess.PIPE,
                             stderr=subprocess.DEVNULL, timeout=timeout)
    except Exception:
        return ""
    return out.stdout.decode("utf-8", "replace")


def log_token(file_name):
    """The token a report would print when it names this receipt's log.

    '_r1246bmb_s6_chain.json' -> 'r1246bmb_s6'; the receipt is json, the sentence cites the .log
    of the same run, so the shared part is everything before '_chain.json'.
    """
    base = file_name.lstrip("_")
    for suffix in ("_chain.json", "-chain.json", ".json"):
        if base.endswith(suffix):
            base = base[: -len(suffix)]
            break
    return base


def parse_ts(raw):
    if not isinstance(raw, str):
        return None
    raw = raw.strip().replace("T", " ")
    for fmt in ("%Y-%m-%d %H:%M:%S", "%Y-%m-%d %H:%M"):
        try:
            return time.mktime(time.strptime(raw, fmt))
        except ValueError:
            continue
    return None


def _markers(text):
    low = (text or "").lower()
    return {
        "subset_marker": next((m for m in SUBSET_MARKERS if m.strip() in low), None),
        "absence_claim": next((m for m in ABSENCE_MARKERS if m.lower() in low), None),
    }


def round_first_commit(rnd):
    """Earliest commit whose message names this round.

    A round number is shared across the fleet, and a commit may also name a round *before* it
    runs ("next: r1246"), so the count and the span are published beside the timestamp: the delta
    is a witness about text, never a proof of ordering, and this study never decides on it.
    """
    if rnd is None:
        return None
    out = _git(["log", "--fixed-strings", "--grep=round %d" % int(rnd),
                "--format=%ct\t%h\t%s", "-20"])
    rows = []
    for line in out.splitlines():
        parts = line.split("\t")
        if len(parts) < 3:
            continue
        try:
            ct = int(parts[0])
        except ValueError:
            continue
        rows.append({"ct": ct, "sha": parts[1], "subject": parts[2][:120]})
    if not rows:
        return None
    rows.sort(key=lambda r: r["ct"])
    first = dict(rows[0])
    first["commits_naming_the_round"] = len(rows)
    first["span_sec"] = rows[-1]["ct"] - rows[0]["ct"]
    return first


def receipt_witness(path):
    entry = {"path": path, "exists": os.path.exists(path)}
    if not entry["exists"]:
        return entry
    entry["mtime"] = int(os.path.getmtime(path))
    try:
        data = _read_json(path)
    except Exception:
        entry["unparsed"] = True
        return entry
    entry["ts_raw"] = data.get("ts") or data.get("finished") or data.get("generated")
    entry["ts"] = parse_ts(entry["ts_raw"])
    entry["legs"] = len(data.get("legs") or [])
    entry["leg_names"] = [l.get("leg") for l in (data.get("legs") or []) if isinstance(l, dict)]
    entry["stated_total"] = data.get("legs_total")
    tracked = _git(["ls-files", "--error-unmatch", path]).strip()
    entry["tracked"] = bool(tracked)
    entry["mtime_equals_ts"] = (entry["ts"] is not None
                                and abs(entry["mtime"] - entry["ts"]) <= 120)
    return entry


def table_for(rnd, machine):
    try:
        face = _read_json(E568_FACE)
    except Exception:
        return None
    for row in face.get("rows") or []:
        if row.get("round") == rnd and (machine is None or row.get("machine") == machine):
            return row.get("table")
    return None


def classify(w):
    """First match wins; the returned (class, witness) pair is the whole science of this card."""
    if not w.get("receipt", {}).get("exists"):
        return C_UNDECIDED, "no receipt on disk to attribute"
    if w.get("cites_this_receipt") and w.get("numbers_differ"):
        return C_WRONG, "the sentence cites this receipt's own log token and its numbers differ"
    if w.get("absence_claim"):
        return C_REWRITTEN, ("the sentence says the file was absent (marker %r) and it is here, "
                             "so the bytes belong to a later run" % w["absence_claim"])
    if w.get("subset_marker"):
        return C_FAMILY, ("the sentence labels a subset (%r): the numerator counts the family it "
                          "names, not the rows this receipt holds" % w["subset_marker"])
    return C_UNDECIDED, "no witness fires: the sentence neither cites this receipt nor labels a scope"


def row_for(e569_row):
    receipt = receipt_witness(os.path.join("results", e569_row["file"]))
    rnd = e569_row.get("name_round")
    commit = round_first_commit(rnd)
    sentence = e569_row.get("printed_sentence") or ""
    token = log_token(e569_row["file"])
    marks = _markers(sentence)
    stated = (e569_row.get("printed_numerator"), e569_row.get("printed_denominator"))
    derived = e569_row.get("derived_rc0")
    numbers_differ = (stated[0] is not None and derived is not None and stated[0] != derived)
    row = {
        "file": e569_row["file"],
        "machine": e569_row.get("machine"),
        "name_round": rnd,
        "printed": {"numerator": stated[0], "denominator": stated[1]},
        "derived_rc0": derived,
        "numbers_differ": numbers_differ,
        "log_token": token,
        "cites_this_receipt": token.lower() in sentence.lower(),
        "subset_marker": marks["subset_marker"],
        "absence_claim": marks["absence_claim"],
        "receipt": receipt,
        "round_first_commit": commit,
        "table": table_for(rnd, e569_row.get("machine")),
        "sentence": sentence[:300],
    }
    klass, witness = classify(row)
    row["class"] = klass
    row["decided_by"] = witness
    row["ts_vs_commit_sec"] = (
        None if not receipt.get("ts") or not commit else receipt["ts"] - commit["ct"])
    return row


def _verdict(summary):
    counts = summary.get("by_class") or {}
    if not counts.get("files"):
        return "no_disagreement_to_attribute"
    if counts.get(C_WRONG) == 0 and counts.get(C_UNDECIDED) == 0:
        return "none_of_the_disagreements_is_a_wrong_count_in_the_prose"
    if counts.get(C_WRONG):
        return ("%d_of_the_%d_disagreements_is_a_wrong_count_in_the_prose"
                % (counts[C_WRONG], counts["files"]))
    return ("%d_of_the_%d_disagreements_cannot_be_decided_from_its_own_bytes"
            % (counts.get(C_UNDECIDED, 0), counts["files"]))


def _verdict_line(s):
    c = s.get("by_class") or {}
    return ("files=%d wrong_count=%d rewritten_after=%d family_vs_subset=%d undecidable=%d "
            "| cited_own_log=%d absence_claim=%d subset_marker=%d"
            % (c.get("files", 0), c.get(C_WRONG, 0), c.get(C_REWRITTEN, 0), c.get(C_FAMILY, 0),
               c.get(C_UNDECIDED, 0), s.get("cites_this_receipt", 0),
               s.get("absence_claim", 0), s.get("subset_marker", 0)))


def build(write=True):
    e569 = _read_json(E569_FACE)
    population = [r for r in (e569.get("rows") or [])
                  if r.get("printed_matches_derived_rc0") is False]
    rows = [row_for(r) for r in population]
    by_class = {k: sum(1 for r in rows if r["class"] == k) for k in CLASSES}
    by_class["files"] = len(rows)
    summary = {
        "population_from_E569": len(population),
        "by_class": by_class,
        "cites_this_receipt": sum(1 for r in rows if r["cites_this_receipt"]),
        "absence_claim": sum(1 for r in rows if r["absence_claim"]),
        "subset_marker": sum(1 for r in rows if r["subset_marker"]),
        "receipts_tracked_in_git": sum(1 for r in rows if (r["receipt"] or {}).get("tracked")),
        "receipts_whose_mtime_equals_their_own_ts": sum(
            1 for r in rows if (r["receipt"] or {}).get("mtime_equals_ts")),
        "rounds_with_a_recovered_table": sum(1 for r in rows if r.get("table")),
        "rounds_whose_commit_delta_exceeds_48h": sum(
            1 for r in rows if r.get("ts_vs_commit_sec") is not None
            and abs(r["ts_vs_commit_sec"]) > 48 * 3600),
        "unnamed_witnesses": ["leg_names_are_a_prefix_of_the_table"],
    }
    face = {
        "study": "E572_receipt_run_identity",
        "card": "E572",
        "dept": "research+engineering",
        "machine": "bm-b",
        "evidence_cutoff": CUTOFF,
        "population": ("every E569 row whose printed numerator differs from a recount of the "
                       "receipt's own rows (machine-read from chainnumerator_latest.json)"),
        "rule": ("cites_own_log+differs -> wrong count; absence claim -> rewritten after the "
                 "sentence; subset marker -> family vs subset; else undecidable"),
        "summary": summary,
        "verdict": _verdict(summary),
        "verdict_line": _verdict_line(summary),
        "rows": rows,
    }
    if write:
        if not os.path.isdir(OUTDIR):
            os.makedirs(OUTDIR)
        path = os.path.join(OUTDIR, "RECEIPTRUNID-%s.json" % CUTOFF)
        with io.open(path, "w", encoding="utf-8", newline="\n") as fh:
            json.dump(face, fh, ensure_ascii=False, indent=1, sort_keys=True)
        with io.open(os.path.join(OUTDIR, "receiptrunid_latest.json"), "w",
                     encoding="utf-8", newline="\n") as fh:
            json.dump(face, fh, ensure_ascii=False, indent=1, sort_keys=True)
    return face


def face_problems(face):
    problems = []
    rows = face.get("rows") or []
    s = face.get("summary") or {}
    if face.get("verdict") != _verdict(s):
        problems.append("the verdict does not re-derive from the summary")
    if face.get("verdict_line") != _verdict_line(s):
        problems.append("the verdict line does not re-derive from the summary")
    if s.get("population_from_E569") != len(rows):
        problems.append("the population count does not equal the rows")
    counts = {k: sum(1 for r in rows if r.get("class") == k) for k in CLASSES}
    for k, v in counts.items():
        if (s.get("by_class") or {}).get(k) != v:
            problems.append("by_class.%s does not re-derive from the rows" % k)
    if (s.get("by_class") or {}).get("files") != len(rows):
        problems.append("by_class.files does not equal the rows")
    for r in rows:
        if r.get("class") not in CLASSES:
            problems.append("%s: class %r is not one this study declares"
                            % (r.get("file"), r.get("class")))
            break
        if not r.get("decided_by"):
            problems.append("%s: no witness is named" % r.get("file"))
            break
        # a row must not be decided on its file name alone: every non-undecidable class needs
        # at least one witness read from the bytes or from git
        if r.get("class") == C_WRONG and not (r.get("cites_this_receipt") and r.get("numbers_differ")):
            problems.append("%s: wrong_count without a citing sentence and differing numbers"
                            % r.get("file"))
            break
        if r.get("class") == C_REWRITTEN and not r.get("absence_claim"):
            problems.append("%s: rewritten_after without an absence claim" % r.get("file"))
            break
        if r.get("class") == C_FAMILY and not r.get("subset_marker"):
            problems.append("%s: family_vs_subset without a subset marker" % r.get("file"))
            break
    return problems


def _fixture(klass):
    base = {
        "file": "_r100bmb_s6_chain.json", "machine": "b", "name_round": 100,
        "printed": {"numerator": 5, "denominator": 5}, "derived_rc0": 7,
        "numbers_differ": True, "log_token": "r100bmb_s6",
        "cites_this_receipt": False, "subset_marker": None, "absence_claim": None,
        "receipt": {"exists": True, "ts": 1, "mtime": 1, "mtime_equals_ts": True,
                    "tracked": False, "stated_total": 7},
        "round_first_commit": {"ct": 2, "sha": "0" * 7, "subject": "round 100"},
        "table": 7, "ts_vs_commit_sec": -1,
    }
    if klass == C_WRONG:
        base["cites_this_receipt"] = True
    elif klass == C_REWRITTEN:
        base["absence_claim"] = "json absent"
    elif klass == C_FAMILY:
        base["subset_marker"] = "--only"
    base["class"] = klass or C_UNDECIDED
    base["decided_by"] = "fixture"
    return base


def selftest():
    ok = []

    def eq(name, got, want):
        ok.append((name, got == want, "%r != %r" % (got, want) if got != want else ""))

    eq("a_citing_sentence_with_different_numbers_is_a_wrong_count",
       classify(_fixture(C_WRONG))[0], C_WRONG)
    eq("an_absence_claim_against_a_present_file_is_a_later_run",
       classify(_fixture(C_REWRITTEN))[0], C_REWRITTEN)
    eq("a_subset_marker_makes_the_join_a_family_artifact",
       classify(_fixture(C_FAMILY))[0], C_FAMILY)
    eq("nothing_fires_means_undecidable", classify(_fixture(None))[0], C_UNDECIDED)
    eq("a_missing_receipt_is_undecidable, so the file name is never a witness",
       classify({"receipt": {"exists": False}, "cites_this_receipt": False})[0], C_UNDECIDED)
    eq("log_token_strips_the_chain_suffix", log_token("_r1246bmb_s6_chain.json"), "r1246bmb_s6")
    eq("log_token_keeps_a_name_without_the_suffix", log_token("_r--allbmc_s6_chain.json"), "r--allbmc_s6")
    eq("a_t_iso_ts_parses", parse_ts("2026-10-29T12:36:14") is not None, True)
    eq("a_space_ts_parses", parse_ts("2026-09-29 01:21:25") is not None, True)
    eq("nones_do_not_parse", parse_ts(None), None)
    eq("only_a_marker_is_found", _markers("ran with --only star_self_price")["subset_marker"], "--only")
    eq("an_absence_marker_is_found", _markers("chain had DIED at leg 6/36")["absence_claim"], "died")
    eq("a_clean_sentence_has_no_marker", _markers("S6 25/25 rc=0")["absence_claim"], None)
    fixture_face = {
        "summary": {"population_from_E569": 1,
                    "by_class": {"files": 1, C_WRONG: 1, C_REWRITTEN: 0, C_FAMILY: 0,
                                 C_UNDECIDED: 0},
                    "cites_this_receipt": 1, "absence_claim": 0, "subset_marker": 0},
        "rows": [_fixture(C_WRONG)],
    }
    fixture_face["verdict"] = _verdict(fixture_face["summary"])
    fixture_face["verdict_line"] = _verdict_line(fixture_face["summary"])
    eq("a_consistent_fixture_face_has_no_problems", face_problems(fixture_face), [])
    bad = json.loads(json.dumps(fixture_face))
    bad["verdict"] = "a_verdict_this_study_never_publishes"
    eq("a_hand_written_verdict_is_refused", bool(face_problems(bad)), True)
    bad = json.loads(json.dumps(fixture_face))
    bad["rows"][0]["class"] = C_FAMILY
    eq("a_class_without_its_witness_is_refused", bool(face_problems(bad)), True)
    bad = json.loads(json.dumps(fixture_face))
    bad["rows"][0]["class"] = "looks_like_a_later_run"
    eq("an_invented_class_is_refused", bool(face_problems(bad)), True)
    bad = json.loads(json.dumps(fixture_face))
    bad["summary"]["by_class"][C_WRONG] = 0
    eq("a_count_that_does_not_re_derive_is_refused", bool(face_problems(bad)), True)

    failed = [n for n, good, _ in ok if not good]
    for n, good, detail in ok:
        print("  %s %s%s" % ("PASS" if good else "FAIL", n, "" if good else "  <- " + detail))
    print("selftest %d/%d" % (len(ok) - len(failed), len(ok)))
    return 0 if not failed else 1


def check():
    face = _read_json(os.path.join(OUTDIR, "receiptrunid_latest.json"))
    problems = face_problems(face)
    if problems:
        for p in problems:
            print("CHECK FAIL %s" % p)
        return 1
    print("CHECK PASS %s" % face.get("verdict_line"))
    return 0


def verify():
    """Re-derive the face from the live inputs and compare to what is published."""
    fresh = build(write=False)
    published = _read_json(os.path.join(OUTDIR, "receiptrunid_latest.json"))
    problems = face_problems(published)
    for key in ("verdict", "verdict_line"):
        if fresh.get(key) != published.get(key):
            problems.append("%s drifted between the published face and a live rebuild" % key)
    if [r.get("class") for r in fresh.get("rows") or []] != \
            [r.get("class") for r in published.get("rows") or []]:
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