#!/usr/bin/env python3
"""E249 -- is the negative one-session lead the star's own flow, or does every column pay it?

E248 found exactly one crossing against a shuffled null: lag 1, negative, -0.586 on the star
column, with the family-wise line at 0.351. Two readings survive that result and the lag row
cannot separate them, because the row only ever fits ONE column of interest:

  (a) that sleeve's flow is absorbed -- its turnover spikes and the book's next move is
      smaller, a source with a negative sign; or
  (b) every column pays the same lag-1 negative because a book-wide liquidity proxy
      mean-reverts, and the star is simply the column the fit reads most cleanly.

The counterfactual is direct and was frozen before the sweep was read: run the same 5-lag row
with EACH member as the column of interest (the other four are the rows), publish the lag-1
coefficient per column with its OWN 200-draw shuffled band, and ask whether the star's lag-1
reading is distinguishable from the others' -- with the column-to-column spread measured
against the within-column band, so "specific" is a comparison and not an impression.

Vocabulary (frozen):

  nothing_outside_own_null     no column's lag-1 reaches its own shuffled band
  column_specific              exactly one column crosses; named, and the gap to the rest is
                               published against the within-column band width
  book_wide_same_sign          several columns cross, they share a sign, and the spread between
                               them does not exceed the median within-column band width -- one
                               number that everyone pays, so no sleeve may be billed for it
  multiple_crossings_differ    several cross but they disagree in sign or their spread is larger
                               than the band
  unresolved_too_few_rows

NO BILL, NO ADOPTION, NO RE-PRICING. This face separates a channel; it prices nothing.
"""

from __future__ import annotations

import argparse
import json
import math
import os
import sys
from datetime import datetime

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
if HERE not in sys.path:
    sys.path.insert(0, HERE)

import e222_tom_overlay as e222  # noqa: E402
import e225_state_tilt as e225  # noqa: E402
import e239_own_vs_cross as e239  # noqa: E402
import e240_aggregate_attenuation as e240  # noqa: E402
import e243_additivity_out_of_sample as e243  # noqa: E402
import e245_pair_slope_matrix as e245  # noqa: E402
import e246_star_direction as e246  # noqa: E402
import e248_star_lag_band as e248  # noqa: E402

ROOT = e222.ROOT
OUTDIR = os.path.join(ROOT, "results", "state_tilt")
BASKET = e225.BASKET
MIN_SESSIONS = e240.MIN_SESSIONS
STUDY = "E249"

LAGS = (1, 2, 3, 4, 5)
COLUMN_DRAWS = 200                      # shuffled draws per column, headline cell
ERA_DRAWS = 60                          # the era cells are corroboration, not the headline
BAND_MODE = "%d_draw_full_range_per_column" % COLUMN_DRAWS
BASESEED = 20261101
COUNTED_KINDS = ("headline", "window", "era", "neighbour")

VERDICTS = ("nothing_outside_own_null",
            "column_specific",
            "book_wide_same_sign",
            "multiple_crossings_differ",
            "unresolved_too_few_rows")

CELLS = e245.CELLS


# ---------------------------------------------------------------- the sweep
def column_sweep(panel, syms, draws=COLUMN_DRAWS, seed=BASESEED):
    """Fit the 5-lag row once per column of interest, each against its own shuffled band.

    Reuses E248's estimator and band verbatim (same `fit_lag_row`, same `permutation_band`,
    same family-wise line). The only thing new here is that the column of interest moves, so
    the five readings are five measurements of the same design rather than one measurement
    read once.
    """
    out = {}
    for i, c in enumerate(syms):
        row = e248.fit_lag_row(panel, syms, c)
        if not row.get("decided"):
            out[c] = {"decided": False, "reason": row.get("reason") or "row refused"}
            continue
        col = e248._mean_lags(row["members"])
        if col is None:
            out[c] = {"decided": False, "reason": "column could not be averaged"}
            continue
        band = e248.permutation_band(panel, syms, c, draws=draws, seed=seed + i)
        bands = band["bands"]
        fam = band.get("family")
        per_member = {r["one_of"]: r["lags"][1] for r in row["members"] if r.get("decided")}
        b1s = list(per_member.values())
        out[c] = {"decided": True,
                  "rows_used": row["rows"],
                  "b1": col[1],
                  "lag_column": {"lag%d" % k: col[k] for k in range(len(col))},
                  "band_lag1": bands[1] if len(bands) > 1 else None,
                  "band_family": fam,
                  "draws_used": band["draws_used"],
                  "outside_own_band": e248._outside(col[1], bands[1] if len(bands) > 1 else None,
                                                    fam),
                  "members_fitted": len(b1s),
                  "per_member_b1": {k: v for k, v in sorted(per_member.items())},
                  "per_member_b1_spread": (max(b1s) - min(b1s)) if len(b1s) > 1 else None}
    return out


