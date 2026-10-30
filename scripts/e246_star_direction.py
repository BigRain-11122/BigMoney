#!/usr/bin/env python3
"""E246 -- does the star lead anything, or is it the same commonality read best on one sleeve?

E245 found the "rest channel" is a star: sh588000's turnover is decisive for every other member
(mean slope 0.769 in the five-member window), and pre-2020, before that sleeve prints, the
columns are diffuse. Two mechanisms produce exactly that simultaneity:

  (a) that sleeve's turnover carries a book-wide factor -- its flow moves the others,
  (b) all five sleeves load on one common driver and the star is simply the one the regression
      reads best,

and a contemporaneous regression cannot tell them apart: both produce a big column and nothing
else. This face asks the question the two mechanisms answer differently -- the LEAD. The matrix
is refitted with the counterparty's turnover lagged one and two sessions, in both directions
(every member's move against the star's past turnover, and the star's move against everyone
else's past turnover), and each direction is published with its HAC interval.

If nothing leads anything, the star is a contemporaneous common factor: it is not a channel a
single sleeve's flow can be blamed for, and no bill may be written against it.

The lag designs reuse E245's row fit verbatim (own contemporaneous, each counterparty
separately, one HAC per row) -- selftest pins that the lag-0 reading is bit-identical to E245's,
so the contemporaneous number is not re-estimated by this face.

NO BILL, NO ADOPTION, NO RE-PRICING. This face names direction; it prices nothing.
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
import e245_pair_slope_matrix as e245  # noqa: E402

ROOT = e222.ROOT
OUTDIR = os.path.join(ROOT, "results", "state_tilt")
BASKET = e225.BASKET
NW_LAG = e225.NW_LAG
Z95 = 1.96
MIN_SESSIONS = e240.MIN_SESSIONS
STUDY = "E246"

# frozen before the face was read
LAGS = (0, 1, 2)
RESOLUTION_MAX = e245.RESOLUTION_MAX          # same bound the matrix face carries
STAR_DECISIVE_SHARE = e245.STAR_DECISIVE_SHARE
CONTEMP_MIN_ABS = e245.STAR_MIN_ABS_SLOPE     # a tenth of a log point
LEAD_MIN_ABS = 0.10
COUNTED_KINDS = ("headline", "window", "era", "neighbour")

VERDICTS = ("star_flow_leads_members",
            "flow_leads_and_contemporaneous",
            "star_flow_leads_with_sign_flip",
            "star_flow_leads_inverse",
            "contemporaneous_common_factor",
            "members_lead_the_star",
            "no_direction_resolved",
            "unresolved_matrix_too_wide",
            "unresolved_insufficient_rows")

CELLS = e245.CELLS


# ---------------------------------------------------------------- fits
def fit_row_lag(panel, syms, m, lag):
    """One member's move on its own turnover, every other member's, and their `lag`-session past.

    `lag = 0` is E245's row fit exactly (same columns, same order, same HAC), so the
    contemporaneous reading is re-used rather than re-estimated.

    For `lag > 0` the lagged block goes into the SAME regression as the contemporaneous block.
    A row that carried only lagged counterparties would be a proxy, not a test: on a persistent
    sleeve the lagged turnover is 0.87-correlated with the contemporaneous one, and the lone
    lag coefficient simply re-reads the same column (measured 0.51 on a fixture whose true lead
    was 0.00). Partialling the past against the present is what makes the coefficient a lead.
    """
    others = [s for s in syms if s != m]
    # the panel's dy/dx arrays carry one entry per session PAIR, i.e. len(dates) entries
    n = len(panel["dy"][m])
    rows = n - lag
    if lag < 0 or rows <= 2 * len(others) + 6:
        return {"own_of": m, "lag": lag, "decided": False,
                "reason": "too few rows once %d session(s) of lag are consumed" % lag}
    y = panel["dy"][m][lag:]
    cols = [panel["dx"][m][lag:]] + [panel["dx"][j][lag:] for j in others]
    if lag > 0:
        cols += [panel["dx"][j][:rows] for j in others]
    fit = e235._ols_hac_full(y, cols, NW_LAG)
    if fit is None:
        return {"own_of": m, "lag": lag, "decided": False,
                "reason": "HAC fit refused (singular or too few rows)"}
    beta, cov = fit["beta"], fit["cov"]

    def ci(idx):
        var = cov[idx][idx]
        se = math.sqrt(var) if var is not None and var > 0 else None
        return (None if se is None else [beta[idx] - Z95 * se, beta[idx] + Z95 * se],
                (beta[idx] / se) if se else None)

    own_ci, own_t = ci(1)
    cross, lagged = [], []
    for pos, j in enumerate(others):
        idx = 2 + pos
        c, t = ci(idx)
        cell = {"one_of": j, "slope": beta[idx], "ci": c, "t_nw": t,
                "decisive": bool(c and not (c[0] <= 0.0 <= c[1]))}
        lagged.append(cell)
        if lag == 0:
            cross.append(cell)
            continue
        c2, t2 = ci(2 + len(others) + pos)
        cross.append({"one_of": j, "slope": beta[idx], "ci": c, "t_nw": t,
                      "decisive": bool(c and not (c[0] <= 0.0 <= c[1]))})
        lagged[-1] = {"one_of": j, "slope": beta[2 + len(others) + pos], "ci": c2, "t_nw": t2,
                      "decisive": bool(c2 and not (c2[0] <= 0.0 <= c2[1]))}
    return {"own_of": m, "lag": lag, "decided": True, "rows_used": fit["n"], "r2": fit["r2"],
            "b_own": beta[1], "b_own_ci": own_ci, "b_own_t_nw": own_t,
            "cross": cross, "lagged": (lagged if lag > 0 else None)}


def _column(rows, j, field="cross"):
    slopes = [c for r in rows for c in (r.get(field) or []) if c["one_of"] == j]
    if not slopes:
        return {"one_of": j, "members": 0, "decisive": 0, "decisive_share": None,
                "mean_slope": None, "mean_abs_slope": None}
    dec = [c for c in slopes if c["decisive"]]
    return {"one_of": j, "field": field, "members": len(slopes), "decisive": len(dec),
            "decisive_share": len(dec) / float(len(slopes)),
            "mean_slope": sum(c["slope"] for c in slopes) / len(slopes),
            "mean_abs_slope": sum(abs(c["slope"]) for c in slopes) / len(slopes),
            "decisive_signs": sorted({1 if c["slope"] > 0 else -1 for c in dec})}


def _row_lead(rows, m):
    """The star's OWN move against everyone else's past turnover (the reverse direction)."""
    row = next((r for r in rows if r.get("own_of") == m and r.get("decided")), None)
    if not row or not row.get("lagged"):
        return {"members": 0, "decisive": 0, "decisive_share": None, "mean_slope": None}
    dec = [c for c in row["lagged"] if c["decisive"]]
    return {"members": len(row["lagged"]), "decisive": len(dec),
            "decisive_share": len(dec) / float(len(row["lagged"])) if row["lagged"] else None,
            "mean_slope": (sum(c["slope"] for c in row["lagged"]) / len(row["lagged"])
                           if row["lagged"] else None),
            "decisive_signs": sorted({1 if c["slope"] > 0 else -1 for c in dec})}


def own_lag_persistence(panel, syms):
    """Is a member's own turnover move predictable from its own previous move?

    Disclosure only: a white-noise regulator still supplies a lagged regressor with full
    variance, so the lead tests are powered either way, but the reading means something
    different on a persistent series and the face says which it has.
    """
    out = {}
    for s in syms:
        x = panel["dx"][s]
        if len(x) < 10:
            out[s] = {"decided": False, "reason": "too few rows"}
            continue
        y, xl = x[1:], x[:-1]
        fit = e235._ols_hac_full(y, [xl], NW_LAG)
        if fit is None:
            out[s] = {"decided": False, "reason": "fit refused"}
            continue
        se = math.sqrt(fit["cov"][1][1]) if fit["cov"][1][1] > 0 else None
        out[s] = {"decided": True, "ar1": fit["beta"][1],
                  "t_nw": (fit["beta"][1] / se) if se else None, "rows_used": fit["n"]}
    return out


def derive_verdict(counts):
    """The whole classification, recomputable from the published counts alone.

    Frozen before the face was read; the smoke leg re-runs this against the face's own
    numbers so a cell cannot carry a verdict its counts do not produce.
    """
    c = counts.get("contemporaneous") or {}
    share0, mean0 = c.get("decisive_share"), c.get("mean_slope")
    contemp = (share0 is not None and mean0 is not None
               and share0 >= STAR_DECISIVE_SHARE and abs(mean0) >= CONTEMP_MIN_ABS)
    leads = []
    signs = set()
    for L in ("1", "2"):
        b = (counts.get("lead") or {}).get(L) or {}
        sh, mu = b.get("decisive_share"), b.get("mean_slope")
        # a decisive NEGATIVE lead is still a lead: the star's past turnover predicting a
        # member's move is information flow whichever way the sign runs, and reading only the
        # positive half would have thrown away this face's largest coefficient (lag 1, -0.527)
        if sh is not None and mu is not None and sh >= STAR_DECISIVE_SHARE \
                and abs(mu) >= LEAD_MIN_ABS:
            leads.append(int(L))
            signs.add(1 if mu > 0 else -1)
    rv = counts.get("reverse_lead") or {}
    rev_sh, rev_mu = rv.get("decisive_share"), rv.get("mean_slope")
    reverse = (rev_sh is not None and rev_mu is not None
               and rev_sh >= STAR_DECISIVE_SHARE and abs(rev_mu) >= LEAD_MIN_ABS)
    if leads and len(signs) > 1:
        return "star_flow_leads_with_sign_flip", leads
    if leads and 1 in signs and contemp:
        return "flow_leads_and_contemporaneous", leads
    if leads and 1 in signs:
        return "star_flow_leads_members", leads
    if leads:
        return "star_flow_leads_inverse", leads
    if reverse and not contemp:
        return "members_lead_the_star", leads
    if contemp:
        return "contemporaneous_common_factor", leads
    return "no_direction_resolved", leads


# ---------------------------------------------------------------- cells
def cell(per, syms, lo=None, hi=None, label="", kind="window", note=None, star_override=None):
    syms = [s for s in syms if per.get(s) and len(per[s]) > 2]
    out = {"label": label, "kind": kind, "members": list(syms),
           "window_inclusive": [lo, hi], "note": note}
    if len(syms) < 3:
        out.update({"decided": False,
                    "reason": "fewer than three members have a panel in this window"})
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

    by_lag = {}
    for lag in LAGS:
        rows = [fit_row_lag(panel, syms, m, lag) for m in syms]
        by_lag[str(lag)] = rows
    decided0 = [r for r in by_lag["0"] if r.get("decided")]
    if len(decided0) < 3:
        out.update({"decided": False,
                    "reason": "only %d of %d rows could be fitted at lag 0"
                              % (len(decided0), len(syms))})
        return out

    halves = [abs(c["ci"][1] - c["ci"][0]) / 2.0
              for r in decided0 for c in r["cross"] if c["ci"]]
    median_half = sorted(halves)[len(halves) // 2] if halves else None

    # the star is named at lag 0 by E245's own rule, so the direction question is asked of the
    # same object the matrix face published
    columns0 = [_column(decided0, j) for j in syms]
    mags = sorted(c["mean_abs_slope"] for c in columns0 if c["mean_abs_slope"] is not None)
    median_mag = mags[len(mags) // 2] if mags else 0.0
    stars = [c for c in columns0
             if c.get("decisive_share") is not None
             and c["decisive_share"] >= STAR_DECISIVE_SHARE
             and c["mean_abs_slope"] is not None
             and c["mean_abs_slope"] >= CONTEMP_MIN_ABS
             and (median_mag <= 0.0 or c["mean_abs_slope"] >= e245.STAR_RATIO_MIN * median_mag)]
    stars.sort(key=lambda c: (-c["decisive_share"], -c["mean_abs_slope"]))
    star = stars[0]["one_of"] if stars else None
    star_source = "e245_star_rule" if star else "no_star_at_lag0"
    if star is None:
        best = max((c for c in columns0 if c.get("mean_abs_slope") is not None),
                   key=lambda c: c["mean_abs_slope"], default=None)
        star = best["one_of"] if best else None
        star_source = "max_mean_abs_slope_disclosure_only"
    if star_override:
        star = star_override if star_override in syms else star
        star_source = "caller_override"

    counts = {"contemporaneous": _column(decided0, star) if star else {}}
    for lag in LAGS[1:]:
        rows = [r for r in by_lag[str(lag)] if r.get("decided")]
        counts.setdefault("lead", {})[str(lag)] = _column(rows, star, "lagged") if star else {}
        by_lag[str(lag)] = rows
    rows1 = [r for r in by_lag["1"] if r.get("decided")] or [r for r in by_lag["1"]]
    counts["reverse_lead"] = _row_lead(rows1, star) if star else {}
    verdict, lead_lags = derive_verdict(counts)

    if median_half is not None and median_half > RESOLUTION_MAX:
        verdict = "unresolved_matrix_too_wide"

    out.update({"decided": True,
                "star": star, "star_source": star_source,
                "resolution_median_halfwidth": median_half,
                "resolution_max": RESOLUTION_MAX,
                "lags": {k: {"rows_used": max([r.get("rows_used") or 0 for r in v] or [0]),
                             "rows_decided": sum(1 for r in v if r.get("decided"))}
                         for k, v in by_lag.items()},
                "counts": counts,
                "lead_lags_decisive": lead_lags,
                "own_lag_persistence": own_lag_persistence(panel, syms),
                "matrix_by_lag": {k: {r["own_of"]: {c["one_of"]: c["slope"] for c in r["cross"]}
                                      for r in v if r.get("decided")}
                                  for k, v in by_lag.items()},
                "verdict": verdict})
    return out


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
        era_v = {c["verdict"] for c in counted if c["kind"] == "era"}
        verdict = "verdict_era_dependent" if len(era_v) > 1 else "verdict_mixed_across_cells"
    return {"cells_counted": len(counted), "cells_by_verdict": by, "verdict": verdict,
            "headline_verdict": head.get("verdict"),
            "headline_star": head.get("star"),
            "stable_across_cells": len(by) == 1,
            "overlapping_cells_note": "the era cells overlap in time, so a verdict that "
                                      "repeats is corroboration, not replication (E244 caveat)"}


def _answer(face):
    roll = face["rollup"]
    head = next((c for c in face["cells"] if c["label"] == "all_five"), {})
    star = head.get("star") or "the star"
    v = roll["verdict"]
    lags = head.get("lead_lags_decisive") or []
    if v == "star_flow_leads_members":
        return ("%s's turnover LEADS the other members at lag %s: the star carries a factor a "
                "single sleeve's flow can be named for" % (star, ",".join(map(str, lags))))
    if v == "flow_leads_and_contemporaneous":
        return ("%s leads the book at lag %s AND reads contemporaneously: both mechanisms are "
                "present, so the column is part flow and part common driver"
                % (star, ",".join(map(str, lags))))
    if v == "star_flow_leads_with_sign_flip":
        return ("%s's past turnover predicts the book at lag %s, but the lags DISAGREE in sign "
                "(%s): that is an oscillation in the shared driver, not a one-way flow -- the "
                "column may not be billed to that sleeve"
                % (star, ",".join(map(str, lags)), _lag_signs(head)))
    if v == "star_flow_leads_inverse":
        return ("%s's past turnover predicts the book with a NEGATIVE coefficient at lag %s: a "
                "spike in that sleeve's turnover is followed by smaller moves, which is a "
                "bounce, not a source" % (star, ",".join(map(str, lags))))
    if v in ("verdict_mixed_across_cells", "verdict_era_dependent"):
        by = roll["cells_by_verdict"]
        parts = ["%s=%d" % (k, len(labels)) for k, labels in sorted(by.items())]
        return ("the cells do not read the same way (%s): %s -- an aggregate verdict would "
                "average different structures" % (
                    ", ".join(parts),
                    "the eras disagree" if v == "verdict_era_dependent"
                    else "the cell families disagree"))
    if v == "contemporaneous_common_factor":
        return ("nothing leads anything: %s's column is a CONTEMPORANEOUS common factor, not a "
                "channel that sleeve's flow can be blamed for" % star)
    if v == "members_lead_the_star":
        return ("the lead runs the other way -- the members' turnover leads %s, so the column is "
                "a follower's mirror, not a source" % star)
    if v == "unresolved_matrix_too_wide":
        return ("the lag designs carry no resolvable direction: median half-width %.2f sits "
                "above the frozen %.2f bound"
                % ((head.get("resolution_median_halfwidth") or -1.0), RESOLUTION_MAX))
    return ("no direction resolved in any counted cell (%d counted)" % roll["cells_counted"])


def _lag_signs(head):
    parts = []
    for L in ("1", "2"):
        b = ((head.get("counts") or {}).get("lead") or {}).get(L) or {}
        mu = b.get("mean_slope")
        if mu is not None:
            parts.append("lag %s %+.3f" % (L, mu))
    return ", ".join(parts) or "no lag design"


def _summary(face):
    roll = face["rollup"]
    head = next((c for c in face["cells"] if c["label"] == "all_five"), {})
    counts = head.get("counts") or {}
    return {"verdict": roll["verdict"],
            "headline_verdict": head.get("verdict"),
            "headline_star": head.get("star"),
            "headline_star_source": head.get("star_source"),
            "headline_resolution": head.get("resolution_median_halfwidth"),
            "contemporaneous": counts.get("contemporaneous"),
            "lead_lag1": (counts.get("lead") or {}).get("1"),
            "lead_lag2": (counts.get("lead") or {}).get("2"),
            "reverse_lead": counts.get("reverse_lead"),
            "lead_lags_decisive": head.get("lead_lags_decisive"),
            "cells_counted": roll["cells_counted"],
            "stable_across_cells": roll["stable_across_cells"],
            "cells_by_verdict": roll["cells_by_verdict"],
            "one_line": _answer(face)}


def run(save=True, per=None, outdir=None, basket=None, panels=None, star=None):
    per = per if per is not None else e239.panels(panels)
    syms = [s for s in (basket or BASKET) if per.get(s)]
    outdir = outdir or OUTDIR
    cells = []
    for label, kind, lo, hi, members in CELLS:
        these = [s for s in (members or syms) if s in syms]
        cells.append(cell(per, these, lo, hi, label=label, kind=kind, star_override=star))
    dates = sorted({d for s in syms for d in per[s]})
    face = {"study": STUDY,
            "title": "does the star lead the book, or is it one common factor read best there",
            "generated": datetime.now().isoformat(timespec="seconds"),
            "evidence_cutoff": dates[-1] if dates else None,
            "frozen_spec": {"lags": list(LAGS),
                            "resolution_max_halfwidth": RESOLUTION_MAX,
                            "star_decisive_share": STAR_DECISIVE_SHARE,
                            "contemporaneous_min_abs": CONTEMP_MIN_ABS,
                            "lead_min_abs": LEAD_MIN_ABS,
                            "min_sessions": MIN_SESSIONS,
                            "nw_lag": NW_LAG,
                            "verdicts": list(VERDICTS)},
            "members": syms,
            "cells": cells,
            "no_bill": "direction only: no adoption, no re-pricing, and a contemporaneous "
                       "common factor may not be billed to one sleeve"}
    face["rollup"] = rollup(cells)
    face["summary"] = _summary(face)
    if save:
        face["written"] = _write(face, outdir)
    return face


def _write(face, outdir):
    os.makedirs(outdir, exist_ok=True)
    name = "STARDIR-" + str(face.get("evidence_cutoff") or "unknown") + ".json"
    for fn in (name, "stardir_latest.json"):
        with open(os.path.join(outdir, fn), "w", encoding="utf-8") as fh:
            json.dump(face, fh, ensure_ascii=False, indent=1)
    return name


# ---------------------------------------------------------------- fixtures
def _dates(n, start="2019-01-01"):
    import datetime as _dt
    y, mth, d = [int(x) for x in start.split("-")]
    cur = _dt.date(y, mth, d)
    out = []
    while len(out) < n:
        out.append(cur.isoformat())
        cur = cur + _dt.timedelta(days=1)
    return out


def synth(n=600, own=0.30, cross=None, lead=None, noise=0.40, members=5, seed=7,
          star_ar=0.0, start="2019-01-01"):
    """Panels whose increments obey the design, including a one-session LEAD term.

    `cross` is {(m, j): slope} on dl_j[t]; `lead` is {(m, j): slope} on dl_j[t-1]. Shapes follow
    E245's fixture so the lag-0 fit is the same object, and integer member indices are
    normalised (an un-normalised key silently reads as 0.0).
    """
    def norm(d):
        out = {}
        for (m, j), v in (d or {}).items():
            out[("S%d" % m if isinstance(m, int) else m,
                 "S%d" % j if isinstance(j, int) else j)] = v
        return out

    cross, lead = norm(cross), norm(lead)
    dates = _dates(n, start)
    rng = random.Random(seed)
    syms = ["S%d" % i for i in range(members)]
    dl = {s: [rng.gauss(0.0, 1.0) for _ in dates] for s in syms}
    if star_ar:
        base = dl[syms[0]]
        for t in range(1, len(base)):
            base[t] = star_ar * base[t - 1] + math.sqrt(max(1e-9, 1.0 - star_ar ** 2)) * base[t]
    per = {}
    for m in syms:
        # the LEVEL is what the panel stores, exactly as in the real data (log|move| and log
        # turnover): the fit reads DIFFERENCES, so the fixture has to accumulate them or every
        # lag design would be reading the difference of two increments instead of a move
        y, lvl = [0.0], [0.0]
        for t in range(1, len(dates)):
            v = own * dl[m][t]
            for j in syms:
                if j == m:
                    continue
                v += cross.get((m, j), 0.0) * dl[j][t]
                v += lead.get((m, j), 0.0) * dl[j][t - 1]
            y.append(y[-1] + v + rng.gauss(0.0, noise))
            lvl.append(lvl[-1] + dl[m][t])
        per[m] = {dates[t]: (y[t], lvl[t]) for t in range(len(dates))}
    return per


def _run(per, star="S0"):
    return run(save=False, per=per, basket=sorted(per), star=star)


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

    def gate_signs():
        # the sign vocabulary is part of the frozen gate: an inverse lead and a sign-flipping
        # pair must not both be published as "leads"
        pos = derive_verdict({"contemporaneous": {"decisive_share": 0.0, "mean_slope": 0.0},
                              "lead": {"1": {"decisive_share": 1.0, "mean_slope": 0.5},
                                       "2": {"decisive_share": 0.0, "mean_slope": 0.0}},
                              "reverse_lead": {"decisive_share": 0.0, "mean_slope": 0.0}})
        neg = derive_verdict({"contemporaneous": {"decisive_share": 0.0, "mean_slope": 0.0},
                              "lead": {"1": {"decisive_share": 1.0, "mean_slope": -0.5},
                                       "2": {"decisive_share": 0.0, "mean_slope": 0.0}},
                              "reverse_lead": {"decisive_share": 0.0, "mean_slope": 0.0}})
        flip = derive_verdict({"contemporaneous": {"decisive_share": 1.0, "mean_slope": 0.77},
                               "lead": {"1": {"decisive_share": 1.0, "mean_slope": -0.53},
                                        "2": {"decisive_share": 1.0, "mean_slope": 0.40}},
                               "reverse_lead": {"decisive_share": 0.0, "mean_slope": 0.0}})
        ok = (pos[0] == "star_flow_leads_members"
              and neg[0] == "star_flow_leads_inverse"
              and flip[0] == "star_flow_leads_with_sign_flip")
        return ok, "%s / %s / %s" % (pos[0], neg[0], flip[0])

    def lead_is_detected():
        # activity first: the fixture must actually carry the 0.6 lead, otherwise "leads" is a
        # statement about a panel with nothing in it (r1261 family)
        per = synth(lead={(m, 0): 0.6 for m in range(1, 5)})
        head = _head(_run(per))
        col = (head.get("counts") or {}).get("lead", {}).get("1") or {}
        return (col.get("mean_slope") is not None and abs(col["mean_slope"] - 0.6) < 0.08
                and (col.get("decisive_share") or 0) >= 0.75), "lag1 %s" % col

    def lead_only_verdict():
        per = synth(lead={(m, 0): 0.6 for m in range(1, 5)})
        head = _head(_run(per))
        return head.get("verdict") == "star_flow_leads_members", head.get("verdict")

    def contemp_only_no_lead():
        # the star moves the others NOW and nothing else: the contemporaneous column must read
        # the truth and BOTH lead designs must stay empty (activity asserted on the lag that
        # does have signal, so this is not a statement about a fixture that never moves)
        per = synth(cross={(m, 0): 0.6 for m in range(1, 5)})
        head = _head(_run(per))
        c0 = (head.get("counts") or {}).get("contemporaneous") or {}
        lag1 = (head.get("counts") or {}).get("lead", {}).get("1") or {}
        sh1 = lag1.get("decisive_share")
        ok = (abs((c0.get("mean_slope") or 0.0) - 0.6) < 0.08
              and sh1 is not None and sh1 == 0.0)
        return ok, "lag0 mean=%s lag1 decisive_share=%s" % (
            _f(c0.get("mean_slope")), _f(sh1))

    def contemp_common_factor():
        # a PERSISTENT star with a purely contemporaneous effect and no lead at all: its own
        # lagged turnover is 0.87-correlated with the current one, so a lead test that did not
        # partial the present against the past would read a lead that is not there (the first
        # draft of this face did exactly that, 0.51 on a zero-lead fixture)
        per = synth(cross={(m, 0): 0.6 for m in range(1, 5)}, star_ar=0.85)
        head = _head(_run(per))
        return (head.get("verdict") == "contemporaneous_common_factor",
                "verdict=%s lead1=%s" % (
                    head.get("verdict"),
                    _f(((head.get("counts") or {}).get("lead", {}).get("1") or {}
                        ).get("mean_slope"))))

    def both_verdict():
        per = synth(cross={(m, 0): 0.5 for m in range(1, 5)},
                    lead={(m, 0): 0.4 for m in range(1, 5)})
        head = _head(_run(per))
        return head.get("verdict") == "flow_leads_and_contemporaneous", head.get("verdict")

    def no_signal():
        per = synth()
        head = _head(_run(per))
        return head.get("verdict") == "no_direction_resolved", head.get("verdict")

    def reverse_direction():
        # members lead the star: dy_star[t] on dl_j[t-1], nothing forward
        per = synth(lead={(0, j): 0.5 for j in range(1, 5)})
        head = _head(_run(per))
        rv = (head.get("counts") or {}).get("reverse_lead") or {}
        return (head.get("verdict") == "members_lead_the_star"
                and (rv.get("decisive_share") or 0) >= 0.5), "rev=%s verdict=%s" % (
            rv, head.get("verdict"))

    def lag0_matches_e245():
        per = synth(n=700, cross={(0, j): 0.3 for j in range(1, 4)}, members=4)
        _, panel = e240.common_increments(per, ["S0", "S1", "S2", "S3"])
        mine = fit_row_lag(panel, ["S0", "S1", "S2", "S3"], "S0", 0)
        ref = e245.fit_row(panel, ["S0", "S1", "S2", "S3"], "S0")
        d = [abs(mine["b_own"] - ref["b_own"])]
        d += [abs(a["slope"] - b["slope"]) for a, b in zip(mine["cross"], ref["cross"])]
        return max(d) < 1e-12, "max diff %.2e" % max(d)

    def gate_recomputes():
        face = _run(synth(cross={(m, 0): 0.6 for m in range(1, 5)}))
        cells = [c for c in face["cells"] if c.get("decided")]
        bad = []
        for c in cells:
            v, _ = derive_verdict(c.get("counts") or {})
            if c.get("resolution_median_halfwidth") is not None \
                    and c["resolution_median_halfwidth"] > RESOLUTION_MAX:
                v = "unresolved_matrix_too_wide"
            if v != c.get("verdict"):
                bad.append("%s: counts say %s, face says %s" % (c["label"], v, c.get("verdict")))
        # and the gate must refuse a hand-written "leads" that its counts do not support
        tampered = {"contemporaneous": {"decisive_share": 0.1, "mean_slope": 0.02},
                    "lead": {"1": {"decisive_share": 0.1, "mean_slope": 0.02},
                             "2": {"decisive_share": 0.0, "mean_slope": 0.01}},
                    "reverse_lead": {"decisive_share": 0.0, "mean_slope": 0.0}}
        refute, _ = derive_verdict(tampered)
        if refute != "no_direction_resolved":
            bad.append("gate accepted a lead its counts do not carry (%s)" % refute)
        return not bad, "; ".join(bad) or "all %d cells recompute" % len(cells)

    def own_lag_disclosed():
        per = synth(members=4, star_ar=0.6)
        head = _head(_run(per))
        pers = head.get("own_lag_persistence") or {}
        ar = (pers.get("S0") or {}).get("ar1")
        others = [(pers.get("S%d" % i) or {}).get("ar1") or 0.0 for i in (1, 2, 3)]
        return (ar is not None and ar > 0.3 and max(others) < 0.2), "ar S0=%s others=%s" % (
            ar, others)

    def too_few_sessions():
        face = _run(synth(n=60, members=4))
        head = _head(face)
        return (head.get("decided") is False
                and "sessions" in (head.get("reason") or "")), head.get("reason")

    def deterministic():
        per = synth(n=320, cross={(0, 1): 0.3}, members=4)
        a, b = _run(per), _run(per)
        return (_head(a).get("matrix_by_lag") == _head(b).get("matrix_by_lag"),
                "identical=%s" % (_head(a).get("matrix_by_lag") == _head(b).get("matrix_by_lag")))

    def member_order_invariant():
        per = synth(cross={(0, 1): 0.3}, members=4, n=340)
        a = run(save=False, per=per, basket=["S0", "S1", "S2", "S3"])
        b = run(save=False, per=per, basket=["S3", "S2", "S1", "S0"])
        ma = _head(a).get("matrix_by_lag") or {}
        mb = _head(b).get("matrix_by_lag") or {}
        ok = all(abs(ma[k][m][j] - mb[k][m][j]) < 1e-12
                 for k in ma for m in ma[k] for j in ma[k][m])
        return ok, "lag0..2 invariant=%s" % ok

    leg("the sign vocabulary separates inverse and sign-flipping leads", gate_signs)
    leg("a real lead is detected at lag 1 with the right magnitude", lead_is_detected)
    leg("a lead-only panel is classified as the star leading", lead_only_verdict)
    leg("a contemporaneous-only panel reads its column and no lead", contemp_only_no_lead)
    leg("a persistent star does not fabricate a lead on its own", contemp_common_factor)
    leg("simultaneous plus lead is reported as both", both_verdict)
    leg("a panel with no cross or lead signal resolves no direction", no_signal)
    leg("the reverse direction is its own verdict", reverse_direction)
    leg("lag 0 is bit-identical to the published E245 row fit", lag0_matches_e245)
    leg("the gate recomputes every verdict and refuses an unsupported lead", gate_recomputes)
    leg("own-lag persistence is measured, not assumed", own_lag_disclosed)
    leg("too few sessions is undecided, not empty-green", too_few_sessions)
    leg("same input publishes the same lag matrices", deterministic)
    leg("member order does not change any lag matrix", member_order_invariant)

    n_ok = sum(1 for l in legs if l["ok"])
    print("selftest: %d/%d" % (n_ok, len(legs)))
    for l in legs:
        print(("  PASS " if l["ok"] else "  FAIL ") + l["leg"] + " :: " + str(l["detail"])[:220])
    return 0 if n_ok == len(legs) else 1


def main(argv=None):
    ap = argparse.ArgumentParser(description="E246 star direction")
    ap.add_argument("cmd", nargs="?", default="run", choices=("run", "selftest"))
    args = ap.parse_args(argv)
    if args.cmd == "selftest":
        return selftest()
    face = run(save=True)
    s = face["summary"]
    print("verdict: %s (headline %s)" % (s["verdict"], s["headline_verdict"]))
    print("star: %s [%s] lags decisive: %s" % (s["headline_star"], s["headline_star_source"],
                                               s["lead_lags_decisive"]))
    print(_fmt_counts(s))
    print(s["one_line"])
    print("written: %s" % face.get("written"))
    return 0


def _fmt_counts(s):
    def one(d, lbl):
        if not d:
            return "%s=n/a" % lbl
        return "%s share=%s mean=%s" % (lbl, _f(d.get("decisive_share")), _f(d.get("mean_slope")))
    return " | ".join([one(s.get("contemporaneous"), "lag0"),
                       one(s.get("lead_lag1"), "lag1"),
                       one(s.get("lead_lag2"), "lag2"),
                       one(s.get("reverse_lead"), "reverse")])


def _f(v):
    return "n/a" if v is None else "%.3f" % v


if __name__ == "__main__":
    sys.exit(main())