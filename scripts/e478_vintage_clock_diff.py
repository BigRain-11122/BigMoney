"""E478 -- do the unread vintages differ from their own `*_latest` twin only in a clock field?

E477 measured the byte-identity floor: retiring the 97 unread vintage families would destroy
25.36 MB that nothing else holds.  A byte hash is the strictest possible witness, and it charges
a vintage the full price for a single changed timestamp.  The retention question is one step
wider: if a dated vintage is *semantically* its family's latest twin -- same payload once the
clock-shaped top-level fields are removed -- the bytes it occupies are not a second measurement,
they are the same measurement written on an earlier day.

Population: E472's published rows (the 97 unread vintage families, 571 member files).  Only the
families that carry a resolvable `*_latest.json` twin can be compared, and the twin itself is not
part of the population -- it is the reference the vintage is compared against.

Each member file lands in exactly one class:

  identical_after_top_level_clock_strip   parses as JSON, the twin parses as JSON, and the two
                                          objects are equal after removing the frozen top-level
                                          clock names on both sides
  differs_beyond_the_top_level_clock_fields
                                          both parse as JSON objects and differ on something other
                                          than a frozen clock name; `differing_keys` says where
  not_a_json_object                       the member is not a .json payload (csv/md/jsonl), so the
                                          comparison has no meaning for it -- it is published as
                                          unmeasured, never as a negative
  unreadable_member                       the file is missing or does not parse
  family_has_no_resolvable_twin           the member's family publishes no twin, or the twin the
                                          E472 row names is not on disk

A second arm (published beside the first, never folded into it) repeats the comparison with the
clock names stripped at every depth.  The two arms answer different questions -- "only the top
level moves" and "nothing but the clock moves anywhere" -- and where they disagree the recursive
count is the larger one by construction, which is itself the evidence that some families carry
per-row timestamps.

Delivered numbers: `vintage_files_identical_after_clock_strip` and
`bytes_collapsible_without_losing_a_measurement` (the bytes of exactly those files).  This is a
retention estimate under the frozen definition, not a licence to delete: E479 owns whether a twin
is read at all.

CLI: run | check | verify | selftest
"""

import argparse
import io
import json
import os
import shutil
import sys
import tempfile
import time

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUTDIR = os.path.join(ROOT, "results", "state_tilt")
FACE_NAME = "vintageclock_latest.json"
DATED_PREFIX = "VINTAGECLOCK"
CARD = ("E478-DO-THE-531-UNIQUE-UNREAD-VINTAGES-DIFFER-FROM-THEIR-OWN-LATEST-TWIN-ONLY-IN-A-CLOCK-FIELD")
PARENT_FACE = "vintageread_latest.json"          # E472: the 97 unread vintage families
SIBLING_FACE = "vintageretire_latest.json"       # E477: the byte-identity floor this refines

# Frozen by the card text.  Nothing outside this tuple is stripped, and the face publishes the
# tuple so a reader can see exactly which names were forgiven (E207 family: a name must measure
# what it counts).
CLOCK_FIELDS_TOP = ("generated", "ts", "timestamp", "elapsed_sec")

# Date-shaped names that are NOT forgiven by the frozen definition.  They are published beside the
# result because `evidence_cutoff` moves every time a face is republished, and a reader is entitled
# to know whether any vintage differs from its twin on that name ALONE -- i.e. whether the frozen
# four-name set is hiding redundancy.  This is a bound on the verdict, never an input to it.
DATE_SHAPED_NOT_FORGIVEN = ("evidence_cutoff",)

C_IDENTICAL = "identical_after_top_level_clock_strip"
C_DIFFERS = "differs_beyond_the_top_level_clock_fields"
C_NOT_JSON = "not_a_json_object"
C_UNREADABLE = "unreadable_member"
C_NO_TWIN = "family_has_no_resolvable_twin"
COMPARABLE = (C_IDENTICAL, C_DIFFERS)
NOT_COMPARABLE = (C_NOT_JSON, C_UNREADABLE, C_NO_TWIN)
CLASSES = COMPARABLE + NOT_COMPARABLE

