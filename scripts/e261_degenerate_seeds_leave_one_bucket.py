#!/usr/bin/env python3
"""E261 -- how much of each published band interval is the endpoint-already-attained bucket?

E259 published 52 of 640 per-seed multipliers reading EXACTLY one, and those seeds dragged p05 down
to 1.000 in 14 of its 16 arms. E259 published that degeneracy honestly but left the obvious
follow-up unasked: if you take the bucket out, does the interval move a little (the floor is
structural -- the multiplier genuinely cannot go below one on this design) or a lot (the floor was
the bucket -- the "band can only widen" statement was carried by the seeds whose endpoint had
already stopped moving)?

This face answers only that, and it adds no draws. It reads the per-seed multiplier tables E259
already published -- 4 windows x 2 published base counts x 2 legs x 40 seeds -- and publishes both
readings side by side:

    full      [p05, p95] over all 40 seeds                    (= E259, bit-for-bit)
    trimmed   [p05, p95] over the seeds still free to move    (= the bucket removed)

with the width each one carries, the share of the width the bucket accounts for, and whether the
lower end leaves 1.0 once the bucket is gone.

THE HONEST CAVEAT, published on the face rather than in this docstring: removing the attained bucket
is a SELECTION ON THE SAMPLE'S OWN MINIMUM. The trimmed interval is narrower by construction and it
answers a different question -- "how far can the band still move" -- than the full interval, which
answers "where does it land". The trimmed interval is therefore NOT a better band and NOT something
to bill against; it is the decomposition that says which of the two sentences a published interval
is actually making. Any row that reads outside under the tighter interval reads outside MORE easily,
so a newly-outside row is the direction of the edit, not a finding about the strategy.

A SECOND DEFECT SURFACES WHILE DOING THIS (published as its own block, not folded into the headline):
E259 re-judged every published row against the arm keyed `self:<base>`, so the 8 rows that name the
cross arm -- the 4 `cross` rows and the 4 `star_lag1_residual` rows, whose published coefficient is
the cross coefficient -- were judged against the self interval. That is the same "a lookup keyed
more coarsely than the arm it claims to read silently returns another arm" pit E259 recorded against
E258, recurring one level down. This face re-judges every row on the leg its own coefficient
identifies and publishes both answers, so the reader can see whether any verdict actually moved.

NO BILL, NO ADOPTION, NO RE-PRICING: measurement only, on an already-published face.
"""

from __future__ import annotations

import argparse
import io
import json
import os
import statistics
import sys
from datetime import datetime

HERE = os.path.dirname(os.path.abspath(__file__))
if HERE not in sys.path:
    sys.path.insert(0, HERE)

import e257_band_at_top_flips as e257  # noqa: E402
import e259_band_multiplier_distribution as e259  # noqa: E402

ROOT = e259.ROOT
OUTDIR = os.path.join(ROOT, "results", "state_tilt")

STUDY = "E261_degenerate_seeds_leave_one_bucket"
CUTOFF = "2026-10-29"
FACE = "BANDBUCKET-%s.json" % CUTOFF
SRC_FACE = "BANDWINDIST-%s.json" % CUTOFF

LEGS = ("self", "cross")
ATTAIN_TOL = e259.ATTAIN_TOL if hasattr(e259, "ATTAIN_TOL") else 1e-12
MATERIAL_DROP = 0.05      # frozen: a width drop of >= 5% of the full width is "material"
MIN_KEPT = 5              # frozen: below this the trimmed interval is not published at all
BASE_DEFAULT = 200        # E259's own rule for a row with no band_draws
ROW_LEG_BY_NAME = {"self": "self", "cross": "cross"}   # star_lag1_residual resolves by coefficient

TITLE = "how much of each interval width is the endpoint-attained bucket?"

VERDICT_VOCAB = (
    "floor_at_one_is_the_attained_bucket",
    "floor_at_one_is_structural",
    "floor_at_one_is_part_regime",
    "no_floor_to_decompose",
    "no_windows_measured",
)

NO_BILL = ("measurement only: the per-seed multiplier tables E259 already published are re-read to "
           "split each interval into the endpoint-attained bucket and the seeds still free to move; "
           "no draw is added, no coefficient is re-priced, nothing is adopted")


# ------------------------------------------------------------------ io
def _p(name):
    return os.path.join(OUTDIR, name)


def load(name):
    with io.open(_p(name), encoding="utf-8") as fh:
        return json.load(fh)


def _try_load(name):
    try:
        return load(name)
    except FileNotFoundError:
        return None


def source_face(outdir=None):
    return _try_load(SRC_FACE)


# ------------------------------------------------------------------ the bucket
def is_attained(m):
    """A multiplier of one means the band's lower endpoint never moved after the base prefix.

    E259's exact rule (abs(m - 1.0) <= 1e-12) is reused rather than re-invented: one published seed
    reads 0.9999999999999999, so an equality test would silently disagree with the count E259
    published beside the same interval.
    """
    return m is not None and abs(float(m) - 1.0) <= ATTAIN_TOL


def bucket_split(vals):
    vals = [float(v) for v in (vals or []) if v is not None]
    attained = [v for v in vals if is_attained(v)]
    kept = [v for v in vals if not is_attained(v)]
    return attained, kept


