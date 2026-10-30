"""E273 -- is a published THRESHOLD enough to re-run the guard, or does it need the triple?

E270 measured the limit of this family: the guard consumes four numbers per row
(`b`, `band_lo`, `band_hi`, `own_p95`) and only 4 of 17 published band collections carry all
four, so 27 verdict-bearing collections (584 records) publish a judgement a reader cannot
re-decide from the page.

But every rule in this family is a comparison of a MULTIPLIER against a threshold:

    t_max_end = |b| / max(|lo|, |hi|)        (E264/E265 form -- the exact transfer threshold)
    t_side    = |b| / |the band end on the row's own side|

and `outside at m` is `m < t`.  So a face that publishes the threshold plus the p95 it is
compared against does not need the band at all -- the triple is redundant arithmetic.  The
question this face answers is not whether that is plausible but whether it is EXACT, and how far
the substitution reaches:

  1. re-derive both thresholds from the triple on the 36 comparisons that publish BOTH spellings
     and publish the residual (a non-zero residual means the published threshold is not the
     published band's threshold, and nothing downstream can be trusted);
  2. re-run the three published screens (S1 single / S2 guarded / S3 bracket) from thresholds
     alone and compare with the faces' own predicted columns -- 36/36 or the substitute fails;
  3. price the AMBIGUITY a threshold-only face inherits: 18 rows carry two different published
     thresholds, so a reader who is given "the threshold" without the face's rule label can land
     on two different verdicts;
  4. census the family for collections that become runnable under the substitute but were not
     guard-complete in E270, and say which faces a reader can now screen without the triple.

Reads BANDSCREEN (both spellings) + BANDMARGIN/BANDPOOLED (threshold-only spellings) + E270's
inventory.  Writes results/state_tilt/BANDTHRESHGUARD-2026-10-29.json.  No draws, no engine.
"""
from __future__ import print_function

import glob
import io
import json
import os
import shutil
import sys
import tempfile
import time

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
OUTDIR = os.path.join(ROOT, "results", "state_tilt")

STUDY = "E273_threshold_guard_substitution"
TITLE = "is a published threshold enough to re-run the guard, or does it need the triple?"
CUTOFF = "2026-10-29"
FACE = "BANDTHRESHGUARD-%s.json" % CUTOFF
LATEST = "bandthreshguard_latest.json"

DUAL_FACE = "BANDSCREEN-%s.json" % CUTOFF     # publishes the triple AND both thresholds
INVENTORY_FACE = "BANDFIELDS-%s.json" % CUTOFF  # E270's field census
THRESHOLD_COLS = ("t_max_end", "t_side")
P95_COLS = ("own_p95", "donor_p95")
TRIPLE_COLS = ("b", "band_lo", "band_hi")
PUBLISHED_RULES = ("predicted_single", "predicted_guarded", "predicted_bracket")
TOL = 1e-12

DOMAIN_PREFIX = "BAND"
LATEST_SUFFIX = "_latest.json"
SELF_EXCLUDED_PREFIXES = ("BANDTHRESHGUARD",)

NO_BILL = ("measurement only: published faces are re-read and re-derived; no shuffle stream is "
           "drawn, no band is rebuilt, no row verdict outside this face moves")


# ---------------------------------------------------------------- arithmetic (the frozen rules)

def t_max_end(b, lo, hi):
    """|b| / max(|lo|,|hi|) -- the exact transfer threshold (E264/E265 form)."""
    den = max(abs(lo), abs(hi))
    if den == 0:
        return None                      # a zero-width band has no threshold: publish, never guess
    return abs(b) / den


def t_side_threshold(b, lo, hi, side):
    """|b| / |the band end on the row's own side| (S3's published form)."""
    edge = lo if (side or "lo") == "lo" else hi
    if edge == 0:
        return None
    return abs(b) / abs(edge)


def outside_at_max_end(b, lo, hi, m):
    """The literal band test: outside at multiplier m iff |b| > max(|lo|,|hi|)*m."""
    return abs(b) > max(abs(lo), abs(hi)) * m


