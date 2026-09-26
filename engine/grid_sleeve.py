"""GRID_SLEEVE engine v1 — CN price-grid trading machinery (T-2026-09-26-78
unlock-4, CEO order O-20260926-0958; prereg research/GRID_SLEEVE_P1.md).

NEW ADDITIVE machinery, options_runner/futures_runner precedent: house
backtester / exit_rules / frozen exit priority ZERO-TOUCH (grid = independent
sleeve + independent judgment face per O-0958 (c)).

Execution semantics (frozen prereg sec.3; daily-modelable, causal):
  - band = trailing `band_win`-day [min, max] of close over
    [t-band_win, t-1] -- EXCLUDING today's close: day t's close is measured
    against the previously established band (below-lo must be reachable;
    recomputed daily); no band before warmup -> flat, no signals;
  - levels: `n_grids` equal spacings; level_k = lo + (k+offset)*spacing,
    k=0..n_grids-1 (offset = null-face band-phase jitter only);
  - per-grid position: fixed unit_cash = nav0/n_grids (classic, no
    compounding; each level holds at most one unit);
  - buy: close t crosses DOWN through an unoccupied in-band level
    (prev_close >= level > close) -> buy one unit at open t+1;
  - harvest: a lot exits when close t crosses UP through its frozen target
    (buy_level + spacing at buy time) -> sell whole lot at open t+1;
  - band exit: close t < band_lo (below the *trailing* low, unreachable by
    a monotone slide -- fires on breaks below an established range) ->
    liquidate ALL lots at open t+1, disarm; re-arm when close returns above
    band_lo (no retro buys);
  - above band: no chasing (top-level lots exit via targets on the way up);
  - T+1: signals on close t, executions at open t+1 (a lot bought at open
    t+1 can first be sold at open >= t+2 by construction);
  - costs: `cost_bp` per side (V1 legacy 13.0bp, smoke-verified face),
    x2 pressure face via cost_bp=26.0 (CostPatch(2) convention); cash
    yields 0; fractional shares allowed (weight-face convention).

Segment/judgment faces (frozen prereg sec.4/5): non-overlapping
`seg_len`-day windows classified by close-to-close window return
(|r| < chop_thresh = chop); per-window grid-vs-passive comparison;
chop cumulative face = GATE-A input. Fund-event guard (r239 law):
idiosyncratic |r1| beyond the code's limit with a calm universe median
-> instrument quarantine, honest disclosure.
"""
from __future__ import annotations

import numpy as np
import pandas as pd

from engine.metrics import annual_return, max_drawdown, sharpe


def guard_event_days(close: pd.Series, limit: float = 0.105,
                     universe_median_abs: pd.Series | None = None,
                     uni_thresh: float = 0.03) -> list:
    """Fund-event guard (r239 law, frozen GRID_SLEEVE_P1 sec.2).

    A day counts as a fund event iff |r1| exceeds `limit` (use 0.205 for
    20cm codes) AND the same-day universe median |r1| is below
    `uni_thresh` (idiosyncratic jump, not a market-wide extreme)."""
    r1 = close.pct_change()
    days = []
    for d, r in r1.items():
        if not np.isfinite(r) or abs(r) <= limit:
            continue
        if universe_median_abs is None:
            days.append(d)
            continue
        med = universe_median_abs.get(d, np.nan)
        if (not np.isfinite(med)) or med < uni_thresh:
            days.append(d)
    return days


