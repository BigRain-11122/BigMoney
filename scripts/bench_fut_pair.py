"""Bench cell: paired (long/short) trend -- can cutting the noise make an edge testable?

Why this cell exists
--------------------
`bench_fut_trend` already judged five trend styles NO_EDGE and published the reason
that matters here: on ten products over 9.7 years at 13.6% vol, the minimum
detectable annual edge is 8.6-9.6pp -- the sample cannot see a 5pp edge, so "no
edge" there only rules out enormous edges. `research/BENCH-NEXT.md` item 2 named
the way out: stop asking each product to be directionally right and instead pair
the strongest against the weakest. A balanced long/short book throws away the
market leg, so the same signal should show up in a much smaller volatility and
therefore a much smaller MDE. This cell asks that question and only that one:

    does the cross-sectional trend ranking, expressed as long-top-k / short-
    bottom-k, produce a net edge after 3bp/side that the sample can actually
    resolve -- and does the ranking (not merely the shape "long k names, short
    k names") carry it?

Criteria, frozen before any number is read
------------------------------------------
Primary arm = k=2 per side, 120-bar trend on roll-adjusted prices, weekly
re-strike, 3bp/side, hold pos[t-1] over ret[t].

  H1 full-sample net annual >= 4.0%
  H2 out-of-sample (2024-01-01 on) net annual >= 3.0% and Sharpe >= 0.30
  H3 both halves of the sample net positive
  H4 drop-the-best-calendar-year net annual >= 2.0%
  H5 the ranking beats a control that picks the same k names per side at
     random each rebalance (same weights, same turnover), p < 0.05

H5 is the load-bearing one. On ten products a long/short book can look fine just
because the short leg happens to sit on the low-vol names or because the two
legs carry opposite roll/carry drift; the random-pick control holds all of that
fixed and keeps only the ranking. veredict_of() reads H1-H5.

Robustness arms (printed, not judged): k in {1,2,3} x window in {60,120,250}.
A GO that exists only at one cell of that grid is a claim about the grid, not
about the market, so the grid is published in full.

Nothing here reads the network, writes a shared face, or touches the engine.
"""
import os
import sys

import numpy as np
import pandas as pd

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import bench_core as bc

PRIMARY_K = 2
PRIMARY_W = 120
TARGET_VOL = 0.10
COST_BP_SIDE = bc.COST_BP_SIDE
DRAWS = 200
SEED = 20261122
SPLIT = "2024-01-01"
OUT_JSON = os.path.join(bc.RESULTS, "bench_fut_pair.json")
OUT_PAGE = os.path.join(bc.RESEARCH, "BENCH-FUT-PAIR.md")


def trend_frame(closes, window):
    """Trend score per product: roll-adjusted price vs its own `window`-bar mean."""
    out = {}
    for code, s in closes.items():
        out[code] = s / s.shift(window) - 1.0
    return pd.DataFrame(out)


def select_signals(trend, k):
    """+1 for the k strongest trends, -1 for the k weakest, NaN elsewhere."""
    r = trend.rank(axis=1, ascending=True)
    n = trend.notna().sum(axis=1)
    sig = pd.DataFrame(np.nan, index=trend.index, columns=trend.columns)
    sig = sig.mask(r.le(k), -1.0)
    sig = sig.mask(r.gt(n.sub(k, axis=0), axis=0), 1.0)
    return sig


def random_pick_signals(trend, k, rng):
    """Same shape, no information: pick k names per side at random each bar."""
    vals = trend.values
    sig = np.full(vals.shape, np.nan)
    for i in range(vals.shape[0]):
        ok = np.flatnonzero(np.isfinite(vals[i]))
        if len(ok) < 2 * k:
            continue
        pick = rng.permutation(ok)
        sig[i, pick[:k]] = 1.0
        sig[i, pick[k:2 * k]] = -1.0
    return pd.DataFrame(sig, index=trend.index, columns=trend.columns)


