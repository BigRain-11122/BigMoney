"""zoo90_alligator_timing -- supply berth probe (SLOT-11 candidate).

WHY THIS FILE EXISTS
--------------------
The fill ladder has reported `compatible_ready=0 floor=3` for six straight
rounds while every round since r1380 shipped another *gate*.  The standing
law (TRIAL_LABOR_LAW sec.1 / S3 standing line) says the default action when
the pool is starved is to draft or continue the next wave, not to build more
machinery.  The r258 eligibility scan ranked `zoo90_alligator_timing` as the
A-layer BACKUP berth and it has never been burned (only two mentions in the
tree: the scan itself and one judgment digest line).

This probe answers exactly one question, before anyone spends a frozen
prereg and a full judge on it:

    does a Bill-Williams Alligator timing state, applied to the same
    equal-weight core panel the rest of the firm measures on, beat simply
    holding that panel -- after the real cost of its own turnover, and
    beyond what a random exposure with the SAME in-market share would buy?

Everything here is a PROBE.  It does not burn a family, does not register a
seed, does not write a ledger row, and its verdict is a *supply* verdict
(`ADMIT_TO_PREREG` / `REFUSE_AS_CANDIDATE`), never a research verdict.

CONSTRUCTION (frozen; changing any of it changes the family)
------------------------------------------------------------
  median price          (high + low) / 2, equal-weight basket of the panel
  SMMA(n)               x[0]=median[0]; x[i]=(x[i-1]*(n-1)+median[i])/n
  jaw / teeth / lips    SMMA(13) shift 8 / SMMA(8) shift 5 / SMMA(5) shift 3
  state                 1 when lips > teeth > jaw (fast stack above slow),
                        else 0 -- evaluated on the CLOSE of bar i
  exposure              state shifted one bar (decide at close, hold next bar)
  returns               equal-weight daily basket return, close-to-close
  cost                  COST_X1_RATE per side (ce_transfer, single source)
                        charged on |exposure - exposure.shift(1)|
  null                  K circular shifts of the exposure series: identical
                        persistence and identical in-market share, only the
                        phase moves.  Two-sided.

The circular-shift null is chosen on purpose: a block bootstrap would have to
invent a block length, and a permutation would destroy the very persistence
whose value we are testing.
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
FAMILY = "zoo90_alligator_timing"
BATCH = "SUPPLY_BERTH_SLOT_11_CANDIDATE"
JAW, TEETH, LIPS = 13, 8, 5
SH_J, SH_T, SH_L = 8, 5, 3
NULL_K = 200
NULL_SEED = 20311000
EVIDENCE_CUTOFF = "2026-10-30"
MIN_BARS = 750                      # ~3y of basket history or refuse
ADMIT_MIN_EXCESS = 0.0              # net excess over buy-and-hold must be >0
ADMIT_MAX_P = 0.05
ADMIT_DD_MUST_IMPROVE = True

RES_PATH = os.path.join(ROOT, "results", "supply_berth",
                        "zoo90_alligator_probe.json")


def _now():
    return time.strftime("%Y-%m-%dT%H:%M:%S%z")


def smma(s: pd.Series, n: int) -> pd.Series:
    """Smoothed moving average (Wilder form), first value = first input."""
    vals = s.to_numpy(dtype=float)
    out = np.empty_like(vals)
    if len(vals) == 0:
        return pd.Series(out, index=s.index)
    out[0] = vals[0]
    a = 1.0 / n
    for i in range(1, len(vals)):
        out[i] = out[i - 1] + a * (vals[i] - out[i - 1])
    return pd.Series(out, index=s.index)


def alligator_state(median: pd.Series) -> pd.Series:
    """1 where lips > teeth > jaw on this bar's close, else 0."""
    jaw = smma(median, JAW).shift(SH_J)
    teeth = smma(median, TEETH).shift(SH_T)
    lips = smma(median, LIPS).shift(SH_L)
    state = ((lips > teeth) & (teeth > jaw)).astype(float)
    state[jaw.isna() | teeth.isna() | lips.isna()] = 0.0
    return state


