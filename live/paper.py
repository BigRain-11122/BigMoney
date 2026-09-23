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
import strategies.patterns as _pt_mod
import strategies.ta as _ta_mod
from scripts.science_gates import COST_X2_RATE, CostPatch  # T-03-F12 single source (re-exported for lfc/p3 importers)

OOS_START = "2025-01-01"        # registered evidence segment split (J7+)
ANCHOR_TOL = 0.002             # project standard (J14/J15)
COST_X1_RATE = 0.0013041       # G2-recorded baseline single-side cost
MIN_BARS_COST_CHECK = 20       # cost-x2 verdict needs a real window
INITIAL_CASH = 1_000_000.0     # engine default (anchor + paper same)
PAPER_LEVELS = ("INTERN", "TRAINEE")   # paper-tracked levels (TRADER+ -> live)
REGIME_GUARD_STATE = os.path.join(PATHS.results_dir, "regime_state.json")
REGIME_GUARD_APPROVAL = os.path.join(PATHS.results_dir,
                                     "regime_enforce_approved.json")

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


def paper_run(t: dict, prices_full: dict, P: dict) -> dict:
    """Fresh-portfolio paper window from hire date, closed bars only.

    Signal is computed on the full close history (warmup lookback uses
    PAST closes); the engine only trades window dates (its _injected
    reindexes the signal frame to engine dates -- pre-hire rows never
    enter the engine loop).
    """
    entry = SIGNAL_BUILDERS[t["params"]["entry"]](P)
    ps = pd.Timestamp(t["created"])
    n_bars = int((P["close"].index >= ps).sum())
    if n_bars == 0:
        return {"bars": 0, "equity": None, "metrics": None, "trades": []}
    window = {s: df[df.index >= ps] for s, df in prices_full.items()}
    params = {k: v for k, v in t["params"].items() if k != "entry"}
    with ExitPatch(t.get("exit_overrides")):
        res = run_backtest(window, params, entry_signal=entry,
                           exit_signal=(entry <= 0))
    idx = P["close"].index
    widx = idx[idx >= ps][:len(res["equity_curve"])]
    eq = pd.Series(res["equity_curve"], index=widx)
    return {"bars": n_bars, "equity": eq, "metrics": res["metrics"],
            "trades": res["trades"]}


def load_vi_bar():
    try:
        p = os.path.join(PATHS.results_dir, "p2_calibration.json")
        with open(p, encoding="utf-8") as fh:
            return json.load(fh)["g1_prime_gate"]["vi_full_sharpe_gt"]
    except Exception:
        return None


