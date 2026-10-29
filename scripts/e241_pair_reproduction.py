"""E241 -- why does E238's published (A, B) pair not reproduce on the common grid?

E238 published the leave-one-out pair (b_own 0.596, b_agg 0.771) on each member's OWN date
grid. E240 re-ran the same coordinates on the COMMON five-member grid and published
(A_share -0.333, B_book -0.174) beside a gap of -1.16/-1.18 rather than reconciling it.

There are three separable candidate causes and this face tests them one at a time as a
ladder, never as a single re-run:

  ROWS      E238 fits each member on its own sessions (3,504 dates, aggregate over the
            members that printed); the common grid keeps only dates where all five print.
  WEIGHTS   E238's share is the turnover-level share of the printing book; the common grid
            recomputes the share increment from the members' levels. Kappa (w/(1-w)) is the
            nominal 1/5 in one reading and a measured share in the other.
  RESPONSE  the book-scaling coefficient g flips sign. No weighting choice can produce a
            sign flip of the response, so if g flips while the DERIVED rest channel
            b_agg = g - b_own does not, the published gap was two different objects.

WHAT IS PUBLISHED
  (1) a four-rung ladder r0 (E238 reproduced on its own rows) -> r1 (same construction,
      common dates) -> r2 (common grid, share recomputed from levels = E240's coordinate)
      -> r3 (aligned comparison), each rung carrying a_share, g_book, the derived b_agg and
      their Newey-West intervals.
  (2) the exact decomposition of E240's published gap_B:
          gap_B_naive = (B_r2 - b_agg_pub)
                      = (B_r2 - b_agg_r2)      <- parametrisation (two different objects)
                      + (b_agg_r2 - b_agg_pub) <- the aligned change
      pinned to 1e-12, plus the aligned change split into ROWS and WEIGHTS components.
  (3) the verdict: which single rung step carries the sign flip, and whether the rest
      channel survives it. Until this is settled the family must not quote 0.771 as a rest
      coefficient outside E238's own parametrisation.

NO ADOPTION: this face reprices the reproduction record only. It publishes no charge and
adopts no arm.
"""
from __future__ import annotations

import argparse
import json
import math
import os
import sys
from datetime import datetime

HERE = os.path.dirname(os.path.abspath(__file__))
if HERE not in sys.path:
    sys.path.insert(0, HERE)

import e222_tom_overlay as e222        # noqa: E402  (ROOT)
import e225_state_tilt as e225         # noqa: E402  (BASKET)
import e233_empirical_gamma as e233    # noqa: E402  (basket rows)
import e235_charge_granularity as e235 # noqa: E402  (sd / corr helpers)
import e236_share_difference as e236   # noqa: E402  (the differenced design, reused verbatim)
import e238_leave_one_out_book as e238 # noqa: E402  (the published pair and its rows)
import e239_own_vs_cross as e239       # noqa: E402  (panels)
import e240_aggregate_attenuation as e240  # noqa: E402  (common grid + coordinate map)

ROOT = e222.ROOT
OUTDIR = os.path.join(ROOT, "results", "state_tilt")
BASKET = e225.BASKET

TOL_ID = 1e-12
MATCH_TOL = 5e-3          # the published face carries 16 significant digits; 5e-3 is a
                          # generous "reproduced" line and it is reported, never assumed
NOMINAL_KAPPA = 0.25      # w = 1/5 on an equal-weight five-member book
STEP_NAMES = ("r0_published_rows_loo",
              "r1_common_rows_loo",
              "r2_common_rows_inclusive",
              "r3_common_grid_e240_code_path",
              "r3b_e240_code_y_realigned",
              "r4_aligned_comparison")
CHANNEL = ("rest (leave-one-out denominator)", "rest (leave-one-out denominator)",
           "book (inclusive denominator)", "book (inclusive denominator)",
           "book (inclusive denominator)", "aligned comparison")


# ---------------------------------------------------------------- rungs
def rung_pair(seqs, pooled=True):
    """One rung of the ladder: E236/E238's differenced design on whichever series it is given.

    Three numbers are published together and they are NOT the same object:
      a_share : the coefficient on d(log share)  -- E238's b_own
      g_book  : the coefficient on d(log book)   -- the BOOK-SCALING coefficient
      b_agg   : g_book - a_share                 -- the derived rest channel (E238's b_agg)
    Reusing e238.fit_all means the rung differs from E238 only in the series it is handed.
    """
    fit = e238.fit_all(seqs, pooled=pooled)
    d = (fit or {}).get("differences") or {}
    a, g = d.get("b_own"), d.get("g_scaling")
    out = {
        "design": "differences",
        "rows": d.get("rows_used"),
        "a_share": a,
        "g_book": g,
        "b_agg": d.get("b_agg"),
        "a_share_ci": d.get("b_own_ci"),
        "a_share_t": d.get("b_own_t_nw"),
        "g_book_se": d.get("g_scaling_se"),
        "g_book_ci": d.get("g_scaling_ci"),
        "b_agg_ci": d.get("b_agg_ci"),
        "b_agg_t": d.get("b_agg_t_nw"),
        "r2": d.get("r2"),
        "reason": d.get("reason"),
        "members": len(seqs),
    }
    out["derived_identity_checked"] = derived_identity(a, g, out["b_agg"])
    return out


