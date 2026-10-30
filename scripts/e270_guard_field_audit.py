"""E270 -- does every published face a screen reads actually carry the guard's inputs?

E267 shrank the transfer screen to one operative rule: judge a row with its OWN side's p95, i.e.
compare a donor against `b/band_edge` on the side the row already sits beyond.  E268 then showed
the row's own p95 is the one number a reader of a table does not have, and that the pooled tight
end can substitute for it.  Both of those are statements about NUMBERS THAT WERE PUBLISHED -- so
the screen's reach is bounded by which faces actually carry the four inputs it consumes:

    b, band_lo, band_hi  -- the row's band and where it sits
    own_p95              -- the end the guard compares the donor against

A face can publish a verdict (moved / not moved, outside / inside) while dropping the inputs that
produce it.  That is not a defect of the arithmetic, it is a limit on what a reader can re-run,
and this family has already had one face whose verdict could not be re-decided from its own page.

So: enumerate the published band family, and for every record collection in it report
  - which of the four guard inputs are present (a None is ABSENT; 0.0 is a value),
  - how many records carry ALL four (the guard-runnable ones),
  - which verdict-shaped fields sit on records that carry none of them,
and then CROSS-CHECK THE VALUES, because presence is not agreement: the same row index appears in
six faces and its own_p95 must be the same number in all of them.

Reads: every results/state_tilt/BAND*.json (latest mirrors excluded, they are byte copies).
Writes: results/state_tilt/BANDFIELDS-2026-10-29.json.  No engine, no draws, no admission.
"""
from __future__ import print_function

import io
import json
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
OUTDIR = os.path.join(ROOT, "results", "state_tilt")

STUDY = "E270_guard_field_audit"
TITLE = "does every published face a screen reads actually carry the guard's inputs?"
CUTOFF = "2026-10-29"
FACE = "BANDFIELDS-%s.json" % CUTOFF
LATEST = "bandfields_latest.json"

# The four numbers E267/E268's guard consumes, per row.  Frozen: this is the rule as published.
GUARD_INPUTS = ("b", "band_lo", "band_hi", "own_p95")
# Fields that state a judgement about a row or a comparison.  Used only to NAME which records
# carry a verdict without its inputs -- the audit never re-decides any of them.
VERDICT_HINTS = ("verdict", "verdict_wide", "verdict_tight", "published_verdict_wide",
                 "own_verdict", "actual_moved", "predicted", "moved", "n_moved", "m_star",
                 "flips_from_published_at_any_end", "inside_at_every_end")

DOMAIN_PREFIX = "BAND"
DOMAIN_SUFFIX = ".json"
LATEST_SUFFIX = "_latest.json"
# this study's own face lands inside the domain it scans: a second burn would audit the audit
# (r1238 self-inclusion defect) -- excluded by name, and the exclusion is published
SELF_EXCLUDED_PREFIXES = ("BANDFIELDS",)
CANON_FACE = "BANDTRANSFER"      # the face E262 published the row records on
JOIN_TOL = 1e-9

NO_BILL = ("measurement only: the published band faces are re-read and field-checked; no shuffle "
           "stream is drawn, no band is rebuilt, no engine runs. A field that is present here is "
           "present on disk -- nothing is re-derived from the market.")

VERDICT_VOCAB = (
    "guard_inputs_are_published_where_the_screen_runs",
    "guard_inputs_are_face_local",
    "guard_inputs_disagree_across_faces",
    "no_guard_bearing_record",
)


# ------------------------------------------------------------------ field presence
def present(rec, field):
    """A key with a None value is ABSENT -- but 0.0 is a value, not a missing number."""
    return isinstance(rec, dict) and field in rec and rec[field] is not None


def collections_of(doc, prefix=""):
    """Every list-of-dicts anywhere in the document, with its path.

    The band faces nest their row lists at different depths (rows, comparison_rows,
    comparison_margins, curves/cells/pairs), so the audit walks instead of naming keys -- and
    prints the path it walked to, so a collection the reader expects is never silently absent.
    """
    out = []
    if isinstance(doc, dict):
        for key in sorted(doc):
            val = doc[key]
            path = "%s/%s" % (prefix, key)
            if isinstance(val, list) and val and isinstance(val[0], dict):
                out.append((path, val))
            elif isinstance(val, (dict, list)):
                out.extend(collections_of(val, path))
    elif isinstance(doc, list):
        for idx, val in enumerate(doc):
            path = "%s[%d]" % (prefix, idx)
            if isinstance(val, (dict, list)):
                out.extend(collections_of(val, path))
    return out


