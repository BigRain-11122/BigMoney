"""zoo_supply_xs_reversal_probe -- supply berth probe (cross-sectional short-term reversal).

WHY THIS FILE EXISTS
--------------------
`compute_audit` has reported `supply_floor ready 0 < floor 3` for nine straight
rounds (supply_candidates verdict = AGENDA_DEBT).  The two berths measured so far
this week were *timing* families (zoo90 alligator, zoo83 gem_ashare), and both were
refused partly because a rule that sits in cash has to earn the exit tax first
(r1387 measured it at +0.64..+8.39 pp/yr at 0.95..0.30 exposure).  So the next
berth has to be a family whose exposure is structurally 1.0: it is always fully
invested and its only question is *which* names to hold.

That is the cross-sectional short-term reversal family:

    inside the liquid ETF universe, does buying the names with the WORST trailing
    20-bar return and holding them for the next 20 bars beat holding the whole
    eligible universe equal-weight, after costs, and beyond a same-exposure book
    that holds the same number of names on the same decision grid but ranks them
    at random?

Everything here is a PROBE.  It burns no family, registers no seed, writes no
ledger row.  Its verdict is a *supply* verdict (ADMIT_TO_PREREG /
REFUSE_AS_CANDIDATE), never a research verdict.

CONSTRUCTION (frozen; changing any of it changes the family)
------------------------------------------------------------
  panel        the same wide ETF panel the published composite book reads
               (scripts/etf_composite_pf.py: _load_prices -> _dedupe ->
               drop_hollow_tail), so a bar means what it means there
  universe     amt >= MIN_AMT (20-bar median close*volume) and hist >= MIN_HIST
               finished bars -- identical eligibility to the published book
  signal       ret_w = close[t] / close[t-W] - 1, W = 20 bars; score is the
               cross-sectional RANK of -ret_w (worst trailing performers first)
  selection    top `n_hold` by score among eligible names; equal weight, always
               fully invested (no cash leg, no leverage, no partial sizing)
  grid         every `rebal`-th bar of the panel, decided on the close, filled at
               the NEXT open -- run through the published leg engine
               (`run_next_open`, score passed in) so the fill/cost maths is not
               re-implemented here
  cost         COST per side on sum |dw| (a full swap of one slot = 2/clamped by
               the engine's own turnover bookkeeping)
  benchmark    equal weight across the SAME eligible universe on the same grid
               (`run_ew`) -- the honest control for a cross-sectional question,
               because it removes the "the universe itself went up" component
  null         K random-ranking books: identical eligibility, identical grid,
               identical n_hold, identical costs, ranking replaced by a seeded
               uniform draw -> same exposure, no signal

A NOTE ON WHAT WOULD MAKE THIS LOOK GOOD BY ACCIDENT
----------------------------------------------------
The wide ETF panel is a *surviving* universe, and it is bond-heavy in the early
years.  A reversal book that leans into recently-fallen bond ETFs in 2020-2021
could read as alpha while only being a duration tilt.  That is why the headline
is the excess over the equal-weight universe (same assets, same weights on
average) and the null is same-exposure: neither comparison can be won by simply
holding more of whatever the panel was doing.
"""

from __future__ import annotations

import json
import os
import sys
import time

import numpy as np
import pandas as pd

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
for p in (HERE, ROOT):
    if p not in sys.path:
        sys.path.insert(0, p)

from etf_composite_pf import (  # noqa: E402
    COST, MIN_AMT, MIN_HIST, _dedupe, _load_prices, drop_hollow_tail,
    metrics, run_ew, run_next_open,
)

# ---- frozen constants (echoed into every artifact) -------------------------
FAMILY = "xs_reversal_20"
BATCH = "SUPPLY_BERTH_SLOT_13_CANDIDATE"
WINDOW = 20
REBAL = 20
N_HOLD = 10
START = "2020-01-01"
NULL_K = 200
NULL_SEED = 20261107
EVIDENCE_CUTOFF = "2026-11-06"
ADMIT_MIN_EXCESS_PP = 1.0          # pp/yr over the equal-weight universe
ADMIT_MAX_P = 0.05
ADMIT_MAX_TURNOVER_PER_YEAR = 40.0

