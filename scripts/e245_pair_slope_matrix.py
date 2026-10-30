#!/usr/bin/env python3
"""E245 -- publish the full cross-member slope matrix before any "rest channel" is named again.

E244 located the spread on the counterparty identity (50.7% counterparty / 0.1% own / 49%
residual) but it could only read the intervals E243 had already published, and those came out of
a SUM design: `rest` is one member against an average of the others, so twenty ordered pairs
report numbers no single counterparty ever produced. The unfiltered object is the slope matrix:

    dy_m = a + b_own * dlog(own turnover_m) + sum_{j != m} b_mj * dlog(turnover_j) + e

one slope per counterparty, no sum regressor, no kappa. Per cell this face publishes:

  * the full k x (k-1) matrix with a HAC interval per cell,
  * a Wald test of ROW EQUALITY (one coherent rest channel: all b_mj equal for fixed m),
  * COLUMN CONCENTRATION (one counterparty that is decisive for many members),
  * the matrix analogue of E243's difference: b_mj minus the mean of the row's other slopes,
    which is the same object the sum design priced, quotes without kappa,
  * the resolution the matrix actually carries (median CI half-width).

The matrix is fitted jointly per row, so the row-equality test has a covariance to work with.
Cells overlap in time (E244's own caveat): repeats are not replications, and the rollup says so.

NO BILL, NO ADOPTION, NO RE-PRICING. This face names structure; it prices nothing.
"""

from __future__ import annotations

import argparse
import json
import math
import os
import random
import sys
from datetime import datetime

HERE = os.path.dirname(os.path.abspath(__file__))
if HERE not in sys.path:
    sys.path.insert(0, HERE)

import e222_tom_overlay as e222  # noqa: E402
import e225_state_tilt as e225  # noqa: E402
import e235_charge_granularity as e235  # noqa: E402
import e239_own_vs_cross as e239  # noqa: E402
import e240_aggregate_attenuation as e240  # noqa: E402
import e243_additivity_out_of_sample as e243  # noqa: E402

ROOT = e222.ROOT
OUTDIR = os.path.join(ROOT, "results", "state_tilt")
BASKET = e225.BASKET
NW_LAG = e225.NW_LAG
Z95 = 1.96
MIN_SESSIONS = e240.MIN_SESSIONS
STUDY = "E245"

# frozen before the face was read
ROW_EQUALITY_ALPHA = 0.05
RESOLUTION_MAX = 0.30        # median CI half-width above which no cell can name a structure
STAR_DECISIVE_SHARE = 0.50   # one counterparty must be decisive for half of its members
STAR_MIN_ABS_SLOPE = 0.10    # and its mean slope must exceed a tenth of a log point
STAR_RATIO_MIN = 2.0         # and be at least twice the median column, or "star" is just "signal"
COUNTED_KINDS = ("headline", "window", "era", "neighbour")

CHI2_95 = {1: 3.841, 2: 5.991, 3: 7.815, 4: 9.488, 5: 11.070, 6: 12.592,
           7: 14.067, 8: 15.507, 9: 16.919, 10: 18.307}

VERDICTS = ("coherent_rest_channel",
            "counterparty_concentration",
            "heterogeneous_rows",
            "unresolved_matrix_too_wide",
            "unresolved_insufficient_rows")

CELLS = (("all_five", "headline", None, None, None),
         # the four members that exist before sh588000 prints; passing all five would intersect
         # to an empty grid and the cell would silently publish zero sessions
         ("pre2020_four", "window", None, "2020-11-15",
          ("sh510050", "sh510300", "sh510500", "sh512100")),
         ("era_2020_2022", "era", "2020-11-16", "2022-12-31", None),
         ("era_2023_2024", "era", "2023-01-01", "2024-12-31", None),
         ("era_2025_now", "era", "2025-01-01", None, None),
         ("early_three", "neighbour", e243.EARLY_THREE_FROM, e243.EARLY_THREE_TO,
          e243.EARLY_THREE))


