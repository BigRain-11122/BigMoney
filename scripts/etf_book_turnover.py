"""r1260 said the binding constraint on this ETF book is turnover, not concentration.

That finding came out of a capacity ladder (1M -> 500M) in which the trade cost was
priced by participation. This script attacks the stated bottleneck directly and
measures what two structural changes buy before any new signal work:

  (A) CADENCE. Does the book need to trade every 20 bars? The same score face is run
      at rebal 10 / 20 / 40 / 60 under two cost regimes -- the flat 8bp assumption
      every r1249-r1259 number used, and the participation-priced cost of r1260 at
      10M / 50M / 100M NAV. The question is not "which cadence wins" but "how much
      of the edge is a trading-frequency artefact".

  (B) STAGGER. Rebalancing eight names on one bar concentrates the whole month's
      impact into a single session. Splitting the same eight names into two
      four-name sleeves that rebalance half a period apart spreads it. The sleeves
      are built from the SAME ranked score face (ranks 1-4 and 5-8), so this is a
      phasing change, never a different selection.

What is reused, never rewritten:
  * selection / fills / leg maths = `F.run_next_open` (r1250 next-open basis);
  * the score face              = `F.build_score`;
  * the participation cost      = `ImpactCost` from scripts/etf_book_capacity.py
    (r1260) -- imported, never re-implemented, and its scalar path stays pinned by
    that script's own selftest;
  * controls                    = `F.run_ew` at the SAME cadence plus 510300.

Honest limits stated up front:
  * the blend of two sleeves assumes a daily rebalance between them (weights held
    50/50 by construction), which the single-sleeve book also implicitly assumes
    inside a holding period -- both are approximations, neither is a fill model;
  * a stagger does NOT reduce total turnover, only its concentration per session;
    turnover is reported for every line so that cannot be misread;
  * this is exploratory: no preregistration, no verdict, no ledger booking.

  python scripts/etf_book_turnover.py run [--out=...]
  python scripts/etf_book_turnover.py --selftest
"""
import argparse
import json
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import numpy as np
import pandas as pd

from config import PATHS
from scripts import etf_composite_pf as F
from scripts.etf_book_capacity import BASE_BP, IMPACT_BP_PER_PCT, ImpactCost

REBAL_GRID = (10, 20, 40, 60)
NAV_GRID = (1e7, 5e7, 1e8)
START = "2020-01-01"
BARS_PER_YEAR = 252.0
# Breadth the stagger face is graded at. The two sleeves partition ranks 1..STAGGER_TOP,
# so the single-sleeve reference must hold exactly STAGGER_TOP names as well -- anything
# else grades a breadth change as if it were a phasing change. The r1261 run compared a
# staggered 4+4 book against the engine default 5-name book (F.N_HOLD=5) and attributed
# the whole 8-vs-5 difference to staggering.
STAGGER_TOP = 8
SLEEVE_TOP = STAGGER_TOP // 2


def top_slice(score, lo, hi):
    """Score face restricted to the names ranked `lo`..`hi` (1-based, inclusive).

    Ranks are taken row-wise with method='first' so the split is deterministic when
    scores tie -- a stagger built on a non-deterministic split would silently migrate
    names between sleeves on every run.
    """
    r = score.rank(axis=1, ascending=False, method="first")
    return score.where((r >= lo) & (r <= hi))


def phase_start(index, start, offset):
    """The date `offset` trading bars after `start`, used to shift a sleeve's clock.

    `run_next_open` takes its rebalance grid from `dates[::rebal]`, i.e. it starts on
    whatever bar `start` lands on. Handing the second sleeve a later `start` is
    therefore exactly a phase shift -- no engine change is needed, which is the whole
    reason the stagger can be built without touching the fill maths.
    """
    dates = [d for d in index if d >= pd.Timestamp(start)]
    if offset < 0 or offset >= len(dates):
        return None
    return dates[offset]


def blend(sers):
    """Equal-weight daily blend of sleeve equity curves, renormalised per day.

    A sleeve that has not started yet contributes no weight rather than a zero return
    (df.notna() gates the weights), so the blend is honest during the burn-in of a
    phase-shifted sleeve instead of quietly halving the book.
    """
    df = pd.concat(sers, axis=1).sort_index()
    rets = df.pct_change()
    avail = df.notna() & rets.notna()
    w = avail.astype(float).div(avail.sum(axis=1).replace(0, np.nan), axis=0)
    port = (rets.fillna(0.0) * w.fillna(0.0)).sum(axis=1)
    curve = (1.0 + port).cumprod()
    curve.iloc[0] = 1.0
    return curve