def outside_at_side(b, lo, hi, side, m):
    """The side form actually published by e262.judge: only the row's own side end."""
    edge = lo if (side or "lo") == "lo" else hi
    return abs(b) > abs(edge) * m


def rule_single(donor_p95, t):
    return donor_p95 > t


def rule_guarded(donor_p95, own_p95, t):
    return (donor_p95 > t) and (own_p95 < t)


def rule_bracket(donor_p95, own_p95, t):
    return min(donor_p95, own_p95) < t < max(donor_p95, own_p95)


# ---------------------------------------------------------------- reading

def _load(name):
    path = os.path.join(OUTDIR, name)
    with io.open(path, encoding="utf-8") as fh:
        return json.load(fh)


def _domain_faces(exclude_prefixes):
    faces = []
    for path in sorted(glob.glob(os.path.join(OUTDIR, DOMAIN_PREFIX + "*"))):
        base = os.path.basename(path)
        if not base.endswith(".json") or base.endswith(LATEST_SUFFIX):
            continue
        if any(base.startswith(p) for p in exclude_prefixes):
            continue
        faces.append(base)
    return faces


def _collections(node, path=""):
    """Yield (path, rows, union_of_keys) for every list-of-dicts collection."""
    if isinstance(node, list):
        if node and all(isinstance(x, dict) for x in node):
            keys = set()
            for x in node:
                keys |= set(x.keys())
            yield path or "/", node, keys
            return
        for item in node:
            for hit in _collections(item, path):
                yield hit
        return
    if isinstance(node, dict):
        for key, val in node.items():
            for hit in _collections(val, path + "/" + str(key)):
                yield hit


# ---------------------------------------------------------------- the three measurements

def reproduce():
    """Re-derive both thresholds from the triple and re-run the three rules from thresholds only."""
    sink = _load(DUAL_FACE)
    rows = sink["comparison_rows"]

    d_max = 0.0
    d_side = 0.0
    t_null = 0
    literal_max_agree = 0
    literal_side_agree = 0
    own_verdict_agree_max = 0
    own_verdict_agree_side = 0
    t_side_ne_t_max = 0
    own_verdict_ambiguous = 0
    guarded_ambiguous = 0
    rule_agree = {name: 0 for name in PUBLISHED_RULES}
    rule_total = {name: 0 for name in PUBLISHED_RULES}
    ambiguous_rows = []
    per_rule_diff = []

    for row in rows:
        b, lo, hi = row.get("b"), row.get("band_lo"), row.get("band_hi")
        side = row.get("side") or "lo"
        own = row.get("own_p95")
        donor = row.get("donor_p95")
        tm_c = t_max_end(b, lo, hi)
        ts_c = t_side_threshold(b, lo, hi, side)
        if tm_c is None or ts_c is None:
            t_null += 1
            continue
        d_max = max(d_max, abs(tm_c - row["t_max_end"]))
        d_side = max(d_side, abs(ts_c - row["t_side"]))
        if outside_at_max_end(b, lo, hi, own) == (own < row["t_max_end"]):
            literal_max_agree += 1
        if outside_at_side(b, lo, hi, side, own) == (own < row["t_side"]):
            literal_side_agree += 1
        if row.get("own_verdict") == ("outside" if own < row["t_max_end"] else "inside"):
            own_verdict_agree_max += 1
        if row.get("own_verdict") == ("outside" if own < row["t_side"] else "inside"):
            own_verdict_agree_side += 1
        if abs(row["t_side"] - row["t_max_end"]) > TOL:
            t_side_ne_t_max += 1
        own_amb = (own < row["t_side"]) != (own < row["t_max_end"])
        grd_amb = (rule_guarded(donor, own, row["t_side"])
                   != rule_guarded(donor, own, row["t_max_end"]))
        if own_amb:
            own_verdict_ambiguous += 1
        if grd_amb:
            guarded_ambiguous += 1
        if own_amb or grd_amb:
            ambiguous_rows.append({"arm": row.get("arm"), "cell": row.get("cell"),
                                   "row": row.get("row"), "index": row.get("index"),
                                   "donor": row.get("donor"),
                                   "own_p95": own, "donor_p95": donor,
                                   "t_side": row["t_side"], "t_max_end": row["t_max_end"],
                                   "own_verdict_side_form": "outside" if own < row["t_side"] else "inside",
                                   "own_verdict_maxend_form": "outside" if own < row["t_max_end"] else "inside",
                                   "guarded_flips": grd_amb})
        # the three published screens, re-run from thresholds alone
        preds = {
            "predicted_single": rule_single(donor, row["t_max_end"]),
            "predicted_guarded": rule_guarded(donor, own, row["t_max_end"]),
            "predicted_bracket": rule_bracket(donor, own, row["t_side"]),
        }
        for name, pred in preds.items():
            if name in row:
                rule_total[name] += 1
                if bool(row[name]) == bool(pred):
                    rule_agree[name] += 1
                elif len(per_rule_diff) < 8:
                    per_rule_diff.append({"rule": name, "index": row.get("index"),
                                          "published": bool(row[name]), "threshold_only": bool(pred)})

    return {
        "comparisons": len(rows),
        "thresholds_undefined": t_null,
        "max_abs_diff_t_max_end": d_max,
        "max_abs_diff_t_side": d_side,
        "literal_band_test_agrees_maxend": literal_max_agree,
        "literal_band_test_agrees_side": literal_side_agree,
        "published_own_verdict_agrees_maxend": own_verdict_agree_max,
        "published_own_verdict_agrees_side": own_verdict_agree_side,
        "rows_with_two_different_thresholds": t_side_ne_t_max,
        "rows_own_verdict_ambiguous": own_verdict_ambiguous,
        "rows_guarded_screen_ambiguous": guarded_ambiguous,
        "rules_rerun_from_thresholds": {k: {"agree": rule_agree[k], "of": rule_total[k]}
                                        for k in PUBLISHED_RULES},
        "rule_disagreements": per_rule_diff,
        "ambiguous_rows": ambiguous_rows,
    }


