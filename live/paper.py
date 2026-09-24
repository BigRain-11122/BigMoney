"""Paper tracking pipeline (J16): accrue paper evidence for registered traders.

Why: firm/hr.py INTERN->TRAINEE requires paper months (paper_months_min=1,
OS-round-8 fix). Without this pipeline months_tracked stays 0 forever =
promotion channel dead-locked. PLAN.md 0.6: no live before paper.

Contract per trader JSON (self-contained repro, no results-file dependency):
  - entry signal rebuilt from the SIGNAL_BUILDERS registry (registered
    params.entry string); unknown string -> hard abort, no silent fallback
  - engine params from the params dict (bridge kwargs); NON-bridged exit
    fields (e.g. loss_time_days) via the runtime ExitConfig factory patch
    (engine files untouched, bridge kwargs WIN -- J15-proven pattern)
  - anchor gate first: full-history run TRUNCATED at evidence_cutoff must
    reproduce the registered in_sample/out_sample numbers (|d|<0.002,
    trades exact) BEFORE any paper write; drift -> abort, trader JSON
    untouched (fake-evidence guard, G2 lesson 6.1). evidence_cutoff keeps
    the anchor stable under daily data extension.
  - closed bars only; signal at day T close executes T+1 open (engine
    contract, no look-ahead); paper clock starts at trader["created"]
    with a fresh portfolio -- signal warmup uses PAST closes only
  - month counting: a month is tracked iff it is a FULL calendar month
    observed from hire (first day >= paper_start) AND fully elapsed by
    the data cutoff; the hire stub-month never counts (no promotion
    gaming); current_dd uses the engine negative convention (hr.py
    thresholds compare against negative drawdowns)
  - T-20 PAPER_GUARD_DUAL_RAIL: the FORWARD accounting window runs
    guarded (board-seal buy drops / limit-down sell deferral /
    suspension blocks via scripts/t14_rules_fidelity.build_guard, built
    fresh each run); the anchor_gate reproduction path NEVER receives a
    guard (A-rail legacy byte-identical). Disclosure rides in the
    additive "forward_guard" block of results/paper/<TID>_paper.json.

Usage:
    python -m live.paper             # update paper state + trader JSONs
    python -m live.paper --selftest  # patches + aggregation + causality + anchor

Products:
    results/paper/<TID>_paper.json   state (window, months, cost-x2 check)
    firm/traders/<TID>.json          paper block (months_tracked,
                                     monthly_returns, current_dd, as_of)
"""
import datetime as dt
import json
import os
import sys
import time

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import pandas as pd

from config import PATHS
import engine.backtester as _eb
from engine import run_backtest
from engine.metrics import annual_return, max_drawdown, sharpe
from firm.hr import TRADERS_DIR, load_trader, save_trader
from firm.risk.regime import regime_report
from strategies import volatility
from strategies.composite_rotation import top_n_rotation
import strategies.folk as _fk_mod
import strategies.patterns as _pt_mod
import strategies.ta as _ta_mod
from scripts.science_gates import COST_X2_RATE, CostPatch  # T-03-F12 single source (re-exported for lfc/p3 importers)
from scripts.regime_calibration import (  # T-21 s3.2 import-replay (no cache)
    build_bench, bench_dim_series, breadth_series, raw_series, state_replay)
from scripts.market_regime import raw_level_v3, resolve_state_v3

OOS_START = "2025-01-01"        # registered evidence segment split (J7+)
ANCHOR_TOL = 0.002             # project standard (J14/J15)
COST_X1_RATE = 0.0013041       # G2-recorded baseline single-side cost
MIN_BARS_COST_CHECK = 20       # cost-x2 verdict needs a real window
INITIAL_CASH = 1_000_000.0     # engine default (anchor + paper same)
PAPER_LEVELS = ("INTERN", "TRAINEE")   # paper-tracked levels (TRADER+ -> live)
REGIME_GUARD_STATE = os.path.join(PATHS.results_dir, "regime_state.json")
REGIME_GUARD_APPROVAL = os.path.join(PATHS.results_dir,
                                     "regime_enforce_approved.json")
# T-21 (REGIME_ENFORCE_WIRING s3.1 gate 2): O-1325 condition-2 month-boundary
# lock -- HARD constant; paper-window dates on/after this day follow the v3
# enforce response matrix (when all three gates are open), earlier window
# dates stay legacy (no retroactive rewrite). Node self-rule excludes
# changing the month boundary.
ENFORCE_ACTIVE_FROM = "2026-10-01"
# T-20 PAPER_GUARD_DUAL_RAIL: forward-window execution-fidelity guard
# source (prereg s2: T-14 builder reuse mandatory, built fresh per run).
GUARD_SOURCE_LABEL = "t14_rules_fidelity.build_guard"

# registered entry expressions -> signal builder(P) where P = panels dict
# (composite rotation needs high/low/close); unknown key = hard abort
SIGNAL_BUILDERS = {
    "low_vol_long(n=60, top_k=5, daily)":
        lambda P: volatility.low_vol_long(P["close"], 60, top_k=5),
    "top_n_rotation(composite, n=5, rebal_days=20)":
        lambda P: top_n_rotation(P["high"], P["low"], P["close"],
                                 top_n=5, rebal_days=20),
    "top_n_rotation(composite, n=8, rebal_days=20)":
        lambda P: top_n_rotation(P["high"], P["low"], P["close"],
                                 top_n=8, rebal_days=20),
}


def _apply_sym(fn, P, keys, **kw):
    """Per-symbol state application (batch sym_panel convention): the
    per-symbol Series constructors are applied column-wise."""
    syms = list(P["close"].columns)
    return pd.DataFrame({s: fn(*[P[k][s] for k in keys], **kw)
                         for s in syms}).fillna(0)


# G2_FOLK registrants (2026-09-23, CEO order O-20260923-2210 chain)
SIGNAL_BUILDERS["engulf_reversal(drop_th=-0.05)"] = lambda P: _apply_sym(
    _ta_mod.engulf_reversal, P, ["open", "close"], drop_th=-0.05)
SIGNAL_BUILDERS["needle_probe(drop_th=-0.05, shadow_pct=0.02)"] = \
    lambda P: _apply_sym(
        _pt_mod.needle_probe, P, ["open", "high", "low", "close"],
        drop_th=-0.05, shadow_pct=0.02)
SIGNAL_BUILDERS["vol_drought_reversal(vol_floor=0.55, drop_th=-0.05)"] = \
    lambda P: _apply_sym(
        _pt_mod.vol_drought_reversal, P,
        ["open", "high", "low", "close", "volume"],
        vol_floor=0.55, drop_th=-0.05)