def turns_per_year(turn_per_decision, rebal):
    return round(turn_per_decision * BARS_PER_YEAR / rebal, 4)


def _priced(close, openp, amt, feats, rebal, nav, score, n_hold=F.N_HOLD, start=START):
    """One book run under participation-priced cost; returns metrics + participation."""
    cm = ImpactCost(amt, nav)
    ser, turn, gap = F.run_next_open(close, openp, amt, feats, rebal, n_hold=n_hold,
                                     cost=cm, start=start, score=score)
    m = F.metrics(ser, "nav=%.0e rebal=%d" % (nav, rebal))
    pmax = pd.Series([r["participation_max"] for r in cm.rows
                      if r["participation_max"] is not None])
    m.update({
        "turnover_per_decision": round(turn, 4),
        "turns_per_year": turns_per_year(turn, rebal),
        "open_gapfill": gap,
        "missing_adv_legs": cm.missing_names,
        "participation_max_p50": round(float(pmax.median()), 6) if len(pmax) else None,
        "participation_max_p90": round(float(pmax.quantile(0.9)), 6) if len(pmax) else None,
        "decisions_over_1pct": int((pmax > 0.01).sum()) if len(pmax) else 0,
    })
    return m, ser, cm


def run(start=START):
    close, openp, amt, feats = F.build_panel()
    score = F.build_score(close, amt, feats)
    mkt = F.bench_series(close, start)
    mkt_m = F.metrics(mkt, "510300") if mkt is not None else None

    # ---- (A) cadence ladder -------------------------------------------------
    ladder = []
    for rebal in REBAL_GRID:
        print("[ladder] rebal=%d" % rebal, flush=True)
        ew = F.metrics(F.run_ew(close, amt, rebal, start=start), "ew rebal=%d" % rebal)
        ser_flat, turn_flat, gap_flat = F.run_next_open(
            close, openp, amt, feats, rebal, cost=F.COST, start=start, score=score)
        m_flat = F.metrics(ser_flat, "flat8 rebal=%d" % rebal)
        row = {
            "rebal": rebal,
            "flat_8bp": dict(m_flat, turnover_per_decision=round(turn_flat, 4),
                             turns_per_year=turns_per_year(turn_flat, rebal),
                             open_gapfill=gap_flat,
                             excess_vs_ew_pp=None if (m_flat.get("cagr") is None
                                                      or ew.get("cagr") is None) else
                             round(100.0 * (m_flat["cagr"] - ew["cagr"]), 3)),
            "pool_equal_weight": ew,
            "priced": {},
        }
        for nav in NAV_GRID:
            m, _, _ = _priced(close, openp, amt, feats, rebal, nav, score, start=start)
            m["excess_vs_ew_pp"] = (None if (m.get("cagr") is None or ew.get("cagr") is None)
                                    else round(100.0 * (m["cagr"] - ew["cagr"]), 3))
            row["priced"]["%.0e" % nav] = m
        ladder.append(row)

    # ---- (B) stagger -------------------------------------------------------
    # The same STAGGER_TOP-name selection, split into ranks 1..SLEEVE_TOP and
    # SLEEVE_TOP+1..STAGGER_TOP, the second sleeve phased half a period later. Each
    # sleeve carries half the capital. The single-sleeve reference holds STAGGER_TOP
    # names in one sleeve, so the only difference between the two lines is phasing.
    rebal = 20
    lo_a, hi_a = 1, SLEEVE_TOP
    lo_b, hi_b = SLEEVE_TOP + 1, STAGGER_TOP
    print("[stagger] sleeves ranks %d-%d / %d-%d" % (lo_a, hi_a, lo_b, hi_b), flush=True)
    ew20 = F.metrics(F.run_ew(close, amt, rebal, start=start), "ew rebal=20")

    ser_a = F.run_next_open(close, openp, amt, feats, rebal, n_hold=SLEEVE_TOP,
                            cost=F.COST, start=start, score=top_slice(score, lo_a, hi_a))[0]
    off = rebal // 2
    st_b = phase_start(close.index, start, off)
    ser_b, turn_b, _ = F.run_next_open(close, openp, amt, feats, rebal, n_hold=SLEEVE_TOP,
                                       cost=F.COST, start=st_b,
                                       score=top_slice(score, lo_b, hi_b))
    stagger_flat = blend([ser_a, ser_b])
    m_stag_flat = F.metrics(stagger_flat, "stagger flat8")

    # single-sleeve reference: same breadth, same cadence, same flat cost
    ser_single, turn_single, _ = F.run_next_open(
        close, openp, amt, feats, rebal, n_hold=STAGGER_TOP,
        cost=F.COST, start=start, score=score)
    m_single_flat = F.metrics(ser_single, "single flat8")

    stagger = {
        "rebal": rebal,
        "breadth": {"stagger_top": STAGGER_TOP, "sleeve_top": SLEEVE_TOP,
                    "sleeve_a_ranks": [lo_a, hi_a], "sleeve_b_ranks": [lo_b, hi_b],
                    "single_reference_n_hold": STAGGER_TOP},
        "phase_offset_bars": off,
        "sleeve_b_start": None if st_b is None else str(pd.Timestamp(st_b).date()),
        "single_flat_8bp": dict(m_single_flat,
                                turnover_per_decision=round(turn_single, 4),
                                turns_per_year=turns_per_year(turn_single, rebal),
                                excess_vs_ew_pp=round(100.0 * (m_single_flat["cagr"]
                                                               - ew20["cagr"]), 3)),
        "stagger_flat_8bp": dict(m_stag_flat,
                                 turnover_per_decision=round(0.5 * (turn_single + turn_b), 4),
                                 turns_per_year=turns_per_year(0.5 * (turn_single + turn_b), rebal),
                                 excess_vs_ew_pp=round(100.0 * (m_stag_flat["cagr"]
                                                                - ew20["cagr"]), 3)),
        "sleeve_turnover_per_decision": {"a": round(turn_single, 4), "b": round(turn_b, 4)},
        "priced": {},
    }
    for nav in NAV_GRID:
        # each sleeve carries nav/2, so its own participation is priced on half the NAV
        ca = ImpactCost(amt, nav * 0.5)
        sa, ta, _ = F.run_next_open(close, openp, amt, feats, rebal, n_hold=SLEEVE_TOP,
                                    cost=ca, start=start, score=top_slice(score, lo_a, hi_a))
        cb = ImpactCost(amt, nav * 0.5)
        sb, tb, _ = F.run_next_open(close, openp, amt, feats, rebal, n_hold=SLEEVE_TOP,
                                    cost=cb, start=st_b, score=top_slice(score, lo_b, hi_b))
        blended = blend([sa, sb])
        mb = F.metrics(blended, "stagger nav=%.0e" % nav)
        pmax = pd.Series([r["participation_max"] for r in (ca.rows + cb.rows)
                          if r["participation_max"] is not None])
        mb.update({
            "turnover_per_decision": round(0.5 * (ta + tb), 4),
            "turns_per_year": turns_per_year(0.5 * (ta + tb), rebal),
            "participation_max_p90": round(float(pmax.quantile(0.9)), 6) if len(pmax) else None,
            "decisions_over_1pct": int((pmax > 0.01).sum()) if len(pmax) else 0,
            "excess_vs_ew_pp": (None if mb.get("cagr") is None
                                else round(100.0 * (mb["cagr"] - ew20["cagr"]), 3)),
        })
        # the priced single reference must be breadth-matched too -- grading an 8-name
        # staggered book against the 5-name ladder would repeat the r1261 mistake at
        # a different NAV
        m1, _, cm1 = _priced(close, openp, amt, feats, rebal, nav, score,
                             n_hold=STAGGER_TOP, start=start)
        stagger["priced"]["%.0e" % nav] = {
            "single": m1,
            "stagger": mb,
            "delta_cagr_pp": (None if (m1.get("cagr") is None or mb.get("cagr") is None)
                              else round(100.0 * (mb["cagr"] - m1["cagr"]), 3)),
            "participation_p90_single": cm1 and round(float(pd.Series(
                [r["participation_max"] for r in cm1.rows
                 if r["participation_max"] is not None]).quantile(0.9)), 6),
            "participation_p90_stagger": mb.get("participation_max_p90"),
        }

    out = {
        "ts": pd.Timestamp.now().strftime("%Y-%m-%d %H:%M:%S"),
        "evidence_cutoff": str(pd.Timestamp(close.index[-1]).date()),
        "script": "scripts/etf_book_turnover.py",
        "config": {"rebal_grid": list(REBAL_GRID), "nav_grid": list(NAV_GRID),
                   "base_bp": BASE_BP, "impact_bp_per_pct": IMPACT_BP_PER_PCT,
                   "n_hold_ladder": F.N_HOLD, "stagger_top": STAGGER_TOP,
                   "sleeve_top": SLEEVE_TOP, "start": start},
        "corrections_disclosed": [
            "r1262: the r1261 stagger face graded a staggered %d-name book against the "
            "engine default %d-name single book (F.N_HOLD), so its '-X pp cost of "
            "staggering' and '+61%% capacity' figures mixed a breadth change into a "
            "phasing change. Both lines are now %d names wide."
            % (STAGGER_TOP, F.N_HOLD, STAGGER_TOP),
        ],
        "market_510300": mkt_m,
        "cadence_ladder": ladder,
        "stagger": stagger,
        "readings": _readings(ladder, stagger),
    }
    return out