def census():
    """Which collections can re-run the guard from a threshold, and which ones E270 could not."""
    inventory = _load(INVENTORY_FACE)
    guard_complete = set()
    for entry in inventory.get("faces", []):
        for coll in entry.get("scan", {}).get("collections", []):
            if coll.get("n_complete"):
                guard_complete.add((entry["face"], coll["path"]))

    seen = []
    for face in _domain_faces(SELF_EXCLUDED_PREFIXES):
        doc = _load(face)
        for path, rows, keys in _collections(doc):
            thresholds = [c for c in THRESHOLD_COLS if c in keys]
            p95s = [c for c in P95_COLS if c in keys]
            if not thresholds or not p95s:
                continue
            # a pair screen additionally needs the counterpart p95; a row screen needs own_p95
            screen = "pair" if len(p95s) == 2 else "row"
            complete_from_threshold = screen == "pair" or "own_p95" in keys
            if not complete_from_threshold:
                continue
            seen.append({
                "face": face,
                "path": path,
                "records": len(rows),
                "thresholds": thresholds,
                "p95": p95s,
                "screen": screen,
                "exact_form": "t_max_end" in thresholds or screen == "row",
                "guard_complete_in_e270": (face, path) in guard_complete,
            })
    newly = [r for r in seen if not r["guard_complete_in_e270"]]
    return {
        "collections_scanned": len(seen),
        "collections_threshold_runnable": len(seen),
        "collections_already_guard_complete": len([r for r in seen if r["guard_complete_in_e270"]]),
        "collections_newly_runnable": len(newly),
        "records_newly_runnable": sum(r["records"] for r in newly),
        "faces_newly_runnable": sorted(set(r["face"] for r in newly)),
        "newly_runnable": newly,
        "threshold_runnable": seen,
        "e270_guard_complete_collections": inventory["summary"]["guard_complete_collections"],
    }


# ---------------------------------------------------------------- verdict

