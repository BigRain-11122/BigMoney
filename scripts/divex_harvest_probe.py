"""Dividend pre-ex-date ("抢权") harvest probe: cost-adjusted, execution-timed.

Source prior: results/div_event_census/CENSUS-2026-10-19.json measured
close-to-close windows around ex-dates and found pre10 excess +0.86pp vs a
matched random-date control. That census explicitly applied no cost model and
no execution face, so it cannot answer "is the run-up harvestable".

This probe answers that question in measurement terms only:
  * execution face = buy at the OPEN of day (ex_date - k), sell at the CLOSE of
    day (ex_date - 1). No lookahead: both legs are observable trading days.
  * market leg = arithmetic equal-weight cross-sectional mean return over the
    same open-to-close window (same estimator as the event leg, so the excess
    carries no volatility-drag bias).
  * costs = two sides at COST_X1_RATE (single source scripts/ce_transfer.py).
  * tradability filters: entry day must not be a one-price session (high == low,
    i.e. open locked - not realistically buyable) and exit day must not be a
    one-price session (not sellable); suspended/missing legs drop the event.
  * random control = same-holding-length random (symbol, day) windows drawn from
    the panel with a fixed seed, same adjustment and same cost.

Zero judged lines, zero prereg gates, zero pool writes. A judged batch (if any)
must open through research/PREREG_TEMPLATE.md with an explicit exit axis.

Usage:
  python scripts/divex_harvest_probe.py            # run -> results/divex_harvest/
  python scripts/divex_harvest_probe.py --selftest # offline math self-test
"""
from __future__ import annotations

import argparse
import json
import os
import sys
import time

import numpy as np

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(ROOT, "scripts"))

OUT_DIR = os.path.join(ROOT, "results", "divex_harvest")
DIV_FACE = os.path.join(ROOT, "data", "fund_history_export", "div_events_faces.parquet")
HOLD_KS = (3, 5, 10, 15)
ERAS = ((1990, 2009), (2010, 2015), (2016, 2020), (2021, 2099))
CONTROL_SEED = 20261020
CONTROL_PER_K = 5000


def cost_x1():
    from ce_transfer import COST_X1_RATE
    return float(COST_X1_RATE)


def _era(year: int) -> str:
    for lo, hi in ERAS:
        if lo <= year <= hi:
            return f"{lo}-{hi}"
    return "out-of-range"


def _board(code: str) -> str:
    if code.startswith(("60", "68")):
        return "sh"
    if code.startswith(("00", "30")):
        return "sz"
    if code.startswith(("8", "4", "920")):
        return "bj"
    return "other"


def stats(x) -> dict:
    x = np.asarray(x, dtype=float)
    x = x[np.isfinite(x)]
    n = int(x.size)
    if n < 2:
        return {"n": n, "mean": None, "sd": None, "t": None, "win_rate": None}
    mean = float(np.mean(x))
    sd = float(np.std(x, ddof=1))
    t = float(mean / (sd / np.sqrt(n))) if sd > 0 else None
    return {"n": n, "mean": round(mean, 6), "sd": round(sd, 6),
            "t": None if t is None else round(t, 3),
            "win_rate": round(float(np.mean(x > 0)), 4)}


def market_window_ret(open_, close, i0: int, i1: int, cache: dict) -> float:
    """Arithmetic equal-weight market window return (open i0 -> close i1).

    Arithmetic (not geometric) on purpose: the event leg is an arithmetic
    single-name return, so the benchmark must use the same estimator or the
    excess would carry a Jensen/volatility-drag bias.
    """
    key = (i0, i1)
    if key in cache:
        return cache[key]
    with np.errstate(divide="ignore", invalid="ignore"):
        r = close[i1] / open_[i0] - 1.0
    r = np.where(np.isfinite(r), r, np.nan)
    vals = r[np.isfinite(r)]
    m = float(np.mean(vals)) if vals.size >= 4 else float("nan")
    cache[key] = m
    return m


def _one_price(hi: np.ndarray, lo: np.ndarray, i: int, j: int) -> bool:
    h, l = float(hi[i, j]), float(lo[i, j])
    return bool(np.isfinite(h) and np.isfinite(l) and h > 0 and abs(h - l) < 1e-12)