def _readings(ladder, stagger):
    """A few derived sentences, computed from the rows themselves (never hand-typed)."""
    by = {r["rebal"]: r for r in ladder}
    out = {}
    base = by.get(20)
    if base and base["flat_8bp"].get("cagr") is not None:
        out["flat_cagr_by_cadence"] = {str(k): v["flat_8bp"]["cagr"] for k, v in sorted(by.items())}
        out["priced_10m_cagr_by_cadence"] = {
            str(k): (v["priced"].get("1e+07") or {}).get("cagr") for k, v in sorted(by.items())}
    s = stagger
    if s["single_flat_8bp"].get("cagr") is not None and s["stagger_flat_8bp"].get("cagr"):
        out["stagger_vs_single_flat_pp"] = round(
            100.0 * (s["stagger_flat_8bp"]["cagr"] - s["single_flat_8bp"]["cagr"]), 3)

    # Capacity is derived, never carried over. p = |dw| * NAV / ADV, so p is linear in
    # NAV and the NAV at which p90 participation reaches the 1%-ADV discipline is just
    # NAV_ref * 1% / p90(NAV_ref). Every line is computed from its own measured p90 so
    # a breadth or phasing change cannot inherit someone else's capacity figure.
    ref_nav = float(min(NAV_GRID))
    ref_key = "%.0e" % ref_nav
    cap = {"adv_discipline_pct": 1.0, "reference_nav": ref_nav}
    ladder20 = (by.get(20) or {}).get("priced", {}).get(ref_key) or {}
    if ladder20.get("participation_max_p90"):
        cap["book_%d_names" % F.N_HOLD] = round(
            ref_nav * (0.01 / ladder20["participation_max_p90"]))
    priced_st = (s.get("priced") or {}).get(ref_key) or {}
    if (priced_st.get("single") or {}).get("participation_max_p90"):
        cap["single_%d_names" % STAGGER_TOP] = round(
            ref_nav * (0.01 / priced_st["single"]["participation_max_p90"]))
    if (priced_st.get("stagger") or {}).get("participation_max_p90"):
        cap["staggered_%d_names" % STAGGER_TOP] = round(
            ref_nav * (0.01 / priced_st["stagger"]["participation_max_p90"]))
    if "book_%d_names" % F.N_HOLD in cap and "staggered_%d_names" % STAGGER_TOP in cap:
        base_cap = cap["book_%d_names" % F.N_HOLD]
        for k in ("single_%d_names" % STAGGER_TOP, "staggered_%d_names" % STAGGER_TOP):
            if k in cap:
                cap[k + "_vs_book_pct"] = round(100.0 * (cap[k] / base_cap - 1.0), 1)
    if ("single_%d_names" % STAGGER_TOP in cap
            and "staggered_%d_names" % STAGGER_TOP in cap):
        cap["stagger_vs_single_pct"] = round(
            100.0 * (cap["staggered_%d_names" % STAGGER_TOP]
                     / cap["single_%d_names" % STAGGER_TOP] - 1.0), 1)
    out["p90_capacity_nav"] = cap
    return out


