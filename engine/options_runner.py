"""OPTIONS_WAVE2 sleeve engine — CC/PP/CSP overlays on SSE ETF option panels.

Prereg: research/OPTIONS_WAVE2_PREREG.md §2/§3 (frozen R191, sha
a6998921371ef4f867a448dd07f047e9288fdd47254f6c8a61fda4444396d0e6).
NEW ADDITIVE engine (prereg §3: futures_runner / ETF backtester zero-touch,
R99 law). Domain: retention-window option panel (data/options/, s0 census
200 contracts 2 underlyings) + ETF underlying legs (data/daily).

Execution semantics (frozen §3):
  - signal/selection on day T close (contract listed: first daily row <= T;
    sizing at T-close sleeve equity; underlying ADV20 causal at T) ->
    T+1 open fills (option OHLCV open, ETF open); roll schedule weekly
    (first panel day of ISO week) / monthly (last panel day of calendar
    month), roll-always (frozen entries estimate face).
  - daily close marking; expiry = intrinsic cash settlement at underlying
    close (physical-delivery proxy, disclosed); settlement fee 0 (proxy).
  - zero-volume gap days (illiquid contracts skip no-trade days in the
    sina daily face): marking carries the last observable contract close
    (ffill close_mark face); fills only on days with a row — a roll landing
    on a gap day is deferred whole (position carries to next roll/expiry,
    R194 fix, disclosed; selection tradability still reads the raw face).
  - limit guard: ETF open beyond +/-10% vs prior ETF close -> no NEW opens
    that day (closes always allowed).
  - costs: option leg = per-lot fee + max(2 ticks, 5% premium)/share/side;
    ETF leg = knowledge.rules cost_v2_side_rate (ADV20 tiered) with 1% ADV
    fill cap on entry buys. cost_mult scales both.
  - sizing frozen §3: CC/PP lots=floor(sig_equity/(S_T*unit)),
    CSP lots=floor(sig_equity/(K*unit)); PP decremented while cash would go
    negative (budget guard, deterministic, disclosed).

Instrument constants provisional pending G2 exchange verification
(scripts/options_wave2.py gate_g2): unit=10_000 shares/contract,
fee 6.6 yuan/contract/side, tick 0.0001.
"""
from __future__ import annotations

import math
import os
import sys

import numpy as np
import pandas as pd

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROOT)

from knowledge.rules import cost_v2_side_rate, ADV_FILL_CAP_RATE  # noqa: E402

OPT_UNIT = 10_000            # contract unit (shares per contract), provisional
OPT_FEE_LOT = 6.6            # yuan per contract per side, provisional (G2)
OPT_TICK = 0.0001            # option price tick (yuan), provisional (G2)
OPT_SLIP_TICKS = 2           # slippage floor: 2 ticks
OPT_SLIP_PREMIUM_RATE = 0.05  # slippage: 5% of premium (OTM wide-spread frozen)
ETF_LIMIT = 0.10             # underlying ETF daily price limit (main board)
MONEYNESS = (0.03, 0.05, 0.10)
FAMILIES = ("covered_call", "protective_put", "cash_secured_put")
UNDERLYINGS = ("510050", "510300")


def option_side_cost(premium: float, lots: int, cost_mult: float = 1.0) -> float:
    """Yuan cost (fee + slippage) for one side of `lots` contracts."""
    slip = max(OPT_SLIP_TICKS * OPT_TICK, OPT_SLIP_PREMIUM_RATE * premium)
    return lots * (OPT_FEE_LOT + slip * OPT_UNIT) * cost_mult


# ---------------------------------------------------------------- panel