def _iv(values):
    q = e259.quantiles(values)
    return {"p05": q["p05"], "p95": q["p95"], "median": q["p50"],
            "interval": [q["p05"], q["p95"]], "width": (q["p95"] - q["p05"])}


def arm_record(cell, arm, rec):
    """One (window, base count, leg): the full interval and the same interval without the bucket."""
    vals = [float(v) for v in (rec.get("seed_multipliers") or [])]
    attained, kept = bucket_split(vals)
    full = _iv(vals) if len(vals) >= 2 else None
    out = {
        "cell": cell,
        "arm": arm,
        "leg": rec.get("leg"),
        "base_draws": rec.get("base_draws"),
        "top_draws": rec.get("top_draws"),
        "n_seeds": len(vals),
        "n_attained": len(attained),
        "n_kept": len(kept),
        "e259_n_endpoint_already_attained": rec.get("n_endpoint_already_attained"),
        "attained_count_matches_e259": (len(attained) == rec.get("n_endpoint_already_attained")),
        "e259_interval": rec.get("interval"),
        "e259_interval_width": rec.get("interval_width"),
        "full": full,
        "reproduces_e259_interval": (full is not None and full["interval"] == rec.get("interval")),
        "reproduces_e259_width": (full is not None
                                  and full["width"] == rec.get("interval_width")),
        "attained_values": attained,
        "kept_min": (min(kept) if kept else None),
        "kept_max": (max(kept) if kept else None),
    }
    if out["full"] is None:
        out.update({"trimmed": None, "trimmed_reason": "fewer than two seeds in the arm"})
        return out
    if len(kept) < MIN_KEPT:
        out.update({"trimmed": None,
                    "trimmed_reason": ("only %d of %d seeds are still free to move (floor %d); "
                                       "the trimmed interval is not published"
                                       % (len(kept), len(vals), MIN_KEPT))})
        return out
    trimmed = _iv(kept)
    drop = out["full"]["width"] - trimmed["width"]
    out.update({
        "trimmed": trimmed,
        "width_delta": drop,
        "width_drop_share": (drop / out["full"]["width"]) if out["full"]["width"] else None,
        "width_retained_share": (trimmed["width"] / out["full"]["width"]
                                 if out["full"]["width"] else None),
        "material": (bool(out["full"]["width"])
                     and (drop / out["full"]["width"]) >= MATERIAL_DROP),
        "floor_at_one": out["full"]["interval"][0] <= 1.0 + ATTAIN_TOL,
        # names the MOVE, not the position: an arm whose full interval already starts above one has
        # no floor to move, so it must never be counted as one that did (the first draft of this
        # field said `floor_lifted` and counted 16 of 16, twice the 8 arms that have a floor).
        "floor_moved_off_one": (out["full"]["interval"][0] <= 1.0 + ATTAIN_TOL
                                and trimmed["interval"][0] > 1.0 + ATTAIN_TOL),
        "lo_shift": trimmed["interval"][0] - out["full"]["interval"][0],
        "hi_shift": trimmed["interval"][1] - out["full"]["interval"][1],
        "median_shift": (trimmed["median"] - out["full"]["median"]),
    })
    return out


def arms_of(face):
    out = []
    for cell in sorted((face.get("windows") or {})):
        table = face["windows"][cell] or {}
        for arm in sorted(table):
            out.append(arm_record(cell, arm, table[arm] or {}))
    return out


def floor_by_base(arms):
    """Where the floor at one actually lives, keyed by the published base draw count.

    This cross-tab is published rather than left to the reader. A floor that concentrates in one
    base count is a statement about ARRIVAL, not about the stream's lower bound: more draws means
    more endpoints have already arrived, and an arrived endpoint reports a multiplier of exactly
    one. The counts are published as measured -- an earlier draft of this docstring said "every
    floored arm sits at the larger base count", and the face then measured 7 of 8 at base 200 with
    one at base 60, so the sentence is the counts and not the expectation.
    """
    out = {}
    for a in arms:
        if not a.get("trimmed"):
            continue
        key = str(int(float(a.get("base_draws") or BASE_DEFAULT)))
        rec = out.setdefault(key, {"arms": 0, "arms_with_floor": 0, "arms_floor_moved": 0})
        rec["arms"] += 1
        rec["arms_with_floor"] += 1 if a.get("floor_at_one") else 0
        rec["arms_floor_moved"] += 1 if a.get("floor_moved_off_one") else 0
    return out


def arms_missing(face):
    """Windows E259 reported as skipped, carried verbatim so an absent arm is not a silent zero."""
    out = []
    for rec in (face.get("windows_skipped") or []):
        if isinstance(rec, dict):
            out.append(rec)
        else:
            out.append({"cell": rec, "reason": None})
    return sorted(out, key=lambda r: str(r.get("cell")))