def classify(records, path):
    """Field census for one record collection."""
    fields = {}
    for field in GUARD_INPUTS:
        n = sum(1 for rec in records if present(rec, field))
        fields[field] = {"present": n, "absent": len(records) - n}
    complete = sum(1 for rec in records if all(present(rec, f) for f in GUARD_INPUTS))
    verdict_fields = sorted({f for rec in records if isinstance(rec, dict)
                             for f in VERDICT_HINTS if present(rec, f)})
    indexed = sum(1 for rec in records if present(rec, "index"))
    return {
        "path": path,
        "n_records": len(records),
        "n_complete": complete,
        "n_partial": len(records) - complete,
        "fields": fields,
        "missing_fields": [f for f in GUARD_INPUTS if fields[f]["present"] == 0],
        "partial_fields": [f for f in GUARD_INPUTS
                           if 0 < fields[f]["present"] < len(records)],
        "verdict_fields": verdict_fields,
        "n_indexed": indexed,
        "guard_runnable": bool(len(records) and complete == len(records)),
    }


def _buffer(cols):
    """Collections carrying `b` with no band at all: the clearance curves' buffer grid.

    `b` is two different numbers in this family (the row's own move, and a buffer sweep), so a
    buffer row must not be filed as a half-instrumented ROW -- it is published under its own name.
    """
    return [c["path"] for c in cols
            if c["fields"]["b"]["present"] > 0
            and c["fields"]["band_lo"]["present"] == 0
            and c["fields"]["band_hi"]["present"] == 0]


def scan_face(doc):
    cols = [classify(recs, path) for path, recs in collections_of(doc)]
    guard = [c for c in cols if any(c["fields"][f]["present"] for f in GUARD_INPUTS)]
    verdict = [c for c in cols if c["verdict_fields"]]
    return {
        "collections": cols,
        "guard_collections": [c["path"] for c in guard],
        "guard_runnable_collections": [c["path"] for c in guard if c["guard_runnable"]],
        # a collection that states a judgement on records carrying NONE of the four numbers
        "collections_with_verdict_but_no_inputs": [c["path"] for c in verdict
                                                  if c["n_complete"] == 0
                                                  and c["path"] not in _buffer(cols)],
        # `b` is not one number across this family: it is the row's own move in the row faces and
        # a buffer grid in the clearance curves.
        "b_without_a_band": _buffer(cols),
        "n_records_guard_runnable": sum(c["n_complete"] for c in guard),
        "n_records_with_verdict_but_no_inputs": sum(c["n_records"] for c in verdict
                                                    if c["n_complete"] == 0),
    }


# ------------------------------------------------------------------ cross-face value join
def index_key(rec):
    if not present(rec, "index"):
        return None
    parts = [rec.get("index")]
    for extra in ("leg", "base", "cell"):
        if present(rec, extra):
            parts.append(rec.get(extra))
    return tuple(parts)


def canon_map(doc):
    """The most fully-instrumented row collection in the canonical face, keyed for joining.

    Not "the complete one": unmeasured rows legitimately carry None in the very fields the join
    checks, so requiring every record to be complete would find no canonical face at all and the
    value cross-check would silently publish zero cells compared.
    """
    best = None
    for path, recs in collections_of(doc):
        c = classify(recs, path)
        if c["n_complete"] == 0 or not c["n_indexed"]:
            continue
        if best is None or c["n_complete"] > best[1]["n_complete"]:
            best = (path, c, recs)
    if best is None:
        return {"path": None, "records": 0, "basis": "none", "map": {}}
    path, c, recs = best
    recs = [r for r in recs if index_key(r) is not None]
    raw = [index_key(r) for r in recs]
    # duplicate index alone is not a usable key: fall back to the composite the records carry
    basis = "index" if len({r[0] for r in raw}) == len(recs) else "composite"
    mapping = {}
    for rec, key in zip(recs, raw):
        if basis == "index":
            key = (key[0],)
        mapping[key] = rec
    return {"path": path, "records": len(mapping), "basis": basis,
            "n_complete": c["n_complete"], "map": mapping}