def _verdict(rep, cen):
    """Frozen decision rule -- derived from the measurements, never hand-typed."""
    rules_ok = all(v["of"] and v["agree"] == v["of"]
                   for v in rep["rules_rerun_from_thresholds"].values())
    residual_ok = (rep["max_abs_diff_t_max_end"] <= TOL and rep["max_abs_diff_t_side"] <= TOL)
    if not residual_ok:
        return ("published_threshold_is_not_the_published_bands_threshold",
                "the threshold does not re-derive from the triple (max |diff| %r / %r), so no "
                "threshold-only face can be screened until the spelling is reconciled"
                % (rep["max_abs_diff_t_max_end"], rep["max_abs_diff_t_side"]))
    if not rules_ok:
        return ("threshold_is_not_a_substitute",
                "the three published screens are not reproducible from the threshold columns alone")
    if rep["rows_own_verdict_ambiguous"]:
        return ("threshold_substitutes_for_the_triple_only_alongside_its_rule",
                "all %d comparisons re-run exactly from threshold columns alone (0 triple columns "
                "consulted; the threshold re-derives from the band to %r/%r), but %d rows carry two "
                "different published thresholds and %d of those read a DIFFERENT verdict on them, "
                "so a threshold without the face's rule label is ambiguous on those rows"
                % (rep["comparisons"], rep["max_abs_diff_t_max_end"],
                   rep["max_abs_diff_t_side"], rep["rows_with_two_different_thresholds"],
                   rep["rows_own_verdict_ambiguous"]))
    return ("threshold_substitutes_for_the_triple",
            "all %d comparisons re-run exactly from threshold columns alone and no row carries two "
            "different verdicts under the two published forms" % rep["comparisons"])


# ---------------------------------------------------------------- output

def build():
    rep = reproduce()
    cen = census()
    verdict, reason = _verdict(rep, cen)
    face = {
        "study": STUDY,
        "title": TITLE,
        "evidence_cutoff": CUTOFF,
        "generated": time.strftime("%Y-%m-%dT%H:%M:%S"),
        "source_face": DUAL_FACE,
        "inventory_face": INVENTORY_FACE,
        "frozen_spec": {
            "population": "the %d comparisons BANDSCREEN publishes with BOTH spellings "
                          "(the triple and the two thresholds)" % rep["comparisons"],
            "t_max_end": "|b| / max(|lo|,|hi|)  (E264/E265 form) -- exact: outside(m) <=> m < t",
            "t_side": "|b| / |the band end on the row's own side|  (S3's published form)",
            "substitute": "a face is threshold-runnable iff it publishes a threshold column plus "
                          "own_p95 (row screen) or own_p95 AND donor_p95 (pair screen)",
            "rules": {"S1_single": "donor_p95 > t_max_end",
                      "S2_guarded": "donor_p95 > t_max_end and own_p95 < t_max_end",
                      "S3_bracket": "min(donor_p95,own_p95) < t_side < max(donor_p95,own_p95)"},
            "comparison": "the three rules are re-run from threshold columns only and compared with "
                          "the published predicted_* columns on the same rows",
            "no_bill": NO_BILL,
        },
        "rederivation": {k: rep[k] for k in (
            "comparisons", "thresholds_undefined", "max_abs_diff_t_max_end",
            "max_abs_diff_t_side", "literal_band_test_agrees_maxend",
            "literal_band_test_agrees_side", "published_own_verdict_agrees_maxend",
            "published_own_verdict_agrees_side", "rows_with_two_different_thresholds",
            "rows_own_verdict_ambiguous", "rows_guarded_screen_ambiguous",
            "rules_rerun_from_thresholds", "rule_disagreements")},
        "ambiguous_rows": rep["ambiguous_rows"],
        "census": cen,
        "summary": {
            "comparisons": rep["comparisons"],
            "triple_columns_consulted_to_rerun": 0,
            "max_abs_diff_t_max_end": rep["max_abs_diff_t_max_end"],
            "max_abs_diff_t_side": rep["max_abs_diff_t_side"],
            "rules_reproduced_exactly": all(v["of"] and v["agree"] == v["of"]
                                            for v in rep["rules_rerun_from_thresholds"].values()),
            "rows_with_two_different_thresholds": rep["rows_with_two_different_thresholds"],
            "rows_own_verdict_ambiguous": rep["rows_own_verdict_ambiguous"],
            "rows_guarded_screen_ambiguous": rep["rows_guarded_screen_ambiguous"],
            "ambiguous_share": (float(rep["rows_own_verdict_ambiguous"]) / rep["comparisons"]
                                if rep["comparisons"] else None),
            "collections_threshold_runnable": cen["collections_threshold_runnable"],
            "collections_newly_runnable": cen["collections_newly_runnable"],
            "records_newly_runnable": cen["records_newly_runnable"],
            "faces_newly_runnable": cen["faces_newly_runnable"],
        },
        "verdict": verdict,
        "verdict_reason": reason,
        "no_bill": NO_BILL,
    }
    return face