# ------------------------------------------------------------------ row re-judging
def _judge(b, lo, hi, iv, median_m):
    ends = {}
    for name, m in (("tight", iv[0]), ("median", median_m), ("wide", iv[1])):
        slo, shi = e257.scale_band(lo, hi, m)
        outs = e257.outside(b, slo, shi)
        ends[name] = {"multiplier": m, "outside": outs,
                      "margin": (abs(b) / max(abs(slo), abs(shi))
                                 if max(abs(slo), abs(shi)) else None)}
    verdicts = {k: ("outside" if v["outside"] else "inside") if v["outside"] is not None
                else "unjudgeable" for k, v in ends.items()}
    distinct = set(verdicts.values())
    return {"ends": ends, "verdicts": verdicts,
            "same_at_every_end": len(distinct) == 1,
            "interval_dependent": len(distinct) > 1}


def resolve_leg(row, rows_by_cell):
    """Which arm does this row's own coefficient belong to?

    The row name decides for `self`/`cross`. `star_lag1_residual` carries no leg field anywhere in
    the upstream faces, so it is resolved by the coefficient it publishes: it is judged against the
    leg whose own row in the same cell publishes the same b. If both legs share b, the row is
    published as ambiguous rather than quietly assigned.
    """
    name = row.get("row")
    if name in ROW_LEG_BY_NAME:
        return ROW_LEG_BY_NAME[name], "row name"
    b = row.get("b")
    peers = rows_by_cell.get(row.get("cell")) or {}
    hits = [leg for leg in LEGS
            if b is not None and (peers.get(leg) or {}).get("b") is not None
            and abs((peers.get(leg) or {}).get("b") - b) <= 1e-12]
    if len(hits) == 1:
        return hits[0], "coefficient match"
    if len(hits) > 1:
        return "self", "ambiguous (both legs publish this b) -- read as self"
    return "self", "unresolved (no leg publishes this b) -- read as self"


def rows_of(face, arms):
    """Re-judge every published row on its own leg, at the full interval and the trimmed one."""
    by_arm = {(a["cell"], a["leg"], int(float(a["base_draws"] or BASE_DEFAULT))): a for a in arms}
    rows_by_cell = {}
    for r in (face.get("rows") or []):
        rows_by_cell.setdefault(r.get("cell"), {})[r.get("row")] = r

    out = []
    for r in (face.get("rows") or []):
        base = int(float(r.get("band_draws") or BASE_DEFAULT))
        leg, how = resolve_leg(r, rows_by_cell)
        arm = by_arm.get((r.get("cell"), leg, base))
        rec = {
            "cell": r.get("cell"), "row": r.get("row"), "b": r.get("b"),
            "band_draws": base, "sessions": r.get("sessions"),
            "leg_resolved": leg, "leg_resolution": how,
            "leg_e259_used": "self",
            "judged_on_the_named_leg_by_e259": (leg == "self"),
            "e259_published_interval": r.get("interval"),
            "e259_published_verdicts": {"tight": r.get("verdict_tight"),
                                        "median": r.get("verdict_median"),
                                        "wide": r.get("verdict_wide")},
        }
        if r.get("b") is None or r.get("band_lo") is None or r.get("band_hi") is None:
            rec.update({"verdict": "unjudgeable",
                        "reason": "row carries no coefficient or no band"})
            out.append(rec)
            continue
        if arm is None or arm.get("full") is None:
            rec.update({"verdict": "window_not_measured",
                        "reason": "no measured arm for %s/%s at base %d"
                                  % (r.get("cell"), leg, base)})
            out.append(rec)
            continue
        b, lo, hi = r["b"], r["band_lo"], r["band_hi"]
        full = _judge(b, lo, hi, arm["full"]["interval"], arm["full"]["median"])
        rec.update({
            "own_leg_interval_full": arm["full"]["interval"],
            "own_leg_interval_trimmed": (arm["trimmed"] or {}).get("interval"),
            "verdicts_full_own_leg": full["verdicts"],
            "interval_dependent_full_own_leg": full["interval_dependent"],
            "same_at_every_end_full_own_leg": full["same_at_every_end"],
            "same_verdict_as_e259": (full["verdicts"] == rec["e259_published_verdicts"]),
            "verdict": full["verdicts"]["median"],
        })
        if arm.get("trimmed"):
            trim = _judge(b, lo, hi, arm["trimmed"]["interval"], arm["trimmed"]["median"])
            rec.update({
                "verdicts_trimmed_own_leg": trim["verdicts"],
                "interval_dependent_trimmed_own_leg": trim["interval_dependent"],
                "same_verdict_as_full": (trim["verdicts"] == full["verdicts"]),
                "outside_becomes_easier": (trim["verdicts"]["tight"] == "outside"
                                           and full["verdicts"]["tight"] != "outside"),
            })
        else:
            rec.update({"verdicts_trimmed_own_leg": None,
                        "verdicts_trimmed_reason": arm.get("trimmed_reason")})
        out.append(rec)
    return out


# ------------------------------------------------------------------ verdicts
def _base_clause(arms):
    """One sentence on how the floor is distributed across published base counts, or nothing."""
    fb = floor_by_base(arms)
    keys = [k for k in sorted(fb, key=lambda k: int(float(k))) if fb[k]["arms_with_floor"]]
    if len(keys) < 2:
        return ""
    parts = ["%d of %d at base %s" % (fb[k]["arms_with_floor"], fb[k]["arms"], k) for k in keys]
    return (" (the floor is not spread evenly across the published base counts: %s, and the "
            "larger-count arm is the direction E260's arrival result predicts -- more draws means "
            "more endpoints have already arrived)" % ", ".join(parts))