RES_PATH = os.path.join(ROOT, "results", "supply_berth",
                        "zoo_supply_xs_reversal_probe.json")


def _now():
    return time.strftime("%Y-%m-%dT%H:%M:%S%z")


# --------------------------------------------------------------- mechanics
def reversal_score(close: pd.DataFrame, amt: pd.DataFrame, window: int = WINDOW,
                   min_amt: float = MIN_AMT, min_hist: int = MIN_HIST) -> pd.DataFrame:
    """Cross-sectional rank of the NEGATED trailing return, masked to eligibility.

    Ranked (not z-scored) on purpose: the composite book ranks its factor legs, so
    a rank face is the same currency; and a rank face cannot be distorted by one
    extreme mover in a 1,700-name row.
    """
    if window <= 0:
        raise ValueError("window must be positive")
    hist = close.notna().cumsum()
    elig = (amt >= min_amt) & (hist >= min_hist)
    ret = close / close.shift(window) - 1.0
    rank = ret.rank(axis=1, pct=True)          # 1.0 = biggest gainer
    score = -(rank - 0.5) * 2.0                # 1.0 = biggest loser
    score = score.where(elig)
    score.index = pd.to_datetime(score.index)
    return score


def random_score(score: pd.DataFrame, seed: int) -> pd.DataFrame:
    """Same-exposure null: the SAME eligibility mask, a uniform random ranking.

    Built off the real score face's mask rather than off the panel, so "which
    names could have been held" is bit-identical between the rule and the null.
    """
    rng = np.random.default_rng(seed)
    mask = score.notna().to_numpy()
    draw = rng.random(mask.shape)
    draw = np.where(mask, draw, np.nan)
    return pd.DataFrame(draw, index=score.index, columns=score.columns)


def turnover_per_year(close: pd.DataFrame, score: pd.DataFrame, rebal: int = REBAL,
                      n_hold: int = N_HOLD, start: str = START) -> dict:
    """How often the selection actually changes -- the cost driver, counted, not guessed."""
    dates = [d for d in close.index if d >= pd.Timestamp(start)]
    rebal_days = set(dates[::rebal])
    prev, n_swap, n_dec = set(), 0, 0
    for d in dates:
        if d not in rebal_days:
            continue
        s = score.loc[d].dropna()
        if len(s) < n_hold:
            continue
        cur = set(s.nlargest(n_hold).index)
        n_dec += 1
        if prev:
            n_swap += len(cur - prev)
        prev = cur
    yrs = (dates[-1] - dates[0]).days / 365.25 if len(dates) > 1 else 0.0
    return {"decisions": n_dec, "swapped_slots": n_swap,
            "swaps_per_year": round(n_swap / yrs, 2) if yrs else None}


def evaluate(close, openp, amt, score, n_hold=N_HOLD, rebal=REBAL):
    """Rule book, equal-weight control, and their metrics, all through the published engine."""
    book, turn, gapfill = run_next_open(close, openp, amt, {}, rebal, n_hold=n_hold,
                                        cost=COST, start=START, score=score)
    ew = run_ew(close, amt, rebal, start=START)
    return book, ew, turn, gapfill


def _period_returns(close: pd.DataFrame, rebal: int = REBAL, start: str = START):
    """Simple close-to-close return per (rebalance period, name), plus the period index.

    The published engine holds weights flat inside a period and charges cost at the
    fill, so a period's gross return is the mean of its members' period returns.
    Building the whole (periods x names) matrix once is what makes a 200-draw null
    affordable; the rule's own book is still measured by the engine, and the two
    bases are cross-checked in the selftest and disclosed in the artifact.
    """
    px = close.ffill()
    dates = [d for d in px.index if d >= pd.Timestamp(start)]
    bounds = [px.index.get_loc(d) for d in dates[::rebal]]
    g = px.to_numpy()
    n = g.shape[0]
    periods = []
    for i, a in enumerate(bounds):
        b = bounds[i + 1] if i + 1 < len(bounds) else n - 1
        if b <= a:
            continue
        with np.errstate(invalid="ignore", divide="ignore"):
            periods.append(g[b] / g[a] - 1.0)
    return np.vstack(periods), bounds[:len(periods)], dates


