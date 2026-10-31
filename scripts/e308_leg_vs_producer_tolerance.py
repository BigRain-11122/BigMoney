"""E308 -- smoke legs that compare a face value tighter than the face's own declared gate.

r1316 repaired a leg comparing two copies at 1e-9; r1324 (E299) priced how many legs compare
finer than the field is *printed*; r1327 (E305) priced the rows that could only be bounded at
face level. Pricing those rows surfaced a different shape, which this study measures:

    a face publishes its own decision tolerance (``rel_tol``, ``tolerance``, ``frozen_spec.tolerance``)
    AND a smoke leg that reads that face compares the same quantity at a tighter tolerance.

If the producer is entitled to make a difference up to G and the leg fails on anything above L,
then with L < G there is a band (L, G] of differences the producer may legitimately contain and
the leg would call a breach. This study pairs the two gates and publishes the band; it does not
count "wrong legs".

Declared join rules (fixed before a number is read):

  GATE  -- a published NUMBER whose last key segment names a comparison tolerance
           (tolerance / tol / rel_tol / abs_tol / rtol / atol / epsilon), value inside (0, 1],
           booleans excluded. Keys whose name says the number measures rather than permits are
           NOT gates and are published as exclusions with their reason: required_* / reachable_* /
           *_fraction / *_pct / edge_* / *_scale / flat_rel_tol / gamma_tol (those are quantities
           the producer measured *about* a tolerance, or gates on a derived property, not on the
           published scalar a leg reads).
  UNIT  -- 'relative' when the key says rel/rtol, 'absolute' when it says abs/atol, otherwise
           'unspecified'. The unit is published and never silently assumed.
  BAND  -- for an absolute (or unspecified) gate the band is non-empty iff L < G, independent of
           any scale. For a relative gate the permitted error is G*|x|, so the band is non-empty
           iff |x| > L/G: the census publishes ``scale_above_which_leg_is_tighter = L/G`` and
           states that, rather than inventing a scale the face does not publish.
  SLACK -- L is the site's own tolerance from ``smoke_test.py`` (equality sites carry 0.0).

Nothing is rebuilt and no study is re-run: every number is arithmetic over ``smoke_test.py``'s
source and the published JSON under ``results/`` (legs and sites come from the E299 parser, which
owns that grammar -- imported, not copied).
"""

import glob
import io
import json
import os
import re
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
OUTDIR = os.path.join(ROOT, "results", "state_tilt")
sys.path.insert(0, HERE)

import e299_rounded_vs_tolerance_census as E299  # noqa: E402  (leg/site grammar owner)

STUDY = "E308_leg_vs_producer_tolerance"
TITLE = ("where a smoke leg compares a face value tighter than the face's own declared tolerance "
         "gate, how wide is the band of differences the producer may contain and the leg would fail?")
FACE = "GATETOL-%s.json"
LATEST = "gatetol_latest.json"
TODAY = "2026-10-31"

GATE_WORDS = {"tolerance", "tol", "rel_tol", "abs_tol", "rtol", "atol", "epsilon"}
EXCLUDE_WORDS = (
    "required", "reachable", "fraction", "pct", "edge", "scale", "toll", "stability",
    "clears", "flat_rel_tol", "gamma_tol",
)


# --------------------------------------------------------------------------- reading

def _read(path):
    with io.open(path, encoding="utf-8") as fh:
        return json.load(fh)


def save(payload, name, outdir=None):
    outdir = outdir or OUTDIR
    if not os.path.isdir(outdir):
        os.makedirs(outdir)
    path = os.path.join(outdir, name)
    with io.open(path, "w", encoding="utf-8", newline="\n") as fh:
        fh.write(json.dumps(payload, ensure_ascii=False, indent=1))
        fh.write("\n")
    return path


def is_number(v):
    return isinstance(v, (int, float)) and not isinstance(v, bool)


