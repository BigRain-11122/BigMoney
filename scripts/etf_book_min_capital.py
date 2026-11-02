"""How small an account can run the delivered book before the 5-yuan floor eats it?

Every cost number on the shelf is a *rate* per side: 8bp base + square-root impact
(`etf_book_capacity.py`), applied to traded notional. A rate has no floor, and a real
brokerage charge does: the A-share/ETF commission carries a **minimum of 5 CNY per
trade** on most retail accounts. For a book that holds `k = min(1, 0.20/beta)` of NAV
in twelve names, one rebalance buys or sells ~1.5% of NAV per name, so the trade
notional is small and the floor stops being negligible -- the 8bp assumption is then
optimistic, and the published 8.46%/yr is not reachable at that size.

The question this face answers is therefore two-sided, and both halves are money:

  * below the fee-neutral NAV the modelled 8bp is too cheap (the floor binds);
  * above it the same model is too expensive, because 万2.5 is 2.5bp, not 8bp.

Both are measured on the SAME weight path as the published arm, so the delta is
attributable to the fee schedule and nothing else (the r1290/r1291 lesson).

Cost model (one arm per schedule, identical impact term):

    bp_side = max(prop_bp, 1e4 * min_fee_cny / notional) + K * sqrt(p / 1%)

with `notional = dw * capital`, `p = notional / ADV20` known one bar before the fill
(`C.adv_at`, punitive 100bp for a name with no ADV -- reused, never re-typed).
Capital is held constant over the window so each ladder rung is comparable to the
published `@8bp` arm at the same NAV; compounding the account size would confound the
fee question with a second, unrelated one.

Frozen reading rule (written before the run, per the r1325 adoption discipline):

  * `fee_neutral_vs_model` = the capital at which the *median* traded leg's real
    commission equals the modelled 8bp (closed form: 1e4*min_fee/(8bp*dw_median)).
  * `fee_neutral_vs_real` = the capital at which it equals the plain 万2.5 rate.
  * verdict tokens:
      - `FLOOR_BINDS_BELOW_<X>` when fee_neutral_vs_model is inside the ladder and
        the small-capital rungs actually lose CAGR against the 8bp arm;
      - `NO_FLOOR_EFFECT` when even the smallest rung reproduces the 8bp arm;
      - `INSUFFICIENT_LADDER` when the neutral point lies outside the tested sizes
        (then no claim is made -- a size we did not price is not a finding).

  python scripts/etf_book_min_capital.py run
  python scripts/etf_book_min_capital.py --check        # re-derive from published rows
  python scripts/etf_book_min_capital.py --selftest

Exit contract: 0 ok | 2 mechanism failure | 3 published face disagrees with its own
rows (drifted, refuse to print a verdict).
Outputs results/etf_book_min_capital.json.
Exploratory: no preregistration, no verdict adjudication, no ledger booking.
"""
import json
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import numpy as np
import pandas as pd

from scripts import etf_composite_pf as F
from scripts import etf_book_capacity as C
from scripts import etf_book_capacity_rule as R

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUT = os.path.join(ROOT, "results", "etf_book_min_capital.json")
EPS = 1e-12

# Retail brokerage assumptions, stated as parameters rather than buried in the cost line.
MIN_FEE_CNY = 5.0
SCHEDULES = (
    {"name": "wan2.5+5", "prop_bp": 2.5, "min_fee_cny": MIN_FEE_CNY},
    {"name": "wan1.5+5", "prop_bp": 1.5, "min_fee_cny": MIN_FEE_CNY},
    {"name": "wan2.5+0", "prop_bp": 2.5, "min_fee_cny": 0.0},
)
CAPITALS = (1e4, 2e4, 5e4, 1e5, 2e5, 4e5, 1e6, 1.5e6, 3e6, 1e7)
BASE_BP = C.BASE_BP            # the published flat assumption (imported, not retyped)

# The neutral point is a closed form in the median traded leg, and that leg is a property
# of the SAMPLE, not of the fee schedule: a window that churns harder trades bigger pieces,
# so the same 8bp model stops being optimistic sooner. Each entry is (name, face start,
# inclusive cutoff or None). The path slice reuses `curve`, so there is no second leg-scan.
WINDOWS = (
    ("published_2020", "2020-01-01", None),
    ("full_2015", "2015-01-01", None),
    ("pre_2020", "2015-01-01", "2019-12-31"),
)
WINDOW_STABLE_PCT = 10.0       # frozen before the run: a >10% move is not a constant

# The neutral point also moves with the BASKET, not only with the years: more names means
# smaller legs means the cash floor bites at a bigger account. Same engine, same rule,
# same grid -- only n_hold changes (prereg-free reading rule frozen here, before the run).
WIDTHS = (5, 8, 12, 20)
WIDTH_STABLE_PCT = 10.0

CARD_JSON = os.path.join(ROOT, "results", "etf_book_production", "latest.json")


