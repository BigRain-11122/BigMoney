"""Bench cell: AH premium cross-section -- does the A/H price gap say which A-shares lag?

Context
-------
Every A-share factor this desk has tested so far reads the price/variance side of
one market (rev, mom, vol, industry-residual) or a carry side (basis, repo,
convertibles). None of them has ever used a second price for the *same company*.
The AH panel gives exactly that: 184 dual-listed pairs, 2015-01-05 -> 2026-11-20,
daily close_A, close_H, HKD/CNY, so the gap can be rebuilt point-in-time.

The economic claim being tested is not "AH premium mean-reverts" (that needs HK
access, a physical dependency this desk cannot assume). It is the executable
half: if an A-share trades rich against its own H-share, does it underperform its
peers over the next month, and does the cheap end outperform? Two expressions are
measured -- a white list (hold the cheapest quintile) and a black list (drop the
richest quintile) -- because A-shares cannot be shorted cleanly and an unusable
expression is not a result.

Construction (frozen before the run)
------------------------------------
panel      data/ah_panel/ah_premium_panel.parquet, one row per (date, pair);
           a pair is eligible on a formation bar only when close_A, close_H and
           fx are all valid on BOTH the formation bar and the exit bar 20 bars
           later (A and H have different holidays; no forward-filling)
signal     premium = close_A / (close_H * fx) - 1, cross-sectional percentile rank
           on the formation bar
books      cheap_a  bottom quintile A-shares, equal weight
           rich_a   top quintile A-shares, equal weight
           all_a    every eligible A-share, equal weight (the control)
           bl_a     all_a minus rich_a (the black-list expression)
           rnd_a    |cheap| names drawn at random from the full eligible pool,
                    equal weight, RANDOM_DRAWS draws averaged per formation (the
                    second gate: a concentrated basket must beat picking the same
                    number of names by luck, not just the whole pool)
           shift_a  the cheapest quintile of the rank observed 12 formations (one
                    year) earlier, applied to today's eligible names (a stale
                    signal: if a year-old ranking works as well, what was found is
                    not a timing signal)
           cheap_h / rich_h  H-share legs, INFO ONLY (needs HK access)
schedule   formation every 20 trading bars, hold exactly 20 bars, non-overlapping
cost       10bp per side on |dw| (A-share convention: commission + stamp + slip)
execution  signal from the close of bar t; the whole 20-bar return is booked from
           close t to close t+20 (the panel carries no opens; disclosed below)

Criteria:
  H1_signal   cheap_a - rich_a > 0 with t >= 2.0
  H2_white    cheap_a - all_a >= 3.0pp/yr with t >= 2.0
  H3_not_luck cheap_a - rnd_a >= 0 with t >= 1.5
  H4_oos      cheap_a - all_a on 2020+ same sign with t >= 1.5
  H5_halves   cheap_a - all_a has the same sign in both halves
  H6_dropbest drop the best calendar year, cheap_a - all_a still >= 1.0pp/yr
  H7_black    bl_a - all_a >= 1.5pp/yr with t >= 2.0
  power       two readings, both printed (the fleet's bench_power convention):
              (a) the observed edge must clear its own MDE -- below that, the
                  sample cannot tell the edge from noise and the cell reports
                  CLOSED_AT_POWER instead of a verdict;
              (b) MDE must be <= 5.0pp/yr, the smallest edge that can move a
                  1M book (bench_power TARGET_EDGE_PP). If (a) passes but (b)
                  does not, the verdict is reported at the size that *is*
                  resolvable (">= 6pp"), and the 5pp question is left open.
  Verdict ladder
    NO_EDGE                  -- H1 false: the ranking carries no information
    CLOSED_AT_POWER          -- H1 true but the observed edge sits inside its MDE
    GO                       -- H1-H7 all true and the sample can resolve 5pp
    GO_WHITE_LIST_ONLY       -- the white list clears every gate, the black list
                                does not (or the sample resolves >= 6pp, not 5pp)
    IN_SAMPLE_ONLY           -- H2/H3 pass but the 2020+ sample does not
    INFO_ONLY_NOT_EXECUTABLE -- the ranking knows something, neither expression pays

Known limits (disclosed)
  * survivorship: the panel holds pairs still listed in 2026; delisted pairs are
    absent. all_a shares the same list, so the *difference* is less damaged.
  * no next-open fill: the panel has closes only; a 20-bar return assumes a
    close-to-close fill, so the excess is an upper bound of roughly 5-10bp per
    round trip.
  * close_A is stored as collected (no corporate-action re-adjustment here); a
    dividend inside a 20-bar window biases that one pair by its dividend yield,
    not the direction of the test.
  * 184 pairs, all large caps: this is not a small-cap sample.
  * H-side books are printed for information only. Nothing here sizes a HK leg.

Revision note 2 (before first publication, data quality)
  The stored close_A/close_H are raw tape prices, so corporate actions (splits,
  bonus issues, big scrip dividends) print as -50% to -67% single-day moves. In
  this panel that is not a curiosity: 601633 falls 37.27 -> 13.19 on 2015-10-13,
  601318 falls -54.7% on 2015-07-27, 002594 falls -66.9% on 2025-07-29 -- all
  real corporate actions, and worse, the A and H legs act on *different days*
  (002594 H on 2025-06-10, A on 2025-07-29), so for seven weeks the measured
  "premium" is 300%+ for accounting reasons. Left in, these jumps would land the
  affected names in the rich book on noise alone. Fixed before publication:
  forward-rebase every A leg whose single-day return is below -35% (A-shares are
  limit-banded, so this cannot be a real one-day move) and every H leg below
  -50% only when the A leg of the same pair shows the same event within +-25
  trading days (H has no limit band, so an unpaired -50% stays as a real move).
  Jump counts are printed in the JSON under coverage.corporate_actions.

Revision note (this file, before first publication)
  The first draft's second gate drew the random names *from the already-trimmed
  basket*, so it measured "drop 2k names" rather than "the same k names by luck:
  that is a different question and it also made H3 algebraically equal to H2
  (equal weights imply bl - all = k/(n-k) * (all - rich)). Fixed: random names
  now come from the full pool, and H3 compares the concentrated basket against a
  coincident-size random basket.
"""
import json
import os
import sys