def bucket_verdict(arms):
    live = [a for a in arms if a.get("trimmed") and a.get("floor_at_one")]
    if not arms:
        return "no_windows_measured", "E259's BANDWINDIST face is absent; there is no interval to split"
    if not live:
        return ("no_floor_to_decompose",
                "no measured arm carries a lower interval end at one, so there is no attained "
                "bucket to decompose")
    lifted = [a for a in live if a.get("floor_moved_off_one")]
    drops = [a["width_drop_share"] for a in live if a.get("width_drop_share") is not None]
    med_drop = statistics.median(drops) if drops else None
    med_lift = statistics.median([a["lo_shift"] for a in lifted]) if lifted else None
    if len(lifted) == len(live):
        return ("floor_at_one_is_the_attained_bucket",
                "all %d arms whose lower end sits at one lift it once the attained bucket is removed "
                "(median lift %s, median %s%% of the width); the 'the band can only widen' floor "
                "was carried by the seeds whose endpoint had already stopped moving, not by the "
                "stream's own lower bound"
                % (len(live), (("%.4f" % med_lift) if med_lift is not None else "n/a"),
                   (("%.1f" % (100 * med_drop)) if med_drop is not None else "n/a")))
    if not lifted:
        return ("floor_at_one_is_structural",
                "none of the %d arms with a lower end at one lift it when the attained bucket is "
                "removed (median width change %s%%), so the floor is the stream's own bound and not "
                "an artefact of the degenerate seeds"
                % (len(live), (("%.1f" % (100 * med_drop)) if med_drop is not None else "n/a")))
    return ("floor_at_one_is_part_regime",
            "%d of %d arms with a lower end at one lift it when the attained bucket is removed and "
            "%d do not (median width drop %s%%): whether the floor is structural depends on the "
            "window, so a single family-level sentence is not available"
            % (len(lifted), len(live), len(live) - len(lifted),
               (("%.1f" % (100 * med_drop)) if med_drop is not None else "n/a")))


def leg_key_audit(rows):
    """E259 judged every row against the self arm; count how many rows name another leg."""
    judged = [r for r in rows if r.get("leg_resolved")]
    other = [r for r in judged if not r.get("judged_on_the_named_leg_by_e259")]
    other_judgeable = [r for r in other if r.get("verdicts_full_own_leg")]
    changed = [r for r in judged if r.get("same_verdict_as_e259") is False]
    ambiguous = [r for r in judged if "ambiguous" in (r.get("leg_resolution") or "")]
    return {
        "rows": len(rows),
        "rows_judged": len(judged),
        "rows_judged_on_a_leg_other_than_the_one_they_name": len(other),
        "rows_on_another_leg_that_carry_a_band": len(other_judgeable),
        "rows_on_another_leg": [{"cell": r.get("cell"), "row": r.get("row"),
                                 "leg_resolved": r.get("leg_resolved"),
                                 "leg_resolution": r.get("leg_resolution"),
                                 "verdict": r.get("verdict")} for r in other],
        "rows_whose_verdict_changes_on_their_own_leg": len(changed),
        "rows_leg_ambiguous": len(ambiguous),
        "rows_by_resolution": {how: sum(1 for r in judged if r.get("leg_resolution") == how)
                               for how in sorted({r.get("leg_resolution") for r in judged})},
        "pin": ("E259's rejudge reads the arm keyed self:<base> for every row, so the cross rows and "
                "the star_lag1_residual rows (whose coefficient is the cross coefficient) were "
                "judged against the self interval; this face re-judges each row on the leg its own "
                "coefficient identifies and publishes whether the verdict actually moved"),
        "verdict": ("row_leg_key_is_coarse_but_verdicts_survive" if not changed
                    else "row_leg_key_is_coarse_and_a_verdict_moves"),
    }


def trimming_verdict(rows):
    usable = [r for r in rows if r.get("verdicts_trimmed_own_leg")]
    changed = [r for r in usable
               if r.get("same_verdict_as_full") is False]
    easier = [r for r in usable if r.get("outside_becomes_easier")]
    return {
        "rows_with_a_trimmed_interval": len(usable),
        "rows_verdict_changes_under_trimming": len(changed),
        "rows_newly_outside_at_the_tight_end": len(easier),
        "direction": ("trimming removes the sample's own minimum, so the interval is narrower by "
                      "construction and 'outside' becomes easier -- a newly-outside row is the "
                      "direction of the edit, not a finding"),
        "verdict": ("no_row_verdict_depends_on_the_bucket" if not changed
                    else "a_row_verdict_depends_on_the_bucket"),
    }