def ladder_width(card_json=None):
    """How many names the ladder must be priced on: the ones the delivered card holds.

    The engine's own default is 5 (`F.N_HOLD`), but the production card overrides it via
    `config.n_hold`, and a ladder priced on the engine default answers a question about a
    basket nobody is holding (r1240: 5 names -> 67,737 CNY, 12 names -> 203,007 CNY --
    a 3.0x difference in the answer to 'how much money do I need').

    Returns `(n_hold, source)`; a missing or unreadable card falls back to the engine
    default and *says so*, so the face never wears the delivered label by accident.
    """
    path = card_json or CARD_JSON
    try:
        with open(path, encoding="utf-8") as fh:
            n = (json.load(fh).get("config") or {}).get("n_hold")
        if n is not None and int(n) > 0:
            return int(n), "production_card"
    except Exception:                                           # noqa: BLE001
        pass
    return int(F.N_HOLD), "engine_default"


def fee_bp(prop_bp, min_fee_cny, notional):
    """Per-side commission in bp: the proportional rate with a cash floor."""
    if notional is None or not np.isfinite(notional) or notional <= EPS:
        return float(prop_bp) if not min_fee_cny else float(min_fee_cny) * 1e4
    floor_bp = 1e4 * float(min_fee_cny) / float(notional)
    return float(max(float(prop_bp), floor_bp))


def neutral_nav(dw, prop_bp, min_fee_cny):
    """Capital at which the cash floor stops binding for a leg of weight `dw`.

    `fee_bp == prop_bp` exactly at notional = 1e4*min_fee/prop_bp, and notional = NAV*dw.
    Without a floor the neutral point is 0 (nothing to neutralise).
    """
    dw = float(dw)
    if not min_fee_cny or dw <= EPS or prop_bp <= 0:
        return 0.0
    return 1e4 * float(min_fee_cny) / (float(prop_bp) * dw)


def curve(face, capital, prop_bp, min_fee_cny, k_bp=C.IMPACT_BP_PER_PCT,
          path=None, trace=False):
    """Daily NAV of the delivered rule at `capital`, priced with a commission floor.

    Returns (level series, per-decision rows, counters). The impact term is the
    published one; only the base rate is replaced by `max(prop, floor)`, so the delta
    against the `@8bp` arm is the fee schedule and nothing else.
    """
    if path is None:
        path = R.weight_path(face)
    amt = face["amt"]
    rp, rf = face["rp"], face["rf"]
    prev_w = {}
    equity = 1.0
    levels = []
    rows = []
    below_floor = 0
    legs_total = 0
    fee_cny = 0.0
    dws = []
    for d, w, cash in path:
        k = 1.0 - cash
        adv_row = C.adv_at(amt, d, back=1)
        cost = 0.0
        day_legs = 0
        for s in sorted(set(prev_w) | set(w)):
            dw = abs(w.get(s, 0.0) - prev_w.get(s, 0.0))
            if dw <= R.EPS:
                continue
            day_legs += 1
            dws.append(dw)
            notional = dw * capital
            base = fee_bp(prop_bp, min_fee_cny, notional)
            if min_fee_cny and base > float(prop_bp) + 1e-12:
                below_floor += 1
            adv = np.nan if adv_row is None else float(adv_row.get(s, np.nan))
            if not np.isfinite(adv) or adv <= 0:
                bp = C.PUNITIVE_BP
            else:
                bp = base + k_bp * np.sqrt((notional / adv) / 0.01)
            cost += dw * bp
            fee_cny += dw * base * capital / 1e4
        legs_total += day_legs
        cost /= 1e4
        if trace and day_legs:
            rows.append({"date": str(pd.Timestamp(d).date()), "legs": day_legs,
                         "cost_frac": round(cost, 10)})
        r = k * float(rp.get(d, 0.0)) + cash * float(rf.get(d, 0.0))
        equity *= (1.0 + r) * (1.0 - cost)
        levels.append((d, equity))
        prev_w = w
    ser = pd.Series(dict(levels))
    dws = np.asarray(dws, dtype=float)
    cnt = {"legs": legs_total, "legs_below_floor": below_floor,
           "share_below_floor": (float(below_floor) / legs_total) if legs_total else None,
           "fee_cny_total": round(fee_cny, 2),
           "dw_median": float(np.median(dws)) if len(dws) else None,
           "dw_mean": float(np.mean(dws)) if len(dws) else None}
    return ser, rows, cnt