def join_collection(records, canon, tol=JOIN_TOL):
    """Compare every shared guard number between a face's records and the canonical rows."""
    mapping = canon["map"]
    basis = canon["basis"]
    out = {"n_records": len(records), "joined": 0, "unjoined": 0, "cells_compared": 0,
           "agree": 0, "disagree": 0, "max_abs_diff": None, "disagreeing": []}
    if not mapping or basis == "none":
        out["reason"] = "no canonical row to join against"
        return out
    for rec in records:
        key = index_key(rec)
        if key is None:
            out["unjoined"] += 1
            continue
        look = (key[0],) if basis == "index" else key
        ref = mapping.get(look)
        if ref is None:
            out["unjoined"] += 1
            continue
        out["joined"] += 1
        for field in GUARD_INPUTS:
            if not present(rec, field) or not present(ref, field):
                continue
            a, b = rec[field], ref[field]
            if not isinstance(a, (int, float)) or not isinstance(b, (int, float)):
                continue
            diff = abs(float(a) - float(b))
            out["cells_compared"] += 1
            if out["max_abs_diff"] is None or diff > out["max_abs_diff"]:
                out["max_abs_diff"] = diff
            if diff <= tol:
                out["agree"] += 1
            else:
                out["disagree"] += 1
                if len(out["disagreeing"]) < 8:
                    out["disagreeing"].append({"index": rec.get("index"), "field": field,
                                               "face_value": a, "canonical_value": b,
                                               "abs_diff": diff})
    return out


# ------------------------------------------------------------------ verdict
def verdict_of(summary):
    if summary["guard_columns"] == 0:
        return ("no_guard_bearing_record",
                "no published collection in the domain carries any of b / band_lo / band_hi / "
                "own_p95: the guard cannot be applied from the tables at all")
    if summary["value_disagreements"] > 0:
        return ("guard_inputs_disagree_across_faces",
                ("%d of %d joined guard cell(s) disagree with the canonical row (max |diff| %r): "
                 "the same row is published as two different numbers, so presence is not "
                 "agreement and a reader picking a different face gets a different screen"
                 % (summary["value_disagreements"], summary["cells_compared"],
                    summary["max_abs_diff"])))
    if summary["verdict_collections_without_inputs"] > 0:
        return ("guard_inputs_are_face_local",
                ("%d verdict-bearing collection(s) (%d records) publish a judgement without the "
                 "four inputs, while the guard's own triple lives on %d collection(s) (%d "
                 "record(s), %d of them on measured rows only): the screen is a table recipe on "
                 "the faces that carry it and a black box on the rest"
                 % (summary["verdict_collections_without_inputs"],
                    summary["records_with_verdict_but_no_inputs"],
                    summary["guard_complete_collections"],
                    summary["records_guard_runnable"],
                    summary["guard_complete_on_measured_rows_only"])))
    return ("guard_inputs_are_published_where_the_screen_runs",
            ("every verdict-bearing collection carries all four guard inputs and all %d joined "
             "cell(s) agree with the canonical rows: the screen is fully re-runnable from the "
             "published tables" % summary["cells_compared"]))


# ------------------------------------------------------------------ run
def _stamp():
    import datetime
    return datetime.datetime.now().strftime("%Y-%m-%dT%H:%M:%S")


def domain_faces(outdir, self_excluded=SELF_EXCLUDED_PREFIXES):
    names = []
    if not os.path.isdir(outdir):
        return names
    for name in sorted(os.listdir(outdir)):
        if not name.startswith(DOMAIN_PREFIX) or not name.endswith(DOMAIN_SUFFIX):
            continue
        if name.endswith(LATEST_SUFFIX):
            continue          # byte copies of the dated face -- counting them double-counts
        if any(name.startswith(pre) for pre in self_excluded):
            continue          # this study's own face may not be one of its own inputs
        names.append(name)
    return names


