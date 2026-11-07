"""E506 (r1535 bm-b) -- what do the 725 certifications with no parseable date actually witness?

E503 priced 2932 (read-only leg, face) relations: 725 of them certify a face whose payload
publishes no date in any of the witness fields the chain's age check reads, so those bytes
cannot be aged at all.  E503 published that as one opaque number.  This study reads those
faces and asks what each one *does* carry:

  A. a date under a top-level field name that is not in the witness list (a one-word fix)
  B. a witness field name, but below the top level (``meta.generated``)
  C. a date inside prose or an unstructured value (needs a parser, not a key)
  D. nothing anywhere -- only ``st_mtime`` is left, and this tree materialises every file at
     checkout (E453), so mtime cannot age these bytes either
  E. unreadable / absent (an honest hole, never folded into D)

Second axis, per certifying leg: does the leg's own script mention a date field name at all,
and does it test the face for existence?  These are whole-script literal scans, published as
such -- a mention is not proof that the leg reads *this* face's date.

Everything here is static: the chain module is never imported, no face is rewritten, no
network.  The verdict is computed by the gate from the rows.
"""

import ast
import datetime
import io
import json
import os
import re
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
if HERE not in sys.path:
    sys.path.insert(0, HERE)

ROOT = os.path.dirname(HERE)
OUTDIR = os.path.join(ROOT, "results", "state_tilt")

import e503_chain_stale as e503  # noqa: E402  (reuse: the chain parse must not be re-built)

FACE_NAME = "nodatewitness_latest.json"
DATED_PREFIX = "NODATEWITNESS"
DATE_STAMP = "2026-11-07"
CARD = "E506-WHAT-DO-THE-725-CERTIFICATIONS-WITH-NO-PARSEABLE-DATE-ACTUALLY-READ"
STUDY = "E506_nodate_witness"
POPULATION_SOURCE = "E503 CHAINSTALE relations whose class is C_NODATE (Tools/s6_chain_bmb.py)"

# date shapes a payload may carry outside the witness fields
ISO_RE = re.compile(r"\b(?:19|20)\d{2}[-/]\d{2}[-/]\d{2}\b")
COMPACT_RE = re.compile(r"\b(?:19|20)\d{6}\b")

DATE_FIELDS = tuple(e503.DATE_FIELDS)

# per-face witness class.  The split is by WHERE the date sits, because "a date is in this
# payload" and "this payload can be aged by a rule that looks for one" are different facts:
# an unlisted top-level field is one word away from the chain's list; the same name nested a
# level down needs a path; a date inside a log line or a source-text cache is not a witness.
W_UNLISTED = ("the_face_carries_a_top_level_date_field_whose_name_is_not_in_the_witness_list")
W_NESTED = "the_face_carries_a_witness_field_name_below_the_top_level"
W_UNLISTED_NESTED = ("the_face_carries_a_structured_date_under_a_nested_field_whose_name_is_not_"
                     "in_the_witness_list")
W_PROSE = ("the_face_carries_its_only_dates_inside_prose_a_log_line_or_bulk_text_so_none_of_them_"
           "is_a_declared_witness")
W_NONE = "the_face_carries_no_date_anywhere_so_only_st_mtime_is_left"
W_UNREADABLE = "the_face_cannot_be_decoded_so_no_witness_can_be_read"
W_ABSENT = "the_named_face_is_not_on_disk_so_nothing_is_certified"
WITNESS_VOCAB = (W_UNLISTED, W_NESTED, W_UNLISTED_NESTED, W_PROSE, W_NONE, W_UNREADABLE, W_ABSENT)

# per-leg reliance class (whole-script literal scan, disclosed)
L_MENTIONS_DATE = "the_leg_script_mentions_a_date_field_name"
L_NO_DATE = "the_leg_script_mentions_no_date_field_name"
L_UNREAD = "the_leg_script_could_not_be_read"
RELIANCE_VOCAB = (L_MENTIONS_DATE, L_NO_DATE, L_UNREAD)

V_ALL_HIDDEN = ("every_no_date_face_does_carry_a_structured_date_outside_the_witness_fields_so_"
                "the_field_list_is_the_hole")
V_NONE = ("no_no_date_face_carries_a_date_anywhere_so_the_chain_certifies_bytes_it_cannot_age_"
          "and_that_nothing_refreshes")