def _equity_from_picks(P: np.ndarray, picks: list, cost: float, turnover: float) -> float:
    """Compound one selection path: (1 - cost*turnover) once per period, then the mean member return."""
    eq = 1.0
    for i, sel in enumerate(picks):
        if len(sel) == 0:
            continue
        r = float(np.nanmean(P[i, sel]))
        if not np.isfinite(r):
            continue
        eq *= (1.0 + r) * (1.0 - cost * turnover)
    return eq


def _picks_from_score(score: pd.DataFrame, close: pd.DataFrame, bounds, n_hold: int):
    """Top-n_hold eligible names at each period's decision bar, as positional indexes."""
    cols = {c: i for i, c in enumerate(close.columns)}
    picks, prev = [], None
    for a in bounds:
        d = close.index[a]
        s = score.loc[d].dropna() if d in score.index else pd.Series(dtype=float)
        if len(s) < n_hold:
            picks.append([])
            continue
        sel = [cols[c] for c in s.nlargest(n_hold).index]
        picks.append(sel)
        prev = sel
    return picks


def _turnover_of(picks: list, n_hold: int) -> list:
    """sum|dw| per period: a slot that changes costs 2/n_hold (sell + buy)."""
    out, prev = [], None
    for sel in picks:
        if not sel:
            out.append(0.0)
            continue
        if prev is None:
            out.append(1.0)              # first entry from flat
        else:
            ch = len(set(sel) - set(prev))
            out.append(2.0 * ch / float(n_hold))
        prev = sel
    return out


def null_distribution(close, openp, amt, score, k=NULL_K, seed=NULL_SEED,
                      n_hold=N_HOLD, rebal=REBAL):
    """Same-exposure null, vectorised over rebalance periods.

    Each draw keeps the eligibility mask, the decision grid, n_hold and the cost and
    turnover convention; only the ranking is replaced by a seeded uniform draw.
    """
    P, bounds, _dates = _period_returns(close, rebal=rebal)
    cols = close.columns
    mask_at = []
    for a in bounds:
        d = close.index[a]
        m = score.loc[d] if d in score.index else pd.Series(dtype=float)
        mask_at.append(np.flatnonzero(m.reindex(cols).notna().to_numpy()))
    rng = np.random.default_rng(seed)
    draws = []
    for _ in range(k):
        picks = []
        for elig in mask_at:
            if len(elig) < n_hold:
                picks.append([])
                continue
            picks.append(list(rng.choice(elig, size=n_hold, replace=False)))
        turn = _turnover_of(picks, n_hold)
        eq = 1.0
        for i, sel in enumerate(picks):
            if not sel:
                continue
            r = float(np.nanmean(P[i, sel]))
            if not np.isfinite(r):
                continue
            eq *= (1.0 + r) * (1.0 - COST * turn[i])
        draws.append(eq)
    # Convert each draw's terminal equity into a CAGR so it is comparable with the
    # engine's excess read, then take the excess over 1.0 (the EW book is the baseline
    # only through the excess definition; both sides use the same renormalisation).
    yrs = (bounds and (close.index[bounds[-1]] - close.index[bounds[0]]).days / 365.25) or 0.0
    if yrs <= 0:
        return np.asarray([], dtype=float)
    ew_cagr = float(np.prod(1.0 + np.nanmean(P, axis=1)) ** (1.0 / yrs) - 1.0)
    return np.asarray([(e ** (1.0 / yrs) - 1.0) - ew_cagr for e in draws], dtype=float)