# T-24 PROSPECT candidate families (2026-09-24, ticket T-20260924-24
# slice-2): constructions VERBATIM from the frozen p4 batch cells
# (batch1 state panel / batch2a+folk+queue per-symbol convention); key
# strings carry the frozen params. These keys are consumed ONLY by the
# PROSPECT anchor-repro gate (scripts/t24_prospect_onboard.py via
# p3_portfolio.member_run) -- PROSPECT is not in PAPER_LEVELS, so the
# registered 6 composition stays byte-identical by construction.
SIGNAL_BUILDERS["oversold_bounce(lookback=20, drop=-15%, shrink=0.8)"] = \
    lambda P: ((P["close"].pct_change(20) < -0.15)
               & (P["amount"].rolling(5).mean()
                  < 0.8 * P["amount"].rolling(20).mean())
               ).fillna(False).astype(int)
SIGNAL_BUILDERS["rsrs_timing(18/250/0.8/-0.8)"] = lambda P: _apply_sym(
    _ta_mod.rsrs_timing, P, ["high", "low"])
SIGNAL_BUILDERS["vol_breakout(20/1.5/20/10)"] = lambda P: _apply_sym(
    _ta_mod.vol_breakout, P, ["high", "low", "close", "volume"])
SIGNAL_BUILDERS["hammer_reversal(classic, drop5, reclaim_ma20)"] = \
    lambda P: _apply_sym(
        _ta_mod.hammer_reversal, P, ["open", "high", "low", "close"])
SIGNAL_BUILDERS["three_methods_up()"] = lambda P: _apply_sym(
    _pt_mod.three_methods_up, P, ["open", "high", "low", "close"])
SIGNAL_BUILDERS["doji_at_low()"] = lambda P: _apply_sym(
    _pt_mod.doji_at_low, P, ["open", "high", "low", "close"])
SIGNAL_BUILDERS["inside_bar_breakup()"] = lambda P: _apply_sym(
    _pt_mod.inside_bar_breakup, P, ["open", "high", "low", "close"])
SIGNAL_BUILDERS["ma_converge_break()"] = lambda P: _apply_sym(
    _pt_mod.ma_converge_break, P, ["open", "high", "low", "close"])
SIGNAL_BUILDERS["duck_head()"] = lambda P: _apply_sym(
    _pt_mod.duck_head, P, ["open", "high", "low", "close"])
SIGNAL_BUILDERS["immortal_guide()"] = lambda P: _apply_sym(
    _pt_mod.immortal_guide, P, ["open", "high", "low", "close"])
SIGNAL_BUILDERS["ants_climb()"] = lambda P: _apply_sym(
    _fk_mod.ants_climb, P, ["open", "high", "low", "close"])
SIGNAL_BUILDERS["bb_squeeze_breakout()"] = lambda P: _apply_sym(
    _ta_mod.bb_squeeze_breakout, P, ["high", "low", "close"])


def load_core(min_listing_days: int = 60) -> dict:
    """Core-48 bare-code universe (mirror of combined_exit_screen.load_core)."""
    out = {}
    daily = PATHS.daily_dir
    for f in sorted(os.listdir(daily)):
        if not (f.endswith(".csv") and f[:-4].isdigit()):
            continue
        df = pd.read_csv(os.path.join(daily, f), parse_dates=["date"])
        df = df.set_index("date").sort_index()
        if len(df) < min_listing_days:
            continue
        if "open" not in df.columns:
            df["open"] = df["close"]
        if "amount" not in df.columns:
            df["amount"] = df["volume"] * df["close"]
        out[f[:-4]] = df[["open", "high", "low", "close", "volume", "amount"]]
    return out


def build_panels(prices: dict) -> dict:
    return {f: pd.DataFrame({s: df[f] for s, df in prices.items()})
            .sort_index().ffill()
            for f in ["open", "high", "low", "close", "volume", "amount"]}


class ExitPatch:
    """Runtime ExitConfig factory patch: inject NON-bridged exit fields.

    Engine builds ExitConfig from params-bridge kwargs only; fields the
    bridge cannot reach are injected here. Bridge kwargs WIN over patch
    fields. Exit-rule PRIORITY untouched; engine files untouched.
    """

    def __init__(self, overrides: dict | None):
        self.overrides = overrides or {}
        self.orig = None

    def __enter__(self):
        if not self.overrides:
            return self
        self.orig = _eb.ExitConfig
        Orig, ov = self.orig, self.overrides

        def factory(**kw):
            return Orig(**{**ov, **kw})

        _eb.ExitConfig = factory
        return self

    def __exit__(self, *exc):
        if self.orig is not None:
            _eb.ExitConfig = self.orig
        return False


# CostPatch -> single source scripts/science_gates.py (T-03-F12;
# re-exported via the module-level import above for live.paper importers)


def self_test_patches() -> bool:
    """Gate: patches must bite AND restore (G2 lesson 6.1)."""
    ok = True
    with CostPatch(2):
        fee = _eb.FeeSchedule()
        rate = (fee.commission_rate + fee.handling_fee
                + fee.supervision_fee + fee.slippage_a)
        ok &= abs(rate - COST_X2_RATE) < 1e-6
    fee = _eb.FeeSchedule()
    rate = (fee.commission_rate + fee.handling_fee
            + fee.supervision_fee + fee.slippage_a)
    ok &= abs(rate - COST_X1_RATE) < 1e-6
    with ExitPatch({"loss_time_days": 16, "take_profit_fractions": (0.5, 1.0)}):
        cfg = _eb.ExitConfig(max_positions=7)
        ok &= cfg.loss_time_days == 16 and cfg.take_profit_fractions == (0.5, 1.0)
        ok &= cfg.max_positions == 7
        cfg2 = _eb.ExitConfig(take_profit_fractions=(1 / 3, 1 / 3, 1.0))
        ok &= cfg2.take_profit_fractions == (1 / 3, 1 / 3, 1.0)  # bridge kwarg WINS
        ok &= cfg2.loss_time_days == 16
    cfg = _eb.ExitConfig()
    ok &= cfg.loss_time_days == 8 and cfg.take_profit_fractions == (1 / 3, 1 / 3, 1.0)
    return bool(ok)


def seg_metrics(equity: pd.Series, start: str | None = None) -> dict:
    seg = equity[equity.index >= start] if start else equity
    if len(seg) < 20:
        # T-04 F4: explicit honesty, never fake zeros (a fake 0.0 sharpe
        # could spuriously match a near-zero registered evidence).
        return {"status": "insufficient_data", "bars": int(len(seg))}
    return {"sharpe": round(float(sharpe(seg)), 4),
            "annual_return": round(float(annual_return(seg)), 4),
            "max_drawdown": round(float(max_drawdown(seg)), 4)}


def anchor_seg_guard(got: dict) -> str | None:
    """Anchor-gate guard for F4: insufficient segments must yield an
    explicit honest not-ok, never a fake pass/fail via zero comparison."""
    for seg_name in ("in_sample", "out_sample"):
        m = got.get(seg_name, {})
        if m.get("status") == "insufficient_data":
            return (f"{seg_name} segment too short ({m['bars']} bars < 20): "
                    "anchor evidence not computable")
    return None


