"""风控引擎：模拟盘/实盘共用（回测内的仓位截断同源于此配置）。

稳健档（用户指定）：小散户定位，10万本金、短线日频、单笔持股3~15个交易日。
- 单只股票 ≤ 15% / 单只ETF ≤ 50% 组合市值；最多 8 只持仓
- 个股 -8% 硬止损（风险离场不受最短持股限制）
- 最短持股 3 个交易日（调仓卖出受限；止损/超时离场不受限）
- 最高持股 15 个交易日 → 超时强制离场
- 出局机制（2026-09-21 用户指令"我顶一个亏完出局，但不能盘中波动就出局"）：
  · 盘中波动永不触发出局类动作（旧"单日-3%熔断"已两端一致停用）
  · 回撤停机线 10%（用户确认红线）：只看收盘结算，停机=人工复盘后可恢复
  · 毁灭出局线 ruin_loss_pct（亏完出局）：收盘权益≤本金×(1-80%) → 永久出局
"""
from __future__ import annotations

import datetime as dt
import logging

import pandas as pd

from . import clock
from .config import AppConfig
from .data import is_etf, max_order_shares
from .state import halt_now

log = logging.getLogger("quant.risk")

LOT = 100
MIN_TRADE_VALUE = 3000.0  # 低于此金额的调仓单直接忽略（降低碎片单）