def held(exposure: pd.Series) -> pd.Series:
    """Exposure decides at the close of bar i and earns bar i+1's return."""
    return exposure.shift(1).fillna(0.0)


def run_series(ret: pd.Series, exposure: pd.Series, cost: float = COST_X1_RATE):
    """Net timing series vs buy-and-hold on one basket."""
    e = held(exposure)
    turn = (e - e.shift(1)).abs().fillna(0.0)
    net = e * ret - turn * cost
    ann = 252.0
    bh = ret
    sd = float(net.std(ddof=1))
    out = {
        "bars": int(len(ret)),
        "in_market_share": float(e.mean()),
        "trades": int((turn > 0).sum()),
        "turnover_per_year": float(turn.sum() / max(len(ret) / ann, 1e-9)),
        "cost_drag_per_year": float(turn.sum() * cost / max(len(ret) / ann, 1e-9)),
        "timing_cagr": float((1.0 + net).prod() ** (ann / len(ret)) - 1.0),
        "buyhold_cagr": float((1.0 + bh).prod() ** (ann / len(ret)) - 1.0),
        "timing_sharpe": float(net.mean() / sd * np.sqrt(ann)) if sd > 0 else None,
        "buyhold_sharpe": (float(bh.mean() / bh.std(ddof=1) * np.sqrt(ann))
                           if float(bh.std(ddof=1)) > 0 else None),
        "timing_maxdd": _maxdd(net),
        "buyhold_maxdd": _maxdd(bh),
    }
    out["excess_cagr_net"] = out["timing_cagr"] - out["buyhold_cagr"]
    out["maxdd_delta"] = out["timing_maxdd"] - out["buyhold_maxdd"]
    return out


def _maxdd(r: pd.Series) -> float:
    eq = (1.0 + r.fillna(0.0)).cumprod()
    return float((eq / eq.cummax() - 1.0).min())


def basket(close: pd.DataFrame) -> pd.Series:
    """Equal-weight daily return of every member priced on both bars."""
    r = close.pct_change()
    return r.mean(axis=1, skipna=True).dropna()


def circular_null(ret: pd.Series, exposure: pd.Series, observed: float,
                  k: int = NULL_K, seed: int = NULL_SEED):
    """Null: the same exposure series, phase-rotated.  Same share, same
    persistence, different alignment -- the sharpest available placebo for a
    timing rule whose value *is* its alignment."""
    e = exposure.to_numpy(dtype=float)
    n = len(e)
    rng = np.random.default_rng(seed)
    draws = []
    for _ in range(k):
        s = int(rng.integers(1, n - 1))
        draws.append(run_series(ret, pd.Series(np.roll(e, s), index=ret.index))
                     ["excess_cagr_net"])
    arr = np.array(draws, dtype=float)
    ge = int((np.abs(arr) >= abs(observed)).sum())
    return {
        "k": k,
        "seed": seed,
        "method": "circular phase rotation of the exposure series "
                  "(conserves in-market share and persistence)",
        "mean": float(arr.mean()),
        "sd": float(arr.std(ddof=1)) if len(arr) > 1 else 0.0,
        "p_two_sided": float((ge + 1) / (k + 1)),
        "p_floor": float(1.0 / (k + 1)),
    }


def decide(summary: dict, null: dict) -> dict:
    """Frozen supply verdict.  Every condition is reported, not just the
    boolean, so a reader can see WHICH one refused the candidate."""
    conds = {
        "net_excess_positive": summary["excess_cagr_net"] > ADMIT_MIN_EXCESS,
        "beats_null": null["p_two_sided"] <= ADMIT_MAX_P,
        "drawdown_improves": (summary["maxdd_delta"] > 0
                              if ADMIT_DD_MUST_IMPROVE else True),
        "enough_bars": summary["bars"] >= MIN_BARS,
    }
    ok = all(conds.values())
    return {
        "verdict": "ADMIT_TO_PREREG" if ok else "REFUSE_AS_CANDIDATE",
        "conditions": conds,
        "thresholds": {"min_excess": ADMIT_MIN_EXCESS, "max_p": ADMIT_MAX_P,
                       "dd_must_improve": ADMIT_DD_MUST_IMPROVE,
                       "min_bars": MIN_BARS},
        "note": "supply verdict only: it decides whether this family earns a "
                "frozen prereg + judge, never what the judge will find",
    }