def _evidence_matches(got: dict, want: dict) -> bool:
    """got uses engine metric names; the registration JSON uses max_dd/annual."""
    want_dd = want.get("max_dd", want.get("max_drawdown"))
    want_ann = want.get("annual", want.get("annual_return"))
    return (abs(got["sharpe"] - want["sharpe"]) < ANCHOR_TOL
            and abs(got["max_drawdown"] - want_dd) < ANCHOR_TOL
            and abs(got["annual_return"] - want_ann) < ANCHOR_TOL
            and got["trades"] == want["trades"])


def evidence_cutoff(t: dict, prices_full: dict) -> str:
    """Data state the registered evidence was computed on.

    Stored field wins; fallback = last bar strictly before the trader was
    created (registrations run intraday on already-closed data).
    """
    ec = t.get("evidence_cutoff")
    if ec:
        return ec
    created = pd.Timestamp(t["created"])
    last = max(df.index[df.index < created].max() for df in prices_full.values())
    return str(last.date())


def anchor_gate(t: dict, prices_full: dict) -> dict:
    """Reproduce the registered backtest evidence BEFORE any paper write."""
    entry_key = t["params"]["entry"]
    builder = SIGNAL_BUILDERS.get(entry_key)
    if builder is None:
        return {"ok": False, "error": f"entry not in SIGNAL_BUILDERS: {entry_key!r}"}
    cutoff = evidence_cutoff(t, prices_full)
    ps = pd.Timestamp(cutoff)
    prices = {s: df[df.index <= ps] for s, df in prices_full.items()}
    P = build_panels(prices)
    idx = P["close"].index
    entry = builder(P)
    params = {k: v for k, v in t["params"].items() if k != "entry"}
    with ExitPatch(t.get("exit_overrides")):
        res = run_backtest(prices, params, entry_signal=entry,
                           exit_signal=(entry <= 0))
    eq = pd.Series(res["equity_curve"], index=idx[:len(res["equity_curve"])])
    n_trades = res["metrics"]["num_trades"]
    oos_trades = sum(1 for tr in res["trades"] if str(tr["date"]) >= OOS_START)
    got = {"in_sample": {**seg_metrics(eq[eq.index < OOS_START]),
                         "trades": n_trades - oos_trades},
           "out_sample": {**seg_metrics(eq, OOS_START), "trades": oos_trades}}
    guard = anchor_seg_guard(got)
    if guard is not None:
        return {"ok": False, "cutoff": cutoff, "error": guard}
    want = t["backtest"]
    checks = {"in_sample": _evidence_matches(got["in_sample"], want["in_sample"]),
              "out_sample": _evidence_matches(got["out_sample"], want["out_sample"])}
    return {"ok": all(checks.values()), "cutoff": cutoff, "got": got,
            "checks": checks}


def monthly_aggregate(equity: pd.Series | None, initial_cash: float,
                      paper_start: str) -> dict:
    """Calendar-month paper evidence.

    A month is tracked iff FULL from hire (first day >= paper_start) AND
    fully elapsed by the data cutoff. The hire stub-month never counts.
    Returns are mark-to-market month over month (base = previous month's
    last equity, or initial_cash for the first observed month).
    """
    zero = {"months_tracked": 0, "monthly_returns": [], "current_dd": 0.0,
            "months_detail": [], "bars": 0, "last_bar": None}
    if equity is None or len(equity) == 0:
        return zero
    cutoff = equity.index[-1].date()
    ps = dt.date.fromisoformat(paper_start)
    cutoff_m = dt.date(cutoff.year, cutoff.month, 1)
    detail, rets = [], []
    base = float(initial_cash)
    dd = float(max_drawdown(equity))
    for (y, m), seg in equity.groupby([equity.index.year, equity.index.month]):
        month_first = dt.date(y, m, 1)
        month_ended = month_first < cutoff_m
        full = month_first >= ps
        ret = round(float(seg.iloc[-1]) / base - 1, 4)
        detail.append({"month": f"{y}-{m:02d}", "return": ret,
                       "bars": int(len(seg)), "month_ended": bool(month_ended),
                       "full_from_hire": bool(full),
                       "counted": bool(month_ended and full)})
        if month_ended and full:
            rets.append(ret)
        base = float(seg.iloc[-1])
    return {"months_tracked": len(rets), "monthly_returns": rets,
            "current_dd": round(dd, 4), "months_detail": detail,
            "bars": int(len(equity)), "last_bar": str(cutoff)}


def paper_run(t: dict, prices_full: dict, P: dict,
              regime_mask: dict | None = None,
              fill_guard: dict | None = None) -> dict:
    """Fresh-portfolio paper window from hire date, closed bars only.

    Signal is computed on the full close history (warmup lookback uses
    PAST closes); the engine only trades window dates (its _injected
    reindexes the signal frame to engine dates -- pre-hire rows never
    enter the engine loop).

    T-21 regime_mask (None = legacy, zero change): dict from
    _enforce_mask -- buy_fillable gates new-entry FILLS (P4-B2 drop
    semantics, exits untouched), scale halves YELLOW-day nominals.

    T-20 PAPER_GUARD_DUAL_RAIL B-rail (None = legacy, zero change): dict
    from scripts/t14_rules_fidelity.build_guard -- {"buy": DF, "sell": DF}.
    Engine consumption = P4-B2 verbatim: buy=False exec day -> pending
    order DROPPED; sell=False exit day -> deferred to the next fillable
    close with the ORIGINAL action. Composition with regime_mask: buy
    blocked iff EITHER face blocks; sell = guard only (the T-21 response
    matrix never touches exits).
    """
    entry = SIGNAL_BUILDERS[t["params"]["entry"]](P)
    ps = pd.Timestamp(t["created"])
    n_bars = int((P["close"].index >= ps).sum())
    if n_bars == 0:
        return {"bars": 0, "equity": None, "metrics": None, "trades": []}
    window = {s: df[df.index >= ps] for s, df in prices_full.items()}
    params = {k: v for k, v in t["params"].items() if k != "entry"}
    guard = None
    scale = None
    if regime_mask is not None:
        guard = {"buy": pd.DataFrame(
            {s: regime_mask["buy_fillable"] for s in window})}
        scale = regime_mask["scale"]
    if fill_guard is not None:
        widx = P["close"].index[P["close"].index >= ps]
        cols = list(window)
        gbuy = fill_guard["buy"].reindex(
            index=widx, columns=cols).fillna(True)
        gsell = fill_guard["sell"].reindex(
            index=widx, columns=cols).fillna(True)
        if guard is None:
            guard = {"buy": gbuy, "sell": gsell}
        else:
            # T-20 x T-21 composition: buy blocked iff either face blocks
            guard = {"buy": gbuy & guard["buy"].reindex(
                index=widx, columns=cols).fillna(True),
                "sell": gsell}
    with ExitPatch(t.get("exit_overrides")):
        res = run_backtest(window, params, entry_signal=entry,
                           exit_signal=(entry <= 0),
                           fill_guard=guard, entry_size_scale=scale)
    idx = P["close"].index
    widx = idx[idx >= ps][:len(res["equity_curve"])]
    eq = pd.Series(res["equity_curve"], index=widx)
    return {"bars": n_bars, "equity": eq, "metrics": res["metrics"],
            "trades": res["trades"],
            "open_positions": res.get("open_positions", [])}