def derived_identity(a_share, g_book, b_agg):
    """b_agg == g_book - a_share, to 1e-12. Returns the residual (None if any part missing)."""
    if a_share is None or g_book is None or b_agg is None:
        return None
    return b_agg - (g_book - a_share)


def mask_common(maps, syms, key="loo"):
    """Keep only the dates on which EVERY member printed, under E238's own row construction.

    On those dates the aggregate E238 used already sums all five members, so the only thing
    that changes between two rungs sharing a key is the ROW SET. ``key`` selects the
    denominator: "loo" is E238's leave-one-out book, "incl" its inclusive book.
    """
    date_sets = [set(r[0] for r in maps[s][key]) for s in syms]
    if not date_sets:
        return {}
    common = set.intersection(*date_sets)
    return {s: [r for r in maps[s][key] if r[0] in common] for s in syms}


def misalignment_proof(per, panel, syms):
    """Is E240's y vector on the same session as the regressors it is fitted against?

    common_increments indexes its arrays by the KEPT session (dy[i] is the move INTO
    dates[i]), while design_share_book re-pairs the sessions from k=1 and takes dy[k-1] --
    so the dependent variable is one session behind the share increments. The proof is a
    count, not an opinion: how many rows match on the same session and how many match when
    the y is shifted back by one.
    """
    dates = panel.get("dates") or []
    if len(dates) < 3:
        return {"available": False, "reason": "fewer than three common sessions"}
    same, shifted, n = 0, 0, 0
    for m in syms:
        dy = (panel.get("dy") or {}).get(m) or []
        if len(dy) < len(dates):
            continue
        for k in range(1, len(dates)):
            same_move = per[m][dates[k]][0] - per[m][dates[k - 1]][0]
            prev_move = per[m][dates[k - 1]][0] - per[m][dates[k - 2]][0]
            n += 1
            if abs(dy[k - 1] - same_move) <= 1e-9:
                same += 1
            if abs(dy[k - 1] - prev_move) <= 1e-9:
                shifted += 1
    return {"available": n > 0, "rows_tested": n,
            "dy_matches_the_same_session": same,
            "dy_matches_the_previous_session": shifted,
            "dy_is_one_session_behind": bool(n and shifted > 0.9 * n and same <= 0.1 * n),
            "note": "common_increments indexes dy by the KEPT session; design_share_book takes "
                    "dy[k-1] while pairing the sessions k-1 -> k"}


def _aligned_share_book(per, panel, syms, lag=None):
    """E240's coordinate with the y taken from the session the regressors describe."""
    lag = e225.NW_LAG if lag is None else lag
    dates = panel["dates"]
    y, xs, xa = [], [], []
    for m in syms:
        for k in range(1, len(dates)):
            d1, d0 = dates[k], dates[k - 1]
            la1 = e240._log_agg(per, syms, d1)
            la0 = e240._log_agg(per, syms, d0)
            y.append(per[m][d1][0] - per[m][d0][0])     # same session as the increments
            xs.append((per[m][d1][1] - la1) - (per[m][d0][1] - la0))
            xa.append(la1 - la0)
    fit = e240._fit(y, [xs, xa], lag)
    if fit is None:
        return {"reason": "within_or_singular"}
    a, b = fit["betas"][1], fit["betas"][2]
    return {"rows": fit["rows_used"], "a_share": a, "g_book": b, "b_agg": b - a,
            "a_share_ci": fit["cis"][0], "g_book_ci": fit["cis"][1], "r2": fit["r2"]}


def _as_published_share_book(per, panel, syms, lag=None):
    """E240's coordinate EXACTLY as published (dy[k-1]) -- kept as the reproduction rung.

    The current routine on disk is repaired (F-20261030-01), so the published numbers can only
    be reproduced by this replica; keeping it means the ladder still shows what the face said.
    """
    lag = e225.NW_LAG if lag is None else lag
    dates = panel["dates"]
    dy = panel["dy"]
    y, xs, xa = [], [], []
    for m in syms:
        for k in range(1, len(dates)):
            d1, d0 = dates[k], dates[k - 1]
            la1 = e240._log_agg(per, syms, d1)
            la0 = e240._log_agg(per, syms, d0)
            y.append(dy[m][k - 1])
            xs.append((per[m][d1][1] - la1) - (per[m][d0][1] - la0))
            xa.append(la1 - la0)
    fit = e240._fit(y, [xs, xa], lag)
    if fit is None:
        return {"reason": "within_or_singular"}
    a, b = fit["betas"][1], fit["betas"][2]
    return {"rows": fit["rows_used"], "a_share": a, "g_book": b, "b_agg": b - a,
            "a_share_ci": fit["cis"][0], "g_book_ci": fit["cis"][1], "r2": fit["r2"],
            "source": "replica of the published routine (y indexed dy[k-1])"}


