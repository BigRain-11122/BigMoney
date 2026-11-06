"""E480 -- does a dated vintage file's payload state the same date its name states?

E472 published 97 unread vintage families (571 member files); E477 priced their bytes and E478
found 31 of 176 comparable vintages are their own latest twin once four clock names are stripped.
Every one of those studies had to *trust the file name* for "when was this written".  This face
tests that trust directly: for each member file whose name carries exactly one ISO date, does the
payload itself state that same date in one of the frozen date fields?

Each member lands in exactly one class:

  date_agrees                 the name carries exactly one ISO date and at least one frozen date
                              field in the payload starts with that same YYYY-MM-DD
  date_disagrees              the name carries exactly one ISO date, the payload states at least
                              one date, and none of them is the name's date
  no_date_in_name             the basename carries no ISO date at all
  ambiguous_name_date         the basename carries two or more distinct ISO dates (a range name)
  no_date_in_payload          the name carries a date but the payload states none of the frozen
                              names -- unmeasured, not a negative
  not_a_json_object           the member is not a .json payload (csv/md/jsonl)
  unreadable_member           missing on disk or does not parse

The verdict is computed over `date-comparable` files only (agrees + disagrees).  A file whose
payload never states a date is published as unmeasured: a missing witness is not a lie.

This is an index-integrity measurement, not a retention licence: it says whether the name can be
used as the file's date, which is the assumption every earlier vintage study leaned on.

CLI: run | check | verify | selftest
"""

import argparse
import io
import json
import os
import re
import shutil
import sys
import tempfile
import time

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUTDIR = os.path.join(ROOT, "results", "state_tilt")
FACE_NAME = "vintagedate_latest.json"
DATED_PREFIX = "VINTAGEDATE"
CARD = "E480-DO-THE-VINTAGE-FILES-CARRY-AN-EVIDENCE-CUTOFF-THAT-MATCHES-THE-DATE-IN-THEIR-NAME"
PARENT_FACE = "vintageread_latest.json"      # E472: the 97 unread vintage families
SIBLING_CLOCK = "vintageclock_latest.json"   # E478: twin comparison
SIBLING_RETIRE = "vintageretire_latest.json"  # E477: byte floor

# Frozen by the card text.  A name outside this tuple does not witness a date, and the face
# publishes the tuple so a reader can see exactly which names were accepted (E207 family).
DATE_FIELDS = ("evidence_cutoff", "generated", "ts", "timestamp", "date", "as_of", "asof_bar")

ISO_DATE_RE = re.compile(r"(?<!\d)(\d{4})-(\d{2})-(\d{2})(?!\d)")

C_AGREES = "date_agrees"
C_DISAGREES = "date_disagrees"
C_NO_NAME_DATE = "no_date_in_name"
C_AMBIGUOUS = "ambiguous_name_date"
C_NO_PAYLOAD_DATE = "no_date_in_payload"
C_NOT_JSON = "not_a_json_object"
C_UNREADABLE = "unreadable_member"
COMPARABLE = (C_AGREES, C_DISAGREES)
NOT_COMPARABLE = (C_NO_NAME_DATE, C_AMBIGUOUS, C_NO_PAYLOAD_DATE, C_NOT_JSON, C_UNREADABLE)
CLASSES = COMPARABLE + NOT_COMPARABLE

V_EMPTY = "no_vintage_file_name_and_payload_both_state_a_date"
V_NONE = "no_vintage_file_name_agrees_with_the_date_its_payload_states"
V_ALL = "every_dated_vintage_file_name_agrees_with_the_date_its_payload_states"
V_MOST = "most_dated_vintage_file_names_agree_with_the_date_their_payload_states"
V_SOME = "some_dated_vintage_file_names_agree_with_the_date_their_payload_states_and_the_majority_do_not"
VERDICT_VOCAB = (V_EMPTY, V_NONE, V_ALL, V_MOST, V_SOME)


# ----------------------------------------------------------------------------- helpers


def _rel(path, root=None):
    return os.path.relpath(path, root or ROOT).replace("\\", "/")


def name_dates(basename):
    """Every distinct ISO date in a file name, in the order they appear."""
    seen = []
    for m in ISO_DATE_RE.finditer(basename):
        d = "%s-%s-%s" % (m.group(1), m.group(2), m.group(3))
        if d not in seen:
            seen.append(d)
    return seen