def collect_events(open_, close, high, low, dates, syms, events, mkt, c1):
    """Per-k event table with net excess returns after cost."""
    day = {d: i for i, d in enumerate(dates)}
    col = {s: j for j, s in enumerate(syms)}
    out = {k: [] for k in HOLD_KS}
    drop = {k: {"no_ex_date": 0, "no_entry": 0, "no_exit": 0,
                "entry_locked": 0, "exit_locked": 0, "mkt_leg": 0}
            for k in HOLD_KS}
    n_events = 0
    for code, ex_date, per10 in events:
        j = col.get(code)
        i1 = day.get(ex_date)
        if j is None or i1 is None or i1 < 1:
            for k in HOLD_KS:
                drop[k]["no_ex_date"] += 1
            continue
        n_events += 1
        ex_close = close[i1 - 1, j]
        ex_open = open_[i1, j]
        yield_proxy = (float(per10) / 10.0 / float(ex_close)
                       if np.isfinite(ex_close) and ex_close > 0 else float("nan"))
        for k in HOLD_KS:
            i0 = i1 - k
            if i0 < 1:
                drop[k]["no_entry"] += 1
                continue
            o, c = open_[i0, j], close[i1 - 1, j]
            if not (np.isfinite(o) and np.isfinite(c) and o > 0 and c > 0):
                if not np.isfinite(o):
                    drop[k]["no_entry"] += 1
                else:
                    drop[k]["no_exit"] += 1
                continue
            if _one_price(high, low, i0, j):
                drop[k]["entry_locked"] += 1
                continue
            if _one_price(high, low, i1 - 1, j):
                drop[k]["exit_locked"] += 1
                continue
            m = market_window_ret(open_, close, i0, i1 - 1, mkt)
            if not np.isfinite(m):
                drop[k]["mkt_leg"] += 1
                continue
            gross = float(c) / float(o) - 1.0
            excess = gross - m
            net = excess - 2.0 * c1
            out[k].append((net, gross, excess, yield_proxy,
                           int(dates[i1 - 1][:4]), _board(code), code,
                           ex_date, float(ex_open) if np.isfinite(ex_open) else None))
    return out, drop, n_events


def random_control(open_, close, high, low, mkt, c1, k, rng, n):
    """Random (symbol, day) windows of the same holding length, same filters."""
    T, N = close.shape
    vals = []
    tries = 0
    while len(vals) < n and tries < n * 40:
        tries += 1
        i0 = int(rng.integers(1, T - k))
        j = int(rng.integers(0, N))
        i1 = i0 + k - 1
        o, c = open_[i0, j], close[i1, j]
        if not (np.isfinite(o) and np.isfinite(c) and o > 0 and c > 0):
            continue
        if _one_price(high, low, i0, j) or _one_price(high, low, i1, j):
            continue
        m = market_window_ret(open_, close, i0, i1, mkt)
        if not np.isfinite(m):
            continue
        vals.append(float(c) / float(o) - 1.0 - m - 2.0 * c1)
    return np.asarray(vals, dtype=float)


def summarize(events_k, ctrl, depth=1):
    net = np.asarray([r[0] for r in events_k], dtype=float)
    gross = np.asarray([r[1] for r in events_k], dtype=float)
    excess = np.asarray([r[2] for r in events_k], dtype=float)
    face = {
        "n_events": int(net.size),
        "net_excess": stats(net),
        "gross": stats(gross),
        "excess_pre_cost": stats(excess),
        "control": stats(ctrl),
        "pctl_vs_control": (None if ctrl.size < 10 or net.size < 2
                            else round(float(np.mean(ctrl < np.mean(net))), 4)),
        "by_era": {},
        "by_board": {},
        "by_year": {},
        "by_yield_quintile": {},
    }
    yq = [r[3] for r in events_k]
    yq_arr = np.asarray(yq, dtype=float)
    finite = yq_arr[np.isfinite(yq_arr)]
    cuts = (np.quantile(finite, [0.2, 0.4, 0.6, 0.8]) if finite.size >= 10 else None)
    for r in events_k:
        era = _era(r[4])
        board = r[5]
        yr = str(r[4])
        if cuts is not None and np.isfinite(r[3]):
            q = int(np.searchsorted(cuts, r[3], side="right"))
            qk = f"Q{q + 1}"
        else:
            qk = "NA"
        face["by_era"].setdefault(era, []).append(r[0])
        face["by_board"].setdefault(board, []).append(r[0])
        face["by_year"].setdefault(yr, []).append(r[0])
        face["by_yield_quintile"].setdefault(qk, []).append(r[0])
    for name in ("by_era", "by_board", "by_year", "by_yield_quintile"):
        face[name] = {kk: stats(vv) for kk, vv in sorted(face[name].items())}
    return face


def probe(open_, close, high, low, dates, syms, events, c1):
    mkt = {}
    ev, drop, n_events = collect_events(open_, close, high, low, dates, syms,
                                        events, mkt, c1)
    rng = np.random.default_rng(CONTROL_SEED)
    out = {}
    for k in HOLD_KS:
        ctrl = random_control(open_, close, high, low, mkt, c1, k, rng,
                              CONTROL_PER_K)
        out[str(k)] = {"drops": drop[k], "face": summarize(ev[k], ctrl)}
    return out, n_events