def gate_units(key):
    low = key.lower()
    if "rel" in low or "rtol" in low:
        return "relative"
    if "abs" in low or "atol" in low:
        return "absolute"
    return "unspecified"


def scan_tolerance_keys(payload, path=""):
    """Every number whose key NAMES a tolerance, split into gates and disclosed exclusions.

    The name test is deliberately broad (any key containing "tol") so that a tolerance-named
    MEASUREMENT (required_tolerance_pct, edge_tolerance_pct, tolerance_fraction) is seen and
    published as an exclusion instead of silently failing to be a gate -- the E208 rule: a
    rejection must be recorded, not dropped.
    """
    gates, excluded = [], []
    if isinstance(payload, dict):
        for key, value in payload.items():
            here = (path + "." + key) if path else key
            if is_number(value) and re.search(r"tol", key.lower()) and "toll" not in key.lower():
                last = key.lower()
                row = {"path": here, "key": key, "value": value, "units": gate_units(key)}
                hits = [w for w in EXCLUDE_WORDS if w in last]
                if last in GATE_WORDS or last.endswith("_tol") or last.endswith("tolerance"):
                    if hits:
                        row["excluded_because"] = "name measures rather than permits: " + ",".join(hits)
                        excluded.append(row)
                    elif not (0 < value <= 1):
                        row["excluded_because"] = "value outside (0,1]: a tolerance is a fraction"
                        excluded.append(row)
                    else:
                        gates.append(row)
                elif hits:
                    row["excluded_because"] = "name measures rather than permits: " + ",".join(hits)
                    excluded.append(row)
                else:
                    row["excluded_because"] = ("the key is tolerance-named but is not a comparison "
                                               "tolerance (no tol/tolerance suffix)")
                    excluded.append(row)
            sub_g, sub_x = scan_tolerance_keys(value, here)
            gates.extend(sub_g)
            excluded.extend(sub_x)
    elif isinstance(payload, list):
        for i, value in enumerate(payload):
            sub_g, sub_x = scan_tolerance_keys(value, "%s[%d]" % (path, i))
            gates.extend(sub_g)
            excluded.extend(sub_x)
    return gates, excluded


_PRODUCERS = None
COMPARISON = re.compile(r"(<=|>=|==|!=|<|>)")


def producer_sources():
    """Every python source under the repo's producing packages, read once."""
    global _PRODUCERS
    if _PRODUCERS is None:
        _PRODUCERS = []
        for sub in ("scripts", "Tools", "live", "monitor", "firm"):
            base = os.path.join(ROOT, sub)
            for dirpath, _dirs, files in os.walk(base):
                for fn in sorted(files):
                    if fn.endswith(".py"):
                        _PRODUCERS.append(os.path.join(dirpath, fn))
    return _PRODUCERS


def producers_for(face):
    """The scripts that name this face file -- the writers whose use of a gate can be read.

    The study's own source is excluded: its docstrings and selftest legs name face files, so a
    census that included itself would answer its own question with its own text (the E294/E298
    self-inclusion family).
    """
    needle = os.path.basename(face).replace("%s", "")
    own = os.path.abspath(__file__)
    hits = []
    for path in producer_sources():
        if os.path.abspath(path) == own:
            continue
        try:
            with io.open(path, encoding="utf-8", errors="replace") as fh:
                src = fh.read()
        except OSError:
            continue
        if needle and needle in src:
            hits.append((path, src))
    return hits


def gate_scope(face, gate, producers):
    """Does the producer itself COMPARE with this gate, or only publish it?

    A published tolerance the writer never compares against is a declaration, and a leg comparing
    tighter than a declaration is not thereby flagging a difference the producer permits. The
    reading is a verbatim source scan of the scripts that name the face: every line carrying the
    gate's key; a line that also carries a comparison operator is evidence the gate is used as one.
    Evidence lines are published so the reading can be re-checked by eye.
    """
    key = gate["key"]
    evidence = []
    for path, src in producers:
        for i, line in enumerate(src.splitlines()):
            if key not in line:
                continue
            if COMPARISON.search(line):
                evidence.append({"producer": rel(path), "line": i + 1, "text": line.strip()[:170]})
    if evidence:
        return "used_in_a_comparison", evidence[:4]
    if producers:
        return "declared_but_never_compared", []
    return "producer_not_found", []


