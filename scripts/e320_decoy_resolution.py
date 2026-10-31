"""E320 -- is the decoy avoidable? For every substitution-span gate, is the gated quantity itself
in the block?

E317 published 225 gate leaves whose block offers at least two positive numbers a reader could
substitute for the quantity (``decoy.span_orders_of_magnitude``), and its headline quote -- "the
tolerance a reader would compute from those decoys spans N orders of magnitude" -- is a statement
about ambiguity, not about impossibility.  A reader who reads the whole block may find the
quantity itself; if it is there, and it is the only candidate the gate's own name points at, the
substitution is avoidable and the span overstates the risk.  If it is not there, the span is the
truth.

E318 then pruned the count-named leaves out of the census (a count is not a gate).  This study
takes the substitution-span leaves that survive that prune, and for each one asks:

  * does a candidate carry the gate's own quantity token (``close_diff_tolerance`` -> ``close_diff``)?
  * does a candidate carry the gate's magnitude fingerprint (the same number printed twice)?
  * after the identified candidate is removed, how many decades of ambiguity remain?

Three legs, one face:

1. **The control.** Recompute every leaf's substitution span from the block and compare it with
   the span E317 published.  If it does not reproduce, this study is reading a different block.
2. **The resolution.** Classify each leaf ``resolved_by_name`` / ``resolved_by_copy`` /
   ``ambiguous`` / ``unresolved`` / ``block_unresolved``, publishing the candidates it decided
   on and the channel it used.
3. **The residual ambiguity.** The span of the candidates that are NOT the gated quantity --
   the number a reader still faces after doing the right thing.

usage:
  python scripts/e320_decoy_resolution.py run
  python scripts/e320_decoy_resolution.py verify
  python scripts/e320_decoy_resolution.py selftest
"""

import io
import json
import math
import os
import subprocess
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
if HERE not in sys.path:
    sys.path.insert(0, HERE)

import e317_print_coverage_census as e317  # noqa: E402
import e318_count_named_gate_leaves as e318  # noqa: E402

ROOT = e317.ROOT
OUTDIR = os.path.join(ROOT, "results", "state_tilt")
INPUT = "PRINTCOV-2026-10-31.json"
FACE = "DECOYRESOLVE-%s.json"
LATEST = "decoyresolve_latest.json"
TODAY = "2026-10-31"
STUDY = "E320_decoy_resolution"

# Tokens that name the quantity a gate is rated in, once the gate's own tolerance word is
# removed.  The list is deliberately small: a token that turns up in a leaf path is context
# (``gates``, ``spec``, ``value``), never the quantity's name.
STEM_DROP = frozenset(("tol", "tolerance", "rtol", "atol", "eps", "epsilon"))
UNIT_WORDS = frozenset(("bp", "bps", "pp", "ppts", "pct", "percent", "shares", "share",
                        "usd", "cny", "lots", "draws", "count", "units"))
COPY_RTOL = 1e-12


def leaves(doc):
    return e317.all_leaves(doc)


def block_candidates(doc, block, gate_leaf):
    """The positive numeric leaves a reader of this block could substitute for the quantity.

    Same rule E317 used to publish the span (numbers whose immediate parent is this block, not
    tolerance-named, not noise), with the gate leaf itself removed -- it is the tolerance, never
    the quantity.  The immediate-parent rule is kept deliberately: it is what published E317's
    span, so re-deriving it is a control on this study rather than a second convention.
    """
    all_leaves = leaves(doc)
    if block in ("<face root>", "", None):
        blk = [x for x in all_leaves if e317.parent_path(x[1]) == ""]
    else:
        blk = [x for x in all_leaves if e317.parent_path(x[1]) == block]
    out = []
    for value, path, kind in blk:
        if kind != "number" or value is None:
            continue
        if path == gate_leaf:
            continue
        if e317.is_tolerance_leaf(path) or e317.is_noise_leaf(path):
            continue
        if not math.isfinite(value):
            continue
        out.append((value, path))
    return out


