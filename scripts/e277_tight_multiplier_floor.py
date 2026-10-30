"""E277 -- is "the tight end never narrows" a property of these windows, or of how a band is built?

E272 measured both tails of the flip budget on one ruler and found the tight tail reaches NONE of
the 12 measured rows, because every published p05 in the family is >= 1.0000 while 10 of 12 flips
need a multiplier LARGER than that.  A tail that never fires is not a finding about windows if the
number that makes it inert cannot go below 1.0 by construction.

This face answers that without drawing anything new.  Three mechanisms, each measurable:

  A  BAND BUILD      the published band is the FULL draw range (BAND_PCT = 0..100), so lo is the
                     minimum of the per-draw coefficient, read off a NESTED prefix.  The minimum
                     of a growing sample can only move outward, so |lo| is monotone non-decreasing
                     in draws and m = |lo|(top) / |lo|(base) >= 1 for every base < top -- whenever
                     the extreme is on the negative side.  (If every draw were positive, |min|
                     would shrink instead and m < 1 would be possible; the branch is published
                     rather than assumed away.)
  B  MEASURED EXPONENT  BANDDRAW already fitted the endpoint's draw exponent: gamma_head 0.348,
                     gamma_tail 0.647, and across 7 rungs x 2 families the endpoint rose on 6 of 7
                     with a minimum rise of 0.0% -- it never narrowed once.
  C  DEGENERATE BRANCH  where p05 is EXACTLY 1.0 it is not a narrowing that failed to happen, it is
                     the draw that sets the endpoint having already arrived inside the base prefix.
                     BANDNEAR1 already publishes that mass and shows dropping one seed lifts it
                     (four floor rows at p05 = 1.0 lift to 1.11..1.20).

The census half walks every published BAND* face and counts every multiplier p05 / range lower end
on disk, so "no tight pass ever fired" is a count, not a claim.

Verdict vocabulary:
    tight_end_dead_by_construction_family_should_stop_publishing_tight_pass_checks
    tight_end_is_a_property_of_these_windows
    tight_end_is_construction_limited_and_windows_not_yet_tested   (band not full-range)

Modes: run | verify | selftest
"""

from __future__ import print_function

import glob
import io
import json
import os
import re
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
if HERE not in sys.path:
    sys.path.insert(0, HERE)

OUTDIR = os.path.join(ROOT, "results", "state_tilt")
CUTOFF = "2026-10-29"
FACE = "BANDFLOOR-%s.json" % CUTOFF
LATEST = "bandfloor_latest.json"
SELF_FACES = (FACE, LATEST)

SRC_BAND = "e251_star_own_component.py"     # BAND_PCT / BAND_MODE live here
SRC_DRAW = "BANDDRAW-%s.json" % CUTOFF      # published endpoint draw exponent
SRC_NEAR1 = "BANDNEAR1-%s.json" % CUTOFF    # published exact-1.0 mass
SRC_FLIPBUDGET = "BANDFLIPBUDGET-%s.json" % CUTOFF  # published tight-tail reach

# The two branches of |lo|'s monotonicity, named so the verdict can be scoped to the one that ran.
NEGATIVE_EXTREME = "negative_extreme_endpoint_never_narrows"
POSITIVE_EXTREME = "positive_extreme_endpoint_can_narrow"


# ------------------------------------------------------------------ io
def load(name):
    with io.open(os.path.join(OUTDIR, name), encoding="utf-8") as fh:
        return json.load(fh)


def _walk(o, path=""):
    """Yield (path, scalar) for every leaf; list indices collapse to /[] so paths are stable."""
    if isinstance(o, dict):
        for k in sorted(o):
            for item in _walk(o[k], path + "/" + str(k)):
                yield item
    elif isinstance(o, list):
        for v in o:
            for item in _walk(v, path + "/[]"):
                yield item
    else:
        yield path, o