class RiskManager:

    def __init__(self, cfg: AppConfig, state: dict):
        self.cfg = cfg
        self.state = state
        self.risk = cfg.risk

    # -------------------------------------------------- 日级状态

    def refresh_day(self, today_key: str, equity: float) -> None:
        """新交易日簿记：重置日基准、解锁 T+1、更新高水位。
        出局机制改革（2026-09-21 用户指令"不能盘中波动就出局"）：
        本函数盘中被高频调用，故只做簿记——回撤停机/毁灭出局判定全部移至
        settle_day（收盘结算唯一判定点），高水位也只用收盘权益更新
        （盘中冲高不抬高回撤基准，防变相的盘中波动触发）。"""
        acc = self.state["account"]
        if acc.get("day_key") != today_key:
            acc["day_key"] = today_key
            acc["day_start_equity"] = equity
            acc["daily_pnl"] = 0.0
            # T+1 解锁：昨日及更早买入的可卖
            for pos in acc["positions"].values():
                locked = pos.get("locked") or {}
                pos["available"] = pos.get("available", 0) + sum(locked.values())
                pos["locked"] = {}

    def settle_day(self, today_key: str, equity: float,
                   halt_pct: float | None = 0.0) -> None:
        """收盘结算检查——出局类动作的唯一判定点（盘中波动永不触发）。

        ① 回撤停机（halt_pct 参数化，2026-09-21 用户指令"根据策略来，激进的
           亏8成都行，但亏完就永远出局"）：分仓制下停机权下放到各风格仓
           （S1 10%/S2 20%/S3 激进仓不停机），账户级调用传 halt_pct=None
           跳过全局停机——统一紧线会勒死激进风格。
        ② 毁灭出局线 ruin_loss_pct（用户"亏完出局"）：
           收盘权益 ≤ 初始本金×(1-ruin_loss_pct) → 永久出局：停机+留痕+宣告，
           不自动恢复，残值保留（亏80%需+400%回本=数学实质亏完）。"""
        acc = self.state["account"]
        # 高水位：只用收盘权益（盘中冲高不抬高基准）
        if equity > acc.get("equity_high", 0.0):
            acc["equity_high"] = equity
        date_str = today_key[:4] + "-" + today_key[4:6] + "-" + today_key[6:]
        # ② 毁灭出局（先判毁灭：优先级高于停机）
        ruin_line = self.cfg.risk.initial_capital * (1.0 - self.risk.ruin_loss_pct)
        if self.risk.ruin_loss_pct > 0 and equity <= ruin_line:
            self.state["ruined_at"] = dt.datetime.now().isoformat(timespec="seconds")
            self.state.setdefault("risk_events", []).append({
                "date": date_str, "type": "ruin",
                "detail": f"毁灭出局线触发：收盘权益 {equity:,.0f} ≤ 本金×{1 - self.risk.ruin_loss_pct:.0%}"
                          f"（{ruin_line:,.0f}）——账户永久出局，残值保留，人工复盘后另行处置"})
            self.state["risk_events"] = self.state["risk_events"][-100:]
            halt_now(self.state,
                     f"毁灭出局（亏完出局线 {self.risk.ruin_loss_pct:.0%}）：收盘权益 {equity:,.0f} "
                     f"≤ 出局线 {ruin_line:,.0f}。账户永久出局，不自动恢复。")
            return
        # ① 回撤停机（结算口径；halt_pct=None → 本级不设停机，只毁灭线管辖）
        if halt_pct is None:
            return
        line = float(halt_pct)
        high = acc.get("equity_high", 0.0)
        if line > 0 and high > 0 and not self.state["risk"]["halt"]:
            dd = equity / high - 1.0
            if dd < -line:
                self.state.setdefault("risk_events", []).append({
                    "date": date_str, "type": "drawdown_halt",
                    "detail": f"收盘回撤 {dd:.1%} 触及停机线 {line:.0%}（结算口径，"
                              f"盘中波动不触发）——停机等人工复盘"})
                self.state["risk_events"] = self.state["risk_events"][-100:]
                halt_now(self.state,
                         f"组合收盘回撤 {dd:.1%} 触及停机线 {line:.0%}，"
                         f"已全停机，请人工复盘后执行 run.py resume")

    def note_daily_loss(self, today_key: str, equity: float) -> None:
        """日亏损观察（旧日熔断通道，2026-09-21 已停用）：
        daily_loss_limit_pct=0 即不干预——日亏损不是出局理由，波动不打断系统。
        极端广度闸（市场环境级，非自身波动）仍复用 daily_breaker_date 通道在 paper 层直接设置。"""
        if self.risk.daily_loss_limit_pct <= 0:
            return
        acc = self.state["account"]
        base = acc.get("day_start_equity", 0.0)
        if base <= 0:
            return
        day_ret = equity / base - 1.0
        if day_ret < -self.risk.daily_loss_limit_pct:
            if self.state["risk"]["daily_breaker_date"] != today_key:
                log.warning("单日亏损 %.2f%% 触发熔断：今日停止新开仓", day_ret * 100)
                # 风控事件审计（统计中心可见）
                self.state.setdefault("risk_events", []).append({
                    "date": today_key[:4] + "-" + today_key[4:6] + "-" + today_key[6:],
                    "type": "daily_breaker",
                    "detail": f"单日亏损 {day_ret * 100:.2f}% 触发熔断：当日停止新开仓"})
                self.state["risk_events"] = self.state["risk_events"][-100:]
            self.state["risk"]["daily_breaker_date"] = today_key

    def halt_active(self) -> bool:
        return bool(self.state["risk"]["halt"])

    def can_open_new(self, today_key: str) -> bool:
        if self.halt_active():
            return False
        return self.state["risk"]["daily_breaker_date"] != today_key

    # -------------------------------------------------- 订单生成

    def plan_orders(self, target_w: dict[str, float], positions: dict, prices: dict,
                    equity: float, cash: float, today_key: str) -> list[dict]:
        """按目标权重差生成调仓订单（先卖后买，含全部仓位约束）。"""
        risk = self.risk
        orders: list[dict] = []

        # 期货（F.*）走手数子规划器（保证金/双向/按手，与 futures_backtest 同口径）；
        # 股票分支只处理股票/ETF 正权重（原逻辑零改动）。
        from .futures import is_futures as _is_fut
        tw_fut = {c: float(w) for c, w in target_w.items() if _is_fut(c)}
        if tw_fut:
            orders.extend(self._plan_fut_orders(tw_fut, positions, prices, equity, today_key))
        target_w = {c: float(w) for c, w in target_w.items() if not _is_fut(c)}

        # 分资产仓位上限：股票15%（用户红线）/ ETF 50%（一篮子股票）
        tw = {c: min(w, risk.max_etf_position_pct if is_etf(c) else risk.max_position_pct)
              for c, w in target_w.items() if w > 0}
        if len(tw) > risk.max_positions:
            keep = sorted(tw.items(), key=lambda kv: kv[1], reverse=True)[: risk.max_positions]
            tw = dict(keep)

        cur_val: dict[str, float] = {}
        for c, pos in positions.items():
            p = prices.get(c, {}).get("price") or 0.0
            if p <= 0:
                p = pos.get("cost", 0.0)
            cur_val[c] = pos.get("shares", 0) * p

        # 卖出（回测同规则：目标低于现值超过 0.5% 账户才动）
        for c, v in cur_val.items():
            if v < MIN_TRADE_VALUE:
                continue
            # 最短持股（3~15天级别）：不满 min_hold_days 日不因调仓卖出（止损/超时离场不受限）
            if risk.min_hold_days > 0 and self.held_trade_days(positions[c], today_key) < risk.min_hold_days:
                continue
            target = tw.get(c, 0.0) * equity
            sell_val = v - target - 0.005 * equity
            if sell_val < MIN_TRADE_VALUE:
                continue
            p = prices.get(c, {}).get("price") or positions[c].get("cost", 0.0)
            if p <= 0:
                continue
            shares = int(sell_val / p // LOT) * LOT
            avail = positions[c].get("available", 0)
            shares = min(shares, avail // LOT * LOT)
            if shares > 0:
                orders.append({"code": c, "side": "sell", "shares": int(shares), "reason": "rebalance"})

        # 买入（无熔断时）
        if self.can_open_new(today_key):
            budget = cash - equity * risk.min_keep_cash_pct
            for c, w in sorted(tw.items(), key=lambda kv: kv[1], reverse=True):
                if budget < MIN_TRADE_VALUE:
                    break
                p = prices.get(c, {}).get("price") or 0.0
                if p <= 0:
                    continue
                buy_val = min(w * equity - cur_val.get(c, 0.0), budget)
                if buy_val < max(MIN_TRADE_VALUE, 0.005 * equity):
                    continue
                shares = int(buy_val / p // LOT) * LOT
                shares = min(shares, max_order_shares(c))  # 单笔申报上限（官方规则）
                if shares <= 0:
                    continue
                cost_est = shares * p * 1.003  # 预留费用
                if cost_est > budget:
                    shares = min(int(budget / p / 1.003 // LOT) * LOT, max_order_shares(c))
                if shares > 0:
                    orders.append({"code": c, "side": "buy", "shares": int(shares), "reason": "rebalance"})
                    budget -= shares * p * 1.003
        return orders

    def _plan_fut_orders(self, tw_fut: dict[str, float], positions: dict,
                         prices: dict, equity: float, today_key: str) -> list[dict]:
        """期货调仓单：手数模型，与 futures_backtest 同口径（V1 诚实简化两边一致）。

        目标手数 = int(权重(保证金份额)×权益 ÷(乘数×价×保证金率))，带符号；
        单品种保证金 ≤ max_etf_position_pct×权益；总保证金占用 ≤ 权益，
        超限按占用最大品种逐手缩减；先平后开（翻向=清零单+新开单）；
        开仓受 can_open_new 门（熔断/停机日禁开，平仓始终允许）；
        min/max_hold 与个股止损是股票纪律——期货信号自带通道离场，不适用（两端一致）。
        执行端（paper._execute）按 reason 区分开/平单：开仓撞涨跌停拒开。"""
        import math as _math
        from .futures import futures_meta
        orders: list[dict] = []
        if equity <= 0 or not tw_fut:
            return orders
        cap_w = self.risk.max_etf_position_pct
        want: dict[str, int] = {}
        meta: dict[str, dict] = {}
        px: dict[str, float] = {}
        for c, w in tw_fut.items():
            q = float(prices.get(c, {}).get("price") or 0.0)
            if q <= 0 or w == 0:
                continue
            m = futures_meta(c)
            share = min(abs(w) * equity, cap_w * equity)
            want[c] = int(_math.copysign(share / (m["mult"] * q * m["margin"]), w))
            meta[c], px[c] = m, q
        if not want:
            return orders

        def _usage() -> float:
            return sum(abs(want[c]) * meta[c]["mult"] * px[c] * meta[c]["margin"] for c in want)

        guard = 0
        while _usage() > equity and any(want[c] != 0 for c in want):
            c = max(want, key=lambda k: abs(want[k]) * meta[k]["mult"] * px[k] * meta[k]["margin"])
            if want[c] == 0:
                break
            want[c] += -1 if want[c] > 0 else 1
            guard += 1
            if guard > 10000:
                break

        can_open = self.can_open_new(today_key)
        for c, tgt in want.items():
            cur = int(positions.get(c, {}).get("lots", 0))
            if cur == tgt:
                continue
            close_qty = 0
            if cur != 0:
                if cur * tgt < 0:
                    close_qty = cur                    # 翻向：先全平
                elif abs(tgt) < abs(cur):
                    close_qty = cur - tgt              # 同向减仓（带符号）
            if close_qty != 0:
                orders.append({"code": c, "side": "sell" if close_qty > 0 else "buy",
                               "shares": int(abs(close_qty)), "reason": "fut_close"})
            if not can_open:
                continue  # 熔断/停机日：只平不开（与股票分支同纪律）
            d = tgt - (cur - close_qty)
            if d != 0:
                orders.append({"code": c, "side": "buy" if d > 0 else "sell",
                               "shares": int(abs(d)), "reason": "fut_open"})
        return orders

    def stop_orders(self, positions: dict, prices: dict) -> list[dict]:
        """个股 -8% 硬止损单（仅可卖部分）。"""
        out: list[dict] = []
        for c, pos in positions.items():
            avail = pos.get("available", 0)
            if avail <= 0:
                continue
            p = prices.get(c, {}).get("price") or 0.0
            cost = pos.get("cost", 0.0)
            if p > 0 and cost > 0 and p <= cost * (1.0 - self.risk.stop_loss_pct):
                shares = avail // LOT * LOT
                if shares > 0:
                    out.append({"code": c, "side": "sell", "shares": int(shares), "reason": "stop"})
        return out

    def held_trade_days(self, pos: dict, today_key: str) -> int:
        """持仓已持有交易日数（自最近一次买入日起算；无记录视为0即从今天起计时）。"""
        lb = pos.get("last_buy_date") or ""
        if not lb:
            return 0
        try:
            d0 = dt.datetime.strptime(lb, "%Y%m%d").date()
            today = dt.datetime.strptime(today_key, "%Y%m%d").date()
            cal = clock.trade_dates()
            a = int(cal.searchsorted(pd.Timestamp(d0)))
            b = int(cal.searchsorted(pd.Timestamp(today)))
            return max(0, b - a)
        except Exception:  # noqa: BLE001 日历缺该日则保守视为0
            return 0

    def time_exit_orders(self, positions: dict, today_key: str) -> list[dict]:
        """最高持股 max_hold_days（默认15个交易日）超时离场单（仅可卖部分）。"""
        if self.risk.max_hold_days <= 0:
            return []
        out: list[dict] = []
        for c, pos in positions.items():
            avail = pos.get("available", 0)
            if avail <= 0:
                continue
            if self.held_trade_days(pos, today_key) >= self.risk.max_hold_days:
                shares = avail // LOT * LOT
                if shares > 0:
                    out.append({"code": c, "side": "sell", "shares": int(shares), "reason": "time_exit"})
        return out