# ------------------------------------------------------------------ run
def run(save=True, outdir=None):
    outdir = outdir or OUTDIR
    face = source_face()
    if face is None:
        out = {"study": STUDY, "title": TITLE, "evidence_cutoff": CUTOFF,
               "generated": datetime.now().isoformat(timespec="seconds"),
               "verdict": "no_windows_measured",
               "verdict_reason": "E259's %s is absent; no interval can be split" % SRC_FACE,
               "arms": [], "rows": [], "no_bill": NO_BILL}
        out["summary"] = _summary(out)
        if save:
            _write(out, outdir)
        return out

    arms = arms_of(face)
    rows = rows_of(face, arms)
    bv, bwhy = bucket_verdict(arms)
    bwhy = bwhy + _base_clause(arms)
    out = {
        "study": STUDY,
        "title": TITLE,
        "evidence_cutoff": face.get("evidence_cutoff") or CUTOFF,
        "generated": datetime.now().isoformat(timespec="seconds"),
        "frozen_spec": {
            "design": ("read E259's published per-seed multipliers and publish each interval twice: "
                       "over all seeds, and over the seeds whose band endpoint is still free to move"),
            "attained_rule": ("a multiplier within %g of one means the band's lower endpoint never "
                              "moved after the base draw count -- E259's own rule, reused" % ATTAIN_TOL),
            "quantile_rule": "E259's linear positions (n-1)*q, boundary-clamped",
            "material_drop_share": MATERIAL_DROP,
            "material_rule": "a width drop of at least this share of the full width is material",
            "min_kept_seeds": MIN_KEPT,
            "row_leg_rule": ("self/cross rows are read off their own named leg; star_lag1_residual "
                             "carries no leg in any upstream face and is resolved by the coefficient "
                             "it publishes, published as ambiguous when both legs share b"),
            "selection_caveat": ("removing the attained bucket selects on the sample's own minimum, "
                                 "so the trimmed interval is narrower by construction and answers "
                                 "'how far can the band still move', not 'where does it land'"),
            "source": "E259 windows per-seed multiplier tables -- no new draws, no new estimate",
        },
        "source_face": "results/state_tilt/%s" % SRC_FACE,
        "windows_measured": sorted((face.get("windows") or {})),
        "windows_skipped": arms_missing(face),
        "arms": arms,
        "floor_by_base": floor_by_base(arms),
        "rows": rows,
        "leg_key_audit": leg_key_audit(rows),
        "trimming": trimming_verdict(rows),
        "verdict": bv,
        "verdict_reason": bwhy,
        "no_bill": NO_BILL,
    }
    out["summary"] = _summary(out)
    if save:
        _write(out, outdir)
    return out


def _summary(face):
    arms = face.get("arms") or []
    live = [a for a in arms if a.get("trimmed")]
    drops = [a["width_drop_share"] for a in live if a.get("width_drop_share") is not None]
    shifts = [a["median_shift"] for a in live if a.get("median_shift") is not None]
    rows = face.get("rows") or []
    lk = face.get("leg_key_audit") or {}
    tr = face.get("trimming") or {}
    return {
        "arms": len(arms),
        "arms_with_a_trimmed_interval": len(live),
        "arms_attained_count_matches_e259": sum(1 for a in arms
                                                if a.get("attained_count_matches_e259")),
        "arms_reproduce_e259_interval": sum(1 for a in arms
                                            if a.get("reproduces_e259_interval")),
        "windows_measured": len(face.get("windows_measured") or []),
        "windows_skipped": len(face.get("windows_skipped") or []),
        "seeds": sum(a.get("n_seeds") or 0 for a in arms),
        "seeds_attained": sum(a.get("n_attained") or 0 for a in arms),
        "seeds_kept": sum(a.get("n_kept") or 0 for a in arms),
        "arms_with_floor_at_one": sum(1 for a in live if a.get("floor_at_one")),
        "arms_floor_moved_off_one": sum(1 for a in live if a.get("floor_moved_off_one")),
        "arms_material_width_drop": sum(1 for a in live if a.get("material")),
        "floor_by_base": face.get("floor_by_base"),
        "width_drop_share_median": statistics.median(drops) if drops else None,
        "width_drop_share_min": min(drops) if drops else None,
        "width_drop_share_max": max(drops) if drops else None,
        "median_shift_median": statistics.median(shifts) if shifts else None,
        "rows": len(rows),
        "rows_judged_on_a_leg_other_than_the_one_they_name":
            lk.get("rows_judged_on_a_leg_other_than_the_one_they_name"),
        "rows_whose_verdict_changes_on_their_own_leg":
            lk.get("rows_whose_verdict_changes_on_their_own_leg"),
        "rows_leg_ambiguous": lk.get("rows_leg_ambiguous"),
        "rows_verdict_changes_under_trimming": tr.get("rows_verdict_changes_under_trimming"),
        "rows_newly_outside_at_the_tight_end": tr.get("rows_newly_outside_at_the_tight_end"),
        "leg_key_verdict": lk.get("verdict"),
        "trimming_verdict": tr.get("verdict"),
    }


# ------------------------------------------------------------------ write / verify
def _write(face, outdir, tag=""):
    os.makedirs(outdir, exist_ok=True)
    path = os.path.join(outdir, "BANDBUCKET-%s%s.json" % (face.get("evidence_cutoff"), tag))
    text = json.dumps(face, ensure_ascii=False, indent=1, sort_keys=True)
    with io.open(path, "w", encoding="utf-8", newline="\n") as fh:
        fh.write(text + "\n")
    latest = os.path.join(outdir, "bandbucket_latest.json")
    with io.open(latest, "w", encoding="utf-8", newline="\n") as fh:
        fh.write(text + "\n")
    return path