def span(cands):
    pos = sorted(v for v, _p in cands if v > 0)
    if len(pos) < 2:
        return {"candidates": len(pos), "min": (pos[0] if pos else None),
                "max": (pos[-1] if pos else None), "span_orders_of_magnitude": None}
    return {"candidates": len(pos), "min": pos[0], "max": pos[-1],
            "span_orders_of_magnitude": math.log10(pos[-1] / pos[0])}


def quantity_tokens(gate_leaf):
    """The name the gate promises to be rated in, taken from its own key.

    ``close_diff_tolerance`` -> ("close", "diff").  Two things are deliberately NOT tokens:
    a unit word (``tolerance_bp`` names a unit, not a quantity, and ``*_bp`` is every number in
    the block), and anything the block's own name supplies -- every candidate path starts with
    the block label, so a block-derived token matches every sibling by construction (the first
    cut of this study counted exactly that as "ambiguous").  A gate whose key carries no quantity
    names nothing, and that is published as such instead of being back-filled from context.
    """
    last = str(gate_leaf).split(".")[-1]
    toks = [t for t in e317.path_tokens(last) if t not in STEM_DROP and not t.isdigit()]
    if not toks:
        return [], "gate_key_empty"
    core = [t for t in toks if t not in UNIT_WORDS]
    if not core:
        return [], "gate_key_unit_only"
    return core, "gate_key"


def relative_tokens(path, block):
    """A candidate's name with the block label removed -- the leaf's own name, nothing else."""
    p = str(path)
    if block and block not in ("<face root>", ""):
        if p.startswith(block + "."):
            p = p[len(block) + 1:]
        elif p.startswith(block + "["):
            p = p[len(block):]
    return set(e317.path_tokens(p))


def resolve(doc, gate_leaf, gate_value, block):
    """Classify one gate leaf.  Pure: the whole answer comes from the face document."""
    cands = block_candidates(doc, block, gate_leaf)
    toks, tok_source = quantity_tokens(gate_leaf)

    by_name, by_copy = [], []
    for value, path in cands:
        rtoks = relative_tokens(path, block)
        if toks and set(toks).issubset(rtoks):
            by_name.append({"path": path, "value": value, "channel": "name_token"})
        elif gate_value is not None and abs(value - gate_value) <= COPY_RTOL * max(
                1.0, abs(gate_value)):
            by_copy.append({"path": path, "value": value, "channel": "magnitude_fingerprint"})

    matched = []
    if len(by_name) == 1 and not by_copy:
        klass, matched = "resolved_by_name", by_name
    elif not by_name and len(by_copy) == 1:
        klass, matched = "resolved_by_copy", by_copy
    elif len(by_name) + len(by_copy) > 1:
        klass, matched = "ambiguous", by_name + by_copy
    else:
        klass, matched = "unresolved", []

    matched_paths = set(m["path"] for m in matched)
    rest = [(v, p) for v, p in cands if p not in matched_paths]
    return {
        "leaf": gate_leaf,
        "block": block,
        "gate_value": gate_value,
        "quantity_tokens": list(toks),
        "quantity_tokens_source": tok_source,
        "candidates": [{"path": p, "value": v} for v, p in cands],
        "n_candidates": len(cands),
        "decoy_span": span(cands),
        "matches": matched,
        "n_matches": len(matched),
        "class": klass,
        "residual_span": span(rest),
    }


def base_commit():
    """The commit PRINTCOV was published at: the frozen universe this study reads.

    Census faces read a live directory drift (r1339: three census legs failed because the panel
    under them was rewritten mid-suite).  Here the drift is worse than noise -- a face rewritten
    after E317 scanned it makes E317's published span fail to reproduce, which reads as this
    study's defect.  The input face is pinned to the commit that carries it, and the commit is
    published in the output.
    """
    try:
        out = subprocess.run(["git", "log", "-1", "--format=%H", "--",
                              "results/state_tilt/" + INPUT],
                             cwd=ROOT, capture_output=True, text=True, timeout=60)
        sha = (out.stdout or "").strip().splitlines()
        return sha[0] if sha else None
    except (OSError, subprocess.SubprocessError):
        return None


