"""期货专用组合回测引擎（CTA 策略评测专用路径，2026-09-21 全品种指令）。

为什么不塞进股票引擎：股票引擎的股数/T+1/全额现金模型与期货的
保证金/双向/按手计费/T+0 根本不同——与其在实盘主路径里堆 if-futures
分支（污染股票主战场），不如按权重矩阵自动分流：权重只含 F.* 列的
组合（CTA 策略的结构特征）进本引擎，精确实现期货撮合。

记账模型（现金池 + 带符号市值，统一 delta 口径）：
- 手数为带符号整数：多头>0、空头<0；目标手数 = 权重(保证金份额)×上日权益
  ÷(乘数×开盘价×保证金率)——期货仓位由保证金定义（名义权重语义下小账户
  永远凑不齐一手，冒烟实测抓出）
- 统一成交流：现金 += -Δ手数×乘数×成交价 - |Δ手数|×手续费
  （开多现金流出名义、开空流入名义；权益在成交瞬间不变，盈亏随价格漂移自动体现）
- 保证金约束：Σ|手数|×乘数×价×margin ≤ 上日权益（超限按占用最大品种逐手缩减）
- 单品种保证金份额 ≤ risk.max_etf_position_pct×权益（用户红线对期货的对应纪律）
- T+0（期货规则）；手续费按手×fee_lot（开平各收）
- 开盘触及昨收±品种涨跌幅 → 当日不开新仓（涨跌停近似；平仓始终允许=V1简化）
- 持仓均价 avg_entry 跟踪：平仓已实现盈亏 = (成交价-均价)×乘数×手数×方向 - 手续费
- V1 简化（诚实披露）：无逐仓止损（CTA 信号自带通道离场）；交割/移月成本、
  保证金追缴、结算价制度不建模，用主力连续价近似
"""
from __future__ import annotations

import math

import numpy as np
import pandas as pd

from .backtest import BTResult, compute_metrics
from .config import AppConfig
from .futures import FUT_LIMITS, futures_meta, fut_variety, is_futures