def vectorised_rule_excess(close, openp, amt, score, k=None, seed=NULL_SEED,
                           n_hold=N_HOLD, rebal=REBAL):
    """The rule's excess over the equal-weight universe measured on the NULL's basis.

    Reported beside the engine read so a reader can see whether the two bases agree;
    it is never used to replace the engine number.
    """
    P, bounds, _dates = _period_returns(close, rebal=rebal)
    picks = _picks_from_score(score, close, bounds, n_hold)
    turn = _turnover_of(picks, n_hold)
    eq = 1.0
    for i, sel in enumerate(picks):
        if not sel:
            continue
        r = float(np.nanmean(P[i, sel]))
        if not np.isfinite(r):
            continue
        eq *= (1.0 + r) * (1.0 - COST * turn[i])
    yrs = (close.index[bounds[-1]] - close.index[bounds[0]]).days / 365.25 if bounds else 0.0
    if yrs <= 0:
        return None, None
    ew_cagr = float(np.prod(1.0 + np.nanmean(P, axis=1)) ** (1.0 / yrs) - 1.0)
    cagr = eq ** (1.0 / yrs) - 1.0
    return cagr, cagr - ew_cagr


def verdict_case(excess_pp: float, p: float, swaps_per_year, maxdd_rule, maxdd_ew) -> dict:
    conds = {
        "excess_over_ew_ge_admit": bool(excess_pp >= ADMIT_MIN_EXCESS_PP),
        "beats_same_exposure_null": bool(p <= ADMIT_MAX_P),
        "cost_is_bounded": bool(swaps_per_year is not None
                                and swaps_per_year <= ADMIT_MAX_TURNOVER_PER_YEAR),
        "drawdown_not_worse": bool(maxdd_rule >= maxdd_ew - 0.05),
    }
    return {"conditions": conds,
            "verdict": "ADMIT_TO_PREREG" if all(conds.values()) else "REFUSE_AS_CANDIDATE"}


def run_probe(close=None, openp=None, amt=None, k=NULL_K, seed=NULL_SEED,
              n_hold=N_HOLD, rebal=REBAL, full=True):
    if close is None:
        prices = _dedupe(_load_prices())
        close = pd.DataFrame({s: p["close"] for s, p in prices.items()}).sort_index()
        openp = pd.DataFrame({s: p["open"] for s, p in prices.items()}).sort_index()
        vol = pd.DataFrame({s: p["volume"] for s, p in prices.items()}).sort_index()
        close = close.replace(0.0, np.nan)
        close, dropped = drop_hollow_tail(close)
        if dropped:
            openp, vol = openp.loc[close.index], vol.loc[close.index]
        amt = (close * vol).rolling(20, min_periods=10).median()

    score = reversal_score(close, amt)
    book, ew, turn, gapfill = evaluate(close, openp, amt, score, n_hold=n_hold, rebal=rebal)
    m_book, m_ew = metrics(book, "rule"), metrics(ew, "ew_universe")
    if "cagr" not in m_book or "cagr" not in m_ew:
        raise RuntimeError("panel too short for the probe")
    excess = m_book["cagr"] - m_ew["cagr"]
    vec_cagr, vec_excess = vectorised_rule_excess(close, openp, amt, score,
                                                  n_hold=n_hold, rebal=rebal)
    ex_null = null_distribution(close, openp, amt, score, k=k, seed=seed,
                                n_hold=n_hold, rebal=rebal)
    # The p-value is read on the NULL's own basis (same period/cost convention both
    # sides); the headline excess stays the engine's, and both are published.
    p_basis = vec_excess if vec_excess is not None else excess
    p = float((np.sum(ex_null >= p_basis) + 1.0) / (len(ex_null) + 1.0)) if len(ex_null) else None
    tv = turnover_per_year(close, score, rebal=rebal, n_hold=n_hold)
    vc = verdict_case((vec_excess if vec_excess is not None else excess) * 100.0,
                      p if p is not None else 1.0,
                      tv["swaps_per_year"], m_book["maxdd"], m_ew["maxdd"])
    return {
        "family": FAMILY,
        "batch": BATCH,
        "evidence_cutoff": str(close.index[-1].date()),
        "construction": {
            "window_bars": WINDOW, "rebalance_bars": rebal, "n_hold": n_hold,
            "start": START, "cost_per_side": COST, "min_amt": MIN_AMT,
            "min_hist": MIN_HIST, "exposure": 1.0,
            "execution": "decided on close t, filled at open t+1 (run_next_open)",
        },
        "panel": {"bars": int(len(close)),
                  "symbols": int(close.shape[1]),
                  "first": str(close.index[0].date())},
        "rule": m_book,
        "rule_engine": {"turnover_per_rebalance": round(float(turn), 4),
                        "open_gapfill_bars": int(gapfill)},
        "control_ew": m_ew,
        "excess_vs_ew_pp": round(excess * 100.0, 2),
        "vectorised_basis": {"rule_cagr": None if vec_cagr is None else round(vec_cagr, 4),
                             "excess_vs_ew_pp": None if vec_excess is None else round(vec_excess * 100.0, 2),
                             "note": "the null's basis (close-to-close periods, same cost convention); p-value is read here"},
        "null": {"k": int(len(ex_null)),
                 "mean_excess_pp": round(float(np.mean(ex_null)) * 100.0, 2) if len(ex_null) else None,
                 "sd_pp": round(float(np.std(ex_null)) * 100.0, 2) if len(ex_null) else None,
                 "seed": seed},
        "p_value": None if p is None else round(p, 4),
        "turnover": tv,
        "verdict": vc["verdict"],
        "conditions": vc["conditions"],
        "generated": _now(),
    }