def read_face(face_rel, commit, cache):
    """Read a face from the frozen commit; fall back to the worktree and say which was used."""
    hit = cache.get(face_rel)
    if hit is not None:
        return hit
    doc, source = False, "unreadable"
    if commit:
        try:
            out = subprocess.run(["git", "show", "%s:%s" % (commit, face_rel)],
                                 cwd=ROOT, capture_output=True, timeout=120)
            if out.returncode == 0 and out.stdout:
                doc = json.loads(out.stdout.decode("utf-8"))
                source = "commit"
        except (OSError, ValueError, subprocess.SubprocessError):
            doc = False
    if doc is False:
        path = os.path.join(ROOT, face_rel.replace("/", os.sep))
        if os.path.exists(path):
            try:
                doc = e317._read(path)
                source = "worktree"
            except (ValueError, OSError):
                doc = False
    cache[face_rel] = (doc, source)
    return cache[face_rel]


def load_population():
    """The substitution-span leaves that survive E318's count-word prune."""
    doc_pc, rows = e318.load_rows()
    pop = [r for r in rows
           if r.get("decoy", {}).get("span_orders_of_magnitude") is not None
           and e318.count_word(r["leaf"]) is None]
    dropped = [r for r in rows
               if r.get("decoy", {}).get("span_orders_of_magnitude") is not None
               and e318.count_word(r["leaf"]) is not None]
    return doc_pc, pop, dropped