def _verdict(rows, fee_neutral_model, fee_neutral_real, ladder_bounds):
    """Frozen reading rule -- no hand-written verdict, it is derived from the rows."""
    lo, hi = ladder_bounds
    small = rows[0]
    if small.get("cagr") is None:
        return "INSUFFICIENT_LADDER"
    worsens = small["cagr"] < small["ref_cagr"] - 1e-9
    if fee_neutral_model is None:
        return "INSUFFICIENT_LADDER"
    if not worsens:
        return "NO_FLOOR_EFFECT"
    if not (lo < fee_neutral_model <= hi):
        return "INSUFFICIENT_LADDER"
    token = "FLOOR_BINDS_BELOW_%d" % int(round(fee_neutral_model))
    if fee_neutral_real and fee_neutral_real > fee_neutral_model:
        token += "_AND_MODEL_GENEROUS_ABOVE_%d" % int(round(fee_neutral_real))
    return token


def window_dependence(n_hold=None):
    """Is the fee-neutral NAV a property of the book, or of the years it was priced on?

    One arm, one engine, three samples, and -- since r1241 -- the SAME basket width as the
    ladder. A window table priced on a different width would move for two reasons at once
    and could no longer be read against the published neutral point it is compared with.
    The traded-leg median is read off the SAME `curve` the ladder uses (no second leg
    scan), once per window, at a capital large enough to leave the floor out of the way --
    `dw` does not depend on capital at all, so the rung only serves to make the call
    comparable to the published rows.
    """
    rows = []
    for name, start, cutoff in WINDOWS:
        face = R.build_face(start=start, n_hold=n_hold)
        path = R.weight_path(face)
        if cutoff:
            _cut = pd.Timestamp(cutoff)
            path = [(d, w, c) for (d, w, c) in path if pd.Timestamp(d) <= _cut]
        if not path:
            rows.append({"window": name, "start": start, "cutoff": cutoff,
                         "dw_median": None, "dw_mean": None,
                         "fee_neutral_vs_model_nav": None,
                         "fee_neutral_vs_real_nav": None,
                         "fee_neutral_vs_model_nav_mean_leg": None, "legs": 0,
                         "first_bar": None, "last_bar": None})
            continue
        ser, _r, cnt = curve(face, 1e6, BASE_BP, 0.0, path=path)
        dw = cnt["dw_median"]
        dmean = cnt.get("dw_mean")
        rows.append({
            "window": name,
            "start": start,
            "cutoff": cutoff,
            "first_bar": str(pd.Timestamp(path[0][0]).date()),
            "last_bar": str(pd.Timestamp(path[-1][0]).date()),
            "bars": len(ser),
            "legs": cnt["legs"],
            "dw_median": None if dw is None else round(dw, 8),
            # the mean leg is the size-weighted typical trade: where a book mostly holds
            # and occasionally rotates, the median leg is a rounding-sized trim and its
            # closed form quotes a break-even no account ever reaches. Both are published
            # so the reader can see which one the verdict was taken from (r1241).
            "dw_mean": None if dmean is None else round(dmean, 8),
            "fee_neutral_vs_model_nav": (None if dw is None else
                                         round(neutral_nav(dw, BASE_BP, MIN_FEE_CNY), 2)),
            "fee_neutral_vs_real_nav": (None if dw is None else
                                        round(neutral_nav(dw, SCHEDULES[0]["prop_bp"],
                                                          MIN_FEE_CNY), 2)),
            "fee_neutral_vs_model_nav_mean_leg": (None if not dmean else
                                                  round(neutral_nav(dmean, BASE_BP,
                                                                    MIN_FEE_CNY), 2)),
        })
    return rows


def _window_verdict(rows, reference=None, tol_pct=WINDOW_STABLE_PCT):
    """Frozen reading rule: how far the neutral point travels across samples (%)."""
    vals = [r["fee_neutral_vs_model_nav"] for r in rows
            if r.get("fee_neutral_vs_model_nav") is not None]
    if len(vals) < 2:
        return "WINDOW_UNMEASURED", None
    ref = reference if reference is not None else vals[0]
    spread = 100.0 * (max(vals) - min(vals)) / ref if ref else None
    if spread is None:
        return "WINDOW_UNMEASURED", None
    token = ("BREAKEVEN_WINDOW_MOVES_%dPCT" % int(round(spread))
             if spread > tol_pct else "BREAKEVEN_WINDOW_STABLE")
    return token, round(spread, 2)


def width_dependence(start=R.START):
    """Does the fee-neutral NAV depend on how many names the basket holds?

    The neutral point is 1e4*min_fee/(8bp*dw_median), so it moves exactly with the
    traded leg. A wider basket splits the same NAV into more (smaller) legs, so the
    floor should bind at a LARGER account. That is a prediction, not a reading -- each
    width re-ranks the SAME panel with the SAME rule and is priced on its own path.
    """
    rows = []
    for n in WIDTHS:
        face = R.build_face(start=start, n_hold=n)
        path = R.weight_path(face)
        if not path:
            rows.append({"n_hold": n, "names_median": None, "dw_median": None,
                         "fee_neutral_vs_model_nav": None, "cagr_8bp": None,
                         "legs": 0})
            continue
        ser, _r, cnt = curve(face, 1e6, BASE_BP, 0.0, path=path)
        m = F.metrics(ser, "width %d" % n)
        dw = cnt["dw_median"]
        names = [len(w) for _d, w, _c in path if w]
        rows.append({
            "n_hold": n,
            "names_median": (float(np.median(names)) if names else None),
            "first_bar": str(pd.Timestamp(path[0][0]).date()),
            "last_bar": str(pd.Timestamp(path[-1][0]).date()),
            "bars": len(ser),
            "legs": cnt["legs"],
            "dw_median": None if dw is None else round(dw, 8),
            "fee_neutral_vs_model_nav": (None if dw is None else
                                         round(neutral_nav(dw, BASE_BP, MIN_FEE_CNY), 2)),
            "cagr_8bp": m.get("cagr"),
            "sharpe_8bp": m.get("sharpe"),
        })
    return rows