# ------------------------------------------------------------------ A: how the band is built
def band_build(src_path=None):
    """Read the band percentile/mode off the source rather than importing the module's data."""
    path = src_path or os.path.join(HERE, SRC_BAND)
    with io.open(path, encoding="utf-8") as fh:
        text = fh.read()
    pct = re.search(r"^BAND_PCT\s*=\s*\(([^)]*)\)", text, re.M)
    mode = re.search(r"^BAND_MODE\s*=\s*\"([^\"]*)\"", text, re.M)
    lo_line = re.search(r"^\s*lo\s*=\s*vals\[int\(math\.floor", text, re.M)
    if not pct:
        raise RuntimeError("BAND_PCT not found in %s" % SRC_BAND)
    bounds = tuple(float(x) for x in pct.group(1).split(",") if x.strip())
    full_range = bounds == (0.0, 100.0)
    return {
        "source": SRC_BAND,
        "band_pct": list(bounds),
        "band_mode": mode.group(1) if mode else None,
        "lo_is_the_lowest_draw": bool(lo_line),
        "full_draw_range": full_range,
        "reading": ("lo is the minimum of the per-draw coefficient over the nested prefix, so the "
                    "lower endpoint is an extremum of a growing sample"
                    if full_range and lo_line else
                    "lo is a percentile cut, so a growing sample can move either endpoint"),
    }


def endpoint_branch(sample):
    """Which monotonicity branch this draw stream is on, from the sign of its extreme."""
    if not sample:
        return None
    return NEGATIVE_EXTREME if min(sample) < 0 else POSITIVE_EXTREME


def prefix_edge(vals, draws):
    """|lo| of the band over the FIRST `draws` values -- the extremum branch of e255.prefix_edge."""
    vals = [float(v) for v in (vals or [])[:int(draws)] if v is not None]
    if not vals:
        return None
    return abs(min(vals))


def multiplier(edge_top, edge_base):
    """m = |lo|(top) / |lo|(base); None when the base endpoint is exactly zero (undefined ratio)."""
    if edge_top is None or edge_base is None or edge_base == 0:
        return None
    return float(edge_top) / float(edge_base)


# ------------------------------------------------------------------ census over published faces
def census(outdir=None):
    """Every published p05 and every multiplier-range lower end in the BAND* family, on disk."""
    outdir = outdir or OUTDIR
    faces = sorted(glob.glob(os.path.join(outdir, "BAND*.json")))
    per_face, ledger, mirrors = [], [], []
    for f in faces:
        name = os.path.basename(f)
        if name in SELF_FACES:
            continue
        if name.endswith("_latest.json"):
            # a mirror carries the same numbers as its dated twin; counting both double-counts
            mirrors.append(name)
            continue
        try:
            with io.open(f, encoding="utf-8") as fh:
                face = json.load(fh)
        except (ValueError, IOError):
            per_face.append({"face": name, "error": "unreadable"})
            continue
        p05, lo = [], []
        for path, val in _walk(face):
            if not isinstance(val, (int, float)) or isinstance(val, bool):
                continue
            if path.endswith("/p05"):
                p05.append({"path": path, "value": float(val)})
            elif path.endswith("/range/[]") and path.count("/range/[]") == 1:
                # a published multiplier range: [lo, hi] under a /range key, first element only
                lo.append({"path": path, "value": float(val)})
        if not p05 and not lo:
            continue
        q = [r["value"] for r in p05]
        l = [r["value"] for r in lo]
        per_face.append({
            "face": name,
            "n_p05": len(q),
            "n_range_lo": len(l),
            "p05_min": min(q) if q else None,
            "p05_max": max(q) if q else None,
            "p05_below_one": sum(1 for v in q if v < 1.0 - 1e-12),
            "p05_exactly_one": sum(1 for v in q if abs(v - 1.0) <= 1e-12),
            "range_lo_below_one": sum(1 for v in l if v < 1.0 - 1e-12),
        })
        for r in p05:
            r["face"] = name
            r["kind"] = "p05"
            ledger.append(r)
        for r in lo:
            r["face"] = name
            r["kind"] = "range_lo"
            ledger.append(r)
    values = [r["value"] for r in ledger]
    totals = {
        "faces_with_multiplier_numbers": sum(1 for x in per_face if x.get("n_p05") or
                                            x.get("n_range_lo")),
        "faces_walked": len([x for x in per_face if not x.get("error")]),
        "n_ledger": len(ledger),
        "n_p05": sum(1 for r in ledger if r["kind"] == "p05"),
        "n_range_lo": sum(1 for r in ledger if r["kind"] == "range_lo"),
        "min": min(values) if values else None,
        "max": max(values) if values else None,
        "below_one": sum(1 for v in values if v < 1.0 - 1e-12),
        "exactly_one": sum(1 for v in values if abs(v - 1.0) <= 1e-12),
    }
    return {"per_face": per_face, "ledger": ledger, "totals": totals, "mirrors_excluded": mirrors}