def load_vi_bar():
    try:
        p = os.path.join(PATHS.results_dir, "p2_calibration.json")
        with open(p, encoding="utf-8") as fh:
            return json.load(fh)["g1_prime_gate"]["vi_full_sharpe_gt"]
    except Exception:
        return None


def cost_x2_check(t: dict, prices_full: dict, P: dict, vi_bar,
                  fill_guard: dict | None = None) -> dict:
    """Rolling x2-cost safety check on the paper window to date.

    Guarded: not enough bars -> insufficient_data, never a fake verdict.
    vi_bar unavailable is an ALARM, never a silent skip (T-04 F3).
    T-20 B-rail: the ROLLING recompute leg runs guarded (same window
    semantics as paper_run); the x2 REGISTRATION seed stays legacy (it is
    read from the trader JSON, never recomputed here).
    """
    ps = pd.Timestamp(t["created"])
    n_bars = int((P["close"].index >= ps).sum())
    if n_bars < MIN_BARS_COST_CHECK:
        return {"status": "insufficient_data", "bars": n_bars,
                "min_bars": MIN_BARS_COST_CHECK}
    if vi_bar is None:
        return {"status": "alarm_vi_bar_unavailable",
                "note": "p2_calibration.json vi_bar load failed -- x2 "
                        "safety check blinded, escalate (T-04 F3)"}
    entry = SIGNAL_BUILDERS[t["params"]["entry"]](P)
    window = {s: df[df.index >= ps] for s, df in prices_full.items()}
    params = {k: v for k, v in t["params"].items() if k != "entry"}
    with CostPatch(2), ExitPatch(t.get("exit_overrides")):
        res = run_backtest(window, params, entry_signal=entry,
                           exit_signal=(entry <= 0), fill_guard=fill_guard)
    s = res["metrics"]["sharpe"]
    return {"status": "ok", "paper_window_sharpe_x2": s,
            "skill_bar": vi_bar, "survive": bool(s > vi_bar),
            "margin": round(float(s - vi_bar), 4),
            "note": "rolling x2-cost safety on paper window to date"}


X2_PROBATION_MARGIN = 0.05


def x2_watch_verdict(x2: dict, seed: dict | None = None) -> dict:
    """T-04 F3 escalation chain (O-2205 promised watchdog).

    Non-surviving OR thin margin (< 0.05) -> probation. While the paper
    window is still immature (insufficient bars), the verdict is SEEDED
    from the registration-time cost_x2 evidence so razor-margin traders
    (e.g. +0.031/+0.002) are watched from day one, never naked.
    Report-only annotation: level authority stays with firm/hr.py.
    """
    if x2.get("status") == "ok":
        margin, survive = x2.get("margin"), bool(x2.get("survive"))
        thin = (margin is not None and margin < X2_PROBATION_MARGIN) or not survive
        return {"status": "probation" if thin else "ok",
                "probation": bool(thin), "margin": margin, "survive": survive,
                "source": "paper_window"}
    if seed and seed.get("sharpe") is not None and seed.get("vi_bar") is not None:
        margin = round(float(seed["sharpe"]) - float(seed["vi_bar"]), 4)
        survive = bool(seed.get("survive", margin > 0))
        thin = margin < X2_PROBATION_MARGIN or not survive
        return {"status": "probation" if thin else "ok",
                "probation": bool(thin), "margin": margin, "survive": survive,
                "source": "registration_x2_seed"}
    return {"status": x2.get("status", "unknown"), "probation": False}


def _append_x2_watch_log(entry: dict) -> None:
    """F3 ledger: one JSONL line per trader per paper run (append-only)."""
    p = os.path.join(PATHS.results_dir, "x2_watch_log.jsonl")
    with open(p, "a", encoding="utf-8") as fh:
        fh.write(json.dumps(entry, ensure_ascii=False, default=str) + "\n")


def _load_approval() -> dict | None:
    if not os.path.exists(REGIME_GUARD_APPROVAL):
        return None
    try:
        with open(REGIME_GUARD_APPROVAL, encoding="utf-8") as fh:
            appr = json.load(fh)
    except (OSError, ValueError):
        return None
    return appr if isinstance(appr, dict) else None


def v3_state_series() -> pd.Series:
    """T-21 s3.2: v3 state series via import-replay of the calibration
    primitives (frozen seed: init at last pre-2020 day, resolve_state_v3).
    Live data is re-replayed on every call -- no cache, no second state
    store (bit-consistency with the calibration batch is gate G2)."""
    bench = build_bench()
    ds = bench_dim_series(bench)
    br = breadth_series(bench)
    raw = raw_series(bench, ds, br, level_fn=raw_level_v3)
    states, _streaks, _init = state_replay(bench, raw,
                                           resolver=resolve_state_v3)
    return pd.Series(states).sort_index()


def _enforce_mask(states: pd.Series, panel_index: pd.DatetimeIndex,
                  active_from: str = ENFORCE_ACTIVE_FROM) -> dict:
    """T-21 s3.3: response-matrix mask for the paper window.

    Decision causality (no look-ahead): the state known at exec day E's
    open is the state resolved at the PRIOR close (E-1). buy_fillable(E)
    = state(E-1) not in {ORANGE, RED}; scale(E) = 0.5 iff state(E-1) ==
    YELLOW else 1.0. The matrix applies to exec days ON/after active_from
    only -- earlier window dates stay legacy (single semantics switch
    point, no retroactive rewrite; deterministic on every rerun).

    states are resolved on bench (510300) dates; panel-only dates (a
    bench date absent from the panel) inherit the last known state -- the
    state machine is a step function, ffill is its persistence, disclosed.
    """
    af = pd.Timestamp(active_from)
    st = states.reindex(panel_index).ffill()
    blocked = st.isin(["ORANGE", "RED"])          # decision-day state
    yellow = st == "YELLOW"
    # decision day T -> execution day T+1 (next panel row): shift(1);
    # first row has no prior decision -> not blocked / scale 1.0.
    blocked_exec = blocked.shift(1, fill_value=False)
    yellow_exec = yellow.shift(1, fill_value=False)
    on_or_after = pd.Series(panel_index >= af, index=panel_index)
    blocked_exec = (blocked_exec & on_or_after).astype(bool)
    yellow_exec = (yellow_exec & on_or_after).astype(bool)
    scale = pd.Series(1.0, index=panel_index)
    scale[yellow_exec] = 0.5
    return {"buy_fillable": (~blocked_exec).astype(bool),
            "scale": scale,
            "yellow_exec_days": int(yellow_exec.sum()),
            "blocked_exec_days": int(blocked_exec.sum())}