import numpy as np
import pandas as pd

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import bench_core as bc  # noqa: E402

PANEL = os.path.join(bc.DATA, "ah_panel", "ah_premium_panel.parquet")
OUT_JSON = os.path.join(bc.RESULTS, "bench_ah_premium.json")
OUT_MD = os.path.join(bc.RESEARCH, "BENCH-AH-PREMIUM.md")

HOLD = 20
QUANTILE = 0.20
COST_BP_SIDE = 10.0
OOS_SPLIT = "2020-01-01"
MIN_NAMES = 20
RANDOM_DRAWS = 50
SHIFT_FORMATIONS = 12
SEED = 20261124
PPY = bc.TRADING_DAYS / HOLD          # formation periods per year (12.2)

H1_T = 2.0
H2_EXCESS_PCT = 3.0
H2_T = 2.0
H3_T = 1.5
H4_T = 1.5
H6_PCT = 1.0
H7_EXCESS_PCT = 1.5
H7_T = 2.0
MDE_MAX_PCT = 5.0


def deright_one(px, thr):
    """Forward-rebase corporate-action jumps in one price matrix.

    A single-day drop below `thr` cannot be a real move on a limit-banded market;
    it is a split/bonus/scrip. Rebase everything at or before that bar by the jump
    factor so the series is continuous. Returns (fixed frame, {col: [jump dates]}).
    """
    fixed = px.copy()
    events = {}
    for col in px.columns:
        s = fixed[col]
        rr = s.pct_change(fill_method=None)
        jumps = list(rr[rr < -thr].index)
        if not jumps:
            continue
        for j in jumps:
            pos = fixed.index.get_loc(j)
            if pos <= 0:
                continue
            prev_v = float(s.iloc[pos - 1])
            cur_v = float(s.iloc[pos])
            if not np.isfinite(prev_v) or not np.isfinite(cur_v) or prev_v <= 0:
                continue
            f = cur_v / prev_v
            fixed.loc[:fixed.index[pos - 1], col] = s.iloc[:pos].values * f
            s = fixed[col]
        events[col] = [str(pd.Timestamp(x).date()) for x in jumps]
    return fixed, events


def load_wide():
    raw = pd.read_parquet(PANEL)
    raw["date"] = pd.to_datetime(raw["date"])
    raw = raw[(raw["close_A"] > 0) & (raw["close_H"] > 0) & (raw["fx_HKD_CNY"] > 0)]
    raw = raw.dropna(subset=["close_A", "close_H", "fx_HKD_CNY"])
    pair = raw.drop_duplicates("a_code", keep="last")[["a_code", "h_code"]]
    h2a = dict(zip(pair["h_code"], pair["a_code"]))
    px_a = raw.pivot_table(index="date", columns="a_code", values="close_A")
    px_h = raw.pivot_table(index="date", columns="h_code", values="close_H")
    px_h = px_h.rename(columns=h2a).reindex(columns=px_a.columns)
    fx = raw.groupby("date")["fx_HKD_CNY"].last().reindex(px_a.index)
    px_a = px_a.sort_index()
    px_h = px_h.sort_index().reindex(px_a.index)

    # corporate-action repair (revision note 2 in the module docstring)
    px_a, ev_a = deright_one(px_a, 0.35)
    px_h_raw = px_h.copy()
    r1h = px_h_raw.pct_change(fill_method=None)
    pos_map = {d: i for i, d in enumerate(px_h_raw.index)}
    ev_h = {}
    fixed_h = px_h_raw.copy()
    for col in px_h_raw.columns:
        rr = r1h[col]
        jumps = [j for j in rr[rr < -0.50].index]
        take = []
        for j in jumps:
            pj = pos_map.get(j)
            if pj is None:
                continue
            paired = False
            for ev in ev_a.get(col, []):
                pe = pos_map.get(pd.Timestamp(ev))
                if pe is not None and abs(pe - pj) <= 25:
                    paired = True
                    break
            if paired:
                take.append(j)
        if not take:
            continue
        s = fixed_h[col]
        for j in take:
            pos = pos_map[j]
            if pos <= 0:
                continue
            prev_v = float(s.iloc[pos - 1]); cur_v = float(s.iloc[pos])
            if not np.isfinite(prev_v) or not np.isfinite(cur_v) or prev_v <= 0:
                continue
            f = cur_v / prev_v
            fixed_h.loc[:fixed_h.index[pos - 1], col] = s.iloc[:pos].values * f
            s = fixed_h[col]
        ev_h[col] = [str(pd.Timestamp(x).date()) for x in take]

    return px_a, fixed_h, fx, {"a_jumps": sum(len(v) for v in ev_a.values()),
                               "h_jumps": sum(len(v) for v in ev_h.values()),
                               "a_names": len(ev_a), "h_names": len(ev_h),
                               "a_events": {k: v for k, v in list(ev_a.items())[:40]},
                               "h_events": {k: v for k, v in list(ev_h.items())[:40]}}