V_SPLIT = ("the_no_date_population_splits_three_ways_between_faces_that_hold_a_structured_date_"
           "outside_the_witness_fields_faces_that_hold_only_incidental_dates_and_faces_that_hold_"
           "no_date_at_all")
V_EMPTY = "the_chain_publishes_no_relation_whose_face_lacks_a_parseable_date"
VERDICT_VOCAB = (V_ALL_HIDDEN, V_NONE, V_SPLIT, V_EMPTY)

EXISTENCE_TOKENS = ("os.path.exists(", "os.path.isfile(", "glob.glob(", "os.path.isdir(")
MAX_NODES = 4000
MAX_HITS = 40
# E180/E207 family: the study's own chain leg must never certify the face it is the subject of
SELF_EXCLUDED = ("e506_", "run_e506", "_e506")


def _is_self(script_rel):
    base = os.path.basename(script_rel or "")
    return any(base.startswith(prefix) for prefix in SELF_EXCLUDED)


def _now():
    return datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")


def _load_json(path):
    with io.open(path, encoding="utf-8-sig") as fh:
        return json.load(fh)


def _read_text(path):
    with io.open(path, encoding="utf-8-sig", errors="replace") as fh:
        return fh.read()


def _date_of(text):
    return e503._date_of(text)


def _short(value, limit=60):
    text = value if isinstance(value, str) else str(value)
    text = " ".join(text.split())
    return text[:limit]


def date_hits(payload, max_nodes=MAX_NODES, max_hits=MAX_HITS):
    """Every date-looking value in a decoded payload, with its dotted field path.

    Walks values, not keys: a key named 2026-11-07 is a name, not a witness.
    """
    hits = []
    nodes = [0]

    def walk(node, path):
        if len(hits) >= max_hits or nodes[0] >= max_nodes:
            return
        nodes[0] += 1
        if isinstance(node, dict):
            for key, value in node.items():
                walk(value, path + (str(key),))
        elif isinstance(node, (list, tuple)):
            for index, value in enumerate(node[:50]):
                walk(value, path + ("[%d]" % index,))
        elif isinstance(node, str):
            # A date is only "structured" when it is the WHOLE value.  A compact match inside a
            # longer token is not a witness: "D-20261104-05" is a decision id and
            # "T-2026-10-01-141 s1+s3" is a citation, and both were first read as dates (r1535
            # self-caught: the compact arm left kind=None and the classifier took the row anyway).
            match = ISO_RE.search(node)
            if match:
                kind = "structured" if node.strip() == match.group(0) else "prose"
            else:
                match = COMPACT_RE.search(node)
                kind = ("structured_compact" if match and node.strip() == match.group(0)
                        else "prose") if match else None
            if match:
                hits.append({"field": ".".join(path), "kind": kind,
                             "sample": _short(node)})

    walk(payload, ())
    return hits


def _classify_hits(hits):
    """One class per face, by how close the date sits to a rule the chain could apply."""
    if not hits:
        return W_NONE, None
    for hit in hits:
        segments = hit["field"].split(".")
        if hit["kind"] != "prose" and len(segments) == 1 and hit["field"] not in DATE_FIELDS:
            return W_UNLISTED, hit
    for hit in hits:
        segments = hit["field"].split(".")
        if hit["kind"] != "prose" and len(segments) > 1 and segments[-1] in DATE_FIELDS:
            return W_NESTED, hit
    for hit in hits:
        segments = hit["field"].split(".")
        if hit["kind"] != "prose" and len(segments) > 1:
            return W_UNLISTED_NESTED, hit
    for hit in hits:
        if hit["kind"] == "prose":
            return W_PROSE, hit
    return W_PROSE, hits[0]