def selftest():
    """Offline legs -- every one of them must pass before this script's numbers count."""
    fails = []
    ran = []

    def check(name, cond, detail=""):
        ran.append(name)
        if not cond:
            fails.append("%s %s" % (name, detail))

    # L1: phase_start is a pure bar-offset, not a calendar guess
    idx = pd.bdate_range("2020-01-01", periods=60)
    check("L1a", phase_start(idx, "2020-01-01", 0) == idx[0])
    check("L1b", phase_start(idx, "2020-01-01", 10) == idx[10])
    check("L1c", phase_start(idx, "2020-01-15", 0) == pd.Timestamp("2020-01-15"))
    check("L1d", phase_start(idx, "2020-01-01", 999) is None)

    # L2: the two sleeves partition the top 8 exactly -- no name in both, none lost
    cols = ["s%02d" % i for i in range(12)]
    rows = pd.bdate_range("2021-01-01", periods=6)
    rng = np.random.RandomState(7)
    sc = pd.DataFrame(rng.rand(6, 12), index=rows, columns=cols)
    a = top_slice(sc, 1, 4)
    b = top_slice(sc, 5, 8)
    both = (a.notna() & b.notna()).sum().sum()
    check("L2a", both == 0, "overlap=%d" % both)
    check("L2b", (a.notna().sum(axis=1) == 4).all() and (b.notna().sum(axis=1) == 4).all())
    top8 = sc.rank(axis=1, ascending=False, method="first") <= 8
    covered = (a.notna() | b.notna())
    check("L2c", bool((covered == top8).all().all()))
    # the split must be deterministic across calls (method='first', not 'average')
    a2 = top_slice(sc, 1, 4)
    check("L2d", a.equals(a2))

    # L3: blending two identical sleeves returns the sleeve curve
    date_idx = pd.bdate_range("2022-01-03", periods=40)
    r = pd.Series(rng.randn(40) * 0.01, index=date_idx)
    one = (1.0 + r).cumprod()
    one.iloc[0] = 1.0
    bl = blend([one, one])
    check("L3a", np.allclose(bl.values, one.values, atol=1e-12),
          "max diff=%.2e" % float(np.abs(bl.values - one.values).max()))
    check("L3b", abs(bl.iloc[0] - 1.0) < 1e-12)

    # L4: a sleeve that starts late must not halve the book during burn-in
    late = one.copy()
    late.iloc[:20] = np.nan
    bl2 = blend([one, late])
    check("L4a", np.allclose(bl2.values[:20], one.values[:20], atol=1e-10))
    check("L4b", np.allclose(bl2.values[20:], one.values[20:], atol=1e-10))

    # L5: turnover-per-year arithmetic (the figure this whole script is graded on)
    check("L5a", turns_per_year(1.6, 20) == 20.16)
    check("L5b", turns_per_year(1.6, 40) == 10.08)
    check("L5c", turns_per_year(1.6, 10) == 40.32)

    # L6: ImpactCost scalar-equivalence -- a callable that always charges BASE_BP must
    # reproduce the flat path bit for bit, else the priced ladder is not comparable
    # to the flat one it is graded against.
    n_bars, n_names = 260, 10
    didx = pd.bdate_range("2021-01-04", periods=n_bars)
    prng = np.random.RandomState(11)
    px = pd.DataFrame(100.0 * np.exp(np.cumsum(prng.randn(n_bars, n_names) * 0.01, axis=0)),
                      index=didx, columns=cols[:n_names])
    op = px.shift(1).fillna(px.iloc[0])
    amt = pd.DataFrame(5e7, index=didx, columns=cols[:n_names])
    # a single-factor face is enough to exercise the fill maths; the point of the leg
    # is cost equivalence, not which factors built the score
    feats = {"mom_12_1": px}
    flat_ser, flat_turn, _ = F.run_next_open(px, op, amt, feats, 20,
                                             cost=BASE_BP / 1e4, start=str(didx[0].date()))
    cm = ImpactCost(amt, 1e6, k_bp=0.0)          # k=0 => extra_bp=0 => pure BASE_BP
    call_ser, call_turn, _ = F.run_next_open(px, op, amt, feats, 20,
                                             cost=cm, start=str(didx[0].date()))
    diff = float(np.abs(flat_ser.values - call_ser.values).max())
    # a trivial pass is the real risk here: if MIN_HIST is never satisfied the book
    # never trades and both curves are flat 1.0, which would "pass" L6a for free
    check("L6a", diff < 1e-12, "max diff=%.2e" % diff)
    check("L6b", abs(flat_turn - call_turn) < 1e-12)
    check("L6c", flat_turn > 0.0 and bool(cm.rows), "turn=%.4f rows=%d"
          % (flat_turn, len(cm.rows)))
    check("L6d", cm.rows and all(r["rate_bp_per_side"] >= BASE_BP - 1e-9 for r in cm.rows))

    # L7: the stagger face must be graded at matched breadth. The sleeves partition
    # STAGGER_TOP names, so the reference sleeve has to hold the same count -- the
    # r1261 run graded 4+4 against F.N_HOLD=5 and booked the difference as phasing.
    check("L7a", SLEEVE_TOP * 2 == STAGGER_TOP, "top=%d sleeve=%d" % (STAGGER_TOP, SLEEVE_TOP))
    check("L7b", STAGGER_TOP == 8 and SLEEVE_TOP == 4)
    sc8 = pd.DataFrame(rng.rand(6, 12), index=rows, columns=cols)
    union = (top_slice(sc8, 1, SLEEVE_TOP).notna()
             | top_slice(sc8, SLEEVE_TOP + 1, STAGGER_TOP).notna())
    ref = sc8.rank(axis=1, ascending=False, method="first") <= STAGGER_TOP
    check("L7c", bool((union == ref).all().all()),
          "union rows=%s ref rows=%s" % (union.sum(axis=1).tolist(),
                                         ref.sum(axis=1).tolist()))

    # L8: the capacity reading is derived from each line's own measured p90, so a
    # breadth or phasing change cannot inherit another book's number. Synthetic p90s
    # chosen so the arithmetic is checkable by hand: 10M * 1%/10.63% = 0.941M.
    syn_lad = [{"rebal": 20, "flat_8bp": {"cagr": 0.05},
                "priced": {"1e+07": {"cagr": 0.05, "participation_max_p90": 0.1063}}}]
    syn_st = {"single_flat_8bp": {"cagr": 0.048}, "stagger_flat_8bp": {"cagr": 0.05},
              "priced": {"1e+07": {
                  "single": {"cagr": 0.04, "participation_max_p90": 0.0779},
                  "stagger": {"cagr": 0.04, "participation_max_p90": 0.0660}}}}
    cap = _readings(syn_lad, syn_st)["p90_capacity_nav"]
    check("L8a", abs(cap["book_%d_names" % F.N_HOLD] - 1e7 * 0.01 / 0.1063) <= 1)
    check("L8b", abs(cap["single_%d_names" % STAGGER_TOP] - 1e7 * 0.01 / 0.0779) <= 1)
    check("L8c", abs(cap["staggered_%d_names" % STAGGER_TOP] - 1e7 * 0.01 / 0.0660) <= 1)
    check("L8d", cap["stagger_vs_single_pct"] == round(
        100.0 * ((0.01 / 0.0660) / (0.01 / 0.0779) - 1.0), 1))
    # monotone sanity: a smaller p90 must never mean less capacity
    check("L8e", cap["staggered_%d_names" % STAGGER_TOP]
          >= cap["single_%d_names" % STAGGER_TOP] >= cap["book_%d_names" % F.N_HOLD])

    if fails:
        print("SELFTEST FAILED (%d):" % len(fails))
        for f in fails:
            print("  -", f)
        return 1
    # the total is counted, never typed: a hard-coded "19/19" survives adding legs and
    # then misreports how much was actually asserted
    print("selftest %d/%d PASS" % (len(ran), len(ran)))
    return 0