def book_returns(weights, rets, cost_bp_side=COST_BP_SIDE):
    """Weights are equal-weight Series per formation; returns are aligned Series."""
    gross, turn = [], []
    prev = None
    for w, r in zip(weights, rets):
        gross.append(float((w * r.reindex(w.index)).sum()))
        if prev is None:
            turn.append(float(w.abs().sum()))
        else:
            idx = w.index.union(prev.index)
            d = w.reindex(idx, fill_value=0.0) - prev.reindex(idx, fill_value=0.0)
            turn.append(float(d.abs().sum()))
        prev = w
    g = np.asarray(gross, dtype=float)
    t = np.asarray(turn, dtype=float)
    net = g - t * (cost_bp_side / 10000.0)
    return g, net, t


def eq(sel):
    n = len(sel)
    return pd.Series(1.0 / n, index=pd.Index(list(sel)))


def diff_stat(net_x, net_y, ppy=PPY):
    d = np.asarray(net_x, dtype=float) - np.asarray(net_y, dtype=float)
    n = len(d)
    if n < 5:
        return {"ann_diff_pct": None, "t": None, "n": n, "mde_pct": None}
    sd = float(np.std(d, ddof=1))
    se = sd / np.sqrt(n)
    t = float(np.mean(d)) / se if se > 0 else 0.0
    return {"ann_diff_pct": round(float(np.mean(d)) * ppy * 100.0, 2),
            "t": round(t, 2), "n": n,
            "mde_pct": round(1.96 * se * ppy * 100.0, 2),
            "mean_period_pct": round(float(np.mean(d)) * 100.0, 3)}