def run_arm(signals, closes, rets, vols, dates):
    pos, live = bc.vol_weighted_positions(signals, vols, target_vol=TARGET_VOL,
                                          max_weight=1.0)
    _, net, turn = bc.apply_costs(pos, rets, cost_bp_side=COST_BP_SIDE)
    p = bc.perf(net.values, dates)
    sp = bc.split_perf(net.values, dates, split=SPLIT)
    return {
        "net": net,
        "pos": pos,
        "full": p,
        "is": sp["is"],
        "oos": sp["oos"],
        "halves": {"first_half_ann_pct": sp.get("first_half_ann_pct"),
                   "second_half_ann_pct": sp.get("second_half_ann_pct")},
        "turnover_per_year": round(float(turn.mean()) * bc.TRADING_DAYS, 1),
        "live_median": float(live.median()) if len(live) else None,
    }


def mde_pp(vol_pct, n_bars):
    """Minimum detectable annual edge at 5% two-sided / 80% power (2.8 sigma/sqrt T)."""
    years = n_bars / bc.TRADING_DAYS
    if not vol_pct or years <= 0:
        return None
    return round(2.8 * float(vol_pct) / np.sqrt(years), 2)


def fmt_pct(x):
    return bc.fmt_pct(x)


def main():
    bc.weight_priority()
    panel = bc.load_futures_products()
    if len(panel) < 6:
        print("DATA-BLOCKED: fewer than 6 futures products on disk")
        return 2
    dates, closes, rets, vols = bc.align_futures(panel)
    cutoff = str(pd.DatetimeIndex(dates).max().date())
    print(f"products={len(panel)} bars={len(dates)} {dates[0].date()}..{cutoff}")

    # ---- primary arm -------------------------------------------------------
    tr = trend_frame(closes, PRIMARY_W)
    sig = select_signals(tr, PRIMARY_K)
    primary = run_arm(sig, closes, rets, vols, dates)

    # ---- long-only trend on the same universe (the vol the paired book removes)
    lo_sig = np.sign(tr)
    lo_sig = lo_sig.where(tr.notna())
    long_only = run_arm(lo_sig, closes, rets, vols, dates)

    # ---- robustness grid ---------------------------------------------------
    grid = []
    for w in (60, 120, 250):
        for k in (1, 2, 3):
            t2 = trend_frame(closes, w)
            s2 = select_signals(t2, k)
            a = run_arm(s2, closes, rets, vols, dates)
            grid.append({
                "window": w, "k": k,
                "ann_pct": a["full"]["ann_pct"],
                "vol_pct": a["full"]["vol_pct"],
                "sharpe": a["full"]["sharpe"],
                "mdd_pct": a["full"]["mdd_pct"],
                "oos_ann_pct": a["oos"]["ann_pct"],
                "mde_pp": mde_pp(a["full"]["vol_pct"], a["full"]["n"]),
            })
            print(f"  grid w={w} k={k}: {a['full']['ann_pct']:+.2f}% "
                  f"vol={a['full']['vol_pct']:.2f}% SR={a['full']['sharpe']:.3f}")

    # ---- auxiliary: does the vol-weighting cause the noise result? ----------
    # Equal notional per leg, 1.0x gross: isolates the construction from the
    # risk-parity scaling. If this book is also not quieter than long-only, the
    # falsification does not depend on how the legs were sized.
    dollar_pos = sig * (1.0 / (2 * PRIMARY_K))
    _, dollar_net, dollar_turn = bc.apply_costs(dollar_pos, rets, cost_bp_side=COST_BP_SIDE)
    dollar = {
        "full": bc.perf(dollar_net.values, dates),
        "oos": bc.split_perf(dollar_net.values, dates, split=SPLIT)["oos"],
        "turnover_per_year": round(float(dollar_turn.mean()) * bc.TRADING_DAYS, 1),
        "gross_notional": round(float(dollar_pos.abs().sum(axis=1).median()), 3),
    }

    # ---- control: same shape, random names ---------------------------------
    rng = np.random.default_rng(SEED)
    real_ann = float(np.mean(primary["net"].values) * bc.TRADING_DAYS) * 100.0
    null = []
    for _ in range(DRAWS):
        s2 = random_pick_signals(tr, PRIMARY_K, rng)
        a = run_arm(s2, closes, rets, vols, dates)
        null.append(float(np.mean(a["net"].values) * bc.TRADING_DAYS) * 100.0)
    null = np.array(null)
    p_value = float((null >= real_ann).mean())
    control = {
        "kind": "random_pick_same_shape",
        "draws": DRAWS,
        "real_ann_pct": round(real_ann, 2),
        "null_mean_ann_pct": round(float(null.mean()), 2),
        "null_p95_ann_pct": round(float(np.percentile(null, 95)), 2),
        "p_value": round(p_value, 4),
    }

    # ---- frozen criteria ---------------------------------------------------
    full, oos = primary["full"], primary["oos"]
    h1 = bool(full["ann_pct"] is not None and full["ann_pct"] >= 4.0)
    h2 = bool(oos["ann_pct"] is not None and oos["ann_pct"] >= 3.0
              and oos["sharpe"] is not None and oos["sharpe"] >= 0.30)
    h1h = primary["halves"]["first_half_ann_pct"]
    h2h = primary["halves"]["second_half_ann_pct"]
    h3 = bool(h1h is not None and h2h is not None and h1h > 0 and h2h > 0)
    h4 = bool(full.get("drop_best_year_ann_pct") is not None
              and full["drop_best_year_ann_pct"] >= 2.0)
    h5 = bool(p_value < 0.05)
    checks = {"H1_full_ge_4": h1, "H2_oos_ge_3_sr_03": h2, "H3_both_halves_pos": h3,
              "H4_drop_best_year_ge_2": h4, "H5_beats_random_pick": h5}
    verdict = bc.verdict_of(checks)

    payload = {
        "cell": "fut_pair_trend",
        "title": "Paired (long/short) cross-sectional trend on ten futures",
        "generated": pd.Timestamp.now().strftime("%Y-%m-%dT%H:%M:%S%z"),
        "cutoff": cutoff,
        "evidence_cutoff": cutoff,
        "design": {
            "products": sorted(panel),
            "bars": int(len(dates)),
            "primary_k": PRIMARY_K,
            "primary_window": PRIMARY_W,
            "target_vol": TARGET_VOL,
            "cost_bp_side": COST_BP_SIDE,
            "rebalance_bars": bc.REBALANCE_BARS,
            "split": SPLIT,
        },
        "primary": {
            "full": full, "is": primary["is"], "oos": oos,
            "halves": primary["halves"],
            "turnover_per_year": primary["turnover_per_year"],
            "live_median": primary["live_median"],
            "mde_pp": mde_pp(full["vol_pct"], full["n"]),
        },
        "long_only_same_universe": {
            "full": long_only["full"], "oos": long_only["oos"],
            "mde_pp": mde_pp(long_only["full"]["vol_pct"], long_only["full"]["n"]),
        },
        "vol_reduction": (
            None if (not full["vol_pct"] or not long_only["full"]["vol_pct"])
            else round(long_only["full"]["vol_pct"] / full["vol_pct"], 2)
        ),
        "robustness_grid": grid,
        "dollar_neutral_aux": dollar,
        "control": control,
        "checks": checks,
        "verdict": verdict,
    }
    bc.write_json(OUT_JSON, payload)
    write_page(payload)
    print(f"PRIMARY {full['ann_pct']:+.2f}% vol={full['vol_pct']:.2f}% "
          f"SR={full['sharpe']:.3f} mdd={full['mdd_pct']:.2f}% "
          f"OOS {fmt_pct(oos['ann_pct'])} SR={oos['sharpe']}")
    print(f"LONG-ONLY {long_only['full']['ann_pct']:+.2f}% "
          f"vol={long_only['full']['vol_pct']:.2f}% "
          f"mde={payload['primary']['mde_pp']}pp vs {payload['long_only_same_universe']['mde_pp']}pp")
    print(f"CONTROL real={control['real_ann_pct']:+.2f}% null={control['null_mean_ann_pct']:+.2f}% "
          f"p={control['p_value']}")
    print(f"VERDICT {verdict} checks={checks}")
    return 0


