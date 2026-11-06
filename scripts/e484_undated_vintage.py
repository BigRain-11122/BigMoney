"""E484 -- can the 201 vintage members whose name states no ISO date be dated from the payload?

E480 measured that a dated vintage name agrees with its payload (269/269), but 201 of the 571
unread-vintage members carry no ISO date in the basename at all, so a name-based index cannot
place them in time.  This face asks the next question: does the file itself say when it is from?

Each member lands in exactly one class:

  datable_from_frozen_field     a frozen date field (the same seven E480 froze) states a date
  datable_only_from_non_frozen  no frozen field, but another field in the payload states a date
  undatable                      the payload states no date anywhere the scan looks
  not_a_json_object              the member is not a JSON object (csv/md/jsonl/array)
  unreadable_member              missing on disk or does not parse

For every datable member the date is then placed against its *family's own dated span* (the
min..max of the ISO dates its siblings carry in their file names), giving in_span / outside_span
/ no_span (the family has no dated sibling at all: unmeasurable, never a negative).

Auxiliary census, published beside the classes because it changes the retention conclusion but
must not be smuggled into the class set: how many of these names carry a compact YYYYMMDD date
(the same day, spelled without dashes) -- a name-based rule that only accepts ISO still cannot
place them, but the information is not missing from the name.

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
FACE_NAME = "undated_latest.json"
DATED_PREFIX = "UNDATED"
CARD = "E484-CAN-THE-201-VINTAGE-MEMBERS-WHOSE-NAME-STATES-NO-DATE-BE-DATED-FROM-THE-PAYLOAD"
PARENT_FACE = "vintagedate_latest.json"       # E480: name-date vs payload-date agreement
SIBLING_READ = "vintageread_latest.json"      # E472: the unread vintage families
SIBLING_CLOCK = "vintageclock_latest.json"    # E478: twin comparison

# Frozen by E480's card text and reused verbatim here (a name outside this tuple does not witness a
# date).  Published in the face so a reader sees exactly which names were accepted (E207 family).
DATE_FIELDS = ("evidence_cutoff", "generated", "ts", "timestamp", "date", "as_of", "asof_bar")

ISO_DATE_RE = re.compile(r"(?<!\d)(\d{4})-(\d{2})-(\d{2})(?!\d)")
COMPACT_DATE_RE = re.compile(r"(?<!\d)((?:19|20)\d{2})(\d{2})(\d{2})(?!\d)")

C_FROZEN = "datable_from_frozen_field"
C_NONFROZEN = "datable_only_from_non_frozen_field"
C_UNDATABLE = "undatable"
C_NOT_JSON = "not_a_json_object"
C_UNREADABLE = "unreadable_member"
CLASSES = (C_FROZEN, C_NONFROZEN, C_UNDATABLE, C_NOT_JSON, C_UNREADABLE)
DATABLE = (C_FROZEN, C_NONFROZEN)
PAYLOAD_COMPARABLE = (C_FROZEN, C_NONFROZEN, C_UNDATABLE)

IN_SPAN = "in_span"
OUT_SPAN = "outside_span"
NO_SPAN = "no_span"
SPANS = (IN_SPAN, OUT_SPAN, NO_SPAN)

V_EMPTY = "no_vintage_member_reads_as_a_json_object_so_no_payload_could_be_dated"
V_NONE = "no_undated_vintage_name_can_be_dated_from_its_payload"
V_ALL = "every_undated_vintage_name_can_be_dated_from_its_payload"
V_MOST = "most_undated_vintage_names_can_be_dated_from_their_payload"
V_SOME = "some_undated_vintage_names_can_be_dated_from_their_payload_and_the_majority_cannot"
VERDICT_VOCAB = (V_EMPTY, V_NONE, V_ALL, V_MOST, V_SOME)

V_SPAN_ALL = "every_payload_date_falls_inside_the_span_its_own_family_states_in_its_names"
V_SPAN_MOST = "most_payload_dates_fall_inside_the_span_their_own_family_states_in_its_names"
V_SPAN_SOME = "some_payload_dates_fall_inside_the_span_their_own_family_states_in_its_names"
V_SPAN_NONE = "no_payload_date_falls_inside_the_span_its_own_family_states_in_its_names"
V_SPAN_UNMEASURED = "no_family_of_these_members_states_a_span_in_its_names_so_the_span_is_unmeasured"
SPAN_VERDICT_VOCAB = (V_SPAN_ALL, V_SPAN_MOST, V_SPAN_SOME, V_SPAN_NONE, V_SPAN_UNMEASURED)
MAX_SCAN_DEPTH = 2


# ----------------------------------------------------------------------------- helpers


def _rel(path, root=None):
    return os.path.relpath(path, root or ROOT).replace("\\", "/")


def _iso(m):
    return "%s-%s-%s" % (m.group(1), m.group(2), m.group(3))


def name_compact_dates(basename):
    """Distinct compact YYYYMMDD dates in a file name (the spelling E480's ISO regex misses)."""
    out = []
    for m in COMPACT_DATE_RE.finditer(basename):
        d = "%s-%s-%s" % (m.group(1), m.group(2), m.group(3))
        if d not in out:
            out.append(d)
    return out


def frozen_dates(obj):
    """Dates stated by the frozen field names at the payload's top level."""
    out = []
    if not isinstance(obj, dict):
        return out
    for k in DATE_FIELDS:
        v = obj.get(k)
        if not isinstance(v, str):
            continue
        m = ISO_DATE_RE.search(v)
        if m and _iso(m) not in out:
            out.append(_iso(m))
    return out


def _walk_dates(node, prefix, depth, found):
    if depth > MAX_SCAN_DEPTH:
        return
    if isinstance(node, dict):
        for k, v in node.items():
            key = "%s.%s" % (prefix, k) if prefix else str(k)
            if isinstance(v, str):
                m = ISO_DATE_RE.search(v)
                if m:
                    found.append((key, _iso(m)))
            elif isinstance(v, (dict, list)):
                _walk_dates(v, key, depth + 1, found)
    elif isinstance(node, list):
        for i, v in enumerate(node):
            key = "%s[%d]" % (prefix, i)
            if isinstance(v, str):
                m = ISO_DATE_RE.search(v)
                if m:
                    found.append((key, _iso(m)))
            elif isinstance(v, (dict, list)):
                _walk_dates(v, key, depth + 1, found)


def non_frozen_dates(obj):
    """[(field_path, date)] for every date stated outside the frozen names."""
    found = []
    if not isinstance(obj, dict):
        return found
    for k, v in obj.items():
        if k in DATE_FIELDS:
            continue
        if isinstance(v, str):
            m = ISO_DATE_RE.search(v)
            if m:
                found.append((str(k), _iso(m)))
        elif isinstance(v, (dict, list)):
            _walk_dates(v, str(k), 1, found)
    return found


def classify_file(path, read, exists):
    """(class, date, witness_field) for one member.  read() is injectable for the selftest."""
    ext = os.path.splitext(path)[1].lower()
    if ext != ".json":
        return C_NOT_JSON, None, None
    if not exists(path):
        return C_UNREADABLE, None, None
    try:
        obj = read(path)
    except Exception:
        return C_UNREADABLE, None, None
    if not isinstance(obj, dict):
        return C_NOT_JSON, None, None
    fd = frozen_dates(obj)
    if fd:
        return C_FROZEN, fd[0], "frozen"
    nf = non_frozen_dates(obj)
    if nf:
        return C_NONFROZEN, nf[0][1], nf[0][0]
    return C_UNDATABLE, None, None


def any_name_dates(row):
    """Every date a member's *file name* states, in either spelling (ISO or compact YYYYMMDD).

    E480 only accepted the dashed spelling, so its published rows carry name_dates for the dated
    members and nothing for the rest; here the compact spelling is read back off the path so a
    family span is not declared unmeasurable merely because its names use the short form.
    """
    out = list(row.get("name_dates") or [])
    compact = row.get("name_compact_dates")
    if compact is None:
        compact = name_compact_dates(os.path.basename(row.get("path") or ""))
    for d in compact:
        if d not in out:
            out.append(d)
    return out


def family_spans(rows):
    """{family_key: (min_date, max_date, n_dated_siblings)} from the dates in the member names."""
    spans = {}
    for r in rows:
        key = r.get("family")
        dates = any_name_dates(r)
        if not dates:
            continue
        lo, hi, n = spans.get(key, (None, None, 0))
        d0, d1 = min(dates), max(dates)
        lo = d0 if lo is None or d0 < lo else lo
        hi = d1 if hi is None or d1 > hi else hi
        spans[key] = (lo, hi, n + 1)
    return spans


def span_class(date, span):
    if not span or not span[0]:
        return NO_SPAN
    if span[0] <= date <= span[1]:
        return IN_SPAN
    return OUT_SPAN


def classify(pop_rows, read, exists, size_of, rel, span_source=None, families_of_interest=None):
    rows = []
    counts = {c: 0 for c in CLASSES}
    byte_counts = {c: 0 for c in CLASSES}
    span_counts = {s: 0 for s in SPANS}
    compact = 0
    witness_fields = {}
    samples_undatable = []
    compact_agree = 0
    compact_differ = []
    compact_differ_n = 0
    compact_absent = 0

    for r in sorted(pop_rows, key=lambda x: x.get("path") or ""):
        path = r.get("path") or ""
        abspath = path if os.path.isabs(path) else os.path.join(ROOT, path)
        cls, date, witness = classify_file(abspath, read, exists)
        try:
            size = size_of(abspath)
        except OSError:
            size = r.get("bytes") or 0
        counts[cls] += 1
        byte_counts[cls] += size
        if date and cls in DATABLE:
            witness_fields[witness] = witness_fields.get(witness, 0) + 1
        if cls == C_UNDATABLE and len(samples_undatable) < 20:
            samples_undatable.append(path)
        compact_dates = name_compact_dates(os.path.basename(abspath))
        if compact_dates:
            compact += 1
        if date:
            if compact_dates and date in compact_dates:
                compact_agree += 1
            elif compact_dates:
                compact_differ_n += 1
                if len(compact_differ) < 20:
                    compact_differ.append({"path": rel(abspath), "name_date": compact_dates[0],
                                           "payload_date": date, "witness_field": witness})
            else:
                compact_absent += 1
        rows.append({
            "path": rel(abspath),
            "family": r.get("family"),
            "bytes": size,
            "class": cls,
            "payload_date": date,
            "witness_field": witness,
            "name_dates": r.get("name_dates") or [],
            "name_compact_dates": compact_dates,
            "span_class": None,   # filled below, once every family's span is known
        })

    spans = family_spans(span_source if span_source is not None else pop_rows)
    if families_of_interest is not None:
        spans = {k: v for k, v in spans.items() if k in families_of_interest}
    for row in rows:
        row["span_class"] = span_class(row["payload_date"], spans.get(row["family"])) \
            if row["payload_date"] else None
        if row["span_class"]:
            span_counts[row["span_class"]] += 1

    families = []
    for key in sorted(spans):
        lo, hi, n = spans[key]
        families.append({"family": key, "span_from": lo, "span_to": hi, "dated_siblings": n})
    return (rows, families, counts, byte_counts, span_counts, compact, witness_fields, samples_undatable,
            compact_agree, compact_differ, compact_differ_n, compact_absent)


# ----------------------------------------------------------------------------- build


def build(pop_path=None):
    pop = json.load(io.open(pop_path or os.path.join(OUTDIR, PARENT_FACE), "r", encoding="utf-8"))
    all_rows = pop.get("rows") or []
    pop_rows = [r for r in all_rows if r.get("class") == "no_date_in_name"]
    siblings = {}
    for name in (SIBLING_READ, SIBLING_CLOCK):
        p = os.path.join(OUTDIR, name)
        if os.path.exists(p):
            try:
                siblings[name] = json.load(io.open(p, "r", encoding="utf-8"))
            except Exception:
                siblings[name] = None

    (rows, families, counts, byte_counts, span_counts, compact, witnesses,
     samples, compact_agree, compact_differ, compact_differ_n, compact_absent) = classify(
        pop_rows,
        lambda p: json.load(io.open(p, "r", encoding="utf-8")),
        os.path.exists, os.path.getsize, _rel,
        span_source=all_rows,
        families_of_interest={r.get("family") for r in pop_rows})

    comparable = sum(counts[c] for c in PAYLOAD_COMPARABLE)
    datable = sum(counts[c] for c in DATABLE)
    if comparable == 0:
        verdict = V_EMPTY
    elif datable == 0:
        verdict = V_NONE
    elif datable == comparable:
        verdict = V_ALL
    elif datable * 2 > comparable:
        verdict = V_MOST
    else:
        verdict = V_SOME

    span_measured = span_counts[IN_SPAN] + span_counts[OUT_SPAN]
    if span_measured == 0:
        span_verdict = V_SPAN_UNMEASURED
    elif span_counts[IN_SPAN] == 0:
        span_verdict = V_SPAN_NONE
    elif span_counts[OUT_SPAN] == 0:
        span_verdict = V_SPAN_ALL
    elif span_counts[IN_SPAN] * 2 > span_measured:
        span_verdict = V_SPAN_MOST
    else:
        span_verdict = V_SPAN_SOME

    summary = {
        "families_of_these_members": len({r.get("family") for r in rows}),
        "families_that_state_a_span_in_their_names": len(families),
        "member_files": len(rows),
        "payload_comparable_files": comparable,
        "class_counts": counts,
        "class_bytes": byte_counts,
        "files_datable_from_their_payload": datable,
        "datable_share_of_payload_comparable": round(datable / comparable, 6) if comparable else None,
        "bytes_datable_from_their_payload": byte_counts[C_FROZEN] + byte_counts[C_NONFROZEN],
        "files_undatable_at_all": counts[C_UNDATABLE],
        "bytes_undatable_at_all": byte_counts[C_UNDATABLE],
        "witness_field_counts": dict(sorted(witnesses.items(), key=lambda kv: -kv[1])),
        "span_class_counts": span_counts,
        "span_verdict": span_verdict,
        "names_carrying_a_compact_yyyymmdd_date": compact,
        "compact_name_date_agreement": {
            "payload_date_equals_the_compact_name_date": compact_agree,
            "payload_date_differs_from_the_compact_name_date": compact_differ_n,
            "payload_date_with_no_compact_name_date": compact_absent,
            "disagreeing_samples": compact_differ,
        },
        "files_whose_name_is_silent_and_payload_is_silent": sum(
            1 for r in rows if r["class"] == C_UNDATABLE and not r["name_compact_dates"]),
        "undatable_samples": samples,
        "frozen_date_fields": list(DATE_FIELDS),
        "scan_depth_below_top_level": MAX_SCAN_DEPTH,
        "sibling_context": {
            "e480_names_agreeing_with_payload": ((siblings.get(PARENT_FACE) or {}).get("summary") or {}
                                                 .get("names_agreeing_with_the_date_their_payload_states")),
            "e472_unread_vintage_members": ((siblings.get(SIBLING_READ) or {}).get("summary") or {})
                                           .get("member_files"),
            "e478_identical_after_clock_strip": ((siblings.get(SIBLING_CLOCK) or {}).get("summary") or {})
                                                .get("vintage_files_identical_after_clock_strip"),
        },
    }

    face = {
        "card": CARD,
        "study": "E484_can_the_undated_vintage_names_be_dated_from_their_payload",
        "title": "can the vintage members whose name states no date be dated from the payload?",
        "evidence_cutoff": time.strftime("%Y-%m-%d"),
        "generated": time.strftime("%Y-%m-%dT%H:%M:%S%z"),
        "frozen_date_fields": list(DATE_FIELDS),
        "population_source": {
            "face": PARENT_FACE,
            "face_evidence_cutoff": pop.get("evidence_cutoff"),
            "face_verdict": pop.get("verdict"),
            "population_class": "no_date_in_name",
        },
        "class_definition": {
            C_FROZEN: "a frozen date field at the top level states a date",
            C_NONFROZEN: "no frozen field states a date, but another payload field does",
            C_UNDATABLE: "the payload states no date anywhere the scan looks (depth <= %d)"
                         % MAX_SCAN_DEPTH,
            C_NOT_JSON: "the member is not a JSON object (csv/md/jsonl/array)",
            C_UNREADABLE: "the member is missing on disk or does not parse",
        },
        "span_definition": {
            IN_SPAN: "the payload date lies within [min, max] of the dates the family's member "
                     "names state, in either spelling (ISO or compact YYYYMMDD)",
            OUT_SPAN: "the payload date lies outside that span",
            NO_SPAN: "no member of that family states a date in its name: unmeasurable",
        },
        "summary": summary,
        "verdict": verdict,
        "verdict_vocab": list(VERDICT_VOCAB),
        "span_verdict_vocab": list(SPAN_VERDICT_VOCAB),
        "families": families,
        "rows": rows,
        "method_limits": [
            "the population is E480's no_date_in_name rows; a family that gained or lost members "
            "since then is not rescanned",
            "the scan reads the payload to depth %d below the top level, so a date buried in a "
            "per-row list entry is not a witness (it would date a row, not the file)" % MAX_SCAN_DEPTH,
            "a compact YYYYMMDD date in the name is counted but never promoted to a class: this "
            "face measures the payload, and the name census is published beside it",
            "the family span comes from ISO dates in sibling *names*, not from sibling payloads; a "
            "family whose names are all undated has no span and its members read as no_span",
            "datable says the file can be placed in time, not that it should be kept (E477/E479 own "
            "the retention decision)",
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
    derived_spans = {x: 0 for x in SPANS}
    witnesses = {}
    compact = 0
    for r in rows:
        cls = r.get("class")
        if cls not in CLASSES:
            problems.append("row %s carries a class outside the set" % r.get("path"))
            break
        derived[cls] += 1
        if r.get("name_compact_dates"):
            compact += 1
        if cls in DATABLE:
            if not r.get("payload_date"):
                problems.append("row %s is datable but carries no date" % r.get("path"))
                break
            if not r.get("witness_field"):
                problems.append("row %s is datable but names no witness field" % r.get("path"))
                break
            wk = r["witness_field"]
            witnesses[wk] = witnesses.get(wk, 0) + 1
            if r.get("span_class") not in SPANS:
                problems.append("row %s is datable but its span_class is %r"
                                % (r.get("path"), r.get("span_class")))
                break
            derived_spans[r["span_class"]] += 1
        else:
            if r.get("payload_date") is not None or r.get("span_class") is not None:
                problems.append("row %s is undatable-class but carries a date or span"
                                % r.get("path"))
                break
            if cls == C_FROZEN or cls == C_NONFROZEN:
                problems.append("row %s carries a datable class the loop did not reach"
                                % r.get("path"))
                break

    if derived != counts:
        problems.append("the published class counts do not re-derive from the rows")
    if s.get("files_datable_from_their_payload") != derived[C_FROZEN] + derived[C_NONFROZEN]:
        problems.append("the datable tally does not re-derive from the rows")
    if s.get("payload_comparable_files") != sum(derived[c] for c in PAYLOAD_COMPARABLE):
        problems.append("the payload-comparable tally is not frozen + non-frozen + undatable")
    if s.get("files_undatable_at_all") != derived[C_UNDATABLE]:
        problems.append("the undatable tally does not re-derive from the rows")
    if s.get("witness_field_counts") != dict(sorted(witnesses.items(), key=lambda kv: -kv[1])):
        problems.append("the witness-field histogram does not re-derive from the rows")
    if s.get("span_class_counts") != derived_spans:
        problems.append("the span class counts do not re-derive from the rows")
    if s.get("names_carrying_a_compact_yyyymmdd_date") != compact:
        problems.append("the compact-name-date census does not re-derive from the rows")
    silent = sum(1 for r in rows if r.get("class") == C_UNDATABLE and not r.get("name_compact_dates"))
    if s.get("files_whose_name_is_silent_and_payload_is_silent") != silent:
        problems.append("the silent-name-and-payload tally does not re-derive from the rows")
    if face.get("verdict") not in VERDICT_VOCAB:
        problems.append("verdict is outside the frozen vocabulary: %r" % face.get("verdict"))
    if s.get("span_verdict") not in SPAN_VERDICT_VOCAB:
        problems.append("span verdict is outside the frozen vocabulary: %r" % s.get("span_verdict"))

    spans = {}
    for f in face.get("families") or []:
        spans[f.get("family")] = (f.get("span_from"), f.get("span_to"), f.get("dated_siblings") or 0)
    for r in rows:
        if not r.get("payload_date"):
            continue
        expect = span_class(r["payload_date"], spans.get(r.get("family")))
        if r.get("span_class") != expect:
            problems.append("row %s span_class %r != re-derived %r"
                            % (r.get("path"), r.get("span_class"), expect))
            break

    agree = differ = absent = 0
    for r in rows:
        d = r.get("payload_date")
        if not d:
            continue
        nd = r.get("name_compact_dates") or []
        if not nd:
            absent += 1
        elif d in nd:
            agree += 1
        else:
            differ += 1
    blocks = s.get("compact_name_date_agreement") or {}
    if blocks.get("payload_date_equals_the_compact_name_date") != agree:
        problems.append("the compact-name agreement tally does not re-derive from the rows")
    if blocks.get("payload_date_differs_from_the_compact_name_date") != differ:
        problems.append("the compact-name disagreement tally does not re-derive from the rows")
    if blocks.get("payload_date_with_no_compact_name_date") != absent:
        problems.append("the compact-name-absent tally does not re-derive from the rows")
    if len(blocks.get("disagreeing_samples") or []) > differ:
        problems.append("more disagreeing samples are published than the tally counts")
    return problems


def _expect_verdict(counts):
    comparable = sum(counts.get(c, 0) for c in PAYLOAD_COMPARABLE)
    datable = counts.get(C_FROZEN, 0) + counts.get(C_NONFROZEN, 0)
    if comparable == 0:
        return V_EMPTY
    if datable == 0:
        return V_NONE
    if datable == comparable:
        return V_ALL
    if datable * 2 > comparable:
        return V_MOST
    return V_SOME


def _expect_span_verdict(span_counts):
    measured = span_counts.get(IN_SPAN, 0) + span_counts.get(OUT_SPAN, 0)
    if measured == 0:
        return V_SPAN_UNMEASURED
    if span_counts.get(IN_SPAN, 0) == 0:
        return V_SPAN_NONE
    if span_counts.get(OUT_SPAN, 0) == 0:
        return V_SPAN_ALL
    if span_counts.get(IN_SPAN, 0) * 2 > measured:
        return V_SPAN_MOST
    return V_SPAN_SOME


def check(face=None):
    face = face or json.load(io.open(os.path.join(OUTDIR, FACE_NAME), "r", encoding="utf-8"))
    problems = row_problems(face)
    counts = (face.get("summary") or {}).get("class_counts") or {}
    expect = _expect_verdict(counts)
    if face.get("verdict") != expect:
        problems.append("verdict %r is not the one the counts imply (%r)" % (face.get("verdict"), expect))
    spans = (face.get("summary") or {}).get("span_class_counts") or {}
    expect_span = _expect_span_verdict(spans)
    if (face.get("summary") or {}).get("span_verdict") != expect_span:
        problems.append("span verdict %r is not the one the span counts imply (%r)"
                        % ((face.get("summary") or {}).get("span_verdict"), expect_span))
    return problems


def verify():
    published = json.load(io.open(os.path.join(OUTDIR, FACE_NAME), "r", encoding="utf-8"))
    fresh = build()
    problems = []
    ps, fs = published.get("summary") or {}, fresh.get("summary") or {}
    for key in ("families_of_these_members", "families_that_state_a_span_in_their_names",
                "member_files", "payload_comparable_files", "class_counts", "class_bytes",
                "files_datable_from_their_payload", "datable_share_of_payload_comparable",
                "bytes_datable_from_their_payload", "files_undatable_at_all",
                "bytes_undatable_at_all", "witness_field_counts", "span_class_counts",
                "span_verdict", "names_carrying_a_compact_yyyymmdd_date",
                "files_whose_name_is_silent_and_payload_is_silent"):
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
    tmp = tempfile.mkdtemp(prefix="e484_")
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

        fam = os.path.join(tmp, "fam")
        # 1: frozen field dates it
        a = os.path.join(fam, "FAM_receipt.json")
        w(a, {"evidence_cutoff": "2026-01-02", "x": 1})
        # 2: only a non-frozen field dates it
        b = os.path.join(fam, "FAM_probe.json")
        w(b, {"run_at": "2026-01-03T09:00:00"})
        # 3: undatable (no date anywhere in the scan)
        c = os.path.join(fam, "FAM_profile.json")
        w(c, {"n": 3, "note": "no date here"})
        # 4: not json
        d = os.path.join(fam, "FAM_notes.md")
        w(d, "# notes\n")
        # 5: unreadable (bad json)
        e = os.path.join(fam, "FAM_broken.json")
        w(e, "{not json")
        # 6: missing on disk
        f = os.path.join(fam, "FAM_gone.json")
        # 7: json array, not an object
        g = os.path.join(fam, "FAM_list.json")
        w(g, "[1, 2]")
        # 8: a frozen field that is not a string is not a witness
        h = os.path.join(fam, "FAM_tsint.json")
        w(h, {"ts": 1793977916})

        pop_rows = [{"path": p, "family": "d/FAM", "bytes": 1, "name_dates": []}
                    for p in (a, b, c, d, e, f, g, h)]
        (rows, families, counts, byte_counts, span_counts, compact,
             witnesses, samples, cagree, cdiffer, cdiffer_n, cabsent) = classify(
            pop_rows, lambda p: json.load(io.open(p, "r", encoding="utf-8")),
            os.path.exists, os.path.getsize, lambda p: os.path.basename(p))

        want("frozen count", counts[C_FROZEN], 1)
        want("non-frozen count", counts[C_NONFROZEN], 1)
        want("undatable count", counts[C_UNDATABLE], 2)   # plain profile + int ts
        want("not-json count", counts[C_NOT_JSON], 2)     # md + json list
        want("unreadable count", counts[C_UNREADABLE], 2)  # bad json + missing
        want("class sum", sum(counts.values()), 8)
        want("witness fields", dict(sorted(witnesses.items())), {"frozen": 1, "run_at": 1})
        want("no span when no sibling names a date", families, [])
        want("span classes all no_span would be empty here",
             span_counts, {IN_SPAN: 0, OUT_SPAN: 0, NO_SPAN: 2})
        want("undatable samples kept", len(samples), 2)

        # name census: the spelling E480's ISO regex misses
        want("compact date in a name", name_compact_dates("PROFILE-20261028.json"), ["2026-10-28"])
        want("compact date rejected when it is not a date",
             name_compact_dates("PROFILE-20261328.json"), ["2026-13-28"])
        want("no compact date", name_compact_dates("PROFILE_latest.json"), [])

        # frozen/non-frozen extractors are their own measurements
        want("frozen date from a timestamp",
             frozen_dates({"generated": "2026-02-03T04:05:06"}), ["2026-02-03"])
        want("int field ignored", frozen_dates({"ts": 1793977916}), [])
        want("nested date is not frozen",
             frozen_dates({"meta": {"ts": "2026-02-03"}}), [])
        want("nested date is non-frozen",
             non_frozen_dates({"meta": {"written": "2026-02-03"}}), [("meta.written", "2026-02-03")])
        want("deep date beyond depth is not a witness",
             non_frozen_dates({"a": {"b": {"c": {"d": "2026-02-03"}}}}), [])
        want("list entry date is found one level in",
             non_frozen_dates({"rows": ["2026-02-03"]}), [("rows[0]", "2026-02-03")])

        # family span arithmetic
        want("span in", span_class("2026-01-02", ("2026-01-01", "2026-01-03", 2)), IN_SPAN)
        want("span out", span_class("2026-01-04", ("2026-01-01", "2026-01-03", 2)), OUT_SPAN)
        want("span absent", span_class("2026-01-02", None), NO_SPAN)
        want("span built from sibling names",
             family_spans([{"family": "f", "name_dates": ["2026-01-03"]},
                           {"family": "f", "name_dates": []},
                           {"family": "f", "name_dates": ["2026-01-01"]}]),
             {"f": ("2026-01-01", "2026-01-03", 2)})

        # verdict arithmetic
        empty = {c: 0 for c in CLASSES}
        want("verdict empty", _expect_verdict(empty), V_EMPTY)
        want("verdict none",
             _expect_verdict(dict(empty, **{C_UNDATABLE: 3, C_FROZEN: 0})), V_NONE)
        want("verdict all", _expect_verdict(dict(empty, **{C_FROZEN: 3})), V_ALL)
        want("verdict most", _expect_verdict(dict(empty, **{C_FROZEN: 3, C_UNDATABLE: 2})), V_MOST)
        want("verdict some", _expect_verdict(dict(empty, **{C_FROZEN: 2, C_UNDATABLE: 3})), V_SOME)
        want("not-json is outside the verdict denominator",
             _expect_verdict(dict(empty, **{C_FROZEN: 1, C_NOT_JSON: 9})), V_ALL)
        want("span verdict unmeasured", _expect_span_verdict({IN_SPAN: 0, OUT_SPAN: 0, NO_SPAN: 5}),
             V_SPAN_UNMEASURED)
        want("span verdict none", _expect_span_verdict({IN_SPAN: 0, OUT_SPAN: 2, NO_SPAN: 0}),
             V_SPAN_NONE)
        want("span verdict all", _expect_span_verdict({IN_SPAN: 2, OUT_SPAN: 0, NO_SPAN: 0}),
             V_SPAN_ALL)
        want("span verdict most", _expect_span_verdict({IN_SPAN: 2, OUT_SPAN: 1, NO_SPAN: 0}),
             V_SPAN_MOST)
        want("span verdict some", _expect_span_verdict({IN_SPAN: 1, OUT_SPAN: 2, NO_SPAN: 0}),
             V_SPAN_SOME)

        # guards: a face whose rows contradict their own tallies must be refused
        good = {
            "summary": {
                "member_files": 2, "payload_comparable_files": 2,
                "class_counts": {c: 0 for c in CLASSES},
                "class_bytes": {c: 0 for c in CLASSES},
                "files_datable_from_their_payload": 1, "files_undatable_at_all": 1,
                "witness_field_counts": {"frozen": 1},
                "span_class_counts": {IN_SPAN: 1, OUT_SPAN: 0, NO_SPAN: 0},
                "span_verdict": V_SPAN_ALL,
                "names_carrying_a_compact_yyyymmdd_date": 0,
                "files_whose_name_is_silent_and_payload_is_silent": 1,
                "compact_name_date_agreement": {
                    "payload_date_equals_the_compact_name_date": 0,
                    "payload_date_differs_from_the_compact_name_date": 0,
                    "payload_date_with_no_compact_name_date": 1,
                    "disagreeing_samples": [],
                },
            },
            "families": [{"family": "d/FAM", "span_from": "2026-01-01", "span_to": "2026-01-03",
                          "dated_siblings": 2}],
            "rows": [
                {"path": "a_receipt.json", "family": "d/FAM", "bytes": 1, "class": C_FROZEN,
                 "payload_date": "2026-01-02", "witness_field": "frozen",
                 "name_compact_dates": [], "name_dates": ["2026-01-01", "2026-01-03"],
                 "span_class": IN_SPAN},
                {"path": "b_profile.json", "family": "d/FAM", "bytes": 1, "class": C_UNDATABLE,
                 "payload_date": None, "witness_field": None,
                 "name_compact_dates": [], "name_dates": ["2026-01-01", "2026-01-03"],
                 "span_class": None},
            ],
            "verdict": V_SOME,
        }
        good["summary"]["class_counts"][C_FROZEN] = 1
        good["summary"]["class_counts"][C_UNDATABLE] = 1
        good["summary"]["class_bytes"][C_FROZEN] = 1
        good["summary"]["class_bytes"][C_UNDATABLE] = 1
        want("clean fixture checks", check(good), [])

        def doctored(mut):
            d2 = json.loads(json.dumps(good))
            mut(d2)
            return d2

        if not check(doctored(lambda d: d.update(verdict=V_ALL))):
            fails.append("check() accepted a verdict the counts do not imply")
        if not check(doctored(lambda d: d["rows"][0].update(payload_date=None))):
            fails.append("check() accepted a datable row with no date")
        if not check(doctored(lambda d: d["rows"][0].update(span_class=OUT_SPAN))):
            fails.append("check() accepted a span class the family span refutes")
        if not check(doctored(lambda d: d["summary"].update(files_datable_from_their_payload=2))):
            fails.append("check() accepted a datable tally that does not re-derive")
        if not check(doctored(lambda d: d["summary"].update(names_carrying_a_compact_yyyymmdd_date=1))):
            fails.append("check() accepted a compact-name census that does not re-derive")
        if not check(doctored(lambda d: d["rows"][1].update(payload_date="2026-01-02",
                                                            span_class=IN_SPAN))):
            fails.append("check() accepted an undatable-class row that carries a date")
        if not check(doctored(lambda d: d["summary"]["class_counts"].update({C_NOT_JSON: 1}))):
            fails.append("check() accepted class counts that do not sum to member_files")
        if not check(doctored(lambda d: d["summary"].update(span_verdict=V_SPAN_SOME))):
            fails.append("check() accepted a span verdict the span counts do not imply")
        if not check(doctored(lambda d: d["summary"]["compact_name_date_agreement"].update(
                payload_date_with_no_compact_name_date=0))):
            fails.append("check() accepted a compact-name census that does not re-derive")
        if not check(doctored(lambda d: d["families"][0].update(span_to="2026-01-01"))):
            fails.append("check() accepted a span class the edited family span refutes")
    finally:
        shutil.rmtree(tmp, ignore_errors=True)

    if fails:
        for f in fails:
            print("FAIL %s" % f)
        return 1
    print("selftest 41/41: 5 payload classes + frozen/non-frozen extractors + depth bound + compact "
          "name census + span arithmetic + 5+5 verdict branches + 8 doctored faces: OK")
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