def resolve_face(name):
    """Glob-free path resolution for a face named by a leg (supports the %s template form)."""
    if "%s" in name or "*" in name:
        pattern = name.replace("%s", "*")
        hits = sorted(glob.glob(os.path.join(ROOT, pattern.replace("/", os.sep))))
        return hits[-1] if hits else None
    path = os.path.join(ROOT, name.replace("/", os.sep))
    return path if os.path.exists(path) else None


def rel(path):
    return os.path.relpath(path, ROOT).replace(os.sep, "/")


# --------------------------------------------------------------------------- pairing

def pair(sites, gates_by_face, scope_by_gate):
    """One row per (site, gate) on the same face. Bands only; never a defect count."""
    rows = []
    for site in sites:
        tol = site.get("tolerance")
        for face in site.get("faces_named") or []:
            for gate in gates_by_face.get(face, []):
                scope, evidence = scope_by_gate.get((face, gate["path"]), ("producer_not_found", []))
                row = {
                    "leg": site["leg"],
                    "leg_line": site.get("line"),
                    "face": face,
                    "leg_tolerance": tol,
                    "leg_kind": site.get("kind"),
                    "leg_keys": site.get("keys") or [],
                    "leg_expression": site.get("expression"),
                    "gate_path": gate["path"],
                    "gate_value": gate["value"],
                    "gate_units": gate["units"],
                    "gate_scope": scope,
                    "gate_scope_evidence": evidence,
                }
                if tol is None:
                    row["band"] = "no_leg_tolerance"
                elif gate["units"] == "relative":
                    row["scale_above_which_leg_is_tighter"] = (tol / gate["value"]) if gate["value"] else None
                    row["band"] = ("leg_tighter_for_any_scale_above_that"
                                   if tol > 0 else "leg_exact_equality_tighter_for_any_positive_scale")
                else:
                    tighter = tol < gate["value"]
                    row["band"] = "leg_tighter" if tighter else "leg_looser_or_equal"
                    row["leg_share_of_gate"] = (tol / gate["value"]) if gate["value"] else None
                # a band only stands as a finding where the producer is seen comparing with the gate
                row["band_stands"] = bool(
                    row["band"] != "no_leg_tolerance" and row["band"] != "leg_looser_or_equal"
                    and scope == "used_in_a_comparison")
                if row["band"] == "leg_exact_equality_tighter_for_any_positive_scale":
                    row["band_note"] = ("exact equality is the widest possible band, but the "
                                        "producer's float gate does not entitle a difference in a "
                                        "count; published, not counted as a permitted difference")
                rows.append(row)
    return rows


# --------------------------------------------------------------------------- build