def run_grid_sleeve(open_px, close_px, index=None, n_grids: int = 10,
                    band_win: int = 250, nav0: float = 1_000_000.0,
                    cost_bp: float = 13.0,
                    band_offset_grids: float = 0.0) -> dict:
    """Simulate the grid sleeve on one instrument. Pure function of inputs
    (deterministic; no repo data, no clock). Returns dict with daily NAV
    series, trade log and judgment faces."""
    o = np.asarray(open_px, dtype=float)
    c = np.asarray(close_px, dtype=float)
    T = len(c)
    if len(o) != T or T < 2:
        raise ValueError("open/close length mismatch or T<2")
    idx = pd.Index(range(T)) if index is None else pd.Index(index)
    if len(idx) != T:
        raise ValueError("index length mismatch")
    if n_grids < 2 or band_win < 2:
        raise ValueError("degenerate engine params")

    bp = cost_bp / 1e4
    unit = nav0 / n_grids
    cash = float(nav0)
    lots: list[dict] = []          # {'k','target','shares','value'}
    occupied: set[int] = set()
    armed = True
    nav = np.full(T, nav0, dtype=float)
    buys, sells = [], []
    skipped_buys = 0
    pending: list = []             # queued at close t, executed at open t+1

    for t in range(T):
        # 1) execute pending at open[t] (sells first: free cash)
        pending.sort(key=lambda a: 0 if a[0] in ("sell", "liquidate") else 1)
        for act in pending:
            if act[0] == "sell":
                lot = act[1]
                if not any(lot is x for x in lots):
                    continue
                p = o[t]
                proceeds = lot["shares"] * p * (1.0 - bp)
                cash += proceeds
                lots = [x for x in lots if x is not lot]
                occupied.discard(lot["k"])
                sells.append({"date": idx[t], "kind": act[2],
                              "level_k": lot["k"], "price": p,
                              "value": proceeds,
                              "pnl": proceeds - lot["value"]})
            elif act[0] == "liquidate":
                p = o[t]
                for lot in list(lots):
                    proceeds = lot["shares"] * p * (1.0 - bp)
                    cash += proceeds
                    sells.append({"date": idx[t], "kind": "whipsaw_exit",
                                  "level_k": lot["k"], "price": p,
                                  "value": proceeds,
                                  "pnl": proceeds - lot["value"]})
                lots = []
                occupied = set()
            elif act[0] == "buy":
                k = act[1]
                p = o[t]
                if cash + 1e-9 < unit or p <= 0:
                    skipped_buys += 1
                    continue
                shares = unit / (p * (1.0 + bp))
                cash -= unit
                lot = {"k": k, "target": act[2], "shares": shares,
                       "value": unit}
                lots.append(lot)
                occupied.add(k)
                buys.append({"date": idx[t], "level_k": k, "price": p,
                             "value": unit})
        pending = []

        # 2) mark NAV at close[t]
        nav[t] = cash + sum(l["shares"] * c[t] for l in lots)

        # 3) signals from close[t] for open[t+1]
        if t + 1 >= T:
            continue
        # band = trailing [t-band_win, t-1] closes, EXCLUDING today: today's
        # close is measured against the previously established band (a
        # below-lo close must be reachable -- incl.-today min is not).
        if t >= band_win:
            lo = float(c[t - band_win:t].min())
            hi = float(c[t - band_win:t].max())
        else:
            lo = hi = None
        if lo is None or hi <= lo:
            continue
        prev = c[t - 1] if t >= 1 else c[t]
        spacing = (hi - lo) / n_grids

        if not armed:
            if c[t] > lo:
                armed = True  # re-arm; levels all unoccupied
            else:
                continue
        if c[t] < lo:                       # band exit: liquidate all
            pending.append(("liquidate", None))
            armed = False
            continue

        # harvest: lot target crossed up
        for lot in list(lots):
            if prev < lot["target"] <= c[t]:
                pending.append(("sell", lot, "harvest"))
        # buy: unoccupied in-band level crossed down
        for k in range(n_grids):
            lvl = lo + (k + band_offset_grids) * spacing
            if lvl < lo or lvl > hi:
                continue                    # offset face: outside band
            if prev >= lvl > c[t] and k not in occupied:
                pending.append(("buy", k, lvl + spacing))

    nav_s = pd.Series(nav, index=idx, name="nav")
    harvests = [s for s in sells if s["kind"] == "harvest"]
    whips = [s for s in sells if s["kind"] == "whipsaw_exit"]
    return {
        "nav": nav_s,
        "params": {"n_grids": n_grids, "band_win": band_win,
                   "cost_bp": cost_bp, "band_offset_grids": band_offset_grids},
        "sharpe": float(sharpe(nav_s)),
        "mdd": float(max_drawdown(nav_s)),
        "ann": float(annual_return(nav_s)),
        "n_round_trips": len(harvests),
        "n_entries": len(buys),
        "n_trades": len(buys) + len(sells),
        "harvest_pnl": float(sum(h["pnl"] for h in harvests)),
        "whipsaw_pnl": float(sum(w["pnl"] for w in whips)),
        "skipped_buys": skipped_buys,
        "buys": buys,
        "sells": sells,
    }