def witness_of(face_rel, root=None, cutoff="2026-11-07"):
    root = root or ROOT
    path = os.path.join(root, face_rel.replace("/", os.sep))
    stamp = {"face": face_rel, "exists": os.path.exists(path)}
    if not stamp["exists"]:
        stamp.update({"witness_class": W_ABSENT, "bytes": None, "hits": []})
        return stamp
    stamp["bytes"] = os.path.getsize(path)
    cutoff_date = _date_of(cutoff)
    try:
        mtime = datetime.date.fromtimestamp(os.path.getmtime(path))
        stamp["mtime_age_days"] = (cutoff_date - mtime).days if cutoff_date else None
        stamp["mtime_date"] = mtime.isoformat()
    except OSError:
        stamp["mtime_age_days"] = None
        stamp["mtime_date"] = None
    try:
        payload = _load_json(path)
        stamp["stream"] = "json"
        hits = date_hits(payload)
    except (ValueError, OSError):
        stamp["stream"] = "not_json"
        try:
            text = _read_text(path)
        except OSError:
            stamp.update({"witness_class": W_UNREADABLE, "hits": []})
            return stamp
        matches = []
        for match in ISO_RE.finditer(text):
            matches.append({"field": "<text>", "kind": "prose", "sample": match.group(0)})
            if len(matches) >= MAX_HITS:
                break
        hits = matches
    stamp["hits"] = hits
    stamp["witness_class"], stamp["cheapest_hit"] = _classify_hits(hits)
    return stamp


def leg_reliance(script_rel, root=None, cache=None):
    """Whole-script literal scan: does the certifying leg's script name a date field at all?"""
    cache = cache if cache is not None else {}
    if script_rel in cache:
        return cache[script_rel]
    root = root or ROOT
    path = os.path.join(root, (script_rel or "").replace("/", os.sep))
    if not script_rel or not os.path.exists(path):
        result = {"class": L_UNREAD, "mentions": [], "tests_existence": False}
    else:
        try:
            text = _read_text(path)
        except OSError:
            result = {"class": L_UNREAD, "mentions": [], "tests_existence": False}
        else:
            mentions = [field for field in DATE_FIELDS if re.search(r"\b%s\b" % re.escape(field), text)]
            result = {"class": L_MENTIONS_DATE if mentions else L_NO_DATE,
                      "mentions": mentions,
                      "tests_existence": any(token in text for token in EXISTENCE_TOKENS)}
    cache[script_rel] = result
    return result


def collect(cutoff=None, root=None, chain_rel=None):
    """Population from E503, then one witness row per distinct face."""
    root = root or ROOT
    cutoff = cutoff or DATE_STAMP
    leg_rows, rows, meta = e503.analyse(chain_rel, root, cutoff)
    excluded = [row["leg"] for row in leg_rows if _is_self(row.get("script"))]
    rows = [row for row in rows if not _is_self(row.get("script"))]

    face_relations = {}
    for row in rows:
        for rel in row.get("relations") or []:
            face = rel["face"]
            entry = face_relations.setdefault(face, {
                "face": face, "relations": 0, "certifying_legs": [], "template": False,
                "nodate": False, "writer_legs": set(), "e503_classes": []})
            if row["leg"] not in entry["certifying_legs"]:
                entry["certifying_legs"].append(row["leg"])
            entry["relations"] += 1
            entry["template"] = entry["template"] or bool(rel.get("template"))
            entry["e503_classes"].append(rel.get("class"))
            if rel.get("class") == e503.C_NODATE:
                entry["nodate"] = True
            for writer in rel.get("writer_legs") or []:
                entry["writer_legs"].add(writer)

    scripts = {row["leg"]: row.get("script") for row in rows}
    cache = {}
    rows_out = []
    for face, entry in sorted(face_relations.items()):
        if not entry["nodate"]:
            continue
        stamp = witness_of(face, root, cutoff)
        legs = []
        for leg in entry["certifying_legs"]:
            reliance = leg_reliance(scripts.get(leg), root, cache)
            legs.append({"leg": leg, "script": scripts.get(leg),
                         "reliance_class": reliance["class"],
                         "date_fields_mentioned": reliance["mentions"],
                         "tests_existence": reliance["tests_existence"]})
        rows_out.append({
            "face": face,
            "bytes": stamp.get("bytes"),
            "stream": stamp.get("stream"),
            "witness_class": stamp["witness_class"],
            "cheapest_hit": stamp.get("cheapest_hit"),
            "hits": (stamp.get("hits") or [])[:5],
            "dates_found": len(stamp.get("hits") or []),
            "mtime_date": stamp.get("mtime_date"),
            "mtime_age_days": stamp.get("mtime_age_days"),
            "relations": entry["relations"],
            "certifying_legs": entry["certifying_legs"],
            "leg_reliance": legs,
            "writer_free": not entry["writer_legs"],
            "writer_legs": sorted(entry["writer_legs"]),
            "template": entry["template"],
            "e503_nodate": True,
        })
    meta_out = {"evidence_cutoff": meta.get("evidence_cutoff"),
                "mtime_floor_days": meta.get("mtime_floor_days"),
                "e503_relations": sum(
                    len(row.get("relations") or []) for row in rows),
                "e503_nodate_relations": sum(
                    1 for row in rows for rel in (row.get("relations") or [])
                    if rel.get("class") == e503.C_NODATE),
                "self_excluded_legs": excluded}
    published = None
    try:
        prior = _load_json(os.path.join(root, "results", "state_tilt", e503.FACE_NAME))
        published = ((prior.get("summary") or {}).get("relations_by_class") or {}).get(
            e503.C_NODATE)
    except (ValueError, OSError):
        published = None
    meta_out["published_e503_nodate_relations"] = published
    meta_out["nodate_relations_delta_vs_published_e503"] = (
        meta_out["e503_nodate_relations"] - published if published is not None else None)
    return rows_out, meta_out