def build(outdir=None):
    src_path = os.path.join(ROOT, "smoke_test.py")
    with io.open(src_path, encoding="utf-8") as fh:
        src = fh.read()
    legs, tree = E299.parse_legs(src)
    sites = E299.extract_sites(legs, tree)

    faces = sorted({f for s in sites for f in (s.get("faces_named") or [])})
    gates_by_face, face_rows, exclusions, missing = {}, [], [], []
    scope_by_gate = {}
    for face in faces:
        path = resolve_face(face)
        if path is None:
            missing.append({"face": face, "because": "no file on disk (template or absent)"})
            continue
        try:
            payload = _read(path)
        except Exception as exc:  # unreadable face is reported, never dropped
            missing.append({"face": face, "because": "unreadable: %s" % exc})
            continue
        gates, excl = scan_tolerance_keys(payload)
        reader_legs = sorted({s["leg"] for s in sites if face in (s.get("faces_named") or [])})
        producers = producers_for(face) if gates else []
        for gate in gates:
            scope, evidence = gate_scope(face, gate, producers)
            gate["scope"] = scope
            gate["scope_evidence"] = evidence
            twins = [e["path"] for e in excl if e["value"] == gate["value"]]
            if twins:
                # the same number is a gate under one key and a measurement under another: the
                # partition is not stable under renaming, so the twin is published with the gate
                gate["same_value_as_excluded_key"] = twins
            scope_by_gate[(face, gate["path"])] = (scope, evidence)
        face_rows.append({
            "face": face, "path": rel(path), "reader_legs": reader_legs,
            "n_gates": len(gates), "n_tolerance_named_not_gate": len(excl),
            "writers_naming_this_face": sorted({rel(p) for p, _s in producers}),
            "gates": gates,
        })
        if gates:
            gates_by_face[face] = gates
        for e in excl:
            e["face"] = face
            exclusions.append(e)

    rows = pair(sites, gates_by_face, scope_by_gate)
    tighter = [r for r in rows if r["band"] in ("leg_tighter", "leg_tighter_for_any_scale_above_that")]
    exact = [r for r in rows if r["band"] == "leg_exact_equality_tighter_for_any_positive_scale"]
    looser = [r for r in rows if r["band"] == "leg_looser_or_equal"]
    no_tol = [r for r in rows if r["band"] == "no_leg_tolerance"]
    stands = [r for r in rows if r["band_stands"]]

    gated_faces = sorted(gates_by_face)
    payload = {
        "schema": "bigmoney/e308-gatetol/v1",
        "study": STUDY,
        "title": TITLE,
        "evidence_cutoff": TODAY,
        "generated": TODAY,
        "self_faces_excluded": [FACE % TODAY, LATEST],
        "join_rules": {
            "gate": "number under a tolerance-named last key segment, 0<v<=1, booleans excluded",
            "gate_exclusions": list(EXCLUDE_WORDS),
            "band_absolute": "non-empty iff leg_tolerance < gate_value (scale-free)",
            "band_relative": "permitted error = gate*|x|; non-empty iff |x| > leg_tolerance/gate",
            "slack": "leg tolerance read from smoke_test.py by the E299 parser",
        },
        "census": {
            "legs": len(legs),
            "sites": len(sites),
            "faces_named_by_sites": len(faces),
            "faces_resolved": len(face_rows),
            "faces_publishing_a_gate": len(gated_faces),
            "faces_with_tolerance_named_not_gate_only": len(
                [f for f in face_rows if f["n_gates"] == 0 and f["n_tolerance_named_not_gate"]]) ,
            "faces_with_no_tolerance_name_at_all": len(
                [f for f in face_rows if f["n_gates"] == 0 and f["n_tolerance_named_not_gate"] == 0]),
            "pairs": len(rows),
            "pairs_leg_tighter": len(tighter),
            "pairs_leg_exact_equality": len(exact),
            "pairs_leg_looser_or_equal": len(looser),
            "pairs_no_leg_tolerance": len(no_tol),
            "pairs_band_stands": len(stands),
            "pairs_band_stands_relative": len([r for r in stands if r["gate_units"] == "relative"]),
            "pairs_band_stands_exact_equality": len(
                [r for r in stands if r["band"] == "leg_exact_equality_tighter_for_any_positive_scale"]),
            "pairs_band_rejected_scope": len([r for r in (tighter + exact) if not r["band_stands"]]),
            "pairs_scope_used_in_a_comparison": len([r for r in rows if r["gate_scope"] == "used_in_a_comparison"]),
            "pairs_scope_declared_but_never_compared": len(
                [r for r in rows if r["gate_scope"] == "declared_but_never_compared"]),
            "pairs_scope_producer_not_found": len([r for r in rows if r["gate_scope"] == "producer_not_found"]),
            "gate_exclusions": len(exclusions),
            "gates_with_an_excluded_twin": len(
                [g for f in face_rows for g in f["gates"] if g.get("same_value_as_excluded_key")]),
            "unresolved_faces": len(missing),
        },
        "verdict": (
            "bands_stand_only_where_the_producer_is_seen_comparing_with_the_gate" if stands
            else "no_band_survives_the_scope_test"),
        "rows_band_stands": stands,
        "rows_leg_tighter_or_exact": tighter + exact,
        "rows_leg_looser": looser,
        "rows_no_leg_tolerance": no_tol,
        "faces": face_rows,
        "gate_exclusions": exclusions,
        "unresolved_faces": missing,
        "notes": [
            "a band is not a defect: a leg may be reading a sibling the face also publishes at "
            "full precision, and a relative gate's scale may be far below the threshold published",
            "exclusions are published with their reason so a tolerance-named measurement is not "
            "promoted into a gate (the E207/E208 name-semantics rule)",
            "scope is a source reading, not a proof: a gate used in a comparison elsewhere in the "
            "writer is evidence the gate is a gate, not that it governs this leg's quantity",
            "a gate and an exclusion can carry the same value under different names (gamma_tol vs "
            "tol): those twins are published on the gate row, because the partition is a reading of "
            "names and names are not stable",
        ],
    }
    payload["identity_checks"] = identity_checks(payload)
    save(payload, FACE % TODAY, outdir)
    save(payload, LATEST, outdir)
    return payload