class UndPanel:
    """One underlying: ETF OHLCV arrays + option contracts mapped onto the
    shared panel calendar (positional arrays, loop-friendly)."""

    def __init__(self, code: str, und_df: pd.DataFrame, contracts: list,
                 expiry_map: dict, dates: pd.DatetimeIndex):
        self.code = code
        self.dates = dates
        pos = {ts: i for i, ts in enumerate(dates)}
        n = len(dates)
        self.open = und_df["open"].to_numpy(dtype=float)
        self.close = und_df["close"].to_numpy(dtype=float)
        self.adv20 = und_df["amount"].rolling(20, min_periods=1).mean().to_numpy(dtype=float)
        by_dir: dict[str, list] = {"call": [], "put": []}
        for c in contracts:
            if c["underlying"] != code:
                continue
            frame = pd.read_csv(c["daily_csv"], index_col=0, parse_dates=True).sort_index()
            oarr = np.full(n, np.nan)
            carr = np.full(n, np.nan)
            for ts, row in frame.iterrows():
                i = pos.get(ts)
                if i is not None:
                    oarr[i] = float(row["open"])
                    carr[i] = float(row["close"])
            fd = pos.get(pd.Timestamp(c["first_date"]))
            by_dir[c["direction"]].append({
                "code": c["code"], "month": c["month"], "direction": c["direction"],
                "strike": float(c["strike"]), "open": oarr, "close": carr,
                # marking face: forward-fill close through zero-volume gap days
                # (illiquid deep-OTM contracts skip no-trade days in the sina
                # daily face; fills stay raw-open, marking carries last close)
                "close_mark": pd.Series(carr).ffill().to_numpy(dtype=float),
                "first_idx": fd if fd is not None else n,  # n = never available
                "expiry": expiry_map[(code, c["month"])],
            })
        self.by_dir = by_dir

    @classmethod
    def from_components(cls, code, dates, open_, close, amount, by_dir):
        """Synthetic-panel constructor (selftest/offline path; no files).
        Mirrors the production constructor's close_mark face (r157
        fixture-production pairing law)."""
        obj = cls.__new__(cls)
        obj.code = code
        obj.dates = dates
        obj.open = np.asarray(open_, dtype=float)
        obj.close = np.asarray(close, dtype=float)
        adv = pd.Series(np.asarray(amount, dtype=float)).rolling(20, min_periods=1).mean()
        obj.adv20 = adv.to_numpy(dtype=float)
        for contracts in by_dir.values():
            for c in contracts:
                c["close_mark"] = (pd.Series(np.asarray(c["close"], dtype=float))
                                   .ffill().to_numpy(dtype=float))
        obj.by_dir = by_dir
        return obj

    def select(self, t_idx: int, direction: str, m: float):
        """Frozen §2/§3 rule: among contracts alive at T (first_idx<=T and a
        row at T), take the enumerable nearest-expiry month family (YYYYMM
        ordering = expiry ordering), strike = argmin |K/S_T - 1 - m|."""
        s = self.close[t_idx]
        if not s or math.isnan(s):
            return None
        alive = [c for c in self.by_dir[direction]
                 if c["first_idx"] <= t_idx and not math.isnan(c["close"][t_idx])]
        if not alive:
            return None
        month = min(c["month"] for c in alive)
        fam = [c for c in alive if c["month"] == month]
        return min(fam, key=lambda c: abs(c["strike"] / s - 1.0 - m))


def build_expiry_map(contracts_meta: dict) -> dict:
    """Expiry per (underlying, month) from the contracts.json expiry face;
    null-date months (expired 202609 retention face) resolve to the family's
    max last_date proxy (data-driven, flagged)."""
    out: dict[tuple, tuple] = {}
    for und, months in contracts_meta["expiry"].items():
        for month, face in months.items():
            date_str = face["items"][0]
            if date_str not in (None, "None", ""):
                out[(und, month)] = (pd.Timestamp(date_str), False)
    fams: dict[tuple, list] = {}
    for c in contracts_meta["contracts"]:
        fams.setdefault((c["underlying"], c["month"]), []).append(c["last_date"])
    for key, members in fams.items():
        if key not in out:
            out[key] = (pd.Timestamp(max(members)), True)  # proxy resolution
    return out


