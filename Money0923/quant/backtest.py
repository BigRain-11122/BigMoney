"""回测引擎：A股规则级日频仿真。

规则：t 日收盘出信号 → t+1 日开盘调仓；T+1 锁定；开盘涨跌停拒单；
整手100股；佣金/印花税/过户费/滑点；单票成交额参与率上限；个股硬止损。
仓位上限与实盘风控同源（股票15%；ETF 50%），保证回测≈实盘。
"""
from __future__ import annotations

import logging
import math
from dataclasses import dataclass

import numpy as np
import pandas as pd

from .config import AppConfig
from .data import PanelData, is_etf, is_t0, limit_up_pct, max_order_shares

log = logging.getLogger("quant.backtest")

LOT = 100


@dataclass
class BTResult:
    equity: pd.Series        # 逐日净值（元）
    invested: pd.Series      # 逐日持仓市值（元）
    trades: list[dict]        # 成交流水
    metrics: dict             # 绩效指标


def _buy_cost_total(amount: float, fee) -> float:
    commission = max(amount * fee.commission_rate, fee.min_commission)
    return amount + commission + amount * fee.transfer_fee


def _sell_net_total(amount: float, fee, exempt_stamp: bool = False) -> float:
    """卖出净入账。ETF/基金转让免征印花税（微观结构专家审查修复）。"""
    commission = max(amount * fee.commission_rate, fee.min_commission)
    stamp = 0.0 if exempt_stamp else amount * fee.stamp_duty
    return amount - commission - stamp - amount * fee.transfer_fee


def compute_metrics(equity: np.ndarray, invested: np.ndarray, trades: list,
                    n_days: int, start_cash: float, wins: int, sell_count: int,
                    turnover: float) -> dict:
    eq = pd.Series(equity)
    ret = eq.pct_change().fillna(0.0)
    years = n_days / 252.0
    end = float(eq.iloc[-1])
    total_return = end / start_cash - 1.0
    cagr = (end / start_cash) ** (1.0 / years) - 1.0 if years > 0 and end > 0 else 0.0
    vol = float(ret.std() * math.sqrt(252))
    sharpe = float(ret.mean() / ret.std() * math.sqrt(252)) if ret.std() > 0 else 0.0
    dd = eq / eq.cummax() - 1.0
    max_dd = float(dd.min()) if len(dd) else 0.0
    calmar = cagr / max(0.05, -max_dd) if max_dd < 0 else (cagr if cagr > 0 else 0.0)
    calmar = max(-3.0, min(3.0, calmar))
    avg_eq = float(eq.mean()) if len(eq) else start_cash
    return {
        "total_return": total_return,
        "cagr": cagr,
        "vol": vol,
        "sharpe": sharpe,
        "max_dd": max_dd,
        "calmar": calmar,
        "win_rate": wins / sell_count if sell_count else 0.0,
        "wins": wins,          # 原始盈利卖出次数（适应度做拉普拉斯收缩用）
        "sell_count": sell_count,
        "n_trades": len(trades),
        "turnover": turnover / avg_eq / years if years > 0 and avg_eq > 0 else 0.0,
        "exposure": float((invested / eq).mean()) if len(eq) else 0.0,
    }


def equal_weight_benchmark(panel: PanelData, start_cash: float = 1_000_000.0) -> pd.Series:
    """股票池等权持有基准（用于对比参考）。"""
    ret = panel.close.pct_change().mean(axis=1, skipna=True).fillna(0.0)
    return (1.0 + ret).cumprod() * start_cash