def identity_checks(payload):
    c = payload["census"]
    checks = []
    checks.append(("pair_partition_sums",
                   c["pairs"] == (c["pairs_leg_tighter"] + c["pairs_leg_exact_equality"]
                                  + c["pairs_leg_looser_or_equal"] + c["pairs_no_leg_tolerance"])))
    checks.append(("face_partition_sums",
                   c["faces_resolved"] == (c["faces_publishing_a_gate"]
                                           + c["faces_with_tolerance_named_not_gate_only"]
                                           + c["faces_with_no_tolerance_name_at_all"])))
    checks.append(("every_row_names_a_gate", all(r.get("gate_path") for r in payload["rows_leg_tighter_or_exact"])))
    checks.append(("every_gated_face_has_a_reader",
                   all(f["reader_legs"] for f in payload["faces"] if f["n_gates"])))
    checks.append(("excluded_keys_never_appear_as_gates",
                   not ({e["path"] for e in payload["gate_exclusions"]}
                        & {g["path"] for f in payload["faces"] for g in f["gates"]})))
    checks.append(("gate_values_inside_unit_interval",
                   all(0 < g["value"] <= 1 for f in payload["faces"] for g in f["gates"])))
    checks.append(("no_self_face_in_census",
                   not ({FACE % TODAY, LATEST}
                        & {os.path.basename(f["path"]) for f in payload["faces"]})))
    checks.append(("relative_rows_publish_a_threshold",
                   all(r.get("scale_above_which_leg_is_tighter") is not None
                       for r in payload["rows_leg_tighter_or_exact"]
                       if r["gate_units"] == "relative")))
    checks.append(("band_standing_rows_all_carry_scope_evidence",
                   all(r["gate_scope"] == "used_in_a_comparison" and r["gate_scope_evidence"]
                       for r in payload["rows_band_stands"])))
    checks.append(("scope_partition_sums",
                   c["pairs"] == (c["pairs_scope_used_in_a_comparison"]
                                  + c["pairs_scope_declared_but_never_compared"]
                                  + c["pairs_scope_producer_not_found"])))
    checks.append(("standing_bands_are_a_subset_of_tighter_rows",
                   c["pairs_band_stands"] + c["pairs_band_rejected_scope"]
                   == c["pairs_leg_tighter"] + c["pairs_leg_exact_equality"]))
    return [{"check": n, "ok": bool(ok)} for n, ok in checks]


# --------------------------------------------------------------------------- cli