def readout(faces) -> dict:
    """Descriptive decision aid: does a cost-adjusted pre-ex harvest survive
    into the current era (2021+)?"""
    CURRENT = "2021-2099"
    MIN_CURRENT_NET = 0.0025  # 25bp net of cost = economically meaningful floor
    verdict = {}
    for k, blk in faces.items():
        f = blk["face"]
        eras = f["by_era"]
        pos_eras = sum(1 for e in eras.values()
                       if e["mean"] is not None and e["mean"] > 0)
        cur = eras.get(CURRENT) or {}
        cur_mean = cur.get("mean")
        ctrl = f["control"]
        above = (ctrl["mean"] is not None and f["net_excess"]["mean"] is not None
                 and f["net_excess"]["mean"] > ctrl["mean"])
        verdict[k] = {
            "net_mean": f["net_excess"]["mean"],
            "control_mean": ctrl["mean"],
            "above_control": bool(above),
            "positive_eras": int(pos_eras),
            "n_eras": len(eras),
            "era_stable": bool(pos_eras >= 3),
            "current_era_net_mean": cur_mean,
            "current_era_n": cur.get("n"),
            "current_era_meaningful": bool(
                cur_mean is not None and cur_mean >= MIN_CURRENT_NET),
        }
    alive = [k for k, v in verdict.items() if v["current_era_meaningful"]]
    hist_only = [k for k, v in verdict.items()
                 if v["above_control"] and v["era_stable"]
                 and not v["current_era_meaningful"]]
    if alive:
        label = "PRE_EX_HARVEST_MEASURABLE_CURRENT_ERA"
    elif hist_only:
        label = "PRE_EX_HARVEST_HISTORICAL_ONLY_FADED_IN_2021_PLUS"
    else:
        label = "PRE_EX_HARVEST_NOT_TRADEABLE_ON_THIS_FACE"
    return {
        "per_k": verdict,
        "current_era_floor": MIN_CURRENT_NET,
        "k_current_era_alive": alive,
        "k_historical_only": hist_only,
        "label": label,
    }