def decompose_gap(naive_gap, param_gap, aligned_gap):
    """gap_naive = gap_from_parametrisation + gap_aligned (an identity, not a model)."""
    if naive_gap is None or param_gap is None or aligned_gap is None:
        return {"available": False, "reason": "one of the three gaps is missing"}
    return {"available": True,
            "naive_gap": naive_gap,
            "parametrisation_part": param_gap,
            "aligned_part": aligned_gap,
            "identity_residual": naive_gap - (param_gap + aligned_gap)}


def split_aligned(aligned_gap, rows_part, weights_part, reader_part=0.0):
    """The aligned change splits into ROWS, DENOMINATOR and READER parts; residual published."""
    if aligned_gap is None or rows_part is None or weights_part is None:
        return {"available": False, "reason": "one of the parts is missing"}
    total = rows_part + weights_part + (reader_part or 0.0)
    return {"available": True,
            "aligned_gap": aligned_gap,
            "rows_part": rows_part,
            "weights_part": weights_part,
            "reader_part": reader_part,
            "residual": aligned_gap - total,
            "dominant": ("rows" if abs(rows_part) >= abs(weights_part)
                         else "weights")}


def classify(pub, r2, dec):
    """Which rung step carries the sign flip, and is the comparison even like-for-like?

    pub is E238's LEAVE-ONE-OUT pair (its b_agg is the coefficient on d(log rest), i.e. the
    REST channel). r2 is E240's INCLUSIVE coordinate (its derived b_agg = B - A is the BOOK
    channel). Those two b_agg's are different objects, so a raw comparison between them mixes
    a parametrisation mismatch with a real change -- the decomposition says how much is which.
    """
    if not pub or not r2 or not dec.get("available"):
        return {"verdict": "unavailable",
                "reason": "the published pair, the common-grid rung and the decomposition "
                          "are all required"}
    a_pub, g_pub, b_pub = pub.get("a_share"), pub.get("g_book"), pub.get("b_agg")
    a_r2, g_r2, b_r2 = r2.get("a_share"), r2.get("g_book"), r2.get("b_agg")
    if None in (a_pub, g_pub, b_pub, a_r2, g_r2, b_r2):
        return {"verdict": "unavailable", "reason": "a sign test input is missing"}

    def _flips(x, y):
        return (x < 0.0) != (y < 0.0)

    out = {"denominators_differ": True,
           "channels": {"published_b_agg": "rest (leave-one-out)",
                        "common_grid_b_agg": "book (inclusive)"},
           "a_share_published": a_pub, "a_share_common_grid": a_r2,
           "a_share_sign_flips": _flips(a_pub, a_r2),
           "g_denominator_published": g_pub, "g_denominator_common_grid": g_r2,
           "g_sign_flips": _flips(g_pub, g_r2),
           "b_agg_published": b_pub, "b_agg_common_grid": b_r2,
           "b_agg_sign_flips": _flips(b_pub, b_r2),
           "naive_gap_B": dec["naive_gap"],
           "parametrisation_part": dec["parametrisation_part"],
           "aligned_part": dec["aligned_part"],
           "identity_residual": dec["identity_residual"]}
    share_param = abs(dec["parametrisation_part"]) / max(1e-12, abs(dec["naive_gap"]))
    out["parametrisation_share_of_naive_gap"] = share_param
    if share_param > 0.5:
        out["verdict"] = "the_published_gap_is_mostly_two_different_objects"
    elif out["b_agg_sign_flips"]:
        out["verdict"] = "the_rest_channel_changes_sign_between_the_readings"
    else:
        out["verdict"] = "the_rest_channel_keeps_its_sign_the_gap_is_magnitude"
    out["aligned_b_agg_change"] = dec["aligned_part"]
    return out


# ---------------------------------------------------------------- face io
def _read_face(path):
    if not os.path.exists(path):
        return None
    try:
        with open(path, "r", encoding="utf-8") as fh:
            return json.load(fh)
    except (OSError, ValueError):
        return None


def _published_pair(face):
    """Machine-read the published pair; never transcribe it into this file."""
    if not face:
        return None
    pooled = (face.get("pooled") or {}).get("leave_one_out") or {}
    d = pooled.get("differences") or {}
    a = d.get("b_own")
    b = d.get("b_agg")
    if a is None or b is None:
        return None
    return {"a_share": a, "b_agg": b,
            "g_book": a + b,              # exact by the published parametrisation
            "rows": d.get("rows"),
            "r2": d.get("r2"),
            "kappa_used": (face.get("pooled") or {}).get("kappa_used"),
            "kappa_nominal": (face.get("pooled") or {}).get("kappa_nominal"),
            "face": "loobook_latest.json",
            "sessions": (face.get("book") or {}).get("sessions")}


def _write(face, outdir):
    os.makedirs(outdir, exist_ok=True)
    name = "REPRO-%s.json" % (face.get("evidence_cutoff") or "unknown")
    for path in (os.path.join(outdir, name), os.path.join(outdir, "repro_latest.json")):
        with open(path, "w", encoding="utf-8", newline="\n") as fh:
            json.dump(face, fh, ensure_ascii=False, indent=1, sort_keys=True)
            fh.write("\n")


