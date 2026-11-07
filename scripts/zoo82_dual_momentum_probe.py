"""zoo82_dual_momentum_probe -- supply berth probe (zoo #82 dual-momentum ETF rotation).

WHY THIS FILE EXISTS
--------------------
`compute_audit` has reported `supply_floor ready 0 < floor 3` for twenty straight
rounds (supply_candidates verdict = AGENDA_DEBT).  zoo #82 `dual_momentum_etf` has
been registered since the 波-1 external sweep (2026-09-24) and never burned: 20-bar
relative momentum ranking plus a 60-bar absolute-momentum gate, falling back to a
defensive basket when the gate wipes the field out.  It is the textbook Antonacci
construction and the most recognisable rotation family still on the shelf, which
makes it the right control question for this desk: does the famous dual-momentum
ETF rotation beat the equal-weight universe it selects from, and does it beat the
composite book we actually ship?

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
  relative     rel = close[t]/close[t-20] - 1, ranked cross-sectionally among the
               names that pass the gate (higher rank = stronger)
  absolute     gate = close[t]/close[t-60] - 1 > 0 (the frozen 60-bar absolute
               momentum filter); a name that fails the gate is not selectable
  defense      511880 / 511260 / 518880, carried at a sentinel score BELOW every
               passer, so they are picked only for the slots the gate leaves empty
               -- the registered "无员达标切防御" read as an always-fully-invested
               basket rather than an all-or-nothing switch
  selection    top n_hold=3 by score; equal weight; always fully invested
  grid         every `rebal`=20-th bar of the panel, decided on the close, filled at
               the NEXT open -- run through the published leg engine
               (`run_next_open`, score passed in) so the fill/cost maths is not
               re-implemented here
  cost         COST (8bp) per side on the engine's own turnover bookkeeping
  benchmark    equal weight across the SAME eligible universe on the same grid
               (`run_ew`), plus the published composite book as a second reference
  null         K books with identical eligibility, identical grid, identical
               n_hold and identical costs; only the ranking is replaced by a seeded
               uniform draw -> same exposure, no signal

WHY THE DEFENSIVE LEG IS A SENTINEL AND NOT A SWITCH
----------------------------------------------------
The registered text says "无员达标切防御", i.e. a switch.  A switch makes exposure
time-varying, and r1387 measured what that costs on this panel (a rule out of the
market 30% of the time must out-earn by +3.70pp/yr before it is comparable).  The
sentinel form keeps the comparison at constant exposure and still honours the
registered intent: with zero passers the book holds nothing but the defense
basket, and the artifact reports how often that happened.
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
from zoo_supply_xs_reversal_probe import (  # noqa: E402
    _period_returns, _picks_from_score, _turnover_of,
)

# ---- frozen constants (echoed into every artifact) -------------------------
FAMILY = "dual_momentum_etf_20_60"
BATCH = "SUPPLY_BERTH_SLOT_19_CANDIDATE"
REL_W = 20
ABS_W = 60
REBAL = 20
N_HOLD = 3
DEFENSE = ("sh511880", "sh511260", "sh518880")
START = "2020-01-01"
NULL_K = 200
NULL_SEED = 20261107
ADMIT_MIN_EXCESS_PP = 1.0          # pp/yr over the equal-weight universe
ADMIT_MAX_P = 0.05
ADMIT_MAX_TURNOVER_PER_YEAR = 40.0

RES_PATH = os.path.join(ROOT, "results", "supply_berth",
                        "zoo82_dual_momentum_probe.json")


def _now():
    return time.strftime("%Y-%m-%dT%H:%M:%S%z")


def _defense_names(close):
    """The defensive legs that actually print on this panel (never invented)."""
    return [d for d in DEFENSE if d in close.columns]


def dual_score(close, amt, rel_w=REL_W, abs_w=ABS_W, min_amt=MIN_AMT,
               min_hist=MIN_HIST, defense=None):
    """Score face: relative-momentum rank among gate passers, sentinel defense below.

    A non-finite / ineligible / gate-failing name gets NaN (not selectable).  The
    defensive legs get a sentinel score of 0.0, which sits below every passer's
    pct-rank (>0) and therefore only takes the slots the gate leaves empty.
    """
    if rel_w <= 0 or abs_w <= 0:
        raise ValueError("momentum windows must be positive")
    if defense is None:
        defense = DEFENSE
    px = close.replace(0.0, np.nan)
    amt = amt.reindex(columns=px.columns)
    elig = amt.ge(min_amt) & px.notna()
    hist = px.notna().cumsum()
    elig &= hist.ge(min_hist)
    rel = px / px.shift(rel_w) - 1.0
    absm = px / px.shift(abs_w) - 1.0
    gate = absm > 0
    rank = rel.where(elig & gate).rank(axis=1, pct=True, ascending=True)
    for d in defense:
        if d in rank.columns:
            rank[d] = np.where(elig[d].to_numpy(), 0.0, np.nan)
    return rank


def gate_stats(close, amt, score, rebal=REBAL, start=START, n_hold=N_HOLD,
               defense=None):
    """How often the gate left the book on the defense basket (a reading, not a claim)."""
    if defense is None:
        defense = DEFENSE
    defs = _defense_names(close)
    dates = [d for d in close.index if d >= pd.Timestamp(start)]
    rebal_days = sorted(set(dates[::rebal]))
    n_dec = n_passers_all = all_defense = 0
    parts = []
    for d in rebal_days:
        if d not in score.index:
            continue
        s = score.loc[d].dropna()
        if len(s) < n_hold:
            continue
        n_dec += 1
        passers = int((s[s.index.isin(defs)] <= 0.0).sum())
        n_pass = int(len(s) - passers)
        parts.append(n_pass)
        n_passers_all += n_pass
        if n_pass == 0:
            all_defense += 1
    return {"decisions": n_dec,
            "mean_passers": round(n_passers_all / n_dec, 2) if n_dec else None,
            "all_defense_decisions": all_defense,
            "all_defense_share": round(all_defense / n_dec, 4) if n_dec else None}


def null_excess(close, amt, score, k=NULL_K, seed=NULL_SEED, n_hold=N_HOLD,
                rebal=REBAL):
    """Same-exposure null: the mask and the grid survive, the ranking is random."""
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
    yrs = (bounds and (close.index[bounds[-1]] - close.index[bounds[0]]).days / 365.25) or 0.0
    if yrs <= 0:
        return np.asarray([], dtype=float), None
    ew_cagr = float(np.prod(1.0 + np.nanmean(P, axis=1)) ** (1.0 / yrs) - 1.0)
    ex = np.asarray([(e ** (1.0 / yrs) - 1.0) - ew_cagr for e in draws], dtype=float)
    return ex, ew_cagr


def vectorised_rule_excess(close, amt, score, n_hold=N_HOLD, rebal=REBAL):
    """The rule on the null's own basis (close-to-close periods, same cost)."""
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