def regime_guard_context(mode: str | None = None) -> dict:
    """T-05 (3) + T-21 additive upgrade: regime-guard context for paper.

    'shadow' (default; env BIGMONEY_REGIME_GUARD): log-only -- the block
    rides along in results/paper/<TID>_paper.json, ZERO behavior change
    (engine, sizing, entries, anchor gate untouched).
    'enforce' (T-21 s3.1 three-gate): legal state since O-20260924-1325
    (CEO approved the v3 enforce proposal; approval file
    results/regime_enforce_approved.json delivered with T-21). Gates:
      1. approval file present with calibration_pass AND gm_approval;
      2. date gate ENFORCE_ACTIVE_FROM (2026-10-01) -- enforced per
         window exec date by _enforce_mask; requests whose whole window
         predates the gate = honest downgrade to shadow + gate_note;
      3. env BIGMONEY_REGIME_GUARD stays the request channel -- default
         'shadow' keeps every machine without the env at zero change.
    The pre-T-21 double-refusal ('approved but wiring is a separate signed
    item') is SUPERSEDED by the batch per prereg s3.1."""
    mode = mode or os.environ.get("BIGMONEY_REGIME_GUARD", "shadow")
    if mode not in ("shadow", "enforce"):
        raise SystemExit(f"regime_guard: unknown mode {mode!r} (shadow|enforce)")
    if mode == "enforce":
        appr = _load_approval()
        if not (appr and appr.get("calibration_pass")
                and appr.get("gm_approval")):
            raise SystemExit(
                "regime_guard enforce REFUSED: requires calibration PASS + GM "
                "approval (results/regime_enforce_approved.json; "
                "calibration_pass + gm_approval). Absent/incomplete approval "
                "-> enforce stays OFF (REGIME_GUARD s3 / T-21 gate 1).")
        return {"mode": "enforce", "approved": True,
                "active_from": ENFORCE_ACTIVE_FROM,
                "note": "v3 response matrix wired (T-21); per-date semantics "
                        "governed by the date gate -- pre-active_from window "
                        "dates stay legacy"}
    st = {}
    if os.path.exists(REGIME_GUARD_STATE):
        try:
            with open(REGIME_GUARD_STATE, encoding="utf-8") as fh:
                st = json.load(fh)
        except (OSError, ValueError):
            st = {}
    return {"mode": "shadow", "state": st.get("state"),
            "state_cn": st.get("state_cn"), "asof": st.get("asof"),
            "raw_level": st.get("raw_level"),
            "days_in_state": st.get("days_in_state"),
            "note": "shadow = log-only; enforce needs calibration PASS + "
                    "GM approval (T-05)"}


def update_trader(t: dict, prices_full: dict, P: dict, vi_bar,
                  data_cutoff: str, regime: dict,
                  rg: dict | None = None, regime_mask: dict | None = None,
                  v3_states: pd.Series | None = None,
                  fill_guard: dict | None = None) -> dict:
    """Full pipeline for one trader. Returns the state dict; writes only
    when the anchor gate passes (trader JSON never touched on drift).

    T-21 A-track iron law: anchor_gate and cost_x2_check NEVER receive
    regime_mask / any masking (registration-frame comparisons stay
    same-frame); x2 registration-period seed stays legacy. Only the
    paper_run accounting window carries the enforce response matrix.
    T-20 B-rail: fill_guard reaches paper_run and the cost_x2_check
    ROLLING leg only; anchor_gate NEVER receives it (A-rail verbatim);
    the x2 registration seed stays legacy (read, never recomputed).
    """
    anchor = anchor_gate(t, prices_full)
    if not anchor["ok"]:
        return {"trader": t["id"], "anchor_ok": False, "anchor": anchor}
    run = paper_run(t, prices_full, P, regime_mask=regime_mask,
                    fill_guard=fill_guard)
    agg = monthly_aggregate(run["equity"], INITIAL_CASH, t["created"])
    x2 = cost_x2_check(t, prices_full, P, vi_bar, fill_guard=fill_guard)
    bt_x2 = (t.get("backtest") or {}).get("cost_x2") or {}
    seed = ({"sharpe": bt_x2.get("sharpe"), "vi_bar": vi_bar,
             "survive": bt_x2.get("survive")}
            if (bt_x2.get("sharpe") is not None and vi_bar is not None) else None)
    watch = x2_watch_verdict(x2, seed=seed)
    _append_x2_watch_log({"ts": time.strftime("%Y-%m-%d %H:%M:%S"),
                          "trader": t["id"],
                          "window_semantics":
                          "guarded" if fill_guard is not None else "legacy",
                          **watch})
    m_run = run["metrics"] or {}
    forward_guard = {
        "enabled": fill_guard is not None,
        "guard_source": (GUARD_SOURCE_LABEL
                        if fill_guard is not None else None),
        "buy_rejected_n": int(m_run.get("fill_guard_buy_dropped", 0)),
        "sell_deferred_events_n":
            int(m_run.get("fill_guard_sell_deferred_events", 0)),
        "deferred_days_total":
            int(m_run.get("fill_guard_deferred_days_total", 0)),
        "first_deferred_date": m_run.get("fill_guard_first_deferred_date"),
        "window_semantics":
            "guarded" if fill_guard is not None else "legacy",
        "as_of": time.strftime("%Y-%m-%d %H:%M:%S"),
    }
    if regime_mask is not None:
        forward_guard["note"] = ("composition: buy_rejected_n may include "
                                  "T-21 regime-matrix drops (guard faces "
                                  "ANDed on the buy leg)")
    # T-35 (O-2045 s1.4/s2): CNY capital + open-positions faces, additive
    # to the state JSON (consumed by the intraday marking lane, the daily
    # export and T-29); marks use the last CLOSE bar -- intraday re-marks
    # are the marking lane's job, never backdated here.
    last_close = P["close"].iloc[-1] if len(P["close"]) else None
    pos_face = []
    for p in run.get("open_positions", []):
        sym = p["symbol"]
        lc = (float(last_close[sym])
              if last_close is not None and sym in last_close.index else None)
        pos_face.append({**p,
                         "last_close": round(lc, 4) if lc is not None else None,
                         "market_value_cny":
                             round(p["quantity"] * lc, 2) if lc else None,
                         "unrealized_pnl_cny":
                             round((lc - p["cost_price"]) * p["quantity"], 2)
                             if lc else None})
    eq_end = (float(run["equity"].iloc[-1])
              if run["equity"] is not None and len(run["equity"]) else 0.0)
    pos_val = round(sum(pf["market_value_cny"] or 0.0 for pf in pos_face), 2)
    capital_block = {
        "initial_cash_cny": INITIAL_CASH,
        "equity_cny": round(eq_end, 2),
        "positions_value_cny": pos_val,
        "cash_cny": round(eq_end - pos_val, 2),
        "cash_derivation": "equity - positions mark (paper plane runs no "
                           "parking leg; T-09 cash_parking never wired here)",
        "denomination": "CNY",
    }
    t["paper"] = {"months_tracked": agg["months_tracked"],
                  "monthly_returns": agg["monthly_returns"],
                  "current_dd": agg["current_dd"],
                  "as_of": time.strftime("%Y-%m-%d"),
                  "cutoff": data_cutoff,
                  "x2_watch": {**watch,
                               "as_of": time.strftime("%Y-%m-%d")}}
    save_trader(t)
    guard_block = (rg if rg is not None else
                   {"mode": "shadow", "state": None,
                    "note": "context unavailable (T-05 default block)"})
    if regime_mask is not None:
        # T-21 s3.4 dual-track block: enforced counters + shadow reference.
        af = pd.Timestamp(ENFORCE_ACTIVE_FROM)
        widx = P["close"].index
        wd = widx[widx >= pd.Timestamp(t["created"])]
        m = run["metrics"] or {}
        days_enforced = int((wd >= af).sum())
        tail = None
        if v3_states is not None and len(wd):
            tail_s = v3_states.reindex(wd).ffill()
            tail = {str(d.date()): s for d, s in tail_s.tail(10).items()}
        sh = (rg if isinstance(rg, dict) and rg.get("mode") == "shadow"
              else {})
        guard_block = {
            "mode": "enforce", "active": bool(days_enforced > 0),
            "active_from": ENFORCE_ACTIVE_FROM,
            "gate_note": None if days_enforced else
                f"date gate not yet open (active_from={ENFORCE_ACTIVE_FROM}) "
                "-- window exec dates all legacy, honest downgrade to "
                "shadow semantics",
            "v3_state_tail": tail,
            "enforced": {"active_from": ENFORCE_ACTIVE_FROM,
                         "days_enforced": days_enforced,
                         "entries_blocked": m.get("fill_guard_buy_dropped", 0),
                         "entries_halved": m.get("scaled_entries", 0)},
            "shadow_ref": {"state": sh.get("state"),
                           "asof": sh.get("asof")},
            "note": "v3-enforced paper window (T-21); exits never forced; "
                    "RED new-cash parking is structurally inert in paper "
                    "(fixed INITIAL_CASH) -- live-gate concern, disclosed"}
    return {"trader": t["id"], "anchor_ok": True, "anchor": anchor,
            "paper_start": t["created"], "bars": agg["bars"],
            "months_tracked": agg["months_tracked"],
            "monthly_returns": agg["monthly_returns"],
            "current_dd": agg["current_dd"], "months_detail": agg["months_detail"],
            "window_metrics": run["metrics"], "cost_x2_check": x2,
            "x2_watch": watch,
            "cutoff": data_cutoff, "updated": time.strftime("%Y-%m-%d %H:%M:%S"),
            "risk_regime": {"is_major_bear": regime["is_major_bear"],
                            "position_cap": regime["position_cap"],
                            "as_of": regime["as_of"]},
            "regime_guard": guard_block,
            "forward_guard": forward_guard,
            "open_positions": pos_face,
            "capital": capital_block,
            "no_future_data": "closed bars only; signal T close -> T+1 open "
                              "(engine contract)"}