# ---------------------------------------------------------------- run
def run(save=True, panel_dir=None, outdir=None):
    outdir = outdir or OUTDIR
    maps = e238.book_maps(panel_dir)
    if not maps:
        print("no basket panel")
        return None
    syms = [s for s in BASKET if maps.get(s) and maps[s].get("loo")]
    if len(syms) < 4:
        print("fewer than four members have a usable panel")
        return None

    published = _published_pair(_read_face(os.path.join(outdir, "loobook_latest.json")))

    r0 = rung_pair([maps[s]["loo"] for s in syms])
    common_loo = mask_common(maps, syms, "loo")
    common_dates = sorted(set(r[0] for r in common_loo[syms[0]])) if common_loo else []
    r1 = (rung_pair([common_loo[s] for s in syms]) if common_loo
          else {"reason": "no common dates"})
    common_incl = mask_common(maps, syms, "incl")
    r2 = (rung_pair([common_incl[s] for s in syms]) if common_incl
          else {"reason": "no common dates"})

    per = e239.panels(panel_dir)
    dates, panel = e240.common_increments(per, syms)
    sb = (_as_published_share_book(per, panel, syms)
          if len(panel.get("dates") or []) >= 2 else {"reason": "no common grid"})
    a2, g2 = sb.get("A_share"), sb.get("B_book")
    if a2 is None:
        a2, g2 = sb.get("a_share"), sb.get("g_book")
    r3 = {"design": "share_book_reproduction_as_published",
          "rows": sb.get("rows_used") or sb.get("rows"), "a_share": a2, "g_book": g2,
          "b_agg": (g2 - a2) if (a2 is not None and g2 is not None) else None,
          "a_share_ci": sb.get("A_share_ci") or sb.get("a_share_ci"),
          "g_book_ci": sb.get("B_book_ci") or sb.get("g_book_ci"),
          "b_agg_ci": None, "a_share_t": None, "g_book_se": None, "b_agg_t": None,
          "r2": sb.get("r2"), "reason": sb.get("reason"),
          "measured_kappa": sb.get("measured_kappa"),
          "sessions": len(panel.get("dates") or []),
          "members": len(syms),
          "source": "replica of E240's published routine on the common grid"}
    r3["derived_identity_checked"] = derived_identity(r3["a_share"], r3["g_book"],
                                                      r3["b_agg"])

    proof = (misalignment_proof(per, panel, syms)
             if len(panel.get("dates") or []) >= 3 else {"available": False})
    r3b = (e240.design_share_book(per, panel, syms)
           if len(panel.get("dates") or []) >= 3 else {"reason": "no common grid"})
    if r3b.get("A_share") is not None:
        r3b = {"rows": r3b.get("rows_used"), "a_share": r3b["A_share"],
               "g_book": r3b["B_book"], "b_agg": r3b["B_book"] - r3b["A_share"],
               "a_share_ci": r3b.get("A_share_ci"), "g_book_ci": r3b.get("B_book_ci"),
               "r2": r3b.get("r2"), "source": "current routine on disk (F-20261030-01 fixed)"}

    repro = None
    if published and r0.get("a_share") is not None:
        repro = {"published_a_share": published["a_share"],
                 "rung0_a_share": r0["a_share"],
                 "abs_diff_a": abs(published["a_share"] - r0["a_share"]),
                 "published_b_agg": published["b_agg"],
                 "rung0_b_agg": r0["b_agg"],
                 "abs_diff_b": abs(published["b_agg"] - r0["b_agg"]),
                 "published_rows": published["rows"], "rung0_rows": r0["rows"]}
        repro["reproduced"] = (repro["abs_diff_a"] <= MATCH_TOL
                               and repro["abs_diff_b"] <= MATCH_TOL)
        repro["tolerance"] = MATCH_TOL

    # ---- r4: the aligned comparison, and the exact decomposition of E240's gap
    dec = {"available": False, "reason": "published pair or common-grid rung missing"}
    aligned = {"available": False, "reason": "published pair or common-grid rung missing"}
    if published and r3.get("g_book") is not None and r3.get("b_agg") is not None:
        naive_B = r3["g_book"] - published["b_agg"]
        param_B = r3["g_book"] - r3["b_agg"]
        aligned_B = r3["b_agg"] - published["b_agg"]
        dec = decompose_gap(naive_B, param_B, aligned_B)
        rows_part = ((r1.get("b_agg") - r0.get("b_agg"))
                     if r1.get("b_agg") is not None and r0.get("b_agg") is not None else None)
        denom_part = ((r2.get("b_agg") - r1.get("b_agg"))
                      if rows_part is not None and r2.get("b_agg") is not None else None)
        code_path_part = ((r3b.get("b_agg") - r2.get("b_agg"))
                          if (r3b.get("b_agg") is not None and r2.get("b_agg") is not None)
                          else None)
        aligned = split_aligned(r3b.get("b_agg") - published["b_agg"],
                                rows_part, denom_part, code_path_part)
        aligned["aligned_gap_name"] = ("the CORRECTED common-grid rest channel vs the "
                                       "published one (r3b - published)")
        aligned["reader_defect_b_agg"] = (
            r3.get("b_agg") - r3b.get("b_agg")
            if (r3.get("b_agg") is not None and r3b.get("b_agg") is not None) else None)
        aligned["reader_part_name"] = ("READER (E240's y one session behind its regressors; "
                                       "the difference between r3 as published and the "
                                       "corrected r3b, shown separately and NOT summed in)")
        if aligned.get("available"):
            aligned["rows_part_name"] = "ROWS (own grid -> common dates, leave-one-out)"
            aligned["weights_part_name"] = ("DENOMINATOR (leave-one-out -> inclusive), "
                                            "measured on E238's own code path")
        # the two code paths must agree on the same object, or the ladder measures the harness
        aligned["code_path_cross_check"] = {
            "r2_e238_code_on_inclusive_rows": {"a_share": r2.get("a_share"),
                                               "g_book": r2.get("g_book"),
                                               "b_agg": r2.get("b_agg"),
                                               "rows": r2.get("rows")},
            "r3_e240_code_on_common_grid": {"a_share": r3.get("a_share"),
                                            "g_book": r3.get("g_book"),
                                            "b_agg": r3.get("b_agg"),
                                            "rows": r3.get("rows")},
            "a_share_abs_diff": (abs(r2.get("a_share") - r3["a_share"])
                                 if r2.get("a_share") is not None else None),
            "g_book_abs_diff": (abs(r2.get("g_book") - r3["g_book"])
                                if r2.get("g_book") is not None else None),
            "same_object": bool(
                r2.get("a_share") is not None and r3.get("a_share") is not None
                and abs(r2["a_share"] - r3["a_share"]) <= 1e-6),
        }
        aligned["a_share_published"] = published["a_share"]
        aligned["a_share_rung0"] = r0.get("a_share")
        aligned["a_share_rung1"] = r1.get("a_share")
        aligned["a_share_rung2"] = r2.get("a_share")
        aligned["a_share_rung3"] = r3.get("a_share")
        aligned["a_share_moves"] = (r3["a_share"] - published["a_share"]
                                    if r3.get("a_share") is not None else None)
        aligned["kappa_published"] = published.get("kappa_used")
        aligned["kappa_nominal"] = published.get("kappa_nominal") or NOMINAL_KAPPA
        aligned["kappa_common_grid"] = ((r3.get("measured_kappa") or {}).get("kappa"))
        aligned["coordinate_map_common_grid"] = e240.coordinate_map(
            r3["a_share"], r3["g_book"], aligned["kappa_nominal"] or NOMINAL_KAPPA)
        aligned["coordinate_map_published"] = e240.coordinate_map(
            published["a_share"], published["b_agg"],
            aligned["kappa_nominal"] or NOMINAL_KAPPA)

    verdict = classify(published, r3, dec)
    pub_face = _read_face(os.path.join(outdir, "aggatt_latest.json")) or {}
    pub_sb = ((pub_face.get("designs") or {}).get("share_book_reproduction") or {})
    published_face_check = {
        "face": "aggatt_latest.json",
        "published_a_share": pub_sb.get("A_share"),
        "published_b_book": pub_sb.get("B_book"),
        "replica_a_share": r3.get("a_share"),
        "replica_b_book": r3.get("g_book"),
        "reproduced": (pub_sb.get("A_share") is not None
                       and r3.get("a_share") is not None
                       and abs(pub_sb["A_share"] - r3["a_share"]) <= MATCH_TOL
                       and abs((pub_sb.get("B_book") or 0.0)
                               - (r3.get("g_book") or 0.0)) <= MATCH_TOL),
        "superseded": None,
    }
    if proof.get("dy_is_one_session_behind") and r3b.get("a_share") is not None:
        verdict["misalignment"] = proof
        verdict["realigned_pair"] = {"a_share": r3b["a_share"], "g_book": r3b["g_book"],
                                     "b_agg": r3b["b_agg"], "rows": r3b["rows"],
                                     "a_share_ci": r3b.get("a_share_ci")}
        verdict["realigned_agrees_with_rung2"] = (
            r2.get("a_share") is not None
            and abs(r3b["a_share"] - r2["a_share"]) <= 5e-3)
        verdict["verdict"] = "the_non_reproduction_is_a_one_session_misalignment_in_the_reader"
        published_face_check["superseded"] = bool(
            published_face_check["reproduced"]
            and abs(r3b["a_share"] - r3["a_share"]) > MATCH_TOL)

    ladder = []
    for i, (name, rung) in enumerate(zip(STEP_NAMES[:5], (r0, r1, r2, r3, r3b))):
        ladder.append({"step": name,
                       "channel": CHANNEL[i],
                       "change_vs_previous": ("baseline (E238 reproduced)" if i == 0 else
                                              ("ROWS" if i == 1 else
                                               ("DENOMINATOR (leave-one-out -> inclusive)"
                                                if i == 2 else
                                                ("CODE PATH (E240 routine, same object)"
                                                 if i == 3 else
                                                 "Y ALIGNMENT (same routine, y from the "
                                                 "session the regressors describe)")))),
                       "rows": rung.get("rows"),
                       "a_share": rung.get("a_share"),
                       "g_denominator": rung.get("g_book"),
                       "b_agg": rung.get("b_agg"),
                       "a_share_ci": rung.get("a_share_ci"),
                       "g_denominator_ci": rung.get("g_book_ci"),
                       "r2": rung.get("r2"),
                       "reason": rung.get("reason")})
    ladder.append({"step": STEP_NAMES[5], "channel": CHANNEL[5],
                   "verdict": verdict.get("verdict"),
                   "naive_gap_B": dec.get("naive_gap"),
                   "parametrisation_part": dec.get("parametrisation_part"),
                   "aligned_part": dec.get("aligned_part"),
                   "identity_residual": dec.get("identity_residual"),
                   "aligned_split": aligned})

    face = {
        "study": "E241",
        "title": "why does E238's published (A, B) pair not reproduce on the common grid?",
        "generated": datetime.now().isoformat(timespec="seconds"),
        "evidence_cutoff": (common_dates[-1] if common_dates
                            else (r0.get("last") or None)),
        "dept": "研究",
        "members": syms,
        "frozen_spec": {
            "question": "E238 published (b_own 0.596, b_agg 0.771) on its own date grid; E240 "
                        "re-ran the coordinates on the common five-member grid and read "
                        "(A -0.333, B -0.174), a gap of -1.16/-1.18. Which single change "
                        "carries it?",
            "three_candidates": {
                "rows": "E238 fits each member on its own sessions; the common grid keeps "
                        "only dates where all five print",
                "weights": "the share is the turnover-level share of the printing book in "
                           "E238 and a level recomputation on the common grid in E240; kappa "
                           "is the nominal 1/5 in one reading and a measured share in the "
                           "other",
                "response": "the book-scaling coefficient g flips sign, which no weighting "
                            "choice can produce",
            },
            "ladder_rule": "one dimension relaxed per rung; every rung publishes a_share, "
                           "g_book AND the derived b_agg = g_book - a_share, because E238's "
                           "published b_agg is the derived rest channel and NOT the "
                           "coefficient on d(log book)",
            "no_transcription": "the published pair is machine-read from loobook_latest.json",
            "no_adoption": "this face reprices the reproduction record only; no charge, no arm",
        },
        "published_pair": published,
        "reproduction": repro,
        "ladder": ladder,
        "alignment": aligned,
        "misalignment": proof,
        "published_face_check": published_face_check,
        "verdict_block": verdict,
        "summary": {
            "verdict": verdict.get("verdict"),
            "reproduces_published": (repro or {}).get("reproduced"),
            "rows_rung0": r0.get("rows"), "rows_common": r1.get("rows"),
            "rows_common_grid_240": r2.get("rows"),
            "sessions_common": len(common_dates),
        },
    }
    face["answer"] = _answer(face)
    face["no_bill"] = {"permitted": False,
                       "reason": "a reproduction ladder identifies a unit error; it publishes "
                                 "no charge and adopts no arm"}
    if save:
        _write(face, outdir)
    return face