def segment_windows(close: pd.Series, seg_len: int = 60,
                    chop_thresh: float = 0.10) -> list:
    """Frozen segmenter: non-overlapping windows from panel start,
    classified by window close-to-close return (chop / trend_up /
    trend_down)."""
    out = []
    c = np.asarray(close, dtype=float)
    for s in range(0, len(c) - 1, seg_len):
        e = min(s + seg_len, len(c) - 1)
        if e <= s:
            continue
        r = c[e] / c[s] - 1.0
        label = ("chop" if abs(r) < chop_thresh
                 else ("trend_up" if r > 0 else "trend_down"))
        out.append({"start": s, "end": e, "ret": float(r), "label": label})
    return out


def segment_faces(nav: pd.Series, close: pd.Series, seg_len: int = 60,
                  chop_thresh: float = 0.10) -> dict:
    """Grid-vs-passive comparison per segment label (frozen GATE-A face:
    chop cumulative grid return vs chop cumulative passive return)."""
    segs = segment_windows(close, seg_len, chop_thresh)
    nav_v = np.asarray(nav, dtype=float)
    by = {"chop": [], "trend_up": [], "trend_down": []}
    for s in segs:
        g = nav_v[s["end"]] / nav_v[s["start"]] - 1.0
        by[s["label"]].append({"grid": float(g), "passive": s["ret"],
                               "start": s["start"], "end": s["end"]})

    def _cum(rows):
        if not rows:
            return {"grid_cum": 0.0, "passive_cum": 0.0, "n": 0}
        gc, pc = 1.0, 1.0
        for r in rows:
            gc *= (1.0 + r["grid"])
            pc *= (1.0 + r["passive"])
        return {"grid_cum": float(gc - 1.0), "passive_cum": float(pc - 1.0),
                "n": len(rows)}

    return {k: {"windows": v, "cum": _cum(v)} for k, v in by.items()}