def roll_schedule(dates: pd.DatetimeIndex, style: str) -> list:
    """[(signal_idx, exec_idx)] — weekly: first panel trading day of each ISO
    week; monthly: last panel trading day of each calendar month. Execution
    is always the next panel trading day (T -> T+1 open, frozen §3)."""
    if style == "weekly":
        sig = [i for i in range(len(dates))
               if i == 0 or (dates[i].isocalendar()[0:2] != dates[i - 1].isocalendar()[0:2])]
    else:
        sig = [i for i in range(len(dates))
               if i == len(dates) - 1 or dates[i].month != dates[i + 1].month]
    return [(i, i + 1) for i in sig if i + 1 < len(dates)]


# ---------------------------------------------------------------- metrics

def _metrics(equity: pd.Series) -> dict:
    rets = equity.pct_change().dropna()
    sd = rets.std(ddof=1)
    sharpe = float(rets.mean() / sd * math.sqrt(252)) if sd and sd > 0 else 0.0
    peak = equity.cummax()
    mdd = float(((equity - peak) / peak).min())
    total = float(equity.iloc[-1] / equity.iloc[0])
    years = len(equity) / 252.0
    annual = float(total ** (1.0 / years) - 1.0) if years > 0 and total > 0 else 0.0
    return {"sharpe": round(sharpe, 4), "annual_return": round(annual, 4),
            "max_drawdown": round(mdd, 4)}


def yearly_returns(equity: pd.Series) -> dict:
    out = {}
    for year, seg in equity.groupby(equity.index.year):
        if len(seg) > 1:
            out[str(year)] = round(float(seg.iloc[-1] / seg.iloc[0] - 1.0), 4)
    return out


# ---------------------------------------------------------------- sleeve

class _SleeveState:
    def __init__(self):
        self.cash = 0.0
        self.pos = None
        self.shares = 0
        self.trades = []
        self.cycles = []
        self.entry_execs = []


def _etf_trade(st: _SleeveState, pnl: UndPanel, i: int, delta_shares: int,
               adv20: float, cost_mult: float, reason: str) -> bool:
    """Buy/sell `delta_shares` at day-i ETF open with V2 costs; 1% ADV fill
    cap applies to entry buys only (reason == 'open')."""
    if delta_shares == 0:
        return True
    px = pnl.open[i]
    value = abs(delta_shares) * px
    cost = value * cost_v2_side_rate(adv20) * cost_mult
    if reason == "open" and adv20 > 0 and value > ADV_FILL_CAP_RATE * adv20:
        return False
    if delta_shares > 0:
        st.cash -= value + cost
    else:
        st.cash += value - cost
    st.shares += delta_shares
    st.trades.append({"date": str(pnl.dates[i].date()),
                      "leg": "etf_buy" if delta_shares > 0 else "etf_sell",
                      "code": pnl.code, "lots": abs(delta_shares), "price": px,
                      "value": (-1 if delta_shares > 0 else 1) * value,
                      "cost": cost, "reason": reason})
    return True


def _opt_trade(st: _SleeveState, pnl: UndPanel, i: int, contract: dict, lots: int,
               side: str, reason: str, cost_mult: float) -> float:
    """Option leg fill at day-i open. Returns net cash delta (signed)."""
    copen = float(contract["open"][i])
    cost = option_side_cost(copen, lots, cost_mult)
    premium = lots * OPT_UNIT * copen
    if side == "sell":
        delta = premium - cost
    else:
        delta = -(premium + cost)
    st.cash += delta
    st.trades.append({"date": str(pnl.dates[i].date()),
                      "leg": "opt_sell" if side == "sell" else "opt_buy",
                      "code": contract["code"], "lots": lots, "price": copen,
                      "value": (premium if side == "sell" else -premium),
                      "cost": cost, "reason": reason})
    return delta