# ------------------------------------------------------------------ B / C: published mechanisms
def draw_exponent_null(draw=None, near1=None):
    """The endpoint's measured draw exponent and the published exact-1.0 mass, read off faces."""
    draw = draw or {}
    tables = draw.get("tables") or {}
    conv = ((draw.get("secondary_reads") or {}).get("endpoint_convergence") or {})
    out = {"families": {}}
    for fam in sorted(tables):
        t = tables[fam] or {}
        c = conv.get(fam) or {}
        out["families"][fam] = {
            "gamma": t.get("gamma_at_main"),
            "r2": t.get("r2_at_main"),
            "rungs": c.get("rungs"),
            "rungs_that_rose": c.get("rungs_that_rose"),
            "min_rise_pct": c.get("min_rise_pct"),
            "median_rise_pct": c.get("median_rise_pct"),
            "never_narrowed": (c.get("rows_never_narrowed") if "rows_never_narrowed" in c
                               else (c.get("min_rise_pct") is not None
                                     and float(c["min_rise_pct"]) >= 0.0)),
        }
    gammas = [v["gamma"] for v in out["families"].values() if v.get("gamma") is not None]
    out["gammas_positive"] = bool(gammas) and all(g > 0 for g in gammas)
    out["gamma_min"] = min(gammas) if gammas else None
    out["gamma_max"] = max(gammas) if gammas else None
    out["any_family_narrowed"] = any(v.get("never_narrowed") is False
                                     for v in out["families"].values())
    rows = (near1 or {}).get("floor_rows") or []
    lifts = [r.get("p05_without_near_one") for r in rows
             if isinstance(r.get("p05"), (int, float)) and r.get("p05_without_near_one") is not None]
    out["degenerate_branch"] = {
        "face": SRC_NEAR1,
        "rows_at_the_floor": len(rows),
        "lift_min": min(lifts) if lifts else None,
        "lift_max": max(lifts) if lifts else None,
        "reading": ("every exact-1.0 row on BANDNEAR1 is ONE seed away from a multiplier above 1, "
                    "so those ones are the degenerate branch, not a window that narrowed and "
                    "then stopped" if lifts else "no published floor row carries a lift"),
    }
    fb = (draw.get("_flipbudget") or {})
    out["published_tight_reach"] = {
        "face": SRC_FLIPBUDGET,
        "reachable_tight_indices": fb.get("reachable_tight_indices"),
        "rows_measured": fb.get("rows_measured"),
        "rows_flip_needs_narrowing": fb.get("rows_flip_needs_narrowing"),
        "p05_floor": fb.get("published_p05_floor"),
    }
    return out


def synthetic_stream(n=200, seed=20261031):
    """A deterministic draws stream with a negative extreme -- the branch the family runs on."""
    import random
    rng = random.Random(seed)
    return [rng.gauss(-0.46, 0.30) for _ in range(int(n))]


def late_extreme_stream(n=240, base=60, seed=20261031):
    """Same stream shape, but the deepest draw arrives AFTER the base prefix.

    The synthetic gaussian can put its minimum inside the first `base` draws, in which case the
    endpoint does not move at all and m is exactly 1 (the degenerate branch the family publishes).
    This stream forces the other case so strictness can be asserted separately from degeneracy.
    """
    s = synthetic_stream(n, seed=seed)
    s[base + 40] = min(s) - 1.0
    return s


def percentile_lo(vals, pct):
    """The same interpolation e251._band uses, so the counterfactual is the family's own rule."""
    vals = sorted(float(v) for v in vals)
    if len(vals) < 2:
        return None
    lo = vals[int(__import__("math").floor(pct / 100.0 * (len(vals) - 1)))]
    return float(lo)


def counterfactual(stream, base=60, top=240, pct=5.0):
    """Same stream, percentile band instead of full range: does m ever fall below 1?"""
    lo_base = abs(percentile_lo(stream[:base], pct) or 0.0)
    lo_top = abs(percentile_lo(stream[:top], pct) or 0.0)
    m = multiplier(lo_top, lo_base)
    ext_base = prefix_edge(stream, base)
    ext_top = prefix_edge(stream, top)
    return {"band_pct": pct, "lo_base": lo_base, "lo_top": lo_top, "multiplier": m,
            "extremum_multiplier": multiplier(ext_top, ext_base)}