def _width_verdict(rows, reference=None, tol_pct=WIDTH_STABLE_PCT):
    """Frozen reading rule: how far the neutral point travels across basket widths (%)."""
    vals = [r["fee_neutral_vs_model_nav"] for r in rows
            if r.get("fee_neutral_vs_model_nav") is not None]
    if len(vals) < 2:
        return "WIDTH_UNMEASURED", None
    ref = reference if reference is not None else vals[0]
    spread = 100.0 * (max(vals) - min(vals)) / ref if ref else None
    if spread is None:
        return "WIDTH_UNMEASURED", None
    token = ("BREAKEVEN_WIDTH_MOVES_%dPCT" % int(round(spread))
             if spread > tol_pct else "BREAKEVEN_WIDTH_STABLE")
    return token, round(spread, 2)


def _delivered_width(rows, published_neutral):
    """Which width is the ladder actually priced on? The one whose own neutral matches it.

    This is a check on the face, not a parameter: if no width reproduces the published
    number, the ladder's path is not one of the widths in the sweep and that must be
    said rather than guessed (an unmatched path reads None).
    """
    if published_neutral is None:
        return None
    best = None
    for r in rows:
        v = r.get("fee_neutral_vs_model_nav")
        if v is None:
            continue
        d = abs(v - published_neutral)
        if best is None or d < best[0]:
            best = (d, r["n_hold"])
    if best is None:
        return None
    # published precision is 0.01 CNY; anything inside 1% is the same path
    return best[1] if best[0] <= 0.01 * max(1.0, published_neutral) else None