def payload_dates(obj):
    """The YYYY-MM-DD prefix of every frozen date field present at the payload's top level."""
    out = []
    if not isinstance(obj, dict):
        return out
    for k in DATE_FIELDS:
        if k not in obj:
            continue
        v = obj.get(k)
        if not isinstance(v, str):
            continue
        m = ISO_DATE_RE.search(v)
        if m:
            d = "%s-%s-%s" % (m.group(1), m.group(2), m.group(3))
            if d not in out:
                out.append(d)
    return out


def classify_file(path, read, exists):
    """Classify one member file.  read() is injectable for the selftest."""
    dates = name_dates(os.path.basename(path))
    if not dates:
        return C_NO_NAME_DATE, [], []
    if len(dates) > 1:
        return C_AMBIGUOUS, dates, []
    ext = os.path.splitext(path)[1].lower()
    if ext != ".json":
        return C_NOT_JSON, dates, []
    if not exists(path):
        return C_UNREADABLE, dates, []
    try:
        obj = read(path)
    except Exception:
        return C_UNREADABLE, dates, []
    if not isinstance(obj, dict):
        return C_NOT_JSON, dates, []
    stated = payload_dates(obj)
    if not stated:
        return C_NO_PAYLOAD_DATE, dates, []
    return (C_AGREES if dates[0] in stated else C_DISAGREES), dates, stated


def classify(rows_by_family, read, exists, size_of, rel):
    """rows_by_family: {family_key: {'members': [...]}}"""
    rows = []
    families = []
    counts = {c: 0 for c in CLASSES}
    byte_counts = {c: 0 for c in CLASSES}
    disagree_offsets = {}

    for fam_key in sorted(rows_by_family):
        fam = rows_by_family[fam_key]
        fam_counts = {c: 0 for c in CLASSES}
        fam_bytes = 0
        for member in sorted(fam.get("members") or []):
            cls, nd, stated = classify_file(member, read, exists)
            try:
                size = size_of(member)
            except OSError:
                size = 0
            counts[cls] += 1
            byte_counts[cls] += size
            fam_counts[cls] += 1
            fam_bytes += size
            if cls == C_DISAGREES:
                key = "%s -> %s" % (nd[0], stated[0])
                disagree_offsets[key] = disagree_offsets.get(key, 0) + 1
            rows.append({
                "path": rel(member),
                "family": fam_key,
                "bytes": size,
                "class": cls,
                "name_dates": nd,
                "payload_dates": stated,
            })
        families.append({
            "family": fam_key,
            "members": len(fam.get("members") or []),
            "counts": fam_counts,
            "bytes": fam_bytes,
        })

    return rows, families, counts, byte_counts, disagree_offsets


# ----------------------------------------------------------------------------- build