def cost_x2_check(t: dict, prices_full: dict, P: dict, vi_bar) -> dict:
    """Rolling x2-cost safety check on the paper window to date.

    Guarded: not enough bars -> insufficient_data, never a fake verdict.
    vi_bar unavailable is an ALARM, never a silent skip (T-04 F3).
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
                           exit_signal=(entry <= 0))
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


def regime_guard_context(mode: str | None = None) -> dict:
    """T-05 deliverable (3): additive regime-guard context for paper state.

    'shadow' (default; env BIGMONEY_REGIME_GUARD): log-only -- the block
    rides along in results/paper/<TID>_paper.json, ZERO behavior change
    (engine, sizing, entries, anchor gate untouched).
    'enforce': hard-refused unless results/regime_enforce_approved.json
    carries calibration_pass AND gm_approval -- and even then the response
    wiring is a separate signed item (REGIME_GUARD s3 + T-05 ticket: OFF
    until calibration passes + GM approval; calibration v1/v2 = honest
    FAIL as of 2026-09-24, so enforce is structurally OFF)."""
    mode = mode or os.environ.get("BIGMONEY_REGIME_GUARD", "shadow")
    if mode not in ("shadow", "enforce"):
        raise SystemExit(f"regime_guard: unknown mode {mode!r} (shadow|enforce)")
    if mode == "enforce":
        appr = None
        if os.path.exists(REGIME_GUARD_APPROVAL):
            try:
                with open(REGIME_GUARD_APPROVAL, encoding="utf-8") as fh:
                    appr = json.load(fh)
            except (OSError, ValueError):
                appr = None
        if not (isinstance(appr, dict) and appr.get("calibration_pass")
                and appr.get("gm_approval")):
            raise SystemExit(
                "regime_guard enforce REFUSED: requires calibration PASS + GM "
                "approval (results/regime_enforce_approved.json). Calibration "
                "v1/v2 = honest FAIL (REGIME_GUARD_VALIDATION*) -- enforce "
                "stays OFF (REGIME_GUARD s3 / T-05 ticket).")
        raise SystemExit(
            "regime_guard enforce approved, but response wiring is a separate "
            "signed item -- refusing to run paper under enforce (T-05 scope).")
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
                  rg: dict | None = None) -> dict:
    """Full pipeline for one trader. Returns the state dict; writes only
    when the anchor gate passes (trader JSON never touched on drift)."""
    anchor = anchor_gate(t, prices_full)
    if not anchor["ok"]:
        return {"trader": t["id"], "anchor_ok": False, "anchor": anchor}
    run = paper_run(t, prices_full, P)
    agg = monthly_aggregate(run["equity"], INITIAL_CASH, t["created"])
    x2 = cost_x2_check(t, prices_full, P, vi_bar)
    bt_x2 = (t.get("backtest") or {}).get("cost_x2") or {}
    seed = ({"sharpe": bt_x2.get("sharpe"), "vi_bar": vi_bar,
             "survive": bt_x2.get("survive")}
            if (bt_x2.get("sharpe") is not None and vi_bar is not None) else None)
    watch = x2_watch_verdict(x2, seed=seed)
    _append_x2_watch_log({"ts": time.strftime("%Y-%m-%d %H:%M:%S"),
                           "trader": t["id"], **watch})
    t["paper"] = {"months_tracked": agg["months_tracked"],
                  "monthly_returns": agg["monthly_returns"],
                  "current_dd": agg["current_dd"],
                  "as_of": time.strftime("%Y-%m-%d"),
                  "cutoff": data_cutoff,
                  "x2_watch": {**watch,
                               "as_of": time.strftime("%Y-%m-%d")}}
    save_trader(t)
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
            "regime_guard": rg if rg is not None else
                {"mode": "shadow", "state": None,
                 "note": "context unavailable (T-05 default block)"},
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
    """T-05 (3): shadow block from synthetic state file; state-file-absent
    honest; enforce refused without approval AND with approval (wiring =
    separate signed item); unknown mode refused. Offline path-swap only."""
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
        # C: enforce without approval -> hard refuse
        try:
            regime_guard_context("enforce")
            ok &= False
        except SystemExit:
            pass
        # D: enforce WITH approval -> still refused (wiring = separate item)
        with open(REGIME_GUARD_APPROVAL, "w", encoding="utf-8") as fh:
            json.dump({"calibration_pass": True, "gm_approval": True}, fh)
        try:
            regime_guard_context("enforce")
            ok &= False
        except SystemExit:
            pass
        # E: unknown mode -> refuse
        try:
            regime_guard_context("banana")
            ok &= False
        except SystemExit:
            pass
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
    rg = regime_guard_context()   # T-05 (3): additive shadow block (enforce refused)
    print(f"universe: {len(prices_full)} ETFs, data through {data_cutoff}")
    print(f"regime: major_bear={regime['is_major_bear']} "
          f"cap={regime['position_cap']} (close<MA250={regime['below_ma250']}, "
          f"dd={regime['dd_from_250d_high']})")
    print(f"regime_guard: {rg['mode']} state={rg['state']} asof={rg['asof']}")

    ok_all = True
    paper_dir = os.path.join(PATHS.results_dir, "paper")
    os.makedirs(paper_dir, exist_ok=True)
    for path in sorted(TRADERS_DIR.glob("*.json")):
        if path.name.startswith("_"):
            continue
        t = load_trader(path.stem)
        if t.get("level") not in PAPER_LEVELS:
            continue
        state = update_trader(t, prices_full, P, vi_bar, data_cutoff, regime, rg)
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