def _ramp_month(base: float, target: float, year: int, month: int) -> pd.Series:
    """Synthetic straight-line month equity for aggregation unit tests."""
    idx = pd.bdate_range(f"{year}-{month:02d}-01", f"{year}-{month:02d}-28")
    vals = [base + (target - base) * i / (len(idx) - 1) for i in range(len(idx))]
    return pd.Series(vals, index=idx)


def _selftest_aggregation() -> bool:
    initial = 1_000_000.0
    jan = _ramp_month(initial, initial * 1.02, 2026, 1)
    feb = _ramp_month(initial * 1.02, initial * 0.98, 2026, 2)
    mar = _ramp_month(initial * 0.98, initial * 1.01, 2026, 3)
    feb_ret = round(0.98 / 1.02 - 1, 4)
    dd_exp = round(0.98 / 1.02 - 1, 4)
    ok = True

    # A: full months Jan-Mar, cutoff inside March -> Jan/Feb tracked, Mar open
    a = monthly_aggregate(pd.concat([jan, feb, mar]), initial, "2025-12-01")
    ok &= a["months_tracked"] == 2 and a["monthly_returns"] == [0.02, feb_ret]
    ok &= a["current_dd"] == dd_exp and a["months_detail"][-1]["counted"] is False

    # B: hired mid-Jan -> stub month never counts (no promotion gaming)
    b = monthly_aggregate(pd.concat([jan, feb, mar]), initial, "2026-01-15")
    ok &= b["months_tracked"] == 1 and b["monthly_returns"] == [feb_ret]
    ok &= b["months_detail"][0]["full_from_hire"] is False

    # C: cutoff end of Feb -> only Jan tracked
    c = monthly_aggregate(pd.concat([jan, feb]), initial, "2025-12-01")
    ok &= c["months_tracked"] == 1 and c["monthly_returns"] == [0.02]

    # D: zero-bar window (hire after data cutoff) -> legal zero, no crash
    d = monthly_aggregate(None, initial, "2026-09-23")
    ok &= d["months_tracked"] == 0 and d["monthly_returns"] == [] \
        and d["current_dd"] == 0.0
    return bool(ok)


def _selftest_seg_metrics() -> bool:
    """F4: short segment -> explicit insufficient_data (no fake zeros);
    normal segment -> metrics keys, no status key; guard maps to honest
    not-ok error string."""
    ok = True
    full_month = _ramp_month(1.0, 1.1, 2026, 1)
    short = seg_metrics(full_month.iloc[:19])
    ok &= (short.get("status") == "insufficient_data"
           and short.get("bars") == 19 and "sharpe" not in short)
    full = seg_metrics(full_month)
    ok &= ("sharpe" in full and "status" not in full
           and abs(full["sharpe"] - round(float(sharpe(full_month)), 4)) < 1e-12)
    # exactly at the boundary is computable (>= 20)
    ok &= seg_metrics(full_month.iloc[:20]).get("status") is None
    err = anchor_seg_guard({"in_sample": {"sharpe": 0.5, "annual_return": 0.1,
                                          "max_drawdown": -0.05},
                            "out_sample": {"status": "insufficient_data",
                                           "bars": 12}})
    ok &= err is not None and "out_sample segment too short (12 bars" in err
    ok &= anchor_seg_guard({"in_sample": {"sharpe": 0.5},
                            "out_sample": {"sharpe": 0.4}}) is None
    return bool(ok)