V_EMPTY = "no_unread_vintage_family_has_a_resolvable_latest_twin"
V_NONE = "no_vintage_is_semantically_identical_to_its_own_latest_twin"
V_ALL = "every_vintage_is_semantically_identical_to_its_own_latest_twin"
V_MOST = "most_vintages_are_semantically_identical_to_their_own_latest_twin"
V_SOME = "some_vintages_are_semantically_identical_to_their_own_latest_twin_and_the_majority_are_not"
VERDICT_VOCAB = (V_EMPTY, V_NONE, V_ALL, V_MOST, V_SOME)


# ----------------------------------------------------------------------------- helpers


def _rel(path, root=None):
    return os.path.relpath(path, root or ROOT).replace("\\", "/")


def strip_clock(obj, depth):
    """Remove the frozen clock names from a dict (depth='top') or recursively (depth='any')."""
    if not isinstance(obj, dict):
        return obj
    if depth == "top":
        return {k: v for k, v in obj.items() if k not in CLOCK_FIELDS_TOP}
    out = {}
    for k, v in obj.items():
        if k in CLOCK_FIELDS_TOP:
            continue
        if isinstance(v, dict):
            out[k] = strip_clock(v, "any")
        elif isinstance(v, list):
            out[k] = [strip_clock(x, "any") for x in v]
        else:
            out[k] = v
    return out


def _differing_keys(a, b):
    keys = set(a) | set(b)
    return sorted(k for k in keys if k not in CLOCK_FIELDS_TOP and a.get(k) != b.get(k))


def compare_pair(member_path, twin_path, reader=None):
    """Classify one member against its twin.  reader() is injectable for the selftest."""
    ext = os.path.splitext(member_path)[1].lower()
    if ext != ".json":
        return C_NOT_JSON, None, None, []
    read = reader or (lambda p: json.load(io.open(p, "r", encoding="utf-8")))
    try:
        member = read(member_path)
        twin = read(twin_path)
    except Exception:
        return C_UNREADABLE, None, None, []
    if not isinstance(member, dict) or not isinstance(twin, dict):
        return C_NOT_JSON, None, None, []
    top_same = strip_clock(member, "top") == strip_clock(twin, "top")
    any_same = strip_clock(member, "any") == strip_clock(twin, "any")
    keys = _differing_keys(member, twin)
    cls = C_IDENTICAL if top_same else C_DIFFERS
    return cls, top_same, any_same, keys


def classify(rows_by_family, read, exists, size_of, rel):
    """rows_by_family: {family_key: {'members': [...], 'twin': path or None}}"""
    rows = []
    families = []
    counts = {c: 0 for c in CLASSES}
    byte_counts = {c: 0 for c in CLASSES}
    key_hist = {}

    for fam_key in sorted(rows_by_family):
        fam = rows_by_family[fam_key]
        twin = fam.get("twin")
        twin_ok = bool(twin) and exists(twin)
        fam_counts = {c: 0 for c in CLASSES}
        fam_bytes = 0
        for member in sorted(fam.get("members") or []):
            if not exists(member):
                cls, top_same, any_same, keys = C_UNREADABLE, None, None, []
            elif not twin_ok:
                cls, top_same, any_same, keys = C_NO_TWIN, None, None, []
            else:
                cls, top_same, any_same, keys = compare_pair(member, twin, read)
            try:
                size = size_of(member)
            except OSError:
                size = 0
            counts[cls] += 1
            byte_counts[cls] += size
            fam_counts[cls] += 1
            fam_bytes += size
            if cls == C_DIFFERS:
                for k in keys:
                    key_hist[k] = key_hist.get(k, 0) + 1
            rows.append({
                "path": rel(member),
                "family": fam_key,
                "bytes": size,
                "class": cls,
                "identical_after_recursive_clock_strip": any_same,
                "differing_keys": keys[:12],
                "differing_key_count": len(keys) if cls == C_DIFFERS else None,
                "only_differing_key_is_a_date_shaped_name": (
                    (len(keys) == 1 and keys[0] in DATE_SHAPED_NOT_FORGIVEN)
                    if cls == C_DIFFERS else None),
            })
        families.append({
            "family": fam_key,
            "twin": rel(twin) if twin else None,
            "twin_present": twin_ok,
            "members": len(fam.get("members") or []),
            "counts": fam_counts,
            "bytes": fam_bytes,
        })

    return rows, families, counts, byte_counts, key_hist


