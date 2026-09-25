"""Backtest engine.

Fixes vs old version:
  - entry signal at day T -> execute at day T+1 OPEN (no look-ahead)
  - T+1: positions opened today cannot be sold today
  - fees from knowledge/rules.py (commission + handling + slippage)
  - ffill + min listing age filter
"""
import numpy as np
import pandas as pd

from .exit_rules import ExitConfig, ExitState, evaluate
from .metrics import summarize, win_rate, profit_factor
from knowledge.rules import (
    FeeSchedule, is_t0,
    ADV20_TIER_2BP_YUAN, ADV20_TIER_5BP_YUAN, ADV_FILL_CAP_RATE,
    SLIPPAGE_TIER_2BP, SLIPPAGE_TIER_5BP, SLIPPAGE_TIER_10BP, COST_BASIS_V2,
)


def _entry_signal(close: pd.Series, fast: int = 5, slow: int = 20) -> pd.Series:
    f = close.rolling(fast).mean()
    s = close.rolling(slow).mean()
    cross = (f > s) & (f.shift(1) <= s.shift(1))
    return cross.fillna(False)


def _exit_signal(close: pd.Series, fast: int = 5, slow: int = 20) -> pd.Series:
    f = close.rolling(fast).mean()
    s = close.rolling(slow).mean()
    cross = (f < s) & (f.shift(1) >= s.shift(1))
    return cross.fillna(False)