def _close_overlay(st: _SleeveState, pnl: UndPanel, i: int, cost_mult: float) -> bool:
    """Buy back / sell the held option overlay at day-i open (roll close or
    flatten; closes always allowed). Returns False when the held contract has
    no daily row at day i (zero-volume gap day: no observable price, no honest
    fill) — caller defers the whole roll (position carries to the next roll or
    expiry). R194 fix for the 2026-03-10 NaN-fill cash-poisoning crash."""
    p = st.pos
    if p is None:
        return True
    contract = p["contract"]
    if math.isnan(float(contract["open"][i])):
        return False
    side = "buy" if p["family"] in ("covered_call", "cash_secured_put") else "sell"
    delta = _opt_trade(st, pnl, i, contract, p["lots"], side, "roll_close", cost_mult)
    st.cycles.append(delta + p["opt_open_delta"])
    st.pos = None
    return True


def _settle_expiry(st: _SleeveState, pnl: UndPanel, i: int) -> None:
    """Expiry: intrinsic cash settlement at underlying close (frozen §3
    physical-delivery proxy); fee 0 (proxy, disclosed)."""
    p = st.pos
    if p is None:
        return
    contract = p["contract"]
    s = float(pnl.close[i])
    k = contract["strike"]
    if contract["direction"] == "call":
        intrinsic = max(s - k, 0.0)
        delta = -p["lots"] * OPT_UNIT * intrinsic      # short call pays out
    else:
        intrinsic = max(k - s, 0.0)
        delta = (p["lots"] * OPT_UNIT * intrinsic if p["family"] == "protective_put"
                 else -p["lots"] * OPT_UNIT * intrinsic)
    st.cash += delta
    st.trades.append({"date": str(pnl.dates[i].date()), "leg": "opt_settle",
                      "code": contract["code"], "lots": p["lots"],
                      "price": intrinsic, "value": delta, "cost": 0.0,
                      "reason": "expiry_settle"})
    st.cycles.append(delta + p["opt_open_delta"])
    st.pos = None


def _open_position(st: _SleeveState, pnl: UndPanel, i: int, family: str,
                   contract: dict, lots: int, cost_mult: float, adv20: float,
                   sig_close: float) -> bool:
    """Open the overlay at day-i open: limit guard + fill cap + budget guard
    all checked BEFORE any leg trades (atomic open)."""
    copen = float(contract["open"][i])
    if math.isnan(copen) or lots < 1:
        return False
    # limit guard (frozen §3): no new opens beyond +/-10% ETF open move
    if i > 0:
        prev = pnl.close[i - 1]
        if prev and abs(pnl.open[i] / prev - 1.0) > ETF_LIMIT:
            return False
    direction = "call" if family == "covered_call" else "put"
    side = "sell" if family in ("covered_call", "cash_secured_put") else "buy"
    target_shares = lots * OPT_UNIT if family in ("covered_call", "protective_put") else 0
    d_shares = target_shares - st.shares
    px = float(pnl.open[i])
    share_value = abs(d_shares) * px
    etf_cost = share_value * cost_v2_side_rate(adv20) * cost_mult
    if d_shares > 0 and adv20 > 0 and share_value > ADV_FILL_CAP_RATE * adv20:
        return False
    opt_cost = option_side_cost(copen, lots, cost_mult)
    premium = lots * OPT_UNIT * copen
    opt_delta = (premium - opt_cost) if side == "sell" else -(premium + opt_cost)
    share_delta_cash = (-share_value - etf_cost) if d_shares > 0 else (share_value - etf_cost)
    if st.cash + opt_delta + share_delta_cash < 0:
        return False  # budget guard (caller may decrement lots and retry)
    # execute: option leg + share adjustment
    st.cash += opt_delta
    st.trades.append({"date": str(pnl.dates[i].date()),
                      "leg": "opt_sell" if side == "sell" else "opt_buy",
                      "code": contract["code"], "lots": lots, "price": copen,
                      "value": (premium if side == "sell" else -premium),
                      "cost": opt_cost, "reason": "open"})
    if d_shares != 0:
        _etf_trade(st, pnl, i, d_shares, adv20, cost_mult,
                   "open" if d_shares > 0 else "flatten")
    st.pos = {"family": family, "contract": contract, "lots": lots,
              "opt_open_delta": opt_delta, "expiry_ts": contract["expiry"][0]}
    return True