# ------------------------------------------------------------------ assembly
def verdict_of(build, expon, totals):
    if totals["below_one"] > 0:
        return ("tight_end_is_a_property_of_these_windows",
                "%d of %d published multiplier lower ends sit below 1.0, so the tight tail does "
                "move on part of the family and the inert reading is a window property"
                % (totals["below_one"], totals["n_ledger"]))
    if not build.get("full_draw_range") or not build.get("lo_is_the_lowest_draw"):
        return ("tight_end_is_construction_limited_and_windows_not_yet_tested",
                "the published band is a percentile cut, so a growing sample can move it either "
                "way and the zeros E272 measured are not decidable from the build")
    if not expon.get("gammas_positive"):
        return ("tight_end_is_construction_limited_and_windows_not_yet_tested",
                "the band is an extremum of a nested prefix, but no published positive draw "
                "exponent is on disk, so 'the endpoint only widens' is asserted, not measured")
    return ("tight_end_dead_by_construction_family_should_stop_publishing_tight_pass_checks",
            "lo is the MINIMUM of a nested prefix (BAND_PCT 0..100) and the endpoint's draw "
            "exponent is positive on every published family (gamma %s), so the lower endpoint only "
            "moves outward and m = |lo|(top)/|lo|(base) cannot go below 1 unless every draw were "
            "positive -- which never happens on this population (%d published lower ends, all "
            ">= 1.0, %d exactly 1.0).  The exact ones are the degenerate branch, not a window that "
            "narrowed and stopped: one seed away they lift to %s.  A tight-pass check on this "
            "family can therefore only ever return zero"
            % ("%.3f..%.3f" % (expon["gamma_min"], expon["gamma_max"]),
               totals["n_ledger"], totals["exactly_one"],
               ("%.2f..%.2f" % (expon["degenerate_branch"]["lift_min"],
                                expon["degenerate_branch"]["lift_max"]))
               if expon["degenerate_branch"]["lift_min"] is not None else "-"))


def summary_of(census_rec, build, expon, cf):
    t = census_rec["totals"]
    return {
        "published_lower_ends": t["n_ledger"],
        "published_p05": t["n_p05"],
        "faces_with_multiplier_numbers": t["faces_with_multiplier_numbers"],
        "below_one": t["below_one"],
        "exactly_one": t["exactly_one"],
        "min": t["min"],
        "max": t["max"],
        "band_pct": build["band_pct"],
        "full_draw_range": build["full_draw_range"],
        "lo_is_the_lowest_draw": build["lo_is_the_lowest_draw"],
        "gamma_min": expon["gamma_min"],
        "gamma_max": expon["gamma_max"],
        "gammas_positive": expon["gammas_positive"],
        "any_family_narrowed": expon["any_family_narrowed"],
        "degenerate_rows": expon["degenerate_branch"]["rows_at_the_floor"],
        "tight_reach": expon["published_tight_reach"]["reachable_tight_indices"],
        "tight_rows_measured": expon["published_tight_reach"]["rows_measured"],
        "counterfactual_pct_multiplier": cf["multiplier"],
        "counterfactual_extremum_multiplier": cf["extremum_multiplier"],
        "counterfactual_breaks_the_floor": bool(cf["multiplier"] is not None
                                                and cf["multiplier"] < 1.0),
    }


def run(save=True, outdir=None):
    cen = census(outdir)
    build = band_build()
    draw = load(SRC_DRAW)
    near1 = load(SRC_NEAR1)
    fb = load(SRC_FLIPBUDGET)
    draw = dict(draw)
    draw["_flipbudget"] = fb.get("summary") or {}
    expon = draw_exponent_null(draw, near1)
    stream = synthetic_stream()
    cf = counterfactual(stream)
    s = summary_of(cen, build, expon, cf)
    verdict, why = verdict_of(build, expon, cen["totals"])
    s["verdict"] = verdict
    out = {
        "study": "e277_tight_multiplier_floor",
        "title": ("is 'the tight end never narrows' a property of these windows or of how a band "
                  "is built?"),
        "evidence_cutoff": CUTOFF,
        "generated": _stamp(),
        "source_faces": [SRC_DRAW, SRC_NEAR1, SRC_FLIPBUDGET],
        "source_code": SRC_BAND,
        "frozen_spec": {
            "design": ("census every published multiplier lower end on the BAND* family and read "
                       "the band build (percentile + which end lo takes) off the source"),
            "no_new_draws": ("no shuffle stream is drawn from the panel; the counterfactual runs on "
                             "a fixed synthetic stream whose seed is frozen below"),
            "synthetic_seed": 20261031,
            "branch_disclosure": ("the claim holds only where the endpoint's extreme is on the "
                                  "negative side; if every draw were positive |min| would shrink "
                                  "and m < 1 would be reachable -- published as a branch, not "
                                  "assumed away"),
            "why_not_min_max": ("a range over three seeds cannot answer this: p05 interpolates "
                                "inside the seed sample, so the floor can sit at exactly 1.0 "
                                "without any seed having narrowed"),
        },
        "band_build": build,
        "published_draw_exponent": expon,
        "counterfactual_percentile_band": cf,
        "census": cen["per_face"],
        "mirrors_excluded": cen["mirrors_excluded"],
        "ledger_sample": [{"face": r["face"], "kind": r["kind"], "path": r["path"],
                           "value": r["value"]} for r in cen["ledger"][:32]],
        "summary": s,
        "verdict": verdict,
        "verdict_reason": why,
        "no_bill": "descriptive census over published faces; no trial, no ledger booking",
    }
    if save:
        _write(out, outdir)
    return out