def build():
    doc_pc, pop, dropped = load_population()
    commit = base_commit()
    cache = {}
    out, unresolved_face = [], []
    control = []
    sources = {}

    for r in pop:
        face = r["face"]
        doc, source = read_face(face, commit, cache)
        sources[source] = sources.get(source, 0) + 1
        if doc is False:
            out.append({"face": face, "leaf": r["leaf"], "block": r["block"],
                        "class": "face_unreadable", "quantity_tokens": [],
                        "quantity_tokens_source": "none", "candidates": [],
                        "n_candidates": 0, "matches": [], "n_matches": 0,
                        "decoy_span": r["decoy"], "residual_span": None,
                        "gate_value": r.get("value"), "read_from": source})
            continue
        got = resolve(doc, r["leaf"], r.get("value"), r["block"])
        got["face"] = face
        got["read_from"] = source
        got["published_span"] = r["decoy"]["span_orders_of_magnitude"]
        got["span_reproduces"] = (
            got["decoy_span"]["span_orders_of_magnitude"] is not None
            and abs(got["decoy_span"]["span_orders_of_magnitude"]
                    - r["decoy"]["span_orders_of_magnitude"]) <= 1e-6)
        control.append(got["span_reproduces"])
        out.append(got)

    tally = {}
    for o in out:
        tally[o["class"]] = tally.get(o["class"], 0) + 1

    resolved = [o for o in out if o["class"] in ("resolved_by_name", "resolved_by_copy")]
    ambiguous = [o for o in out if o["class"] == "ambiguous"]
    unresolved = [o for o in out if o["class"] == "unresolved"]
    for o in unresolved:
        unresolved_face.append(o)

    spans_before = [o["decoy_span"]["span_orders_of_magnitude"] for o in out
                    if o["decoy_span"]["span_orders_of_magnitude"] is not None]
    spans_after = [o["residual_span"]["span_orders_of_magnitude"] for o in out
                   if o.get("residual_span")
                   and o["residual_span"]["span_orders_of_magnitude"] is not None]

    def median(xs):
        xs = sorted(xs)
        if not xs:
            return None
        n = len(xs)
        return xs[n // 2] if n % 2 else 0.5 * (xs[n // 2 - 1] + xs[n // 2])

    total = len(out)
    verdict_class = ("%d_of_%d_substitution_span_gates_are_avoidable_by_a_reader_who_reads_the_"
                     "whole_block_and_%d_are_not" % (len(resolved), total, len(unresolved)))

    identity = [
        {"check": "the_population_is_e317_substitution_spans_minus_e318_count_words",
         "ok": len(pop) + len(dropped) == doc_pc["census"]["leaves_with_a_substitution_span"],
         "detail": [len(pop), len(dropped),
                    doc_pc["census"]["leaves_with_a_substitution_span"]]},
        {"check": "every_published_span_reproduces_from_the_block",
         "ok": all(control) and bool(control),
         "detail": {"rows": len(control), "reproduced": sum(1 for c in control if c)}},
        {"check": "the_classes_account_for_every_row",
         "ok": sum(tally.values()) == total, "detail": [tally, total]},
        {"check": "a_match_is_always_a_candidate",
         "ok": all(set(m["path"] for m in o["matches"])
                   <= set(c["path"] for c in o["candidates"]) for o in out)},
        {"check": "the_gate_leaf_is_never_a_candidate",
         "ok": all(o["leaf"] not in set(c["path"] for c in o["candidates"]) for o in out)},
        {"check": "the_residual_span_recomputes_from_the_published_candidates",
         "ok": all(_residual_ok(o) for o in out)},
        {"check": "a_resolved_row_names_exactly_one_candidate",
         "ok": all(o["n_matches"] == 1 for o in resolved)},
        {"check": "an_unresolved_row_names_none",
         "ok": all(o["n_matches"] == 0 for o in unresolved)},
    ]

    face = {
        "schema": "bigmoney/e320-decoyresolve/v1",
        "study": STUDY,
        "title": ("for every substitution-span gate that survives E318's count-word prune, is the "
                  "gated quantity itself published in the block, and what ambiguity remains?"),
        "evidence_cutoff": TODAY,
        "generated": TODAY,
        "input_face": "results/state_tilt/" + INPUT,
        "base_commit": commit,
        "read_sources": dict(sorted(sources.items())),
        "join_rules": {
            "population": ("E317's substitution-span leaves (a block publishing >= 2 positive "
                           "numeric candidates) minus the leaves E318 pruned as counts"),
            "candidates": ("positive numeric leaves of the gate's own block, excluding "
                           "tolerance-named and noise-named leaves and the gate leaf itself -- "
                           "the rule that published E317's span"),
            "name_token": ("the gate's own key, tolerance word removed "
                           "(close_diff_tolerance -> close+diff); when the key carries nothing "
                           "else the block's name is used and that is published as the source"),
            "magnitude_fingerprint": ("a candidate equal to the gate value at 1e-12 relative: the "
                                      "same number printed twice"),
            "classes": ("resolved_by_name / resolved_by_copy (exactly one identification) / "
                        "ambiguous (>= 2 identifications) / unresolved (none) / "
                        "block or face unreadable"),
        },
        "census": {
            "population": total,
            "dropped_as_count_words": len(dropped),
            "classes": dict(sorted(tally.items())),
            "resolved": len(resolved),
            "ambiguous": len(ambiguous),
            "unresolved": len(unresolved),
            "resolved_by_name": tally.get("resolved_by_name", 0),
            "resolved_by_copy": tally.get("resolved_by_copy", 0),
            "quantity_tokens_from_gate_key": sum(
                1 for o in out if o["quantity_tokens_source"] == "gate_key"),
            "quantity_tokens_gate_key_empty": sum(
                1 for o in out if o["quantity_tokens_source"] == "gate_key_empty"),
            "quantity_tokens_gate_key_unit_only": sum(
                1 for o in out if o["quantity_tokens_source"] == "gate_key_unit_only"),
            "span_before": {"median": median(spans_before),
                            "max": (max(spans_before) if spans_before else None),
                            "rows": len(spans_before)},
            "span_after": {"median": median(spans_after),
                           "max": (max(spans_after) if spans_after else None),
                           "rows": len(spans_after)},
            "span_decades_removed_total": (
                round(sum(spans_before) - sum(spans_after), 4) if spans_after else None),
            "rows_with_no_residual_ambiguity": sum(
                1 for o in out if o["residual_span"]
                and o["residual_span"]["span_orders_of_magnitude"] is None),
            "faces_in_population": len(set(o["face"] for o in out)),
            "faces_with_an_unresolved_leaf": len(set(o["face"] for o in unresolved)),
            "top_residual_spans": sorted(
                [{"face": o["face"], "leaf": o["leaf"], "class": o["class"],
                  "span": round(o["residual_span"]["span_orders_of_magnitude"], 4)}
                 for o in out if o["residual_span"]
                 and o["residual_span"]["span_orders_of_magnitude"] is not None],
                key=lambda x: -x["span"])[:10],
        },
        "verdict": verdict_class,
        "rows": out,
        "identity_checks": identity,
        "notes": [
            "%d of %d gates are avoidable by a reader who reads the whole block (%d by the "
            "quantity's own name token, %d by the gate's magnitude printed twice); %d are not." % (
                len(resolved), total, tally.get("resolved_by_name", 0),
                tally.get("resolved_by_copy", 0), len(unresolved)),
            "E317's substitution span is a worst case for the reader who stops at the first "
            "number: after the identified candidate is removed the median span falls from %s to "
            "%s decades." % (
                ("%.3f" % median(spans_before)) if spans_before else "n/a",
                ("%.3f" % median(spans_after)) if spans_after else "n/a"),
            "the quantity's name comes from the gate's own key on %d rows; on %d rows the key names "
            "nothing but the tolerance word and on %d it names only a unit, so those rows are "
            "resolved by the fingerprint channel or not at all." % (
                sum(1 for o in out if o["quantity_tokens_source"] == "gate_key"),
                sum(1 for o in out if o["quantity_tokens_source"] == "gate_key_empty"),
                sum(1 for o in out if o["quantity_tokens_source"] == "gate_key_unit_only")),
            "a resolved row is not a readable gate: E317 already measured that %d of %d leaves "
            "are reader-complete, and resolving the quantity does not supply the unit." % (
                doc_pc["census"]["reader_complete_leaves"],
                doc_pc["census"]["gate_leaves"]),
        ],
    }
    return face


def _residual_ok(o):
    """The published residual span must be the span of the published non-matched candidates."""
    if not o.get("residual_span"):
        return True
    rest = [c["value"] for c in o["candidates"]
            if c["path"] not in set(m["path"] for m in o["matches"])]
    want = span([(v, "") for v in rest])
    got = o["residual_span"]
    if want["span_orders_of_magnitude"] is None or got["span_orders_of_magnitude"] is None:
        return want["span_orders_of_magnitude"] is None \
            and got["span_orders_of_magnitude"] is None
    return abs(want["span_orders_of_magnitude"] - got["span_orders_of_magnitude"]) <= 1e-9


def run():
    face = build()
    e317.save(face, FACE % TODAY)
    e317.save(face, LATEST)
    print("%s  %s" % (face["schema"], face["verdict"]))
    print("census: %s" % json.dumps(face["census"]["classes"], ensure_ascii=False))
    bad = [c["check"] for c in face["identity_checks"] if not c["ok"]]
    if bad:
        print("IDENTITY FAILED: %s" % bad)
        return 1
    return 0


def verify():
    path = os.path.join(OUTDIR, FACE % TODAY)
    if not os.path.exists(path):
        print("face missing: %s" % path)
        return 1
    published = e317._read(path)
    fresh = build()
    problems = []
    if published.get("verdict") != fresh["verdict"]:
        problems.append("verdict")
    if published.get("census") != fresh["census"]:
        problems.append("census")
    if len(published.get("rows", [])) != len(fresh["rows"]):
        problems.append("row count")
    for a, b in zip(published.get("rows", []), fresh["rows"]):
        if a.get("class") != b.get("class") or a.get("leaf") != b.get("leaf"):
            problems.append("row %s" % a.get("leaf"))
            break
    for c in fresh["identity_checks"]:
        if not c["ok"]:
            problems.append("identity %s" % c["check"])
    print("verify: %d problems" % len(problems))
    if problems:
        print(json.dumps(problems[:8], ensure_ascii=False))
        return 1
    return 0


# ---- selftest -----------------------------------------------------------------
def _fixture(name_match=1, copies=0, tol_value=0.25):
    """A block with one gate and a controlled candidate set."""
    blk = {"close_diff_tolerance": tol_value}
    for i in range(name_match):
        blk["close_diff" if i == 0 else "close_diff_%d" % i] = 1.5 + i
    for i in range(copies):
        blk["copy_%d" % i] = tol_value
    blk["noise_count"] = 7.0
    blk["far_away"] = 9000.0
    return {"gates": {"A": blk}}


def selftest():
    fails = []

    def check(name, ok, detail=""):
        check.total += 1
        if not ok:
            fails.append((name, detail))
    check.total = 0

    # one name match -> resolved_by_name, and the residual span drops
    doc = _fixture(name_match=1)
    got = resolve(doc, "gates.A.close_diff_tolerance", 0.25, "gates.A")
    check("one_name_match_resolves", got["class"] == "resolved_by_name", got["class"])
    check("the_match_is_the_quantity",
          [m["path"] for m in got["matches"]] == ["gates.A.close_diff"], got["matches"])
    check("the_quantity_token_is_the_gate_key_stem",
          got["quantity_tokens"] == ["close", "diff"] and
          got["quantity_tokens_source"] == "gate_key", got["quantity_tokens"])
    check("the_residual_span_excludes_the_match",
          got["residual_span"]["candidates"] == got["n_candidates"] - 1)

    # two name matches -> ambiguous, and the ambiguity is published
    doc = _fixture(name_match=2)
    got = resolve(doc, "gates.A.close_diff_tolerance", 0.25, "gates.A")
    check("two_name_matches_are_ambiguous", got["class"] == "ambiguous", got["class"])
    check("ambiguity_names_both", got["n_matches"] == 2, got["n_matches"])

    # a bare tolerance key names no quantity: the block's own name is not a statement about it
    doc = {"gates": {"GA": {"tolerance": 0.1, "GA_observed": 3.0, "other": 4.0}}}
    got = resolve(doc, "gates.GA.tolerance", 0.1, "gates.GA")
    check("a_bare_tolerance_names_no_quantity",
          got["quantity_tokens_source"] == "gate_key_empty" and got["quantity_tokens"] == [],
          [got["quantity_tokens"], got["quantity_tokens_source"]])
    check("a_unit_only_stem_is_not_a_name",
          resolve({"b": {"residual_tolerance_bp": 5.0, "expected_bp": 1.0, "measured_bp": 9.0}},
                  "b.residual_tolerance_bp", 5.0, "b")["quantity_tokens_source"] == "gate_key")

    # a copy of the gate value resolves when no name matches
    doc = _fixture(name_match=0, copies=1)
    got = resolve(doc, "gates.A.close_diff_tolerance", 0.25, "gates.A")
    check("a_copy_resolves_by_fingerprint", got["class"] == "resolved_by_copy", got["class"])

    # nothing matching -> unresolved, and the full span survives
    doc = _fixture(name_match=0, copies=0)
    got = resolve(doc, "gates.A.close_diff_tolerance", 0.25, "gates.A")
    check("nothing_matching_is_unresolved", got["class"] == "unresolved", got["class"])
    check("the_unresolved_span_is_the_whole_block",
          got["residual_span"]["span_orders_of_magnitude"] ==
          got["decoy_span"]["span_orders_of_magnitude"])

    # the gate leaf is never one of its own candidates
    doc = _fixture(name_match=1)
    got = resolve(doc, "gates.A.close_diff_tolerance", 0.25, "gates.A")
    check("the_gate_is_not_a_candidate",
          "gates.A.close_diff_tolerance" not in [c["path"] for c in got["candidates"]])

    # a count word is not a gate: the population excludes it
    check("count_words_are_excluded",
          e318.count_word("census.faces_with_no_tolerance_name_at_all") is not None)

    # a tolerance-named sibling is not a candidate (it would be a second gate)
    doc = {"gates": {"A": {"close_diff_tolerance": 0.25, "close_diff_rtol": 0.5,
                           "close_diff": 1.5}}}
    got = resolve(doc, "gates.A.close_diff_tolerance", 0.25, "gates.A")
    check("a_second_tolerance_is_not_a_candidate",
          [c["path"] for c in got["candidates"]] == ["gates.A.close_diff"],
          got["candidates"])

    for name, detail in fails:
        print("FAIL %s %s" % (name, detail))
    total = check.total
    print("selftest: %d/%d" % (total - len(fails), total))
    return 0 if not fails else 1


def main(argv):
    cmd = argv[1] if len(argv) > 1 else "run"
    if cmd == "run":
        return run()
    if cmd == "verify":
        return verify()
    if cmd == "selftest":
        return selftest()
    print(__doc__)
    return 2


if __name__ == "__main__":
    sys.exit(main(sys.argv))