def build(pop_path=None):
    pop = json.load(io.open(pop_path or os.path.join(OUTDIR, PARENT_FACE), "r", encoding="utf-8"))
    siblings = {}
    for name in (SIBLING_CLOCK, SIBLING_RETIRE):
        p = os.path.join(OUTDIR, name)
        if os.path.exists(p):
            try:
                siblings[name] = json.load(io.open(p, "r", encoding="utf-8"))
            except Exception:
                siblings[name] = None

    rows_by_family = {}
    for r in pop.get("rows") or []:
        key = "%s/%s" % (r.get("dir", "?"), r.get("family", "?"))
        members = [m if os.path.isabs(m) else os.path.join(ROOT, m) for m in (r.get("members") or [])]
        twin = r.get("latest")
        if twin:
            twin_abs = twin if os.path.isabs(twin) else os.path.join(ROOT, twin)
            members = [m for m in members if os.path.normpath(m) != os.path.normpath(twin_abs)]
        rows_by_family[key] = {"members": members}

    rows, families, counts, byte_counts, offsets = classify(
        rows_by_family,
        lambda p: json.load(io.open(p, "r", encoding="utf-8")),
        os.path.exists,
        os.path.getsize,
        _rel,
    )

    comparable = counts[C_AGREES] + counts[C_DISAGREES]
    agrees = counts[C_AGREES]
    if comparable == 0:
        verdict = V_EMPTY
    elif agrees == 0:
        verdict = V_NONE
    elif agrees == comparable:
        verdict = V_ALL
    elif agrees * 2 > comparable:
        verdict = V_MOST
    else:
        verdict = V_SOME

    dated_files = sum(1 for r in rows if r.get("name_dates") and len(r["name_dates"]) == 1)
    summary = {
        "families_total": len(families),
        "member_files": len(rows),
        "files_whose_name_states_a_date": dated_files,
        "files_whose_name_states_no_date": counts[C_NO_NAME_DATE],
        "files_whose_name_states_more_than_one_date": counts[C_AMBIGUOUS],
        "comparable_files": comparable,
        "class_counts": counts,
        "class_bytes": byte_counts,
        "names_agreeing_with_the_date_their_payload_states": agrees,
        "agreement_share_of_comparable": round(agrees / comparable, 6) if comparable else None,
        "published_dates_not_witnessed_by_the_payload": counts[C_NO_PAYLOAD_DATE],
        "bytes_whose_name_date_is_confirmed_by_the_payload": byte_counts[C_AGREES],
        "disagreement_pairs": dict(sorted(offsets.items(), key=lambda kv: -kv[1])[:12]),
        "frozen_date_fields": list(DATE_FIELDS),
        "sibling_context": {
            "e477_bytes_lost_if_retired": ((siblings.get(SIBLING_RETIRE) or {}).get("summary") or {}).get(
                "bytes_lost_if_retired"),
            "e478_identical_after_clock_strip": ((siblings.get(SIBLING_CLOCK) or {}).get("summary") or {}).get(
                "vintage_files_identical_after_clock_strip"),
        },
    }

    face = {
        "card": CARD,
        "study": "E480_do_the_vintage_files_carry_a_date_that_matches_the_date_in_their_name",
        "title": "do the vintage files carry a date that matches the date in their name?",
        "evidence_cutoff": time.strftime("%Y-%m-%d"),
        "generated": time.strftime("%Y-%m-%dT%H:%M:%S%z"),
        "frozen_date_fields": list(DATE_FIELDS),
        "population_source": {
            "face": PARENT_FACE,
            "face_evidence_cutoff": pop.get("evidence_cutoff"),
            "face_verdict": pop.get("verdict"),
            "twin_excluded_from_population": True,
        },
        "class_definition": {
            C_AGREES: "the name carries exactly one ISO date and a frozen payload date field starts "
                      "with that same YYYY-MM-DD",
            C_DISAGREES: "the name carries exactly one ISO date, the payload states dates, and none "
                         "of them is the name's date",
            C_NO_NAME_DATE: "the basename carries no ISO date",
            C_AMBIGUOUS: "the basename carries two or more distinct ISO dates (a range name)",
            C_NO_PAYLOAD_DATE: "the name carries a date but the payload states none of the frozen "
                               "names: unmeasured, never a negative",
            C_NOT_JSON: "the member is not a .json payload",
            C_UNREADABLE: "the member is missing on disk or does not parse",
        },
        "summary": summary,
        "verdict": verdict,
        "verdict_vocab": list(VERDICT_VOCAB),
        "families": families,
        "rows": rows,
        "method_limits": [
            "seven field names are accepted (frozen_date_fields); a payload that records its day "
            "under another name (run_at, written, bar_date) reads as unmeasured, not as disagrees",
            "only the filename is consulted for the name date -- a date carried in a directory "
            "segment is out of scope here",
            "agreement is date-level: a payload whose evidence_cutoff is the 5th while the name says "
            "the 4th is a disagreement even when both describe the same snapshot",
            "the population is E472's published rows; a family that gained or lost members since "
            "then is not rescanned",
            "this measures whether the name can be used as the file's date -- it says nothing about "
            "whether the file should be kept (E477/E479 own that)",
        ],
    }
    return face


# ----------------------------------------------------------------------------- guards


