"""实盘会话：与模拟盘同一套决策/风控/熔断，撮合改走 QMT 券商通道。

风控专家审查（2026-09-19）强化版，修复实盘通道P0：
- 权益三重防护：券商查询失败/返回0 → 快照估值兜底 → 沿用上次有效值，绝不以0触发停机
- 日熔断真正拦单：开盘买单前复核 can_open_new；盘中熔断首次触发即撤全部在途单
- go-live 基线迁移：首次实盘同步以券商真实权益重置回撤/日熔断基线（防模拟盘高水位误停机）
- 持有计时保全：同步持仓保留原 last_buy_date（2周超时离场在实盘同样生效）
- 限价夹板：委托价强制夹入[跌停价,涨停价]（ETF按0.001元精度），跌停日卖单挂跌停价排队
- 当日去重：同一(code,side,reason)只报一次，崩溃重启先对账再补单
- 极端行情闸：市场广度<-4%当日禁买（复用日熔断通道）
- 事件告警：停机/熔断/止损触发时日志+webhook（meta.alert_webhook）
"""
from __future__ import annotations

import datetime as dt
import json
import logging
import os
import time

from . import clock
from . import data as qdata
from . import fundamental
from .broker_qmt import QmtBroker
from .config import STOP_FILE, AppConfig
from .decide import account_equity, prepare_orders, team_fingerprint
from .report import alert, daily_report
from .risk import LOT, RiskManager
from .state import halt_now, save_state
from .validation import effective_limit

log = logging.getLogger("quant.live")

PRICE_BAND = 0.004          # 限价让价区间
EXTREME_BREADTH = -0.04     # 市场广度阈值：全池最新价/昨收均值低于此值当日禁买


def _tick_size(code: str) -> int:
    return 3 if qdata.is_etf(code) else 2  # ETF最小变动0.001元，股票0.01元