def run_backtest(prices: dict, params: dict,
                 initial_cash: float = 1_000_000.0,
                 entry_signal: pd.DataFrame = None,
                 exit_signal: pd.DataFrame = None,
                 fill_guard=None,
                 cost_v2=None,
                 cash_parking=None,
                 entry_size_scale=None,
                 staged_entry=None) -> dict:
    """prices: dict[symbol] -> DataFrame with date index, cols open/close/high/low.

    J7 signal-injection adapter (BACKTEST_PLAN S2 contract):
      entry_signal / exit_signal: DataFrame (date x symbol), truthy -> on.
      Default None -> built-in MA(5,20) cross (432-grid behavior unchanged).
      Signals computed on day T close execute at T+1 open (no look-ahead).

    P4-B2 s3.1 fill_guard (additive; default None = legacy path
    byte-identical). Execution-time transactability overlay built from the
    execution day's OWN information (no look-ahead):
      dict {"buy": DF(date x symbol, bool), "sell": DF(...)} -> side-aware
        (stock limit-board semantics: buy blocked on sealed limit-UP open,
         sell deferred off sealed limit-DOWN close);
      single DataFrame(date x symbol, bool) -> applied to BOTH sides.
      buy False on execution day -> pending entry DROPPED (unfilled order,
        not retried; a fresh signal may re-queue later -- that is a new order).
      sell False on exit day -> exit DEFERRED: retried each later close,
        force-executed at the first fillable close with the ORIGINAL exit
        reason/size (stale decision, honest late fill).
      Missing symbol/date -> unrestricted (True).

    D5 cost-basis v2 (BACKTEST_SCIENCE.md s5; additive; default None =
    legacy path byte-identical). cost_v2 accepts:
      DataFrame(date x symbol) -- ADV(20d) panel: rolling 20-day mean daily
        turnover in yuan ENDING at each date (inclusive); the engine shifts
        one day so an execution on day D only sees information through the
        prior (signal) close -- no look-ahead;
      dict {"adv20": <that DataFrame>} -- same panel keyed.
    When ON: per-side slippage tiered 2/5/10bp by ADV(20d) (missing ->
    10bp conservative = legacy); entry demand capped at 1% of ADV(20d)
    (excess does not fill, partial fill kept; zero/negative ADV -> order
    dropped; missing ADV -> no cap, counted). Exits keep the tiered rate but
    are NOT quantity-capped (exit machine owns sizing via close_fraction).
    Basis + counters are disclosed in result["cost_v2"] (key absent when off).

    T-09 CASH_LEG additive flag (research/CASH_LEG.md frozen spec; default
    None = legacy path byte-identical). cash_parking is a dict, three keys:
      repo_rate     pd.Series -- annualized % (1.475 = 1.475%), date-indexed;
                    the engine does no IO: caller assembles and truncates.
      major_bear    pd.Series(bool) -- bear-day mask; sole implementation
                    source = firm/risk/regime.py (caller assembles).
      bear_park_frac  float -- parking target fraction (R-配3 = 0.80).
    Daily rolling block appended AFTER close mark-to-market (GC001-style
    T+1; engine intra-day order unchanged): settle the balance parked at
    the prior close back into cash + accrue one trading-day of interest
    rate(T)/100/252 on it (missing-rate day -> ffill last known rate; no
    known rate yet -> 0, never fabricated; trading-day-only accrual is a
    conservative understatement of true repo carry); then on bear days
    re-park min(cash, frac*equity) and on non-bear days fully release.
    Parked funds are NOT available for same-day entries (subtracted from
    cash when parked; returned by the settle step). No forced liquidation
    if positions hold the equity share -- enforcement to the 80% target is
    a portfolio-layer concern (gated behind REGIME_GUARD calibration),
    explicitly out of scope. New metrics keys appear ONLY when the flag
    is ON: parked_days / bear_days_in_window / parking_yield_total /
    parked_balance_end / parking_accrual_series.

    T-03 engine-integrity additive flags (AUDIT-20260923 P0-2/3/4, P1-1/2/3;
    task T-2026-09-23-03). ALL flags default OFF/absent -> legacy path
    byte-identical (engine additive iron rule). New metrics use NEW field
    names; historical keys are never overwritten:
      trade_pnl_mode="full"   -> per-trade pnl_full charges BUY-side cost
                                 (legacy 'pnl' omits it, ~13bp/trade, P0-2);
                                 metrics gain win_rate_full/profit_factor_full/
                                 avg_pnl_full.
      strict_open_fills=True   -> fills require a REAL bar that day, not an
                                 ffilled stale price (P0-3): pending entries on
                                 suspension days are DROPPED (fill_guard
                                 precedent); exits on stale closes are DEFERRED
                                 to the next real close.
      stale_mark_tag=True      -> mark-to-market on ffilled close is flagged;
                                 metrics gain stale_mark_days + sharpe_ex_stale
                                 (stale-end days excluded, P0-4).
      sizing_mode="equity_fraction" -> target_value = (cash+pos_val)*pct at
                                 execution instead of initial_cash*pct (P1-1).
      report_num_entries=True  -> metrics gain num_entries (distinct position
                                 opens) alongside num_trades (tranche count,
                                 P1-3 layered take-profit padding).
      params["trailing_lock"]/["initial_stop"] -> exposed via ExitConfig (P1-2).

    T-21 REGIME_ENFORCE additive flag (research/REGIME_ENFORCE_WIRING.md
    frozen spec; default None = legacy path byte-identical).
      entry_size_scale  pd.Series (date-indexed, 0<scale<=1) -- per
        EXECUTION-day nominal multiplier applied to target_value AFTER the
        sizing-mode base and BEFORE the cost-v2 ADV cap. Missing dates ->
        1.0 (legacy nominal); values clipped to [0,1] (the response matrix
        only halves, never leverages). Decision causality is the CALLER's
        contract: the value indexed at exec day E must reflect information
        through the prior close (REGIME_GUARD state known at E-1).
      fill_guard buy-side drops are COUNTED when any fill_guard is supplied:
        metrics gain "fill_guard_buy_dropped" (new key only when a guard is
        present; the None path never emits it).
      metrics gain "scaled_entries" only when entry_size_scale is not None
        (count of filled entries whose applied scale was < 1.0).

    P4-B3 STAGED_ENTRY additive flag (research/shortline/P4_BATCH3_DCA_SPEC.md
    section 2 frozen spec; default None = legacy path byte-identical).
      staged_entry dict {"grid_fracs": (0.40, 0.30, 0.30),
                         "add_triggers": (0.0, -0.05, -0.10)}
      Splits the SAME legacy nominal (sizing_mode -> entry_size_scale ->
      cost_v2 ADV-cap chain, all computed up-front exactly as the single-shot
      entry) into per-tranche budgets x fracs; HARD ASSERT sum(fracs) <= 1.0
      (staging pre-splits the budget, never leverages it -- redline 3-a).
      Tranche 0 = the normal entry signal; tranche k >= 1 queues at a close
      where close <= first_fill * (1 + trigger_k) (level state; the first-fill
      price anchors every trigger; no trigger exists before tranche 0 fills)
      and fills at the NEXT day open (same T -> T+1 causality as entries,
      zero future data; max_adds = len(fracs) - 1 constructive cap). On each
      add fill: quantity += add_qty; cost_price := VWAP (exit machinery
      untouched -> stop/tiers/trailing inherit the new average; the -8%
      initial stop follows the VWAP down -- the definitionally accepted cost
      of averaging down); high_watermark keeps its continuous max since the
      first fill (never reset, conservative); trailing_stop_price never
      reset; hold_days / tier_reached unchanged. Each add is an independent
      execution: fill_guard buy-reject drops that tranche's order (counted;
      the level may re-queue it at a later close -- P4-B2 precedent),
      cost_v2 ADV cap applies per tranche at its own execution day,
      strict_open_fills drops on suspension days; insufficient cash keeps
      the add queued (retries next open, legacy pending-entry precedent).
      Adds bypass max_positions (a staged position occupies its slot by
      name, not by capital). Execution order within the open: signal
      entries first (legacy loop untouched), then staged adds.
      New metric keys ONLY when the flag is ON (G5 keyset discipline):
      num_adds_filled / num_adds_dropped / avg_cost_first / avg_cost_end /
      adds_per_entry. Queued adds orphaned by a full position close or by
      the window end count as drops (they never filled).
    """
    cfg = ExitConfig(
        take_profit_levels=tuple(params.get("take_profit_levels", (0.05, 0.10, 0.20))),
        trailing_activate=params.get("trailing_stop_activate", 0.05),
        trailing_lock=params.get("trailing_lock", 0.01),   # T-03-F5 exposed (default = ExitConfig legacy)
        initial_stop=params.get("initial_stop", -0.08),   # T-03-F5 exposed (default = ExitConfig legacy)
        time_decay_period=params.get("time_decay_period", 12),
        time_decay_threshold=params.get("time_decay_threshold", 0.02),
        position_size_pct=params.get("position_size_pct", 0.10),
        max_positions=params.get("max_positions", 5),
    )
    fee = FeeSchedule()
    cost_rate = fee.commission_rate + fee.handling_fee + fee.supervision_fee + fee.slippage_a

    # T-03 additive flags: defaults keep the legacy path byte-identical.
    strict_fills = bool(params.get("strict_open_fills", False))
    stale_marks = bool(params.get("stale_mark_tag", False))
    trade_pnl_mode = params.get("trade_pnl_mode", "legacy")
    sizing_mode = params.get("sizing_mode", "fixed_initial")
    report_num_entries = bool(params.get("report_num_entries", False))

    # P4-B3 staged_entry additive flag: None -> legacy path byte-identical
    # (engine additive iron rule).
    if staged_entry is None:
        stage_fracs = stage_triggers = None
    else:
        stage_fracs = tuple(float(x) for x in staged_entry["grid_fracs"])
        stage_triggers = tuple(float(x) for x in staged_entry["add_triggers"])
        if len(stage_triggers) != len(stage_fracs):
            raise ValueError("staged_entry: add_triggers must align 1:1 with grid_fracs")
        if sum(stage_fracs) > 1.0:
            # redline hard assert (P4_BATCH3_DCA_SPEC.md section 2 / 3-a):
            # staging pre-splits the SAME single-shot nominal budget;
            # sum > 1.0 would be leveraging, refuse to run.
            raise ValueError(
                f"staged_entry: grid_fracs sum {sum(stage_fracs):.4f} > 1.0 "
                "(staged budget must not exceed the single-shot nominal)")
        if any(f <= 0.0 for f in stage_fracs):
            raise ValueError("staged_entry: every grid_frac must be > 0")

    # align all symbols on common trading calendar
    closes = pd.DataFrame({sym: df["close"] for sym, df in prices.items()}).sort_index()
    opens = pd.DataFrame({sym: df["open"] for sym, df in prices.items()}).sort_index()
    # T-03-F2: real-bar masks captured BEFORE ffill (suspension gaps ARE the
    # ffilled cells). Consumed only when strict/stale flags are ON.
    if strict_fills or stale_marks:
        col_pos = {sym: j for j, sym in enumerate(closes.columns)}
        real_close_mask = (~closes.isna()).to_numpy()
        real_open_mask = (~opens.isna()).to_numpy() if strict_fills else None
    else:
        col_pos = None
        real_close_mask = None
        real_open_mask = None
    closes = closes.ffill()
    opens = opens.ffill()

    cash = initial_cash
    positions: dict[str, ExitState] = {}
    trades: list[dict] = []
    num_entries = 0                   # T-03-F6: distinct position opens
    stale_flags: list[bool] = []      # T-03-F2: per-day stale-mark day flag (flag ON only)
    equity_curve: list[float] = []
    dates = closes.index

    # D5 cost v2 panels (built only when the additive flag is ON; the
    # legacy path below never touches these variables when cost_v2=None).
    if cost_v2 is None:
        tier_v2 = cap_v2 = None
        stats_v2 = None
    else:
        adv = cost_v2["adv20"] if isinstance(cost_v2, dict) else cost_v2
        adv = adv.reindex(index=dates, columns=closes.columns)
        adv_arr = adv.shift(1).to_numpy(dtype=float)   # exec day -> signal-day info
        with np.errstate(invalid="ignore"):
            finite = np.isfinite(adv_arr)
            tier_arr = np.full(adv_arr.shape, SLIPPAGE_TIER_10BP, dtype=float)
            m5 = finite & (adv_arr >= ADV20_TIER_5BP_YUAN)
            m2 = finite & (adv_arr >= ADV20_TIER_2BP_YUAN)
            tier_arr[m5] = SLIPPAGE_TIER_5BP
            tier_arr[m2] = SLIPPAGE_TIER_2BP          # m2 subset of m5: 2bp wins
            cap_arr = np.where(finite, ADV_FILL_CAP_RATE * adv_arr, np.inf)
        tier_v2 = pd.DataFrame(tier_arr, index=dates, columns=closes.columns)
        cap_v2 = pd.DataFrame(cap_arr, index=dates, columns=closes.columns)
        stats_v2 = {
            "cost_basis": COST_BASIS_V2,
            "tier_entries_2bp": 0, "tier_entries_5bp": 0,
            "tier_entries_10bp": 0,
            "capped_entries": 0, "dropped_zero_adv": 0,
            "missing_adv_executions": 0,
        }

    # T-09 CASH_LEG additive flag: default None keeps the legacy path
    # byte-identical (engine additive iron rule).
    if cash_parking is None:
        park_rate = park_bear = None
        park_frac = 0.80
        parking_state = None
        parked_bal = 0.0          # on-deposit balance held into today
    else:
        park_rate = cash_parking["repo_rate"].reindex(dates).ffill()
        park_bear = (cash_parking["major_bear"]
                     .reindex(dates).fillna(False).astype(bool))
        park_frac = float(cash_parking.get("bear_park_frac", 0.80))
        parking_state = {
            "parked_days": 0,          # days funds were on deposit (accrued)
            "bear_days_in_window": 0,
            "parking_yield_total": 0.0,
            "parking_accrual_series": [],
        }
        parked_bal = 0.0

    # precompute signals on close
    def _injected(sig: pd.DataFrame, sym: str) -> pd.Series:
        if sig is None or sym not in sig.columns:
            return pd.Series(False, index=dates)
        return sig[sym].reindex(dates).fillna(0).astype(bool)

    if entry_signal is None:
        entry_sig = {sym: _entry_signal(closes[sym]) for sym in closes.columns}
    else:
        entry_sig = {sym: _injected(entry_signal, sym) for sym in closes.columns}
    if exit_signal is None:
        exit_sig = {sym: _exit_signal(closes[sym]) for sym in closes.columns}
    else:
        exit_sig = {sym: _injected(exit_signal, sym) for sym in closes.columns}

    # P4-B2 s3.1 fill guard: None -> fully unrestricted (legacy path).
    def _guard_arrays(guard) -> dict:
        out = {}
        for sym in closes.columns:
            if guard is not None and sym in guard.columns:
                out[sym] = guard[sym].reindex(dates).fillna(True).astype(bool).to_numpy()
            else:
                out[sym] = None
        return out

    if fill_guard is None:
        buy_g = sell_g = None
        guard_drops = 0                   # T-21: count buy-side drops (any guard)
    elif isinstance(fill_guard, dict):
        buy_g = _guard_arrays(fill_guard.get("buy"))
        sell_g = _guard_arrays(fill_guard.get("sell"))
        guard_drops = 0
    else:
        buy_g = _guard_arrays(fill_guard)
        sell_g = buy_g
        guard_drops = 0

    # T-21 REGIME_ENFORCE additive: per-execution-day nominal scale
    # (default None -> arr None -> legacy path byte-identical).
    if entry_size_scale is None:
        scale_arr = None
    else:
        _es = entry_size_scale
        if isinstance(_es, dict):
            _es = pd.Series(_es)
        scale_arr = (_es.reindex(dates).astype(float)
                     .fillna(1.0).clip(lower=0.0, upper=1.0).to_numpy())
    scaled_entries = 0

    def _fillable(arrs: dict, sym: str, i: int) -> bool:
        if arrs is None:
            return True
        a = arrs.get(sym)
        return True if a is None else bool(a[i])

    def _real_bar(mask, sym: str, i: int) -> bool:
        # T-03-F2: was there a REAL (non-ffilled) bar for sym on day i?
        if mask is None:
            return True
        j = col_pos.get(sym)
        return True if j is None else bool(mask[i][j])

    # pending entries: signal fired at day T, execute at day T+1 open
    pending_entries: dict[str, dict] = {}
    # sell-deferral book (P4-B2): sym -> stored ExitAction awaiting a fillable close
    deferred_exits: dict[str, object] = {}
    # T-20 PAPER_GUARD_DUAL_RAIL additive disclosure counters (emitted ONLY
    # when fill_guard is present -- same pattern as fill_guard_buy_dropped;
    # fill semantics above stay P4-B2 verbatim, these are report-only).
    deferred_events = 0        # guard-deferral episodes (incl. window-end open)
    deferred_days = 0         # closes where a guard-deferred exit waited
    first_deferred_date = None
    deferred_open: set = set() # episodes still awaiting a fillable close

    # P4-B3 staged_entry books (flag ON only; the None path never reads them)
    staged_books: dict = {}          # sym -> {"first_fill", "nominal", "filled"}
    pending_adds: dict = {}           # sym -> {tranche k: queued close-date}
    adds_filled_total = 0
    adds_dropped_total = 0
    staged_entries_total = 0
    stage_first_fill_px: list = []    # first-tranche fill px per staged entry
    stage_end_cost_px: list = []      # final cost_price per staged position

    for i, date in enumerate(dates):
        row_close = closes.loc[date]
        row_open = opens.loc[date]

        # 0) execute pending entries at today's OPEN
        for sym, info in list(pending_entries.items()):
            if sym in positions:
                continue
            if len(positions) >= cfg.max_positions:
                break
            px = row_open[sym]
            if pd.isna(px):
                continue
            if not _fillable(buy_g, sym, i):
                # P4-B2 buy rejection: unfilled at this open (e.g. sealed
                # limit-up) -> order dropped, not retried on stale signal.
                del pending_entries[sym]
                guard_drops += 1
                continue
            if strict_fills and not _real_bar(real_open_mask, sym, i):
                # T-03-F2 strict_open_fills: suspension day (ffilled stale
                # open, no real bar) -> cannot fill; drop the pending order.
                del pending_entries[sym]
                continue
            if sizing_mode == "equity_fraction":
                # T-03-F4: target as a fraction of CURRENT equity (cash +
                # positions marked at today's open) instead of frozen initial.
                pos_val_now = sum(st.quantity * row_open[s]
                                  for s, st in positions.items() if s in row_open)
                target_value = (cash + pos_val_now) * cfg.position_size_pct
            else:
                target_value = initial_cash * cfg.position_size_pct
            if scale_arr is not None:
                # T-21 REGIME_ENFORCE: YELLOW-day nominal x0.5 (caller owns
                # the decision-date causality; scale read at EXEC day).
                target_value *= float(scale_arr[i])
                if scale_arr[i] < 1.0:
                    scaled_entries += 1
            if tier_v2 is None:
                rate_buy = cost_rate   # legacy path (identical arithmetic)
            else:
                # --- D5 cost-v2 entry path ---
                cap_i = float(cap_v2.at[date, sym])
                tier_i = float(tier_v2.at[date, sym])
                if not np.isfinite(cap_i):
                    # missing ADV: conservative 10bp slippage (= legacy), no cap
                    stats_v2["missing_adv_executions"] += 1
                elif cap_i <= 0:
                    # zero/negative ADV(20d): no measurable liquidity -> dropped
                    del pending_entries[sym]
                    stats_v2["dropped_zero_adv"] += 1
                    continue
                elif cap_i < target_value:
                    # D5 volume constraint: demand > 1% ADV -> excess unfilled
                    target_value = cap_i
                    stats_v2["capped_entries"] += 1
                rate_buy = (fee.commission_rate + fee.handling_fee
                            + fee.supervision_fee + tier_i)

            if stage_fracs is not None:
                # P4-B3: the SAME nominal (sizing/scale/ADV-cap chain above,
                # untouched) pre-split into per-tranche budgets; tranche 0
                # fills now, the rest are drawdown-triggered adds.
                budget = target_value * stage_fracs[0]
            else:
                budget = target_value
            qty = budget / px
            total_cost = px * qty * (1 + rate_buy)
            if total_cost > cash:
                continue
            cash -= total_cost
            if tier_v2 is not None:
                if tier_i == SLIPPAGE_TIER_2BP:
                    stats_v2["tier_entries_2bp"] += 1
                elif tier_i == SLIPPAGE_TIER_5BP:
                    stats_v2["tier_entries_5bp"] += 1
                else:
                    stats_v2["tier_entries_10bp"] += 1
            positions[sym] = ExitState(
                cost_price=px, quantity=qty, high_watermark=px,
            )
            num_entries += 1
            if stage_fracs is not None:
                # P4-B3: open the staged book; every trigger is anchored to
                # THIS first-fill price (no trigger exists before it).
                staged_books[sym] = {
                    "first_fill": px,
                    "nominal": target_value,
                    "filled": set(),
                }
                staged_entries_total += 1
                stage_first_fill_px.append(px)
            del pending_entries[sym]

        # 0b) P4-B3 staged adds: queued at a prior close, fill at today's
        # OPEN (flag ON only). Signal entries keep cash priority; adds
        # never take a max_positions slot (a staged position occupies its
        # slot by name, not by capital).
        if stage_fracs is not None and pending_adds:
            for sym in list(pending_adds.keys()):
                if sym not in positions:
                    # defensive: staged book dies with the position (step 1);
                    # anything still queued here never filled.
                    adds_dropped_total += len(pending_adds.pop(sym))
                    continue
                px = row_open[sym]
                if pd.isna(px):
                    continue            # no open price -> stays queued
                st = positions[sym]
                guard_ok = _fillable(buy_g, sym, i)
                real_ok = (not strict_fills) or _real_bar(real_open_mask, sym, i)
                for k in list(pending_adds[sym].keys()):
                    if not guard_ok or not real_ok:
                        # P4-B2 buy-reject / strict-suspension precedent:
                        # drop THIS tranche's order (counted); the level
                        # trigger may re-queue it at a later close.
                        del pending_adds[sym][k]
                        adds_dropped_total += 1
                        continue
                    budget = staged_books[sym]["nominal"] * stage_fracs[k]
                    if tier_v2 is None:
                        rate_buy = cost_rate   # legacy path (identical arithmetic)
                    else:
                        # --- D5 cost-v2 add path: cap per tranche at its own day
                        cap_i = float(cap_v2.at[date, sym])
                        tier_i = float(tier_v2.at[date, sym])
                        if not np.isfinite(cap_i):
                            stats_v2["missing_adv_executions"] += 1
                        elif cap_i <= 0:
                            del pending_adds[sym][k]
                            stats_v2["dropped_zero_adv"] += 1
                            adds_dropped_total += 1
                            continue
                        elif cap_i < budget:
                            budget = cap_i
                            stats_v2["capped_entries"] += 1
                        if tier_i == SLIPPAGE_TIER_2BP:
                            stats_v2["tier_entries_2bp"] += 1
                        elif tier_i == SLIPPAGE_TIER_5BP:
                            stats_v2["tier_entries_5bp"] += 1
                        else:
                            stats_v2["tier_entries_10bp"] += 1
                        rate_buy = (fee.commission_rate + fee.handling_fee
                                    + fee.supervision_fee + tier_i)
                    add_qty = budget / px
                    total_cost = px * add_qty * (1 + rate_buy)
                    if total_cost > cash:
                        continue        # stays queued, retries next open
                    cash -= total_cost
                    old_qty = st.quantity
                    # P4-B3 frozen add accounting: VWAP update only.
                    st.quantity = old_qty + add_qty
                    st.cost_price = ((st.cost_price * old_qty + px * add_qty)
                                    / st.quantity)
                    # high_watermark: continuous max since first fill, never
                    # reset (conservative). trailing_stop_price: never reset
                    # (inactive -> the -8% initial stop follows the VWAP
                    # down automatically; active -> keeps its locked line).
                    # hold_days / tier_reached: unchanged.
                    staged_books[sym]["filled"].add(k)
                    del pending_adds[sym][k]
                    adds_filled_total += 1
                if sym in pending_adds and not pending_adds[sym]:
                    del pending_adds[sym]

        # 1) manage open positions at today's CLOSE
        for sym in list(positions.keys()):
            st = positions[sym]
            # T+1: cannot sell on entry day
            if st.hold_days == 0 and not is_t0(sym):
                st.hold_days += 1
                continue
            px = row_close[sym]
            if pd.isna(px):
                st.hold_days += 1
                continue
            if sym in deferred_exits:
                # P4-B2 sell deferral: exit already decided, executing late.
                action = deferred_exits.pop(sym)
            else:
                action = evaluate(st, px, cfg, signal_reversed=bool(exit_sig[sym].loc[date]))

            if action.should_close:
                if not _fillable(sell_g, sym, i):
                    # P4-B2 sell deferral: no liquidity at this close (e.g.
                    # sealed limit-down) -> retry at next fillable close.
                    deferred_exits[sym] = action
                    # T-20 additive disclosure: count guard-driven deferral
                    # days/episodes (the None path never reads these).
                    deferred_days += 1
                    if first_deferred_date is None:
                        first_deferred_date = str(date.date())
                    deferred_open.add(sym)
                    st.hold_days += 1
                    continue
                if strict_fills and not _real_bar(real_close_mask, sym, i):
                    # T-03-F2 strict_open_fills: suspension day (ffilled
                    # stale close) -> cannot trade; defer with the ORIGINAL
                    # action until the first real-bar close.
                    deferred_exits[sym] = action
                    st.hold_days += 1
                    continue
                qty = st.quantity * action.close_fraction
                gross = qty * px
                if tier_v2 is None:
                    rate_sell = cost_rate   # legacy path (identical arithmetic)
                else:
                    rate_sell = (fee.commission_rate + fee.handling_fee
                                 + fee.supervision_fee
                                 + float(tier_v2.at[date, sym]))
                proceeds = gross * (1 - rate_sell)
                cash += proceeds
                pnl_rate = (px - st.cost_price) / st.cost_price
                trades.append({
                    "date": str(date.date()), "symbol": sym,
                    "reason": action.reason,
                    "price": round(px, 4), "qty": round(qty, 2),
                    "fee": round(gross * rate_sell, 2),
                    "pnl": round((px - st.cost_price) * qty - gross * rate_sell, 2),
                    "pnl_rate": round(pnl_rate, 4),
                    "hold_days": st.hold_days,
                })
                if trade_pnl_mode == "full":
                    # T-03-F1: honest per-trade pnl incl. the BUY-side cost
                    # (legacy 'pnl' above omits it -- audit P0-2, ~13bp/trade;
                    # applies to every tranche scale-out on its closed qty).
                    trades[-1]["pnl_full"] = round(
                        (px - st.cost_price) * qty
                        - gross * cost_rate
                        - st.cost_price * qty * cost_rate, 2)
                if action.close_fraction >= 1.0:
                    if stage_fracs is not None and sym in staged_books:
                        # P4-B3: the staged book dies with the position;
                        # queued adds that never filled are honest drops.
                        staged_books.pop(sym, None)
                        if sym in pending_adds:
                            adds_dropped_total += len(pending_adds.pop(sym))
                        stage_end_cost_px.append(st.cost_price)
                    del positions[sym]
                else:
                    st.quantity -= qty
                    st.tier_reached += 1
                # T-20 additive disclosure: a guard-deferred episode just
                # filled -- close it (episode == decision -> first fillable).
                if sym in deferred_open:
                    deferred_open.discard(sym)
                    deferred_events += 1
            st.hold_days += 1

        # 1b) P4-B3 staged trigger check at today's CLOSE (flag ON only):
        # unfilled tranche k (>= 1) with close <= first_fill*(1+trigger_k)
        # queues for tomorrow's open (level state; first-fill anchor; the
        # T+1 sell guard does not apply -- adds are buys).
        if stage_fracs is not None and staged_books:
            for sym, bk in staged_books.items():
                if sym not in positions:
                    continue
                px_c = row_close[sym]
                if pd.isna(px_c):
                    continue
                for k in range(1, len(stage_fracs)):
                    if k in bk["filled"] or k in pending_adds.get(sym, {}):
                        continue
                    if px_c <= bk["first_fill"] * (1.0 + stage_triggers[k]):
                        pending_adds.setdefault(sym, {})[k] = str(date.date())

        # 2) queue new entries based on today's close signals
        for sym in closes.columns:
            if sym in positions or sym in pending_entries:
                continue
            if len(positions) + len(pending_entries) >= cfg.max_positions:
                break
            if entry_sig[sym].loc[date]:
                pending_entries[sym] = {"queued": str(date.date())}

        # 3) mark-to-market
        pos_val = sum(st.quantity * row_close[sym]
                      for sym, st in positions.items() if sym in row_close)
        if stale_marks:
            # T-03-F2 stale_mark_tag: a day is stale-marked when ANY held
            # position is marked at an ffilled (non-real) close.
            stale_today = False
            for sym in positions:
                j = col_pos.get(sym)
                if j is not None and not bool(real_close_mask[i][j]):
                    stale_today = True
                    break
            stale_flags.append(stale_today)
        eq_today = cash + pos_val
        if parked_bal:
            # T-09 CASH_LEG: on-deposit balance is part of total equity
            eq_today += parked_bal
        equity_curve.append(eq_today)
        if parking_state is not None:
            # T-09 CASH_LEG parking block (appended after close valuation;
            # parked funds were excluded from `cash` all day -> they never
            # funded same-day entries, invariant by construction).
            rate_t = park_rate.iloc[i]
            if pd.isna(rate_t):
                rate_t = 0.0        # no known rate -> no fabricated interest
            interest = parked_bal * float(rate_t) / 100.0 / 252.0
            cash += parked_bal + interest          # settle principal + yield
            parking_state["parking_yield_total"] += interest
            parking_state["parking_accrual_series"].append(round(interest, 6))
            if parked_bal > 0.0:
                parking_state["parked_days"] += 1
            if interest:
                equity_curve[-1] = equity_curve[-1] + interest
            if bool(park_bear.iloc[i]):
                parking_state["bear_days_in_window"] += 1
                eq_close = cash + pos_val          # parked_bal already settled
                parked_bal = min(cash, park_frac * eq_close)
                cash -= parked_bal
            else:
                parked_bal = 0.0                    # non-bear day: full release

    equity = pd.Series(equity_curve, index=dates[:len(equity_curve)])
    # T-20 additive disclosure: episodes still open at window end happened --
    # the position is held at close, exit awaiting a fillable day (counted).
    deferred_events += len(deferred_open)
    if stage_fracs is not None:
        # P4-B3: adds still queued at the window end never filled (honest
        # drops); still-open staged positions close the avg_cost book.
        adds_dropped_total += sum(len(v) for v in pending_adds.values())
        for sym in staged_books:
            if sym in positions:
                stage_end_cost_px.append(positions[sym].cost_price)
    metrics = summarize(equity, trades)
    if trade_pnl_mode == "full":
        # T-03-F1: full-cost per-trade stats under NEW field names only
        # (legacy win_rate/profit_factor keys untouched).
        pnls_full = [t["pnl_full"] for t in trades]
        metrics.update({
            "win_rate_full": round(win_rate(pnls_full), 4),
            "profit_factor_full": round(profit_factor(pnls_full), 4),
            "avg_pnl_full": round(float(np.mean(pnls_full)) if pnls_full else 0.0, 2),
        })
    if report_num_entries:
        # T-03-F6: dual-basis trade count (num_trades counts tranches;
        # num_entries counts distinct position opens).
        metrics["num_entries"] = num_entries
    if fill_guard is not None:
        # T-21: buy-side drops under any guard (new key only when a guard
        # is supplied; the None path never emits it).
        metrics["fill_guard_buy_dropped"] = guard_drops
        # T-20 PAPER_GUARD_DUAL_RAIL: sell-deferral disclosure (additive;
        # P4-B2 fill semantics unchanged, report-only face).
        metrics["fill_guard_sell_deferred_events"] = deferred_events
        metrics["fill_guard_deferred_days_total"] = deferred_days
        metrics["fill_guard_first_deferred_date"] = first_deferred_date
    if entry_size_scale is not None:
        # T-21: filled entries whose nominal was scaled below 1.0.
        metrics["scaled_entries"] = scaled_entries
    if stage_fracs is not None:
        # P4-B3 STAGED_ENTRY: NEW metrics keys only (flag ON); the legacy
        # keyset is never touched (G5 keyset discipline).
        metrics.update({
            "num_adds_filled": adds_filled_total,
            "num_adds_dropped": adds_dropped_total,
            "avg_cost_first": round(
                float(np.mean(stage_first_fill_px))
                if stage_first_fill_px else 0.0, 4),
            "avg_cost_end": round(
                float(np.mean(stage_end_cost_px))
                if stage_end_cost_px else 0.0, 4),
            "adds_per_entry": round(
                adds_filled_total / staged_entries_total
                if staged_entries_total else 0.0, 4),
        })
    if stale_marks:
        # T-03-F2: NEW Sharpe field excluding stale-marked end-days.
        rets = equity.pct_change().tolist()
        kept = [r for k, r in enumerate(rets) if k >= 1 and not stale_flags[k]]
        if len(kept) >= 2:
            m = sum(kept) / len(kept)
            sd = (sum((r - m) ** 2 for r in kept) / (len(kept) - 1)) ** 0.5
            sharpe_ex = (m / sd) * (252 ** 0.5) if sd > 0 else 0.0
        else:
            sharpe_ex = 0.0
        metrics.update({
            "stale_mark_days": int(sum(1 for f in stale_flags if f)),
            "sharpe_ex_stale": round(sharpe_ex, 4),
        })
    if parking_state is not None:
        # T-09 CASH_LEG: NEW metrics keys only (flag ON); legacy keyset
        # untouched (G5 keyset discipline).
        metrics.update({
            "parked_days": parking_state["parked_days"],
            "bear_days_in_window": parking_state["bear_days_in_window"],
            "parking_yield_total": round(
                parking_state["parking_yield_total"], 6),
            "parked_balance_end": round(parked_bal, 2),
            "parking_accrual_series": parking_state["parking_accrual_series"],
        })
    result = {
        "metrics": metrics,
        "trades": trades,
        "equity_curve": [round(v, 2) for v in equity_curve],
    }
    if positions:
        # T-35 (O-2045 s2/s3): positions still held at window end -- the
        # paper intraday-marking and daily-export faces need the held set.
        # ADDITIVE top-level key, emitted only when non-empty (legacy
        # empty-window runs keep the exact legacy keyset); read-side
        # consumers use .get("open_positions", []). Exit priority, T+1
        # fills and the cost model are untouched.
        result["open_positions"] = [
            {"symbol": s, "quantity": round(st.quantity, 2),
             "cost_price": round(st.cost_price, 4),
             "high_watermark": round(st.high_watermark, 4),
             "hold_days": int(st.hold_days)}
            for s, st in sorted(positions.items())]
    if pending_entries:
        # T-35 d2-c (O-2045 s2.1): entries queued at the final close that
        # will fill at the NEXT session's 09:30 open. Export the set so
        # the intraday marks lane can capture that session's real open
        # price (pending_watch) for open-fill verification. ADDITIVE
        # top-level key, emitted only when non-empty (same legacy-keyset
        # discipline as open_positions above). Fill logic, exit priority
        # and the cost model are untouched.
        result["pending_entries"] = [
            {"symbol": s, "queued_date": info["queued"]}
            for s, info in sorted(pending_entries.items())]
    if stats_v2 is not None:
        result["cost_v2"] = stats_v2
    return result