def run(start=R.START, n_hold=None):
    """Price the ladder on the basket the delivered card holds, not on the engine default."""
    n_used, n_source = ((int(n_hold), "explicit") if n_hold is not None
                        else ladder_width())
    face = R.build_face(start=start, n_hold=n_used)
    path = R.weight_path(face)
    # reference: the published flat-8bp assumption, same path, same impact term
    ref_rows = {}
    for capital in CAPITALS:
        ser, _r, _c = curve(face, capital, BASE_BP, 0.0, path=path)
        ref_rows[capital] = F.metrics(ser, "8bp @ %.0e" % capital)

    ladder = []
    dw_median = None
    dw_mean = None
    for sched in SCHEDULES:
        for capital in CAPITALS:
            ser, rows, cnt = curve(face, capital, sched["prop_bp"],
                                   sched["min_fee_cny"], path=path, trace=True)
            m = F.metrics(ser, "%s @ %.0e" % (sched["name"], capital))
            ref = ref_rows[capital]
            row = {"schedule": sched["name"], "capital": capital,
                   "cagr": m.get("cagr"), "vol": m.get("vol"),
                   "sharpe": m.get("sharpe"), "maxdd": m.get("maxdd"),
                   "ref_cagr": ref.get("cagr"), "ref_sharpe": ref.get("sharpe"),
                   "legs": cnt["legs"],
                   "share_below_floor": (None if cnt["share_below_floor"] is None
                                         else round(cnt["share_below_floor"], 6)),
                   "fee_cny_total": cnt["fee_cny_total"],
                   "dw_median": (None if cnt["dw_median"] is None
                                 else round(cnt["dw_median"], 8)),
                   "dw_mean": (None if cnt.get("dw_mean") is None
                               else round(cnt["dw_mean"], 8))}
            if m.get("cagr") is not None and ref.get("cagr") is not None:
                row["delta_vs_8bp_pp"] = round(100.0 * (m["cagr"] - ref["cagr"]), 4)
                row["annual_delta_cny"] = round(capital * (m["cagr"] - ref["cagr"]), 0)
            if row["dw_median"]:
                dw_median = row["dw_median"]
            if row.get("dw_mean"):
                dw_mean = row["dw_mean"]
            ladder.append(row)

    primary = SCHEDULES[0]
    fee_neutral_model = neutral_nav(dw_median, BASE_BP, primary["min_fee_cny"])
    fee_neutral_real = neutral_nav(dw_median, primary["prop_bp"], primary["min_fee_cny"])
    primary_rows = [r for r in ladder if r["schedule"] == primary["name"]]
    verdict = _verdict(primary_rows, fee_neutral_model, fee_neutral_real,
                       (min(CAPITALS), max(CAPITALS)))

    window_rows = window_dependence(n_hold=n_used)
    window_verdict, window_spread_pct = _window_verdict(window_rows, fee_neutral_model)

    width_rows = width_dependence(start=start)
    width_verdict, width_spread_pct = _width_verdict(width_rows, fee_neutral_model)

    out = {
        "ts": pd.Timestamp.now().strftime("%Y-%m-%d %H:%M:%S"),
        "evidence_cutoff": str(pd.Timestamp(face["idx"][-1]).date()),
        "script": "scripts/etf_book_min_capital.py",
        "config": {"capital_grid": list(CAPITALS), "schedules": list(SCHEDULES),
                   "base_bp_published": BASE_BP,
                   "impact_bp_per_pct": C.IMPACT_BP_PER_PCT,
                   "punitive_bp": C.PUNITIVE_BP,
                   "rebal": R.REBAL, "start": start,
                   "ladder_n_hold": n_used, "ladder_n_hold_source": n_source,
                   "dw_median_all_legs": (None if dw_median is None
                                          else round(dw_median, 8)),
                   "dw_mean_all_legs": (None if dw_mean is None
                                        else round(dw_mean, 8))},
        "fee_neutral_vs_model_nav": (None if fee_neutral_model is None
                                     else round(fee_neutral_model, 2)),
        "fee_neutral_vs_real_nav": (None if fee_neutral_real is None
                                    else round(fee_neutral_real, 2)),
# the same question read off the MEAN leg (size-weighted typical trade) rather than the
        # median leg; published side by side because a book that mostly holds and rarely
        # rotates makes the median leg a rounding-sized trim (r1241)
        "fee_neutral_vs_model_nav_mean_leg": (None if not dw_mean else
                                              round(neutral_nav(dw_mean, BASE_BP,
                                                                primary["min_fee_cny"]), 2)),
        "verdict": verdict,
        "ladder": ladder,
        "window": {
            "verdict": window_verdict,
            "spread_pct_of_published": window_spread_pct,
            "stability_tol_pct": WINDOW_STABLE_PCT,
            "rows": window_rows,
            "note": ("the traded-leg median is measured on three samples with the same "
                     "engine; the reported neutral NAV is the published 2020-2026 one, "
                     "and the window rows say how far it travels when the sample changes"),
        },
        "method_note": ("one engine, one weight path, one window; only the base "
                        "per-side rate is replaced by max(prop, 5 CNY / notional), "
                        "impact term identical. Capital held constant per rung so each "
                        "delta is attributable to the fee schedule (compare vs the "
                        "same-NAV @8bp arm, not across rungs)."),
        "width": {
            "verdict": width_verdict,
            "spread_pct_of_published": width_spread_pct,
            "stability_tol_pct": WIDTH_STABLE_PCT,
            "widths": list(WIDTHS),
            "published_path_width": (
                None if not width_rows else _delivered_width(width_rows, fee_neutral_model)),
            "rows": width_rows,
            "note": ("each width re-ranks the same panel with the same rule at its own "
                     "n_hold; the neutral NAV is a closed form in that path's traded-leg "
                     "median, so a width row is a reading and not an extrapolation"),
        },
        "scope_note": ("fees only: spread is inside the 8bp reference and is NOT added "
                       "here; a broker with no 5-yuan floor is the wan2.5+0 row; the "
                       "delivered rule's own turnover is imported from the engine."),
    }
    with open(OUT, "w", encoding="utf-8") as fh:
        json.dump(out, fh, ensure_ascii=False, indent=1)
    return out


def _close(got, want, abs_tol=0.02, rel_tol=1e-5):
    """Published rows carry the traded leg rounded to 8dp, so a closed form recomputed
    from them differs in the last digits -- at 4e5 CNY that is 0.06 CNY, not drift.
    Absolute 0.02 CNY for small numbers, 1e-5 relative above (a width change moves this
    by thousands, so the tolerance cannot swallow a real disagreement)."""
    try:
        a, b = float(got), float(want)
    except (TypeError, ValueError):
        return False
    return abs(a - b) <= max(abs_tol, rel_tol * max(1.0, abs(b)))