def verify(outdir=None, tag=""):
    """Re-derive the published face from E259 and report every field that does not come back."""
    outdir = outdir or OUTDIR
    try:
        got = load("BANDBUCKET-%s%s.json" % (CUTOFF, tag))
    except FileNotFoundError:
        return ["no published face at %s" % os.path.join(outdir, "BANDBUCKET-%s%s.json"
                                                         % (CUTOFF, tag))]
    fresh = run(save=False)
    problems = []
    if got.get("verdict") != fresh.get("verdict"):
        problems.append("verdict published %r != %r" % (got.get("verdict"), fresh.get("verdict")))
    if got.get("verdict_reason") != fresh.get("verdict_reason"):
        problems.append("verdict_reason does not re-derive")
    if (got.get("summary") or {}) != (fresh.get("summary") or {}):
        problems.append("summary does not re-derive from the published face")
    if got.get("frozen_spec") != fresh.get("frozen_spec"):
        problems.append("frozen_spec does not re-derive")
    pa = {(a.get("cell"), a.get("arm")): a for a in (got.get("arms") or [])}
    fa = {(a.get("cell"), a.get("arm")): a for a in (fresh.get("arms") or [])}
    if set(pa) != set(fa):
        problems.append("arm set published %d != re-derived %d" % (len(pa), len(fa)))
    for k in sorted(set(pa) & set(fa)):
        for field in ("n_attained", "n_kept", "full", "trimmed", "floor_moved_off_one",
                      "floor_at_one", "material",
                      "width_drop_share", "median_shift", "reproduces_e259_interval"):
            if pa[k].get(field) != fa[k].get(field):
                problems.append("arm %s/%s: %s published %r != %r"
                                % (k[0], k[1], field, pa[k].get(field), fa[k].get(field)))
    pr = {(r.get("cell"), r.get("row")): r for r in (got.get("rows") or [])}
    fr = {(r.get("cell"), r.get("row")): r for r in (fresh.get("rows") or [])}
    if set(pr) != set(fr):
        problems.append("row set published %d != re-derived %d" % (len(pr), len(fr)))
    for k in sorted(set(pr) & set(fr)):
        for field in ("leg_resolved", "verdicts_full_own_leg", "verdicts_trimmed_own_leg",
                      "same_verdict_as_e259", "own_leg_interval_full"):
            if pr[k].get(field) != fr[k].get(field):
                problems.append("row %s/%s: %s published %r != %r"
                                % (k[0], k[1], field, pr[k].get(field), fr[k].get(field)))
    for block in ("leg_key_audit", "trimming"):
        if (got.get(block) or {}).get("verdict") != (fresh.get(block) or {}).get("verdict"):
            problems.append("%s verdict does not re-derive" % block)
    return problems


# ------------------------------------------------------------------ selftest
def _leg(ok, name, detail=None):
    return {"leg": name, "ok": bool(ok), "detail": detail}


def _arm(vals, **kw):
    rec = {"seed_multipliers": list(vals), "leg": "self", "base_draws": 60, "top_draws": 1920,
           "n_endpoint_already_attained": sum(1 for v in vals if is_attained(v)),
           "interval": None, "interval_width": None}
    iv = _iv(vals) if len(vals) >= 2 else None
    if iv:
        rec["interval"] = iv["interval"]
        rec["interval_width"] = iv["width"]
    rec.update(kw)
    return rec