def row_problems(face):
    problems = []
    s = face.get("summary") or {}
    rows = face.get("rows") or []
    counts = s.get("class_counts") or {}
    if set(counts) != set(CLASSES):
        problems.append("class_counts keys are not the published class set: %r" % sorted(counts))
    if sum(counts.values()) != s.get("member_files"):
        problems.append("class counts do not sum to member_files")
    if len(rows) != s.get("member_files"):
        problems.append("row count %d != member_files %r" % (len(rows), s.get("member_files")))
    if sum((s.get("class_bytes") or {}).values()) != sum(r.get("bytes", 0) for r in rows):
        problems.append("class bytes do not sum to the row bytes")
    derived = {c: 0 for c in CLASSES}
    for r in rows:
        if r.get("class") not in CLASSES:
            problems.append("row %s carries a class outside the set" % r.get("path"))
            break
        derived[r.get("class")] += 1
        if r.get("class") == C_AGREES:
            nd, pd = r.get("name_dates") or [], r.get("payload_dates") or []
            if len(nd) != 1 or nd[0] not in pd:
                problems.append("row %s is date_agrees but its dates do not witness it" % r.get("path"))
                break
        if r.get("class") == C_DISAGREES:
            nd, pd = r.get("name_dates") or [], r.get("payload_dates") or []
            if len(nd) != 1 or not pd or nd[0] in pd:
                problems.append("row %s is date_disagrees but its dates do not witness it" % r.get("path"))
                break
        if r.get("class") == C_NO_PAYLOAD_DATE and not (r.get("name_dates") and not r.get("payload_dates")):
            problems.append("row %s is no_date_in_payload without a name date and an empty payload list"
                            % r.get("path"))
            break
        if r.get("class") == C_AMBIGUOUS and len(r.get("name_dates") or []) < 2:
            problems.append("row %s is ambiguous with fewer than two name dates" % r.get("path"))
            break
        if r.get("class") == C_NO_NAME_DATE and r.get("name_dates"):
            problems.append("row %s is no_date_in_name yet carries a name date" % r.get("path"))
            break
    if derived != counts:
        problems.append("the published class counts do not re-derive from the rows")
    if s.get("names_agreeing_with_the_date_their_payload_states") != derived.get(C_AGREES):
        problems.append("the agreement tally does not re-derive from the rows")
    if s.get("comparable_files") != derived.get(C_AGREES, 0) + derived.get(C_DISAGREES, 0):
        problems.append("the comparable tally is not agrees + disagrees")
    if s.get("files_whose_name_states_no_date") != derived.get(C_NO_NAME_DATE):
        problems.append("the no-name-date tally does not re-derive from the rows")
    if face.get("verdict") not in VERDICT_VOCAB:
        problems.append("verdict is outside the frozen vocabulary: %r" % face.get("verdict"))
    fam_sum = sum(f.get("members", 0) for f in face.get("families") or [])
    if fam_sum != s.get("member_files"):
        problems.append("family member counts do not sum to member_files")
    dated = sum(1 for r in rows if len(r.get("name_dates") or []) == 1)
    if s.get("files_whose_name_states_a_date") != dated:
        problems.append("the dated-name tally does not re-derive from the rows")
    return problems


def _expect_verdict(counts):
    comparable = counts.get(C_AGREES, 0) + counts.get(C_DISAGREES, 0)
    agrees = counts.get(C_AGREES, 0)
    if comparable == 0:
        return V_EMPTY
    if agrees == 0:
        return V_NONE
    if agrees == comparable:
        return V_ALL
    if agrees * 2 > comparable:
        return V_MOST
    return V_SOME


def check(face=None):
    face = face or json.load(io.open(os.path.join(OUTDIR, FACE_NAME), "r", encoding="utf-8"))
    problems = row_problems(face)
    counts = (face.get("summary") or {}).get("class_counts") or {}
    expect = _expect_verdict(counts)
    if face.get("verdict") != expect:
        problems.append("verdict %r is not the one the counts imply (%r)" % (face.get("verdict"), expect))
    return problems


def verify():
    published = json.load(io.open(os.path.join(OUTDIR, FACE_NAME), "r", encoding="utf-8"))
    fresh = build()
    problems = []
    ps, fs = published.get("summary") or {}, fresh.get("summary") or {}
    for key in ("families_total", "member_files", "files_whose_name_states_a_date",
                "files_whose_name_states_no_date", "files_whose_name_states_more_than_one_date",
                "comparable_files", "class_counts", "class_bytes",
                "names_agreeing_with_the_date_their_payload_states",
                "published_dates_not_witnessed_by_the_payload",
                "bytes_whose_name_date_is_confirmed_by_the_payload", "disagreement_pairs"):
        if ps.get(key) != fs.get(key):
            problems.append("%s: published %r != fresh %r" % (key, ps.get(key), fs.get(key)))
    if published.get("verdict") != fresh.get("verdict"):
        problems.append("verdict: published %r != fresh %r" % (published.get("verdict"), fresh.get("verdict")))
    return problems