def summary_of(rows, meta):
    by_class = {key: 0 for key in WITNESS_VOCAB}
    by_stream = {}
    bytes_total = 0
    bytes_class = {}
    writer_free = 0
    bytes_writer_free = 0
    legs_mention = 0
    legs_total = 0
    legs_existence = 0
    relations = 0
    template_faces = 0
    ages = []
    for row in rows:
        klass = row.get("witness_class")
        by_class[klass] = by_class.get(klass, 0) + 1
        size = row.get("bytes") or 0
        bytes_total += size
        bytes_class[klass] = bytes_class.get(klass, 0) + size
        stream = row.get("stream") or "unknown"
        by_stream[stream] = by_stream.get(stream, 0) + 1
        relations += row.get("relations") or 0
        if row.get("writer_free"):
            writer_free += 1
            bytes_writer_free += size
        if row.get("template"):
            template_faces += 1
        if row.get("mtime_age_days") is not None:
            ages.append(row["mtime_age_days"])
        for leg in row.get("leg_reliance") or []:
            legs_total += 1
            if leg.get("reliance_class") == L_MENTIONS_DATE:
                legs_mention += 1
            if leg.get("tests_existence"):
                legs_existence += 1
    hidden = (by_class[W_UNLISTED] + by_class[W_NESTED] + by_class[W_UNLISTED_NESTED])
    bytes_structured_hidden = (bytes_class.get(W_UNLISTED, 0) + bytes_class.get(W_NESTED, 0)
                               + bytes_class.get(W_UNLISTED_NESTED, 0))
    bytes_no_declared = bytes_class.get(W_NONE, 0) + bytes_class.get(W_PROSE, 0)
    return {
        "faces": len(rows),
        "relations": relations,
        "relations_per_e503": meta.get("e503_nodate_relations"),
        "published_e503_nodate_relations": meta.get("published_e503_nodate_relations"),
        "nodate_relations_delta_vs_published_e503": meta.get(
            "nodate_relations_delta_vs_published_e503"),
        "self_excluded_legs": len(meta.get("self_excluded_legs") or []),
        "bytes_total": bytes_total,
        "by_class": by_class,
        "bytes_by_class": bytes_class,
        "by_stream": by_stream,
        "faces_with_a_structured_date_outside_the_witness_fields": hidden,
        "bytes_with_a_structured_date_outside_the_witness_fields": bytes_structured_hidden,
        "faces_with_only_incidental_dates": by_class[W_PROSE],
        "faces_with_no_declared_witness": by_class[W_PROSE] + by_class[W_NONE],
        "bytes_with_no_declared_witness": bytes_no_declared,
        "faces_with_no_date_anywhere": by_class[W_NONE],
        "bytes_with_no_witness_anywhere": bytes_class[W_NONE],
        "faces_writer_free": writer_free,
        "bytes_writer_free": bytes_writer_free,
        "template_faces": template_faces,
        "certifying_legs": legs_total,
        "certifying_legs_mentioning_a_date_field": legs_mention,
        "certifying_legs_testing_existence": legs_existence,
        "mention_axis_informative": 0 < legs_mention < legs_total,
        "mtime_age_days_max": max(ages) if ages else None,
        "mtime_age_days_median": sorted(ages)[len(ages) // 2] if ages else None,
        "mtime_floor_days": meta.get("mtime_floor_days"),
        "evidence_cutoff": meta.get("evidence_cutoff"),
    }


def _verdict(summary):
    if not summary["faces"]:
        return V_EMPTY
    hidden = summary["faces_with_a_structured_date_outside_the_witness_fields"]
    none = summary["faces_with_no_date_anywhere"]
    if hidden == summary["faces"]:
        return V_ALL_HIDDEN
    if none == summary["faces"]:
        return V_NONE
    return V_SPLIT


def build(root=None, write=True, chain_rel=None, cutoff=None):
    root = root or ROOT
    rows, meta = collect(cutoff, root, chain_rel)
    summary = summary_of(rows, meta)
    face = {
        "study": STUDY,
        "card": CARD,
        "title": ("For every face E503 priced as carrying no parseable date: what freshness "
                  "witness does its payload actually hold, how many bytes are certified with no "
                  "witness at all, and is the face also writer-free?"),
        "evidence_cutoff": meta["evidence_cutoff"],
        "generated": _now(),
        "population_source": POPULATION_SOURCE,
        "witness_vocab": list(WITNESS_VOCAB),
        "reliance_vocab": list(RELIANCE_VOCAB),
        "verdict_vocab": list(VERDICT_VOCAB),
        "method_limits": [
            "the population is E503's C_NODATE relations re-derived in this window, not a "
            "separate chain parse",
            "a witness is a date-shaped VALUE anywhere in the payload; keys that look like "
            "dates are not witnesses",
            "the cheapest-hit field is the first hit in document order for its class, so it is "
            "an example of the fix, not necessarily the only one",
            "reliance is a whole-script literal scan (does the leg's script name a date field / "
            "an existence test at all) -- it does not prove the leg reads THIS face's date",
            "st_mtime cannot age anything in this tree: every file is materialised at checkout "
            "(E453); the measured floor is published beside the mtime ages",
            "writer-free means no writing-mode leg in this chain names the face -- a writer run "
            "by hand or by another agent is invisible here",
        ],
        "summary": summary,
        "verdict": _verdict(summary),
        "rows": rows,
    }
    if write:
        write_face(face, root)
    return face


def write_face(face, root=None):
    root = root or ROOT
    outdir = os.path.join(root, "results", "state_tilt")
    if not os.path.isdir(outdir):
        os.makedirs(outdir)
    body = json.dumps(face, ensure_ascii=False, indent=1, sort_keys=True)
    for name in (FACE_NAME, "%s-%s.json" % (DATED_PREFIX, DATE_STAMP)):
        with io.open(os.path.join(outdir, name), "w", encoding="utf-8", newline="\n") as fh:
            fh.write(body + "\n")


def row_problems(face):
    problems = []
    rows = face.get("rows") or []
    summary = face.get("summary") or {}
    meta = {"evidence_cutoff": summary.get("evidence_cutoff"),
            "mtime_floor_days": summary.get("mtime_floor_days"),
            "e503_nodate_relations": summary.get("relations_per_e503"),
            "published_e503_nodate_relations": summary.get("published_e503_nodate_relations"),
            "nodate_relations_delta_vs_published_e503": summary.get(
                "nodate_relations_delta_vs_published_e503"),
            "self_excluded_legs": [None] * int(summary.get("self_excluded_legs") or 0)}
    fresh = summary_of(rows, meta)
    for key, value in fresh.items():
        if summary.get(key) != value:
            problems.append("summary.%s=%r does not re-derive from the rows (%r)"
                            % (key, summary.get(key), value))
    if (summary.get("published_e503_nodate_relations") is not None
            and summary.get("nodate_relations_delta_vs_published_e503") is not None
            and summary.get("relations_per_e503") - summary.get(
                "published_e503_nodate_relations") != summary.get(
                "nodate_relations_delta_vs_published_e503")):
        problems.append("the delta against the published E503 count does not add up")
    if face.get("verdict") != _verdict(fresh):
        problems.append("verdict=%r does not re-derive from the rows (%r)"
                        % (face.get("verdict"), _verdict(fresh)))
    seen = set()
    for row in rows:
        klass = row.get("witness_class")
        if klass not in WITNESS_VOCAB:
            problems.append("%s: witness class %r outside the vocabulary" % (row.get("face"), klass))
            continue
        if row.get("face") in seen:
            problems.append("%s: published twice" % row.get("face"))
        seen.add(row.get("face"))
        if not row.get("e503_nodate"):
            problems.append("%s: row is not from the C_NODATE population" % row.get("face"))
        if not (row.get("relations") or 0) >= 1:
            problems.append("%s: a certifying relation must exist to be in the population"
                            % row.get("face"))
        if not row.get("certifying_legs"):
            problems.append("%s: no certifying leg" % row.get("face"))
        if klass == W_NONE and row.get("dates_found"):
            problems.append("%s: classed none but found %r dates"
                            % (row.get("face"), row.get("dates_found")))
        if klass != W_NONE and not row.get("dates_found"):
            problems.append("%s: classed %r but found no date" % (row.get("face"), klass))
        if klass in (W_UNLISTED, W_NESTED, W_UNLISTED_NESTED, W_PROSE) and not row.get("cheapest_hit"):
            problems.append("%s: hidden date class without the hit that proves it"
                            % row.get("face"))
        for hit in row.get("hits") or []:
            if hit.get("kind") not in ("structured", "structured_compact", "prose"):
                problems.append("%s: hit %r carries no usable kind"
                                % (row.get("face"), hit.get("field")))
            if klass in (W_UNLISTED, W_NESTED, W_UNLISTED_NESTED) and hit.get("kind") == "prose" \
                    and row.get("cheapest_hit") == hit:
                problems.append("%s: a hidden class rests on a prose hit" % row.get("face"))
        if row.get("writer_free") and row.get("writer_legs"):
            problems.append("%s: writer-free yet names %r writers"
                            % (row.get("face"), row.get("writer_legs")))
        for leg in row.get("leg_reliance") or []:
            if leg.get("reliance_class") not in RELIANCE_VOCAB:
                problems.append("%s/%s: reliance class %r outside the vocabulary"
                                % (row.get("face"), leg.get("leg"), leg.get("reliance_class")))
            if leg.get("reliance_class") == L_MENTIONS_DATE and not leg.get("date_fields_mentioned"):
                problems.append("%s/%s: mentions-date class with no mentioned field"
                                % (row.get("face"), leg.get("leg")))
    return problems


def check(face=None, root=None):
    root = root or ROOT
    face = face or _load_json(os.path.join(root, "results", "state_tilt", FACE_NAME))
    problems = row_problems(face)
    print("check problems=%r" % (problems,))
    return 0 if not problems else 1


def verify(root=None):
    root = root or ROOT
    face = build(root, write=False)
    problems = row_problems(face)
    print("verify problems=%r" % (problems,))
    print("verdict=%s" % face["verdict"])
    print("summary=%s" % json.dumps(face["summary"], ensure_ascii=False, sort_keys=True))
    return 0 if not problems else 1


# ---------------------------------------------------------------- selftest

UNLISTED_FIXTURE = {"built": "2026-10-02", "payload": [1, 2, 3]}
NESTED_FIXTURE = {"meta": {"generated": "2026-10-03"}, "n": 4}
PROSE_FIXTURE = {"note": "panel 2026-10-04 (bars 10-15)", "n": 5}
NONE_FIXTURE = {"count": 7, "names": ["a", "b"], "flag": True}
LIST_FIXTURE = {"stamps": ["2026-10-05", "2026-10-06"]}
KEY_ONLY_FIXTURE = {"2026-10-07": {"n": 1}}


def selftest():
    checks = 0
    failures = []
    import tempfile

    def ok(label, cond, extra=""):
        nonlocal checks
        checks += 1
        if not cond:
            failures.append("%s %s" % (label, extra))

    # --- classifier, no disk
    hits = date_hits(UNLISTED_FIXTURE)
    klass, hit = _classify_hits(hits)
    ok("unlisted top-level field is the cheapest fix", klass == W_UNLISTED, (klass, hits))
    ok("the unlisted hit names the field", hit and hit["field"] == "built", hit)

    klass, hit = _classify_hits(date_hits(NESTED_FIXTURE))
    ok("a witness field below the top level is its own class", klass == W_NESTED, klass)
    ok("the nested hit carries the dotted path", hit and hit["field"] == "meta.generated", hit)

    klass, hit = _classify_hits(date_hits(PROSE_FIXTURE))
    ok("a date inside prose is its own class", klass == W_PROSE, klass)

    ok("a payload with no date yields no hits", date_hits(NONE_FIXTURE) == [])
    klass, _ = _classify_hits([])
    ok("no hits classes as none", klass == W_NONE, klass)

    ok("a date inside a list is found", bool(date_hits(LIST_FIXTURE)))
    ok("a date-shaped KEY is not a witness", date_hits(KEY_ONLY_FIXTURE) == [])
    # r1535 self-caught: a compact date inside a longer token is not a structured witness
    decision_hits = date_hits({"decision": "D-20261104-05"})
    ok("a decision id is not a structured date",
       decision_hits and decision_hits[0]["kind"] == "prose", decision_hits)
    ok("a decision id does not class as an unlisted date field",
       _classify_hits(decision_hits)[0] == W_PROSE, _classify_hits(decision_hits)[0])
    citation_hits = date_hits({"law_ref": "firm/X.md v1.0 (T-2026-10-01-141 s1+s3)"})
    ok("a citation is prose, not a witness",
       citation_hits and citation_hits[0]["kind"] == "prose", citation_hits)
    ok("a compact WHOLE value is structured",
       (date_hits({"built": "20261005"}) or [{}])[0].get("kind") == "structured_compact")
    ok("every hit carries a kind (no None arm)",
       all(hit.get("kind") in ("structured", "structured_compact", "prose")
           for hit in date_hits({"a": "D-20261104-05", "b": "2026-10-01",
                                 "c": "prose 2026-10-02 here", "d": "20261005"})))

    ok("a prose date does not parse as a witness date (E207 family)",
       _date_of("panel 2026-11-07 (bars 10-15)") is None)

    # --- witness_of against fixtures on disk
    tmp = tempfile.mkdtemp(prefix="e506_")
    outdir = os.path.join(tmp, "results", "state_tilt")
    os.makedirs(outdir)
    fixtures = {"unlisted.json": UNLISTED_FIXTURE, "nested.json": NESTED_FIXTURE,
                "prose.json": PROSE_FIXTURE, "none.json": NONE_FIXTURE,
                "keyonly.json": KEY_ONLY_FIXTURE}
    for name, payload in fixtures.items():
        with io.open(os.path.join(outdir, name), "w", encoding="utf-8", newline="\n") as fh:
            json.dump(payload, fh)
    with io.open(os.path.join(outdir, "notes.md"), "w", encoding="utf-8", newline="\n") as fh:
        fh.write("# notes\n\ncutoff 2026-10-08\n")

    got = {}
    for name in list(fixtures) + ["notes.md", "absent.json"]:
        got[name] = witness_of("results/state_tilt/" + name, tmp)["witness_class"]
    ok("disk unlisted", got["unlisted.json"] == W_UNLISTED, got)
    ok("disk nested", got["nested.json"] == W_NESTED, got)
    ok("disk prose", got["prose.json"] == W_PROSE, got)
    ok("disk none", got["none.json"] == W_NONE, got)
    ok("key-only face is none", got["keyonly.json"] == W_NONE, got)
    ok("a text face with a date is prose", got["notes.md"] == W_PROSE, got)
    ok("an absent face is absent", got["absent.json"] == W_ABSENT, got)

    # --- reliance scan
    script = os.path.join(tmp, "scripts", "dated_leg.py")
    os.makedirs(os.path.join(tmp, "scripts"))
    with io.open(script, "w", encoding="utf-8", newline="\n") as fh:
        fh.write("import os\n"
                 "def check():\n"
                 "    assert os.path.exists('results/state_tilt/unlisted.json')\n"
                 "    return {'evidence_cutoff': '2026-11-07'}\n")
    reliance = leg_reliance("scripts/dated_leg.py", tmp)
    ok("a leg naming a date field is classed as such", reliance["class"] == L_MENTIONS_DATE,
       reliance)
    ok("the mentioned field is published", "evidence_cutoff" in reliance["mentions"], reliance)
    ok("the existence test is detected", reliance["tests_existence"] is True, reliance)
    quiet = leg_reliance("scripts/absent_leg.py", tmp)
    ok("an unreadable leg is not silently 'no date'", quiet["class"] == L_UNREAD, quiet)

    # --- gate on a small in-memory face
    rows = [
        {"face": "results/state_tilt/unlisted.json", "bytes": 40, "stream": "json",
         "witness_class": W_UNLISTED,
         "cheapest_hit": {"field": "built", "kind": "structured", "sample": "2026-10-02"},
         "dates_found": 1, "mtime_date": "2026-11-07", "mtime_age_days": 0, "relations": 2,
         "certifying_legs": ["beta_check"],
         "leg_reliance": [{"leg": "beta_check", "script": "scripts/dated_leg.py",
                           "reliance_class": L_MENTIONS_DATE,
                           "date_fields_mentioned": ["evidence_cutoff"],
                           "tests_existence": True}],
         "writer_free": True, "writer_legs": [], "template": False, "e503_nodate": True},
        {"face": "results/state_tilt/none.json", "bytes": 20, "stream": "json",
         "witness_class": W_NONE, "cheapest_hit": None, "dates_found": 0,
         "mtime_date": "2026-11-07", "mtime_age_days": 0, "relations": 1,
         "certifying_legs": ["gamma_scan"],
         "leg_reliance": [{"leg": "gamma_scan", "script": "scripts/absent_leg.py",
                           "reliance_class": L_UNREAD, "date_fields_mentioned": [],
                           "tests_existence": False}],
         "writer_free": False, "writer_legs": ["alpha_build"], "template": False,
         "e503_nodate": True},
    ]
    meta = {"evidence_cutoff": "2026-11-07", "mtime_floor_days": 21, "e503_nodate_relations": 3}
    summary = summary_of(rows, meta)
    face = {"rows": rows, "summary": summary, "verdict": _verdict(summary)}
    ok("fixture gate passes", row_problems(face) == [], row_problems(face))
    ok("fixture verdict is split", face["verdict"] == V_SPLIT, face["verdict"])
    ok("fixture counts one hidden / one none",
       (summary["faces_with_a_structured_date_outside_the_witness_fields"],
        summary["faces_with_no_date_anywhere"]) == (1, 1), summary)

    doctored = json.loads(json.dumps(face))
    doctored["verdict"] = V_ALL_HIDDEN
    ok("gate refuses a hand-written verdict", row_problems(doctored) != [])
    doctored2 = json.loads(json.dumps(face))
    doctored2["summary"]["bytes_total"] += 1
    ok("gate refuses a hand-written count", row_problems(doctored2) != [])
    doctored3 = json.loads(json.dumps(face))
    doctored3["rows"][0]["witness_class"] = W_NONE
    ok("gate refuses a hidden class with no hit", row_problems(doctored3) != [])
    doctored4 = json.loads(json.dumps(face))
    doctored4["rows"][0]["e503_nodate"] = False
    ok("gate refuses a row outside the population", row_problems(doctored4) != [])
    doctored5 = json.loads(json.dumps(face))
    doctored5["rows"][1]["writer_free"] = True
    ok("gate refuses writer-free next to named writers", row_problems(doctored5) != [])

    # --- real population sanity (no verdict assertion: the tree may grow)
    real_rows, real_meta = collect("2026-11-07", ROOT) if os.path.exists(
        os.path.join(ROOT, "Tools", "s6_chain_bmb.py")) else ([], {})
    ok("real population is non-empty", len(real_rows) > 50, len(real_rows))
    ok("every real row carries a certifying leg",
       all(row["certifying_legs"] for row in real_rows))
    ok("real relations match their face rows",
       sum(row["relations"] for row in real_rows) >= len(real_rows))

    print("selftest %d/%d" % (checks - len(failures), checks))
    for failure in failures:
        print("FAIL: %s" % failure)
    return 0 if not failures else 1


def main(argv=None):
    argv = list(sys.argv[1:] if argv is None else argv)
    mode = argv[0] if argv else "run"
    if mode in ("run", "build"):
        face = build()
        print("verdict=%s" % face["verdict"])
        print("summary=%s" % json.dumps(face["summary"], ensure_ascii=False, sort_keys=True))
        return 0
    if mode == "check":
        return check()
    if mode == "verify":
        return verify()
    if mode == "selftest":
        return selftest()
    print("unknown mode %r" % mode)
    return 2


if __name__ == "__main__":
    sys.exit(main())