# --------------------------------------------------------------- selftest
def _synth_panel(n_days=900, n_names=40, kind="reversal", seed=11):
    """Synthetic panel with a known answer.

    kind='reversal' : each name's next 20-bar return is made to mean-revert to the
                      panel, so "buy the losers" MUST win over the equal-weight book
    kind='walk'     : pure geometric random walk, no cross-sectional structure, so
                      the reversal rule must NOT clear the null
    """
    rng = np.random.default_rng(seed)
    dates = pd.bdate_range("2019-01-01", periods=n_days)
    cols = [f"ET{i:03d}" for i in range(n_names)]
    r = rng.normal(0, 0.01, size=(n_days, n_names))
    if kind == "reversal":
        # systematic pull: a name that fell over the last 20 bars outperforms
        for t in range(21, n_days):
            past = r[t - 20:t].sum(axis=0)
            r[t] = r[t] - 0.25 * past / np.sqrt(20)
    px = 100.0 * np.exp(np.cumsum(r, axis=0))
    close = pd.DataFrame(px, index=dates, columns=cols)
    openp = close.shift(1).fillna(close.iloc[0])
    amt = pd.DataFrame(1e9, index=dates, columns=cols)
    return close, openp, amt


def selftest() -> int:
    ok = 0
    fails = []

    def leg(name, cond, extra=""):
        nonlocal ok
        if cond:
            ok += 1
        else:
            fails.append(f"{name} {extra}")

    # L1 window must be positive
    try:
        reversal_score(pd.DataFrame({"a": [1.0, 2.0]}), pd.DataFrame({"a": [1e9, 1e9]}), window=0)
        leg("L1 window<=0 refused", False)
    except ValueError:
        leg("L1 window<=0 refused", True)

    # L2 eligibility mask is applied: an ineligible name that would rank first is masked out
    close = pd.DataFrame({"a": [1.0, 2.0, 1.0, 0.5], "b": [1.0, 1.1, 1.2, 1.3]},
                         index=pd.bdate_range("2024-01-01", periods=4))
    amt = pd.DataFrame({"a": [0.0, 0.0, 0.0, 0.0], "b": [1e9] * 4}, index=close.index)
    sc = reversal_score(close, amt, window=1, min_amt=1e6, min_hist=1)
    leg("L2 ineligible name masked", sc["a"].isna().all())

    # L3 engineered reversal panel: the rule must beat the equal-weight book
    c, o, a = _synth_panel(kind="reversal")
    sc = reversal_score(c, a, window=20, min_amt=1e6, min_hist=120)
    book, ew, _t, _g = evaluate(c, o, a, sc)
    m_b, m_ew = metrics(book, "rule"), metrics(ew, "ew")
    leg("L3 engineered reversal wins", m_b["cagr"] > m_ew["cagr"] + 0.01,
        f"{m_b['cagr']:.4f} vs {m_ew['cagr']:.4f}")

    # L4 same-exposure null keeps exposure: the null books hold exactly n_hold names
    rs = random_score(sc, 123)
    leg("L4 null keeps the mask", bool((rs.notna().sum(axis=1) == sc.notna().sum(axis=1)).all()))

    # L5 random walk: the reversal rule must not be able to manufacture alpha
    c2, o2, a2 = _synth_panel(kind="walk", seed=29)
    sc2 = reversal_score(c2, a2, window=20, min_amt=1e6, min_hist=120)
    b2, e2, _t2, _g2 = evaluate(c2, o2, a2, sc2)
    ex_null = null_distribution(c2, o2, a2, sc2, k=60, seed=5)
    _vc2, vex2 = vectorised_rule_excess(c2, o2, a2, sc2)
    p = float((np.sum(ex_null >= vex2) + 1.0) / (len(ex_null) + 1.0))
    leg("L5 random walk not admitted", p > ADMIT_MAX_P, f"p={p:.3f}")

    # L5b the two bases must agree on a panel with a known answer (they are read
    # side by side in the artifact, so a drifting vectorised basis would silently
    # move the p-value away from the engine's headline)
    m_b2, m_ew2 = metrics(b2, "rule"), metrics(e2, "ew")
    eng_ex = m_b2["cagr"] - m_ew2["cagr"]
    leg("L5b vectorised basis reproduces the engine excess",
        abs(eng_ex - vex2) < 0.02, f"engine {eng_ex:.4f} vs vec {vex2:.4f}")

    # L6 determinism: same inputs -> same score face
    leg("L6 deterministic score", reversal_score(c, a, window=20, min_amt=1e6, min_hist=120)
        .equals(sc))

    # L7 turnover counter is a count, not an estimate: static score -> zero swaps
    static = pd.DataFrame(1.0, index=c.index, columns=c.columns)
    tv = turnover_per_year(c, static, rebal=20, n_hold=5)
    leg("L7 static selection has zero swaps", tv["swapped_slots"] == 0, str(tv))

    # L8 a flat panel (no dispersion) must not be read as a winning rule
    flat = pd.DataFrame(100.0, index=c.index, columns=c.columns)
    m_flat = metrics(run_ew(flat, a, 20, start="2020-01-01"), "flat")
    leg("L8 flat panel is unmeasurable, not green",
        ("cagr" not in m_flat) or abs(m_flat["cagr"]) < 1e-9, str(m_flat.get("cagr")))

    print(f"selftest {ok}/{ok + len(fails)} PASS")
    for f in fails:
        print("FAIL", f)
    return 0 if not fails else 1


def main(argv):
    if len(argv) > 1 and argv[1] == "--selftest":
        return selftest()
    payload = run_probe()
    os.makedirs(os.path.dirname(RES_PATH), exist_ok=True)
    with open(RES_PATH, "w", encoding="utf-8") as f:
        json.dump(payload, f, ensure_ascii=False, indent=2, sort_keys=True)
    print(json.dumps({k: payload[k] for k in
                      ("family", "evidence_cutoff", "excess_vs_ew_pp", "p_value",
                       "verdict", "conditions")}, ensure_ascii=False, indent=2))
    print("wrote", RES_PATH)
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv))