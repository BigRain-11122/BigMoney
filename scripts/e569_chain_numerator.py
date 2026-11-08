"""E569 -- does the numerator a chain sentence prints equal the rc0 count of its own receipt?

E567 priced the prose and E570 traced the runners' print expression.  Both stopped at the
sentences that already have a receipt.  This card asks the narrower arithmetic question over
the whole on-disk receipt corpus:  a receipt carries a `legs` array and (sometimes) a stated
rc0 count; if the stated count is not what a recount of its own rows gives, then every
sentence that quotes it inherits the drift, and a sentence can be *green* while the row it
dropped was the one that failed.

Three arms, all read-only and no runner executed:

  1. recount       -- per receipt, rows / rows-without-rc / failing rows / derived rc0
                      against whatever count field the envelope actually states.
                      An absent field is not a field that disagrees (E570's split, kept).
  2. completeness  -- does the file's own row count equal the table it claims
                      (`legs_total`, or `total`/`finished` when the envelope states it)?
                      Reuses E561's class when the file is in that face, so this face never
                      re-derives a class a published face already owns.
  3. printed       -- machine-read E567's claim join (printed numerator, receipt rc0) rather
                      than re-parsing the reports; publish every pair that differs and say
                      whether a dropped row was a failing row.

A receipt whose rows carry no `rc` at all cannot decide arm 3; that is published as
`rows_without_rc` and excluded from the arithmetic, never silently counted as green.

    python scripts/e569_chain_numerator.py build      # write dated face + latest
    python scripts/e569_chain_numerator.py check      # re-derive from disk, compare to published
    python scripts/e569_chain_numerator.py verify     # re-derive, print problems
    python scripts/e569_chain_numerator.py selftest   # offline arms
"""

import glob
import hashlib
import io
import json
import os
import re
import sys
import tempfile

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
EVIDENCE_CUTOFF = "2026-11-08"
DATED_PREFIX = "CHAINNUMERATOR"
STATE_TILT = os.path.join(ROOT, "results", "state_tilt")
LATEST = os.path.join(STATE_TILT, "chainnumerator_latest.json")
DATED = os.path.join(STATE_TILT, "%s-%s.json" % (DATED_PREFIX, EVIDENCE_CUTOFF))
CLAIMS_FACE = os.path.join(STATE_TILT, "CHAINCLAIM-2026-11-08.json")
RECEIPTTABLE_FACE = os.path.join(STATE_TILT, "RECEIPTTABLE-2026-11-08.json")

RECEIPT_GLOB = os.path.join(ROOT, "results", "_r*bm*_s6_chain.json")

# count fields seen across the corpus, in the order this face trusts them
RC0_FIELDS = ("legs_rc0", "nonzero_count", "legs_nonzero", "nonzero_legs", "nonzero")
TOTAL_FIELDS = ("legs_total", "total", "finished", "end")

COUNT_RULE = {
    "derived_rc0": "len(rows) - sum(1 for r in rows if r.get('rc') not in (0, None))",
    "stated_rc0": "first of %s that the envelope states as an int" % (RC0_FIELDS,),
    "offset_fields": "nonzero_count/legs_nonzero/nonzero_legs/nonzero state the *failures*; "
                     "their rc0 is len(rows) - value",
    "absent_is_not_disagreeing": "a receipt with no count field is published with "
                                 "stated_field=null and never in the disagreeing set",
    "understates_its_own_rc0": "stated_rc0 < derived_rc0 -- the number the sentence prints "
                               "drops green rows its own file carries",
    "claims_a_failing_row_is_green": "stated_rc0 > derived_rc0 while failing_rows > 0 -- the "
                                     "sentence prints a failure as a pass",
}


def _read_json(path):
    try:
        return json.load(io.open(path, encoding="utf-8-sig"))
    except Exception:
        return None


def _sha16(path):
    try:
        with io.open(path, "rb") as fh:
            return hashlib.sha256(fh.read()).hexdigest()[:16]
    except Exception:
        return ""


def _rows_of(data):
    if isinstance(data, list):
        return data, "a_bare_list_of_rows"
    if isinstance(data, dict):
        for k in ("legs", "rows", "results"):
            if isinstance(data.get(k), list):
                return data[k], "an_envelope_with_rows"
        return [], "an_envelope_without_rows"
    return [], "neither_a_list_nor_an_envelope"