def run():
    face = build()
    path = os.path.join(OUTDIR, FACE)
    with io.open(path, "w", encoding="utf-8", newline="\n") as fh:
        json.dump(face, fh, ensure_ascii=False, indent=1, sort_keys=True)
        fh.write(u"\n")
    latest = os.path.join(OUTDIR, LATEST)
    shutil.copyfile(path, latest)
    return face


def verify():
    """Re-derive every published number from the sources; never re-read its own summary."""
    problems = []
    path = os.path.join(OUTDIR, FACE)
    if not os.path.exists(path):
        return ["face missing: %s" % FACE]
    with io.open(path, encoding="utf-8") as fh:
        face = json.load(fh)
    rep = reproduce()
    cen = census()
    red = face.get("rederivation", {})
    for key in ("comparisons", "max_abs_diff_t_max_end", "max_abs_diff_t_side",
                "rows_with_two_different_thresholds", "rows_own_verdict_ambiguous",
                "rows_guarded_screen_ambiguous", "literal_band_test_agrees_maxend"):
        if red.get(key) != rep[key]:
            problems.append("rederivation.%s published %r, re-derived %r" % (key, red.get(key), rep[key]))
    pub_rules = red.get("rules_rerun_from_thresholds") or {}
    for name, val in rep["rules_rerun_from_thresholds"].items():
        if pub_rules.get(name) != val:
            problems.append("rule %s published %r, re-derived %r" % (name, pub_rules.get(name), val))
    summ = face.get("summary", {})
    if summ.get("collections_newly_runnable") != cen["collections_newly_runnable"]:
        problems.append("census.collections_newly_runnable published %r, re-derived %r"
                        % (summ.get("collections_newly_runnable"), cen["collections_newly_runnable"]))
    if summ.get("records_newly_runnable") != cen["records_newly_runnable"]:
        problems.append("census.records_newly_runnable published %r, re-derived %r"
                        % (summ.get("records_newly_runnable"), cen["records_newly_runnable"]))
    verdict, reason = _verdict(rep, cen)
    if face.get("verdict") != verdict:
        problems.append("verdict published %r, rule gives %r" % (face.get("verdict"), verdict))
    if face.get("verdict_reason") != reason:
        problems.append("verdict_reason does not match the rule's sentence")
    if not face.get("no_bill"):
        problems.append("no_bill missing")
    return problems


# ---------------------------------------------------------------- selftest

def _row(b, lo, hi, side, own, donor, **kw):
    row = {"b": b, "band_lo": lo, "band_hi": hi, "side": side,
           "own_p95": own, "donor_p95": donor,
           "t_max_end": t_max_end(b, lo, hi) if t_max_end(b, lo, hi) is not None else 0.0,
           "t_side": t_side_threshold(b, lo, hi, side) if t_side_threshold(b, lo, hi, side) is not None else 0.0,
           "arm": "self:200", "cell": "c", "row": "r", "index": 1, "donor": "d",
           "own_verdict": "outside" if (t_max_end(b, lo, hi) or 0) > own else "inside",
           "predicted_single": bool(donor > (t_max_end(b, lo, hi) or 0)),
           "predicted_guarded": bool(donor > (t_max_end(b, lo, hi) or 0)
                                     and own < (t_max_end(b, lo, hi) or 0)),
           "predicted_bracket": bool(min(donor, own) < (t_side_threshold(b, lo, hi, side) or 0)
                                     < max(donor, own))}
    row.update(kw)
    return row