def selftest():
    legs = []

    # --- the attained rule is E259's, tolerance included
    legs.append(_leg(is_attained(1.0) and is_attained(0.9999999999999999),
                     "a multiplier of one and E259's 0.9999999999999999 both count as attained"))
    legs.append(_leg(not is_attained(1.0001) and not is_attained(0.999),
                     "1.0001 and 0.999 are not attained"))

    # --- split
    a, k = bucket_split([1.0, 1.05, 0.9999999999999999, 1.4])
    legs.append(_leg(len(a) == 2 and len(k) == 2, "the bucket splits 2/2 on the fixture", [a, k]))

    # --- a bucket that carries the whole floor: full interval starts at one, trimmed does not
    vals = [1.0] * 6 + [1.30, 1.35, 1.40, 1.50, 1.60, 1.70]
    rec = arm_record("fx", "self:60", _arm(vals))
    legs.append(_leg(rec["n_attained"] == 6 and rec["n_kept"] == 6, "fixture bucket is 6 of 12",
                     [rec["n_attained"], rec["n_kept"]]))
    legs.append(_leg(rec["full"]["interval"][0] == 1.0, "the full interval starts at one",
                     rec["full"]["interval"]))
    legs.append(_leg(rec["floor_at_one"] is True and rec["floor_moved_off_one"] is True,
                     "removing the bucket moves the floor off one"))
    legs.append(_leg(rec["width_drop_share"] > 0 and rec["material"] is True,
                     "removing the bucket narrows the interval materially",
                     rec["width_drop_share"]))
    legs.append(_leg(rec["median_shift"] > 0,
                     "removing a bucket at the bottom moves the median up", rec["median_shift"]))

    # --- a bucket that does NOT carry the floor: p05 sits above one even before the bucket goes,
    # because a single attained seed out of ten cannot reach the fifth percentile
    vals2 = [1.0, 1.02, 1.05, 1.08, 1.10, 1.12, 1.20, 1.30, 1.40, 1.50]
    rec2 = arm_record("fx", "self:60", _arm(vals2))
    legs.append(_leg(rec2["trimmed"]["interval"][0] > 1.0,
                     "the fixture's trimmed floor leaves one on its own", rec2["trimmed"]))
    # --- an arm whose full interval already starts above one has NO floor, so it must not be
    # counted as one whose floor moved -- the naming defect this file carries in its own history
    legs.append(_leg(rec2["floor_at_one"] is False and rec2["floor_moved_off_one"] is False,
                     "an arm without a floor is never counted as a floor that moved",
                     [rec2["floor_at_one"], rec2["floor_moved_off_one"]]))

    # --- too few kept seeds: trimmed is not published, and the reason is named
    vals3 = [1.0] * 9 + [1.10, 1.20]
    rec3 = arm_record("fx", "self:60", _arm(vals3))
    legs.append(_leg(rec3["trimmed"] is None and "still free to move" in rec3["trimmed_reason"],
                     "two free seeds out of eleven are published as no trimmed interval",
                     rec3.get("trimmed_reason")))

    # --- a two-seed arm does not produce a full interval either
    rec4 = arm_record("fx", "self:60", _arm([1.0]))
    legs.append(_leg(rec4["full"] is None and rec4["trimmed"] is None,
                     "a one-seed arm publishes no interval at all"))

    # --- reproducibility: the count must agree with what E259 published beside the interval
    rec5 = arm_record("fx", "self:60", _arm([1.0, 1.2, 1.3], n_endpoint_already_attained=5))
    legs.append(_leg(rec5["attained_count_matches_e259"] is False,
                     "a disagrees-with-E259 count is flagged, not silently accepted",
                     rec5["attained_count_matches_e259"]))

    # --- material threshold is a frozen share, not an absolute width
    small = [1.0, 1.0, 1.01, 1.02, 1.03, 1.04, 1.05]
    big = [1.0, 1.0, 1.20, 1.40, 1.55, 1.60, 1.80]
    legs.append(_leg(arm_record("fx", "self:60", _arm(small))["material"]
                     and arm_record("fx", "self:60", _arm(big))["material"],
                     "the material rule is a share, so both widths clear it"))

    # --- leg resolution
    peers = {"self": {"b": -0.20}, "cross": {"b": -0.49}}
    leg, how = resolve_leg({"row": "cross", "b": -0.49, "cell": "c"}, peers)
    legs.append(_leg(leg == "cross" and how == "row name",
                     "a row named cross is read off the cross arm", [leg, how]))
    leg2, how2 = resolve_leg({"row": "star_lag1_residual", "b": -0.49, "cell": "c"}, {"c": peers})
    legs.append(_leg(leg2 == "cross" and how2 == "coefficient match",
                     "a star_lag1 row follows the leg whose b it publishes", [leg2, how2]))
    leg3, how3 = resolve_leg({"row": "star_lag1_residual", "b": -0.99, "cell": "c"}, {"c": peers})
    legs.append(_leg(leg3 == "self" and "unresolved" in how3,
                     "a row with no matching b says so instead of guessing silently", [leg3, how3]))
    leg4, how4 = resolve_leg({"row": "star_lag1_residual", "b": -0.20, "cell": "c"},
                             {"c": {"self": {"b": -0.20}, "cross": {"b": -0.20}}})
    legs.append(_leg("ambiguous" in how4, "a b shared by both legs is published as ambiguous", how4))

    # --- row judging: an outside row stays outside when the interval narrows (the only direction)
    row = {"cell": "c", "row": "self", "b": -0.60, "band_lo": -0.25, "band_hi": 0.10,
           "band_draws": 60,
           "verdict_tight": "outside", "verdict_median": "outside", "verdict_wide": "outside"}
    arm = {"cell": "c", "leg": "self", "base_draws": 60.0,
           "full": {"interval": [1.0, 2.0], "median": 1.3, "width": 1.0},
           "trimmed": {"interval": [1.4, 1.9], "median": 1.6, "width": 0.5}}
    rr = rows_of({"rows": [row]}, [arm])[0]
    legs.append(_leg(rr["verdicts_full_own_leg"]["tight"] == "outside"
                     and rr["verdicts_full_own_leg"]["wide"] == "outside",
                     "an outside row reads outside at both ends of the full interval",
                     rr["verdicts_full_own_leg"]))
    legs.append(_leg(rr["leg_resolved"] == "self" and rr["judged_on_the_named_leg_by_e259"] is True,
                     "a self row was already judged on its own leg by E259", rr["leg_resolution"]))
    legs.append(_leg(rr["same_verdict_as_e259"] is True,
                     "a re-derivation that agrees with E259 says so", rr["same_verdict_as_e259"]))

    # --- a row whose band comes out inside at the wide end is interval-dependent, not flipped
    row2 = dict(row, b=-0.45)
    rr2 = rows_of({"rows": [row2]}, [arm])[0]
    legs.append(_leg(rr2["verdicts_full_own_leg"]["tight"] == "outside"
                     and rr2["verdicts_full_own_leg"]["wide"] == "inside"
                     and rr2["interval_dependent_full_own_leg"] is True,
                     "a row that changes at the wide end is interval-dependent",
                     rr2["verdicts_full_own_leg"]))

    # --- a row in a window E259 skipped is named, never silently zero
    row3 = {"cell": "pre2020_four", "row": "self", "b": -0.5, "band_lo": -0.3, "band_hi": 0.2}
    rr3 = rows_of({"rows": [row3]}, [])[0]
    legs.append(_leg(rr3["verdict"] == "window_not_measured",
                     "a row in an unmeasured window is published as such", rr3["verdict"]))

    # --- a row without a coefficient is unjudgeable, not inside
    row4 = {"cell": "c", "row": "self", "b": None, "band_lo": -0.3, "band_hi": 0.2}
    rr4 = rows_of({"rows": [row4]}, [arm])[0]
    legs.append(_leg(rr4["verdict"] == "unjudgeable",
                     "a row with no coefficient is unjudgeable", rr4["verdict"]))

    # --- verdicts on fixtures
    a_bucket = arm_record("fx", "self:60", _arm([1.0] * 6 + [1.3, 1.4, 1.5, 1.6, 1.7, 1.8]))
    v, _ = bucket_verdict([a_bucket])
    legs.append(_leg(v == "floor_at_one_is_the_attained_bucket",
                     "every floored arm lifting gives the attained-bucket verdict", v))
    a_struct = arm_record("fx", "self:60", _arm([1.01, 1.02, 1.04, 1.06, 1.08, 1.10]))
    v2, _ = bucket_verdict([a_struct])
    legs.append(_leg(v2 == "no_floor_to_decompose",
                     "an arm with no floor has nothing to decompose", v2))
    v3, _ = bucket_verdict([])
    legs.append(_leg(v3 == "no_windows_measured", "no arms at all is named, not zeroed", v3))

    # --- the floor cross-tab: a floor that lives in one base count is a statement about arrival
    a60 = arm_record("fx", "self:60", _arm([1.05, 1.10, 1.15, 1.20, 1.25, 1.30],
                                           base_draws=60))
    a200 = arm_record("fx", "self:200", _arm([1.0, 1.0, 1.05, 1.10, 1.15, 1.20, 1.25],
                                             base_draws=200))
    fb = floor_by_base([a60, a200])
    legs.append(_leg(fb["60"]["arms_with_floor"] == 0 and fb["200"]["arms_with_floor"] == 1,
                     "the cross-tab says which base count carries the floor", fb))
    # an arm that cannot support a trimmed interval is left out of the cross-tab rather than
    # counted with a floor it never measured
    legs.append(_leg(fb["60"]["arms"] == 1 and fb["200"]["arms"] == 1,
                     "the cross-tab only counts arms that carry a trimmed interval", fb))

    # --- trimming direction is published, so a newly-outside row cannot be read as a finding
    tr = trimming_verdict([rr, rr2])
    legs.append(_leg("direction" in tr and tr["rows_with_a_trimmed_interval"] >= 1,
                     "the trimming block publishes its direction", tr.get("direction")))
    lk = leg_key_audit([rr])
    legs.append(_leg(lk["rows_judged_on_a_leg_other_than_the_one_they_name"] == 0,
                     "a self-only row set has no coarse-key hits", lk))

    ok = all(r["ok"] for r in legs)
    return {"ok": ok, "legs": legs, "passed": sum(1 for r in legs if r["ok"]), "total": len(legs)}