def build(prices: dict | None = None) -> dict:
    prices = prices if prices is not None else load_core()
    P = build_panels(prices)
    close = P["close"]
    if close.index[-1] > pd.Timestamp(EVIDENCE_CUTOFF):
        close = close.loc[:pd.Timestamp(EVIDENCE_CUTOFF)]
    hl = (P["high"] + P["low"]) / 2.0
    if hl.index[-1] > pd.Timestamp(EVIDENCE_CUTOFF):
        hl = hl.loc[:pd.Timestamp(EVIDENCE_CUTOFF)]

    ret = basket(close)
    med = hl.mean(axis=1, skipna=True)
    state = alligator_state(med)
    exposure = state.reindex(ret.index).fillna(0.0)

    summary = run_series(ret, exposure)
    null = circular_null(ret, exposure, summary["excess_cagr_net"])
    verdict = decide(summary, null)

    #: single-symbol cross-check so a basket average cannot hide a rule that
    #: only works on the panel's lucky member
    cross = {}
    for sym in ("510300", "510500", "510050"):
        if sym not in close.columns:
            continue
        c = close[sym].dropna()
        if len(c) < MIN_BARS:
            cross[sym] = {"skipped": "history %d < %d" % (len(c), MIN_BARS)}
            continue
        r1 = c.pct_change().dropna()
        e1 = alligator_state(hl[sym].dropna()).reindex(r1.index).fillna(0.0)
        cross[sym] = run_series(r1, e1)

    shape = {"n_members": int(close.shape[1]),
             "bars": int(close.shape[0]),
             "first_bar": str(close.index[0].date()),
             "last_bar": str(close.index[-1].date()),
             "median_price_basis": "(high+low)/2 cross-sectional mean"}
    return {
        "artifact": "zoo90_alligator_timing supply berth probe",
        "machine": os.environ.get("BM_MACHINE") or _machine(),
        "ts": _now(),
        "evidence_cutoff": EVIDENCE_CUTOFF,
        "batch": BATCH,
        "family": FAMILY,
        "construct": {
            "smma_periods": [JAW, TEETH, LIPS],
            "shifts": [SH_J, SH_T, SH_L],
            "state_rule": "lips > teeth > jaw (fast stack over slow), "
                          "close of bar i, exposure on bar i+1",
            "cost_per_side": COST_X1_RATE,
        },
        "panel": shape,
        "summary": summary,
        "null": null,
        "verdict_block": verdict,
        "cross_symbol": cross,
        "honest": [
            "probe only: one construct, one parameter set, no grid -- a "
            "positive here buys a frozen prereg and a proper judge, not a "
            "claim that the rule makes money",
            "the equal-weight basket rebalances daily at zero cost; the "
            "timing overlay's own turnover IS charged, the basket's is not "
            "(it is the measuring rod, not the candidate)",
            "in-market share is reported first because that is what the "
            "circular null conserves: a rule that is simply long most of the "
            "time cannot win this test on share alone",
            "no look-ahead is possible by construction (one-bar lag plus "
            "twelve bars of SMMA/shift warmup), but the basket composition "
            "is today's panel applied to history -- the usual survivor "
            "caveat, unchanged",
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
    print("[zoo90] panel %d members x %d bars (%s..%s)" % (
        out["panel"]["n_members"], out["panel"]["bars"],
        out["panel"]["first_bar"], out["panel"]["last_bar"]))
    print("[zoo90] in_market %.3f  trades %d  cost_drag %.4f/yr | "
          "timing %.4f vs buyhold %.4f  excess %+.4f" % (
              s["in_market_share"], s["trades"], s["cost_drag_per_year"],
              s["timing_cagr"], s["buyhold_cagr"], s["excess_cagr_net"]))
    print("[zoo90] maxdd %.4f vs %.4f (delta %+.4f) | null p=%.4f "
          "(mean %+.4f sd %.4f)" % (
              s["timing_maxdd"], s["buyhold_maxdd"], s["maxdd_delta"],
              n["p_two_sided"], n["mean"], n["sd"]))
    print("[zoo90] VERDICT %s  conditions=%s" % (v["verdict"], v["conditions"]))
    print("[zoo90] receipt %s" % os.path.relpath(RES_PATH, ROOT))
    return 0


# --------------------------------------------------------------- selftest
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

    def l_smma_flat():
        s = pd.Series([5.0] * 40)
        a = smma(s, 13)
        assert abs(float(a.iloc[-1]) - 5.0) < 1e-12, "SMMA of a constant != it"

    def l_smma_step():
        # Wilder form: after a step the value must sit strictly between old
        # and new, never overshoot
        s = pd.Series([0.0] * 20 + [1.0] * 20)
        a = smma(s, 5)
        assert 0.0 < float(a.iloc[-1]) < 1.0, "SMMA overshoots its input range"

    def l_state_bullish():
        idx = pd.date_range("2020-01-01", periods=200, freq="D")
        med = pd.Series(np.linspace(10, 40, 200), index=idx)
        st = alligator_state(med)
        assert float(st.iloc[-1]) == 1.0, "rising series must read bullish"

    def l_state_flat_zero():
        idx = pd.date_range("2020-01-01", periods=200, freq="D")
        st = alligator_state(pd.Series(10.0, index=idx))
        assert float(st.sum()) == 0.0, "flat series must never read bullish"

    def l_no_lookahead():
        # the exposure that earns bar i's return must have been decided on i-1
        e = pd.Series([0.0, 0.0, 1.0, 1.0], index=range(4))
        h = held(e)
        assert float(h.iloc[2]) == 0.0 and float(h.iloc[3]) == 1.0, \
            "held() must lag the decision by one bar"

    def l_cost_only_on_change():
        idx = pd.date_range("2020-01-01", periods=10, freq="D")
        r = pd.Series(0.0, index=idx)
        e = pd.Series(1.0, index=idx)          # enter once, never leave
        out = run_series(r, e, cost=0.001)
        assert out["trades"] == 1, "one ramp in = one trade, got %d" % \
            out["trades"]
        assert abs(out["cost_drag_per_year"] - 0.001 * 252 / 10) < 1e-9, \
            "cost must be charged exactly once"

    def l_zero_exposure_matches_cash():
        idx = pd.date_range("2020-01-01", periods=10, freq="D")
        r = pd.Series(np.linspace(-0.01, 0.01, 10), index=idx)
        out = run_series(r, pd.Series(0.0, index=idx))
        assert abs(out["timing_cagr"]) < 1e-15, "flat exposure must earn zero"
        assert out["trades"] == 0, "flat exposure must not trade"

    def l_null_identity_no_edge():
        # a rule that IS buy-and-hold has no excess; the same-share null must
        # not hand it a significant p.  The one-bar decision lag means bar 0's
        # return is never earnable, so the fixture starts flat and charges no
        # cost: what is under test is the null, not the lag convention.
        idx = pd.date_range("2015-01-01", periods=1200, freq="D")
        rng = np.random.default_rng(7)
        r = pd.Series(rng.normal(0.0003, 0.01, len(idx)), index=idx)
        r.iloc[0] = 0.0
        e = pd.Series(1.0, index=idx)
        s = run_series(r, e, cost=0.0)
        n = circular_null(r, e, s["excess_cagr_net"], k=whale_k(),
                          seed=NULL_SEED)
        assert abs(s["excess_cagr_net"]) < 1e-12, \
            "buy-and-hold must show exactly zero excess, got %r" % \
            s["excess_cagr_net"]
        assert n["p_two_sided"] > 0.05, \
            "null must not flag an all-ones exposure, p=%r" % n["p_two_sided"]

    def l_null_catches_bad_alignment():
        # a rule held exactly through the down bars is a large NEGATIVE
        # excess; the null is two-sided, so it must flag it just the same.
        # The exposure is pre-lagged here so that held() lands it on the
        # intended bars -- the fixture tests the null, not the rule.
        idx = pd.date_range("2015-01-01", periods=1200, freq="D")
        rng = np.random.default_rng(11)
        r = pd.Series(rng.normal(0.0003, 0.01, len(idx)), index=idx)
        e = (r < 0).astype(float).shift(-1).fillna(0.0)
        s = run_series(r, e)
        n = circular_null(r, e, s["excess_cagr_net"], k=whale_k(),
                          seed=NULL_SEED)
        assert s["excess_cagr_net"] < 0, \
            "long-only-when-falling must read negative, got %r" % \
            s["excess_cagr_net"]
        assert n["p_two_sided"] <= 0.05, (
            "a perfectly misaligned rule must be flagged by its own phase "
            "null, p=%r" % n["p_two_sided"])

    def l_decide_reports_every_condition():
        s = {"excess_cagr_net": 0.02, "maxdd_delta": -0.05, "bars": 900}
        n = {"p_two_sided": 0.01}
        v = decide(s, n)
        assert v["verdict"] == "REFUSE_AS_CANDIDATE", \
            "dd that worsens must refuse even with positive excess and p"
        assert v["conditions"]["drawdown_improves"] is False, \
            "the failing condition must be named"
        assert v["conditions"]["net_excess_positive"] is True, \
            "passing conditions must still be reported"

    def l_decide_admits():
        s = {"excess_cagr_net": 0.02, "maxdd_delta": 0.05, "bars": 900}
        v = decide(s, {"p_two_sided": 0.01})
        assert v["verdict"] == "ADMIT_TO_PREREG", "clean sweep must admit"

    def l_basket_ignores_short_history():
        idx = pd.date_range("2020-01-01", periods=6, freq="D")
        a = pd.Series([1, 2, 3, 4, 5, 6], index=idx, dtype=float)
        b = pd.Series([1.0, 1.0, np.nan, np.nan, np.nan, np.nan], index=idx)
        r = basket(pd.DataFrame({"a": a, "b": b}))
        assert len(r) == 5, "basket must keep bars with any priced member"

    def l_receipt_is_deterministic():
        # same inputs -> byte-identical summary (wall clock lives outside it)
        idx = pd.date_range("2018-01-01", periods=400, freq="D")
        med = pd.Series(np.sin(np.arange(400) / 12.0) + 20.0, index=idx)
        st = alligator_state(med)
        a = run_series(pd.Series(0.001, index=idx), st)
        b = run_series(pd.Series(0.001, index=idx), alligator_state(med))
        assert json.dumps(a, sort_keys=True) == json.dumps(b, sort_keys=True), \
            "identical input must give identical numbers"

    def whale_k():
        return 40

    for name, fn in [
        ("smma of a constant is that constant", l_smma_flat),
        ("smma never overshoots a step", l_smma_step),
        ("rising series reads bullish", l_state_bullish),
        ("flat series never reads bullish", l_state_flat_zero),
        ("exposure lags the decision one bar", l_no_lookahead),
        ("cost is charged once per change", l_cost_only_on_change),
        ("flat exposure earns zero and trades zero", l_zero_exposure_matches_cash),
        ("null does not flag buy-and-hold", l_null_identity_no_edge),
        ("null catches a perfectly aligned rule", l_null_catches_bad_alignment),
        ("verdict names every condition", l_decide_reports_every_condition),
        ("verdict admits a clean sweep", l_decide_admits),
        ("basket keeps partially priced bars", l_basket_ignores_short_history),
        ("receipt is deterministic", l_receipt_is_deterministic),
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
    print("usage: zoo90_alligator_probe.py [run|selftest]", file=sys.stderr)
    return 2


if __name__ == "__main__":
    raise SystemExit(main(sys.argv))