def receipt_row(path):
    data = _read_json(path)
    base = os.path.basename(path)
    m = re.match(r"^_r(.*?)bm([abc])_s6_chain\.json$", base)
    entry = {
        "file": base,
        "machine": (m.group(2) if m else None),
        "name_round": (int(m.group(1)) if m and m.group(1).isdigit() else None),
        "unparsed": None,
    }
    if data is None:
        entry.update({"unparsed": "the file could not be parsed as json", "rows": None})
        return entry
    rows, shape = _rows_of(data)
    entry["shape"] = shape
    entry["rows"] = len(rows)
    entry["rows_without_rc"] = sum(1 for r in rows
                                   if not isinstance(r, dict) or "rc" not in r)
    entry["failing_rows"] = sum(1 for r in rows
                                if isinstance(r, dict) and r.get("rc") not in (0, None))
    measured = len(rows) - entry["rows_without_rc"]
    entry["derived_rc0"] = (measured - entry["failing_rows"]) if rows else None

    stated_field, stated_value, is_offset = None, None, False
    if isinstance(data, dict):
        for f in RC0_FIELDS:
            if isinstance(data.get(f), int):
                stated_field, stated_value = f, data[f]
                is_offset = f != "legs_rc0"
                break
    entry["stated_field"] = stated_field
    entry["stated_rc0"] = (None if stated_field is None else
                           (len(rows) - stated_value if is_offset else stated_value))
    entry["stated_is_an_offset_field"] = is_offset if stated_field else None
    entry["count_agrees_with_its_own_rows"] = (
        None if entry["stated_rc0"] is None or entry["derived_rc0"] is None
        else entry["stated_rc0"] == entry["derived_rc0"])

    total = None
    if isinstance(data, dict):
        for f in TOTAL_FIELDS:
            v = data.get(f)
            if isinstance(v, int):
                total = v
                entry["total_field"] = f
                break
    entry["stated_total"] = total
    entry["completeness"] = ("unknown" if total is None
                             else ("complete" if total == len(rows) else "subset"))

    entry["understates_its_own_rc0"] = bool(
        entry["stated_rc0"] is not None and entry["derived_rc0"] is not None
        and entry["stated_rc0"] < entry["derived_rc0"])
    entry["claims_a_failing_row_is_green"] = bool(
        entry["stated_rc0"] is not None and entry["derived_rc0"] is not None
        and entry["stated_rc0"] > entry["derived_rc0"] and entry["failing_rows"] > 0)
    return entry


def _claims():
    face = _read_json(CLAIMS_FACE)
    if not isinstance(face, dict):
        return None
    return face.get("claims") or []


def _receipt_table():
    face = _read_json(RECEIPTTABLE_FACE)
    if not isinstance(face, dict):
        return {}
    return {r.get("file"): r for r in face.get("rows") or [] if r.get("file")}


def _summarize(rows, joined):
    with_count = [r for r in rows if r.get("stated_rc0") is not None]
    disagree = [r for r in with_count if r.get("count_agrees_with_its_own_rows") is False]
    return {
        "receipts_on_disk": len(rows),
        "receipts_parsed": sum(1 for r in rows if r.get("rows") is not None),
        "receipts_unparsed": sum(1 for r in rows if r.get("unparsed")),
        "receipts_stating_a_count": len(with_count),
        "receipts_stating_no_count": (sum(1 for r in rows if r.get("rows") is not None)
                                     - len(with_count)),
        "count_fields_used": {f: sum(1 for r in rows if r.get("stated_field") == f)
                              for f in RC0_FIELDS},
        "count_agrees_with_its_own_rows": sum(
            1 for r in with_count if r.get("count_agrees_with_its_own_rows")),
        "count_disagrees_with_its_own_rows": len(disagree),
        "offset_style_fields_in_disagreements": sum(
            1 for r in disagree if r.get("stated_is_an_offset_field")),
        "completeness": {k: sum(1 for r in rows if r.get("completeness") == k)
                         for k in ("complete", "subset", "unknown")},
        "receipts_understating_their_own_rc0": sum(
            1 for r in rows if r.get("understates_its_own_rc0")),
        "receipts_claiming_a_failing_row_is_green": sum(
            1 for r in rows if r.get("claims_a_failing_row_is_green")),
        "files_claiming_a_failing_row_is_green": [
            r["file"] for r in rows if r.get("claims_a_failing_row_is_green")][:20],
        "receipts_with_rows_missing_rc": sum(
            1 for r in rows if (r.get("rows_without_rc") or 0) > 0),
        "joined_to_a_printed_sentence": len(joined),
        "printed_numerator_equals_derived_rc0": sum(
            1 for r in joined if r["printed_matches_derived_rc0"]),
        "printed_numerator_differs_from_derived_rc0": sum(
            1 for r in joined if not r["printed_matches_derived_rc0"]),
        "disagreeing_files": [
            {"file": r["file"], "stated_field": r["stated_field"],
             "stated_rc0": r["stated_rc0"], "derived_rc0": r["derived_rc0"],
             "rows": r["rows"], "failing_rows": r["failing_rows"]}
            for r in disagree][:40],
    }