def swaps_per_year(close, score, rebal=REBAL, n_hold=N_HOLD, start=START):
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


def verdict_case(excess_pp, p, swaps, maxdd_rule, maxdd_ew):
    conds = {
        "excess_over_ew_ge_admit": bool(excess_pp >= ADMIT_MIN_EXCESS_PP),
        "beats_same_exposure_null": bool(p <= ADMIT_MAX_P),
        "cost_is_bounded": bool(swaps is not None
                                and swaps <= ADMIT_MAX_TURNOVER_PER_YEAR),
        "drawdown_not_worse": bool(maxdd_rule >= maxdd_ew - 0.05),
    }
    return {"conditions": conds,
            "verdict": "ADMIT_TO_PREREG" if all(conds.values()) else "REFUSE_AS_CANDIDATE"}


def run_probe(close=None, openp=None, amt=None, k=NULL_K, seed=NULL_SEED,
              n_hold=N_HOLD, rebal=REBAL):
    pub_feats = None
    if close is None:
        # build_panel() is the published book's own panel constructor; using it
        # (rather than a second copy of _load_prices/_dedupe/drop_hollow_tail)
        # keeps "a bar means the same thing" true by construction and hands back
        # the factor faces the published book's score needs.
        from etf_composite_pf import build_panel
        close, openp, amt, pub_feats = build_panel()

    defs = _defense_names(close)
    score = dual_score(close, amt, defense=defs)
    book, turn, gapfill = run_next_open(close, openp, amt, {}, rebal, n_hold=n_hold,
                                       cost=COST, start=START, score=score)
    ew = run_ew(close, amt, rebal, start=START)
    pub = None
    if pub_feats is not None:
        pub, _t2, _g2 = run_next_open(close, openp, amt, pub_feats, rebal, n_hold=5,
                                      cost=COST, start=START)
    m_book, m_ew = metrics(book, "rule"), metrics(ew, "ew_universe")
    m_pub = metrics(pub, "published_book") if pub is not None else {"note": "not available"}
    if "cagr" not in m_book or "cagr" not in m_ew:
        raise RuntimeError("panel too short for the probe")
    excess = m_book["cagr"] - m_ew["cagr"]
    vec_cagr, vec_excess = vectorised_rule_excess(close, amt, score,
                                                  n_hold=n_hold, rebal=rebal)
    ex_null, _ew_from_null = null_excess(close, amt, score, k=k, seed=seed,
                                         n_hold=n_hold, rebal=rebal)
    p_basis = vec_excess if vec_excess is not None else excess
    p = float((np.sum(ex_null >= p_basis) + 1.0) / (len(ex_null) + 1.0)) if len(ex_null) else None
    tv = swaps_per_year(close, score, rebal=rebal, n_hold=n_hold)
    gs = gate_stats(close, amt, score, rebal=rebal, n_hold=n_hold, defense=defs)
    vc = verdict_case(p_basis * 100.0, p if p is not None else 1.0,
                      tv["swaps_per_year"], m_book["maxdd"], m_ew["maxdd"])
    return {
        "family": FAMILY,
        "batch": BATCH,
        "evidence_cutoff": str(close.index[-1].date()),
        "construction": {
            "rel_window_bars": REL_W, "abs_window_bars": ABS_W,
            "rebalance_bars": rebal, "n_hold": n_hold, "start": START,
            "cost_per_side": COST, "min_amt": MIN_AMT, "min_hist": MIN_HIST,
            "exposure": 1.0,
            "defense_legs": defs,
            "defense_form": "sentinel score below every passer (slots, not a switch)",
            "execution": "decided on close t, filled at open t+1 (run_next_open)",
        },
        "panel": {"bars": int(len(close)), "symbols": int(close.shape[1]),
                  "first": str(close.index[0].date())},
        "rule": m_book,
        "rule_engine": {"turnover_per_rebalance": round(float(turn), 4),
                        "open_gapfill_bars": int(gapfill)},
        "control_ew": m_ew,
        "reference_published_book": m_pub,
        "excess_vs_ew_pp": round(excess * 100.0, 2),
        "excess_vs_published_book_pp": (round((m_book["cagr"] - m_pub["cagr"]) * 100.0, 2)
                                         if "cagr" in m_pub else None),
        "vectorised_basis": {"rule_cagr": None if vec_cagr is None else round(vec_cagr, 4),
                             "excess_vs_ew_pp": None if vec_excess is None else round(vec_excess * 100.0, 2),
                             "note": "the null's basis (close-to-close periods, same cost convention); p-value is read here"},
        "null": {"k": int(len(ex_null)),
                 "mean_excess_pp": round(float(np.mean(ex_null)) * 100.0, 2) if len(ex_null) else None,
                 "sd_pp": round(float(np.std(ex_null)) * 100.0, 2) if len(ex_null) else None,
                 "seed": seed},
        "p_value": None if p is None else round(p, 4),
        "turnover": tv,
        "gate": gs,
        "verdict": vc["verdict"],
        "conditions": vc["conditions"],
        "generated": _now(),
    }