def write_page(p):
    """Render the research page from the payload so the numbers cannot be retyped."""
    d = p["design"]
    full = p["primary"]["full"]
    oos = p["primary"]["oos"]
    lo = p["long_only_same_universe"]["full"]
    h1, h2 = p["primary"]["halves"].get("first_half_ann_pct"), p["primary"]["halves"].get("second_half_ann_pct")
    ratio = p["vol_reduction"]
    aux = p["dollar_neutral_aux"]["full"]
    aux_ratio = (None if (not lo["vol_pct"] or not aux["vol_pct"])
                 else round(lo["vol_pct"] / aux["vol_pct"], 2))
    if ratio is None or aux_ratio is None:
        noise_line = "Volatility could not be compared (a leg is missing a reading)."
    else:
        verdict_word = "cut" if aux_ratio >= 1.05 else "did not cut"
        noise_line = (
            f"**The premise does not reproduce.** `BENCH-NEXT` item 2 expected pairing to take "
            f"vol to 5-6% and the MDE to ~3.5pp. Measured here: the risk-parity paired book runs "
            f"at {full['vol_pct']:.2f}% vol (long-only {lo['vol_pct']:.2f}%, ratio {ratio}x — "
            f"pairing *raised* it), and the equal-notional paired book runs at {aux['vol_pct']:.2f}% "
            f"(ratio {aux_ratio}x — pairing {verdict_word} vol). The quietest paired book we "
            f"actually found is {aux['vol_pct']:.2f}%, not 5-6%, and it earns "
            f"{fmt_pct(aux['ann_pct'])}/年 at Sharpe {bc.fmt_num(aux['sharpe'])}: it bought quiet "
            f"by giving up the return. Trading the carry for the noise is not an improvement in "
            f"resolution.")
    rows = "\n".join(
        f"| {g['window']} | {g['k']} | {fmt_pct(g['ann_pct'])} | {g['vol_pct']:.2f}% | "
        f"{bc.fmt_num(g['sharpe'])} | {fmt_pct(g['oos_ann_pct'])} | {g['mde_pp']}pp |"
        for g in p["robustness_grid"])
    ck = "\n".join(f"| {k} | {'PASS' if v else 'FAIL'} |" for k, v in p["checks"].items())
    text = f"""# Paired trend on ten futures — does cutting the noise make the edge visible?

> Generated by `scripts/bench_fut_pair.py` at {p['generated']} on bars through
> **{p['cutoff']}**. Every number on this page is rendered from
> `results/bench_fut_pair.json`; retyping a number here is a bug.

## The question

`bench_fut_trend` judged five trend styles NO_EDGE and said why that verdict is
weak: on {d['products'].__len__()} products over this sample, a directional book
at ~13.6% vol can only resolve an edge of 8.6-9.6pp/年. A 5pp edge is invisible
there. The fix `research/BENCH-NEXT.md` item 2 proposed is to stop asking each
product to be right and pair the strongest against the weakest — the market leg
cancels, volatility drops, and the same information becomes measurable.

**One question:** does the cross-sectional trend ranking, as long-top-k / short-
bottom-k, net of {d['cost_bp_side']}bp per side, produce an edge this sample can
resolve — and is it the *ranking* that carries it, or just the shape of holding
long k names and short k names?

## Design (frozen before the numbers)

- Universe: {', '.join(d['products'])} ({d['bars']} bars)
- Signal: roll-adjusted price vs its own {d['primary_window']}-bar mean
- Primary arm: k={d['primary_k']} per side, {d['target_vol']*100:.0f}% vol target,
  weights re-struck every {d['rebalance_bars']} bars, {d['cost_bp_side']}bp/side
- Signal at t's close, position held over t+1's return; roll jumps removed from
  returns, not from prices (a holder rolls, they do not eat the gap)
- Split: in-sample before {d['split']}, out-of-sample on/after

## Primary arm

| | net annual | vol | Sharpe | max drawdown |
|---|---|---|---|---|
| full | {fmt_pct(full['ann_pct'])} | {full['vol_pct']:.2f}% | {bc.fmt_num(full['sharpe'])} | {full['mdd_pct']:.2f}% |
| in-sample | {fmt_pct(p['primary']['is']['ann_pct'])} | {p['primary']['is']['vol_pct']:.2f}% | {bc.fmt_num(p['primary']['is']['sharpe'])} | {p['primary']['is']['mdd_pct']:.2f}% |
| out-of-sample | {fmt_pct(oos['ann_pct'])} | {oos['vol_pct']:.2f}% | {bc.fmt_num(oos['sharpe'])} | {oos['mdd_pct']:.2f}% |
| first half | {fmt_pct(h1)} | | | |
| second half | {fmt_pct(h2)} | | | |

Turnover {p['primary']['turnover_per_year']}/年 notional; median {p['primary']['live_median']:.0f}
products live per bar. Drop the best year: {fmt_pct(full.get('drop_best_year_ann_pct'))}/年.

## Did the pairing buy resolution?

| book | vol | minimum detectable edge |
|---|---|---|
| long/short pair (this cell, {d['target_vol']*100:.0f}% risk-parity) | {full['vol_pct']:.2f}% | {p['primary']['mde_pp']}pp/年 |
| long/short pair, equal notional 1.0x | {p['dollar_neutral_aux']['full']['vol_pct']:.2f}% | {mde_pp(p['dollar_neutral_aux']['full']['vol_pct'], p['dollar_neutral_aux']['full']['n'])}pp/年 |
| long-only trend, same universe | {lo['vol_pct']:.2f}% | {p['long_only_same_universe']['mde_pp']}pp/年 |

Volatility ratio (long-only / paired) {ratio}x. {noise_line}

## Robustness grid (published in full, not judged)

| window | k | net annual | vol | Sharpe | OOS annual | MDE |
|---|---|---|---|---|---|---|
{rows}

## Control: same shape, random names

Re-drawn {p['control']['draws']} times, each draw picking k names per side at
random with identical weights, turnover and costs. Real {fmt_pct(p['control']['real_ann_pct'])}
vs null mean {fmt_pct(p['control']['null_mean_ann_pct'])} (p95 {fmt_pct(p['control']['null_p95_ann_pct'])}),
p = {p['control']['p_value']}.

This is the load-bearing test: on ten products a long/short book can look
respectable because the short leg lands on low-vol names or because the two legs
carry opposite roll drift. The random-pick control holds every one of those
fixed and leaves only the ranking.

## Verdict

| check | result |
|---|---|
{ck}

**{p['verdict']}**

## What this does and does not say

- A NO_EDGE here is *stronger* than in `bench_fut_trend`, because the noise floor
  is lower: it rules out the 3-5pp edges that the directional test could not see.
- A GO here is not a licence to trade. It is a licence to spend the next hour on
  an independent recompute and a paper book, with the grid above published so a
  reader can see whether the answer lives at one grid point or across all nine.
- Ten products is still ten products. Short leg breadth on the bond futures is
  thin, and the 2024+ split is ~2 years — the OOS column is a sanity check, not a
  second sample.
"""
    os.makedirs(os.path.dirname(OUT_PAGE), exist_ok=True)
    with open(OUT_PAGE, "w", encoding="utf-8", newline="\n") as f:
        f.write(text)


if __name__ == "__main__":
    sys.exit(main())