def _median(xs):
    xs = sorted(x for x in xs if x is not None)
    if not xs:
        return None
    n = len(xs)
    return xs[n // 2] if n % 2 else 0.5 * (xs[n // 2 - 1] + xs[n // 2])


def _width(cell):
    b = (cell or {}).get("band_lag1") or {}
    return b.get("width")


def _sign(x):
    return 1 if (x or 0.0) > 0.0 else (-1 if (x or 0.0) < 0.0 else 0)


def derive_verdict(cols, star=None):
    """The whole classification, recomputable from the published per-column numbers alone.

    Frozen before the sweep was read; the smoke leg re-runs this against the face's own cells
    so no cell can carry a verdict its numbers do not produce.
    """
    ok = {k: v for k, v in (cols or {}).items() if v.get("decided")}
    if len(ok) < 3:
        return {"verdict": "unresolved_too_few_rows",
                "reason": "%d of %d columns decided" % (len(ok), len(cols or {}))}
    names = sorted(ok)
    b1 = {k: ok[k]["b1"] for k in names}
    crossed = [k for k in names if ok[k].get("outside_own_band")]
    widths = [w for w in (_width(ok[k]) for k in names) if w is not None]
    med_width = _median(widths)
    spread = max(b1.values()) - min(b1.values())
    # the star, if it is one of the fitted columns, measured against the rest
    star_gap = None
    star_rank = None
    if star in b1:
        others = [b1[k] for k in names if k != star]
        star_gap = b1[star] - (_median(others) if others else 0.0)
        star_rank = 1 + sum(1 for k in names if b1[k] < b1[star])

    base = {"columns": names, "b1": b1, "crossed": crossed,
            "median_within_band_width": med_width,
            "column_spread": spread,
            "spread_over_band": (spread / med_width) if med_width else None,
            "star": star, "star_gap_to_median_others": star_gap,
            "star_rank_by_b1": star_rank,
            "star_band_width": _width(ok[star]) if star in ok else None,
            "all_decided": len(ok) == len(cols or {})}

    if not crossed:
        base["verdict"] = "nothing_outside_own_null"
        return base
    if len(crossed) == 1:
        only = crossed[0]
        others = [b1[k] for k in names if k != only]
        gap = b1[only] - (_median(others) if others else 0.0)
        base["verdict"] = "column_specific"
        base["specific_column"] = only
        base["specific_gap_to_median_others"] = gap
        base["specific_is_star"] = (only == star)
        # SEPARATION, published beside the frozen label. "Exactly one column crossed" is not
        # the same statement as "this column is an outlier": in a cell with fewer sessions the
        # other columns fall just inside their own bands while carrying the SAME sign, and one
        # crossing is then a power reading rather than a channel. The gap must clear one band
        # width before the lone crossing may be read as anybody's own flow.
        base["specific_gap_over_band"] = (abs(gap) / med_width) if med_width else None
        base["specific_is_separated"] = bool(med_width and abs(gap) > med_width)
        return base
    signs = {_sign(b1[k]) for k in crossed}
    cs = [b1[k] for k in crossed]
    crossed_spread = max(cs) - min(cs)
    base["crossed_spread"] = crossed_spread
    if len(signs) == 1 and med_width is not None and crossed_spread <= med_width:
        base["verdict"] = "book_wide_same_sign"
        base["crossed_sign"] = list(signs)[0]
        return base
    base["verdict"] = "multiple_crossings_differ"
    base["crossed_signs"] = sorted(signs)
    return base


def pairwise_corr(panel, syms):
    """Disclosure: how alike are the five turnover series the columns are read from?"""
    out = {}
    mats = {s: np.asarray(panel["dx"][s], dtype=float) for s in syms}
    for i, a in enumerate(syms):
        for b in syms[i + 1:]:
            x, y = mats[a], mats[b]
            n = min(len(x), len(y))
            if n < 10:
                continue
            xa, ya = x[-n:], y[-n:]
            sx, sy = xa.std(), ya.std()
            if sx <= 0 or sy <= 0:
                continue
            out["%s~%s" % (a, b)] = float(((xa - xa.mean()) * (ya - ya.mean())).mean()
                                          / (sx * sy))
    return out


def _cell(per, syms, lo=None, hi=None, label="", kind="window", note=None, star_override=None,
          draws=COLUMN_DRAWS):
    syms = [s for s in syms if per.get(s) and len(per[s]) > 2]
    out = {"label": label, "kind": kind, "members": list(syms),
           "window_inclusive": [lo, hi], "note": note, "draws": draws}
    if len(syms) < 3:
        out.update({"decided": False, "reason": "fewer than three members in this window"})
        return out
    win = e243.subset_per(per, syms, lo, hi)
    _, panel = e240.common_increments(win, syms)
    dates = panel.get("dates") or []
    out["sessions"] = len(dates)
    out["first"] = dates[0] if dates else None
    out["last"] = dates[-1] if dates else None
    if len(dates) < MIN_SESSIONS:
        out.update({"decided": False,
                    "reason": "common grid has %d sessions (floor %d)"
                              % (len(dates), MIN_SESSIONS)})
        return out

    # the star is named by E246's published lag-0 rule, the same object E248 read
    rows0 = [e248.fit_row_zero(panel, syms, m) for m in syms]
    decided0 = [r for r in rows0 if r.get("decided")]
    star = None
    star_source = "no_star_at_lag0"
    if len(decided0) >= 3:
        columns0 = [e246._column(decided0, j) for j in syms]
        mags = sorted(c["mean_abs_slope"] for c in columns0 if c["mean_abs_slope"] is not None)
        median_mag = mags[len(mags) // 2] if mags else 0.0
        stars = [c for c in columns0
                 if c.get("decisive_share") is not None
                 and c["decisive_share"] >= e245.STAR_DECISIVE_SHARE
                 and c["mean_abs_slope"] is not None
                 and c["mean_abs_slope"] >= e245.STAR_MIN_ABS_SLOPE
                 and (median_mag <= 0.0 or c["mean_abs_slope"] >= e245.STAR_RATIO_MIN * median_mag)]
        stars.sort(key=lambda c: (-c["decisive_share"], -c["mean_abs_slope"]))
        if stars:
            star = stars[0]["one_of"]
            star_source = "e245_star_rule"
    if star_override:
        star = star_override if star_override in syms else star
        star_source = "caller_override"

    cols = column_sweep(panel, syms, draws=draws)
    d = derive_verdict(cols, star)
    out.update({"decided": True, "star": star, "star_source": star_source,
                "columns_read": cols, "verdict": d["verdict"], "decision": d,
                "dx_pairwise_corr": pairwise_corr(panel, syms)})
    return out


def rollup(cells):
    counted = [c for c in cells if c.get("decided") and c.get("kind") in COUNTED_KINDS]
    by = {}
    for c in counted:
        by.setdefault(c["verdict"], []).append(c["label"])
    head = next((c for c in cells if c["label"] == "all_five"), {})
    if not counted:
        verdict = "unresolved_too_few_rows"
    elif len(by) == 1:
        verdict = counted[0]["verdict"]
    else:
        era_v = {c["verdict"] for c in counted if c["kind"] == "era"}
        verdict = "verdict_era_dependent" if len(era_v) > 1 else "verdict_mixed_across_cells"
    return {"cells_counted": len(counted), "cells_by_verdict": by, "verdict": verdict,
            "headline_verdict": head.get("verdict"),
            "headline_star": head.get("star"),
            "headline_decision": head.get("decision"),
            "stable_across_cells": len(by) == 1,
            "overlapping_cells_note": "the era cells overlap in time, so a verdict that repeats "
                                      "is corroboration, not replication (E244 caveat)"}


def reclassify(cell):
    """Post-hoc reading of a `column_specific` cell, published beside the frozen verdict.

    Frozen vocabulary first (a cell labelled column_specific stays labelled that in `cells` and
    `rollup`); this block asks the second question -- was the lone crossing SEPARATED from the
    other columns, or only the one that cleared its own null? A cell whose other columns carry
    the same sign, sit inside the same band width, and where the crossing column's gap to their
    median is smaller than that band width is a power reading, not a channel.
    """
    d = (cell.get("decision") or {})
    if not cell.get("decided"):
        return None
    if d.get("verdict") != "column_specific":
        return {"frozen_verdict": d.get("verdict"), "post_hoc": d.get("verdict"),
                "reason": None}
    sep = d.get("specific_is_separated")
    ratio = d.get("specific_gap_over_band")
    b1 = d.get("b1") or {}
    others = [v for k, v in b1.items() if k != d.get("specific_column")]
    same_sign = bool(others) and all(_sign(v) == _sign(b1.get(d.get("specific_column")))
                                     for v in others)
    if sep:
        return {"frozen_verdict": "column_specific", "post_hoc": "column_specific",
                "specific_column": d.get("specific_column"),
                "specific_gap_over_band": ratio,
                "reason": "the lone crossing is separated from the other columns by more than "
                          "one band width"}
    if same_sign:
        return {"frozen_verdict": "column_specific", "post_hoc": "book_wide_same_sign",
                "specific_column": d.get("specific_column"),
                "specific_gap_over_band": ratio,
                "reason": "every column carries the same sign and the lone crossing sits "
                          "inside one band width of their median (gap/band %s): the other "
                          "columns fell just inside their own nulls, so this cell is a POWER "
                          "reading, not a channel" % _fmt(ratio)}
    return {"frozen_verdict": "column_specific", "post_hoc": "column_specific",
            "specific_column": d.get("specific_column"),
            "specific_gap_over_band": ratio,
            "reason": "the lone crossing clears one band width but the other columns do not "
                      "share its sign, so separation cannot be decided from this cell alone"}


def rollup_post_hoc(cells, frozen_rollup):
    """The same counted cells under the separation reading, with the frozen verdict kept."""
    counted = [c for c in cells if c.get("decided") and c.get("kind") in COUNTED_KINDS]
    by = {}
    for c in counted:
        r = reclassify(c) or {}
        by.setdefault(r.get("post_hoc") or c.get("verdict"), []).append(c["label"])
    head = next((c for c in cells if c.get("label") == "all_five"), {})
    verdict = "unresolved_too_few_rows" if not counted else \
        (list(by)[0] if len(by) == 1 else "verdict_mixed_across_cells")
    reclassified = [{"cell": c["label"],
                     "frozen": (reclassify(c) or {}).get("frozen_verdict"),
                     "post_hoc": (reclassify(c) or {}).get("post_hoc"),
                     "gap_over_band": (reclassify(c) or {}).get("specific_gap_over_band"),
                     "reason": (reclassify(c) or {}).get("reason")}
                    for c in counted
                    if (reclassify(c) or {}).get("post_hoc")
                    != (reclassify(c) or {}).get("frozen_verdict")]
    head_r = reclassify(head) or {}
    return {"verdict": verdict,
            "cells_by_verdict": by,
            "cells_counted": len(counted),
            "reclassified": reclassified,
            "headline_post_hoc": head_r.get("post_hoc"),
            "headline_frozen": head_r.get("frozen_verdict"),
            "stable_across_cells": len(by) == 1,
            "frozen_verdict_kept": frozen_rollup.get("verdict"),
            "note": "the frozen vocabulary is unchanged; this block adds the separation test "
                    "the frozen label cannot express, and names every cell it moves",
            "overlapping_cells_note": "the era cells overlap in time, so a verdict that repeats "
                                      "is corroboration, not replication (E244 caveat)"}


def e248_reproduction():
    """Does this sweep reproduce the published -0.586 on the column E248 named?

    A cross-face check, not a gate: if the star's lag-1 here disagreed with E248's published
    number the sweep would be measuring something else, and every comparison below would be
    a comparison between two different designs.
    """
    path = os.path.join(OUTDIR, "starlagband_latest.json")
    if not os.path.exists(path):
        return {"available": False, "reason": "starlagband_latest.json absent"}
    try:
        with open(path, "r", encoding="utf-8") as fh:
            prev = json.load(fh)
    except (OSError, ValueError) as exc:
        return {"available": False, "reason": "%s: %s" % (type(exc).__name__, exc)}
    head = next((c for c in (prev.get("cells") or []) if c.get("label") == "all_five"), {})
    return {"available": True,
            "e248_star": head.get("star"),
            "e248_lag1": (head.get("lag_column") or {}).get("lag1"),
            "e248_cutoff": prev.get("evidence_cutoff"),
            "e248_family_line": ((head.get("band_family") or {}).get("max_abs"))}


def run(save=True, per=None, outdir=None, basket=None, panels=None, star=None,
        draws=COLUMN_DRAWS, era_draws=ERA_DRAWS, cells=None):
    per = per if per is not None else e239.panels(panels)
    syms = [s for s in (basket or BASKET) if per.get(s)]
    outdir = outdir or OUTDIR
    out_cells = []
    for label, kind, lo, hi, members in (cells if cells is not None else CELLS):
        these = [s for s in (members or syms) if s in syms]
        out_cells.append(_cell(per, these, lo, hi, label=label, kind=kind,
                               star_override=star,
                               draws=draws if kind == "headline" else era_draws))
    dates = sorted({d for s in syms for d in per[s]})
    face = {"study": STUDY,
            "title": "per-column lag-1 counterfactual: one sleeve's flow, or a book-wide number",
            "generated": datetime.now().isoformat(timespec="seconds"),
            "evidence_cutoff": dates[-1] if dates else None,
            "frozen_spec": {"lags": list(LAGS),
                            "column_draws": COLUMN_DRAWS,
                            "era_draws": ERA_DRAWS,
                            "band_mode": BAND_MODE,
                            "family_wise_line": "a column must exceed the largest |coefficient| "
                                                "any shuffled draw of THAT column produced "
                                                "anywhere in lags 1..5 (E248's line, per column)",
                            "min_sessions": MIN_SESSIONS,
                            "verdicts": list(VERDICTS),
                            "base_seed": BASESEED,
                            "reuse": "estimator, band and star rule are E248/E245/E246 verbatim"},
            "members": syms,
            "cells": out_cells,
            "e248_reproduction_ref": e248_reproduction(),
            "no_bill": "channel separation only: no adoption, no re-pricing, and a book-wide "
                       "negative lead may not be billed to any sleeve"}
    face["rollup"] = rollup(out_cells)
    face["rollup_post_hoc"] = rollup_post_hoc(out_cells, face["rollup"])
    face["summary"] = _summary(face)
    if save:
        face["written"] = _write(face, outdir)
    return face


def _summary(face):
    roll = face["rollup"]
    head = next((c for c in face["cells"] if c.get("label") == "all_five"), {})
    d = head.get("decision") or {}
    return {"verdict": roll["verdict"],
            "headline_verdict": head.get("verdict"),
            "headline_star": head.get("star"),
            "columns": d.get("columns"),
            "b1": d.get("b1"),
            "crossed": d.get("crossed"),
            "column_spread": d.get("column_spread"),
            "median_within_band_width": d.get("median_within_band_width"),
            "spread_over_band": d.get("spread_over_band"),
            "star_gap_to_median_others": d.get("star_gap_to_median_others"),
            "star_rank_by_b1": d.get("star_rank_by_b1"),
            "specific_column": d.get("specific_column"),
            "cells_counted": roll["cells_counted"],
            "stable_across_cells": roll["stable_across_cells"],
            "cells_by_verdict": roll["cells_by_verdict"],
            "rollup_post_hoc_verdict": (face.get("rollup_post_hoc") or {}).get("verdict"),
            "cells_by_verdict_post_hoc": (face.get("rollup_post_hoc") or {}).get("cells_by_verdict"),
            "post_hoc_reclassified": (face.get("rollup_post_hoc") or {}).get("reclassified"),
            "e248_reproduction": face.get("e248_reproduction_ref"),
            "one_line": _answer(face)}


def _answer(face):
    roll = face["rollup"]
    head = next((c for c in face["cells"] if c.get("label") == "all_five"), {})
    d = head.get("decision") or {}
    star = head.get("star") or "the star"
    v = roll["verdict"]
    b1 = d.get("b1") or {}
    def sig(k):
        x = b1.get(k)
        return "n/a" if x is None else "%+.3f" % x
    cols = ", ".join("%s %s" % (k, sig(k)) for k in (d.get("columns") or []))
    if v == "nothing_outside_own_null":
        return ("no column's lag-1 reaches its own %d-draw shuffled band (%s): the single "
                "crossing E248 published does not survive as a specific channel"
                % (COLUMN_DRAWS, cols))
    if v == "column_specific":
        only = d.get("specific_column")
        gap = d.get("specific_gap_to_median_others")
        return ("the negative lead is COLUMN-SPECIFIC to %s (lag1 %s against a median of the "
                "other four at %s, gap %s vs a within-column band of %s)=%s"
                % (only, sig(only),
                   "n/a" if gap is None else "%+.3f" % ((b1.get(only) or 0.0) - gap),
                   "n/a" if gap is None else "%+.3f" % gap,
                   _fmt(d.get("median_within_band_width")),
                   "the named sleeve's own flow" if d.get("specific_is_star")
                   else "NOT the star named by the lag-0 rule"))
    if v == "book_wide_same_sign":
        return ("every crossing shares a sign and the columns sit within one band width of each "
                "other (spread %s vs band %s): this is a BOOK-WIDE number (%s), not a sleeve's "
                "flow, so no member may be billed for it"
                % (_fmt(d.get("column_spread")), _fmt(d.get("median_within_band_width")), cols))
    if v == "multiple_crossings_differ":
        return ("several columns cross but they disagree in sign or spread wider than the band "
                "(spread %s vs band %s): the lead is not one number and not one sleeve (%s)"
                % (_fmt(d.get("column_spread")), _fmt(d.get("median_within_band_width")), cols))
    if v in ("verdict_mixed_across_cells", "verdict_era_dependent"):
        parts = ["%s=%d" % (k, len(v_)) for k, v_ in sorted(roll["cells_by_verdict"].items())]
        ph = (face.get("rollup_post_hoc") or {})
        moved = ph.get("reclassified") or []
        if moved and ph.get("verdict") in [x.get("post_hoc") for x in moved]:
            return ("the frozen cells split (%s), but every cell is one sign and the cells "
                    "labelled column_specific are the low-power ones: their lone crossing sits "
                    "inside one band width of the other columns (gap/band %s), so the reading "
                    "is BOOK-WIDE (%s) and no member may be billed for it"
                    % (", ".join(parts),
                       ", ".join("%s %s" % (m["cell"], _fmt(m["gap_over_band"])) for m in moved),
                       ph.get("verdict")))
        return "the cells do not read the same way (%s)" % ", ".join(parts)
    return "no verdict resolved in any counted cell (%d counted)" % roll["cells_counted"]


def _write(face, outdir):
    os.makedirs(outdir, exist_ok=True)
    name = "LEADCOUNTER-" + str(face.get("evidence_cutoff") or "unknown") + ".json"
    for fn in (name, "leadcounter_latest.json"):
        with open(os.path.join(outdir, fn), "w", encoding="utf-8", newline="\n") as fh:
            json.dump(face, fh, ensure_ascii=False, indent=1)
    return name


def _fmt(v):
    return "n/a" if v is None else "%.3f" % v


# ---------------------------------------------------------------- fixtures
def _fake_cols(b1s, widths=None, outside=None, star=None):
    """A column dict as `column_sweep` would publish it, so the gate can be tested directly."""
    widths = widths or {}
    out = {}
    for k, v in b1s.items():
        w = widths.get(k, 0.2)
        out[k] = {"decided": True, "b1": v,
                  "band_lag1": {"lo": -w / 2.0, "hi": w / 2.0, "width": w},
                  "outside_own_band": (outside or {}).get(k, False)}
    return out


SMALL_CELLS = (("all_five", "headline", None, None, None),)


def _run(per, star="S0", draws=40, era_draws=20):
    return run(save=False, per=per, basket=sorted(per), star=star, draws=draws,
               era_draws=era_draws, cells=SMALL_CELLS)


def _head(face, label="all_five"):
    return next((c for c in face["cells"] if c["label"] == label), {})


# ---------------------------------------------------------------- selftest
def selftest():
    legs = []

    def leg(name, fn):
        try:
            ok, detail = fn()
        except Exception as exc:  # noqa: BLE001 - a leg that raises is a red leg
            ok, detail = False, "%s: %s" % (type(exc).__name__, exc)
        legs.append({"leg": name, "ok": bool(ok), "detail": detail})

    def vocabulary_separates():
        # four readings that must not collapse into one label
        book = _fake_cols({"a": -0.5, "b": -0.55, "c": -0.45, "d": -0.52, "e": -0.48},
                          widths={k: 0.3 for k in "abcde"},
                          outside={k: True for k in "abcde"})
        spec = _fake_cols({"a": -0.60, "b": -0.05, "c": -0.02, "d": -0.03, "e": -0.01},
                          widths={k: 0.2 for k in "abcde"}, outside={"a": True})
        none = _fake_cols({"a": -0.10, "b": -0.08, "c": -0.12, "d": -0.05, "e": -0.09},
                          widths={k: 0.4 for k in "abcde"})
        diff = _fake_cols({"a": -0.60, "b": 0.55, "c": -0.02, "d": 0.01, "e": -0.03},
                          widths={k: 0.2 for k in "abcde"}, outside={"a": True, "b": True})
        got = [derive_verdict(x, star="a")["verdict"] for x in (book, spec, none, diff)]
        want = ["book_wide_same_sign", "column_specific", "nothing_outside_own_null",
                "multiple_crossings_differ"]
        return got == want, " / ".join(got)

    def book_wide_refuses_a_bill():
        # the point of the vocabulary: a same-sign set inside one band width must not be
        # readable as a sleeve's own flow, even though every column crosses
        d = derive_verdict(_fake_cols({"a": -0.5, "b": -0.55, "c": -0.45, "d": -0.52, "e": -0.48},
                                      widths={k: 0.3 for k in "abcde"},
                                      outside={k: True for k in "abcde"}), star="a")
        return (d["verdict"] == "book_wide_same_sign"
                and d["spread_over_band"] is not None
                and d["spread_over_band"] <= 1.0), \
            "spread/band=%.3f" % (d.get("spread_over_band") or -1)

    def spread_uses_measured_band():
        # a spread that is large must be large RELATIVE to the measured within-column band,
        # not an absolute constant: same numbers, wider band, different verdict
        tight = _fake_cols({"a": -0.60, "b": -0.55, "c": -0.50, "d": -0.58, "e": -0.52},
                           widths={k: 0.05 for k in "abcde"},
                           outside={k: True for k in "abcde"})
        wide = _fake_cols({"a": -0.60, "b": -0.55, "c": -0.50, "d": -0.58, "e": -0.52},
                          widths={k: 0.60 for k in "abcde"},
                          outside={k: True for k in "abcde"})
        return (derive_verdict(tight, star="a")["verdict"] == "multiple_crossings_differ"
                and derive_verdict(wide, star="a")["verdict"] == "book_wide_same_sign"), \
            "%s / %s" % (derive_verdict(tight, star="a")["verdict"],
                         derive_verdict(wide, star="a")["verdict"])

    def star_specific_label():
        d = derive_verdict(_fake_cols({"a": -0.60, "b": -0.05, "c": -0.02, "d": -0.03, "e": -0.01},
                                      widths={k: 0.2 for k in "abcde"}, outside={"a": True}),
                           star="a")
        return (d["verdict"] == "column_specific" and d["specific_is_star"] is True
                and d["specific_column"] == "a"), "%s/%s" % (d["verdict"], d.get("specific_is_star"))

    def non_star_specific_label():
        # the honest alternative: another column is the outlier and the star is not it
        d = derive_verdict(_fake_cols({"a": -0.05, "b": -0.60, "c": -0.02, "d": -0.03, "e": -0.01},
                                      widths={k: 0.2 for k in "abcde"}, outside={"b": True}),
                           star="a")
        return (d["verdict"] == "column_specific" and d["specific_is_star"] is False
                and d["specific_column"] == "b"), "%s/%s" % (d["verdict"], d.get("specific_column"))

    def too_few_columns():
        d = derive_verdict(_fake_cols({"a": -0.5, "b": -0.4},
                                      widths={k: 0.2 for k in "ab"},
                                      outside={k: True for k in "ab"}), star="a")
        return d["verdict"] == "unresolved_too_few_rows", d["verdict"]

    def undecided_column_is_not_a_zero():
        cols = _fake_cols({"a": -0.5, "b": -0.5, "c": -0.5, "d": -0.5},
                          widths={k: 0.2 for k in "abcd"}, outside={k: True for k in "abcd"})
        cols["e"] = {"decided": False, "reason": "HAC fit refused"}
        d = derive_verdict(cols, star="a")
        return (d["verdict"] == "book_wide_same_sign" and d["all_decided"] is False
                and "e" not in d["columns"]), "%s all_decided=%s" % (d["verdict"],
                                                                     d["all_decided"])

    def sweep_moves_every_column():
        # r1261 family: prove the mechanism actually moved. A sweep that returned the same
        # number for all five columns would pass every gate above while measuring nothing.
        per = e248.synth(n=520, lead={(m, 0, 1): -0.5 for m in range(1, 5)})
        face = _run(per, star="S0")
        cols = (_head(face).get("decision") or {}).get("b1") or {}
        vals = [round(v, 6) for v in cols.values()]
        return (len(vals) == 5 and len(set(vals)) >= 3), "distinct %d of %d" % (len(set(vals)),
                                                                                len(vals))

    def star_column_is_negative_on_a_star_lead():
        # the fixture carries a negative lead from S0 only; the S0 column must read it and the
        # other columns must not be pulled to the same value
        per = e248.synth(n=520, lead={(m, 0, 1): -0.5 for m in range(1, 5)})
        face = _run(per, star="S0")
        d = _head(face).get("decision") or {}
        b1 = d.get("b1") or {}
        others = [b1.get(k) or 0.0 for k in ("S1", "S2", "S3", "S4")]
        return ((b1.get("S0") or 0.0) < -0.25 and max(others) < 0.15
                and d.get("verdict") in ("column_specific", "multiple_crossings_differ")), \
            "S0=%s others=%s verdict=%s" % (_fmt(b1.get("S0")),
                                            [_fmt(x) for x in others], d.get("verdict"))

    def book_wide_fixture_reads_book_wide():
        # every member's move responds to every column's lagged flow: the columns must agree
        per = e248.synth(n=520,
                         lead={(m, j, 1): -0.30 for m in range(5) for j in range(5) if m != j})
        face = _run(per, star="S0")
        d = _head(face).get("decision") or {}
        b1 = d.get("b1") or {}
        vals = [v for v in b1.values() if v is not None]
        spread = (max(vals) - min(vals)) if vals else None
        return (len(vals) == 5 and spread is not None and spread < 0.35
                and all(v < 0 for v in vals)), \
            "spread=%s b1=%s verdict=%s" % (_fmt(spread), [_fmt(v) for v in vals],
                                            d.get("verdict"))

    def gate_recomputes_from_face():
        per = e248.synth(n=460, lead={(m, 0, 1): -0.4 for m in range(1, 5)})
        face = _run(per, star="S0")
        bad = []
        for c in [x for x in face["cells"] if x.get("decided")]:
            d = derive_verdict(c.get("columns_read") or {}, c.get("star"))
            if d["verdict"] != c.get("verdict"):
                bad.append("%s: numbers say %s, face says %s" % (c["label"], d["verdict"],
                                                                 c.get("verdict")))
        return not bad, "; ".join(bad) or "all cells recompute"

    def deterministic_and_order_invariant():
        per = e248.synth(n=360, lead={(1, 0, 1): -0.4}, members=4)
        a = run(save=False, per=per, basket=["S0", "S1", "S2", "S3"], star="S0", draws=20,
                era_draws=10, cells=SMALL_CELLS)
        b = run(save=False, per=per, basket=["S0", "S1", "S2", "S3"], star="S0", draws=20,
                era_draws=10, cells=SMALL_CELLS)
        c = run(save=False, per=per, basket=["S3", "S2", "S1", "S0"], star="S0", draws=20,
                era_draws=10, cells=SMALL_CELLS)
        ba = (_head(a).get("decision") or {}).get("b1") or {}
        bb = (_head(b).get("decision") or {}).get("b1") or {}
        bc = (_head(c).get("decision") or {}).get("b1") or {}
        ok = (ba == bb and all(abs((ba[k] or 0.0) - (bc[k] or 0.0)) < 1e-12 for k in ba))
        return ok, "same=%s invariant=%s" % (ba == bb,
                                             all(abs((ba[k] or 0.0) - (bc[k] or 0.0)) < 1e-12
                                                 for k in ba))

    def too_few_sessions_undecided():
        head = _head(_run(e248.synth(n=60, members=4), star="S0"))
        return (head.get("decided") is False and "sessions" in (head.get("reason") or "")), \
            head.get("reason")

    def bands_are_measured_per_column():
        # each column must carry its OWN band; five copies of one band would make the
        # specificity test compare a number to itself
        per = e248.synth(n=420, star_ar=0.5)
        face = _run(per, star="S0", draws=30)
        cols = (_head(face).get("columns_read") or {})
        widths = [c["band_lag1"]["width"] for c in cols.values()
                  if c.get("decided") and c.get("band_lag1")]
        return (len(widths) == 5 and len({round(w, 6) for w in widths}) >= 3), \
            "widths %s" % [round(w, 4) for w in widths]

    def per_member_spread_published():
        face = run(save=False, per=e248.synth(n=300, lead={(1, 0, 1): -0.4}, members=4),
                   basket=["S0", "S1", "S2", "S3"], star="S0", draws=12, era_draws=8,
                   cells=SMALL_CELLS)
        cols = (_head(face).get("columns_read") or {})
        ok = all(c.get("members_fitted", 0) == 3 and c.get("per_member_b1")
                 and c.get("per_member_b1_spread") is not None
                 for c in cols.values() if c.get("decided"))
        return ok, "members fitted %s" % [c.get("members_fitted") for c in cols.values()
                                          if c.get("decided")]

    def lone_crossing_inside_band_is_power_not_channel():
        # the defect this leg exists for: five same-sign columns, one clears its null, and the
        # gap to the others is a third of a band -- "exactly one crossing" must NOT be read as
        # a channel, and the post-hoc block must say so while the frozen label stays put
        d = derive_verdict(_fake_cols({"a": -0.315, "b": -0.276, "c": -0.181, "d": -0.042},
                                      widths={k: 0.306 for k in "abcd"}, outside={"a": True}),
                           star="a")
        cell = {"label": "x", "kind": "era", "decided": True, "decision": d}
        r = reclassify(cell)
        return (d["verdict"] == "column_specific" and d["specific_is_separated"] is False
                and r["post_hoc"] == "book_wide_same_sign"), \
            "gap/band=%s post_hoc=%s" % (_fmt(d.get("specific_gap_over_band")), r["post_hoc"])

    def separated_lone_crossing_stays_specific():
        # the control: with a two-band gap the same shape IS a channel, so the leg above is a
        # statement about separation and not a blanket refusal of the label
        d = derive_verdict(_fake_cols({"a": -0.90, "b": -0.05, "c": -0.02, "d": -0.03},
                                      widths={k: 0.2 for k in "abcd"}, outside={"a": True}),
                           star="a")
        r = reclassify({"label": "x", "kind": "era", "decided": True, "decision": d})
        return (d["verdict"] == "column_specific" and d["specific_is_separated"] is True
                and r["post_hoc"] == "column_specific"), \
            "gap/band=%s post_hoc=%s" % (_fmt(d.get("specific_gap_over_band")), r["post_hoc"])

    def post_hoc_names_every_cell_it_moves():
        cells = [{"label": "h", "kind": "headline", "decided": True,
                  "decision": derive_verdict(_fake_cols({"a": -0.315, "b": -0.276, "c": -0.181,
                                                         "d": -0.042},
                                                        widths={k: 0.306 for k in "abcd"},
                                                        outside={"a": True}), star="a")},
                 {"label": "e", "kind": "era", "decided": True,
                  "decision": derive_verdict(_fake_cols({"a": -0.9, "b": -0.05, "c": -0.02,
                                                         "d": -0.03},
                                                        widths={k: 0.2 for k in "abcd"},
                                                        outside={"a": True}), star="a")}]
        ph = rollup_post_hoc(cells, {"verdict": "column_specific"})
        moved = [m["cell"] for m in ph["reclassified"]]
        ok = (moved == ["h"])
        return ok, "moved=%s by=%s" % (moved, {k: len(v_) for k, v_ in ph["cells_by_verdict"].items()})

    leg("the vocabulary separates book-wide, specific, null and mixed", vocabulary_separates)
    leg("a same-sign set inside one band width refuses a per-sleeve bill",
        book_wide_refuses_a_bill)
    leg("spread is judged against the measured band, not an absolute constant",
        spread_uses_measured_band)
    leg("a single crossing on the star is labelled star-specific", star_specific_label)
    leg("a single crossing on another column is labelled, not credited to the star",
        non_star_specific_label)
    leg("fewer than three decided columns is undecided", too_few_columns)
    leg("an undecided column is dropped, not read as a zero", undecided_column_is_not_a_zero)
    leg("the sweep moves every column (the mechanism actually ran)", sweep_moves_every_column)
    leg("a star-only negative lead reads as the star's column, not the others",
        star_column_is_negative_on_a_star_lead)
    leg("a book-wide fixture reads book-wide, not specific", book_wide_fixture_reads_book_wide)
    leg("the gate recomputes every verdict from the published columns", gate_recomputes_from_face)
    leg("same input and member order publish the same readings", deterministic_and_order_invariant)
    leg("too few sessions is undecided, not empty-green", too_few_sessions_undecided)
    leg("each column carries its own shuffled band", bands_are_measured_per_column)
    leg("per-member b1 and its spread are published", per_member_spread_published)
    leg("a lone crossing inside one band width is a power reading, not a channel",
        lone_crossing_inside_band_is_power_not_channel)
    leg("a lone crossing separated by more than a band stays specific",
        separated_lone_crossing_stays_specific)
    leg("the post-hoc block names every cell it moves", post_hoc_names_every_cell_it_moves)

    n_ok = sum(1 for l_ in legs if l_["ok"])
    print("selftest: %d/%d" % (n_ok, len(legs)))
    for l_ in legs:
        print(("  PASS " if l_["ok"] else "  FAIL ") + l_["leg"] + " :: " + str(l_["detail"])[:220])
    return 0 if n_ok == len(legs) else 1


def main(argv=None):
    ap = argparse.ArgumentParser(description="E249 per-column lead counterfactual")
    ap.add_argument("cmd", nargs="?", default="run", choices=("run", "selftest"))
    ap.add_argument("--draws", type=int, default=COLUMN_DRAWS)
    ap.add_argument("--era-draws", type=int, default=ERA_DRAWS)
    args = ap.parse_args(argv)
    if args.cmd == "selftest":
        return selftest()
    face = run(save=True, draws=args.draws, era_draws=args.era_draws)
    s = face["summary"]
    print("verdict: %s (headline %s)" % (s["verdict"], s["headline_verdict"]))
    print("star: %s  b1: %s" % (s["headline_star"], s["b1"]))
    print("crossed: %s  spread: %s  band: %s  spread/band: %s"
          % (s["crossed"], _fmt(s["column_spread"]), _fmt(s["median_within_band_width"]),
             _fmt(s["spread_over_band"])))
    print("e248 ref: %s" % (s["e248_reproduction"] or {}))
    print(s["one_line"])
    print("written: %s" % face.get("written"))
    return 0


if __name__ == "__main__":
    sys.exit(main())