def _verdict(summary):
    if summary["count_disagrees_with_its_own_rows"] == 0:
        return ("every_receipt_that_states_an_rc0_count_states_the_count_its_own_rows_give")
    return ("%d of the %d receipts that state an rc0 count state a number their own rows do "
            "not give; %d of those state an offset field instead of an rc0"
            % (summary["count_disagrees_with_its_own_rows"],
               summary["receipts_stating_a_count"],
               summary["offset_style_fields_in_disagreements"]))


def _verdict_line(s):
    return ("%d receipts / %d state a count (%d agree, %d disagree, %d offset-style) / "
            "%d understate / %d claim-a-red-row-green / %d joined to a printed sentence "
            "(%d equal, %d differ)"
            % (s["receipts_on_disk"], s["receipts_stating_a_count"],
               s["count_agrees_with_its_own_rows"], s["count_disagrees_with_its_own_rows"],
               s["offset_style_fields_in_disagreements"],
               s["receipts_understating_their_own_rc0"],
               s["receipts_claiming_a_failing_row_is_green"],
               s["joined_to_a_printed_sentence"],
               s["printed_numerator_equals_derived_rc0"],
               s["printed_numerator_differs_from_derived_rc0"]))


def build(write=False):
    receipts = [receipt_row(p) for p in sorted(glob.glob(RECEIPT_GLOB))]
    claims = _claims()
    table = _receipt_table()

    # published numerator per (round, machine) -- reuse E567's join, never re-parse the prose
    printed = {}
    for c in claims or []:
        if c.get("receipt") is None:
            continue
        printed.setdefault((c.get("round"), c.get("machine")), []).append(c)

    rows = []
    for r in receipts:
        if r.get("rows") is not None:
            r["receipt_class_per_E561"] = (table.get(r["file"]) or {}).get("class")
            ps = printed.get((r["name_round"], r["machine"])) or []
            if ps:
                c = ps[0]
                r["printed_numerator"] = c.get("numerator")
                r["printed_denominator"] = c.get("denominator")
                r["printed_report"] = c.get("report")
                r["printed_sentence"] = (c.get("sentence") or "")[:240]
                r["printed_matches_derived_rc0"] = (
                    None if r["derived_rc0"] is None
                    else c.get("numerator") == r["derived_rc0"])
            else:
                r["printed_numerator"] = None
                r["printed_matches_derived_rc0"] = None
        rows.append(r)

    joined = [r for r in rows if r.get("printed_matches_derived_rc0") is not None]
    summary = _summarize(rows, joined)
    face = {
        "study": "E569",
        "card": "E569",
        "dept": "research+engineering",
        "machine": "bm-b",
        "round": None,
        "evidence_cutoff": EVIDENCE_CUTOFF,
        "population": {
            "glob": "results/_r*bm*_s6_chain.json",
            "receipts": summary["receipts_on_disk"],
            "join_face": os.path.relpath(CLAIMS_FACE, ROOT).replace(os.sep, "/"),
            "join_face_sha16": _sha16(CLAIMS_FACE),
            "class_face": os.path.relpath(RECEIPTTABLE_FACE, ROOT).replace(os.sep, "/"),
            "class_face_sha16": _sha16(RECEIPTTABLE_FACE),
        },
        "count_rule": COUNT_RULE,
        "summary": summary,
        "verdict": _verdict(summary),
        "verdict_line": _verdict_line(summary),
        "rows": rows,
    }
    if write:
        _write(DATED, face)
        _write(LATEST, face)
    return face