def run(save=True, outdir=None, only=None):
    outdir = outdir or OUTDIR
    faces = []
    canon = {"path": None, "records": 0, "basis": "none", "map": {}}
    canon_doc = None
    names = domain_faces(outdir)
    inventory_note = None
    if only is not None:
        # verify re-derives over the inventory this face was PUBLISHED with: faces land while the
        # machine keeps working, and a count that silently moves with the directory is not a
        # re-derivable number (a new BAND* face appeared mid-round and moved every total).
        keep = [n for n in names if n in set(only)]
        gone = [n for n in only if n not in set(names)]
        if gone:
            inventory_note = "published face(s) missing from the domain: %s" % ",".join(gone)
        names = keep
    for name in names:
        path = os.path.join(outdir, name)
        with io.open(path, encoding="utf-8") as fh:
            doc = json.load(fh)
        if name.startswith(CANON_FACE) and canon_doc is None:
            canon_doc = doc
        scan = scan_face(doc)
        faces.append({"face": name, "verdict": doc.get("verdict"), "scan": scan,
                      "joins": {}})
    if canon_doc is not None:
        canon = canon_map(canon_doc)
        for entry in faces:
            path = os.path.join(outdir, entry["face"])
            with io.open(path, encoding="utf-8") as fh:
                doc = json.load(fh)
            entry["joins"] = {p: join_collection(recs, canon)
                              for p, recs in collections_of(doc)
                              if any(present(r, f) for r in recs for f in GUARD_INPUTS)}

    cells = sum(j["cells_compared"] for e in faces for j in e["joins"].values())
    complete_cols = [{"face": e["face"], "path": c["path"], "n_complete": c["n_complete"],
                      "n_records": c["n_records"]}
                     for e in faces for c in e["scan"]["collections"] if c["n_complete"] > 0]
    disagree = sum(j["disagree"] for e in faces for j in e["joins"].values())
    diffs = [j["max_abs_diff"] for e in faces for j in e["joins"].values()
             if j["max_abs_diff"] is not None]
    guard_cols = sum(len(e["scan"]["guard_collections"]) for e in faces)
    verdict_cols = sum(len(e["scan"]["collections_with_verdict_but_no_inputs"]) for e in faces)
    summary = {
        "faces_scanned": len(faces),
        "collections_scanned": sum(len(e["scan"]["collections"]) for e in faces),
        "guard_columns": guard_cols,
        "guard_runnable_columns": sum(len(e["scan"]["guard_runnable_collections"])
                                      for e in faces),
        "guard_complete_collections": len(complete_cols),
        "guard_complete_on_measured_rows_only": sum(1 for c in complete_cols
                                                    if c["n_complete"] < c["n_records"]),
        "records_guard_runnable": sum(e["scan"]["n_records_guard_runnable"] for e in faces),
        "verdict_collections_without_inputs": verdict_cols,
        "records_with_verdict_but_no_inputs": sum(e["scan"]["n_records_with_verdict_but_no_inputs"]
                                                  for e in faces),
        "joined_records": sum(j["joined"] for e in faces for j in e["joins"].values()),
        "unjoined_records": sum(j["unjoined"] for e in faces for j in e["joins"].values()),
        "cells_compared": cells,
        "value_agreements": sum(j["agree"] for e in faces for j in e["joins"].values()),
        "value_disagreements": disagree,
        "max_abs_diff": max(diffs) if diffs else None,
        "canonical_face": canon_doc is not None and CANON_FACE or None,
        "canonical_path": canon.get("path"),
        "canonical_basis": canon.get("basis"),
        "canonical_records": canon.get("records"),
        "collections_carrying_b_without_a_band": sum(len(e["scan"]["b_without_a_band"])
                                                     for e in faces),
        "resolve_note": ("join keys are (index) when unique in the canonical face, else "
                         "(index, leg, base, cell); records without an index are counted as "
                         "unjoined, never dropped"),
    }
    verdict, why = verdict_of(summary)
    summary["verdict"] = verdict

    out = {
        "study": STUDY,
        "title": TITLE,
        "evidence_cutoff": CUTOFF,
        "generated": _stamp(),
        "no_bill": NO_BILL,
        "source_faces": [e["face"] for e in faces],
        "inventory_note": inventory_note or (
            "the counts below are those of THIS inventory: the domain grows whenever the machine "
            "publishes another dated BAND* face, so verify re-derives over the published list "
            "rather than over whatever is on disk at verification time"),
        "frozen_spec": {
            "guard_inputs": list(GUARD_INPUTS),
            "presence_rule": ("a field is present iff the key exists and its value is not None; "
                              "0.0 is a value -- a zero is a measurement, not a missing number"),
            "domain_rule": ("every %s*%s in results/state_tilt except the %s byte mirrors: the "
                            "mirrors are the same face twice"
                            % (DOMAIN_PREFIX, DOMAIN_SUFFIX, LATEST_SUFFIX)),
            "complete_rule": "a record is guard-runnable iff it carries all four inputs",
            "join_rule": ("a collection is joined against the canonical row collection of the "
                          "face that published the rows; a shared number must match to %r, "
                          "so presence alone cannot pass" % JOIN_TOL),
            "verdict_rule": ("disagreement outranks incompleteness: two faces publishing "
                             "different values for one row is a stronger finding than a face "
                             "that publishes no value at all"),
            "tolerance": JOIN_TOL,
            "verdict_vocabulary": list(VERDICT_VOCAB),
        },
        "summary": summary,
        "guard_complete_collections": complete_cols,
        "self_excluded_faces": (["%s*%s" % (pre, DOMAIN_SUFFIX) for pre in SELF_EXCLUDED_PREFIXES]
                                + ["*%s" % LATEST_SUFFIX]),
        "faces": faces,
        "verdict": verdict,
        "verdict_reason": why,
    }
    if save:
        _write(out, outdir)
    return out