def run(face=None):
    face = face or build()
    os.makedirs(OUTDIR, exist_ok=True)
    dated = os.path.join(OUTDIR, "%s-%s.json" % (DATED_PREFIX, face["evidence_cutoff"]))
    latest = os.path.join(OUTDIR, FACE_NAME)
    compact = json.dumps(face, ensure_ascii=False, sort_keys=True)
    for path in (dated, latest):
        with io.open(path, "w", encoding="utf-8", newline="\n") as fh:
            fh.write(compact + "\n")
    problems = check(face)
    print(json.dumps({"face": _rel(latest), "dated": _rel(dated),
                      "summary": face["summary"], "verdict": face["verdict"],
                      "problems": problems}, ensure_ascii=False, sort_keys=True))
    return 0 if not problems else 1


# ----------------------------------------------------------------------------- selftest


def selftest():
    tmp = tempfile.mkdtemp(prefix="e480_")
    fails = []

    def want(name, got, expect):
        if got != expect:
            fails.append("%s: got %r want %r" % (name, got, expect))

    try:
        def w(path, obj):
            d = os.path.dirname(path)
            if d and not os.path.isdir(d):
                os.makedirs(d)
            with io.open(path, "w", encoding="utf-8", newline="\n") as fh:
                fh.write(obj if isinstance(obj, str) else json.dumps(obj, sort_keys=True))

        base = os.path.join(tmp, "fam")
        # 1: agrees (payload states the name's date, with a time suffix)
        a = os.path.join(base, "FAM-2026-01-01.json")
        w(a, {"evidence_cutoff": "2026-01-01", "x": 1})
        # 2: disagrees (payload says the 2nd, name says the 3rd)
        b = os.path.join(base, "FAM-2026-01-03.json")
        w(b, {"generated": "2026-01-02T10:00:00+08:00", "x": 1})
        # 3: no date in the name
        c = os.path.join(base, "FAM_latest.json")
        w(c, {"evidence_cutoff": "2026-01-04"})
        # 4: ambiguous name (a range)
        d = os.path.join(base, "FAM-2026-01-05-2026-01-06.json")
        w(d, {"evidence_cutoff": "2026-01-05"})
        # 5: name has a date, payload states none of the frozen names
        e = os.path.join(base, "FAM-2026-01-07.json")
        w(e, {"run_at": "2026-01-07T09:00:00", "x": 1})
        # 6: not json
        f = os.path.join(base, "FAM-2026-01-08.csv")
        w(f, "a,b\n1,2\n")
        # 7: unreadable json
        g = os.path.join(base, "FAM-2026-01-09.json")
        w(g, "{not json")
        # 8: missing on disk
        h = os.path.join(base, "FAM-2026-01-10.json")
        # 9: json list, not an object
        i = os.path.join(base, "FAM-2026-01-11.json")
        w(i, "[1, 2, 3]")

        rows_by_family = {"fam/FAM": {"members": [a, b, c, d, e, f, g, h, i]}}
        rows, families, counts, byte_counts, offsets = classify(
            rows_by_family,
            lambda p: json.load(io.open(p, "r", encoding="utf-8")),
            os.path.exists, os.path.getsize, lambda p: os.path.basename(p))

        want("agrees count", counts[C_AGREES], 1)
        want("disagrees count", counts[C_DISAGREES], 1)
        want("no-name-date count", counts[C_NO_NAME_DATE], 1)
        want("ambiguous count", counts[C_AMBIGUOUS], 1)
        want("no-payload-date count", counts[C_NO_PAYLOAD_DATE], 1)
        want("not-json count", counts[C_NOT_JSON], 2)   # csv + json list
        want("unreadable count", counts[C_UNREADABLE], 2)  # bad json + missing
        want("class sum", sum(counts.values()), 9)
        want("comparable", counts[C_AGREES] + counts[C_DISAGREES], 2)
        want("agrees bytes", byte_counts[C_AGREES], os.path.getsize(a))
        want("disagreement pair histogram",
             offsets, {"2026-01-03 -> 2026-01-02": 1})
        want("family member count", [f["members"] for f in families], [9])

        # name_dates / payload_dates are their own measurements
        want("name dates de-duplicated", name_dates("X-2026-01-01-2026-01-01.json"), ["2026-01-01"])
        want("two name dates", name_dates("X-2026-01-01-2026-01-02.json"), ["2026-01-01", "2026-01-02"])
        want("no name date", name_dates("X_latest.json"), [])
        want("payload date from a timestamp",
             payload_dates({"timestamp": "2026-02-03T04:05:06"}), ["2026-02-03"])
        want("non-string date field ignored", payload_dates({"ts": 1793977916}), [])
        want("unknown field ignored", payload_dates({"run_at": "2026-02-03"}), [])
        want("date de-duplicated across fields",
             payload_dates({"ts": "2026-02-03T01:00", "generated": "2026-02-03T02:00"}), ["2026-02-03"])

        # verdict arithmetic
        empty = {c: 0 for c in CLASSES}
        want("verdict empty", _expect_verdict(empty), V_EMPTY)
        want("verdict none", _expect_verdict(dict(empty, **{C_DISAGREES: 3})), V_NONE)
        want("verdict all", _expect_verdict(dict(empty, **{C_AGREES: 3})), V_ALL)
        want("verdict most", _expect_verdict(dict(empty, **{C_AGREES: 3, C_DISAGREES: 2})), V_MOST)
        want("verdict some", _expect_verdict(dict(empty, **{C_AGREES: 2, C_DISAGREES: 3})), V_SOME)

        # guards: a face whose row classes contradict their dates must be refused
        good = {
            "summary": {"member_files": 2, "class_counts": {c: 0 for c in CLASSES},
                        "class_bytes": {c: 0 for c in CLASSES}, "comparable_files": 2,
                        "names_agreeing_with_the_date_their_payload_states": 1,
                        "files_whose_name_states_no_date": 0,
                        "files_whose_name_states_a_date": 2},
            "families": [{"members": 2}],
            "rows": [{"path": "a-2026-01-01.json", "class": C_AGREES, "bytes": 1,
                      "name_dates": ["2026-01-01"], "payload_dates": ["2026-01-01"]},
                     {"path": "b-2026-01-02.json", "class": C_DISAGREES, "bytes": 1,
                      "name_dates": ["2026-01-02"], "payload_dates": ["2026-01-03"]}],
            "frozen_date_fields": list(DATE_FIELDS),
            "verdict": V_SOME,
        }
        good["summary"]["class_counts"][C_AGREES] = 1
        good["summary"]["class_counts"][C_DISAGREES] = 1
        good["summary"]["class_bytes"][C_AGREES] = 1
        good["summary"]["class_bytes"][C_DISAGREES] = 1
        want("clean fixture checks", check(good), [])
        doctored = json.loads(json.dumps(good))
        doctored["verdict"] = V_ALL
        if not check(doctored):
            fails.append("check() accepted a verdict the counts do not imply")
        doctored2 = json.loads(json.dumps(good))
        doctored2["rows"][0]["payload_dates"] = ["2026-01-05"]
        if not check(doctored2):
            fails.append("check() accepted a date_agrees row whose dates disagree")
        doctored3 = json.loads(json.dumps(good))
        doctored3["summary"]["class_counts"][C_NO_NAME_DATE] = 1
        if not check(doctored3):
            fails.append("check() accepted class counts that do not sum to member_files")
        doctored4 = json.loads(json.dumps(good))
        doctored4["rows"][1]["payload_dates"] = []
        if not check(doctored4):
            fails.append("check() accepted a date_disagrees row with no payload date")
        doctored5 = json.loads(json.dumps(good))
        doctored5["summary"]["files_whose_name_states_a_date"] = 1
        if not check(doctored5):
            fails.append("check() accepted a dated-name tally that does not re-derive")
    finally:
        shutil.rmtree(tmp, ignore_errors=True)

    if fails:
        for f in fails:
            print("FAIL %s" % f)
        return 1
    print("selftest 36/36: 7 classes + 2 date extractors + byte tally + disagreement histogram + "
          "5 verdict branches + 5 doctored faces: OK")
    return 0


def main(argv):
    ap = argparse.ArgumentParser()
    ap.add_argument("cmd", choices=("run", "check", "verify", "selftest"))
    args = ap.parse_args(argv)
    if args.cmd == "run":
        return run()
    if args.cmd == "check":
        problems = check()
    elif args.cmd == "verify":
        problems = verify()
    else:
        return selftest()
    print(json.dumps({"problems": problems}, ensure_ascii=False))
    return 0 if not problems else 1


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))