def check():
    """Re-derive the verdict and the neutral points from the published rows."""
    if not os.path.exists(OUT):
        print("min_capital: published face missing")
        return 2
    with open(OUT, encoding="utf-8") as fh:
        d = json.load(fh)
    cfg = d["config"]
    dw = cfg["dw_median_all_legs"]
    primary = cfg["schedules"][0]
    model = neutral_nav(dw, cfg["base_bp_published"], primary["min_fee_cny"])
    real = neutral_nav(dw, primary["prop_bp"], primary["min_fee_cny"])
    problems = []
    # published precision is 0.01 CNY: compare at that resolution, not at float equality
    if d["fee_neutral_vs_model_nav"] is not None and \
            abs(model - d["fee_neutral_vs_model_nav"]) > 0.02:
        problems.append("fee_neutral_vs_model_nav %.2f != %.2f"
                        % (d["fee_neutral_vs_model_nav"], model))
    if d["fee_neutral_vs_real_nav"] is not None and \
            abs(real - d["fee_neutral_vs_real_nav"]) > 0.02:
        problems.append("fee_neutral_vs_real_nav %.2f != %.2f"
                        % (d["fee_neutral_vs_real_nav"], real))
    rows = [r for r in d["ladder"] if r["schedule"] == primary["name"]]
    want = _verdict(rows, model, real, (min(cfg["capital_grid"]), max(cfg["capital_grid"])))
    if want != d["verdict"]:
        problems.append("verdict %s != recomputed %s" % (d["verdict"], want))
    # the window rows must satisfy their own arithmetic, and the token must come from them
    w = d.get("window") or {}
    for r in w.get("rows") or []:
        dw_w = r.get("dw_median")
        if dw_w is None or r.get("fee_neutral_vs_model_nav") is None:
            continue
        want_w = neutral_nav(dw_w, cfg["base_bp_published"], primary["min_fee_cny"])
        if not _close(want_w, r["fee_neutral_vs_model_nav"]):
            problems.append("window %s: neutral %.2f != %.2f"
                            % (r.get("window"), r["fee_neutral_vs_model_nav"], want_w))
    if w.get("rows"):
        want_wv, want_ws = _window_verdict(w["rows"],
                                           d.get("fee_neutral_vs_model_nav"))
        if want_wv != w.get("verdict"):
            problems.append("window verdict %s != recomputed %s"
                            % (w.get("verdict"), want_wv))
        if (want_ws is not None and w.get("spread_pct_of_published") is not None
                and abs(want_ws - w["spread_pct_of_published"]) > 0.02):
            problems.append("window spread %.2f != %.2f"
                            % (w["spread_pct_of_published"], want_ws))
    # the width block must satisfy the same arithmetic, and its token must come from rows.
    # (r1241: this block used to sit inside `if w.get("rows")` -- a face with no window
    # rows would have skipped every width check and still printed "check OK".)
    wid = d.get("width") or {}
    for r in wid.get("rows") or []:
        dw_w = r.get("dw_median")
        if dw_w is None or r.get("fee_neutral_vs_model_nav") is None:
            continue
        want_w = neutral_nav(dw_w, cfg["base_bp_published"], primary["min_fee_cny"])
        if not _close(want_w, r["fee_neutral_vs_model_nav"]):
            problems.append("width %s: neutral %.2f != %.2f"
                            % (r.get("n_hold"), r["fee_neutral_vs_model_nav"], want_w))
    if wid.get("rows"):
        want_wv, want_ws = _width_verdict(wid["rows"],
                                          d.get("fee_neutral_vs_model_nav"))
        if want_wv != wid.get("verdict"):
            problems.append("width verdict %s != recomputed %s"
                            % (wid.get("verdict"), want_wv))
        if (want_ws is not None and wid.get("spread_pct_of_published") is not None
                and abs(want_ws - wid["spread_pct_of_published"]) > 0.02):
            problems.append("width spread %.2f != %.2f"
                            % (wid["spread_pct_of_published"], want_ws))
        want_pw = _delivered_width(wid["rows"], d.get("fee_neutral_vs_model_nav"))
        if want_pw != wid.get("published_path_width"):
            problems.append("published_path_width %s != recomputed %s"
                            % (wid.get("published_path_width"), want_pw))
        # the width the ladder was PRICED on must be the width its own rows point at;
        # otherwise the rungs and the sweep describe two different baskets (r1240/r1241)
        if cfg.get("ladder_n_hold") is not None and want_pw is not None \
                and int(cfg["ladder_n_hold"]) != int(want_pw):
            problems.append("ladder priced at %s names but its rows read %s"
                            % (cfg.get("ladder_n_hold"), want_pw))
    if problems:
        for p in problems:
            print("DRIFT: " + p)
        return 3
    print("min_capital: check OK (%s, neutral vs model %s CNY, vs real %s CNY)"
          % (d["verdict"], d["fee_neutral_vs_model_nav"], d["fee_neutral_vs_real_nav"]))
    return 0