def cmd_run():
    p = build()
    c = p["census"]
    print("E308 %s cutoff=%s" % (p["verdict"], p["evidence_cutoff"]))
    print("  legs=%d sites=%d faces_named=%d resolved=%d gated=%d pairs=%d"
          % (c["legs"], c["sites"], c["faces_named_by_sites"], c["faces_resolved"],
             c["faces_publishing_a_gate"], c["pairs"]))
    print("  leg_tighter=%d exact=%d looser=%d no_tol=%d exclusions=%d unresolved=%d"
          % (c["pairs_leg_tighter"], c["pairs_leg_exact_equality"], c["pairs_leg_looser_or_equal"],
             c["pairs_no_leg_tolerance"], c["gate_exclusions"], c["unresolved_faces"]))
    print("  scope: comparison=%d declared_only=%d producer_not_found=%d -> bands_stands=%d (rejected %d)"
          % (c["pairs_scope_used_in_a_comparison"], c["pairs_scope_declared_but_never_compared"],
             c["pairs_scope_producer_not_found"], c["pairs_band_stands"], c["pairs_band_rejected_scope"]))
    bad = [x for x in p["identity_checks"] if not x["ok"]]
    print("  identity: %d/%d ok" % (len(p["identity_checks"]) - len(bad), len(p["identity_checks"])))
    for x in bad:
        print("   FAIL", x["check"])
    return 0 if not bad else 1


def cmd_verify():
    path = os.path.join(OUTDIR, FACE % TODAY)
    if not os.path.exists(path):
        print("verify: face absent")
        return 2
    p = _read(path)
    problems = []
    if p["verdict"] != "bands_stand_only_where_the_producer_is_seen_comparing_with_the_gate":
        problems.append("verdict moved")
    for x in identity_checks(p):
        if not x["ok"]:
            problems.append("identity: " + x["check"])
    c = p["census"]
    if c["pairs"] != len(p["rows_leg_tighter_or_exact"]) + len(p["rows_leg_looser"]) + len(p["rows_no_leg_tolerance"]):
        problems.append("rows disagree with census")
    print("verify: %d problems" % len(problems))
    for x in problems:
        print("  -", x)
    return 0 if not problems else 1


def check(name, ok, detail=""):
    print(("  PASS " if ok else "  FAIL ") + name + ((" :: " + detail) if detail and not ok else ""))
    return bool(ok)