def _selftest_x2_watch() -> bool:
    """F3: thin margin / non-survive -> probation; healthy -> ok;
    immature window seeded from registration x2 evidence (razor-margin
    traders watched from day one); non-ok statuses pass through, never
    fake-ok."""
    ok = True
    v = x2_watch_verdict({"status": "ok", "survive": True, "margin": 0.031})
    ok &= v["probation"] is True and v["status"] == "probation" \
        and v["source"] == "paper_window"
    v = x2_watch_verdict({"status": "ok", "survive": False, "margin": 0.20})
    ok &= v["probation"] is True and v["status"] == "probation"
    v = x2_watch_verdict({"status": "ok", "survive": True, "margin": 0.05})
    ok &= v["probation"] is False and v["status"] == "ok"   # boundary: not thin
    # immature window + razor registration margin (+0.002 like ENGULF) -> probation now
    v = x2_watch_verdict({"status": "insufficient_data", "bars": 3},
                         seed={"sharpe": 0.4020, "vi_bar": 0.4004, "survive": True})
    ok &= v["probation"] is True and v["status"] == "probation" \
        and v["source"] == "registration_x2_seed" and v["margin"] == 0.0016
    # immature window + healthy registration margin -> ok (seeded), not insufficient
    v = x2_watch_verdict({"status": "insufficient_data", "bars": 1},
                         seed={"sharpe": 0.5740, "vi_bar": 0.4004})
    ok &= v["probation"] is False and v["status"] == "ok" \
        and v["source"] == "registration_x2_seed"
    # alarm/unknown statuses never become fake-ok, seed or not
    v = x2_watch_verdict({"status": "alarm_vi_bar_unavailable"})
    ok &= v["probation"] is False and v["status"] == "alarm_vi_bar_unavailable"
    v = x2_watch_verdict({"status": "insufficient_data", "bars": 3}, seed=None)
    ok &= v["probation"] is False and v["status"] == "insufficient_data"
    v = x2_watch_verdict({})
    ok &= v["status"] == "unknown" and v["probation"] is False
    return bool(ok)


def _selftest_regime_guard() -> bool:
    """T-05 (3) + T-21: shadow block from synthetic state file; state-file
    absent honest; enforce three-gate resolution (no approval / incomplete
    approval = refuse; full approval = legal enforce context); mask
    builder shift/active-from/no-lookahead fixtures; unknown mode refused.
    Offline path-swap only (no data loads)."""
    import shutil
    import tempfile
    global REGIME_GUARD_STATE, REGIME_GUARD_APPROVAL
    real_state, real_appr = REGIME_GUARD_STATE, REGIME_GUARD_APPROVAL
    tmp = tempfile.mkdtemp(prefix="rg_ctx_st_")
    ok = True
    try:
        REGIME_GUARD_STATE = os.path.join(tmp, "regime_state.json")
        REGIME_GUARD_APPROVAL = os.path.join(tmp, "regime_enforce_approved.json")
        # A: no state file -> shadow block with state None, no crash
        blk = regime_guard_context()
        ok &= blk["mode"] == "shadow" and blk["state"] is None
        # B: state file present -> block carries state/asof verbatim
        with open(REGIME_GUARD_STATE, "w", encoding="utf-8") as fh:
            json.dump({"state": "ORANGE", "state_cn": "橙·高危",
                       "asof": "2026-09-23", "raw_level": "ORANGE",
                       "days_in_state": 1}, fh)
        blk = regime_guard_context()
        ok &= (blk["mode"] == "shadow" and blk["state"] == "ORANGE"
               and blk["asof"] == "2026-09-23" and blk["days_in_state"] == 1)
        # C: enforce without approval -> hard refuse (gate 1)
        try:
            regime_guard_context("enforce")
            ok &= False
        except SystemExit:
            pass
        # D (T-21): approval present but incomplete (gm_approval missing)
        # -> still refuse (gate 1 completeness)
        with open(REGIME_GUARD_APPROVAL, "w", encoding="utf-8") as fh:
            json.dump({"calibration_pass": True}, fh)
        try:
            regime_guard_context("enforce")
            ok &= False
        except SystemExit:
            pass
        # E (T-21 supersedes T-05 double-refusal): FULL approval ->
        # enforce is a legal context; date gate is per-window (main).
        with open(REGIME_GUARD_APPROVAL, "w", encoding="utf-8") as fh:
            json.dump({"calibration_pass": True, "gm_approval": True,
                       "active_from": ENFORCE_ACTIVE_FROM}, fh)
        blk = regime_guard_context("enforce")
        ok &= (blk["mode"] == "enforce" and blk["approved"] is True
               and blk["active_from"] == ENFORCE_ACTIVE_FROM)
        # F: unknown mode -> refuse
        try:
            regime_guard_context("banana")
            ok &= False
        except SystemExit:
            pass
        # G (T-21 s3.3 mask fixtures): decision-day state gates the NEXT
        # session's fill; matrix applies to exec days on/after active_from
        # only; first panel row has no prior decision -> never blocked.
        idx = pd.bdate_range("2026-09-25", "2026-10-09")
        states = pd.Series("GREEN", index=idx)
        states.loc["2026-09-28"] = "ORANGE"   # pre-gate decision -> pre-gate exec
        states.loc["2026-09-30"] = "ORANGE"   # pre-gate decision -> gate-day exec
        states.loc["2026-10-05"] = "YELLOW"   # post-gate yellow -> next-day x0.5
        m = _enforce_mask(states, idx, active_from="2026-10-01")
        ok &= bool(m["buy_fillable"].iloc[0])            # no prior decision
        ok &= bool(m["buy_fillable"].loc["2026-09-29"])   # pre-gate legacy
        ok &= not bool(m["buy_fillable"].loc["2026-10-01"])  # gate day, state ORANGE
        ok &= bool(m["scale"].loc["2026-09-29"] == 1.0)   # pre-gate nominal
        ok &= bool(m["scale"].loc["2026-10-06"] == 0.5)   # YELLOW decision 10-05
        ok &= m["blocked_exec_days"] == 1 and m["yellow_exec_days"] == 1
        # H: whole window pre-gate -> mask is an exact no-op (downgrade path)
        idx2 = pd.bdate_range("2026-09-23", "2026-09-30")
        m2 = _enforce_mask(pd.Series("ORANGE", index=idx2), idx2,
                           active_from="2026-10-01")
        ok &= (m2["blocked_exec_days"] == 0 and m2["yellow_exec_days"] == 0
               and bool(m2["buy_fillable"].all())
               and bool((m2["scale"] == 1.0).all()))
    finally:
        REGIME_GUARD_STATE, REGIME_GUARD_APPROVAL = real_state, real_appr
        shutil.rmtree(tmp, ignore_errors=True)
    return bool(ok)