# ------------------------------------------------------------------ cli
def main(argv=None):
    ap = argparse.ArgumentParser(description=TITLE)
    ap.add_argument("cmd", nargs="?", default="run",
                    choices=["run", "selftest", "verify", "summarize"])
    ap.add_argument("--outdir", default=None)
    ap.add_argument("--tag", default="")
    args = ap.parse_args(argv)
    if args.cmd == "selftest":
        res = selftest()
        for r in res["legs"]:
            print("%-4s %s" % ("ok" if r["ok"] else "FAIL", r["leg"]))
        print("selftest %d/%d" % (res["passed"], res["total"]))
        return 0 if res["ok"] else 1
    if args.cmd == "verify":
        problems = verify(outdir=args.outdir, tag=args.tag)
        for p in problems:
            print("PROBLEM %s" % p)
        print("verify %s (%d problems)" % ("OK" if not problems else "FAILED", len(problems)))
        return 0 if not problems else 1
    if args.cmd == "summarize":
        face = run(save=False)
        print(json.dumps(face.get("summary"), ensure_ascii=False, indent=1, sort_keys=True))
        print(face.get("verdict_reason"))
        return 0
    face = run(outdir=args.outdir)
    print(json.dumps(face.get("summary"), ensure_ascii=False, indent=1, sort_keys=True))
    print(face.get("verdict"))
    print(face.get("verdict_reason"))
    return 0


if __name__ == "__main__":
    sys.exit(main())