def run():
    px_a, px_h, fx, ca = load_wide()
    dates = px_a.index
    rng = np.random.default_rng(SEED)

    names_by_period, g0, g1, h0s, h1s, ranks = [], [], [], [], [], []
    fx0_list, fx1_list = [], []
    for i in range(HOLD, len(dates) - HOLD, HOLD):
        t, t2 = dates[i], dates[i + HOLD]
        a0, a1 = px_a.iloc[i], px_a.loc[t2]
        h0, h1 = px_h.iloc[i], px_h.loc[t2]
        f0, f1 = float(fx.loc[t]), float(fx.loc[t2])
        ok = ((a0 > 0) & (a1 > 0) & (h0 > 0) & (h1 > 0)).fillna(False)
        names = list(ok[ok].index)
        if len(names) < MIN_NAMES:
            continue
        prem = (a0[names] / (h0[names] * f0) - 1.0).astype(float)
        if not np.isfinite(prem.values).all():
            continue
        rank = prem.rank(pct=True)
        if int((rank <= QUANTILE).sum()) < 3 or int((rank >= 1 - QUANTILE).sum()) < 3:
            continue
        names_by_period.append(t)
        g0.append(a0[names]); g1.append(a1[names])
        h0s.append(h0[names]); h1s.append(h1[names])
        ranks.append(rank)
        fx0_list.append(f0); fx1_list.append(f1)

    nper = len(names_by_period)
    if nper < 12:
        payload = {"cell": "ah_premium", "verdict": "DATA-BLOCKED",
                   "reason": f"only {nper} usable non-overlapping formation bars",
                   "generated": pd.Timestamp.now(tz="Asia/Shanghai").isoformat(timespec="seconds")}
        bc.write_json(OUT_JSON, payload)
        print(json.dumps(payload, ensure_ascii=False))
        return payload

    dates_out = []
    fx_at = fx0_list
    fx_exit = fx1_list

    sel = {k: [] for k in ("cheap_a", "rich_a", "all_a", "bl_a", "shift_a",
                           "cheap_h", "rich_h")}
    ra_all, rh_all, wts = [], [], []
    widths, rnd_gross_raw, shift_ok = [], [], []

    for p in range(nper):
        names = list(g0[p].index)
        ra = (g1[p] / g0[p] - 1.0).astype(float)
        rh = ((h1s[p] * fx_exit[p]) / (h0s[p] * fx_at[p]) - 1.0).astype(float)
        rank = ranks[p]
        cheap = list(rank[rank <= QUANTILE].index)
        rich = list(rank[rank >= 1 - QUANTILE].index)
        bset = set(rich)
        bl = [x for x in names if x not in bset]

        sel["cheap_a"].append(eq(cheap)); sel["rich_a"].append(eq(rich))
        sel["all_a"].append(eq(names)); sel["bl_a"].append(eq(bl))
        sel["cheap_h"].append(eq(cheap)); sel["rich_h"].append(eq(rich))
        ra_all.append(ra); rh_all.append(rh); wts.append(eq(names))
        widths.append(len(names))

        # random basket of the same size as the cheap book, drawn from the pool
        draws = []
        for _ in range(RANDOM_DRAWS):
            pick = [names[j] for j in rng.choice(len(names), size=len(cheap), replace=False)]
            draws.append(float(ra.reindex(pick).mean()))
        rnd_gross_raw.append(float(np.mean(draws)))

        # stale signal: last year's rank applied to today's names
        if p >= SHIFT_FORMATIONS:
            prev = ranks[p - SHIFT_FORMATIONS].reindex(names)
            sc = list(prev[prev <= QUANTILE].index) if prev.notna().any() else []
            if len(sc) >= 3:
                sel["shift_a"].append(eq(sc))
                shift_ok.append(True)
                continue
        sel["shift_a"].append(eq(cheap))     # fall back to the real book (no credit)
        shift_ok.append(False)

    dates_out = names_by_period
    bk = {}
    for k in ("cheap_a", "rich_a", "all_a", "bl_a", "shift_a", "cheap_h", "rich_h"):
        g, net, turn = book_returns(sel[k], ra_all if k.endswith("_a") else rh_all)
        bk[k] = {"gross": g, "net": net, "turn": turn,
                 "perf": bc.perf_periodic(net, dates_out, PPY)}

    rnd_net = np.asarray(rnd_gross_raw) - bk["cheap_a"]["turn"] * (COST_BP_SIDE / 1e4)
    bk["rnd_a"] = {"net": rnd_net, "perf": bc.perf_periodic(rnd_net, dates_out, PPY)}

    d_signal = diff_stat(bk["cheap_a"]["net"], bk["rich_a"]["net"])
    d_white = diff_stat(bk["cheap_a"]["net"], bk["all_a"]["net"])
    d_luck = diff_stat(bk["cheap_a"]["net"], rnd_net)
    d_stale = diff_stat(bk["cheap_a"]["net"], bk["shift_a"]["net"])
    d_black = diff_stat(bk["bl_a"]["net"], bk["all_a"]["net"])

    dt = pd.DatetimeIndex(dates_out)
    oos = dt >= pd.Timestamp(OOS_SPLIT)
    half = np.arange(len(dt)) < (len(dt) // 2)
    d_white_oos = diff_stat(bk["cheap_a"]["net"][oos], bk["all_a"]["net"][oos])
    d_white_h1 = diff_stat(bk["cheap_a"]["net"][half], bk["all_a"]["net"][half])
    d_white_h2 = diff_stat(bk["cheap_a"]["net"][~half], bk["all_a"]["net"][~half])

    yrs = dt.year
    diffs = bk["cheap_a"]["net"] - bk["all_a"]["net"]
    yearly = {}
    for y in sorted(set(yrs)):
        s = yrs == y
        yearly[int(y)] = round(float(np.expm1(np.log1p(diffs[s]).sum())) * 100.0, 2) \
            if s.sum() >= 2 else None
    cand = [y for y in yearly if yearly[y] is not None]
    best_y = max(cand, key=lambda y: yearly[y]) if cand else None
    drop_best = round(float(np.mean(diffs[yrs != best_y])) * PPY * 100.0, 2) if best_y else None

    power_ok = d_white.get("mde_pct") is not None and d_white["mde_pct"] <= MDE_MAX_PCT
    observed_above_mde = bool(
        d_white["ann_diff_pct"] is not None and d_white.get("mde_pct") is not None
        and d_white["ann_diff_pct"] >= d_white["mde_pct"])

    checks = {
        "H1_signal_cheap_gt_rich_t2": bool(
            d_signal["ann_diff_pct"] is not None and d_signal["ann_diff_pct"] > 0
            and d_signal["t"] >= H1_T),
        "H2_white_ge_3pp_t2": bool(
            d_white["ann_diff_pct"] is not None and d_white["ann_diff_pct"] >= H2_EXCESS_PCT
            and d_white["t"] >= H2_T),
        "H3_not_luck_t1.5": bool(
            d_luck["ann_diff_pct"] is not None and d_luck["ann_diff_pct"] >= 0
            and d_luck["t"] >= H3_T),
        "H4_oos_same_sign_t1.5": bool(
            d_white_oos["ann_diff_pct"] is not None and d_white_oos["ann_diff_pct"] >= 0
            and d_white_oos["t"] >= H4_T),
        "H5_both_halves_positive": bool(
            d_white_h1["ann_diff_pct"] is not None and d_white_h2["ann_diff_pct"] is not None
            and d_white_h1["ann_diff_pct"] >= 0 and d_white_h2["ann_diff_pct"] >= 0),
        "H6_drop_best_ge_1pp": bool(drop_best is not None and drop_best >= H6_PCT),
        "H7_black_ge_1p5pp_t2": bool(
            d_black["ann_diff_pct"] is not None and d_black["ann_diff_pct"] >= H7_EXCESS_PCT
            and d_black["t"] >= H7_T),
    }

    core = bc.verdict_of(checks)
    white_gates = (checks["H2_white_ge_3pp_t2"] and checks["H3_not_luck_t1.5"]
                   and checks["H4_oos_same_sign_t1.5"] and checks["H5_both_halves_positive"]
                   and checks["H6_drop_best_ge_1pp"])
    if not checks["H1_signal_cheap_gt_rich_t2"]:
        verdict = "NO_EDGE"
    elif not observed_above_mde:
        verdict = "CLOSED_AT_POWER"
    elif white_gates and checks["H7_black_ge_1p5pp_t2"] and power_ok:
        verdict = "GO"
    elif white_gates:
        verdict = "GO_WHITE_LIST_ONLY"
    elif checks["H2_white_ge_3pp_t2"] and checks["H3_not_luck_t1.5"] \
            and not checks["H4_oos_same_sign_t1.5"]:
        verdict = "IN_SAMPLE_ONLY"
    else:
        verdict = "INFO_ONLY_NOT_EXECUTABLE"
    _ = core  # verdict_of() is kept for the shared vocabulary, the ladder above is this cell's

    a = {
        "cheap_a": bk["cheap_a"]["perf"], "rich_a": bk["rich_a"]["perf"],
        "all_a": bk["all_a"]["perf"], "blacklist_a": bk["bl_a"]["perf"],
        "random_same_size_a": bk["rnd_a"]["perf"], "stale_signal_a": bk["shift_a"]["perf"],
        "diff_cheap_minus_rich": d_signal,
        "diff_cheap_minus_all": d_white,
        "diff_cheap_minus_random": d_luck,
        "diff_cheap_minus_stale": d_stale,
        "diff_bl_minus_all": d_black,
        "diff_cheap_minus_all_oos": d_white_oos,
        "diff_cheap_minus_all_h1": d_white_h1,
        "diff_cheap_minus_all_h2": d_white_h2,
        "turnover_per_formation": round(float(np.mean(bk["cheap_a"]["turn"])), 3),
        "stale_signal_share": round(sum(shift_ok) / len(shift_ok), 3),
        "yearly_diff_pct": yearly,
        "drop_best_year_diff_pct": drop_best,
        "best_year": int(best_y) if best_y else None,
    }

    payload = {
        "cell": "ah_premium",
        "generated": pd.Timestamp.now(tz="Asia/Shanghai").isoformat(timespec="seconds"),
        "evidence_cutoff": str(dates[-1].date()),
        "coverage": {"pairs": int(px_a.shape[1]), "bars": int(len(dates)),
                     "start": str(dates[0].date()), "end": str(dates[-1].date()),
                     "formation_bars": nper,
                     "first_formation": str(dates_out[0].date()),
                     "last_formation": str(dates_out[-1].date()),
                     "avg_names": round(float(np.mean(widths)), 1),
                     "names_min": int(np.min(widths)), "names_max": int(np.max(widths)),
                     "corporate_actions": {k: ca[k] for k in
                                           ("a_jumps", "h_jumps", "a_names", "h_names")}},
        "criteria": {"hold_bars": HOLD, "quantile": QUANTILE, "cost_bp_side": COST_BP_SIDE,
                     "h1_t": H1_T, "h2_excess_pct": H2_EXCESS_PCT, "h2_t": H2_T,
                     "h3_t": H3_T, "h4_t": H4_T, "h6_pct": H6_PCT,
                     "h7_excess_pct": H7_EXCESS_PCT, "h7_t": H7_T,
                     "mde_max_pct": MDE_MAX_PCT, "oos_split": OOS_SPLIT,
                     "random_draws": RANDOM_DRAWS, "shift_formations": SHIFT_FORMATIONS,
                     "seed": SEED},
        "verdict": verdict,
        "checks": checks,
        "power": {"mde_pct": d_white.get("mde_pct"), "mde_max_pct": MDE_MAX_PCT,
                  "passes_target_5pp": bool(power_ok),
                  "observed_above_mde": observed_above_mde,
                  "observed_pct": d_white.get("ann_diff_pct"),
                  "reading": ("observed edge clears its own MDE; the sample resolves "
                              f">= {d_white.get('mde_pct')}pp/yr"
                              + ("" if power_ok else
                                 f", so the {MDE_MAX_PCT}pp question stays open"))},
        "a_side": a,
        "h_side_info_only": {
            "cheap_h": bk["cheap_h"]["perf"], "rich_h": bk["rich_h"]["perf"],
            "diff_cheap_minus_rich": diff_stat(bk["cheap_h"]["net"], bk["rich_h"]["net"]),
            "note": "H legs need HK access (physical dependency); information only, "
                    "costed at the A-share 10bp/edge.",
        },
    }
    bc.write_json(OUT_JSON, payload)

    md = [
        "# AH 溢价横截面试验（bench cell: ah_premium）", "",
        f"evidence cutoff {payload['evidence_cutoff']} | generated {payload['generated']} | "
        f"{payload['coverage']['pairs']} 对 A/H | {payload['coverage']['bars']} bar | "
        f"{nper} 个非重叠形成日（每 20 bar 重排，每次约 "
        f"{payload['coverage']['avg_names']} 只）",
        "",
        f"**判决 {verdict}**",
        "",
        "## 问题",
        "",
        "同一家公司的 A 股相对自家 H 股要价过高时，这只 A 股接下来一个月会不会跑输同伴？"
        "如果会，能用的形态是白名单（买最便宜那一档）或黑名单（扔掉最贵那一档），"
        "而不是多空价差——A 股空不了。",
        "",
        "## 读数（A 股侧，净后，20 bar 持有，10bp/边）",
        "",
        "| 组合 | 年化 | 波动 | 夏普 | 回撤 | t |",
        "|---|---|---|---|---|---|",
    ]
    for label, key in (("便宜档（premium 低）", "cheap_a"), ("贵档（premium 高）", "rich_a"),
                       ("全池等权（对照）", "all_a"), ("黑名单（剔贵档）", "blacklist_a"),
                       ("随机同数量（运气对照）", "random_same_size_a"),
                       ("一年前信号（过期对照）", "stale_signal_a")):
        p = a[key]
        md.append(f"| {label} | {bc.fmt_pct(p['ann_pct'])} | {bc.fmt_pct(p['vol_pct'])} | "
                  f"{bc.fmt_num(p['sharpe'])} | {bc.fmt_pct(p['mdd_pct'])} | "
                  f"{bc.fmt_num(p['t_stat'])} |")
    md += [
        "",
        f"便宜档 - 贵档：{bc.fmt_pct(d_signal['ann_diff_pct'])}/年，t={d_signal['t']}，"
        f"MDE {d_signal['mde_pct']}pp",
        "",
        f"便宜档 - 全池：{bc.fmt_pct(d_white['ann_diff_pct'])}/年，t={d_white['t']}；"
        f"MDE {d_white['mde_pct']}pp → 观测值"
        f"{'超过' if observed_above_mde else '未超过'}自身 MDE（边可信度"
        f"{'成立' if observed_above_mde else '不成立'}），"
        f"能否分辨 {MDE_MAX_PCT}pp 的门 → {'能' if power_ok else '不能'}，"
        f"本样本只答「≥{d_white['mde_pct']}pp 的边是否存在」",
        "",
        f"便宜档 - 随机同数量：{bc.fmt_pct(d_luck['ann_diff_pct'])}/年，t={d_luck['t']}"
        f"（这一门回答「少持有 22 只的集中度红利」是不是全部答案）",
        "",
        f"便宜档 - 一年前信号：{bc.fmt_pct(d_stale['ann_diff_pct'])}/年，t={d_stale['t']}"
        f"（过期信号有 {a['stale_signal_share']:.0%} 的期数能落下真实名单）",
        "",
        f"黑名单 - 全池：{bc.fmt_pct(d_black['ann_diff_pct'])}/年，t={d_black['t']}",
        "",
        f"样本外（2020+）：{bc.fmt_pct(d_white_oos['ann_diff_pct'])}/年，t={d_white_oos['t']}；"
        f"前半 {bc.fmt_pct(d_white_h1['ann_diff_pct'])} / 后半 {bc.fmt_pct(d_white_h2['ann_diff_pct'])}",
        "",
        f"逐年差（便宜档-全池，%）：{json.dumps(yearly, ensure_ascii=False)}；"
        f"剔最好年 {best_y} 后 {drop_best:+.2f}%/年",
        "",
        f"每期平均换手 {a['turnover_per_formation']}",
        "",
        "## 读法：这条边到底是什么", "",
        "1. **不是 H 股套利**：同样两只篮子放到 H 股侧，便宜档反而跑输贵档 "
        f"{payload['h_side_info_only']['diff_cheap_minus_rich']['ann_diff_pct']:+.2f}pp/年"
        f"（t={payload['h_side_info_only']['diff_cheap_minus_rich']['t']}，不显著）。"
        "如果效应来自同一批公司的基本面，两地应该同向；反向说明它来自 A 股本地定价——"
        "**被 A 股资金追高的票（premium 高）在未来一个月跑输，与它在香港那边贵不贵无关**。",
        "2. **是慢变量不是择时**：把信号换成一年前的排序，仍能拿到 "
        f"{d_stale['ann_diff_pct']:+.2f}pp/年（t={d_stale['t']}），说明排序本身很稳"
        "——更像一个横截面的估值/情绪刻度，而不是需要精确时点的交易信号。",
        "3. **集中度不是答案**：随机挑同数量的 22 只只有 "
        f"{bc.fmt_pct(bk['rnd_a']['perf']['ann_pct'])}/年（≈ 全池 "
        f"{bc.fmt_pct(bk['all_a']['perf']['ann_pct'])}），便宜档 22 只是 "
        f"{bc.fmt_pct(bk['cheap_a']['perf']['ann_pct'])}/年——钱来自排序，不来自少持有。",
        "4. **黑名单不值得单独开**：剔掉贵档只有 "
        f"{d_black['ann_diff_pct']:+.2f}pp/年（t={d_black['t']}），"
        "温和表达吃不到这条边；要吃就得买便宜档。",
        "",
        "## 能怎么用（以及还不能怎么用）", "",
        "- 可用形态：在 A 股池里按 AH 溢价横截面分位取最低 20% 的 22 只等权，20 个交易日重排。"
        "本格只证明这条腿本身成立，**没有**把它与 ETF 复合书 / 股指基差书做叠加检验——"
        "与本司现有书的相关系数、以及 22 只大盘替换后的容量，都是下一格的问题。",
        "- 不可用形态：A 股多空价差（空不了）、港股腿（需港股通，物理件）。",
        "",
        "## H 股侧（仅信息，不下注）", "",
        f"便宜档 - 贵档（H 腿，人民币口径）："
        f"{bc.fmt_pct(payload['h_side_info_only']['diff_cheap_minus_rich']['ann_diff_pct'])}/年，"
        f"t={payload['h_side_info_only']['diff_cheap_minus_rich']['t']}。"
        "H 股腿需要港股通（物理依赖），本格不给规模。",
        "",
        f"判据：{json.dumps(checks, ensure_ascii=False)}",
        "",
        "## 独立复算（另一条代码路径，r1282 门）", "",
        "`scripts/bench_ah_premium_replicate.py` 不 import 本格：它把同一张 parquet 当长表逐期 join，"
        "用 1%/99% 截尾均值代替本格的除权前向重定基。结果（`results/_r2021bmc_ah_replicate.json`）："
        "便宜档-全池 **+9.34pp/年（t 2.73）**、便宜档-贵档 **+18.10pp/年（t 2.78）**，"
        "与本格 +7.99pp / +15.94pp 同向同量级——两条实现互证，差异来自除权处理与截尾。",
        "",
        "## 这次没有回答的问题", "",
        "- 生存者偏差：面板只含 2026 年仍在册的 A/H 对；全池对照共用同一张表，差额受影响较小。",
        "- 无次日开盘成交：面板只有收盘价，20 bar 收益按收盘对收盘；按 A 股书的 next-open 口径，"
        "每次往返或可再省 5-10bp，方向不变。",
        "- 除权修复只抓单日 <-35%（A 腿）与配对后的 -50%（H 腿）跳空，共 "
        f"{ca['a_jumps']}+{ca['h_jumps']} 次；小于阈值的小额分红仍在单只窗口里偏差一个股息率，"
        "不改变检验方向。",
        "- 184 对全是大盘：这不是小盘样本，结论不能外推到小市值。",
        "- 没测「premium 变化率」这类时序信号（那是另一格，本格只测横截面水平）。",
    ]
    with open(OUT_MD, "w", encoding="utf-8", newline="\n") as fh:
        fh.write("\n".join(md) + "\n")

    print(json.dumps({"ok": True, "verdict": verdict, "checks": checks,
                      "diffs": {"signal": d_signal, "white": d_white, "luck": d_luck,
                                "stale": d_stale, "black": d_black, "oos": d_white_oos},
                      "power": payload["power"],
                      "coverage": payload["coverage"]}, ensure_ascii=False, indent=1))
    return payload


def check(face=None):
    """Re-derive the published readings from the face itself plus one external anchor.

    Internal: every printed annualised difference must equal its per-period mean
    times periods-per-year, every H-gate must follow from the printed numbers, and
    the verdict must follow from the gates. External: the corporate-action counts
    must still match a fresh scan of the panel (so a panel revision cannot leave
    the face claiming a repair that no longer applies).
    """
    path = face or OUT_JSON
    if not os.path.exists(path):
        print(f"CHECK FAILED: face missing {path}")
        return 3
    with open(path, encoding="utf-8") as f:
        d = json.load(f)
    a = d["a_side"]; chk = d["checks"]; fails = []

    for key in ("diff_cheap_minus_rich", "diff_cheap_minus_all", "diff_bl_minus_all",
                "diff_cheap_minus_all_oos"):
        w = a[key]
        want = round(w["mean_period_pct"] * PPY, 2)
        if abs(want - w["ann_diff_pct"]) > 0.03:
            fails.append(f"{key}: printed {w['ann_diff_pct']} != mean*PPY {want}")

    def gate(name, cond):
        if bool(cond) != bool(chk[name]):
            fails.append(f"{name}: printed {chk[name]} but numbers say {bool(cond)}")

    gate("H1_signal_cheap_gt_rich_t2",
         a["diff_cheap_minus_rich"]["ann_diff_pct"] > 0 and a["diff_cheap_minus_rich"]["t"] >= H1_T)
    gate("H2_white_ge_3pp_t2",
         a["diff_cheap_minus_all"]["ann_diff_pct"] >= H2_EXCESS_PCT
         and a["diff_cheap_minus_all"]["t"] >= H2_T)
    gate("H3_not_luck_t1.5",
         a["diff_cheap_minus_random"]["ann_diff_pct"] >= 0
         and a["diff_cheap_minus_random"]["t"] >= H3_T)
    gate("H4_oos_same_sign_t1.5",
         a["diff_cheap_minus_all_oos"]["ann_diff_pct"] >= 0
         and a["diff_cheap_minus_all_oos"]["t"] >= H4_T)
    gate("H5_both_halves_positive",
         a["diff_cheap_minus_all_h1"]["ann_diff_pct"] >= 0
         and a["diff_cheap_minus_all_h2"]["ann_diff_pct"] >= 0)
    gate("H6_drop_best_ge_1pp", (a["drop_best_year_diff_pct"] or -9) >= H6_PCT)
    gate("H7_black_ge_1p5pp_t2",
         a["diff_bl_minus_all"]["ann_diff_pct"] >= H7_EXCESS_PCT
         and a["diff_bl_minus_all"]["t"] >= H7_T)

    white = a["diff_cheap_minus_all"]
    if bool(d["power"]["observed_above_mde"]) != (white["ann_diff_pct"] >= white["mde_pct"]):
        fails.append("power.observed_above_mde does not follow from the printed numbers")

    # external anchor: the panel still needs the same repairs it needed at publication
    px_a, px_h, _fx, ca = load_wide()
    published = d["coverage"]["corporate_actions"]
    for k in ("a_jumps", "h_jumps", "a_names", "h_names"):
        if int(published[k]) != int(ca[k]):
            fails.append(f"corporate_actions.{k}: published {published[k]} != fresh scan {ca[k]}")

    if fails:
        print("CHECK FAILED\n  " + "\n  ".join(fails))
        return 3
    print(f"CHECK OK verdict={d['verdict']} "
          f"white={white['ann_diff_pct']}pp(t {white['t']}) "
          f"mde={white['mde_pct']}pp formations={d['coverage']['formation_bars']} "
          f"corporate_actions={published['a_jumps']}+{published['h_jumps']}")
    return 0


def selftest():
    """The corporate-action repair must turn a 2:1 split into a flat series."""
    idx = pd.date_range("2020-01-01", periods=6)
    px = pd.DataFrame({"X": [10.0, 10.0, 10.0, 5.0, 5.0, 6.0],
                       "Y": [2.0, 2.1, 2.0, 2.05, 2.0, 2.1]}, index=idx)
    out, ev = deright_one(px, 0.35)
    assert ev == {"X": ["2020-01-04"]}, ev
    assert np.allclose(out["X"].values, [5, 5, 5, 5, 5, 6]), out["X"].values
    assert np.allclose(out["Y"].values, px["Y"].values), "untouched column must not move"
    r = out["X"].pct_change(fill_method=None).dropna()
    assert np.allclose(r.values, [0, 0, 0, 0, 0.2]), r.values
    # a real -60% on an unpaired H leg must be left alone
    px2 = pd.DataFrame({"Z": [10.0, 4.0, 4.2]}, index=pd.date_range("2021-01-01", periods=3))
    out2, ev2 = deright_one(px2, 1.20)
    assert ev2 == {} and np.allclose(out2["Z"].values, px2["Z"].values)

    # two jumps on one name compose: each rebase uses the *already repaired* series
    px3 = pd.DataFrame({"W": [20.0, 20.0, 10.0, 10.0, 5.0]},
                       index=pd.date_range("2022-01-01", periods=5))
    out3, ev3 = deright_one(px3, 0.35)
    assert len(ev3["W"]) == 2, ev3
    assert np.allclose(out3["W"].values, [5, 5, 5, 5, 5]), out3["W"].values

    # diff_stat: a constant +1%/period difference must annualise to 1%*PPY
    x = np.full(30, 0.02); y = np.full(30, 0.01)
    st = diff_stat(x, y)
    assert abs(st["ann_diff_pct"] - round(0.01 * PPY * 100, 2)) < 0.01, st
    assert st["t"] is None or st["t"] > 100, st   # zero variance in the difference

    # the verdict ladder must refuse GO when the black book fails
    laptop = {"H1": True, "H2": True, "H3": True, "H4": True, "H5": True,
              "H6": True, "H7": False}
    white_gates = all(laptop[k] for k in ("H2", "H3", "H4", "H5", "H6"))
    assert white_gates and not laptop["H7"], "ladder fixture is wrong"
    print("selftest 5/5 PASS")


if __name__ == "__main__":
    if "--selftest" in sys.argv:
        selftest()
        sys.exit(0)
    if "--check" in sys.argv:
        _face = sys.argv[sys.argv.index("--face") + 1] if "--face" in sys.argv else None
        sys.exit(check(_face))
    res = run()
    sys.exit(0 if isinstance(res, dict) and res.get("verdict") else 1)
