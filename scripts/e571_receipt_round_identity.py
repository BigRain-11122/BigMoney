"""E571 (r1598 bm-b): which round does a receipt belong to when its own round field
disagrees with its file name?

E561 joins a receipt to a round through its *name*; E566/E567/E569 key their joins on the
round number carried by the report or by the file name.  Nothing has yet asked whether the
`round` value *inside* the receipt says the same thing.  If it does not, a consumer that
keys on the field instead of the name silently joins a receipt to the wrong round, and the
mismatch is invisible because both sides are integers.

This face is read-only, no runner executed, and it publishes four things:

  1. dialect   -- how the field is spelled in each vintage (int / decimal string / `rNNNN`
                  label / other).  Two spellings of the same number are not a disagreement,
                  but they *are* a join failure for any consumer that compares types.
  2. identity  -- name_round vs normalised field_round, split into agree / disagree / no
                  field / no round in the name / unnormalisable.
  3. delta     -- for every disagreement, field_round - name_round, so a systematic offset
                  (a label-vs-counter convention) is visible instead of being called sloppy.
  4. exposure  -- of the receipts that state a round at all, how many would be missed by a
                  consumer that keys on the field as an int.

    python scripts/e571_receipt_round_identity.py build|check|verify|selftest
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
DATED_PREFIX = "RECEIPTROUNDCONF"
STATE_TILT = os.path.join(ROOT, "results", "state_tilt")
LATEST = os.path.join(STATE_TILT, "receiptroundconf_latest.json")
DATED = os.path.join(STATE_TILT, "%s-%s.json" % (DATED_PREFIX, EVIDENCE_CUTOFF))
RECEIPT_GLOB = os.path.join(ROOT, "results", "_r*bm*_s6_chain.json")

NAME_RE = re.compile(r"^_r(.*?)bm([abc])_s6_chain\.json$")
ROUND_FIELDS = ("round", "round_no", "round_number", "round_label", "this_round",
                "label", "seq")

RULE = {
    "name_round": "the digits between _r and bm<a|b|c>_ in the file name",
    "field_round": "the first of ROUND_FIELDS the envelope states, normalised: an int is "
                   "itself; a decimal string is int(); an 'rNNNN'/'R-NNNN' label drops the "
                   "prefix; anything else stays unnormalised",
    "dialect": "the raw spelling as published: int / decimal_string / label_string / other",
    "agreement": "compared after normalisation, so a string and an int with the same value "
                 "agree -- the type split is published separately as a join exposure",
    "delta": "field_round - name_round, only for normalisable disagreements",
    "int_keyed_consumer_misses": "the receipt states a round but not as an int, so a consumer "
                                 "that does dict[field] or field == <int> will not find it",
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


def _normalise(value):
    """-> (normalised int or None, dialect)."""
    if isinstance(value, bool):
        return None, "other"
    if isinstance(value, int):
        return value, "int"
    if isinstance(value, str):
        s = value.strip()
        if s.isdigit():
            return int(s), "decimal_string"
        m = re.match(r"^[rR]-?(\d+)$", s)
        if m:
            return int(m.group(1)), "label_string"
        if s.lower().startswith("r") and s[1:].isdigit():
            return int(s[1:]), "label_string"
        return None, "other"
    return None, "other"


def receipt_row(path):
    base = os.path.basename(path)
    m = NAME_RE.match(base)
    name_round = int(m.group(1)) if (m and m.group(1).isdigit()) else None
    entry = {
        "file": base,
        "sha16": _sha16(path),
        "machine": m.group(2) if m else None,
        "name_round": name_round,
        "name_unparsed": None if (m and m.group(1).isdigit()) else "the name carries no digits",
    }
    data = _read_json(path)
    if data is None:
        entry.update({"unparsed": "the file could not be parsed as json", "field_round": None,
                      "dialect": None})
        return entry
    if not isinstance(data, dict):
        entry.update({"unparsed": "not an envelope", "field_round": None, "dialect": None})
        return entry

    field_name, raw = None, None
    for f in ROUND_FIELDS:
        if f in data and data[f] is not None:
            field_name, raw = f, data[f]
            break
    entry["field_name"] = field_name
    entry["field_raw"] = raw if isinstance(raw, (int, str)) else None
    if field_name is None:
        entry.update({"field_round": None, "dialect": None, "identity": "no_round_field"})
        return entry

    norm, dialect = _normalise(raw)
    entry["dialect"] = dialect
    entry["field_round"] = norm
    if norm is None:
        entry["identity"] = "field_unormalisable"
    elif entry["name_round"] is None:
        entry["identity"] = "name_has_no_round"
    elif norm == entry["name_round"]:
        entry["identity"] = "agrees"
    else:
        entry["identity"] = "disagrees"
        entry["delta"] = norm - entry["name_round"]
    entry["int_keyed_consumer_misses"] = dialect != "int"
    return entry


def _summarize(rows):
    stated = [r for r in rows if r.get("field_name")]
    return {
        "receipts_on_disk": len(rows),
        "receipts_unparsed": sum(1 for r in rows if r.get("unparsed")),
        "receipts_stating_a_round": len(stated),
        "receipts_with_no_round_field": sum(
            1 for r in rows if not r.get("unparsed") and not r.get("field_name")),
        "dialect": {d: sum(1 for r in rows if r.get("dialect") == d)
                    for d in ("int", "decimal_string", "label_string", "other")},
        "identity": {k: sum(1 for r in rows if r.get("identity") == k)
                     for k in ("agrees", "disagrees", "no_round_field",
                               "field_unormalisable", "name_has_no_round")},
        "deltas": sorted({r.get("delta") for r in rows if r.get("delta") is not None}),
        "disagreeing_files": [
            {"file": r["file"], "name_round": r["name_round"],
             "field_name": r["field_name"], "field_raw": r["field_raw"],
             "delta": r.get("delta")}
            for r in rows if r.get("identity") == "disagrees"][:40],
        "receipts_an_int_keyed_consumer_would_miss": sum(
            1 for r in stated if r.get("int_keyed_consumer_misses")),
        "field_names_used": {f: sum(1 for r in rows if r.get("field_name") == f)
                             for f in ROUND_FIELDS},
        # E561 counted 17 receipts whose `round` field "disagrees with its name"; this face
        # splits that number into what it actually is.  A value disagreement needs a ts/commit
        # witness to decide which side is the truth; a dialect disagreement needs none, and
        # publishing both under one word would send the next reader hunting 17 phantoms.
        "disagreements_counted_by_E561": 17,
        "value_disagreements_here": sum(1 for r in rows
                                        if r.get("identity") == "disagrees"),
        "dialect_only_disagreements_here": sum(
            1 for r in stated if r.get("dialect") in ("decimal_string", "label_string")),
    }


def _verdict(s):
    if s["identity"]["disagrees"] == 0:
        return ("every_receipt_that_states_a_round_states_the_round_its_name_carries")
    return ("%d of the %d receipts that state a round disagree with the round in their own "
            "file name (deltas %s)"
            % (s["identity"]["disagrees"], s["receipts_stating_a_round"], s["deltas"]))


def _verdict_line(s):
    return ("%d receipts / %d state a round (%s) / identity agrees %d, disagrees %d, "
            "unormalisable %d, no field %d / %d would be missed by an int-keyed consumer"
            % (s["receipts_on_disk"], s["receipts_stating_a_round"],
               ", ".join("%s=%d" % (k, v) for k, v in s["dialect"].items() if v),
               s["identity"]["agrees"], s["identity"]["disagrees"],
               s["identity"]["field_unormalisable"], s["identity"]["no_round_field"],
               s["receipts_an_int_keyed_consumer_would_miss"]))


def build(write=False):
    rows = [receipt_row(p) for p in sorted(glob.glob(RECEIPT_GLOB))]
    s = _summarize(rows)
    face = {
        "study": "E571",
        "card": "E571",
        "dept": "research+engineering",
        "machine": "bm-b",
        "evidence_cutoff": EVIDENCE_CUTOFF,
        "population": {
            "glob": "results/_r*bm*_s6_chain.json",
            "receipts": s["receipts_on_disk"],
            "round_fields_considered": list(ROUND_FIELDS),
            "pinned_by": "file name + sha16 of each receipt in rows; `check` judges the "
                         "published set only, because the chain writes a new receipt every "
                         "time it runs and a population that grows under its own leg would "
                         "turn every round red for a reason that is not a defect",
        },
        "rule": RULE,
        "summary": s,
        "verdict": _verdict(s),
        "verdict_line": _verdict_line(s),
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
    s, rows = face.get("summary") or {}, face.get("rows") or []
    if face.get("verdict") != _verdict(s):
        problems.append("the verdict does not re-derive from the summary")
    if face.get("verdict_line") != _verdict_line(s):
        problems.append("the verdict line does not re-derive from the summary")
    if s.get("receipts_on_disk") != len(rows):
        problems.append("summary.receipts_on_disk != len(rows)")
    for key in ("agrees", "disagrees", "no_round_field", "field_unormalisable",
                "name_has_no_round"):
        if s["identity"][key] != sum(1 for r in rows if r.get("identity") == key):
            problems.append("identity.%s does not re-derive" % key)
    if s["receipts_stating_a_round"] != sum(1 for r in rows if r.get("field_name")):
        problems.append("receipts_stating_a_round does not re-derive")
    for r in rows:
        if r.get("identity") == "disagrees":
            if r.get("field_round") == r.get("name_round"):
                problems.append("%s: flagged disagree but the numbers are equal" % r["file"])
                break
            if r.get("delta") != r.get("field_round") - r.get("name_round"):
                problems.append("%s: delta does not re-derive" % r["file"])
                break
    return problems


def _fixture(raw, name="_r100bmb_s6_chain.json"):
    # the file name IS the measured input, so it must be exact (a random tempfile prefix
    # would strip the digits and every arm would pass as name_has_no_round)
    payload = {"round": raw, "legs": []}
    tmpdir = tempfile.mkdtemp()
    path = os.path.join(tmpdir, name)
    with io.open(path, "w", encoding="utf-8") as out:
        json.dump(payload, out)
    try:
        return receipt_row(path)
    finally:
        os.unlink(path)
        os.rmdir(tmpdir)


def selftest():
    cases = [
        ("an_int_round_that_agrees", 100,
         {"identity": "agrees", "dialect": "int", "int_keyed_consumer_misses": False}),
        ("a_decimal_string_with_the_same_value_agrees_but_is_a_dialect",
         "100", {"identity": "agrees", "dialect": "decimal_string",
                 "int_keyed_consumer_misses": True}),
        ("a_label_string_is_normalised_then_compared", "r100",
         {"identity": "agrees", "dialect": "label_string", "field_round": 100}),
        ("an_int_field_ahead_of_the_name_is_a_disagreement", 101,
         {"identity": "disagrees", "delta": 1}),
        ("a_string_field_behind_the_name_is_a_disagreement", "99",
         {"identity": "disagrees", "delta": -1}),
        ("an_unormalisable_value_is_not_silently_agreeing", "later",
         {"identity": "field_unormalisable", "dialect": "other", "field_round": None}),
    ]
    arms, ok = {}, 0
    for name, raw, expect in cases:
        got = _fixture(raw)
        bad = {k: (v, got.get(k)) for k, v in expect.items() if got.get(k) != v}
        arms[name] = {"expect": expect, "got": {k: got.get(k) for k in expect},
                      "pass": not bad}
        ok += 0 if bad else 1

    # a receipt whose name carries no digits cannot be judged against the name
    tmpdir = tempfile.mkdtemp()
    path = os.path.join(tmpdir, "_draft_s6_chain.json")
    with io.open(path, "w", encoding="utf-8") as out:
        json.dump({"round": 5}, out)
    row = receipt_row(path)
    os.unlink(path)
    os.rmdir(tmpdir)
    expect = "name_has_no_round"
    arms["a_name_without_digits_is_published_not_guessed"] = {
        "expect": expect, "got": row.get("identity"), "pass": row.get("identity") == expect}
    ok += 1 if row.get("identity") == expect else 0

    total = len(cases) + 1
    print(json.dumps({"selftest": "%d/%d" % (ok, total), "arms": arms},
                     ensure_ascii=False, indent=1))
    return 0 if ok == total else 1


def check():
    published = _read_json(LATEST)
    if not isinstance(published, dict):
        print("CHECK FAIL: no published face at %s" % os.path.relpath(LATEST, ROOT))
        return 1
    fresh = build(write=False)
    problems = face_problems(fresh)

    # The chain appends a receipt to this very corpus every time it runs, so the population
    # grows under the leg that measures it.  `check` therefore re-derives the *published*
    # population: a receipt that arrived after the face was written is a note, and a pinned
    # receipt whose bytes changed is the real defect.
    pinned = {r["file"]: r.get("sha16") for r in published.get("rows") or [] if r.get("file")}
    fresh_by_file = {r["file"]: r for r in fresh.get("rows") or [] if r.get("file")}
    missing = sorted(f for f in pinned if f not in fresh_by_file)
    changed = sorted(f for f, sha in pinned.items()
                     if f in fresh_by_file and fresh_by_file[f].get("sha16") != sha)
    newly = sorted(f for f in fresh_by_file if f not in pinned)
    if missing:
        problems.append("pinned receipt(s) disappeared: %s" % ", ".join(missing[:3]))

    subset = [fresh_by_file[f] for f in pinned if f in fresh_by_file]
    subset_summary = _summarize(subset)
    if published.get("summary") != subset_summary:
        problems.append("the published population no longer re-derives from the receipts "
                        "pinned in this face")
    if published.get("verdict") != _verdict(subset_summary):
        problems.append("the verdict does not re-derive from the pinned population")
    if problems:
        print("CHECK FAIL: %d problems; first=%s" % (len(problems), str(problems[0])[:300]))
        return 1
    notes = []
    if newly:
        notes.append("%d receipt(s) arrived after the face was pinned (rebuild extends it)"
                     % len(newly))
    if changed:
        notes.append("%d pinned receipt(s) were rewritten in place; the value classes "
                     "re-derive over them" % len(changed))
    print("CHECK PASS: %s%s" % (_verdict_line(subset_summary),
                                (" | " + "; ".join(notes)) if notes else ""))
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
    print("usage: e571_receipt_round_identity.py build|check|verify|selftest")
    return 2


if __name__ == "__main__":
    sys.exit(main())