def _write(face, outdir, tag=""):
    if not os.path.isdir(outdir):
        os.makedirs(outdir)
    text = json.dumps(face, ensure_ascii=False, indent=1, sort_keys=True)
    path = os.path.join(outdir, "BANDFIELDS-%s%s.json" % (face.get("evidence_cutoff"), tag))
    with io.open(path, "w", encoding="utf-8", newline="\n") as fh:
        fh.write(text + "\n")
    with io.open(os.path.join(outdir, LATEST), "w", encoding="utf-8", newline="\n") as fh:
        fh.write(text + "\n")
    return path


def verify(outdir=None, tag=""):
    outdir = outdir or OUTDIR
    path = os.path.join(outdir, "BANDFIELDS-%s%s.json" % (CUTOFF, tag))
    if not os.path.exists(path):
        return ["no published face at %s" % path]
    with io.open(path, encoding="utf-8") as fh:
        got = json.load(fh)
    published = got.get("source_faces") or []
    fresh = run(save=False, only=published)
    problems = []
    for key in sorted(set(got) | set(fresh)):
        if key == "generated":
            continue
        if got.get(key) != fresh.get(key):
            problems.append("%s does not re-derive" % key)
    now = set(domain_faces(outdir))
    added = sorted(now - set(published))
    dropped = sorted(set(published) - now)
    if added or dropped:
        # not a defect of this face: the domain grows as the machine keeps publishing. A count
        # that silently moved would not be re-derivable, so the inventory is part of the record.
        print("inventory drifted since publication: +%d -%d (re-run to republish; the face's "
              "counts are those of the published inventory)" % (len(added), len(dropped)))
        for name in added[:6]:
            print("  + %s" % name)
        for name in dropped[:6]:
            print("  - %s" % name)
    return problems


# ------------------------------------------------------------------ selftest
def _leg(ok, name, detail=None):
    return {"leg": name, "ok": bool(ok), "detail": detail}


def _rec(index=0, b=-0.5, lo=-0.3, hi=0.3, p95=2.0, **extra):
    rec = {"index": index, "b": b, "band_lo": lo, "band_hi": hi, "own_p95": p95}
    rec.update(extra)
    return rec