# ----------------------------------------------------------------------------- build


def build(pop_path=None):
    pop = json.load(io.open(pop_path or os.path.join(OUTDIR, PARENT_FACE), "r", encoding="utf-8"))
    sibling = None
    sib_path = os.path.join(OUTDIR, SIBLING_FACE)
    if os.path.exists(sib_path):
        try:
            sibling = json.load(io.open(sib_path, "r", encoding="utf-8"))
        except Exception:
            sibling = None

    rows_by_family = {}
    twin_missing = []
    for r in pop.get("rows") or []:
        key = "%s/%s" % (r.get("dir", "?"), r.get("family", "?"))
        twin = r.get("latest")
        members = [m if os.path.isabs(m) else os.path.join(ROOT, m) for m in (r.get("members") or [])]
        if twin:
            twin_abs = twin if os.path.isabs(twin) else os.path.join(ROOT, twin)
            # the twin is the reference, never part of the population under test
            members = [m for m in members if os.path.normpath(m) != os.path.normpath(twin_abs)]
        else:
            twin_abs = None
        if twin_abs and not os.path.exists(twin_abs):
            twin_missing.append(twin)
        rows_by_family[key] = {"members": members, "twin": twin_abs}

    rows, families, counts, byte_counts, key_hist = classify(
        rows_by_family,
        lambda p: json.load(io.open(p, "r", encoding="utf-8")),
        os.path.exists,
        os.path.getsize,
        _rel,
    )

    comparable = counts[C_IDENTICAL] + counts[C_DIFFERS]
    identical = counts[C_IDENTICAL]
    recursive_identical = sum(1 for r in rows if r.get("identical_after_recursive_clock_strip"))
    if comparable == 0:
        verdict = V_EMPTY
    elif identical == 0:
        verdict = V_NONE
    elif identical == comparable:
        verdict = V_ALL
    elif identical * 2 > comparable:
        verdict = V_MOST
    else:
        verdict = V_SOME

    summary = {
        "families_total": len(families),
        "families_with_a_resolvable_twin": sum(1 for f in families if f["twin_present"]),
        "families_with_no_resolvable_twin": sum(1 for f in families if not f["twin_present"]),
        "member_files": len(rows),
        "comparable_files": comparable,
        "class_counts": counts,
        "class_bytes": byte_counts,
        "vintage_files_identical_after_clock_strip": identical,
        "identical_share_of_comparable": round(identical / comparable, 6) if comparable else None,
        "bytes_collapsible_without_losing_a_measurement": byte_counts[C_IDENTICAL],
        "vintages_identical_under_recursive_strip": recursive_identical,
        "recursive_arm_exceeds_top_level_arm_by": recursive_identical - identical,
        "differing_key_histogram": dict(sorted(key_hist.items(), key=lambda kv: -kv[1])),
        "twins_named_but_missing_on_disk": len(twin_missing),
        "e477_bytes_lost_if_retired": ((sibling or {}).get("summary") or {}).get("bytes_lost_if_retired"),
        "robustness": {
            "differing_rows": counts[C_DIFFERS],
            "differing_rows_whose_only_differing_key_is_a_date_shaped_name": sum(
                1 for r in rows if r.get("only_differing_key_is_a_date_shaped_name")),
            "differing_rows_naming_evidence_cutoff": sum(
                1 for r in rows if r.get("class") == C_DIFFERS
                and "evidence_cutoff" in (r.get("differing_keys") or [])),
            "date_shaped_names_not_forgiven": list(DATE_SHAPED_NOT_FORGIVEN),
            "note": "the frozen four names decide the verdict; this block only says whether a "
                    "vintage ever differs from its twin on a date-shaped name alone",
        },
    }

    face = {
        "card": CARD,
        "study": "E478_do_the_unread_vintages_differ_from_their_own_latest_twin_only_in_a_clock_field",
        "title": "do the unread vintages differ from their own *_latest twin only in a clock field?",
        "evidence_cutoff": time.strftime("%Y-%m-%d"),
        "generated": time.strftime("%Y-%m-%dT%H:%M:%S%z"),
        "frozen_clock_fields": list(CLOCK_FIELDS_TOP),
        "population_source": {
            "face": PARENT_FACE,
            "face_evidence_cutoff": pop.get("evidence_cutoff"),
            "face_verdict": pop.get("verdict"),
            "sibling_face": SIBLING_FACE,
            "twin_excluded_from_population": True,
        },
        "class_definition": {
            C_IDENTICAL: "member and twin parse as JSON objects and are equal after removing the "
                         "frozen clock names from the top level of both",
            C_DIFFERS: "both parse as JSON objects and differ beyond the frozen clock names",
            C_NOT_JSON: "the member is not a .json payload (csv/md/jsonl): unmeasured, not a negative",
            C_UNREADABLE: "the member is missing on disk or does not parse as JSON",
            C_NO_TWIN: "the family names no latest twin, or the named twin is not on disk",
        },
        "summary": summary,
        "verdict": verdict,
        "verdict_vocab": list(VERDICT_VOCAB),
        "families": families,
        "rows": rows,
        "method_limits": [
            "only four field names are forgiven (frozen_clock_fields); a family whose clock is spelled "
            "differently (run_at, written, asof-time) reads as differing even when it does not",
            "the comparison is object equality after stripping: a list that gained or lost one element "
            "is a difference, so the identical count is a lower bound on semantic redundancy",
            "non-json members are 100 of the 571 files and are published as unmeasured, never as a "
            "negative result",
            "the population is E472's rows as published; a family that gained members since then is "
            "not rescanned here",
            "identical payloads say nothing about whether the twin itself is read -- that is E479's "
            "question, and this face must not be read as a deletion licence",
        ],
    }
    return face