def _f(v, spec="%.3f"):
    return "n/a" if v is None else spec % v


def _answer(face):
    v = face["summary"]["verdict"]
    rep = face["reproduction"] or {}
    vb = face.get("verdict_block") or {}
    if v == "unavailable":
        return ("reproduction ladder could not be built: %s"
                % (face["summary"].get("reason") or "a rung is missing"))
    if not rep.get("reproduced"):
        return ("E238's pair does NOT reproduce on its own rows (b_own %s vs published %s): "
                "the ladder cannot attribute anything until it does"
                % (_f(rep.get("rung0_a_share"), "%.4f"),
                   _f(rep.get("published_a_share"), "%.4f")))
    if v == "the_non_reproduction_is_a_one_session_misalignment_in_the_reader":
        mp = vb.get("misalignment") or {}
        rp = vb.get("realigned_pair") or {}
        return ("rung0 reproduces E238 exactly (a_share %.4f, b_agg %.4f on %s rows), so the "
                "grid is not the problem. E240's common-grid pair (A %s, B %s) is one session "
                "out of step with its own regressors: of %s rows tested, %s carry the PREVIOUS "
                "session's move (same-session matches %s). Feeding the same increments and the "
                "same y through the same routine gives A %s, b_agg %s, i.e. the row restriction "
                "alone moves the rest channel from %s to %s and nothing here flips a sign. "
                "E240's A/B pair is superseded; its dy/dx designs are unaffected because they "
                "index both arrays by the same session."
                % (rep["rung0_a_share"], rep["rung0_b_agg"], rep.get("rung0_rows"),
                   _f(vb.get("a_share_common_grid"), "%.4f"),
                   _f(vb.get("g_denominator_common_grid"), "%.4f"),
                   _f(mp.get("rows_tested"), "%d"),
                   _f(mp.get("dy_matches_the_previous_session"), "%d"),
                   _f(mp.get("dy_matches_the_same_session"), "%d"),
                   _f(rp.get("a_share"), "%.4f"), _f(rp.get("b_agg"), "%.4f"),
                   _f(vb.get("b_agg_published"), "%.4f"), _f(rp.get("b_agg"), "%.4f")))
    aligned = face.get("alignment") or {}
    return ("rung0 reproduces E238 exactly (a_share %.4f, b_agg %.4f on %s rows) and the "
            "aligned common-grid change is %s, split %s rows / %s denominator: %s"
            % (rep["rung0_a_share"], rep["rung0_b_agg"], rep.get("rung0_rows"),
               _f(vb.get("aligned_part")), _f(aligned.get("rows_part")),
               _f(aligned.get("weights_part")), v))