def selftest():
    legs = []

    # --- presence: None is absent, a zero is a value
    legs.append(_leg(present({"own_p95": None}, "own_p95") is False,
                     "a key whose value is None is ABSENT"))
    legs.append(_leg(present({"b": 0.0}, "b") is True,
                     "0.0 is a value, not a missing number"))
    legs.append(_leg(present({"b": False}, "b") is True,
                     "a False flag is still present (only None is absent)"))
    legs.append(_leg(present({}, "b") is False, "an absent key is absent"))

    # --- classify counts completeness on all four inputs
    c = classify([_rec(), _rec(index=1, p95=None), _rec(index=2)], "x")
    legs.append(_leg(c["n_records"] == 3 and c["n_complete"] == 2,
                     "a record missing one input is not guard-runnable",
                     "%r/%r" % (c["n_complete"], c["n_records"])))
    legs.append(_leg(c["fields"]["own_p95"]["present"] == 2
                     and c["fields"]["own_p95"]["absent"] == 1,
                     "per-field present/absent counts add up"))
    legs.append(_leg(c["missing_fields"] == [] and c["partial_fields"] == ["own_p95"],
                     "a partly-populated field is named as PARTIAL, not missing",
                     str(c["partial_fields"])))
    c0 = classify([{"index": 0, "b": -0.5}], "y")
    legs.append(_leg(c0["missing_fields"] == ["band_lo", "band_hi", "own_p95"]
                     and c0["guard_runnable"] is False,
                     "a collection with only b names the three fields it lacks"))
    legs.append(_leg(classify([], "z")["guard_runnable"] is False,
                     "an empty collection is not runnable"))

    # --- verdict-shaped fields are NAMED, never re-decided
    c2 = classify([_rec(verdict_wide=True, actual_moved=False)], "v")
    legs.append(_leg(c2["verdict_fields"] == ["actual_moved", "verdict_wide"],
                     "verdict-shaped fields are enumerated from the records",
                     str(c2["verdict_fields"])))

    # --- collections_of walks nested structures and reports the path
    doc = {"a": {"rows": [_rec()]}, "transfer": {"self:60": {"pairs": [{"donor": "a"}]}},
           "scalars": [1, 2, 3], "empty": []}
    cols = collections_of(doc)
    paths = sorted(p for p, _r in cols)
    legs.append(_leg(paths == ["/a/rows", "/transfer/self:60/pairs"],
                     "nested row lists are found at any depth, with their path", str(paths)))
    legs.append(_leg(all(not p.startswith("/scalars") and not p.startswith("/empty")
                         for p in paths),
                     "a list of scalars is not a record collection"))

    # --- face scan separates runnable collections from verdicts without inputs
    scan = scan_face({"rows": [_rec(), _rec(index=1)],
                      "summary": {"moves": [{"index": 0, "actual_moved": True}]}})
    legs.append(_leg(scan["guard_runnable_collections"] == ["/rows"],
                     "the row collection is guard-runnable", str(scan["guard_runnable_collections"])))
    legs.append(_leg(scan["collections_with_verdict_but_no_inputs"] == ["/summary/moves"],
                     "a verdict list without the inputs is named", str(scan)))

    # --- `b` carries two meanings in this family; a buffer grid is not a half-built row
    scan_b = scan_face({"curves": [{"b": 0.05, "actual": 2, "predicted": 2, "tp": 2}],
                        "rows": [_rec()]})
    legs.append(_leg(scan_b["b_without_a_band"] == ["/curves"],
                     "a collection with b and no band is the buffer grid, named",
                     str(scan_b["b_without_a_band"])))
    legs.append(_leg(scan_b["collections_with_verdict_but_no_inputs"] == [],
                     "the buffer grid is not filed as a verdict without inputs",
                     str(scan_b["collections_with_verdict_but_no_inputs"])))

    # --- canonical map: unique index joins on index, duplicates force the composite key
    canon = canon_map({"rows": [_rec(index=0), _rec(index=1)]})
    legs.append(_leg(canon["basis"] == "index" and canon["records"] == 2,
                     "unique indices are a usable key", str(canon["basis"])))
    canon_dup = canon_map({"rows": [_rec(index=0, leg="self"), _rec(index=0, leg="cross")]})
    legs.append(_leg(canon_dup["basis"] == "composite"
                     and len(canon_dup["map"]) == 2,
                     "a duplicated index falls back to (index, leg, base, cell)",
                     str(sorted(canon_dup["map"]))))

    # --- join: equal numbers agree, different numbers disagree, and the diff is published
    ok_join = join_collection([_rec(index=0)], canon)
    legs.append(_leg(ok_join["cells_compared"] == 4 and ok_join["agree"] == 4
                     and ok_join["disagree"] == 0,
                     "an identical row agrees on all four cells", str(ok_join)))
    bad_join = join_collection([_rec(index=0, p95=2.0161)], canon)
    legs.append(_leg(bad_join["disagree"] == 1 and bad_join["disagreeing"][0]["field"] == "own_p95",
                     "a different own_p95 is a disagreement, named with the field"))
    legs.append(_leg(abs(bad_join["max_abs_diff"] - 0.0161) < 1e-12,
                     "the disagreement publishes its magnitude", str(bad_join["max_abs_diff"])))
    legs.append(_leg(join_collection([{"b": -0.5}], canon)["unjoined"] == 1,
                     "a record with no index is counted unjoined, never dropped"))
    legs.append(_leg(join_collection([_rec(index=99)], canon)["unjoined"] == 1,
                     "an index the canonical face does not carry is unjoined"))
    legs.append(_leg(join_collection([_rec(index=0)], {"map": {}, "basis": "none"})
                     .get("reason") is not None,
                     "no canonical rows is disclosed, not a silent zero"))

    # --- verdict rules, and their precedence
    s0 = {"guard_columns": 0, "value_disagreements": 0,
          "verdict_collections_without_inputs": 0, "cells_compared": 0,
          "max_abs_diff": None, "records_with_verdict_but_no_inputs": 0,
          "records_guard_runnable": 0, "guard_complete_collections": 0,
          "guard_complete_on_measured_rows_only": 0}
    legs.append(_leg(verdict_of(s0)[0] == "no_guard_bearing_record",
                     "nothing guarded is its own verdict", verdict_of(s0)[0]))
    s1 = dict(s0, guard_columns=3, cells_compared=12, value_disagreements=1, max_abs_diff=0.0161)
    legs.append(_leg(verdict_of(s1)[0] == "guard_inputs_disagree_across_faces",
                     "value disagreement outranks incompleteness"))
    s2 = dict(s0, guard_columns=3, cells_compared=12, verdict_collections_without_inputs=2,
              records_with_verdict_but_no_inputs=5, records_guard_runnable=10,
              guard_complete_collections=4, guard_complete_on_measured_rows_only=3)
    legs.append(_leg(verdict_of(s2)[0] == "guard_inputs_are_face_local",
                     "a verdict without inputs makes the screen face-local"))
    s3 = dict(s0, guard_columns=3, cells_compared=12, records_guard_runnable=10,
              guard_complete_collections=2)
    legs.append(_leg(verdict_of(s3)[0] == "guard_inputs_are_published_where_the_screen_runs",
                     "complete inputs with agreeing values is the green verdict"))

    # --- the domain excludes the byte mirrors, or every face is counted twice
    import tempfile
    import shutil
    tmp = tempfile.mkdtemp(prefix="e270_")
    try:
        for name in ("BANDFOO-2026-10-29.json", "bandfoo_latest.json", "OTHER.json",
                     "BANDFIELDS-2026-10-29.json"):
            with io.open(os.path.join(tmp, name), "w", encoding="utf-8") as fh:
                fh.write(u"{\"rows\": []}")
        names = domain_faces(tmp)
        legs.append(_leg(names == ["BANDFOO-2026-10-29.json"],
                         "the domain is BAND* dated faces only -- no mirror, no other family, "
                         "and not this study's own face", str(names)))
    finally:
        shutil.rmtree(tmp, ignore_errors=True)

    ok = all(l["ok"] for l in legs)
    print("selftest %d/%d %s" % (sum(1 for l in legs if l["ok"]), len(legs), "OK" if ok else "FAIL"))
    for l in legs:
        if not l["ok"]:
            print("  FAIL", l["leg"], l["detail"])
    return 0 if ok else 1