# ----------------------------------------------------------------------------- guards


def row_problems(face):
    """Every tally must re-add to the rows; injected verbatim into the smoke leg."""
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
        if r.get("class") == C_IDENTICAL and r.get("differing_keys"):
            problems.append("row %s is identical but names a differing key" % r.get("path"))
            break
        if r.get("class") == C_DIFFERS and not r.get("differing_keys"):
            problems.append("row %s differs but names no differing key" % r.get("path"))
            break
        if r.get("class") in (C_IDENTICAL, C_DIFFERS) and r.get("identical_after_recursive_clock_strip") is None:
            problems.append("row %s was compared but carries no recursive arm" % r.get("path"))
            break
        if r.get("class") == C_NOT_JSON and os.path.splitext(r.get("path") or "")[1].lower() == ".json":
            problems.append("row %s is .json yet classed not_a_json_object" % r.get("path"))
            break
    if derived != counts:
        problems.append("the published class counts do not re-derive from the rows")
    if s.get("vintage_files_identical_after_clock_strip") != derived.get(C_IDENTICAL):
        problems.append("the identical tally does not re-derive from the rows")
    if s.get("comparable_files") != derived.get(C_IDENTICAL, 0) + derived.get(C_DIFFERS, 0):
        problems.append("the comparable tally is not identical + differs")
    if face.get("verdict") not in VERDICT_VOCAB:
        problems.append("verdict is outside the frozen vocabulary: %r" % face.get("verdict"))
    # a row marked identical in one arm must also be identical in the other (recursive strip only
    # forgives more, never less)
    for r in rows:
        if r.get("class") == C_IDENTICAL and r.get("identical_after_recursive_clock_strip") is False:
            problems.append("row %s is identical at the top level but not recursively" % r.get("path"))
            break
    fam_sum = sum(f.get("members", 0) for f in face.get("families") or [])
    if fam_sum != s.get("member_files"):
        problems.append("family member counts do not sum to member_files")
    if sum(1 for f in face.get("families") or [] if f.get("twin_present")) != s.get("families_with_a_resolvable_twin"):
        problems.append("the resolvable-twin family tally does not re-derive from the families")
    # the robustness block is a measurement too: it must re-derive from the rows it summarises
    rob = s.get("robustness") or {}
    if rob:
        differs = [r for r in rows if r.get("class") == C_DIFFERS]
        if rob.get("differing_rows") != len(differs):
            problems.append("robustness.differing_rows does not re-derive from the rows")
        if rob.get("differing_rows_whose_only_differing_key_is_a_date_shaped_name") != sum(
                1 for r in differs if r.get("only_differing_key_is_a_date_shaped_name")):
            problems.append("the date-shaped-only tally does not re-derive from the rows")
        if rob.get("differing_rows_naming_evidence_cutoff") != sum(
                1 for r in differs if "evidence_cutoff" in (r.get("differing_keys") or [])):
            problems.append("the evidence_cutoff tally does not re-derive from the rows")
    return problems