def _selftest() -> int:
    ok = []

    def check(name, cond):
        ok.append((name, bool(cond)))

    T, N = 60, 4
    close = np.full((T, N), 10.0)
    open_ = np.full((T, N), 10.0)
    high = np.full((T, N), 10.2)
    low = np.full((T, N), 9.8)
    close[40:, 0] = np.linspace(10.0, 11.0, T - 40)
    open_[40:, 0] = np.linspace(10.0, 10.9, T - 40)
    c1 = 0.0013041
    mkt = {}
    check("flat market leg on constant panel",
          abs(market_window_ret(open_, close, 1, 30, mkt)) < 1e-12)
    m = market_window_ret(open_, close, 45, 50, mkt)
    check("market window small when only one column moves", abs(m) < 0.01)
    dates = [f"2020-01-{i + 1:02d}" for i in range(T)]
    dates = sorted(dates)
    syms = ["000001", "000002", "000003", "000004"]
    events = [("000001", dates[50], 5.0)]
    ev, drop, n_events = collect_events(open_, close, high, low, dates, syms,
                                        events, mkt, c1)
    check("event counted", n_events == 1)
    r = ev[3][0]
    expect_gross = float(close[49, 0]) / float(open_[47, 0]) - 1.0
    check("gross uses open entry / pre-ex close exit",
          abs(r[1] - expect_gross) < 1e-12)
    check("net subtracts two-sided cost", abs(r[0] - (r[2] - 2 * c1)) < 1e-12)
    check("yield proxy computed", abs(r[3] - 5.0 / 10.0 / float(close[49, 0])) < 1e-12)
    # one-price entry day must be dropped
    high2 = high.copy()
    low2 = low.copy()
    high2[47, 0] = low2[47, 0] = 10.0
    ev2, drop2, _ = collect_events(open_, close, high2, low2, dates, syms,
                                   events, mkt, c1)
    check("locked entry day dropped", len(ev2[3]) == 0 and drop2[3]["entry_locked"] == 1)
    rng = np.random.default_rng(7)
    ctrl = random_control(open_, close, high2, low2, mkt, c1, 3, rng, 50)
    check("control samples finite", bool(np.all(np.isfinite(ctrl))))
    f = summarize(ev[5], np.asarray([]))
    check("summarize by_era key", list(f["by_era"].keys()) == ["2020-2029"]
          or list(f["by_era"].keys()) == ["2016-2020"])
    fails = [n for n, v in ok if not v]
    for n, v in ok:
        print(("PASS " if v else "FAIL ") + n)
    print(f"selftest {len(ok) - len(fails)}/{len(ok)} PASS")
    return 0 if not fails else 1


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--selftest", action="store_true")
    args = ap.parse_args(argv)
    if args.selftest:
        return _selftest()

    import pandas as pd
    from stagestyle_combo_p1_backtest import load_local_panel

    t0 = time.time()
    panel = load_local_panel()
    if panel is None:
        print("PANEL_MISSING: data/cache/p1c_local not readable -> honest exit 3")
        return 3
    idx, syms, arrays, meta = panel
    close = np.asarray(arrays["close"], dtype=np.float64)
    open_ = np.asarray(arrays["open"], dtype=np.float64)
    high = np.asarray(arrays["high"], dtype=np.float64)
    low = np.asarray(arrays["low"], dtype=np.float64)
    dates = [str(d)[:10] for d in np.asarray(idx)]
    df = pd.read_parquet(DIV_FACE, columns=["code", "ex_date", "cash_div_per_10"])
    df = df[df["cash_div_per_10"].fillna(0) > 0]
    df = df[df["ex_date"].astype(str) >= dates[0]]
    events = [(str(c).zfill(6), str(d)[:10], float(v))
              for c, d, v in zip(df["code"], df["ex_date"], df["cash_div_per_10"])]
    print(f"panel {close.shape} cutoff={meta.get('cutoff')} events={len(events)}")

    c1 = cost_x1()
    faces, n_events = probe(open_, close, high, low, dates, syms, events, c1)
    ro = readout(faces)
    cutoff = str(meta.get("cutoff"))
    payload = {
        "face": "DIV-EX-PRE-HARVEST-PROBE",
        "status": "EXPLORATORY_ZERO_JUDGED_CLAIMS",
        "evidence_cutoff": cutoff,
        "panel": {"path": "data/cache/p1c_local", "shape": list(close.shape),
                  "start": dates[0], "end": dates[-1]},
        "dividend_face": "data/fund_history_export/div_events_faces.parquet",
        "cost": {"unit": "per_side_rate", "x1_rate": c1,
                 "source": "scripts/ce_transfer.py COST_X1_RATE"},
        "method": {
            "execution": "buy at open of (ex_date - k), sell at close of (ex_date - 1)",
            "market_leg": ("arithmetic equal-weight cross-sectional mean return over "
                           "the same open-to-close window (same estimator as the "
                           "event leg, so excess carries no volatility-drag bias)"),
            "net": "gross - market_leg - 2*cost",
            "control": (f"random (symbol, day) windows of the same holding length, "
                        f"seed {CONTROL_SEED}, n={CONTROL_PER_K} per k"),
        },
        "events": {"candidates": len(events), "usable": n_events},
        "windows": faces,
        "readout": ro,
        "disclosures": [
            "qfq panel neutralises the mechanical ex-date dividend drop; only the "
            "economic move net of dividend is measured",
            "yield proxy (cash_div_per_10 / 10 / qfq close) overstates yield for "
            "older events because qfq back-adjusts prices; quintiles are relative "
            "buckets only",
            "one-price sessions (high == low) are dropped on both legs; events "
            "otherwise assume full fill at the open with no market impact beyond "
            "the flat x1 rate",
            "market leg is an equal-weight index proxy, not a tradable benchmark "
            "and not a beta-neutral hedge",
            "the close of (ex_date - 1) is the exit leg; holding through the "
            "ex-date itself is out of scope for this face",
            "events cluster in the dividend season, so t-statistics ignore "
            "cross-event correlation and overstate precision; the random control "
            "and the per-era split are the load-bearing evidence, not the t",
            "control windows are random (symbol, day) draws and share the same "
            "arithmetic-index bias; the event-vs-control gap is the fair read",
            "zero prereg gates, zero judged lines, zero pool writes",
        ],
        "elapsed_sec": round(time.time() - t0, 1),
        "generated_at": time.strftime("%Y-%m-%dT%H:%M:%S"),
    }
    os.makedirs(OUT_DIR, exist_ok=True)
    path = os.path.join(OUT_DIR, f"HARVEST-{cutoff}.json")
    with open(path, "w", encoding="utf-8") as fh:
        json.dump(payload, fh, ensure_ascii=False, indent=1)
    with open(os.path.join(OUT_DIR, "latest.json"), "w", encoding="utf-8") as fh:
        json.dump(payload, fh, ensure_ascii=False, indent=1)
    lines = ["k,era,n,net_mean,net_t,win_rate"]
    for k, blk in faces.items():
        for era, s in blk["face"]["by_era"].items():
            lines.append(f"{k},{era},{s['n']},{s['mean']},{s['t']},{s['win_rate']}")
    with open(os.path.join(OUT_DIR, f"by-k-era-{cutoff}.csv"), "w",
              encoding="utf-8") as fh:
        fh.write("\n".join(lines) + "\n")
    print(f"-> {path}")
    print(json.dumps(ro["per_k"], ensure_ascii=False))
    print("label:", ro["label"])
    return 0


if __name__ == "__main__":
    sys.exit(main())