def _write(path, obj):
    tmp = path + ".tmp"
    with io.open(tmp, "w", encoding="utf-8", newline="\n") as fh:
        json.dump(obj, fh, ensure_ascii=False, indent=1)
        fh.write("\n")
    os.replace(tmp, path)


def face_problems(face):
    problems = []
    s, rows = face["summary"], face["rows"]
    if face.get("verdict") != _verdict(s):
        problems.append("the verdict does not re-derive from the summary")
    if face.get("verdict_line") != _verdict_line(s):
        problems.append("the verdict line does not re-derive from the summary")
    if s["receipts_on_disk"] != len(rows):
        problems.append("summary.receipts_on_disk != len(rows)")
    agree = sum(1 for r in rows if r.get("count_agrees_with_its_own_rows") is True)
    dis = sum(1 for r in rows if r.get("count_agrees_with_its_own_rows") is False)
    if agree + dis != s["receipts_stating_a_count"]:
        problems.append("agree+disagree != receipts_stating_a_count")
    if s["count_disagrees_with_its_own_rows"] != dis:
        problems.append("summary disagrees-count != recount")
    for r in rows:
        st, dv = r.get("stated_rc0"), r.get("derived_rc0")
        if st is not None and dv is not None:
            if r.get("count_agrees_with_its_own_rows") != (st == dv):
                problems.append("%s: agree flag does not re-derive" % r["file"])
                break
    joined = [r for r in rows if r.get("printed_matches_derived_rc0") is not None]
    if s["joined_to_a_printed_sentence"] != len(joined):
        problems.append("joined count != printed-joined rows")
    if s["receipts_understating_their_own_rc0"] != sum(
            1 for r in rows if r.get("understates_its_own_rc0")):
        problems.append("understates count does not re-derive")
    if s["receipts_claiming_a_failing_row_is_green"] != sum(
            1 for r in rows if r.get("claims_a_failing_row_is_green")):
        problems.append("claims-red-green count does not re-derive")
    return problems


def _fixture(payload):
    fh = tempfile.NamedTemporaryFile("w", suffix="_r1bmb_s6_chain.json",
                                     delete=False, encoding="utf-8")
    with fh as out:
        json.dump(payload, out)
    row = receipt_row(fh.name)
    os.unlink(fh.name)
    return row