def _selftest() -> bool:
    """Offline hermetic checks (stdout-only, no repo data, no network)."""
    ok_all = True

    def ok(name, cond):
        nonlocal ok_all
        print(f"  [{'PASS' if cond else 'FAIL'}] {name}")
        if not cond:
            ok_all = False
        return cond

    rng = np.random.default_rng(20260926)
    idx = pd.date_range("2020-01-02", periods=400, freq="B")
    base = 100 + np.cumsum(rng.normal(0, 0.8, 400))
    close = pd.Series(base, index=idx)
    openp = pd.Series(base * (1 + rng.normal(0, 0.002, 400)), index=idx)

    # [1] determinism: two runs identical
    r1 = run_grid_sleeve(openp, close, idx, band_win=20)
    r2 = run_grid_sleeve(openp, close, idx, band_win=20)
    ok("determinism (byte-equal rerun)",
       r1["nav"].equals(r2["nav"]) and r1["n_trades"] == r2["n_trades"]
       and r1["harvest_pnl"] == r2["harvest_pnl"])

    # [2] causality: truncating the tail must not change any earlier NAV
    r_tr = run_grid_sleeve(openp.iloc[:-50], close.iloc[:-50],
                           idx[:-50], band_win=20)
    ok("causality (tail-truncate prefix equality)",
       np.allclose(r1["nav"].iloc[:-50].to_numpy(),
                   r_tr["nav"].to_numpy(), atol=1e-9, rtol=0))

    # [3] T+1: no lot sold in the same session it was bought
    bad = 0
    for s in r1["sells"]:
        b = [x for x in r1["buys"]
             if x["level_k"] == s["level_k"] and x["date"] <= s["date"]]
        if b and max(x["date"] for x in b) == s["date"]:
            bad += 1
    ok("T+1 (buy session != sell session)", bad == 0)

    # [4] band exit + re-arm: range establishes lo=95, a close below it
    #     must liquidate; recovery re-arms and harvests again
    p4 = np.concatenate([
        np.full(60, 100.0),
        np.tile([95.5, 99.0, 95.8, 98.5], 8),      # range 95..100
        [92.0],                                      # close below lo -> exit
        np.full(20, 91.0),
        [96.0],                                      # re-arm above lo
        np.tile([95.5, 99.0, 95.8, 98.5], 6),
        np.full(30, 97.0)])
    close4 = pd.Series(p4, index=idx[:len(p4)])
    open4 = pd.Series(p4, index=idx[:len(p4)])
    r4 = run_grid_sleeve(open4, close4, idx[:len(p4)], band_win=20)
    kinds = [s["kind"] for s in r4["sells"]]
    ok("band-exit (whipsaw liquidation + re-arm harvests)",
       "whipsaw_exit" in kinds and r4["n_round_trips"] > 0
       and r4["nav"].min() > 0)

    # [5] harvest math: engineered sawtooth, formula-checked P&L (bp=0)
    saw = np.tile([95.0, 99.0, 94.5, 98.5, 94.0, 98.0], 6)
    p5 = np.concatenate([np.full(60, 100.0), saw, np.full(40, 96.0)])
    close5 = pd.Series(p5, index=idx[:len(p5)])
    open5 = pd.Series(p5, index=idx[:len(p5)])
    r5 = run_grid_sleeve(open5, close5, idx[:len(p5)], n_grids=10,
                         band_win=20, nav0=1000.0, cost_bp=0.0)
    pairs: dict = {}
    for b in r5["buys"]:
        pairs.setdefault(b["level_k"], []).append(b)
    expect = 0.0
    for h in [s for s in r5["sells"] if s["kind"] == "harvest"]:
        cand = [x for x in pairs[h["level_k"]] if x["date"] < h["date"]]
        b = max(cand, key=lambda x: x["date"])
        expect += (1000.0 / 10) * (h["price"] / b["price"] - 1.0)
    ok("harvest pnl (formula re-derivation)",
       r5["n_round_trips"] >= 5
       and abs(r5["harvest_pnl"] - expect) < 1e-6
       and r5["whipsaw_pnl"] == 0.0)

    # [6] guard: idiosyncratic jump flagged, market-wide jump not
    uni = pd.Series(0.005, index=idx)
    g1 = close.copy()
    g1.iloc[200:] *= 0.85                  # persistent -15% level shift:
    ok("guard idiosyncratic flagged",      # exactly one jump day
       len(guard_event_days(g1, 0.105, uni, 0.03)) == 1)
    uni_mkt = pd.Series(0.05, index=idx)          # market-wide extreme day
    ok("guard market-wide not flagged",
       len(guard_event_days(g1, 0.105, uni_mkt, 0.03)) == 0)

    # [7] invariants: NAV positive, no skipped buys on the random panel
    ok("nav positive + no skipped buys",
       bool((r1["nav"] > 0).all()) and r1["skipped_buys"] == 0)

    # [8] segmenter: labels partition, chop face wired
    sf = segment_faces(r1["nav"], close, seg_len=60, chop_thresh=0.10)
    n_all = sum(sf[k]["cum"]["n"] for k in sf)
    ok("segmenter (windows partition + labels)",
       n_all > 0 and all(sf[k]["cum"]["n"] == len(sf[k]["windows"])
                         for k in sf))

    print(f"grid_sleeve selftest: {'8/8 PASS' if ok_all else 'FAIL'}")
    return ok_all


if __name__ == "__main__":
    raise SystemExit(0 if _selftest() else 2)