def main(argv=None):
    argv = list(sys.argv[1:] if argv is None else argv)
    cmd = argv[0] if argv else "run"
    if cmd == "selftest":
        return selftest()
    if cmd == "verify":
        problems = verify()
        if problems:
            print("verify %d problem(s)" % len(problems))
            for p in problems:
                print("  -", p)
            return 1
        print("verify 0 problems")
        return 0
    if cmd == "run":
        face = run()
        s = face["summary"]
        print("%s: %s" % (face["verdict"], face["verdict_reason"]))
        print("  faces %d / collections %d; guard columns %d (runnable %d), records runnable %d"
              % (s["faces_scanned"], s["collections_scanned"], s["guard_columns"],
                 s["guard_runnable_columns"], s["records_guard_runnable"]))
        print("  verdict collections without inputs %d (%d records)"
              % (s["verdict_collections_without_inputs"],
                 s["records_with_verdict_but_no_inputs"]))
        print("  join: %d record(s) joined / %d unjoined, %d cell(s) compared, %d agree / %d "
              "disagree, max |diff| %r (canonical %s %s)"
              % (s["joined_records"], s["unjoined_records"], s["cells_compared"],
                 s["value_agreements"], s["value_disagreements"], s["max_abs_diff"],
                 s["canonical_path"], s["canonical_basis"]))
        for entry in face["faces"]:
            sc = entry["scan"]
            print("  %-30s cols %2d runnable %d | verdict-no-inputs %d | %s"
                  % (entry["face"], len(sc["collections"]),
                     sc["n_records_guard_runnable"],
                     sc["n_records_with_verdict_but_no_inputs"],
                     ",".join(sc["guard_runnable_collections"]) or "-"))
        return 0
    print("usage: e270_guard_field_audit.py [run|verify|selftest]")
    return 2


if __name__ == "__main__":
    sys.exit(main())