def selftest():
    cases = [
        ("a_complete_envelope_with_true_rc0",
         {"legs_total": 3, "legs_rc0": 2, "legs": [{"rc": 0}, {"rc": 0}, {"rc": 2}]},
         {"derived_rc0": 2, "count_agrees_with_its_own_rows": True,
          "completeness": "complete", "understates_its_own_rc0": False}),
        ("a_stated_rc0_below_its_own_rows",
         {"legs_total": 3, "legs_rc0": 1, "legs": [{"rc": 0}, {"rc": 0}, {"rc": 2}]},
         {"derived_rc0": 2, "count_agrees_with_its_own_rows": False,
          "completeness": "complete", "understates_its_own_rc0": True,
          "claims_a_failing_row_is_green": False}),
        ("a_stated_rc0_above_its_own_rows_when_a_row_failed",
         {"legs_total": 3, "legs_rc0": 3, "legs": [{"rc": 0}, {"rc": 0}, {"rc": 2}]},
         {"derived_rc0": 2, "count_agrees_with_its_own_rows": False,
          "completeness": "complete", "understates_its_own_rc0": False,
          "claims_a_failing_row_is_green": True}),
        ("an_offset_field_is_converted_not_compared_raw",
         {"total": 3, "nonzero_count": 1, "legs": [{"rc": 0}, {"rc": 0}, {"rc": 2}]},
         {"stated_field": "nonzero_count", "stated_rc0": 2,
          "count_agrees_with_its_own_rows": True, "completeness": "complete"}),
        ("a_subset_envelope",
         {"legs_total": 51, "legs_rc0": 2, "legs": [{"rc": 0}, {"rc": 0}]},
         {"completeness": "subset", "count_agrees_with_its_own_rows": True}),
        ("a_receipt_with_no_count_field_is_not_a_disagreement",
         {"legs": [{"rc": 0}, {"rc": 1}]},
         {"stated_rc0": None, "count_agrees_with_its_own_rows": None, "derived_rc0": 1}),
        ("rows_without_rc_are_excluded_not_counted_green",
         {"legs_rc0": 1, "legs": [{"rc": 0}, {"tail": "no rc"}]},
         {"rows_without_rc": 1, "derived_rc0": 1,
          "count_agrees_with_its_own_rows": True}),
        ("a_bare_list_of_rows",
         [{"rc": 0}, {"rc": 0}],
         {"shape": "a_bare_list_of_rows", "derived_rc0": 2, "stated_field": None}),
    ]
    arms, ok = {}, 0
    for name, payload, expect in cases:
        got = _fixture(payload)
        bad = {k: (v, got.get(k)) for k, v in expect.items() if got.get(k) != v}
        arms[name] = {"expect": expect, "got": {k: got.get(k) for k in expect},
                      "pass": not bad}
        ok += 0 if bad else 1
    print(json.dumps({"selftest": "%d/%d" % (ok, len(cases)), "arms": arms},
                     ensure_ascii=False, indent=1))
    return 0 if ok == len(cases) else 1


def check():
    published = _read_json(LATEST)
    if not isinstance(published, dict):
        print("CHECK FAIL: no published face at %s" % os.path.relpath(LATEST, ROOT))
        return 1
    fresh = build(write=False)
    problems = face_problems(fresh)

    # The chain writes a new receipt into this corpus every time it runs, so the population
    # grows under the leg that measures it and a whole-corpus compare went red every round
    # (r1598 saw the leg red for a receipt the chain itself had just appended).  `check`
    # therefore re-derives the *published* population; arrivals are a note, not a defect.
    pinned = {r["file"] for r in published.get("rows") or [] if r.get("file")}
    fresh_by_file = {r["file"]: r for r in fresh.get("rows") or [] if r.get("file")}
    missing = sorted(f for f in pinned if f not in fresh_by_file)
    if missing:
        problems.append("pinned receipt(s) disappeared: %s" % ", ".join(missing[:3]))
    newly = sorted(f for f in fresh_by_file if f not in pinned)

    subset = [fresh_by_file[f] for f in sorted(pinned) if f in fresh_by_file]
    joined_subset = [r for r in subset if r.get("printed_matches_derived_rc0") is not None]
    subset_summary = _summarize(subset, joined_subset)
    if published.get("summary") != subset_summary:
        problems.append("the published population no longer re-derives from the receipts "
                        "pinned in this face")
    if published.get("verdict") != _verdict(subset_summary):
        problems.append("the verdict does not re-derive from the pinned population")
    if problems:
        print("CHECK FAIL: %d problems; first=%s" % (len(problems), str(problems[0])[:300]))
        return 1
    note = (" | %d receipt(s) arrived after the face was pinned (rebuild extends it)"
            % len(newly)) if newly else ""
    print("CHECK PASS: %s%s" % (_verdict_line(subset_summary), note))
    return 0


def verify():
    problems = face_problems(build(write=False))
    print(json.dumps({"problems": problems[:10], "n": len(problems)}, ensure_ascii=False))
    return 0 if not problems else 1


def main(argv=None):
    action = (list(sys.argv[1:] if argv is None else argv) or ["build"])[0]
    if action == "build":
        face = build(write=True)
        print("BUILT %s" % os.path.relpath(LATEST, ROOT))
        print("VERDICT: %s" % face["verdict"])
        print("LINE: %s" % face["verdict_line"])
        return 0
    if action == "check":
        return check()
    if action == "verify":
        return verify()
    if action == "selftest":
        return selftest()
    print("usage: e569_chain_numerator.py build|check|verify|selftest")
    return 2


if __name__ == "__main__":
    sys.exit(main())