def selftest():
    legs = []

    def leg(name, cond):
        legs.append((name, bool(cond)))

    # 1-3: the threshold is the band test, both directions, strict inequality
    leg("L1 t_max_end is |b|/max edge",
        abs(t_max_end(-2.0, -1.0, 4.0) - 0.5) < 1e-15)
    t = t_max_end(-2.0, -1.0, 4.0)
    leg("L2 below the threshold is outside, above is inside",
        outside_at_max_end(-2.0, -1.0, 4.0, t * 0.5) and not outside_at_max_end(-2.0, -1.0, 4.0, t * 2))
    leg("L3 equality is not clearance (strict >)",
        not outside_at_max_end(-2.0, -1.0, 4.0, t))
    leg("L4 zero-width band has no threshold (None, never a division)",
        t_max_end(1.0, 0.0, 0.0) is None)

    # 5-6: the side form uses one edge only, so the two thresholds differ when the side is not the max
    leg("L5 side threshold divides by the own-side edge only",
        abs(t_side_threshold(-2.0, -1.0, 4.0, "lo") - 2.0) < 1e-15)
    leg("L6 the two thresholds differ when the own side is not the widest edge",
        abs(t_side_threshold(-2.0, -1.0, 4.0, "lo") - t_max_end(-2.0, -1.0, 4.0)) > 1e-9)
    leg("L7 they coincide when the own side IS the widest edge",
        abs(t_side_threshold(-2.0, -4.0, 1.0, "lo") - t_max_end(-2.0, -4.0, 1.0)) < 1e-15)

    # 8-10: the three published rules are functions of the thresholds alone
    leg("L8 single = donor over the threshold", rule_single(3.0, 2.0) and not rule_single(1.0, 2.0))
    leg("L9 guarded needs the row inside and the donor outside",
        rule_guarded(3.0, 1.0, 2.0) and not rule_guarded(3.0, 2.5, 2.0) and not rule_guarded(1.0, 1.0, 2.0))
    leg("L10 bracket is strict on both ends",
        rule_bracket(3.0, 1.0, 2.0) and not rule_bracket(3.0, 2.0, 2.0) and not rule_bracket(1.0, 1.0, 2.0))

    # 11-13: ambiguity is a property of the thresholds, counted on a fixture
    hostile = _row(-2.0, -1.0, 4.0, "lo", own=1.0, donor=3.0)
    leg("L11 the fixture really carries two different thresholds",
        abs(hostile["t_side"] - hostile["t_max_end"]) > 1e-9)
    leg("L12 the fixture's own verdict differs between the two forms",
        (hostile["own_p95"] < hostile["t_side"]) != (hostile["own_p95"] < hostile["t_max_end"]))
    friendly = _row(-2.0, -4.0, 1.0, "lo", own=1.0, donor=3.0)
    leg("L13 a row whose side is the widest edge is unambiguous",
        abs(friendly["t_side"] - friendly["t_max_end"]) < 1e-15)

    # 14-16: reproduce() measured against a fixture directory
    tmp = tempfile.mkdtemp(prefix="e273_selftest_")
    try:
        global OUTDIR
        keep = OUTDIR
        OUTDIR = tmp
        rows = [_row(-2.0, -1.0, 4.0, "lo", own=1.0, donor=3.0, index=1),
                _row(-2.0, -4.0, 1.0, "lo", own=3.0, donor=1.0, index=2)]
        with io.open(os.path.join(tmp, DUAL_FACE), "w", encoding="utf-8") as fh:
            json.dump({"comparison_rows": rows}, fh)
        rep = reproduce()
        leg("L14 fixture round-trips: thresholds re-derive with zero residual",
            rep["max_abs_diff_t_max_end"] <= TOL and rep["max_abs_diff_t_side"] <= TOL)
        leg("L15 fixture counts exactly one ambiguous row",
            rep["rows_own_verdict_ambiguous"] == 1)
        leg("L16 fixture reproduces all three published rules",
            all(v["agree"] == v["of"] for v in rep["rules_rerun_from_thresholds"].values()))
        # census: a threshold collection counts, a p95-only collection does not
        with io.open(os.path.join(tmp, "BANDX-2026-10-29.json"), "w", encoding="utf-8") as fh:
            json.dump({"rows": [{"t_max_end": 1.0, "own_p95": 0.5, "donor_p95": 2.0}],
                       "other": [{"own_p95": 0.5}]}, fh)
        with io.open(os.path.join(tmp, INVENTORY_FACE), "w", encoding="utf-8") as fh:
            json.dump({"summary": {"guard_complete_collections": 0}, "faces": []}, fh)
        cen = census()
        paths = sorted(r["path"] for r in cen["threshold_runnable"])
        leg("L17 census takes every threshold collection and drops the p95-only one",
            paths == ["/comparison_rows", "/rows"] and "/other" not in paths)
        leg("L18 collections with no E270 entry are reported as NEW with their record count",
            cen["collections_newly_runnable"] == 2 and cen["records_newly_runnable"] == 3
            and sorted(cen["faces_newly_runnable"]) == ["BANDSCREEN-2026-10-29.json",
                                                        "BANDX-2026-10-29.json"])
        OUTDIR = keep
    finally:
        shutil.rmtree(tmp, ignore_errors=True)

    # 19: verify() refuses a face that was written before its last edit (run/verify pair)
    tmp2 = tempfile.mkdtemp(prefix="e273_verify_")
    try:
        keep = OUTDIR
        OUTDIR = tmp2
        with io.open(os.path.join(tmp2, DUAL_FACE), "w", encoding="utf-8") as fh:
            json.dump({"comparison_rows": [_row(-2.0, -1.0, 4.0, "lo", own=1.0, donor=3.0)]}, fh)
        with io.open(os.path.join(tmp2, INVENTORY_FACE), "w", encoding="utf-8") as fh:
            json.dump({"summary": {"guard_complete_collections": 0}, "faces": []}, fh)
        face = build()
        with io.open(os.path.join(tmp2, FACE), "w", encoding="utf-8") as fh:
            json.dump(face, fh)
        leg("L19 verify is clean on a face built by build()", verify() == [])
        face["summary"]["comparisons"] = 999
        with io.open(os.path.join(tmp2, FACE), "w", encoding="utf-8") as fh:
            json.dump(face, fh)
        # comparisons is re-derived inside rederivation, so a doctored summary alone is not caught;
        # doctoring the rederivation block IS (this pins which side verify trusts)
        face["rederivation"]["comparisons"] = 999
        with io.open(os.path.join(tmp2, FACE), "w", encoding="utf-8") as fh:
            json.dump(face, fh)
        leg("L20 verify catches a doctored rederivation", verify() != [])
        OUTDIR = keep
    finally:
        shutil.rmtree(tmp2, ignore_errors=True)

    bad = [name for name, ok in legs if not ok]
    for name, ok in legs:
        print("%s %s" % ("PASS" if ok else "FAIL", name))
    print("%d/%d" % (len(legs) - len(bad), len(legs)))
    return 0 if not bad else 1


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
        print("  %d comparisons re-run from thresholds only; triple columns consulted %d"
              % (s["comparisons"], s["triple_columns_consulted_to_rerun"]))
        print("  threshold re-derives from the band: max |diff| t_max_end %r / t_side %r"
              % (s["max_abs_diff_t_max_end"], s["max_abs_diff_t_side"]))
        print("  rules reproduced exactly: %s" % s["rules_reproduced_exactly"])
        print("  two different published thresholds on %d row(s); own verdict ambiguous on %d "
              "(%.1f%%), guarded screen ambiguous on %d"
              % (s["rows_with_two_different_thresholds"], s["rows_own_verdict_ambiguous"],
                 100.0 * (s["ambiguous_share"] or 0.0), s["rows_guarded_screen_ambiguous"]))
        print("  threshold-runnable collections %d (new beyond E270: %d / %d records)"
              % (s["collections_threshold_runnable"], s["collections_newly_runnable"],
                 s["records_newly_runnable"]))
        for entry in face["census"]["newly_runnable"]:
            print("    + %-30s %-28s %3d records  %s" % (entry["face"], entry["path"],
                                                         entry["records"], ",".join(entry["thresholds"])))
        return 0
    print("usage: e273_guard_from_threshold.py [run|verify|selftest]")
    return 2


if __name__ == "__main__":
    sys.exit(main())