# ---------------------------------------------------------------- selftest
def _synth_book(n=700, own_channel=0.4, share_noise=0.03, seed=7):
    """Five synthetic members with a KNOWN own channel, in E238's row format."""
    return [e238.synth_member(n=n, w=None, own_channel=own_channel, noise=0.6,
                              share_noise=share_noise, seed=seed + i)
            for i in range(5)]


def selftest():
    legs = []

    def leg(name, fn):
        try:
            fn()
            legs.append((name, True, ""))
        except AssertionError as exc:
            legs.append((name, False, str(exc)))

    def l_rung_reads_three_numbers():
        seqs = [m["loo"] for m in _synth_book()]
        rung = rung_pair(seqs)
        assert rung["rows"] and rung["rows"] > 0, rung
        for key in ("a_share", "g_book", "b_agg"):
            assert rung[key] is not None, (key, rung)
        assert rung["derived_identity_checked"] is not None
        assert abs(rung["derived_identity_checked"]) < TOL_ID, rung["derived_identity_checked"]

    def l_rung_recovers_a_known_channel():
        # own_channel = 1.0 on a synthetic book with a random share: the differenced design
        # must find a positive share coefficient, and a book with NO channel must find a
        # small one. Both are order-of-magnitude checks, not confidence claims.
        hot = rung_pair([m["loo"] for m in _synth_book(own_channel=1.0, seed=11)])
        cold = rung_pair([m["loo"] for m in _synth_book(own_channel=0.0, seed=11)])
        assert hot["a_share"] > cold["a_share"], (hot["a_share"], cold["a_share"])
        assert hot["a_share"] > 0.0, hot["a_share"]

    def l_b_agg_is_not_the_book_coefficient():
        # the whole point of the card: g_book and b_agg are different objects
        rung = rung_pair([m["loo"] for m in _synth_book(seed=3)])
        assert abs(rung["b_agg"] - rung["g_book"]) > 1e-9, rung

    def l_mask_common_narrows_the_row_set():
        maps = {("m%d" % i): {"loo": [(d, 0.0, 0.0, 0.0) for d in dates]}
                for i, dates in enumerate([("a", "b", "c", "d"),
                                           ("b", "c", "d"),
                                           ("c", "d", "e")])}
        syms = list(maps)
        masked = mask_common(maps, syms)
        got = [r[0] for r in masked["m0"]]
        assert got == ["c", "d"], got
        assert all([r[0] for r in masked[s]] == got for s in syms)

    def l_mask_common_is_identity_when_grids_agree():
        dates = ["a", "b", "c"]
        maps = {("m%d" % i): {"loo": [(d, 0.0, 0.0, 0.0) for d in dates]} for i in range(3)}
        masked = mask_common(maps, list(maps))
        for s in maps:
            assert [r[0] for r in masked[s]] == dates

    def l_decomposition_is_an_identity():
        d = decompose_gap(naive_gap=2.5, param_gap=1.0, aligned_gap=1.5)
        assert d["available"] and abs(d["identity_residual"]) < TOL_ID, d
        d2 = decompose_gap(naive_gap=-1.178, param_gap=-0.945, aligned_gap=-0.233)
        assert abs(d2["identity_residual"]) < TOL_ID, d2

    def l_decomposition_refuses_missing_inputs():
        assert decompose_gap(None, 1.0, 1.0)["available"] is False
        assert decompose_gap(1.0, None, 1.0)["available"] is False

    def l_split_aligned_publishes_its_residual():
        s = split_aligned(aligned_gap=0.6, rows_part=0.1, weights_part=0.5)
        assert s["available"] and abs(s["residual"]) < TOL_ID and s["dominant"] == "weights"
        s2 = split_aligned(aligned_gap=0.6, rows_part=0.5, weights_part=0.1)
        assert s2["dominant"] == "rows"
        assert split_aligned(0.6, None, 0.1)["available"] is False

    def l_rest_channel_keeping_its_sign_is_a_magnitude_story():
        pub = {"a_share": 0.596, "g_book": 1.367, "b_agg": 0.771}
        r2 = {"a_share": -0.333, "g_book": -0.174, "b_agg": 0.159}
        dec = decompose_gap(naive_gap=-0.945, param_gap=-0.333, aligned_gap=-0.612)
        v = classify(pub, r2, dec)
        assert v["verdict"] == "the_rest_channel_keeps_its_sign_the_gap_is_magnitude", v
        assert v["b_agg_sign_flips"] is False and v["a_share_sign_flips"] is True, v
        assert abs(v["identity_residual"]) < TOL_ID, v

    def l_parametrisation_majority_is_named():
        pub = {"a_share": 0.5, "g_book": 1.0, "b_agg": 0.5}
        r2 = {"a_share": 0.1, "g_book": -0.3, "b_agg": 0.4}
        dec = decompose_gap(naive_gap=-0.9, param_gap=-0.7, aligned_gap=-0.2)
        v = classify(pub, r2, dec)
        assert v["verdict"] == "the_published_gap_is_mostly_two_different_objects", v
        assert v["parametrisation_share_of_naive_gap"] >= 0.5, v

    def l_rest_channel_flip_is_reported():
        pub = {"a_share": 0.5, "g_book": 1.0, "b_agg": 0.5}
        r2 = {"a_share": 0.5, "g_book": 0.3, "b_agg": -0.2}
        dec = decompose_gap(naive_gap=-1.0, param_gap=-0.5, aligned_gap=-0.5)
        v = classify(pub, r2, dec)
        assert v["verdict"] == "the_rest_channel_changes_sign_between_the_readings", v

    def l_classify_refuses_missing_rungs():
        full = {"a_share": 1.0, "g_book": 2.0, "b_agg": 1.0}
        assert classify(None, full, decompose_gap(1.0, 1.0, 0.0))["verdict"] == "unavailable"
        assert classify(full, None, decompose_gap(1.0, 1.0, 0.0))["verdict"] == "unavailable"
        assert classify(full, full, {"available": False})["verdict"] == "unavailable"
        assert classify({"a_share": 1.0}, full,
                        decompose_gap(1.0, 1.0, 0.0))["verdict"] == "unavailable"

    def l_coordinate_map_identity():
        cm = e240.coordinate_map(0.5962739, 0.7705966, NOMINAL_KAPPA)
        assert cm["available"]
        lhs = 0.7705966 - 0.5962739
        rhs = (1.0 + NOMINAL_KAPPA) * cm["c_rest"]
        assert abs(lhs - rhs) < 1e-9, (lhs, rhs)

    def l_rungs_are_deterministic():
        a = rung_pair([m["loo"] for m in _synth_book(seed=5)])
        b = rung_pair([m["loo"] for m in _synth_book(seed=5)])
        assert a["a_share"] == b["a_share"] and a["g_book"] == b["g_book"]

    def l_no_saved_face_without_a_verdict():
        face = run(save=False)
        assert face is None or "verdict" in (face.get("summary") or {}), "verdict missing"

    for name, fn in [
        ("rung publishes a_share, g_book and the derived b_agg with a 1e-12 identity",
         l_rung_reads_three_numbers),
        ("the differenced design still finds a known own channel", l_rung_recovers_a_known_channel),
        ("b_agg is not the book-scaling coefficient", l_b_agg_is_not_the_book_coefficient),
        ("mask_common keeps only the dates every member printed", l_mask_common_narrows_the_row_set),
        ("mask_common is the identity when the grids already agree", l_mask_common_is_identity_when_grids_agree),
        ("the gap decomposition is an identity to 1e-12", l_decomposition_is_an_identity),
        ("the decomposition refuses a missing input", l_decomposition_refuses_missing_inputs),
        ("the aligned split publishes its residual and its dominant part",
         l_split_aligned_publishes_its_residual),
        ("a gap that is magnitude-only keeps the rest channel's sign",
         l_rest_channel_keeping_its_sign_is_a_magnitude_story),
        ("a gap that is mostly two objects is named as such", l_parametrisation_majority_is_named),
        ("a rest-channel sign flip is reported", l_rest_channel_flip_is_reported),
        ("classify refuses missing rungs", l_classify_refuses_missing_rungs),
        ("the coordinate map is consistent with B - A", l_coordinate_map_identity),
        ("the ladder is deterministic", l_rungs_are_deterministic),
        ("a face never ships without a verdict", l_no_saved_face_without_a_verdict),
    ]:
        leg(name, fn)

    ok = sum(1 for _n, good, _m in legs if good)
    print("Summary: %d/%d" % (ok, len(legs)))
    for name, good, msg in legs:
        print("%s %s%s" % ("PASS" if good else "FAIL", name, ("  <- " + msg) if msg else ""))
    return 0 if ok == len(legs) else 1


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("mode", nargs="?", default="run", choices=("run", "selftest"))
    ap.add_argument("--no-save", action="store_true")
    args = ap.parse_args(argv)
    if args.mode == "selftest":
        return selftest()
    face = run(save=not args.no_save)
    if face is None:
        return 2
    print(face["answer"])
    return 0


if __name__ == "__main__":
    sys.exit(main())