def main(argv=None):
    ap = argparse.ArgumentParser()
    ap.add_argument("cmd", nargs="?", default="run", choices=["run"])
    ap.add_argument("--selftest", action="store_true")
    ap.add_argument("--out", default=None)
    args = ap.parse_args(argv)
    if args.selftest:
        return selftest()
    out = run()
    path = args.out or os.path.join(PATHS.results_dir, "etf_book_turnover.json")
    with open(path, "w", encoding="utf-8") as fh:
        json.dump(out, fh, ensure_ascii=False, indent=1)
    print("wrote", path)
    print("cutoff", out["evidence_cutoff"])
    for row in out["cadence_ladder"]:
        p10 = row["priced"]["1e+07"]
        print("rebal=%-3d flat %6.2f%% turn/yr %5.2f | 10M %6.2f%% (x-ew %+5.2fpp) "
              "p90 %5.2f%%" % (row["rebal"], 100 * (row["flat_8bp"].get("cagr") or 0),
                               row["flat_8bp"]["turns_per_year"],
                               100 * (p10.get("cagr") or 0),
                               p10.get("excess_vs_ew_pp") or 0,
                               100 * (p10.get("participation_max_p90") or 0)))
    st = out["stagger"]
    print("stagger: single %6.2f%% / stagger %6.2f%% (x-ew %+5.2fpp) at flat"
          % (100 * (st["single_flat_8bp"].get("cagr") or 0),
             100 * (st["stagger_flat_8bp"].get("cagr") or 0),
             st["stagger_flat_8bp"].get("excess_vs_ew_pp") or 0))
    return 0


if __name__ == "__main__":
    sys.exit(main())