def run_backtest(panel: PanelData, weights: pd.DataFrame, cfg: AppConfig,
                 start_cash: float | None = None, apply_caps: bool = True) -> BTResult:
    dates = panel.dates
    codes = panel.codes
    n, m = len(dates), len(codes)
    fee, risk = cfg.fee, cfg.risk
    start_cash = float(start_cash if start_cash is not None else risk.initial_capital)

    # 期货分流（2026-09-21 全品种指令的架构裁决）：非零权重列全为 F.* 的组合走期货专用
    # 引擎（保证金/双向/按手/T+0，与股票股数模型根本不同）；混合权重暂不支持——空仓曲线
    # +留痕，绝不让股票引擎错误撮合期货列（团队组建层另设同资产类别约束防混合成形）。
    from .futures import is_futures as _is_futures
    _w = weights.fillna(0.0)
    _nz = [c for c in _w.columns if (_w[c] != 0.0).any()]
    _nz_fut = [c for c in _nz if _is_futures(c)]
    if _nz_fut:
        if len(_nz_fut) == len(_nz):
            from .futures_backtest import run_futures_backtest
            return run_futures_backtest(panel, weights, cfg, start_cash)
        log.warning("混合股票+期货权重暂不支持，按空仓计（非零列: %s）",
                    ",".join(map(str, _nz[:10])))
        eq_flat = np.full(len(dates), start_cash, dtype=float)
        metrics = compute_metrics(eq_flat, np.zeros(len(dates)), [], len(dates),
                                  start_cash, 0, 0, 0.0)
        return BTResult(equity=pd.Series(eq_flat, index=dates),
                        invested=pd.Series(np.zeros(len(dates)), index=dates),
                        trades=[], metrics=metrics)

    # 决策于 t-1 收盘 → t 日开盘执行：权重右移一行
    wdf = weights.reindex(dates).shift(1)
    wmat = np.nan_to_num(wdf.to_numpy(dtype=float), nan=0.0)
    if apply_caps:
        # 分资产仓位上限：股票15%（用户红线）；ETF为一篮子股票允许50%集中（轮动类经典模型需要）
        cap_arr = np.array([risk.max_etf_position_pct if is_etf(c) else risk.max_position_pct
                            for c in codes])
        wmat = np.minimum(wmat, cap_arr)

    op = panel.open.to_numpy(dtype=float)
    hi = panel.high.to_numpy(dtype=float)
    lo = panel.low.to_numpy(dtype=float)
    cl = panel.close.to_numpy(dtype=float)
    am = panel.amount.to_numpy(dtype=float)
    # 涨跌停用"数据推断的真实限制"（创业板ETF 20% 等），与校验闸同源，避免真实行情被误拒单
    from .validation import effective_limit
    limit_arr = np.array([effective_limit(c) for c in codes])
    # T+0品种（跨境/债券/黄金/商品ETF 当日买当日可卖）与单笔申报上限（官方规则）
    t0_arr = np.array([is_t0(c) for c in codes])
    order_cap_arr = np.array([max_order_shares(c) for c in codes], dtype=np.int64)
    # 期货分支（用户指令2026-09-21"期货/基金/股票全品种"）：F.* 列按手数撮合，
    # 保证金占用而非全额；负持仓=空头（双向）。等效股数=手数×乘数。
    from .futures import is_futures, futures_meta
    fut_arr = np.array([is_futures(c) for c in codes])
    if fut_arr.any():
        f_margin = np.array([futures_meta(c)["margin"] for c in codes])
        f_mult = np.array([futures_meta(c)["mult"] for c in codes])
        f_fee = np.array([futures_meta(c)["fee_lot"] for c in codes])
    else:
        f_margin = f_mult = f_fee = np.ones(m)

    pos_shares = np.zeros(m, dtype=np.int64)   # 总持仓（股）
    pos_avail = np.zeros(m, dtype=np.int64)    # 可卖（T+1 已解锁）
    locked = np.zeros(m, dtype=np.int64)       # 昨日买入锁定
    pos_cost = np.zeros(m, dtype=float)        # 含费平均成本（元/股）
    pos_bought_at = np.full(m, -1, dtype=np.int64)  # 最近一次买入日索引（计时离场用）
    cash = start_cash
    prev_close = np.full(m, np.nan)

    equity_arr = np.zeros(n)
    invested_arr = np.zeros(n)
    trades: list[dict] = []
    wins = sell_count = 0
    turnover = 0.0
    date_strs = [d.strftime("%Y-%m-%d") for d in dates]
    # 分档滑点（小市值×2.0，其余×1.0）：无 slip_mult 时全 1.0
    slip_arr = panel.slip_mult if getattr(panel, "slip_mult", None) is not None else np.ones(m)
    # 国债逆回购隔夜现金计息（三端一致）：昨日收盘现金按当日GC001真实历史利率
    # 计息——现金不是死钱，防御型策略不被系统性低估；无利率数据时None=诚实跳过
    _repo_y = None
    _repo_min_lend = float(getattr(risk, "repo_min_lend", 1000.0))
    try:
        from . import repo as qrepo
        _repo_y = qrepo.overnight_cash_yield(date_strs, cfg)
    except Exception:  # noqa: BLE001
        _repo_y = None

    def _do_sell(j: int, shares: int, raw_price: float, reason: str) -> None:
        nonlocal cash, wins, sell_count, turnover
        shares = min(shares, int(pos_avail[j]))
        shares = shares // LOT * LOT
        if shares <= 0 or not math.isfinite(raw_price):
            return
        fill = raw_price * (1.0 - fee.slippage * float(slip_arr[j]))
        amount = shares * fill
        net = _sell_net_total(amount, fee, exempt_stamp=is_etf(codes[j]))
        cash += net
        pos_shares[j] -= shares
        pos_avail[j] -= shares
        pnl = (net / shares - pos_cost[j]) * shares
        if pnl > 0:
            wins += 1
        sell_count += 1
        turnover += amount
        trades.append({"date": _cur_date, "code": codes[j], "side": "sell", "price": round(fill, 3),
                        "shares": int(shares), "amount": round(amount, 2), "pnl": round(pnl, 2),
                        "reason": reason})
        if pos_shares[j] == 0:
            pos_cost[j] = 0.0
            pos_bought_at[j] = -1

    def _do_buy(j: int, shares: int, raw_price: float, reason: str = "rebalance") -> None:
        nonlocal cash, turnover
        if shares <= 0 or not math.isfinite(raw_price):
            return
        fill = raw_price * (1.0 + fee.slippage * float(slip_arr[j]))
        amount = shares * fill
        total_cost = _buy_cost_total(amount, fee)
        if total_cost > cash:  # 现金不够则缩量
            shares = int(cash / (fill * (1 + fee.commission_rate + fee.transfer_fee)) ) // LOT * LOT
            if shares <= 0:
                return
            amount = shares * fill
            total_cost = _buy_cost_total(amount, fee)
        cash -= total_cost
        pos_cost[j] = (pos_cost[j] * pos_shares[j] + total_cost) / (pos_shares[j] + shares)
        pos_shares[j] += shares
        pos_bought_at[j] = _cur_i  # 加仓重置持有计时（近似：整仓按最后买入日计时）
        if t0_arr[j]:
            pos_avail[j] += shares  # T+0品种（跨境/债券/黄金/商品ETF）当日可卖
        else:
            locked[j] += shares  # T+1：今日买入锁定
        turnover += amount
        trades.append({"date": _cur_date, "code": codes[j], "side": "buy", "price": round(fill, 3),
                        "shares": int(shares), "amount": round(amount, 2), "pnl": 0.0,
                        "reason": reason})

    _cur_date = ""
    _cur_i = -1
    day_start_eq = start_cash  # 日熔断基准（每日收盘滚动更新）
    _ret_hist: list[float] = []  # 近端组合日收益（波动率目标用，仅历史信息）
    timed_out_today: set[int] = set()
    for i in range(n):
        _cur_date = date_strs[i]
        _cur_i = i
        timed_out_today = set()
        # 0) 国债逆回购归还+计息：资金T+1开市前到账，今日开盘现金含昨夜利息
        if _repo_y is not None and i >= 1 and cash >= _repo_min_lend:
            cash += cash * _repo_y[i - 1]
        # 1) T+1 解锁：昨天买的今天可用
        pos_avail += locked
        locked[:] = 0

        pc = prev_close
        o, h, l, c = op[i], hi[i], lo[i], cl[i]
        has_bar = ~np.isnan(c) & ~np.isnan(o)
        known_prev = ~np.isnan(pc)
        # 涨跌停价：按最小变动位数四舍五入（ETF 0.001元/股票 0.01元，交易所口径而非银行家舍入）
        tick_arr = np.array([0.001 if is_etf(cd) else 0.01 for cd in codes])
        up_lim = np.where(known_prev, np.floor(pc * (1.0 + limit_arr) / tick_arr + 0.5) * tick_arr, np.nan)
        dn_lim = np.where(known_prev, np.floor(pc * (1.0 - limit_arr) / tick_arr + 0.5) * tick_arr, np.nan)

        with np.errstate(invalid="ignore"):
            can_buy = has_bar & known_prev & (o < up_lim - 1e-9) & ~np.isnan(am[i]) & (am[i] > 0)
            can_sell = has_bar & known_prev & (o > dn_lim + 1e-9)

        held_val = pos_shares * np.where(known_prev, pc, pos_cost)
        equity_prev = cash + float(held_val.sum())

        # 2) 计时离场：持股超 max_hold_days（默认15个交易日）开盘强平（可卖部分，跌停顺延）
        if risk.max_hold_days > 0 and (pos_avail > 0).any():
            stale_mask = (pos_avail > 0) & (pos_bought_at >= 0) & (i - pos_bought_at >= risk.max_hold_days)
            for j in np.nonzero(stale_mask)[0]:
                if can_sell[j]:
                    _do_sell(j, int(pos_avail[j]), o[j], "time_exit")
                    timed_out_today.add(int(j))

        # 3) 开盘止损（-8% 硬止损，仅可卖部分）；当日禁止回买（防止损被调仓架空）
        if risk.stop_loss_pct > 0 and (pos_avail > 0).any():
            stop_price = pos_cost * (1.0 - risk.stop_loss_pct)
            stop_mask = (pos_avail > 0) & (pos_cost > 0) & can_sell & (o <= stop_price)
            for j in np.nonzero(stop_mask)[0]:
                _do_sell(j, int(pos_avail[j]), o[j], "stop_open")
                timed_out_today.add(int(j))

        # 4) 调仓（目标来自昨日收盘信号）；今日止损/计时离场的标的当日不回买；
        #    单日亏损熔断（实盘同源规则）：当日权益较日初亏超限 → 只卖不买；
        #    波动率目标（理性仓位）：近20日实现年化波动 > target_vol → 目标权重线性降杠杆
        tw = wmat[i].copy()
        if risk.target_vol > 0 and len(_ret_hist) >= 20:
            ann_vol_realized = float(np.std(_ret_hist[-20:])) * math.sqrt(252.0)
            if ann_vol_realized > risk.target_vol > 0:
                floor = max(0.05, float(getattr(risk, "vol_scale_floor", 0.25)))
                _vol_scale = max(floor, risk.target_vol / ann_vol_realized)
                tw = tw * _vol_scale
        day_breaker = (risk.daily_loss_limit_pct > 0
                       and equity_prev < day_start_eq * (1.0 - risk.daily_loss_limit_pct))
        if np.any(tw > 0):
            # 持仓数上限：保留权重最大的 max_positions 只
            pos_idx = np.nonzero(tw)[0]
            if len(pos_idx) > risk.max_positions:
                keep = pos_idx[np.argsort(tw[pos_idx])[::-1][: risk.max_positions]]
                tw = np.where(np.isin(np.arange(m), keep), tw, 0.0)

            target_val = tw * equity_prev
            cur_val = pos_shares * o
            thresh = 0.005 * equity_prev  # 0.5% 账户以下的调仓忽略（降换手）

            # 先卖后买（卖出同样受成交额参与率上限）
            sell_val = cur_val - target_val
            sell_val = np.where((sell_val > thresh) & can_sell, sell_val - 0.5 * thresh, 0.0)
            # 最短持股（用户规则：3~15天级别）：不满 min_hold_days 日不因调仓卖出
            # （止损与超时离场在步骤2/3已执行，不受此限——风险永远优先）
            if risk.min_hold_days > 0:
                too_young = (pos_shares > 0) & (pos_bought_at >= 0) \
                    & ((i - pos_bought_at) < risk.min_hold_days)
                sell_val = np.where(too_young, 0.0, sell_val)
            fee_margin = 1.0 + fee.commission_rate + fee.transfer_fee
            for j in np.nonzero(sell_val > 0)[0]:
                fill_est = o[j] * (1.0 - fee.slippage * float(slip_arr[j]))
                max_amt = am[i][j] * risk.max_participation
                shares = int(min(sell_val[j], max_amt) / fill_est // LOT) * LOT
                if shares > 0:
                    _do_sell(j, shares, o[j], "rebalance")

            budget = cash - equity_prev * risk.min_keep_cash_pct
            if budget > 0 and not day_breaker:  # 日熔断：当日停止新开仓（只减不加，与实盘同源）
                cur_val = pos_shares * o
                buy_val = target_val - cur_val
                buy_val = np.where((buy_val > thresh) & can_buy & (tw > 0), buy_val, 0.0)
                order_idx = np.argsort(-tw)  # 权重大者优先
                for j in order_idx:
                    if buy_val[j] <= 0 or budget <= 0:
                        continue
                    if int(j) in timed_out_today:
                        continue  # 今日止损/计时离场的标的不回买（冷却1日）
                    fill = o[j] * (1.0 + fee.slippage * float(slip_arr[j]))  # 与实际成交同口径
                    # 成交额参与率上限 + 单笔申报上限（创业板30万股/主板100万股/基金100万份）
                    max_amt = am[i][j] * risk.max_participation
                    shares = min(int(buy_val[j] / fill // LOT) * LOT,
                                 int(max_amt / fill // LOT) * LOT,
                                 int(order_cap_arr[j]))
                    est_cost = shares * fill * fee_margin
                    if est_cost > budget:
                        shares = int(budget / fill / fee_margin // LOT) * LOT
                    if shares > 0:
                        before = cash
                        _do_buy(j, shares, o[j])
                        budget -= before - cash

        # 5) 盘中止损：开盘价在止损价上方、盘中跌破才按止损价成交；
        #    一字跌停（开盘即封死）由 can_sell 排除，跳空低开由开盘止损处理（P0修复）
        if risk.stop_loss_pct > 0 and (pos_avail > 0).any():
            stop_price = pos_cost * (1.0 - risk.stop_loss_pct)
            stop_mask = (pos_avail > 0) & (pos_cost > 0) & has_bar & (o > stop_price) \
                        & (l <= stop_price) & (stop_price >= dn_lim)
            for j in np.nonzero(stop_mask)[0]:
                _do_sell(j, int(pos_avail[j]), stop_price[j], "stop_intraday")
                timed_out_today.add(int(j))

        # 6) 收盘记账（次日熔断基准用当日收盘权益）
        mark = np.where(np.isnan(c), np.where(np.isnan(o), np.where(known_prev, pc, pos_cost), o), c)
        mv = float((pos_shares * mark).sum())
        equity_arr[i] = cash + mv
        invested_arr[i] = mv
        if i >= 1 and equity_arr[i - 1] > 0:  # 波动率目标：记录近端日收益（仅历史）
            _ret_hist.append(equity_arr[i] / equity_arr[i - 1] - 1.0)
            _ret_hist = _ret_hist[-60:]
        day_start_eq = equity_arr[i]
        prev_close = np.where(np.isnan(c), prev_close, c)

    metrics = compute_metrics(equity_arr, invested_arr, trades, n, start_cash,
                              wins, sell_count, turnover)
    return BTResult(
        equity=pd.Series(equity_arr, index=dates),
        invested=pd.Series(invested_arr, index=dates),
        trades=trades,
        metrics=metrics,
    )