def _stamp():
    import datetime
    return datetime.datetime.now().strftime("%Y-%m-%dT%H:%M:%S%z")


def _write(face, outdir=None):
    outdir = outdir or OUTDIR
    if not os.path.isdir(outdir):
        os.makedirs(outdir)
    text = json.dumps(face, ensure_ascii=False, indent=1, sort_keys=True)
    for name in (FACE, LATEST):
        with io.open(os.path.join(outdir, name), "w", encoding="utf-8", newline="\n") as fh:
            fh.write(text + "\n")


def verify(outdir=None):
    outdir = outdir or OUTDIR
    path = os.path.join(outdir, FACE)
    if not os.path.exists(path):
        return ["no published face at %s" % path]
    with io.open(path, encoding="utf-8") as fh:
        got = json.load(fh)
    fresh = run(save=False, outdir=outdir)
    problems = []
    for key in sorted(set(got) | set(fresh)):
        if key == "generated":
            continue
        if got.get(key) != fresh.get(key):
            problems.append("%s does not re-derive" % key)
    return problems


# ------------------------------------------------------------------ selftest
def _leg(ok, name, detail=None):
    return {"leg": name, "ok": bool(ok), "detail": detail}


def selftest():
    legs = []

    # --- A: the band build, read off the source ----------------------------------------
    build = band_build()
    legs.append(_leg(build["band_pct"] == [0.0, 100.0],
                     "the published band is the full draw range", build["band_pct"]))
    legs.append(_leg(build["lo_is_the_lowest_draw"],
                     "lo is read off the lowest draw (an extremum, not a percentile cut)"))
    legs.append(_leg(build["full_draw_range"] and build["lo_is_the_lowest_draw"],
                     "so the endpoint is an extremum of a growing nested sample"))

    # --- A: the monotone branch, on a stream the family actually runs on ----------------
    stream = synthetic_stream()
    lo_base, lo_top = prefix_edge(stream, 60), prefix_edge(stream, 240)
    m = multiplier(lo_top, lo_base)
    legs.append(_leg(endpoint_branch(stream) == NEGATIVE_EXTREME,
                     "the synthetic stream sits on the negative-extreme branch",
                     endpoint_branch(stream)))
    legs.append(_leg(lo_top >= lo_base and m >= 1.0,
                     "a nested prefix can only widen |lo|: m >= 1", (lo_base, lo_top, m)))
    # the same statement at every cut, not just the two ends
    cuts = [30, 60, 120, 240, 400]
    edges = [prefix_edge(stream, c) for c in cuts]
    legs.append(_leg(all(b >= a for a, b in zip(edges, edges[1:])),
                     "|lo| is non-decreasing across EVERY cut", edges))
    late = late_extreme_stream()
    m_late = multiplier(prefix_edge(late, 240), prefix_edge(late, 60))
    legs.append(_leg(m_late is not None and m_late > 1.0,
                     "a draw that arrives AFTER the base prefix moves the endpoint strictly",
                     m_late))

    # --- the branch that would allow narrowing, published not assumed ------------------
    positive = [abs(v) + 1e-9 for v in stream]
    legs.append(_leg(endpoint_branch(positive) == POSITIVE_EXTREME,
                     "an all-positive stream is the other branch"))
    legs.append(_leg(multiplier(prefix_edge(positive, 240), prefix_edge(positive, 60)) <= 1.0,
                     "on the positive branch |lo| shrinks, so m <= 1 is reachable",
                     multiplier(prefix_edge(positive, 240), prefix_edge(positive, 60))))

    # --- the counterfactual: a percentile band DOES narrow on the same stream ----------
    cf = counterfactual(stream)
    legs.append(_leg(cf["multiplier"] is not None and cf["multiplier"] < 1.0,
                     "a 5% band on the same stream produces m < 1", cf["multiplier"]))
    legs.append(_leg(cf["extremum_multiplier"] >= 1.0,
                     "while the extremum band on the same stream does not",
                     cf["extremum_multiplier"]))
    legs.append(_leg(percentile_lo(stream[:60], 0.0) == min(stream[:60]),
                     "at pct 0 the percentile band IS the extremum (the family's own rule)"))

    # --- C: the exact-1.0 rows are degenerate, not narrowed ----------------------------
    near1 = load(SRC_NEAR1)
    expon = draw_exponent_null(load(SRC_DRAW), near1)
    legs.append(_leg(expon["gammas_positive"],
                     "every published draw exponent is positive", expon["gamma_min"]))
    legs.append(_leg(not expon["any_family_narrowed"],
                     "no published family narrowed its endpoint across rungs"))
    d = expon["degenerate_branch"]
    legs.append(_leg(d["rows_at_the_floor"] == 0 or
                     (d["lift_min"] is not None and d["lift_min"] > 1.0),
                     "every published exact-1.0 row lifts above 1 when one seed is dropped",
                     (d["lift_min"], d["lift_max"])))

    # --- census mechanics --------------------------------------------------------------
    cen = census()
    t = cen["totals"]
    legs.append(_leg(t["n_p05"] == sum(x.get("n_p05") or 0 for x in cen["per_face"]),
                     "per-face p05 counts sum to the ledger", t["n_p05"]))
    legs.append(_leg(all(x["p05_min"] is None or x["p05_min"] >= 1.0 - 1e-12
                         for x in cen["per_face"]),
                     "no published face carries a p05 below 1.0"))
    legs.append(_leg(t["exactly_one"] >=
                     sum(x.get("p05_exactly_one") or 0 for x in cen["per_face"]),
                     "the exact-1.0 count is at least the per-face sum", t["exactly_one"]))
    legs.append(_leg(len([x for x in cen["per_face"] if x.get("error")]) == 0,
                     "every BAND* face on disk parsed"))

    # --- live legs ---------------------------------------------------------------------
    live = run(save=False)
    legs.append(_leg(live["summary"]["verdict"] ==
                     "tight_end_dead_by_construction_family_should_stop_publishing_tight_pass_checks",
                     "live: the census reads dead-by-construction", live["summary"]["verdict"]))
    legs.append(_leg(live["summary"]["below_one"] == 0,
                     "live: not one published lower end sits below 1.0"))
    legs.append(_leg(live["summary"]["counterfactual_breaks_the_floor"] is True,
                     "live: the counterfactual does break the floor, so the build is the cause"))
    legs.append(_leg(live["summary"]["tight_reach"] == [] and
                     live["summary"]["tight_rows_measured"] > 0,
                     "live: the published tight tail reached nothing on a non-empty population",
                     (live["summary"]["tight_reach"],
                      live["summary"]["tight_rows_measured"])))

    ok = all(x["ok"] for x in legs)
    print("selftest %d/%d %s" % (sum(1 for x in legs if x["ok"]), len(legs),
                                 "PASS" if ok else "FAIL"))
    for x in legs:
        if not x["ok"]:
            print("  FAIL %s %s" % (x["leg"], x.get("detail")))
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
        print("  published lower ends=%d (p05=%d) below_one=%d exactly_one=%d min=%s"
              % (s["published_lower_ends"], s["published_p05"], s["below_one"],
                 s["exactly_one"], s["min"]))
        print("  band_pct=%s full_range=%s lo_is_min=%s | gammas %s..%s positive=%s"
              % (s["band_pct"], s["full_draw_range"], s["lo_is_the_lowest_draw"],
                 s["gamma_min"], s["gamma_max"], s["gammas_positive"]))
        print("  counterfactual: extremum m=%.4f | p5 band m=%s"
              % (s["counterfactual_extremum_multiplier"],
                 ("%.4f" % s["counterfactual_pct_multiplier"])
                 if s["counterfactual_pct_multiplier"] is not None else "-"))
        for x in face["census"]:
            print("  %-34s p05=%-3d lo=%-3d min=%-8s below1=%d eq1=%d"
                  % (x["face"], x["n_p05"], x["n_range_lo"],
                     ("%.6f" % x["p05_min"]) if x["p05_min"] is not None else "-",
                     x["p05_below_one"], x["p05_exactly_one"]))
        return 0
    print("usage: e277_tight_multiplier_floor.py [run|verify|selftest]")
    return 2


if __name__ == "__main__":
    sys.exit(main())