def selftest():
    ok = [0, 0]

    def chk(name, cond, detail=""):
        ok[1] += 1
        ok[0] += int(bool(cond))
        print("[%s] %s%s" % ("PASS" if cond else "FAIL", name,
                             "" if not detail else " | " + str(detail)))

    # L1-L4: the fee function itself, exact
    chk("L1 a 1,000 CNY trade pays the 5-yuan floor, not 2.5bp",
        abs(fee_bp(2.5, 5.0, 1000.0) - 50.0) < 1e-12, fee_bp(2.5, 5.0, 1000.0))
    chk("L2 a 1,000,000 CNY trade pays the proportional rate",
        abs(fee_bp(2.5, 5.0, 1e6) - 2.5) < 1e-12, fee_bp(2.5, 5.0, 1e6))
    chk("L3 the crossover notional is exactly 20,000 CNY (floor == 2.5bp)",
        abs(fee_bp(2.5, 5.0, 20000.0) - 2.5) < 1e-12)
    chk("L4 no floor means the proportional rate at any size",
        abs(fee_bp(2.5, 0.0, 1.0) - 2.5) < 1e-12 and abs(fee_bp(2.5, 0.0, 1e9) - 2.5) < 1e-12)

    # L5-L6: the closed form, both sides of the boundary
    n = neutral_nav(0.02, 2.5, 5.0)
    chk("L5 neutral NAV = 1e4*min_fee/(prop*dw) = 1,000,000 for dw=2% at 2.5bp",
        abs(n - 1e6) < 1e-9, n)
    chk("L6 exactly at the neutral NAV the floor does not bind; a hair below it, it does",
        abs(fee_bp(2.5, 5.0, n * 0.02) - 2.5) < 1e-12
        and fee_bp(2.5, 5.0, n * 0.02 * 0.999) > 2.5 + 1e-9)

    # L7-L9: a curve on a hand-built fixture, so the arithmetic is pinned, not trusted
    idx = pd.to_datetime(["2020-01-02", "2020-01-03", "2020-01-06"])
    face = {"idx": idx, "rp": pd.Series([0.0, 0.01, 0.0], index=idx),
            "rf": pd.Series(0.0, index=idx),
            "amt": pd.DataFrame({"A": [1e12, 1e12, 1e12]}, index=idx)}
    path = [(idx[0], {}, 1.0), (idx[1], {"A": 1.0}, 0.0), (idx[2], {"A": 1.0}, 0.0)]
    ser, rows, cnt = curve(face, 1000.0, 2.5, 5.0, k_bp=0.0, path=path)
    # one buy of the whole account: notional 1,000 -> 50bp on the traded weight 1.0
    want = (1 + 0.01) * (1 - 50.0 / 1e4)
    chk("L7 a 1,000 CNY account pays 50bp on the entry bar (fixture, exact)",
        abs(float(ser.iloc[-1]) - want) < 1e-12, float(ser.iloc[-1]))
    chk("L8 the fixture trade is counted as below the floor", cnt["legs_below_floor"] == 1,
        cnt)
    ser2, _r2, cnt2 = curve(face, 1e6, 2.5, 5.0, k_bp=0.0, path=path)
    chk("L9 the same trade at 1,000,000 CNY pays 2.5bp and is not below the floor",
        abs(float(ser2.iloc[-1]) - (1 + 0.01) * (1 - 2.5 / 1e4)) < 1e-12
        and cnt2["legs_below_floor"] == 0, (float(ser2.iloc[-1]), cnt2))

    # L10: with the floor switched off the two schedules must be bit-identical
    ser3, _r3, _c3 = curve(face, 1000.0, 2.5, 0.0, k_bp=0.0, path=path)
    ser4, _r4, _c4 = curve(face, 1000.0, 2.5, 5.0, k_bp=0.0, path=path)
    chk("L10 the floor is the only difference between the two arms (no-floor is cheaper)",
        float(ser3.iloc[-1]) > float(ser4.iloc[-1]) + 1e-9)

    # L11: a bigger account never earns less under a floor (monotone in capital)
    small, _a, _b = curve(face, 1e3, 2.5, 5.0, k_bp=0.0, path=path)
    big, _c, _d = curve(face, 5e5, 2.5, 5.0, k_bp=0.0, path=path)
    chk("L11 monotone in capital: 500,000 beats 1,000 on the same path (50bp -> 2.5bp)",
        float(big.iloc[-1]) > float(small.iloc[-1]) + 1e-9)

    # L12: a size we did not price yields no claim
    chk("L12 an out-of-ladder neutral point refuses a verdict",
        _verdict([{"cagr": 0.05, "ref_cagr": 0.06}], 5e8, 1e9, (1e4, 1e7))
        == "INSUFFICIENT_LADDER")
    chk("L13 a small rung that matches the 8bp arm reports no floor effect",
        _verdict([{"cagr": 0.06, "ref_cagr": 0.06}], 1e5, 1e6, (1e4, 1e7))
        == "NO_FLOOR_EFFECT")

    # L14-L17: the window face. The point of these legs is that the neutral NAV is not a
    # constant of the strategy -- it is a function of the traded-leg median, which is what
    # the sample decides. Fixtures, so the arithmetic is pinned without touching a panel.
    _w_same = [{"window": "a", "fee_neutral_vs_model_nav": 67737.42},
               {"window": "b", "fee_neutral_vs_model_nav": 68000.0}]
    tok, spread = _window_verdict(_w_same, 67737.42)
    chk("L14 a 0.4% spread across samples reads as a constant",
        tok == "BREAKEVEN_WINDOW_STABLE", (tok, spread))
    _w_move = [{"window": "a", "fee_neutral_vs_model_nav": 67737.42},
               {"window": "b", "fee_neutral_vs_model_nav": 49849.0}]
    tok2, spread2 = _window_verdict(_w_move, 67737.42)
    chk("L15 a 26% spread reads as movement, not as a constant",
        tok2.startswith("BREAKEVEN_WINDOW_MOVES_") and spread2 > 25.0, (tok2, spread2))
    chk("L16 one window (or none) makes no claim at all",
        _window_verdict([{"window": "a", "fee_neutral_vs_model_nav": 1.0}], 1.0)[0]
        == "WINDOW_UNMEASURED")
    # the two readings must move in the SAME direction as dw: bigger legs -> cheaper floor
    dw_big = 0.20
    dw_small = 0.05
    chk("L17 a harder-churning sample needs less capital for the same 8bp (dw 20% vs 5%)",
        neutral_nav(dw_big, BASE_BP, 5.0) < neutral_nav(dw_small, BASE_BP, 5.0),
        (neutral_nav(dw_big, BASE_BP, 5.0), neutral_nav(dw_small, BASE_BP, 5.0)))

    # L18-L21: the width face. The neutral point is a closed form in the traded leg, so a
    # wider basket must need MORE capital -- that is arithmetic, and the fixtures pin it
    # so a panel result can be read against it instead of being its own control.
    chk("L18 halving the traded leg doubles the neutral NAV (1/n arithmetic)",
        abs(neutral_nav(0.02, BASE_BP, 5.0) - 2 * neutral_nav(0.04, BASE_BP, 5.0)) < 1e-6,
        (neutral_nav(0.02, BASE_BP, 5.0), neutral_nav(0.04, BASE_BP, 5.0)))
    _w_flat = [{"n_hold": 5, "fee_neutral_vs_model_nav": 67737.42},
               {"n_hold": 12, "fee_neutral_vs_model_nav": 69000.0}]
    _tok_w, _sp_w = _width_verdict(_w_flat, 67737.42)
    chk("L19 a 2% spread across widths reads as a constant",
        _tok_w == "BREAKEVEN_WIDTH_STABLE", (_tok_w, _sp_w))
    _w_up = [{"n_hold": 5, "fee_neutral_vs_model_nav": 67737.42},
             {"n_hold": 20, "fee_neutral_vs_model_nav": 169000.0}]
    _tok_w2, _sp_w2 = _width_verdict(_w_up, 67737.42)
    chk("L20 a 150% spread reads as movement, not as a constant",
        _tok_w2.startswith("BREAKEVEN_WIDTH_MOVES_") and _sp_w2 > 100.0,
        (_tok_w2, _sp_w2))
    chk("L21 a path no width reproduces is reported as unmatched, never guessed",
        _delivered_width(_w_up, 500000.0) is None
        and _delivered_width(_w_up, 68000.0) == 5)

    # L22-L23: which basket the ladder is priced on. The engine default is 5 names, the
    # delivered card holds 12, and the answer moves 3x between them -- so the ladder must
    # read the card, and must label its own source when the card is missing.
    import tempfile as _tempfile
    _card_dir = _tempfile.mkdtemp()
    _card = os.path.join(_card_dir, "latest.json")
    with open(_card, "w", encoding="utf-8") as _fh:
        json.dump({"config": {"n_hold": 12}}, _fh)
    chk("L22 the ladder width is the delivered card's width, and says where it came from",
        ladder_width(_card) == (12, "production_card"), ladder_width(_card))
    _none = os.path.join(_card_dir, "absent.json")
    chk("L23 a missing card falls back to the engine default and names the fallback",
        ladder_width(_none) == (int(F.N_HOLD), "engine_default"), ladder_width(_none))

    print("selftest %d/%d" % (ok[0], ok[1]))
    return 0 if ok[0] == ok[1] else 1


def main(argv):
    argv = [a for a in argv[1:]]
    if "--selftest" in argv:
        return selftest()
    if "--check" in argv:
        return check()
    out = run()
    print("min capital: %s | neutral vs 8bp model %.0f CNY | vs real %.0f CNY"
          % (out["verdict"], out["fee_neutral_vs_model_nav"] or 0,
             out["fee_neutral_vs_real_nav"] or 0))
    print("\n capital      schedule   cagr   vs 8bp    below-floor   fee CNY")
    for r in out["ladder"]:
        print(" %9.0f  %-10s %6.2f%%  %+6.2fpp  %8.2f%%   %9.0f"
              % (r["capital"], r["schedule"], 100 * (r["cagr"] or 0),
                 r.get("delta_vs_8bp_pp") or 0,
                 100 * (r["share_below_floor"] or 0), r["fee_cny_total"]))
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))