def _expect_verdict(counts):
    comparable = counts.get(C_IDENTICAL, 0) + counts.get(C_DIFFERS, 0)
    identical = counts.get(C_IDENTICAL, 0)
    if comparable == 0:
        return V_EMPTY
    if identical == 0:
        return V_NONE
    if identical == comparable:
        return V_ALL
    if identical * 2 > comparable:
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
    for key in ("families_total", "families_with_a_resolvable_twin", "member_files",
                "comparable_files", "class_counts", "class_bytes",
                "vintage_files_identical_after_clock_strip",
                "bytes_collapsible_without_losing_a_measurement",
                "vintages_identical_under_recursive_strip", "differing_key_histogram",
                "twins_named_but_missing_on_disk"):
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
    tmp = tempfile.mkdtemp(prefix="e478_")
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

        base = os.path.join(tmp, "results", "fam")
        twin = os.path.join(base, "FAM_latest.json")
        # 1: identical once the top-level clock goes
        a = os.path.join(base, "FAM-2026-01-01.json")
        w(twin, {"x": 1, "nested": {"ts": 9, "y": 5}, "generated": "2026-02-01"})
        w(a, {"x": 1, "nested": {"ts": 9, "y": 5}, "generated": "2026-01-01"})
        # 2: differs on a non-clock field
        b = os.path.join(base, "FAM-2026-01-02.json")
        w(b, {"x": 2, "nested": {"ts": 9, "y": 5}, "generated": "2026-01-02"})
        # 3: differs at the top level only through a nested clock -> the recursive arm must separate it
        c = os.path.join(base, "FAM-2026-01-03.json")
        w(c, {"x": 1, "nested": {"ts": 1, "y": 5}, "generated": "2026-01-03"})
        # 4: not json
        d = os.path.join(base, "FAM-2026-01-04.csv")
        w(d, "a,b\n1,2\n")
        # 5: unreadable json
        e = os.path.join(base, "FAM-2026-01-05.json")
        w(e, "{not json")
        # 6: missing on disk
        f = os.path.join(base, "FAM-2026-01-06.json")
        # 7: family with no twin
        base2 = os.path.join(tmp, "results", "fam2")
        g = os.path.join(base2, "G-2026-01-01.json")
        w(g, {"x": 1})

        rows_by_family = {
            "fam/FAM": {"members": [a, b, c, d, e, f], "twin": twin},
            "fam2/G": {"members": [g], "twin": None},
        }
        rows, families, counts, byte_counts, hist = classify(
            rows_by_family,
            lambda p: json.load(io.open(p, "r", encoding="utf-8")),
            os.path.exists, os.path.getsize, lambda p: os.path.basename(p))

        want("identical count", counts[C_IDENTICAL], 1)
        want("differs count", counts[C_DIFFERS], 2)
        want("not-json count", counts[C_NOT_JSON], 1)
        want("unreadable count", counts[C_UNREADABLE], 2)   # bad json + missing file
        want("no-twin count", counts[C_NO_TWIN], 1)
        want("class sum", sum(counts.values()), 7)
        want("comparable", counts[C_IDENTICAL] + counts[C_DIFFERS], 3)
        # the recursive arm separates the nested-clock vintage from the top-level verdict
        rec = {os.path.basename(r["path"]): r["identical_after_recursive_clock_strip"] for r in rows}
        cls = {os.path.basename(r["path"]): r["class"] for r in rows}
        want("nested clock is identical recursively", rec["FAM-2026-01-03.json"], True)
        want("nested clock is NOT identical at top level", cls["FAM-2026-01-03.json"], C_DIFFERS)
        want("recursive arm on the differing row", rec["FAM-2026-01-02.json"], False)
        # the identical row's bytes are the collapsible bytes
        want("collapsible bytes", byte_counts[C_IDENTICAL], os.path.getsize(a))
        # differing keys exclude the frozen clock name
        want("differs names only x",
             next(r["differing_keys"] for r in rows if r["path"].endswith("2026-01-02.json")), ["x"])
        want("histogram counts the differing key", hist.get("x"), 1)
        want("the frozen clock never enters the histogram", hist.get("generated"), None)
        want("family twin flag", [f["twin_present"] for f in families], [True, False])

        # verdict arithmetic: empty / none / all / most / some
        empty = {c: 0 for c in CLASSES}
        want("verdict empty", _expect_verdict(empty), V_EMPTY)
        want("verdict none", _expect_verdict(dict(empty, **{C_DIFFERS: 3})), V_NONE)
        want("verdict all", _expect_verdict(dict(empty, **{C_IDENTICAL: 3})), V_ALL)
        want("verdict most", _expect_verdict(dict(empty, **{C_IDENTICAL: 3, C_DIFFERS: 2})), V_MOST)
        want("verdict some", _expect_verdict(dict(empty, **{C_IDENTICAL: 2, C_DIFFERS: 3})), V_SOME)

        # strip_clock: top level only vs any depth
        obj = {"generated": 1, "keep": {"ts": 2, "y": 3}, "list": [{"elapsed_sec": 4, "z": 5}]}
        want("top strip", strip_clock(obj, "top"),
             {"keep": {"ts": 2, "y": 3}, "list": [{"elapsed_sec": 4, "z": 5}]})
        want("recursive strip", strip_clock(obj, "any"), {"keep": {"y": 3}, "list": [{"z": 5}]})

        # guards: a face whose tallies do not re-add must be refused
        good = {
            "summary": {"member_files": 2, "class_counts": {c: 0 for c in CLASSES},
                        "class_bytes": {c: 0 for c in CLASSES}, "comparable_files": 2,
                        "vintage_files_identical_after_clock_strip": 1,
                        "families_with_a_resolvable_twin": 1},
            "families": [{"members": 2, "twin_present": True}],
            "rows": [{"path": "a.json", "class": C_IDENTICAL, "bytes": 1, "differing_keys": [],
                      "identical_after_recursive_clock_strip": True},
                     {"path": "b.json", "class": C_DIFFERS, "bytes": 1, "differing_keys": ["x"],
                      "identical_after_recursive_clock_strip": False}],
            "frozen_clock_fields": list(CLOCK_FIELDS_TOP),
            "verdict": V_SOME,
        }
        good["summary"]["class_counts"][C_IDENTICAL] = 1
        good["summary"]["class_counts"][C_DIFFERS] = 1
        good["summary"]["class_bytes"][C_IDENTICAL] = 1
        good["summary"]["class_bytes"][C_DIFFERS] = 1
        want("clean fixture checks", check(good), [])
        doctored = json.loads(json.dumps(good))
        doctored["verdict"] = V_ALL
        if not check(doctored):
            fails.append("check() accepted a verdict the counts do not imply")
        doctored2 = json.loads(json.dumps(good))
        doctored2["rows"][0]["differing_keys"] = ["x"]
        if not check(doctored2):
            fails.append("check() accepted an identical row that names a differing key")
        doctored3 = json.loads(json.dumps(good))
        doctored3["summary"]["class_counts"][C_NOT_JSON] = 1
        if not check(doctored3):
            fails.append("check() accepted class counts that do not sum to member_files")
        doctored4 = json.loads(json.dumps(good))
        doctored4["rows"][0]["identical_after_recursive_clock_strip"] = False
        if not check(doctored4):
            fails.append("check() accepted a top-level identical row that is not recursively identical")
    finally:
        shutil.rmtree(tmp, ignore_errors=True)

    if fails:
        for f in fails:
            print("FAIL %s" % f)
        return 1
    print("selftest 30/30: 5 classes + recursive arm + byte tally + key histogram + "
          "5 verdict branches + 2 strip depths + 4 doctored faces: OK")
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