class LiveSession:
    def __init__(self, cfg: AppConfig, state: dict, force: bool = False):
        self.cfg = cfg
        self.state = state
        self.force = force
        self.rm = RiskManager(cfg, state)
        self.broker = QmtBroker(cfg.qmt)
        self.filled_open = False
        self._placed: set[tuple] = set()      # (code, side, reason) 当日去重
        self._breaker_cancelled = False
        self._last_valid_equity: float | None = None

    # -------------------------------------------------- 同步

    def _sync_account(self):
        """以券商为准同步持仓/现金；首次实盘同步重置回撤与日熔断基线（go-live迁移）。"""
        acc = self.state["account"]
        prev_positions = acc.get("positions", {})
        pos = self.broker.positions()
        if pos:
            today_key = dt.date.today().strftime("%Y%m%d")
            new_positions = {}
            for c, p in pos.items():
                if p["shares"] <= 0:
                    continue
                old = prev_positions.get(c) or {}
                new_positions[c] = {"shares": p["shares"], "available": p["available"],
                                    "locked": {}, "cost": p["cost"],
                                    # 保留原持有计时（2周上限实盘生效）；仅新增持仓从今天起计
                                    "last_buy_date": old.get("last_buy_date") or today_key}
            acc["positions"] = new_positions
        if not self.broker.dry_run:
            a = self.broker.asset()
            total = float(a.get("total", 0.0) or 0.0)
            if total > 0:
                acc["cash"] = a.get("cash", acc["cash"])
                if not acc.get("live_baseline_done"):
                    acc["equity_high"] = total
                    acc["day_start_equity"] = total
                    acc["day_key"] = dt.date.today().strftime("%Y%m%d")
                    acc["live_baseline_done"] = True
                    log.warning("【go-live迁移】回撤高水位/日熔断基线已重置为券商真实权益 %.0f 元", total)
        save_state(self.state)

    # -------------------------------------------------- 权益与广度

    def _equity(self, quotes: dict) -> tuple[float, bool]:
        """真实权益（三重防护）。返回 (equity, 是否可用于风控判定)。"""
        if not self.broker.dry_run:
            try:
                total = float(self.broker.asset().get("total", 0.0) or 0.0)
            except Exception as e:  # noqa: BLE001
                log.warning("券商权益查询异常: %s", e)
                total = 0.0
            if total > 0:
                self._last_valid_equity = total
                return total, True
            log.warning("券商权益无效(%.2f)：改用快照估值兜底（绝不据此停机）", total)
        if quotes:
            prices = {c: q.get("price", 0.0) for c, q in quotes.items()}
            eq = account_equity(self.state, prices)
            if eq > 0:
                self._last_valid_equity = eq
                return eq, True
        if self._last_valid_equity:
            log.warning("快照亦不可用：沿用上次有效权益 %.0f，本轮跳过风控更新", self._last_valid_equity)
            return self._last_valid_equity, False
        return 0.0, False

    def _market_breadth(self, quotes: dict) -> float | None:
        vals = []
        for q in quotes.values():
            p, pc = q.get("price", 0.0), q.get("prev_close", 0.0)
            if p > 0 and pc > 0:
                vals.append(p / pc - 1.0)
        if len(vals) >= 20:
            return sum(vals) / len(vals)
        return None

    # -------------------------------------------------- 下单

    def _place(self, orders: list[dict], quotes: dict, phase: str) -> int:
        placed = 0
        for o in orders:
            key = (o["code"], o["side"], o.get("reason", phase))
            if key in self._placed:
                continue  # 当日去重：同标的同方向同原因只报一次（防废单轰炸）
            q = quotes.get(o["code"])
            price = float(q.get("price", 0.0)) if q else 0.0
            if price <= 0:
                continue
            shares = int(o["shares"]) // LOT * LOT
            shares = min(shares, qdata.max_order_shares(o["code"]))  # 单笔申报上限（官方规则）
            if shares <= 0:
                continue
            prev = float(q.get("prev_close", 0.0) or 0.0)
            if prev > 0:
                lim = effective_limit(o["code"])  # 数据推断的真实限制（与回测/模拟盘同源）
                ts = _tick_size(o["code"])
                up = round(prev * (1 + lim), ts)
                dn = round(prev * (1 - lim), ts)
            else:
                up, dn = price * 1.1, 0.0
            if o["side"] == "buy":
                if price >= up - 1e-9:
                    log.info("跳过买入 %s：已近涨停（真实盘口也买不到）", o["code"])
                    continue
                limit_px = min(price * (1 + PRICE_BAND), up)     # 夹入涨跌停区间
            else:
                limit_px = max(price * (1 - PRICE_BAND), dn)      # 跌停日挂跌停价排队
            fn = self.broker.buy if o["side"] == "buy" else self.broker.sell
            seq = fn(o["code"], shares, limit_px)
            self._placed.add(key)
            if seq is not None or self.broker.dry_run:
                placed += 1
            self.state["trade_log"].append({"date": dt.date.today().strftime("%Y%m%d"),
                                            "code": o["code"], "side": o["side"],
                                            "shares": shares, "price": round(limit_px, 3),
                                            "reason": f"live_{phase}", "seq": str(seq)})
        self.state["trade_log"] = self.state["trade_log"][-5000:]
        save_state(self.state)
        return placed

    def _refresh_orders_if_team_changed(self) -> None:
        """备单(T-1晚)与执行(T日)之间团队变更 → 按现任团队重备（防执行已换血团队的隔夜单）。"""
        state = self.state
        if not state.get("orders_today"):
            return
        if state.get("orders_fingerprint") != team_fingerprint(state):
            log.warning("备单后冠军团队已变更：重新生成订单")
            state["orders_today"] = []
            try:
                prepare_orders(self.cfg, state)
            except Exception as e:  # noqa: BLE001
                log.warning("重备订单失败（沿用旧单）: %s", e)

    # -------------------------------------------------- 主循环

    def run(self) -> bool:
        state = self.state
        today = dt.date.today()
        today_key = today.strftime("%Y%m%d")
        if not clock.is_trade_date(today):
            log.info("今天非交易日，实盘不运行")
            return False
        if state["auto"].get("session_date") == today_key and not self.force:
            log.info("今日实盘会话已运行过")
            return True

        self._sync_account()
        if not state.get("orders_today"):
            try:
                prepare_orders(self.cfg, state)
            except Exception as e:  # noqa: BLE001
                log.warning("现场生成订单失败: %s", e)
        self._refresh_orders_if_team_changed()

        try:
            uni_df = qdata.load_universe()
            uni_codes = set(uni_df["code"])
            self._uni_names = dict(zip(uni_df["code"].astype(str), uni_df["name"].astype(str)))
        except Exception:  # noqa: BLE001
            uni_codes = set()
            self._uni_names = {}
        codes = uni_codes | set(state["account"]["positions"]) \
            | {o["code"] for o in state.get("orders_today", [])}

        log.warning("实盘会话开始（dry_run=%s）：待执行订单 %d 笔",
                    self.broker.dry_run, len(state.get("orders_today", [])))
        last_quotes: dict = {}
        while True:
            now = dt.datetime.now()
            if now.time() >= dt.time(15, 6):
                break
            if os.path.exists(STOP_FILE):
                log.error("STOP 停机文件触发：撤单并全面停机")
                self.broker.cancel_all()
                alert(self.cfg, "实盘人工STOP停机：已撤全部委托")
                halt_now(state, "STOP 停机文件触发（人工）")
                break
            try:
                quotes = qdata.spot_prices(sorted(codes))
            except Exception as e:  # noqa: BLE001
                log.warning("快照获取失败: %s", e)
                quotes = {}
            if not quotes:
                time.sleep(30)
                continue
            last_quotes = quotes

            equity, valid = self._equity(quotes)
            if not valid:
                time.sleep(60)  # 权益不可得：跳过本轮风控（绝不以0权益停机）
                continue
            self.rm.refresh_day(today_key, equity)
            self.rm.note_daily_loss(today_key, equity)

            # 极端行情闸：市场广度崩坏当日禁买
            breadth = self._market_breadth(quotes)
            if (breadth is not None and breadth < EXTREME_BREADTH
                    and state["risk"]["daily_breaker_date"] != today_key):
                state["risk"]["daily_breaker_date"] = today_key
                alert(self.cfg, f"极端行情：市场广度 {breadth:.2%} < {EXTREME_BREADTH:.0%}，当日禁买")

            if self.rm.halt_active():
                log.error("风控停机：撤单并尽力离场风控单，退出会话（人工复盘后 run.py resume）")
                alert(self.cfg, f"实盘回撤停机触发：{state['risk']['halt_reason']}")
                self.broker.cancel_all()
                self._placed.clear()
                exits = self.rm.stop_orders(state["account"]["positions"], quotes) \
                    + self.rm.time_exit_orders(state["account"]["positions"], today_key)
                if exits:
                    self._place(exits, quotes, "halt_reduce")
                break

            # 日熔断首次触发：撤全部在途单（后续tick自动只补风控卖单）
            if not self.rm.can_open_new(today_key) and not self._breaker_cancelled:
                self.broker.cancel_all()
                self._placed.clear()  # 允许止损/超时卖单重新挂出
                self._breaker_cancelled = True
                alert(self.cfg, "实盘单日亏损熔断：撤全部在途委托，当日只卖不买")

            if not self.filled_open and now.time() >= dt.time(9, 31):
                orders = list(state.get("orders_today", []))
                if not self.rm.can_open_new(today_key):
                    orders = [o for o in orders if o["side"] == "sell"]  # 熔断日禁买单
                self._place(orders, quotes, "open")
                self.filled_open = True
            elif self.filled_open:
                stops = self.rm.stop_orders(state["account"]["positions"], quotes)
                if stops:
                    log.warning("触发个股止损: %s", [(s["code"], s["shares"]) for s in stops])
                    self._place(stops, quotes, "stop")
                time_exits = self.rm.time_exit_orders(state["account"]["positions"], today_key)
                if time_exits:
                    log.info("触发持股超时离场（最高持股2周）: %s",
                             [(t["code"], t["shares"]) for t in time_exits])
                    self._place(time_exits, quotes, "time_exit")
                # 负面清单离场：持仓新触发亏损/暴雷/行业/黑名单 → 强制清仓
                try:
                    neg_exits = fundamental.negative_exit_orders(cfg, state["account"]["positions"],
                                                                getattr(self, "_uni_names", {}))
                except Exception:  # noqa: BLE001
                    neg_exits = []
                if neg_exits:
                    log.warning("持仓触发负面清单离场: %s",
                                [(n["code"], n["shares"]) for n in neg_exits])
                    self._place(neg_exits, quotes, "negative")
            if now.time() >= dt.time(14, 56):
                self.broker.cancel_all()  # 收盘前清未成交单（次日备单自然补差额）
            save_state(state)
            time.sleep(60)

        # ---- 收盘对账
        equity, valid = self._equity(last_quotes)
        if not valid:
            log.warning("收盘对账：权益不可得，跳过轨道写入（避免污染数据）")
            state["auto"]["session_date"] = today_key
            state["orders_today"] = []
            save_state(state)
            return True
        if not self.broker.dry_run:
            try:
                a = self.broker.asset()
                if a.get("total", 0) > 0:
                    state["account"]["cash"] = a.get("cash", state["account"]["cash"])
            except Exception:  # noqa: BLE001
                pass
            self._sync_account()
        track = {"date": today.isoformat(), "cash": round(state["account"]["cash"], 2),
                 "market_value": round(equity - state["account"]["cash"], 2),
                 "equity": round(equity, 2), "n_positions": len(state["account"]["positions"]),
                 "mode": "live", "dry_run": self.broker.dry_run}
        state["paper_track"] = [t for t in state["paper_track"] if t["date"] != track["date"]]
        state["paper_track"].append(track)
        # 出局机制（用户指令"不能盘中波动就出局"）：回撤停机/毁灭出局只在收盘对账判定
        self.rm.settle_day(today_key, equity)
        state["auto"]["session_date"] = today_key
        state["orders_today"] = []
        save_state(state)
        path = daily_report(self.cfg, state, f"实盘收盘对账 {today.isoformat()}（dry_run={self.broker.dry_run}）",
                            extra_lines=[f"真实权益 {equity:,.0f} 元（现金 {state['account']['cash']:,.0f} / "
                                         f"市值 {track['market_value']:,.0f}）",
                                         f"持仓 {track['n_positions']} 只"])
        log.info("实盘收盘对账：真实权益 %.2f 元 | 日报 → %s", equity, path)
        return True