def run_futures_backtest(panel, weights: pd.DataFrame, cfg: AppConfig,
                        start_cash: float | None = None) -> BTResult:
    """期货组合回测：weights 为 dates×列 目标权重（仅 F.* 列非零；决策右移一日）。"""
    risk = cfg.risk
    start = float(start_cash if start_cash is not None else risk.initial_capital)
    fut_cols = [c for c in weights.columns if is_futures(c)]
    if not fut_cols:
        raise ValueError("期货引擎收到无 F.* 列的权重矩阵")

    dates = panel.dates
    if all(c in panel.open.columns for c in fut_cols):
        # 面板已含 F.* 列（测试/旧路径兼容）：直接用面板价格
        op = panel.open.reindex(columns=fut_cols).to_numpy(dtype=float)
        cl = panel.close.reindex(columns=fut_cols).to_numpy(dtype=float)
    else:
        # CTA 自服务架构：面板永不并入 F.*（防股票策略选期货刷杠杆分）→ 按窗口自取
        from .futures import futures_window
        fw = futures_window(dates)
        op = np.full((len(dates), len(fut_cols)), np.nan)
        cl = np.full((len(dates), len(fut_cols)), np.nan)
        for j, c in enumerate(fut_cols):
            fdf = fw.get(c)
            if fdf is None:
                continue
            op[:, j] = fdf["open"].to_numpy(dtype=float)
            cl[:, j] = fdf["close"].to_numpy(dtype=float)
    wdf = weights.reindex(dates).shift(1)
    wmat = np.nan_to_num(wdf[fut_cols].to_numpy(dtype=float), nan=0.0)
    m = len(fut_cols)
    mult = np.array([float(futures_meta(c)["mult"]) for c in fut_cols])
    margin = np.array([float(futures_meta(c)["margin"]) for c in fut_cols])
    fee_lot = np.array([float(futures_meta(c)["fee_lot"]) for c in fut_cols])
    lim = np.array([FUT_LIMITS.get(fut_variety(c), 0.08) for c in fut_cols])
    cap_w = float(getattr(risk, "max_etf_position_pct", 0.5))

    lots = np.zeros(m, dtype=np.int64)
    avg_entry = np.zeros(m, dtype=float)
    prev_close = np.full(m, np.nan)
    cash = start
    n = len(dates)
    equity_arr = np.zeros(n)
    invested_arr = np.zeros(n)
    trades: list[dict] = []
    wins = sell_count = 0
    turnover = 0.0
    date_strs = [d.strftime("%Y-%m-%d") for d in dates]
    # 国债逆回购隔夜计息（与股票引擎三端一致）：CTA账户闲置保证金外现金同样借出GC001
    _repo_y = None
    _repo_min_lend = float(getattr(risk, "repo_min_lend", 1000.0))
    try:
        from . import repo as qrepo
        _repo_y = qrepo.overnight_cash_yield(date_strs, cfg)
    except Exception:  # noqa: BLE001
        _repo_y = None

    for i in range(n):
        o, c = op[i], cl[i]
        # 逆回购资金T+1开市前归还：今日现金含昨夜利息（计息基准=昨日收盘现金）
        if _repo_y is not None and i >= 1 and cash >= _repo_min_lend:
            cash += cash * _repo_y[i - 1]
        mark0 = np.where(np.isfinite(c), c, o)
        eq_prev = cash + float(np.nansum(lots * mult * np.where(np.isfinite(mark0), mark0, 0.0)))
        known = np.isfinite(prev_close)
        up = prev_close * (1.0 + lim)
        dn = prev_close * (1.0 - lim)
        tradable = np.isfinite(o) & (eq_prev > 0)

        # —— 目标手数（权重=保证金份额：期货仓位由保证金定义；涨跌停日不开新仓；
        #    单品种保证金 ≤ risk.max_etf_position_pct×权益=用户红线对期货的对应纪律）——
        tw = wmat[i]
        want = np.zeros(m, dtype=np.int64)
        for j in range(m):
            if not tradable[j] or tw[j] == 0.0 or not known[j]:
                continue
            if tw[j] > 0 and o[j] >= up[j] - 1e-9:
                continue  # 开多撞涨停板
            if tw[j] < 0 and o[j] <= dn[j] + 1e-9:
                continue  # 开空撞跌停板
            margin_share = abs(tw[j]) * eq_prev
            margin_share = min(margin_share, cap_w * eq_prev)
            lots_raw = margin_share / (mult[j] * o[j] * margin[j])
            want[j] = int(math.copysign(lots_raw, tw[j]))

        # —— 保证金预算：占用超上日权益则逐手缩减最大占用品种 ——
        usage = np.abs(want) * mult * np.nan_to_num(o) * margin
        guard = 0
        while usage.sum() > eq_prev and (np.abs(want) > 0).any():
            j = int(np.nanargmax(usage))
            want[j] += -1 if want[j] > 0 else 1
            usage = np.abs(want) * mult * np.nan_to_num(o) * margin
            guard += 1
            if guard > 10000:
                break

        # —— 调仓到目标：先平后开，统一口径（任意手数变化 d：现金 += -d×乘数×价格）——
        for j in range(m):
            if not tradable[j]:
                continue
            cur, tgt = int(lots[j]), int(want[j])
            if cur == tgt:
                continue
            # 平仓段：翻向先全平；同向减仓平差额；同向加仓不在此段
            close_qty = 0
            if cur != 0:
                if cur * tgt < 0:
                    close_qty = cur            # 翻向：清零
                elif abs(tgt) < abs(cur):
                    close_qty = cur - tgt      # 同向减仓（带符号）
            if close_qty != 0:
                direction = 1 if cur > 0 else -1
                qty = abs(close_qty)
                pnl = (o[j] - avg_entry[j]) * direction * mult[j] * qty - qty * fee_lot[j]
                cash += close_qty * mult[j] * o[j] - qty * fee_lot[j]
                trades.append({"date": date_strs[i], "code": fut_cols[j],
                               "side": "sell" if direction > 0 else "buy",
                               "shares": int(qty), "price": round(float(o[j]), 3),
                               "amount": round(qty * mult[j] * o[j], 2),
                               "pnl": round(pnl, 2), "reason": "fut_close"})
                wins += 1 if pnl > 0 else 0
                sell_count += 1
                turnover += qty * mult[j] * o[j]
                lots[j] -= close_qty
                if lots[j] == 0:
                    avg_entry[j] = 0.0
                cur = int(lots[j])
            # 开仓段：至目标（可跨零翻向）
            delta = tgt - cur
            if delta != 0:
                cash += -delta * mult[j] * o[j] - abs(delta) * fee_lot[j]
                old_abs, add_abs = abs(cur), abs(delta)
                if cur * delta >= 0:
                    avg_entry[j] = ((avg_entry[j] * old_abs + o[j] * add_abs)
                                    / (old_abs + add_abs)) if (old_abs + add_abs) else o[j]
                else:
                    avg_entry[j] = o[j]  # 翻向后剩余部分按新价入场
                trades.append({"date": date_strs[i], "code": fut_cols[j],
                               "side": "buy" if delta > 0 else "sell",
                               "shares": int(abs(delta)), "price": round(float(o[j]), 3),
                               "amount": round(abs(delta) * mult[j] * o[j], 2),
                               "pnl": 0.0, "reason": "fut_open"})
                turnover += abs(delta) * mult[j] * o[j]
                lots[j] = tgt

        # —— 收盘记账 ——
        mark = np.where(np.isfinite(c), c, np.where(np.isfinite(o), o, np.nan))
        eq = cash + float(np.nansum(lots * mult * np.where(np.isfinite(mark), mark, 0.0)))
        equity_arr[i] = eq
        invested_arr[i] = float(np.nansum(np.abs(lots) * mult
                                          * np.where(np.isfinite(mark), mark, 0.0)))
        prev_close = np.where(np.isfinite(c), c, prev_close)

    metrics = compute_metrics(equity_arr, invested_arr, trades, n, start,
                              wins, sell_count, turnover)
    metrics["n_trades"] = len(trades)
    metrics["win_rate"] = (wins / sell_count) if sell_count else 0.0
    return BTResult(equity=pd.Series(equity_arr, index=dates),
                    invested=pd.Series(invested_arr, index=dates),
                    trades=trades, metrics=metrics)