# ---------------------------------------------------------------- small linear algebra
def _inv_small(m):
    """Gauss-Jordan inverse of a small symmetric matrix; None when singular."""
    n = len(m)
    a = [list(map(float, row)) + [1.0 if i == j else 0.0 for j in range(n)] for i, row in enumerate(m)]
    for col in range(n):
        piv = max(range(col, n), key=lambda r: abs(a[r][col]))
        if abs(a[piv][col]) < 1e-14:
            return None
        a[col], a[piv] = a[piv], a[col]
        d = a[col][col]
        a[col] = [v / d for v in a[col]]
        for r in range(n):
            if r != col and a[r][col] != 0.0:
                f = a[r][col]
                a[r] = [a[r][c] - f * a[col][c] for c in range(2 * n)]
    return [row[n:] for row in a]


def wald_equal(betas, cov, idx):
    """Wald test that the coefficients at positions `idx` are all equal.

    R is built as successive differences against the first index, so df = len(idx) - 1 and the
    covariance of the differences comes straight out of the fitted covariance -- a per-pair
    comparison of intervals would ignore the correlations between the same row's slopes.
    """
    k = len(idx)
    if k < 2:
        return {"df": 0, "chi2": None, "critical_95": None, "reject": None,
                "reason": "fewer than two slopes in the row"}
    df = k - 1
    base = idx[0]
    R = []
    for pos in idx[1:]:
        row = [0.0] * len(betas)
        row[base] += 1.0
        row[pos] -= 1.0
        R.append(row)
    diff = [sum(row[i] * betas[i] for i in range(len(betas))) for row in R]
    RV = [[sum(sum(R[r][i] * cov[i][j] * R[c][j] for j in range(len(betas))) for i in range(len(betas)))
           for c in range(df)] for r in range(df)]
    inv = _inv_small(RV)
    if inv is None:
        return {"df": df, "chi2": None, "critical_95": CHI2_95.get(df), "reject": None,
                "reason": "difference covariance is singular"}
    chi2 = sum(diff[r] * inv[r][c] * diff[c] for r in range(df) for c in range(df))
    crit = CHI2_95.get(df)
    return {"df": df, "chi2": chi2, "critical_95": crit,
            "reject": (chi2 > crit) if crit is not None else None}


# ---------------------------------------------------------------- fits
def fit_row(panel, syms, m):
    """One member's move on its own turnover plus EVERY other member's, jointly."""
    others = [s for s in syms if s != m]
    y = panel["dy"][m]
    cols = [panel["dx"][m]] + [panel["dx"][j] for j in others]
    fit = e235._ols_hac_full(y, cols, NW_LAG)
    if fit is None:
        return {"own_of": m, "decided": False,
                "reason": "HAC fit refused (singular or too few rows)"}
    beta, cov = fit["beta"], fit["cov"]

    def ci(idx):
        var = cov[idx][idx]
        se = math.sqrt(var) if var is not None and var > 0 else None
        return (None if se is None else [beta[idx] - Z95 * se, beta[idx] + Z95 * se],
                (beta[idx] / se) if se else None)

    own_ci, own_t = ci(1)
    cells = []
    for pos, j in enumerate(others):
        idx = 2 + pos
        c, t = ci(idx)
        cells.append({"one_of": j, "slope": beta[idx], "ci": c, "t_nw": t,
                      "decisive": bool(c and not (c[0] <= 0.0 <= c[1]))})
    cross_idx = [2 + pos for pos in range(len(others))]
    row_mean = (sum(c["slope"] for c in cells) / len(cells)) if cells else None
    for c in cells:
        c["contrast_vs_row"] = (c["slope"] - row_mean) if row_mean is not None else None
    row = {"own_of": m, "decided": True, "rows_used": fit["n"], "r2": fit["r2"],
           "b_own": beta[1], "b_own_ci": own_ci, "b_own_t_nw": own_t,
           "cross": cells, "row_mean_cross": row_mean,
           "row_equal": wald_equal(beta, cov, cross_idx),
           "decisive_pairs": sum(1 for c in cells if c["decisive"])}
    return row