def _selftest_causality(prices_full: dict) -> bool:
    """Every registered builder must be causal: truncating data at D
    leaves the signal on [.., D] unchanged (no look-ahead)."""
    P = build_panels(prices_full)
    cut = P["close"].index[len(P["close"].index) // 2]
    pc = {s: df[df.index <= cut] for s, df in prices_full.items()}
    Pp = build_panels(pc)
    ok = True
    for key, builder in SIGNAL_BUILDERS.items():
        full = builder(P)
        part = builder(Pp)
        ok &= bool(part.equals(full[full.index <= cut]))
    return bool(ok)


def selftest() -> bool:
    """Patch bite/restore + aggregation math + signal causality + anchor
    gate on all registered paper-level traders (real data, ~seconds)."""
    print("  [paper] patch self-tests...", end=" ")
    ok = self_test_patches()
    print("PASS" if ok else "FAIL")

    print("  [paper] monthly aggregation unit tests...", end=" ")
    agg_ok = _selftest_aggregation()
    print("PASS" if agg_ok else "FAIL")
    ok &= agg_ok

    print("  [paper] seg_metrics short-segment honesty (F4)...", end=" ")
    seg_ok = _selftest_seg_metrics()
    print("PASS" if seg_ok else "FAIL")
    ok &= seg_ok

    print("  [paper] x2 watch escalation chain (F3)...", end=" ")
    w_ok = _selftest_x2_watch()
    print("PASS" if w_ok else "FAIL")
    ok &= w_ok

    print("  [paper] regime_guard additive flag (T-05)...", end=" ")
    rg_ok = _selftest_regime_guard()
    print("PASS" if rg_ok else "FAIL")
    ok &= rg_ok
    if not ok:
        return False

    print("  [paper] loading universe for causality + anchor gates...")
    prices_full = load_core()
    print("  [paper] signal causality (truncate-and-compare)...", end=" ")
    causal = _selftest_causality(prices_full)
    print("PASS" if causal else "FAIL")
    ok &= causal

    n = 0
    for path in sorted(TRADERS_DIR.glob("*.json")):
        if path.name.startswith("_"):
            continue
        t = load_trader(path.stem)
        if t.get("level") not in PAPER_LEVELS:
            continue
        n += 1
        print(f"  [paper] anchor gate {t['id']}...", end=" ")
        a = anchor_gate(t, prices_full)
        g = a.get("got", {})
        if a["ok"]:
            print(f"PASS (IS s={g['in_sample']['sharpe']} "
                  f"OOS s={g['out_sample']['sharpe']}, cutoff {a['cutoff']})")
        else:
            print(f"FAIL {a.get('checks') or a.get('error')}")
        ok &= a["ok"]
    if n == 0:
        print("  [paper] no paper-level traders registered (anchor vacuous)")
    return bool(ok)


def main(argv=None) -> int:
    argv = sys.argv[1:] if argv is None else argv
    if "--selftest" in argv:
        return 0 if selftest() else 1

    print(f"=== Bigmoney paper tracking {time.strftime('%Y-%m-%d %H:%M:%S')} ===")
    if not self_test_patches():
        print("patch self-test FAILED -- abort (fake-evidence guard)")
        return 2
    prices_full = load_core()
    P = build_panels(prices_full)
    data_cutoff = str(P["close"].index[-1].date())
    vi_bar = load_vi_bar()
    regime = regime_report()   # R-配3 portfolio gate context (O-1820), report-only in paper domain
    rg = regime_guard_context()   # T-05 (3) + T-21: shadow default / enforce 3-gate
    rg_shadow = (regime_guard_context("shadow") if rg.get("mode") == "enforce"
                 else rg)          # T-21 s3.4: v1 live state for shadow_ref
    regime_mask = None
    v3_states = None
    if rg.get("mode") == "enforce":
        af = pd.Timestamp(ENFORCE_ACTIVE_FROM)
        if P["close"].index[-1] < af:
            # date gate not yet open for the whole window: honest downgrade
            # -- pure legacy call (byte-identical accounting), block records it.
            rg = dict(rg, active=False,
                      enforced={"active_from": ENFORCE_ACTIVE_FROM,
                               "days_enforced": 0, "entries_blocked": 0,
                               "entries_halved": 0},
                      gate_note=f"date gate not yet open "
                      f"(active_from={ENFORCE_ACTIVE_FROM}) -- downgrade to "
                      "shadow semantics until the window reaches the gate")
            print(f"regime_guard: enforce requested, DOWNGRADED to shadow "
                  f"semantics (date gate {ENFORCE_ACTIVE_FROM})")
        else:
            v3_states = v3_state_series()
            regime_mask = _enforce_mask(v3_states, P["close"].index)
            print(f"regime_guard: ENFORCE active from {ENFORCE_ACTIVE_FROM} "
                  f"(window masked exec days: blocked="
                  f"{regime_mask['blocked_exec_days']}, yellow="
                  f"{regime_mask['yellow_exec_days']})")
    print(f"universe: {len(prices_full)} ETFs, data through {data_cutoff}")
    # T-20 B-rail: guard built FRESH each run (seconds; no cache -- prereg
    # s2 reuse-bar). Lazy import: t14_rules_fidelity imports live.paper.
    from scripts.t14_rules_fidelity import build_guard
    fill_guard, guard_diag = build_guard(prices_full)
    gtot = guard_diag["totals"]
    print(f"forward_guard: {GUARD_SOURCE_LABEL} wired (board-seal up="
          f"{gtot['buy_blocked']} dn={gtot['sell_blocked']} "
          f"susp={gtot['susp']})")
    print(f"regime: major_bear={regime['is_major_bear']} "
          f"cap={regime['position_cap']} (close<MA250={regime['below_ma250']}, "
          f"dd={regime['dd_from_250d_high']})")
    print(f"regime_guard: {rg['mode']}"
          + (f" state={rg.get('state')} asof={rg.get('asof')}"
             if rg.get("mode") == "shadow" else
             (f" active_from={ENFORCE_ACTIVE_FROM}"
              f" active={rg.get('active', True)}")))

    ok_all = True
    paper_dir = os.path.join(PATHS.results_dir, "paper")
    os.makedirs(paper_dir, exist_ok=True)
    for path in sorted(TRADERS_DIR.glob("*.json")):
        if path.name.startswith("_"):
            continue
        t = load_trader(path.stem)
        if t.get("level") not in PAPER_LEVELS:
            continue
        state = update_trader(t, prices_full, P, vi_bar, data_cutoff, regime,
                              rg_shadow if regime_mask is not None else rg,
                              regime_mask=regime_mask, v3_states=v3_states,
                              fill_guard=fill_guard)
        if not state["anchor_ok"]:
            ok_all = False
            print(f"{t['id']}: ANCHOR DRIFT -- trader JSON untouched")
            print(f"  checks: {state['anchor'].get('checks')}"
                  f"{state['anchor'].get('error', '')}")
            continue
        sp = os.path.join(paper_dir, f"{t['id']}_paper.json")
        with open(sp, "w", encoding="utf-8") as fh:
            json.dump(state, fh, indent=2, ensure_ascii=False, default=str)
        print(f"{t['id']}: anchor OK (cutoff {state['anchor']['cutoff']}) | "
              f"paper {state['bars']} bars since {state['paper_start']} | "
              f"months_tracked={state['months_tracked']} "
              f"dd={state['current_dd']} | x2: {state['cost_x2_check']['status']}"
              f" | x2 watch: {state['x2_watch']['status']}"
              + (f" margin {state['x2_watch']['margin']}" if state['x2_watch'].get('probation') else "")
              + (" [PROBATION]" if state['x2_watch'].get('probation') else "")
              + f" | saved {sp}")
    print("paper tracking:", "OK" if ok_all else "FAILED")
    return 0 if ok_all else 1


if __name__ == "__main__":
    sys.exit(main())