def cmd_selftest():
    p = _read(os.path.join(OUTDIR, FACE % TODAY))
    ok = True
    ok &= check("gate detection: band frozen_spec.tolerance read as an absolute gate",
                any(g["path"] == "frozen_spec.tolerance" and g["value"] == 1e-12
                    for f in p["faces"] for g in f["gates"]))
    ok &= check("gate detection: t35 rel_tol is relative",
                any(g["path"] == "rel_tol" and g["units"] == "relative"
                    for f in p["faces"] for g in f["gates"]))
    ok &= check("exclusion: required_tolerance_pct never promoted to a gate",
                any("required_tolerance_pct" in e["path"] for e in p["gate_exclusions"]))
    ok &= check("exclusion: edge_tolerance_pct never promoted to a gate",
                any("edge_tolerance" in e["path"] for e in p["gate_exclusions"]))
    ok &= check("no tolerance-named measurement leaked into gates",
                not any(w in g["path"] for f in p["faces"] for g in f["gates"]
                        for w in ("required_", "edge_", "_pct", "fraction", "flat_rel_tol", "gamma_tol")))
    ok &= check("identity: every check green", all(x["ok"] for x in p["identity_checks"]))
    ok &= check("partition: pairs reconcile",
                p["census"]["pairs"] == len(p["rows_leg_tighter_or_exact"]) + len(p["rows_leg_looser"]) + len(p["rows_no_leg_tolerance"]))
    t35 = [r for r in p["rows_leg_tighter_or_exact"]
           if r["face"] == "results/t35_open_fill_verify.json" and r["gate_path"] == "rel_tol"]
    ok &= check("t35: the 1e-9 open-fill leg is tighter than rel_tol=0.002 above a published scale",
                bool(t35) and abs(t35[0]["scale_above_which_leg_is_tighter"] - 5e-7) < 1e-12,
                "rows found=%d" % len(t35))
    ok &= check("absolute band rule: leg_tighter iff leg_tolerance < gate_value",
                all((r["leg_tolerance"] < r["gate_value"]) == (r["band"] == "leg_tighter")
                    for r in p["rows_leg_tighter_or_exact"] + p["rows_leg_looser"]
                    if r["gate_units"] != "relative" and r["leg_tolerance"] is not None))
    ok &= check("scope: a declared-but-never-compared gate cannot make a band stand",
                all(not r["band_stands"] for r in p["rows_leg_tighter_or_exact"]
                    if r["gate_scope"] != "used_in_a_comparison"))
    ok &= check("scope: the study's own source never counts as a producer",
                not any("e308_leg_vs_producer_tolerance" in e["producer"]
                        for f in p["faces"] for g in f["gates"] for e in g["scope_evidence"]))
    ok &= check("twin: a gate holding the same number as an excluded key discloses it",
                p["census"]["gates_with_an_excluded_twin"] >= 1)
    ok &= check("twin: the standing band's gate is flagged name-fragile",
                bool(p["rows_band_stands"]) and all(
                    g.get("same_value_as_excluded_key")
                    for f in p["faces"] for g in f["gates"]
                    if any(r["face"] == f["face"] and r["gate_path"] == g["path"]
                           for r in p["rows_band_stands"])))
    ok &= check("mutation: a standing band without scope evidence is caught",
                not all(x["ok"] for x in identity_checks(
                    dict(p, rows_band_stands=[dict(r, gate_scope="declared_but_never_compared")
                                              for r in p["rows_band_stands"]]))))
    # mutations must be caught
    import copy
    m = copy.deepcopy(p)
    m["census"]["pairs_leg_tighter"] += 1
    ok &= check("mutation: an inflated at-risk count breaks the partition",
                not all(x["ok"] for x in identity_checks(m)))
    m = copy.deepcopy(p)
    m["gate_exclusions"].append({"path": "frozen_spec.tolerance", "excluded_because": "x", "face": "x", "key": "tolerance", "value": 1e-12})
    ok &= check("mutation: a key in both partitions is caught",
                not all(x["ok"] for x in identity_checks(m)))
    m = copy.deepcopy(p)
    for f in m["faces"]:
        if f["n_gates"]:
            f["reader_legs"] = []
    ok &= check("mutation: a gated face with no reader is caught",
                not all(x["ok"] for x in identity_checks(m)))
    m = copy.deepcopy(p)
    m["faces"].append({"face": "results/state_tilt/" + (FACE % TODAY), "path": "results/state_tilt/" + (FACE % TODAY),
                       "reader_legs": ["x"], "n_gates": 1, "n_tolerance_named_not_gate": 0, "gates": []})
    ok &= check("mutation: the census listing itself is caught",
                not all(x["ok"] for x in identity_checks(m)))
    ok &= check("mutation: relative row without a threshold is caught",
                not all(x["ok"] for x in identity_checks(
                    dict(p, rows_leg_tighter_or_exact=[dict(r, scale_above_which_leg_is_tighter=None)
                                                       for r in p["rows_leg_tighter_or_exact"]]))))
    print("selftest: %s" % ("PASS" if ok else "FAIL"))
    return 0 if ok else 1


def main(argv):
    if len(argv) < 2:
        print(__doc__)
        return 2
    cmd = argv[1]
    if cmd == "run":
        return cmd_run()
    if cmd == "verify":
        return cmd_verify()
    if cmd == "selftest":
        return cmd_selftest()
    print("unknown command: " + cmd)
    return 2


if __name__ == "__main__":
    sys.exit(main(sys.argv))