def cell_matrix(per, syms, lo=None, hi=None, label="", kind="window", note=None):
    syms = [s for s in syms if per.get(s) and len(per[s]) > 2]
    cell = {"label": label, "kind": kind, "members": list(syms),
            "window_inclusive": [lo, hi], "note": note}
    if len(syms) < 3:
        cell.update({"decided": False,
                     "reason": "fewer than three members have a panel in this window"})
        return cell
    win = e243.subset_per(per, syms, lo, hi)
    rows, panel = e240.common_increments(win, syms)
    dates = panel.get("dates") or []
    cell["sessions"] = len(dates)
    cell["first"] = dates[0] if dates else None
    cell["last"] = dates[-1] if dates else None
    if len(dates) < MIN_SESSIONS:
        cell.update({"decided": False,
                     "reason": "common grid has %d sessions (floor %d)"
                               % (len(dates), MIN_SESSIONS)})
        return cell
    fitted = [fit_row(panel, syms, m) for m in syms]
    decided = [r for r in fitted if r.get("decided")]
    cell["rows"] = fitted
    if len(decided) < 3:
        cell.update({"decided": False,
                     "reason": "only %d of %d rows could be fitted" % (len(decided), len(syms))})
        return cell

    halves = [abs(c["ci"][1] - c["ci"][0]) / 2.0
              for r in decided for c in r["cross"] if c["ci"]]
    median_half = sorted(halves)[len(halves) // 2] if halves else None
    reject_rows = [r["own_of"] for r in decided
                   if r["row_equal"].get("reject") is True]
    tested_rows = [r["own_of"] for r in decided if r["row_equal"].get("reject") is not None]

    columns = []
    for j in syms:
        slopes = [c for r in decided for c in r["cross"] if c["one_of"] == j]
        if not slopes:
            continue
        dec = [c for c in slopes if c["decisive"]]
        mean = sum(c["slope"] for c in slopes) / len(slopes)
        columns.append({"one_of": j, "members": len(slopes), "decisive": len(dec),
                        "decisive_share": len(dec) / float(len(slopes)),
                        "mean_slope": mean, "mean_abs_slope": sum(abs(c["slope"]) for c in slopes) / len(slopes),
                        "signs": sorted({1 if c["slope"] > 0 else -1 for c in dec})})
    # A star is a column that stands out from the OTHER columns, not merely one that is
    # decisive: with a real effect everywhere, every column is decisive and the ratio is ~1.
    mags = sorted(c["mean_abs_slope"] for c in columns)
    median_mag = mags[len(mags) // 2] if mags else 0.0
    stars = [c for c in columns
             if c["decisive_share"] >= STAR_DECISIVE_SHARE
             and c["mean_abs_slope"] >= STAR_MIN_ABS_SLOPE
             and (median_mag <= 0.0 or c["mean_abs_slope"] >= STAR_RATIO_MIN * median_mag)]
    stars.sort(key=lambda c: (-c["decisive_share"], -c["mean_abs_slope"]))

    if median_half is None:
        verdict = "unresolved_insufficient_rows"
    elif median_half > RESOLUTION_MAX:
        verdict = "unresolved_matrix_too_wide"
    elif stars:
        # a star makes its own rows unequal; naming the column is the more specific reading
        verdict = "counterparty_concentration"
    elif reject_rows:
        verdict = "heterogeneous_rows"
    else:
        verdict = "coherent_rest_channel"

    contrasts = [c["contrast_vs_row"] for r in decided for c in r["cross"]
                 if c.get("contrast_vs_row") is not None]
    cell.update({"decided": True,
                 "resolution_median_halfwidth": median_half,
                 "resolution_max": RESOLUTION_MAX,
                 "rows_tested_for_equality": tested_rows,
                 "rows_rejecting_equality": reject_rows,
                 "columns": columns,
                 "stars": [c["one_of"] for c in stars],
                 "matrix": {r["own_of"]: {c["one_of"]: c["slope"] for c in r["cross"]}
                            for r in decided},
                 "contrast_spread": ([min(contrasts), max(contrasts)] if contrasts else None),
                 "contrast_mean": (sum(contrasts) / len(contrasts)) if contrasts else None,
                 "verdict": verdict})
    return cell


# ---------------------------------------------------------------- previous faces
def _face(name):
    p = os.path.join(OUTDIR, name)
    if not os.path.exists(p):
        return None
    with open(p, encoding="utf-8") as fh:
        return json.load(fh)


def e244_reference():
    face = _face("pairhet_latest.json")
    if not face:
        return {"available": False, "reason": "pairhet_latest.json not on disk"}
    s = face.get("summary") or {}
    return {"available": True,
            "verdict": s.get("verdict"),
            "share_counterparty": s.get("share_counterparty"),
            "share_own": s.get("share_own"),
            "share_residual": s.get("share_residual"),
            "carriers": s.get("carriers") or s.get("carrier_names"),
            "note": "E244 read the SUM design's published intervals; this face reads the "
                    "un-summed slopes, so the residual share there is a property of that "
                    "design's pair statistic, not of the book"}


# ---------------------------------------------------------------- rollup
def rollup(cells):
    counted = [c for c in cells if c.get("decided") and c.get("kind") in COUNTED_KINDS]
    by = {}
    for c in counted:
        by.setdefault(c["verdict"], []).append(c["label"])
    head = next((c for c in cells if c["label"] == "all_five"), {})
    if not counted:
        verdict = "unresolved_insufficient_rows"
    elif len(by) == 1:
        verdict = counted[0]["verdict"]
    else:
        # era-dependent is only meaningful when the eras themselves disagree
        era_v = {c["verdict"] for c in counted if c["kind"] == "era"}
        verdict = "verdict_era_dependent" if len(era_v) > 1 else "verdict_mixed_across_cells"
    return {"cells_counted": len(counted), "cells_by_verdict": by, "verdict": verdict,
            "headline_verdict": head.get("verdict"),
            "stable_across_cells": len(by) == 1,
            "overlapping_cells_note": "the era and leave-one-out cells overlap in time, so a "
                                      "verdict that repeats is corroboration, not replication (E244 caveat)"}


def run(save=True, per=None, outdir=None, basket=None, panels=None):
    per = per if per is not None else e239.panels(panels)
    syms = [s for s in (basket or BASKET) if per.get(s)]
    outdir = outdir or OUTDIR
    cells = []
    for label, kind, lo, hi, members in CELLS:
        these = [s for s in (members or syms) if s in syms]
        cells.append(cell_matrix(per, these, lo, hi, label=label, kind=kind))
    dates = sorted({d for s in syms for d in per[s]})
    face = {"study": STUDY,
            "title": "the un-summed cross-member slope matrix (no rest regressor, no kappa)",
            "generated": datetime.now().isoformat(timespec="seconds"),
            "evidence_cutoff": dates[-1] if dates else None,
            "frozen_spec": {"row_equality_alpha": ROW_EQUALITY_ALPHA,
                            "resolution_max_halfwidth": RESOLUTION_MAX,
                            "star_decisive_share": STAR_DECISIVE_SHARE,
                            "star_min_abs_slope": STAR_MIN_ABS_SLOPE,
                            "star_ratio_min": STAR_RATIO_MIN,
                            "min_sessions": MIN_SESSIONS,
                            "nw_lag": NW_LAG,
                            "verdicts": list(VERDICTS)},
            "members": syms,
            "cells": cells,
            "e244_reference": e244_reference(),
            "no_bill": "structure only: no adoption, no re-pricing, no channel named as a bill"}
    face["rollup"] = rollup(cells)
    face["summary"] = _summary(face)
    if save:
        face["written"] = _write(face, outdir)
    return face


def _summary(face):
    roll = face["rollup"]
    head = next((c for c in face["cells"] if c["label"] == "all_five"), {})
    return {"verdict": roll["verdict"],
            "headline_verdict": head.get("verdict"),
            "headline_resolution": head.get("resolution_median_halfwidth"),
            "headline_stars": head.get("stars"),
            "headline_rows_rejecting_equality": head.get("rows_rejecting_equality"),
            "cells_counted": roll["cells_counted"],
            "stable_across_cells": roll["stable_across_cells"],
            "cells_by_verdict": roll["cells_by_verdict"],
            "e244_share_counterparty": (face.get("e244_reference") or {}).get("share_counterparty"),
            "e244_share_residual": (face.get("e244_reference") or {}).get("share_residual"),
            "one_line": _answer(face)}


def _answer(face):
    roll = face["rollup"]
    head = next((c for c in face["cells"] if c["label"] == "all_five"), {})
    v = roll["verdict"]
    half = head.get("resolution_median_halfwidth")
    res = ("matrix resolution %.3f" % half) if half is not None else "no resolution"
    if v == "coherent_rest_channel":
        return ("row equality holds in every counted cell (%s): the others move as ONE rest "
                "channel, so a single rest slope is the right object" % res)
    if v == "counterparty_concentration":
        return ("one counterparty is decisive for at least half of its members: %s -- the "
                "'rest channel' is a star, not a channel (%s)"
                % (", ".join(head.get("stars") or []), res))
    if v == "heterogeneous_rows":
        return ("rows %s reject equality: each member reads its counterparties differently, so "
                "no single rest slope stands for the row (%s)"
                % (", ".join(head.get("rows_rejecting_equality") or []), res))
    if v in ("verdict_era_dependent", "verdict_mixed_across_cells"):
        by = roll["cells_by_verdict"]
        parts = ["%s=%d" % (k, len(labels)) for k, labels in sorted(by.items())]
        return ("the matrix does not read the same way in every counted cell (%s): %s -- an "
                "aggregate verdict would average two different structures"
                % (", ".join(parts),
                   "the eras disagree" if v == "verdict_era_dependent" else "the cell families disagree"))
    if v == "unresolved_matrix_too_wide":
        return ("the matrix cannot resolve a structure: median half-width %.2f sits above the "
                "frozen %.2f bound" % (half or -1.0, RESOLUTION_MAX))
    return ("the matrix was not decided in any counted cell (%d counted)"
            % roll["cells_counted"])


def _fmt(v, spec="%.4f"):
    return "n/a" if v is None else (spec % v)


def _write(face, outdir):
    os.makedirs(outdir, exist_ok=True)
    name = "SLOPEMATRIX-" + str(face.get("evidence_cutoff") or "unknown") + ".json"
    for fn in (name, "slopematrix_latest.json"):
        with open(os.path.join(outdir, fn), "w", encoding="utf-8") as fh:
            json.dump(face, fh, ensure_ascii=False, indent=1)
    return name


# ---------------------------------------------------------------- fixtures
def _dates(n, start="2019-01-01"):
    y, mth, d = [int(x) for x in start.split("-")]
    out = []
    import datetime as _dt
    cur = _dt.date(y, mth, d)
    while len(out) < n:
        out.append(cur.isoformat())
        cur = cur + _dt.timedelta(days=1)
    return out


def synth(n=500, own=0.30, cross=None, noise=0.40, members=5, seed=7, start="2019-01-01"):
    """Panels whose increments obey the design the matrix fits.

    y_m[t] and l_j[t] are cumulative sums of the increments, so e240.common_increments recovers
    exactly the generated dy/dl; `cross` is a dict {(m, j): slope} with 0.0 as the default.
    Integer members are accepted and normalised to the "S<n>" names the panel carries -- an
    un-normalised key silently reads as 0.0 (r1261 family: a fixture that never moves).
    """
    cross = cross or {}
    norm = {}
    for (m, j), v in cross.items():
        m = "S%d" % m if isinstance(m, int) else m
        j = "S%d" % j if isinstance(j, int) else j
        norm[(m, j)] = v
    cross = norm
    dates = _dates(n, start)
    rng = random.Random(seed)
    syms = ["S%d" % i for i in range(members)]
    dl = {s: [rng.gauss(0.0, 1.0) for _ in dates] for s in syms}
    per = {}
    for m in syms:
        y = [0.0]
        for t in range(1, len(dates)):
            v = own * dl[m][t]
            for j in syms:
                if j == m:
                    continue
                v += cross.get((m, j), 0.0) * dl[j][t]
            y.append(v + rng.gauss(0.0, noise))
        lvl = [0.0]
        for t in range(1, len(dates)):
            lvl.append(lvl[-1] + dl[m][t])
        per[m] = {dates[t]: (y[t], lvl[t]) for t in range(len(dates))}
    return per


def _run(per, lag=NW_LAG):
    return run(save=False, per=per, basket=sorted(per))


# ---------------------------------------------------------------- selftest
def selftest():
    legs = []

    def leg(name, fn):
        try:
            ok, detail = fn()
        except Exception as exc:  # noqa: BLE001 - a leg that raises is a red leg
            ok, detail = False, "%s: %s" % (type(exc).__name__, exc)
        legs.append({"leg": name, "ok": bool(ok), "detail": detail})

    def homogeneous():
        face = _run(synth(cross={(m, j): 0.15 for m in range(5) for j in range(5) if m != j}))
        head = next(c for c in face["cells"] if c["label"] == "all_five")
        rej = head.get("rows_rejecting_equality") or []
        # activity first: the fixture must actually carry the 0.15 cross effect, otherwise
        # "no row rejects" is a statement about a panel with nothing in it (r1261 family).
        slopes = [c["slope"] for r in head["rows"] for c in r["cross"]]
        mean = sum(slopes) / len(slopes) if slopes else 0.0
        ok = head["decided"] and not rej and abs(mean - 0.15) < 0.05 \
            and head.get("verdict") == "coherent_rest_channel"
        return ok, "mean_cross=%.3f rejecting=%s verdict=%s half=%.3f" % (
            mean, rej, head.get("verdict"), head.get("resolution_median_halfwidth") or -1)

    def star():
        # S0's turnover moves every other member: cross[(m, j)] is dy_m on dl_j, so the star
        # sits in COLUMN S0 rather than in row S0.
        cross = {(m, 0): 0.6 for m in range(1, 5)}
        face = _run(synth(cross=cross, noise=0.35))
        head = next(c for c in face["cells"] if c["label"] == "all_five")
        # member 0 moves everybody: counterparty 0 must be decisive in four rows
        col = [c for c in (head.get("columns") or []) if c["one_of"] == "S0"]
        ok = bool(col) and col[0]["decisive"] >= 3 \
            and head.get("verdict") == "counterparty_concentration"
        return ok, "col=%s verdict=%s" % (col, head.get("verdict"))

    def equivalence_with_e239():
        per = synth(n=400, own=0.4, cross={("S0", "S1"): 0.25}, noise=0.3)
        _, panel = e240.common_increments(per, ["S0", "S1"])
        row = fit_row(panel, ["S0", "S1"], "S0")
        ref = e239._fit(panel["dy"]["S0"], panel["dx"]["S0"], panel["dx"]["S1"])
        d_own = abs(row["b_own"] - ref["b_own"])
        d_cross = abs(row["cross"][0]["slope"] - ref["b_cross"])
        return (d_own < 1e-9 and d_cross < 1e-9), "d_own=%.2e d_cross=%.2e" % (d_own, d_cross)

    def contrast_zero_when_rows_equal():
        cross = {(m, j): 0.2 for m in range(4) for j in range(4) if m != j}
        face = _run(synth(cross=cross, noise=0.3, members=4))
        head = next(c for c in face["cells"] if c["label"] == "all_five")
        cm = head.get("contrast_mean")
        ok = cm is not None and abs(cm) < 0.05
        return ok, "contrast_mean=%s spread=%s" % (cm, head.get("contrast_spread"))

    def degenerate_regressor_refused():
        per = synth(n=240, members=3, noise=0.2)
        for d in per["S1"]:
            y, _ = per["S1"][d]
            per["S1"][d] = (y, 0.0)          # constant turnover -> zero variance increments
        face = _run(per)
        head = next(c for c in face["cells"] if c["label"] == "all_five")
        return (head.get("decided") is False), "head=%s" % head.get("verdict")

    def too_few_sessions():
        face = _run(synth(n=60, members=4))
        head = next(c for c in face["cells"] if c["label"] == "all_five")
        return (head.get("decided") is False
                and "sessions" in (head.get("reason") or "")), head.get("reason")

    def deterministic():
        per = synth(n=300, cross={("S0", "S1"): 0.3}, members=4)
        a = _run(per)
        b = _run(per)
        ha = next(c for c in a["cells"] if c["label"] == "all_five")["matrix"]
        hb = next(c for c in b["cells"] if c["label"] == "all_five")["matrix"]
        return ha == hb, "matrix identical=%s" % (ha == hb)

    def recovers_truth():
        truth = {("S0", "S1"): 0.5, ("S0", "S2"): -0.3, ("S2", "S0"): 0.4}
        face = _run(synth(cross=truth, own=0.35, noise=0.25, members=4, n=700))
        head = next(c for c in face["cells"] if c["label"] == "all_five")
        mat = head.get("matrix") or {}
        errs = [abs(mat[m][j] - v) for (m, j), v in truth.items() if m in mat and j in mat[m]]
        ok = len(errs) == 3 and max(errs) < 0.25
        return ok, "errs=%s" % (["%.3f" % e for e in errs],)

    def wald_scales_with_signal():
        hom = _run(synth(cross={(m, j): 0.15 for m in range(5) for j in range(5) if m != j}))
        het = _run(synth(cross={(0, j): 0.7 for j in range(1, 5)}, noise=0.2))
        hh = next(c for c in hom["cells"] if c["label"] == "all_five")
        hd = next(c for c in het["cells"] if c["label"] == "all_five")
        chi_h = [r["row_equal"]["chi2"] for r in hh["rows"] if r["row_equal"].get("chi2") is not None]
        chi_d = [r["row_equal"]["chi2"] for r in hd["rows"] if r["row_equal"].get("chi2") is not None]
        ok = chi_h and chi_d and max(chi_h) < max(chi_d)
        return ok, "max_chi_hom=%s max_chi_het=%s" % (
            "%.2f" % max(chi_h) if chi_h else None, "%.2f" % max(chi_d) if chi_d else None)

    def member_order_invariant():
        per = synth(cross={("S0", "S1"): 0.3}, members=4, n=320)
        a = run(save=False, per=per, basket=["S0", "S1", "S2", "S3"])
        b = run(save=False, per=per, basket=["S3", "S2", "S1", "S0"])
        ma = next(c for c in a["cells"] if c["label"] == "all_five")["matrix"]
        mb = next(c for c in b["cells"] if c["label"] == "all_five")["matrix"]
        ok = all(abs(ma[m][j] - mb[m][j]) < 1e-12 for m in ma for j in ma[m])
        return ok, "invariant=%s" % ok

    leg("homogeneous rows read as one rest channel", homogeneous)
    leg("a star is detected and is not called a channel", star)
    leg("two-member row equals the published pair fit (e239)", equivalence_with_e239)
    leg("contrast is zero when the row's slopes are equal", contrast_zero_when_rows_equal)
    leg("a zero-variance counterparty is refused, not fitted", degenerate_regressor_refused)
    leg("too few sessions is undecided, not empty-green", too_few_sessions)
    leg("same input publishes the same matrix", deterministic)
    leg("the matrix recovers known slopes", recovers_truth)
    leg("row-equality Wald grows with real heterogeneity", wald_scales_with_signal)
    leg("member order does not change the matrix", member_order_invariant)

    n_ok = sum(1 for l in legs if l["ok"])
    print("selftest: %d/%d" % (n_ok, len(legs)))
    for l in legs:
        print(("  PASS " if l["ok"] else "  FAIL ") + l["leg"] + " :: " + str(l["detail"])[:200])
    return 0 if n_ok == len(legs) else 1


def main(argv=None):
    ap = argparse.ArgumentParser(description="E245 pair slope matrix")
    ap.add_argument("cmd", nargs="?", default="run", choices=("run", "selftest"))
    args = ap.parse_args(argv)
    if args.cmd == "selftest":
        return selftest()
    face = run(save=True)
    s = face["summary"]
    print("verdict: %s" % s["verdict"])
    print("headline: %s (resolution %s)" % (s["headline_verdict"],
                                            _fmt(s["headline_resolution"], "%.3f")))
    print("cells counted: %d, stable: %s" % (s["cells_counted"], s["stable_across_cells"]))
    print(s["one_line"])
    print("written: %s" % face.get("written"))
    return 0


if __name__ == "__main__":
    sys.exit(main())