def _equity(st: _SleeveState, pnl: UndPanel, i: int) -> float:
    eq = st.cash + st.shares * pnl.close[i]
    if st.pos is not None:
        cclose = st.pos["contract"]["close_mark"][i]
        if not math.isnan(cclose):  # NaN only before first row (pos never held then)
            mult = OPT_UNIT * st.pos["lots"]
            if st.pos["family"] == "protective_put":
                eq += mult * cclose           # long put asset
            else:
                eq -= mult * cclose           # short leg liability
    return eq


def run_und_sleeve(pnl: UndPanel, plan: list, sub_cash: float,
                   cost_mult: float = 1.0) -> dict:
    """Run one underlying sleeve. `plan` = [(sig_idx, exec_idx, family|None,
    contract|None)] — selection frozen at signal day (look-ahead law)."""
    st = _SleeveState()
    st.cash = sub_cash
    exec_map = {e: (fam, c) for (s, e, fam, c) in plan}
    n = len(pnl.dates)
    equity = np.empty(n)
    for i in range(n):
        day = pnl.dates[i]
        if i in exec_map:
            fam, c = exec_map[i]
            sig_eq = equity[i - 1] if i > 0 else sub_cash  # T-close equity
            sig_close = pnl.close[i - 1] if i > 0 else pnl.close[0]
            adv = pnl.adv20[i - 1] if i > 0 else pnl.adv20[0]
            roll_ok = True
            if st.pos is not None:
                # atomic roll: a held overlay with no fillable price at day i
                # (zero-volume gap day) defers the ENTIRE roll — no orphaned
                # overlays (old leg dropped while new leg opens), no fabricated
                # fills at stale prices; position carries to next roll/expiry
                roll_ok = _close_overlay(st, pnl, i, cost_mult)
            if roll_ok:
                if fam is None:
                    if st.shares:  # flatten: off-state holds no ETF exposure
                        _etf_trade(st, pnl, i, -st.shares, adv, cost_mult, "flatten")
                elif c is not None:
                    if fam == "cash_secured_put":
                        lots = int(sig_eq // (c["strike"] * OPT_UNIT))
                    else:
                        lots = int(sig_eq // (sig_close * OPT_UNIT)) if sig_close > 0 else 0
                    while lots >= 1 and not _open_position(st, pnl, i, fam, c, lots,
                                                           cost_mult, adv, sig_close):
                        lots -= 1  # PP budget guard decrement (deterministic)
                    if st.pos is not None:
                        st.entry_execs.append(i)
        if st.pos is not None and st.pos["expiry_ts"] == day:
            _settle_expiry(st, pnl, i)
        equity[i] = _equity(st, pnl, i)
    return {"equity": pd.Series(equity, index=pnl.dates), "trades": st.trades,
            "entries": len(st.entry_execs), "entry_execs": st.entry_execs,
            "cycles": st.cycles, "shares_end": st.shares, "cash_end": st.cash}


# ---------------------------------------------------------------- plans & cells

def build_plan(panels: dict, schedule: list, family: str | None, m: float) -> list:
    """Candidate cell plan: same family/m every roll (off cells use None)."""
    plan = []
    for sig, exec_i in schedule:
        per = {}
        for code, pnl in panels.items():
            if family is None:
                per[code] = None
            else:
                direction = "call" if family == "covered_call" else "put"
                per[code] = pnl.select(sig, direction, m)
        plan.append((sig, exec_i, family, m, per))
    return plan


def build_null_plan(panels: dict, schedule: list, rng) -> list:
    """K-th null: each roll draws equiprobable {CC, PP, off} then m in the
    frozen moneyness set; one state per roll applied to both underlyings
    (same holding distribution / roll regime / contract rule, §3)."""
    plan = []
    for sig, exec_i in schedule:
        state = int(rng.integers(0, 3))
        fam = FAMILIES[state] if state < 2 else None
        m = MONEYNESS[int(rng.integers(0, 3))]
        per = {}
        for code, pnl in panels.items():
            if fam is None:
                per[code] = None
            else:
                direction = "call" if fam == "covered_call" else "put"
                per[code] = pnl.select(sig, direction, m)
        plan.append((sig, exec_i, fam, m, per))
    return plan


def run_cell(panels: dict, schedule: list, family: str | None, m: float,
             start_cash: float, cost_mult: float = 1.0,
             plan: list | None = None) -> dict:
    """One batch cell: 50/50 blend across both underlyings (frozen §0 18-cell
    reading, disclosed in runner meta). Cell n_entries = synchronized roll
    events where >=1 sleeve actually opened."""
    if plan is None:
        plan = build_plan(panels, schedule, family, m)
    sub = start_cash / len(panels)
    runs = {code: run_und_sleeve(pnl, [(s, e, f, per[code]) for (s, e, f, mm, per) in plan],
                                 sub, cost_mult)
            for code, pnl in panels.items()}
    opened = set()
    for r in runs.values():
        opened.update(r["entry_execs"])
    equity = sum(r["equity"] for r in runs.values())
    trades = []
    for code, r in runs.items():
        trades.extend({**t, "und": code} for t in r["trades"])
    cycles = [c for r in runs.values() for c in r["cycles"]]
    met = _metrics(equity)
    win_rate = round(sum(1 for c in cycles if c > 0) / len(cycles), 4) if cycles else 0.0
    years = len(equity) / 252.0
    avg_eq = float(equity.mean()) if len(equity) else 0.0
    turnover = (round(sum(abs(t["value"]) for t in trades) / avg_eq / years, 4)
                if avg_eq and years else 0.0)
    return {
        "full": {**met, "n_trades": len(trades), "n_entries": len(opened),
                 "win_rate": win_rate, "turnover": turnover,
                 "final_equity": round(float(equity.iloc[-1]), 2),
                 "n_cycles": len(cycles)},
        "per_und": {code: {"entries": r["entries"], "shares_end": r["shares_end"],
                           "cash_end": round(r["cash_end"], 2)}
                    for code, r in runs.items()},
        "_equity": equity, "_returns": equity.pct_change().dropna(),
        "_trades": trades,
        "_premium_paid": sum(-t["value"] for t in trades
                             if t["leg"] == "opt_buy" and t["reason"] == "open"),
        "_premium_received": sum(t["value"] for t in trades
                                 if t["leg"] == "opt_sell" and t["reason"] == "open"),
    }


def run_passive(pnl: UndPanel, start_cash: float, cost_mult: float = 1.0) -> dict:
    """Buy-hold one underlying: entry at first exec day (panel day 1) open
    with V2 costs + fill cap, hold, mark at close (no forced exit)."""
    st = _SleeveState()
    st.cash = start_cash
    n = len(pnl.dates)
    equity = np.empty(n)
    i = 1
    adv = pnl.adv20[i - 1]
    px = float(pnl.open[i])
    rate = cost_v2_side_rate(adv) * cost_mult
    shares = int(start_cash // (px * (1.0 + rate)))
    _etf_trade(st, pnl, i, shares, adv, cost_mult, "open")
    for j in range(n):
        equity[j] = st.cash + st.shares * pnl.close[j]
    eq = pd.Series(equity, index=pnl.dates)
    met = _metrics(eq)
    return {"full": {**met, "n_trades": len(st.trades), "n_entries": 1,
                     "win_rate": 0.0, "turnover": 0.0,
                     "final_equity": round(float(eq.iloc[-1]), 2)},
            "_equity": eq, "_returns": eq.pct_change().dropna()}
