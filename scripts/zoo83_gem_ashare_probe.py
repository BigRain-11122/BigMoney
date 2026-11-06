"""zoo83_gem_ashare -- supply berth probe (monthly 12-month momentum vs cash).

WHY THIS FILE EXISTS
--------------------
`compute_audit` has reported `supply_floor ready 0 < floor 3` for eight straight
rounds (supply_candidates verdict = AGENDA_DEBT, shortfall 3).  The standing law
says the default action when the pool is starved is to draft or continue the next
wave, and the last two rounds measured what a *timing* rule has to earn on this
book before it is even comparable with holding (exit tax +0.64..+8.39 pp/yr at
0.95..0.30 exposure).  So the next berth has to be a family the time-in-market
rulers do not already price, and it should be cheap enough that cost cannot be
trusted to explain the answer either way.

zoo #83 (`gem_ashare`, research/shortline/ASTYLE_ZOO.md sec.13) is registered
`新写` and has never been burned: monthly 12-month momentum on the CSI-300 ETF
against a cash leg, with an absolute-momentum gate.  It decides twelve times a
year, so its own turnover is ~3x/yr and the question it asks is almost purely
"does the 12-month sign carry information" rather than "is the cost small".

    does a 12-month absolute-momentum switch between 510300 and a treasury ETF
    beat simply holding 510300, after the cost of its own switches, and beyond
    what a same-share random-phase version of the same switch buys?

Everything here is a PROBE.  It burns no family, registers no seed, writes no
ledger row.  Its verdict is a *supply* verdict (ADMIT_TO_PREREG /
REFUSE_AS_CANDIDATE), never a research verdict.

CONSTRUCTION (frozen; changing any of it changes the family)
------------------------------------------------------------
  decision bar      the LAST bar of each calendar month present in the panel
  signal            close[t] / close[t - 252] - 1 on the equity leg, > 0 -> equity
                    (a month-end whose 252-bar lookback is not available is not
                    a decision: the book stays where it was)
  execution         decided on the close of bar t, held from bar t+1 (one-bar lag)
  legs              510300 (CSI-300 ETF) and 511260 (10y treasury ETF), 100% one
                    or the other -- no partial sizing, no leverage
  returns           close-to-close on each leg
  cost              COST_X1_RATE per side, charged on sum | dw | (a full switch
                    trades both legs: turnover 2.0)
  benchmark         buy-and-hold 510300 over the SAME evaluated window
  null              K circular shifts of the equity-weight series: identical
                    equity share, identical persistence, different alignment

The circular null is the right placebo here for the same reason it was for the
alligator probe: the rule's value is its alignment with the up/down phases, and a
permutation would destroy the persistence that is being credited.
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
if HERE not in sys.path:
    sys.path.insert(0, HERE)
if ROOT not in sys.path:
    sys.path.insert(0, ROOT)

from ce_transfer import COST_X1_RATE                      # noqa: E402
from live.paper import build_panels, load_core            # noqa: E402

# ---- frozen constants (echoed into every artifact) -------------------------
FAMILY = "zoo83_gem_ashare"
BATCH = "SUPPLY_BERTH_SLOT_12_CANDIDATE"
EQUITY = "510300"
CASH = "511260"
LOOKBACK = 252                     # 12 months of trading bars
NULL_K = 200
NULL_SEED = 20311007
EVIDENCE_CUTOFF = "2026-11-06"
MIN_BARS = 750
ADMIT_MIN_EXCESS = 0.0
ADMIT_MAX_P = 0.05
ADMIT_DD_MUST_IMPROVE = True
ADMIT_MAX_TURNOVER_PER_YEAR = 12.0

RES_PATH = os.path.join(ROOT, "results", "supply_berth",
                        "zoo83_gem_ashare_probe.json")


def _now():
    return time.strftime("%Y-%m-%dT%H:%M:%S%z")


# --------------------------------------------------------------- mechanics
def month_end_bars(index: pd.DatetimeIndex) -> pd.DatetimeIndex:
    """The last bar of each calendar month present in the panel."""
    if len(index) == 0:
        return index[:0]
    per = pd.Series(index, index=index).groupby(
        [index.year, index.month]).max()
    return pd.DatetimeIndex(sorted(per.to_numpy()))


def absolute_momentum_signal(price: pd.Series, lookback: int = LOOKBACK) -> pd.Series:
    """>0 means "the past `lookback` bars ended higher".  NaN where the lookback
    is not available -- NaN is NOT a zero signal, it is 'no decision yet'."""
    return (price / price.shift(lookback) - 1.0)


def decisions_to_weights(signal_at_me: pd.Series, index: pd.DatetimeIndex) -> pd.Series:
    """Decision on the close of bar t is held from bar t+1.

    Bars before the first decision are 0 (all cash) -- they are also excluded
    from the evaluated window by `evaluated_window`, so no cash return is
    credited to the rule before it could have decided anything.
    """
    w = signal_at_me.reindex(index).ffill()
    w = (w > 0).astype(float).where(w.notna())
    return w.shift(1).fillna(0.0)


def evaluated_window(index: pd.DatetimeIndex, signal_at_me: pd.Series) -> pd.DatetimeIndex:
    """Start at the first bar the rule could actually act on."""
    valid = signal_at_me.dropna()
    if len(valid) == 0:
        return index[:0]
    start = valid.index[0]
    pos = index.get_loc(start)
    return index[pos + 1:]


def run_blend(ret_eq: pd.Series, ret_cash: pd.Series, w_eq: pd.Series,
              cost: float = COST_X1_RATE) -> dict:
    """Net return series of an equity/cash blend at weight w_eq."""
    w = w_eq.reindex(ret_eq.index).fillna(0.0)
    dw = w.diff().abs().fillna(w.abs())
    turn = 2.0 * dw                                  # both legs trade
    net = w * ret_eq + (1.0 - w) * ret_cash - turn * cost
    ann = 252.0
    n = int(len(net))
    sd = float(net.std(ddof=1)) if n > 1 else 0.0
    return {
        "bars": n,
        "equity_share": float(w.mean()),
        "switches": int((dw > 1e-12).sum()),
        "turnover_per_year": float(turn.sum() / max(n / ann, 1e-9)),
        "cost_drag_per_year": float(turn.sum() * cost / max(n / ann, 1e-9)),
        "cagr": float((1.0 + net).prod() ** (ann / n) - 1.0) if n > 0 else None,
        "sharpe": float(net.mean() / sd * np.sqrt(ann)) if sd > 0 else None,
        "maxdd": _maxdd(net),
        "net": net,
    }


def _maxdd(r: pd.Series) -> float:
    eq = (1.0 + r.fillna(0.0)).cumprod()
    return float((eq / eq.cummax() - 1.0).min())


def per_year_excess(net: pd.Series, bh: pd.Series) -> dict:
    """Compounded net vs benchmark, one row per calendar year."""
    out = {}
    yrs = sorted({d.year for d in net.index})
    for y in yrs:
        m = np.array([d.year == y for d in net.index])
        if m.sum() < 20:
            continue
        a = float((1.0 + net[m]).prod() - 1.0)
        b = float((1.0 + bh[m]).prod() - 1.0)
        out[str(y)] = {"net": a, "benchmark": b, "excess": a - b,
                       "bars": int(m.sum())}
    return out


def circular_null(ret_eq: pd.Series, ret_cash: pd.Series, w_eq: pd.Series,
                  observed: float, k: int = NULL_K, seed: int = NULL_SEED) -> dict:
    """Same equity share, same persistence, different phase."""
    w = w_eq.reindex(ret_eq.index).fillna(0.0).to_numpy(dtype=float)
    n = len(w)
    if n < 3:
        return {"k": 0, "p_two_sided": 1.0, "mean": 0.0, "sd": 0.0,
                "method": "not enough bars for a phase null"}
    rng = np.random.default_rng(seed)
    draws = []
    for _ in range(k):
        s = int(rng.integers(1, n - 1))
        draws.append(run_blend(ret_eq, ret_cash,
                               pd.Series(np.roll(w, s), index=ret_eq.index))
                     ["cagr"] - _buyhold_cagr(ret_eq))
    arr = np.array(draws, dtype=float)
    ge = int((np.abs(arr) >= abs(observed)).sum())
    return {
        "k": k,
        "seed": seed,
        "method": "circular phase rotation of the equity-weight series "
                  "(conserves equity share and persistence)",
        "mean": float(arr.mean()),
        "sd": float(arr.std(ddof=1)) if len(arr) > 1 else 0.0,
        "p_two_sided": float((ge + 1) / (k + 1)),
        "p_floor": float(1.0 / (k + 1)),
    }


def _buyhold_cagr(ret: pd.Series) -> float:
    n = len(ret)
    if n == 0:
        return 0.0
    return float((1.0 + ret.fillna(0.0)).prod() ** (252.0 / n) - 1.0)


def decide(summary: dict, null: dict) -> dict:
    """Frozen supply verdict; every condition is reported, not just the boolean."""
    conds = {
        "net_excess_positive": summary["excess_cagr_net"] > ADMIT_MIN_EXCESS,
        "beats_null": null["p_two_sided"] <= ADMIT_MAX_P,
        "drawdown_improves": (summary["maxdd_delta"] > 0
                              if ADMIT_DD_MUST_IMPROVE else True),
        "enough_bars": summary["bars"] >= MIN_BARS,
        "turnover_sane": summary["turnover_per_year"] <= ADMIT_MAX_TURNOVER_PER_YEAR,
    }
    ok = all(conds.values())
    return {
        "verdict": "ADMIT_TO_PREREG" if ok else "REFUSE_AS_CANDIDATE",
        "conditions": conds,
        "thresholds": {"min_excess": ADMIT_MIN_EXCESS, "max_p": ADMIT_MAX_P,
                       "dd_must_improve": ADMIT_DD_MUST_IMPROVE,
                       "min_bars": MIN_BARS,
                       "max_turnover_per_year": ADMIT_MAX_TURNOVER_PER_YEAR},
        "note": "supply verdict only: it decides whether this family earns a "
                "frozen prereg + judge, never what the judge will find",
    }


# ------------------------------------------------------------------- build
def build(prices: dict | None = None, cutoff: str = EVIDENCE_CUTOFF) -> dict:
    prices = prices if prices is not None else load_core()
    P = build_panels(prices)
    close = P["close"]
    if close.index[-1] > pd.Timestamp(cutoff):
        close = close.loc[:pd.Timestamp(cutoff)]
    if EQUITY not in close.columns or CASH not in close.columns:
        raise SystemExit("missing leg: %s / %s" % (EQUITY, CASH))

    eq_p = close[EQUITY]
    cash_p = close[CASH]
    ret_eq = eq_p.pct_change()
    ret_cash = cash_p.pct_change()

    me = month_end_bars(close.index)
    sig = absolute_momentum_signal(eq_p).reindex(me)
    w_all = decisions_to_weights(sig, close.index)
    window = evaluated_window(close.index, sig)
    w = w_all.reindex(window)

    obs = run_blend(ret_eq.reindex(window), ret_cash.reindex(window), w)
    bh_ret = ret_eq.reindex(window)
    bh = {"cagr": _buyhold_cagr(bh_ret), "maxdd": _maxdd(bh_ret),
          "sharpe": (float(bh_ret.mean() / bh_ret.std(ddof=1) * np.sqrt(252))
                     if float(bh_ret.std(ddof=1)) > 0 else None)}
    cash_only = {"cagr": _buyhold_cagr(ret_cash.reindex(window)),
                 "maxdd": _maxdd(ret_cash.reindex(window))}

    summary = {
        "bars": obs["bars"],
        "first_bar": str(window[0].date()) if len(window) else None,
        "last_bar": str(window[-1].date()) if len(window) else None,
        "decisions": int(sig.notna().sum()),
        "equity_share": obs["equity_share"],
        "switches": obs["switches"],
        "turnover_per_year": obs["turnover_per_year"],
        "cost_drag_per_year": obs["cost_drag_per_year"],
        "timing_cagr": obs["cagr"],
        "timing_sharpe": obs["sharpe"],
        "timing_maxdd": obs["maxdd"],
        "buyhold_cagr": bh["cagr"],
        "buyhold_sharpe": bh["sharpe"],
        "buyhold_maxdd": bh["maxdd"],
        "cash_only_cagr": cash_only["cagr"],
        "cash_only_maxdd": cash_only["maxdd"],
    }
    summary["excess_cagr_net"] = summary["timing_cagr"] - summary["buyhold_cagr"]
    summary["maxdd_delta"] = summary["timing_maxdd"] - summary["buyhold_maxdd"]

    null = circular_null(ret_eq.reindex(window), ret_cash.reindex(window), w,
                         summary["excess_cagr_net"])
    by_year = per_year_excess(obs["net"], bh_ret)
    verdict = decide(summary, null)

    return {
        "artifact": "zoo83_gem_ashare supply berth probe",
        "machine": os.environ.get("BM_MACHINE") or _machine(),
        "ts": _now(),
        "evidence_cutoff": cutoff,
        "batch": BATCH,
        "family": FAMILY,
        "construct": {
            "legs": {"equity": EQUITY, "cash": CASH},
            "signal": "close[t]/close[t-%d]-1 > 0 -> equity at t+1" % LOOKBACK,
            "decision_bars": "last bar of each calendar month in the panel",
            "execution": "decided on the close of bar t, held from bar t+1",
            "allocation": "100% one leg (no partial sizing, no leverage)",
            "cost_per_side": COST_X1_RATE,
            "turnover_convention": "sum |dw| over both legs (a switch = 2.0)",
        },
        "panel": {"n_members": int(close.shape[1]),
                  "bars": int(close.shape[0]),
                  "first_bar": str(close.index[0].date()),
                  "last_bar": str(close.index[-1].date())},
        "summary": summary,
        "null": null,
        "per_year": by_year,
        "verdict_block": verdict,
        "honest": [
            "probe only: one construct, one parameter set, no grid -- a positive "
            "here buys a frozen prereg and a proper judge, not a claim that the "
            "rule makes money",
            "the cash leg is an INVESTABLE treasury ETF with its own positive "
            "return: the benchmark is buy-and-hold 510300, so part of any excess "
            "is the bond carry of the months spent out of equity, not selection",
            "the legal-form version of zoo #83 selects between an equity leg and a "
            "CROSS-MARKET leg; this probe narrows it to equity-vs-cash because the "
            "cross-market leg is not in the core panel (a widened construct is a "
            "different family and must not be smuggled in here)",
            "the circular null conserves the equity share, so a rule that is "
            "simply long most of the time cannot win this test on share alone",
            "the panel is today's core48 applied to history: the usual survivor "
            "caveat, unchanged, and 511260 was listed before the panel starts so "
            "the cash leg has no early-history hole",
        ],
    }


def _machine() -> str:
    try:
        with open(os.path.join(ROOT, "fleet", "machine.json"),
                  encoding="utf-8") as fh:
            return json.load(fh).get("machine_id", "unknown")
    except Exception:
        return "unknown"


def run() -> int:
    out = build()
    os.makedirs(os.path.dirname(RES_PATH), exist_ok=True)
    with open(RES_PATH, "w", encoding="utf-8") as fh:
        json.dump(out, fh, ensure_ascii=False, indent=1, sort_keys=True)
    s, n, v = out["summary"], out["null"], out["verdict_block"]
    print("[zoo83] window %s..%s (%d bars, %d decisions)" % (
        s["first_bar"], s["last_bar"], s["bars"], s["decisions"]))
    print("[zoo83] equity_share %.3f  switches %d  turnover %.2f/yr  "
          "cost_drag %.4f/yr" % (s["equity_share"], s["switches"],
                                 s["turnover_per_year"], s["cost_drag_per_year"]))
    print("[zoo83] rule %.4f vs buyhold %.4f  excess %+.4f | maxdd %.4f vs "
          "%.4f (delta %+.4f) | cash-only %.4f" % (
              s["timing_cagr"], s["buyhold_cagr"], s["excess_cagr_net"],
              s["timing_maxdd"], s["buyhold_maxdd"], s["maxdd_delta"],
              s["cash_only_cagr"]))
    print("[zoo83] null p=%.4f (mean %+.4f sd %.4f)" % (
        n["p_two_sided"], n["mean"], n["sd"]))
    print("[zoo83] VERDICT %s  conditions=%s" % (v["verdict"], v["conditions"]))
    print("[zoo83] receipt %s" % os.path.relpath(RES_PATH, ROOT))
    return 0


# ---------------------------------------------------------------- selftest
def selftest() -> int:
    ok, fail = 0, []

    def leg(name, fn):
        nonlocal ok
        try:
            fn()
        except AssertionError as e:
            fail.append("%s: %s" % (name, e))
        else:
            ok += 1

    def _idx(n, start="2021-01-01"):
        return pd.date_range(start, periods=n, freq="B")

    def l_month_end_flags_once_per_month():
        idx = _idx(60)
        me = month_end_bars(idx)
        months = [(d.year, d.month) for d in me]
        assert len(months) == len(set(months)), "a month was flagged twice"
        assert me[0] == idx[[(d.year, d.month) == months[0]
                             for d in idx]].max(), "not the last bar of the month"

    def l_momentum_sign():
        idx = _idx(400)
        up = pd.Series(np.linspace(10, 20, 400), index=idx)
        dn = pd.Series(np.linspace(20, 10, 400), index=idx)
        assert float(absolute_momentum_signal(up).iloc[-1]) > 0, "rising leg must read positive"
        assert float(absolute_momentum_signal(dn).iloc[-1]) < 0, "falling leg must read negative"

    def l_no_lookahead():
        idx = _idx(300)
        sig = pd.Series(np.nan, index=idx)
        sig.iloc[-1] = 1.0
        w = decisions_to_weights(sig.reindex(month_end_bars(idx)), idx)
        assert float(w.iloc[-1]) == 0.0, "a decision cannot earn its own bar"

    def l_window_skips_warmup():
        idx = _idx(400)
        sig = absolute_momentum_signal(pd.Series(np.linspace(10, 20, 400), index=idx))
        w_sig = sig.reindex(month_end_bars(idx))
        win = evaluated_window(idx, w_sig)
        assert len(win) > 0 and win[0] > idx[0], "window must start after warmup"
        assert w_sig.dropna().index[0] < win[0], "window must start after the first decision"

    def l_cost_is_two_legs_per_switch():
        idx = _idx(50)
        r = pd.Series(0.0, index=idx)
        w = pd.Series(0.0, index=idx)
        w.iloc[10:] = 1.0                    # one switch, two legs trade
        out = run_blend(r, r, w, cost=0.001)
        assert out["switches"] == 1, "one switch expected, got %d" % out["switches"]
        assert abs(out["cost_drag_per_year"] - 2.0 * 0.001 * 252 / 50) < 1e-12, \
            "cost must charge both legs once"

    def l_cash_only_earns_cash():
        idx = _idx(300)
        r_eq = pd.Series(0.001, index=idx)
        r_cash = pd.Series(0.0001, index=idx)
        out = run_blend(r_eq, r_cash, pd.Series(0.0, index=idx), cost=0.0)
        expect = _buyhold_cagr(r_cash)
        assert abs(out["cagr"] - expect) < 1e-12, \
            "a fully-cash book must earn exactly the cash leg"

    def l_identity_has_no_excess():
        idx = _idx(800)
        rng = np.random.default_rng(3)
        r_eq = pd.Series(rng.normal(0.0003, 0.01, len(idx)), index=idx)
        r_cash = pd.Series(0.0, index=idx)
        out = run_blend(r_eq, r_cash, pd.Series(1.0, index=idx), cost=0.0)
        assert abs(out["cagr"] - _buyhold_cagr(r_eq)) < 1e-12, \
            "always-in must reproduce buy-and-hold exactly"

    def l_null_does_not_flag_buy_and_hold():
        idx = _idx(600)
        rng = np.random.default_rng(5)
        r_eq = pd.Series(rng.normal(0.0003, 0.01, len(idx)), index=idx)
        r_cash = pd.Series(0.0, index=idx)
        w = pd.Series(1.0, index=idx)
        obs = run_blend(r_eq, r_cash, w, cost=0.0)["cagr"] - _buyhold_cagr(r_eq)
        n = circular_null(r_eq, r_cash, w, obs, k=30)
        assert abs(obs) < 1e-12, "identity excess must be zero"
        assert n["p_two_sided"] > 0.05, "null must not flag an all-equity book"

    def l_null_flags_alignment():
        # Regime blocks, and a weight that is exactly right inside each block:
        # the only thing that made this book special is WHERE the up blocks
        # sit, which is precisely what a phase rotation destroys.
        idx = _idx(600)
        rng = np.random.default_rng(9)
        r_eq = pd.Series(rng.normal(0.0, 0.008, len(idx)), index=idx)
        for lo, hi, mu in ((0, 120, 0.010), (120, 240, -0.010),
                           (240, 400, 0.012), (400, 500, -0.009),
                           (500, 600, 0.011)):
            r_eq.iloc[lo:hi] = r_eq.iloc[lo:hi] + mu
        r_cash = pd.Series(0.0, index=idx)
        w = (r_eq > 0).astype(float)
        obs = run_blend(r_eq, r_cash, w)["cagr"] - _buyhold_cagr(r_eq)
        n = circular_null(r_eq, r_cash, w, obs, k=60)
        assert obs > 0, "a perfectly aligned rule must read positive, got %r" % obs
        assert n["p_two_sided"] <= 0.10, \
            "an aligned rule must be flagged by its own phase null, p=%r" % n["p_two_sided"]

    def l_verdict_names_failing_condition():
        s = {"excess_cagr_net": 0.02, "maxdd_delta": -0.05, "bars": 900,
             "turnover_per_year": 3.0}
        v = decide(s, {"p_two_sided": 0.01})
        assert v["verdict"] == "REFUSE_AS_CANDIDATE", "worse drawdown must refuse"
        assert v["conditions"]["drawdown_improves"] is False, "failing condition must be named"
        assert v["conditions"]["net_excess_positive"] is True, "passing conditions still reported"

    def l_verdict_refuses_expensive_rule():
        s = {"excess_cagr_net": 0.05, "maxdd_delta": 0.02, "bars": 900,
             "turnover_per_year": 30.0}
        v = decide(s, {"p_two_sided": 0.001})
        assert v["verdict"] == "REFUSE_AS_CANDIDATE", "turnover budget must bind"
        assert v["conditions"]["turnover_sane"] is False, "turnover condition must be named"

    def l_verdict_admits_clean_sweep():
        s = {"excess_cagr_net": 0.02, "maxdd_delta": 0.02, "bars": 900,
             "turnover_per_year": 3.0}
        v = decide(s, {"p_two_sided": 0.01})
        assert v["verdict"] == "ADMIT_TO_PREREG", "clean sweep must admit"

    def l_short_panel_refuses_on_bars():
        s = {"excess_cagr_net": 0.05, "maxdd_delta": 0.05, "bars": 200,
             "turnover_per_year": 2.0}
        v = decide(s, {"p_two_sided": 0.001})
        assert v["conditions"]["enough_bars"] is False, "a short window must be named"
        assert v["verdict"] == "REFUSE_AS_CANDIDATE", "short window must refuse"

    def l_deterministic():
        idx = _idx(700)
        rng = np.random.default_rng(13)
        r_eq = pd.Series(rng.normal(0.0003, 0.01, len(idx)), index=idx)
        a = run_blend(r_eq, pd.Series(0.0, index=idx),
                      pd.Series((np.arange(len(idx)) % 30 < 15).astype(float), index=idx))
        b = run_blend(r_eq, pd.Series(0.0, index=idx),
                      pd.Series((np.arange(len(idx)) % 30 < 15).astype(float), index=idx))
        assert json.dumps({k: v for k, v in a.items() if k != "net"}, sort_keys=True) == \
            json.dumps({k: v for k, v in b.items() if k != "net"}, sort_keys=True), \
            "identical input must give identical numbers"

    def l_per_year_covers_window():
        idx = _idx(600)
        net = pd.Series(0.0, index=idx)
        bh = pd.Series(0.0, index=idx)
        py = per_year_excess(net, bh)
        assert sum(v["bars"] for v in py.values()) <= len(idx), "years cannot over-count bars"
        assert all(abs(v["excess"]) < 1e-15 for v in py.values()), "flat arms must show zero excess"

    for name, fn in [
        ("month-end flagged once per month", l_month_end_flags_once_per_month),
        ("momentum sign follows the leg", l_momentum_sign),
        ("a decision cannot earn its own bar", l_no_lookahead),
        ("window starts after warmup", l_window_skips_warmup),
        ("a switch trades both legs", l_cost_is_two_legs_per_switch),
        ("a fully-cash book earns the cash leg", l_cash_only_earns_cash),
        ("always-in reproduces buy-and-hold", l_identity_has_no_excess),
        ("null does not flag buy-and-hold", l_null_does_not_flag_buy_and_hold),
        ("null catches a perfectly aligned rule", l_null_flags_alignment),
        ("verdict names the failing condition", l_verdict_names_failing_condition),
        ("verdict refuses an expensive rule", l_verdict_refuses_expensive_rule),
        ("verdict admits a clean sweep", l_verdict_admits_clean_sweep),
        ("short window refuses on bars", l_short_panel_refuses_on_bars),
        ("receipt is deterministic", l_deterministic),
        ("per-year rows cannot over-count", l_per_year_covers_window),
    ]:
        leg(name, fn)

    total = ok + len(fail)
    for f in fail:
        print("FAIL %s" % f)
    print("selftest: %d/%d PASS" % (ok, total))
    return 0 if not fail else 1


def main(argv) -> int:
    mode = (argv[1] if len(argv) > 1 else "run").lower().lstrip("-")
    if mode == "selftest":
        return selftest()
    if mode == "run":
        return run()
    print("usage: zoo83_gem_ashare_probe.py [run|selftest]", file=sys.stderr)
    return 2


if __name__ == "__main__":
    raise SystemExit(main(sys.argv))