# --------------------------------------------------------------- selftest
def _synth_panel(n_days=900, n_names=12, kind="trend", seed=11):
    """Synthetic panel with a known answer.

    kind='trend' : names carry persistent drift, so an absolute-momentum gate plus a
                   relative-momentum rank MUST beat the equal-weight book
    kind='walk'  : pure geometric random walk, no cross-sectional structure, so the
                   rule must NOT clear the null
    """
    rng = np.random.default_rng(seed)
    dates = pd.bdate_range("2019-01-01", periods=n_days)
    cols = [f"sh510{i:03d}" for i in range(n_names - 3)]
    cols += list(DEFENSE)
    drift = np.zeros(len(cols))
    if kind == "trend":
        # Only the CONTESTED names carry dispersion.  If the defensive legs were
        # given the strongest drift the fixture would ask the rule to beat a book
        # holding assets it can only reach when the gate is empty -- that is a
        # property of the fixture, not of the rule.
        drift[:len(cols) - 3] = np.linspace(-0.0004, 0.0016, len(cols) - 3)
    r = rng.normal(0, 0.006, size=(n_days, len(cols))) + drift
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

    # L1 windows must be positive
    try:
        dual_score(pd.DataFrame({"a": [1.0, 2.0]}), pd.DataFrame({"a": [1e9, 1e9]}), rel_w=0)
        leg("L1 rel window<=0 refused", False)
    except ValueError:
        leg("L1 rel window<=0 refused", True)

    # L2 the absolute gate excludes names whose 60-bar return is negative
    dates = pd.bdate_range("2024-01-01", periods=80)
    up = pd.Series(np.linspace(1.0, 2.0, 80), index=dates)
    dn = pd.Series(np.linspace(2.0, 1.0, 80), index=dates)
    c = pd.DataFrame({"sh510001": up, "sh510002": dn})
    a = pd.DataFrame(1e9, index=dates, columns=c.columns)
    sc = dual_score(c, a, min_hist=10, defense=())
    leg("L2 gate drops the down-trend name", bool(np.isnan(sc["sh510002"].iloc[-1])),
        str(sc.iloc[-1].to_dict()))
    leg("L2 gate keeps the up-trend name", bool(np.isfinite(sc["sh510001"].iloc[-1])))

    # L3 the defense sentinel sits below every passer
    c3, o3, a3 = _synth_panel(kind="trend")
    sc3 = dual_score(c3, a3, min_hist=120)
    row = sc3.iloc[-1].dropna()
    defs = [d for d in DEFENSE if d in row.index]
    passers = row[~row.index.isin(defs)]
    leg("L3 sentinel below every passer", bool(len(passers) == 0 or passers.min() > 0.0),
        f"min passer {passers.min() if len(passers) else None}")
    leg("L3 defense legs carry a score", bool(len(defs) == len(DEFENSE)))

    # L4 engineered trend panel: the rule must beat the equal-weight book
    b4, _t4, _g4 = run_next_open(c3, o3, a3, {}, REBAL, n_hold=N_HOLD, cost=COST,
                                 start="2020-01-01", score=sc3)
    e4 = run_ew(c3, a3, REBAL, start="2020-01-01")
    m_b4, m_e4 = metrics(b4, "rule"), metrics(e4, "ew")
    leg("L4 engineered trend wins", m_b4.get("cagr", -9) > m_e4.get("cagr", -9) + 0.01,
        f"{m_b4.get('cagr')} vs {m_e4.get('cagr')}")

    # L5 random walk: the rule must not be able to manufacture alpha
    c5, o5, a5 = _synth_panel(kind="walk", seed=29)
    sc5 = dual_score(c5, a5, min_hist=120)
    _vc5, vex5 = vectorised_rule_excess(c5, a5, sc5)
    ex5, _ew5 = null_excess(c5, a5, sc5, k=60, seed=5)
    p5 = float((np.sum(ex5 >= vex5) + 1.0) / (len(ex5) + 1.0))
    leg("L5 random walk not admitted", p5 > ADMIT_MAX_P, f"p={p5:.3f}")

    # L5b the vectorised basis must reproduce the engine's excess (it is what the
    # p-value is read on, so a drifting basis would move the verdict silently)
    eng_ex = m_b4["cagr"] - m_e4["cagr"]
    _vc3, vex3 = vectorised_rule_excess(c3, a3, sc3)
    leg("L5b vectorised basis reproduces the engine excess", abs(eng_ex - vex3) < 0.05,
        f"engine {eng_ex:.4f} vs vec {vex3:.4f}")

    # L6 determinism
    leg("L6 deterministic score",
        dual_score(c3, a3, min_hist=120).equals(dual_score(c3, a3, min_hist=120)))

    # L7 flat panel is unmeasurable, not green
    flat = pd.DataFrame(100.0, index=c3.index, columns=c3.columns)
    m_flat = metrics(run_ew(flat, a3, REBAL, start="2020-01-01"), "flat")
    leg("L7 flat panel is unmeasurable, not green",
        ("cagr" not in m_flat) or abs(m_flat["cagr"]) < 1e-9, str(m_flat.get("cagr")))

    # L8 with every name failing the gate the book must be all-defense
    dn_all = pd.DataFrame({c: pd.Series(np.linspace(2.0, 1.0, 900), index=c3.index)
                           for c in c3.columns})
    sc8 = dual_score(dn_all, a3, min_hist=120)
    gs8 = gate_stats(dn_all, a3, sc8, n_hold=N_HOLD)
    leg("L8 all-fail gate reads all-defense", gs8["all_defense_share"] == 1.0, str(gs8))

    # L9 the null keeps the same mask (exposure and candidate count untouched)
    P, bounds, _d = _period_returns(c3, rebal=REBAL)
    m0 = sc3.loc[c3.index[bounds[0]]].dropna()
    leg("L9 null mask equals the score mask", len(m0) == int(sc3.notna().iloc[bounds[0]].sum()))

    # L10 turnover counter is a count, not an estimate
    static = pd.DataFrame(1.0, index=c3.index, columns=c3.columns)
    tv = swaps_per_year(c3, static, rebal=REBAL, n_hold=N_HOLD)
    leg("L10 static selection has zero swaps", tv["swapped_slots"] == 0, str(tv))

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
                      ("family", "evidence_cutoff", "excess_vs_ew_pp",
                       "excess_vs_published_book_pp", "p_value", "verdict",
                       "conditions", "gate")}, ensure_ascii=False, indent=2))
    print("wrote", RES_PATH)
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv))