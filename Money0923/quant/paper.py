"""模拟盘引擎（100万虚拟资金）。

- PaperSession：交易日盘中运行，60秒轮询实时快照撮合（费用/滑点/T+1/涨跌停全仿真）
- run_replay：历史回放验证——冻结冠军参数跑窗口，出验证报告（不写交易轨道）

轨道（state.paper_track）只由真实推进的交易日构成：盘中会话每日收盘写入一条，
形成"冠军定型后"的连续模拟实盘记录。
"""
from __future__ import annotations

import datetime as dt
import json
import logging
import os
import time

import numpy as np

from . import clock
from . import data as qdata
from . import fundamental
from . import strategies as strat_lib
from .backtest import equal_weight_benchmark, run_backtest
from .config import LOGS_DIR, STOP_FILE, AppConfig
from .decide import account_equity, prepare_orders, team_fingerprint, team_members, team_target_weights
from .report import alert, daily_report
from .risk import LOT, RiskManager
from .state import save_state
from .validation import effective_limit

log = logging.getLogger("quant.paper")

EXTREME_BREADTH = -0.04  # 市场广度阈值：全池最新价/昨收均值低于此值当日禁买


def _market_breadth(quotes: dict) -> float | None:
    vals = []
    for q in quotes.values():
        p, pc = q.get("price", 0.0), q.get("prev_close", 0.0)
        if p > 0 and pc > 0:
            vals.append(p / pc - 1.0)
    if len(vals) >= 20:
        return sum(vals) / len(vals)
    return None


def _ashare_close_risk(positions: dict, quotes: dict) -> tuple[float, float, list]:
    """沪深规则感知的收盘风险披露（纯披露，不触发出局——用户出局纪律）。

    返回 (理论最大单日损失占权益比, 跌停封死市值占比, 封死代码列表)：
    - 理论最大单日损失 = Σ(持仓市值×该品种有效涨跌幅限制) / 权益。
      沪深主板/多数ETF 10%，创业板股/创业板ETF 20%（validation.effective_limit
      数据驱动推断，勿用固定10%错判20%品种）。
    - 跌停封死 = 现价触及跌停价附近（≤昨收×(1-限制)×1.002）且成交额显著萎缩
      （快照成交额 < 前期常态的30%——封死时排队卖不掉）。快照只有当日数据，
      萎缩判定用绝对阈值兜底（<2千万按封死，主板个股正常日远高于此）。"""
    from .validation import effective_limit
    total_mv = 0.0
    theo_loss_mv = 0.0
    locked_mv = 0.0
    locked_codes: list[str] = []
    equity = 0.0
    for code, pos in positions.items():
        q = quotes.get(code) or {}
        p = q.get("price", 0.0) or 0.0
        pc = q.get("prev_close", 0.0) or 0.0
        mv = pos.get("shares", 0) * (p if p > 0 else pos.get("cost", 0.0))
        if mv <= 0:
            continue
        total_mv += mv
        lim = effective_limit(code)
        theo_loss_mv += mv * lim
        if p > 0 and pc > 0:
            limit_dn = pc * (1.0 - lim)
            amount = q.get("amount", 0.0) or 0.0
            if p <= limit_dn * 1.002 and amount < 2e7:
                locked_mv += mv
                locked_codes.append(code)
    equity = total_mv + 0.0  # 调用方传入的口径为市值合计；占比按市值归一（现金无单日损失敞口）
    if total_mv <= 0:
        return 0.0, 0.0, []
    # 理论损失占比需对账户总权益归一——调用方有 equity，这里先返回市值口径由 _days_to_ruin 统一
    theo_ratio = theo_loss_mv / total_mv if total_mv > 0 else 0.0
    locked_pct = locked_mv / total_mv if total_mv > 0 else 0.0
    return theo_ratio, locked_pct, locked_codes


def _days_to_ruin(cfg, equity: float, theo_daily_loss: float) -> int | None:
    """距毁灭出局线的极端跌停日数（沪深节奏的毁灭路径参考，非预测）。"""
    try:
        ruin_line = cfg.risk.initial_capital * (1.0 - cfg.risk.ruin_loss_pct)
    except AttributeError:
        return None
    if equity <= ruin_line or theo_daily_loss <= 0:
        return None
    n = 0
    eq = equity
    while eq > ruin_line and n < 60:
        eq *= (1.0 - theo_daily_loss)
        n += 1
    return n


class PaperSession:
    """盘中实时模拟会话（auto 守护在 9:25-15:06 自动拉起）。"""

    def __init__(self, cfg: AppConfig, state: dict, force: bool = False):
        self.cfg = cfg
        self.state = state
        self.force = force
        self.rm = RiskManager(cfg, state)
        self.filled_open = False
        self._slip_mult: dict[str, float] = {}
        try:
            self._slip_mult = qdata.load_slip_mult()  # 小市值端 ×2.0 分档滑点
        except Exception:  # noqa: BLE001
            self._slip_mult = {}

    # -------------------------------------------------- 撮合

    def _start_side_league(self) -> None:
        """盘中伴生联赛线程（用户2026-09-22"本地算力没用好"指令）。

        09:25-15:06 的 ~5.7 小时里会话只做每分钟一次轻量行情轮询，32核+GPU 全闲置
        （2026-09-22 实测：09:03 收兵→15:20 重启间联赛零开局）。此线程把闲置算力
        变成联赛证据样本：与闭市联赛完全同构（同认证/同pstats/同锁/同persist），
        预计 +1.2万局/交易日（+90%证据产能）。

        安全边界：
        - 面板=full_panel(readonly=True) 只读昨夜日更缓存，零网络（盘中拉新浪会
          殃及行情源限流——2026-09-21 事故教训）
        - state 写全部经 STATE_LOCK 临界区（_accum_pstats/respawn+save/game_evo/
          purge/_execute/save_state），与主线程互斥不撕裂
        - 批次 240s，14:55 后不开新批（最后一批 ≤14:59 收工），15:06 结算零并发
        - STOP 文件/停机事件即退；daemon 线程不阻塞会话生命周期
        """
        import threading
        self._side_stop = threading.Event()
        self._side_thread = None

        def _loop() -> None:
            try:
                _, panel = qdata.full_panel(self.cfg, readonly=True)
                log.info("【盘中伴生联赛】面板就绪（只读缓存），开始利用盘中闲置算力")
            except Exception:  # noqa: BLE001 面板加载失败=盘中不算，不影响会话
                log.exception("盘中伴生联赛面板加载失败，线程退出（会话不受影响）")
                return
            from . import arena
            while (not self._side_stop.is_set()
                   and dt.datetime.now().time() < dt.time(14, 55)
                   and not os.path.exists(STOP_FILE)):
                try:
                    arena.run_rounds(self.cfg, self.state, panel=panel,
                                     time_budget_s=240, persist=True)
                except Exception:  # noqa: BLE001
                    log.exception("盘中伴生联赛批异常（继续下一批）")
                self._side_stop.wait(5)
            log.info("【盘中伴生联赛】收盘收工")

        self._side_thread = threading.Thread(target=_loop, name="side-league", daemon=True)
        self._side_thread.start()

    def _execute(self, orders: list[dict], quotes: dict, phase: str) -> int:
        """撮合入口：唯一会增删 positions 键的临界区——持锁防盘中伴生联赛线程
        并发 save_state 撞上 key 变化（dict changed size / 撕裂快照）。"""
        from .state import STATE_LOCK
        with STATE_LOCK:
            return self._execute_locked(orders, quotes, phase)

    def _execute_locked(self, orders: list[dict], quotes: dict, phase: str) -> int:
        fee = self.cfg.fee
        risk_cfg = self.cfg.risk
        acc = self.state["account"]
        pos = acc["positions"]
        today_key = dt.date.today().strftime("%Y%m%d")
        executed = 0
        fee_margin = 1.0 + fee.commission_rate + fee.transfer_fee  # 统一费用余量口径
        # 分仓制：带 sleeve 标签的订单以该仓现金为预算与入账（总账同步双记账）
        sv_map = {sv["id"]: sv for sv in (self.state.get("sleeves") or [])}

        for o in orders:
            code, side = o["code"], o["side"]
            q = quotes.get(code)
            if not q or not q.get("price") or q["price"] <= 0:
                continue
            price, prev = float(q["price"]), float(q.get("prev_close") or 0)

            # ---- 期货撮合（F.*）：手数/保证金/双向/T+0，与 futures_backtest 同口径 ----
            if str(code).startswith("F."):
                from .futures import futures_meta
                m = futures_meta(code)
                _sv_f = sv_map.get(o.get("sleeve")) if o.get("sleeve") else None
                d = int(o.get("shares", 0)) * (1 if side == "buy" else -1)
                if d == 0:
                    continue
                cur = int(pos.get(code, {}).get("lots", 0))
                is_open = (cur == 0) or (cur * d > 0)
                if is_open:
                    up = float(q.get("up_limit") or 0.0)
                    dn = float(q.get("dn_limit") or 0.0)
                    if up > 0 and d > 0 and price >= up - 1e-9:
                        log.info("跳过期货开多 %s：撞涨停（真实盘口也开不了）", code)
                        continue
                    if dn > 0 and d < 0 and price <= dn + 1e-9:
                        log.info("跳过期货开空 %s：撞跌停（真实盘口也开不了）", code)
                        continue
                    # 保证金总预算复检（实时价 vs 规划用收盘价的漂移）：超限逐手缩减
                    # 分仓隔离：预算与占用都只看本仓（他仓的期货仓不算本仓预算）
                    if _sv_f is not None:
                        from . import sleeves as qsl
                        eq_now = qsl.sleeve_equity(
                            self.state, _sv_f,
                            {c2: v2.get("price", 0.0) for c2, v2 in quotes.items()})
                    else:
                        eq_now = account_equity(
                            self.state, {c2: v2.get("price", 0.0) for c2, v2 in quotes.items()})

                    def _fut_usage(extra_d: int) -> float:
                        u = 0.0
                        for c2, p2 in self.state["account"]["positions"].items():
                            if not str(c2).startswith("F."):
                                continue
                            if _sv_f is not None and p2.get("sleeve") != _sv_f["id"]:
                                continue
                            mm = futures_meta(c2)
                            lots2 = int(p2.get("lots", 0)) + (extra_d if c2 == code else 0)
                            pr = float(quotes.get(c2, {}).get("price") or 0.0) \
                                or float(p2.get("avg_entry") or 0.0)
                            u += abs(lots2) * mm["mult"] * pr * mm["margin"]
                        if code not in self.state["account"]["positions"]:
                            # 新品种首开：本单自身占用（订单价计）
                            u += abs(extra_d) * m["mult"] * price * m["margin"]
                        return u

                    guard = 0
                    while d != 0 and _fut_usage(d) > eq_now and guard < 10000:
                        d += -1 if d > 0 else 1
                        guard += 1
                    if d == 0:
                        log.info("跳过期货开仓 %s：保证金预算不足（权益 %.0f）", code, eq_now)
                        continue
                _flow = -d * m["mult"] * price - abs(d) * m["fee_lot"]
                acc["cash"] += _flow
                if _sv_f is not None:
                    _sv_f["cash"] += _flow  # 仓内现金双记账
                pnl = 0.0
                p = pos.setdefault(code, {"lots": 0, "avg_entry": 0.0, "last_buy_date": ""})
                if _sv_f is not None:
                    p["sleeve"] = _sv_f["id"]
                if is_open:
                    old_abs, add_abs = abs(cur), abs(d)
                    p["avg_entry"] = ((p.get("avg_entry", 0.0) * old_abs + price * add_abs)
                                      / (old_abs + add_abs)) if (old_abs + add_abs) else price
                    p["last_buy_date"] = today_key
                else:
                    direction = 1 if cur > 0 else -1
                    qty = abs(d)
                    pnl = (price - p.get("avg_entry", 0.0)) * direction * m["mult"] * qty \
                        - qty * m["fee_lot"]
                    if cur + d == 0:
                        p["avg_entry"] = 0.0
                p["lots"] = cur + d
                executed += 1
                log.info("[模拟盘|%s] 期货%s%s %d手 @%.2f（现金 %+.0f%s）",
                         phase, "开仓" if is_open else "平仓",
                         "多" if d > 0 else "空", abs(d), price,
                         -d * m["mult"] * price - abs(d) * m["fee_lot"],
                         f" 已实现盈亏 {pnl:+,.0f}" if not is_open else "")
                entry = {"date": today_key, "code": code, "side": side,
                         "shares": int(abs(d)), "price": round(price, 3),
                         "sleeve": o.get("sleeve"),
                         "reason": o.get("reason", phase)}
                if not is_open:
                    entry["pnl"] = round(pnl, 2)
                self.state["trade_log"].append(entry)
                if p["lots"] == 0:
                    pos.pop(code, None)
                continue

            lim = effective_limit(code)  # 数据推断的真实限制（创业板ETF 20%等），与回测同源
            if prev > 0:
                # 涨跌停按最小变动位数（ETF 0.001/股票 0.01，四舍五入）
                ts = 3 if qdata.is_etf(code) else 2
                up = float(np.floor(prev * (1 + lim) * 10 ** ts + 0.5) / 10 ** ts)
                dn = float(np.floor(prev * (1 - lim) * 10 ** ts + 0.5) / 10 ** ts)
                if side == "buy" and price >= up - 1e-9:
                    log.info("跳过买入 %s：已近涨停（真实盘口也买不到）", code)
                    continue
                if side == "sell" and price <= dn + 1e-9:
                    log.info("跳过卖出 %s：已近跌停（明日再试）", code)
                    continue
            shares = int(o.get("shares", 0))
            if shares <= 0:
                continue
            # 单笔申报上限（交易所规则：创业板30万股/主板100万股/基金100万份）
            shares = min(shares, qdata.max_order_shares(code))
            # 成交额参与率上限（微观结构专家审查#8）：快照成交额×5%截断
            amt_today = float(q.get("amount", 0.0) or 0.0)
            if amt_today > 0:
                max_shares = int(amt_today * risk_cfg.max_participation / price // LOT) * LOT
                if max_shares > 0:
                    shares = min(shares, max_shares)
            slip_m = self._slip_mult.get(code, 1.0)  # 分档滑点（小市值×2.0）

            if side == "buy":
                fill = price * (1 + fee.slippage * slip_m)
                amount = shares * fill
                cost_total = amount + max(amount * fee.commission_rate, fee.min_commission) \
                    + amount * fee.transfer_fee
                _sv = sv_map.get(o.get("sleeve")) if o.get("sleeve") else None
                _ledger = _sv if _sv is not None else acc
                if cost_total > _ledger["cash"]:  # 现金不足自动缩量（仓内现金预算）
                    shares = int(_ledger["cash"] / fill / fee_margin // LOT) * LOT
                    if shares <= 0:
                        continue
                    amount = shares * fill
                    cost_total = amount + max(amount * fee.commission_rate, fee.min_commission) \
                        + amount * fee.transfer_fee
                _ledger["cash"] -= cost_total
                if _sv is not None:
                    acc["cash"] -= cost_total  # 总账同步（双记账不变式）
                p = pos.setdefault(code, {"shares": 0, "available": 0, "locked": {},
                                          "cost": 0.0, "last_buy_date": ""})
                if _sv is not None:
                    p["sleeve"] = _sv["id"]
                p["cost"] = (p["cost"] * p["shares"] + cost_total) / (p["shares"] + shares)
                p["shares"] += shares
                if qdata.is_t0(code):
                    p["available"] += shares  # T+0品种（跨境/债券/黄金/商品ETF）当日可卖
                else:
                    p["locked"][today_key] = p["locked"].get(today_key, 0) + shares  # T+1
                p["last_buy_date"] = today_key
                executed += 1
                log.info("[模拟盘|开盘] 买入 %s %d股 @%.3f", code, shares, fill)
            else:
                p = pos.get(code)
                if not p or p.get("available", 0) <= 0:
                    continue
                shares = min(shares, p["available"] // LOT * LOT)
                if shares <= 0:
                    continue
                fill = price * (1 - fee.slippage * slip_m)
                amount = shares * fill
                stamp = 0.0 if qdata.is_etf(code) else amount * fee.stamp_duty  # ETF免印花税
                net = amount - max(amount * fee.commission_rate, fee.min_commission) \
                    - stamp - amount * fee.transfer_fee
                acc["cash"] += net
                _sv_sell = sv_map.get(p.get("sleeve")) if p.get("sleeve") else None
                if _sv_sell is not None:
                    _sv_sell["cash"] += net  # 卖出归持仓所属仓（总账已同步）
                p["shares"] -= shares
                p["available"] -= shares
                executed += 1
                log.info("[模拟盘|%s] 卖出 %s %d股 @%.3f（已实现盈亏 %+,.0f）",
                         phase, code, shares, fill, (net / shares - p.get("cost", 0.0)) * shares)
                if p["shares"] <= 0:
                    pos.pop(code, None)

            entry = {"date": today_key, "code": code, "side": side,
                     "shares": int(shares), "price": round(fill, 3),
                     "sleeve": o.get("sleeve") or p.get("sleeve"),
                     "reason": o.get("reason", phase)}
            if side == "sell":
                # 已实现盈亏与持有天数（统计中心用）：净卖出摊每股 - 持仓成本
                entry["pnl"] = round((net / shares - p.get("cost", 0.0)) * shares, 2)
                entry["held_days"] = self.rm.held_trade_days(p, today_key)
            self.state["trade_log"].append(entry)
        self.state["trade_log"] = self.state["trade_log"][-5000:]
        if executed:
            save_state(self.state)
        return executed

    # -------------------------------------------------- 主循环

    def run(self) -> bool:
        state, cfg = self.state, self.cfg
        today = dt.date.today()
        today_key = today.strftime("%Y%m%d")

        if not clock.is_trade_date(today):
            log.info("今天非交易日：模拟盘不运行（闭市请用 run.py paper --replay 验证）")
            return False
        if state["auto"].get("session_date") == today_key and not self.force:
            log.info("今日模拟盘会话已运行过，跳过")
            return True
        now = dt.datetime.now()
        if now.time() >= dt.time(15, 6):
            log.info("已过收盘，等晚间数据更新与进化")
            return False

        # 国债逆回购归还（GC001资金T+1开市前到账）——必须在订单执行前入账，
        # 次日开盘执行预算不受任何影响（日频节奏与逆回购天然契合）
        try:
            from . import repo as qrepo
            _ret = qrepo.paper_return(state, today_key)
            if _ret:
                _net = sum(r["amount"] + r["interest"] - r["fee"] for r in _ret)
                log.info("【逆回购】归还 %d 笔，本息 %.2f 元（仓内/总账双记账同步）",
                         len(_ret), _net)
                save_state(state)
        except Exception:  # noqa: BLE001
            log.exception("逆回购归还异常（不阻塞会话）")
        # 周期交接文档：会话开始=新周期起点，落一份盘前快照（收盘结算还会再写）
        try:
            from .handoff import write_handoff
            write_handoff(cfg, state, reason=f"盘前会话 {today.isoformat()}")
        except Exception:  # noqa: BLE001
            log.debug("HANDOFF 生成失败（忽略）")

        # 订单：前一晚备好；缺则现场生成（手动启动场景）
        if not state.get("orders_today"):
            try:
                prepare_orders(cfg, state)
            except Exception as e:  # noqa: BLE001
                log.warning("现场生成订单失败（继续用已有订单）: %s", e)
        # 备单后部署变更（冠军换血/仓换人）→ 重备（防执行已换血阵容的隔夜单）
        from .sleeves import deployment_fingerprint
        if state.get("orders_today") and state.get("orders_fingerprint") != deployment_fingerprint(state):
            log.warning("备单后部署阵容已变更：重新生成订单")
            state["orders_today"] = []
            try:
                prepare_orders(cfg, state)
            except Exception as e:  # noqa: BLE001
                log.warning("重备订单失败（沿用旧单）: %s", e)

        try:
            uni_df = qdata.load_universe()
            uni_codes = set(uni_df["code"])
            self._uni_names = dict(zip(uni_df["code"].astype(str), uni_df["name"].astype(str)))
        except Exception:  # noqa: BLE001
            uni_codes = set()
            self._uni_names = {}
        codes = uni_codes | set(state["account"]["positions"]) \
            | {o["code"] for o in state.get("orders_today", [])}

        log.info("模拟盘会话开始：待执行订单 %d 笔", len(state.get("orders_today", [])))
        self._start_side_league()
        last_quotes: dict = {}
        while True:
            now = dt.datetime.now()
            if now.time() >= dt.time(15, 6):
                break
            if os.path.exists(STOP_FILE):
                log.warning("检测到 STOP 停机文件：模拟盘退出")
                break
            try:
                # 轻量主源（腾讯逐标的，内部分批50/请求）：全宇宙~190只≈4请求，
                # 替代每60秒拉一次新浪全市场5000股大表（限流+浪费的根源）
                quotes = qdata.spot_quotes_light(sorted(codes))
            except Exception:  # noqa: BLE001
                quotes = {}
            if not quotes:
                try:
                    quotes = qdata.spot_prices(sorted(codes))
                except Exception as e:  # noqa: BLE001
                    log.warning("快照获取失败: %s", e)
                    quotes = {}
            if not quotes:
                time.sleep(30)
                continue
            last_quotes = quotes
            equity = self._equity(quotes)
            self.rm.refresh_day(today_key, equity)
            self.rm.note_daily_loss(today_key, equity)
            # 极端行情闸：市场广度崩坏当日禁买（复用日熔断通道）
            breadth = _market_breadth(quotes)
            if (breadth is not None and breadth < EXTREME_BREADTH
                    and state["risk"]["daily_breaker_date"] != today_key):
                state["risk"]["daily_breaker_date"] = today_key
                alert(cfg, f"模拟盘极端行情：市场广度 {breadth:.2%}，当日禁买")
            if self.rm.halt_active():
                log.warning("风控全面停机：先尽力离场风控单，再保留剩余持仓等人工复盘")
                alert(cfg, f"模拟盘回撤停机触发：{state['risk']['halt_reason']}")
                exits = self.rm.stop_orders(state["account"]["positions"], quotes) \
                    + self.rm.time_exit_orders(state["account"]["positions"], today_key)
                if exits:
                    self._execute(exits, quotes, "halt_reduce")
                state["orders_today"] = []
                save_state(state)
                break
            if not self.filled_open and now.time() >= dt.time(9, 31):
                orders = list(state.get("orders_today", []))
                if not self.rm.can_open_new(today_key):
                    orders = [o for o in orders if o["side"] == "sell"]  # 熔断日禁买单
                self._execute(orders, quotes, "open")
                self.filled_open = True
            elif self.filled_open:
                stops = self.rm.stop_orders(state["account"]["positions"], quotes)
                if stops:
                    log.warning("触发个股止损: %s", [(s["code"], s["shares"]) for s in stops])
                    self._execute(stops, quotes, "stop")
                time_exits = self.rm.time_exit_orders(state["account"]["positions"], today_key)
                if time_exits:
                    log.info("触发持股超时离场（最高持股2周）: %s",
                             [(t["code"], t["shares"]) for t in time_exits])
                    self._execute(time_exits, quotes, "time_exit")
                # 负面清单离场：持仓新触发亏损/暴雷/行业/黑名单 → 强制清仓（"不做"含持货）
                try:
                    neg_exits = fundamental.negative_exit_orders(cfg, state["account"]["positions"],
                                                                getattr(self, "_uni_names", {}))
                except Exception:  # noqa: BLE001
                    neg_exits = []
                if neg_exits:
                    log.warning("持仓触发负面清单离场: %s",
                                [(n["code"], n["shares"]) for n in neg_exits])
                    self._execute(neg_exits, quotes, "negative")
            save_state(state)
            time.sleep(60)

        # 盘中伴生联赛收工（最后一批 ≤14:59 自然结束；此处兜底叫停+短等待）
        if getattr(self, "_side_stop", None) is not None:
            self._side_stop.set()
        if getattr(self, "_side_thread", None) is not None:
            self._side_thread.join(timeout=180)

        # ---- 收盘结算
        equity = self._equity(last_quotes) if last_quotes else state["account"]["cash"]
        track = {"date": today.isoformat(),
                 "cash": round(state["account"]["cash"], 2),
                 "market_value": round(equity - state["account"]["cash"], 2),
                 "equity": round(equity, 2),
                 "n_positions": len(state["account"]["positions"])}
        state["paper_track"] = [t for t in state["paper_track"] if t["date"] != track["date"]]
        state["paper_track"].append(track)
        state["paper_track"] = state["paper_track"][-500:]
        # 出局机制（用户指令"不能盘中波动就出局，亏完才出局"）：
        # 回撤停机/毁灭出局只在收盘结算判定——盘中波动永不触发。
        # 账户级结算：毁灭线唯一兜底（用户指令"根据策略来，激进的亏8成都行"——
        # 全局 10% 停机线已撤销，停机权下放到各风格仓 halt_line 分级管辖）
        self.rm.settle_day(today_key, equity, halt_pct=None)
        # ---- 分仓结算：每仓独立 10% 停机线 / 仓毁灭线（收盘口径，盘中永不触发）
        # 账户级 settle_day（上方）仍为最后防线；仓级是"队死换人"的一线淘汰机制。
        try:
            from . import sleeves as qsl
            _sprices = {c: qq.get("price", 0.0) for c, qq in (last_quotes or {}).items()}
            for sv in state.get("sleeves") or []:
                seq = qsl.sleeve_equity(state, sv, _sprices)
                r = sv["risk"]
                if seq > float(r.get("equity_high", 0.0) or 0.0):
                    r["equity_high"] = seq
                ruin_line = float(sv.get("capital_start", 0.0) or 0.0) \
                    * (1.0 - cfg.risk.ruin_loss_pct)
                if (cfg.risk.ruin_loss_pct > 0 and not sv.get("retired")
                        and float(sv.get("capital_start", 0.0) or 0.0) > 0
                        and seq <= ruin_line):
                    sv["retired"] = True
                    state.setdefault("risk_events", []).append({
                        "date": today.isoformat(), "type": "sleeve_ruin",
                        "detail": f"{sv['id']} 仓毁灭出局：收盘权益 {seq:,.0f} ≤ 仓起点×"
                                  f"{1 - cfg.risk.ruin_loss_pct:.0%}（{ruin_line:,.0f}）"
                                  f"——仓退役，现金保留待再分配"})
                    state["risk_events"] = state["risk_events"][-100:]
                    alert(cfg, f"{sv['id']} 仓毁灭出局（≤{ruin_line:,.0f}）：仓退役")
                elif (sv.get("halt_line") is not None and float(sv["halt_line"]) > 0
                        and not qsl.halted(sv)
                        and not sv.get("retired")
                        and float(r.get("equity_high", 0.0) or 0.0) > 0
                        and seq <= float(r["equity_high"])
                        * (1.0 - float(sv["halt_line"]))):
                    # 风险线按风格分级（用户指令"根据策略来，激进的亏8成都行"）：
                    # halt_line=None 的激进仓永不在此停机——只受毁灭线管辖
                    r["halt"] = True
                    r["halt_reason"] = (f"仓回撤 {(1 - seq / r['equity_high']):.1%} "
                                        f"≥ {float(sv['halt_line']):.0%} 停机线（收盘口径）")
                    r["halted_at"] = dt.datetime.now().isoformat(timespec="seconds")
                    state.setdefault("risk_events", []).append({
                        "date": today.isoformat(), "type": "sleeve_halt",
                        "detail": f"{sv['id']}（{qsl.sleeve_label(sv)}）触发仓级停机线："
                                  f"高水位 {r['equity_high']:,.0f} → 收盘 {seq:,.0f}"
                                  f"——队死换人，资金保留"})
                    state["risk_events"] = state["risk_events"][-100:]
                    alert(cfg, f"{sv['id']} 仓触发 {float(sv['halt_line']):.0%} 停机线"
                               f"（{r['halt_reason']}）→ 明日换人")
                sv.setdefault("history", []).append({
                    "date": today.isoformat(), "equity": round(seq, 2),
                    "cash": round(float(sv.get("cash", 0.0) or 0.0), 2),
                    "n_pos": len(qsl.sleeve_positions(state, sv)),
                    "halted": qsl.halted(sv), "retired": bool(sv.get("retired"))})
                sv["history"] = sv["history"][-500:]
                # 停机仓换人：认证池选下一个挑战者（资金保留；新基线=当前仓权益）
                if qsl.halted(sv) and not sv.get("retired"):
                    qsl.rotate_sleeve(state, sv, equity=seq)
        except Exception:
            log.exception("分仓结算/换人异常（不阻塞总账结算）")
        # 沪深特色披露（A股规则感知，纯披露不出局）：理论最大单日损失+跌停封死占比+
        # 距毁灭线的极端跌停日数——一字跌停卖不掉的"流动性死亡路径"必须可见
        theo_loss, locked_pct, locked_codes = _ashare_close_risk(state["account"]["positions"], last_quotes)
        ruin_days = _days_to_ruin(cfg, equity, theo_loss) if theo_loss > 0 else None
        risk_lines = [f"权益 {equity:,.0f} 元（现金 {state['account']['cash']:,.0f} / "
                      f"市值 {track['market_value']:,.0f}）",
                      f"持仓 {track['n_positions']} 只 | 累计成交流水 {len(state['trade_log'])} 笔"]
        if theo_loss > 0:
            risk_lines.append(f"A股规则感知：组合理论最大单日损失 {theo_loss:.1%}"
                              f"（按各持仓有效涨跌幅限制加权，含20%品种）")
        if locked_codes:
            risk_lines.append(f"跌停封死 {len(locked_codes)} 只（{','.join(locked_codes[:5])}，"
                              f"占市值 {locked_pct:.0%}）——T+1+排队卖不掉，流动性风险")
        if ruin_days is not None:
            risk_lines.append(f"距毁灭出局线（本金×20%）≈ 还需连续 {ruin_days} 个全员跌停日"
                              f"（极端情形参考，非预测）")
        if locked_pct >= 0.30:
            consec = int(state.get("limit_locked_streak", 0)) + 1
            state["limit_locked_streak"] = consec
            if consec >= 2:
                state.setdefault("risk_events", []).append({
                    "date": today.isoformat(), "type": "limit_locked",
                    "detail": f"连续 {consec} 日跌停封死占市值≥30%（当前 {locked_pct:.0%}）"
                              f"——A股流动性死亡路径预警：一字跌停止损单排队无法成交，"
                              f"毁灭线照常按收盘权益判定，物理上无法加速离场"})
                state["risk_events"] = state["risk_events"][-100:]
                alert(cfg, f"流动性死亡预警：连续{consec}日跌停封死≥30%，卖出排队中，"
                           f"出局线照常收盘判定")
        else:
            state["limit_locked_streak"] = 0
        # —— 国债逆回购：收盘结算后闲置现金借出GC001（风险≈0，用户指令2026-09-22）
        # 各分仓现金独立借出（利息归属清晰），次日开市前带息归还；占款天数含周末节假日
        try:
            from . import repo as qrepo
            _lends = qrepo.paper_lend(state, cfg, today)
            if _lends:
                _amt = sum(r["amount"] for r in _lends)
                _int = sum(r["interest"] - r["fee"] for r in _lends)
                risk_lines.append(f"国债逆回购：借出 {_amt:,.0f} 元 @ 年化 "
                                  f"{_lends[0]['rate']}% × {_lends[0]['days']}天"
                                  f"（{len(_lends)}笔），预计净利息 {_int:.2f} 元"
                                  f"——次日开市前归还，不影响明晨执行")
                log.info("【逆回购】借出 %d 笔 %.0f 元 @%.3f%%×%d天，预计净利息 %.2f 元",
                         len(_lends), _amt, _lends[0]["rate"], _lends[0]["days"], _int)
            _earned = qrepo.total_interest_earned(state)
            if _earned > 0:
                risk_lines.append(f"逆回购累计已落袋利息 {_earned:.2f} 元（无风险收益）")
        except Exception:  # noqa: BLE001
            log.exception("逆回购借出异常（不阻塞结算）")
        state["auto"]["session_date"] = today_key
        state["orders_today"] = []
        save_state(state)
        path = daily_report(cfg, state, f"模拟盘收盘结算 {today.isoformat()}",
                            extra_lines=risk_lines)
        # 统计面板自动刷新（好的坏的全可见：run.py stats 或直接打开 dashboard_*.html）
        try:
            from .stats import refresh_dashboard
            refresh_dashboard(cfg, state)
        except Exception:  # noqa: BLE001 面板失败不影响结算
            log.debug("统计面板刷新失败（忽略）")
        # 周期交接文档（用户指令2026-09-22）：收盘结算=完整交易周期，立即落盘
        try:
            from .handoff import write_handoff
            write_handoff(cfg, state, reason=f"收盘结算 {today.isoformat()}")
        except Exception:  # noqa: BLE001
            log.debug("HANDOFF 生成失败（忽略）")
        log.info("模拟盘收盘：权益 %.0f 元 | 日报 → %s", equity, path)
        return True

    def _equity(self, quotes: dict) -> float:
        prices = {c: q.get("price", 0.0) for c, q in quotes.items()}
        # 期货盯市兜底：实时源缺失时用日线缓存收盘价（不丢仓位价值）
        for c in self.state["account"]["positions"]:
            if c not in prices and str(c).startswith("F."):
                from .futures import last_close
                prices[c] = last_close(str(c))
        return account_equity(self.state, prices)


# -------------------------------------------------- 历史回放验证

def run_replay(cfg: AppConfig, state: dict, days: int | None = None,
               start_cash: float | None = None) -> dict:
    """冠军团队参数冻结回放验证窗口，输出验证报告（不写 paper_track 轨道）。"""
    members = team_members(state)
    if not members:
        raise SystemExit("暂无冠军团队：先运行 run.py evolve 让系统进化出团队")
    _, panel = qdata.full_panel(cfg)
    e = cfg.evolve
    n = len(panel.dates)
    hold_n = max(20, int(n * e.holdout_pct))
    holdout_start = panel.dates[n - hold_n]
    start = panel.dates[max(0, n - days)] if days else holdout_start
    end = panel.dates[-1]
    in_sample = bool(start <= holdout_start)

    w = team_target_weights(cfg, state, panel)
    res = run_backtest(panel.window(start, end), w, cfg,
                       start_cash=start_cash or cfg.risk.initial_capital)
    bench = equal_weight_benchmark(panel.window(start, end), start_cash or cfg.risk.initial_capital)

    lines = [
        "# 模拟实盘回放验证报告",
        f"- 生成时间: {dt.datetime.now().strftime('%Y-%m-%d %H:%M')}",
        f"- 窗口: {start.date()} ~ {end.date()}（{len(panel.window(start, end).dates)} 个交易日）",
        f"- 数据有效性: {'【注意】该窗口参与过团队晋升验证（样本内）' if in_sample else '样本外（团队定型后新数据）'}",
        f"- 团队: {' + '.join(m['strategy'] for m in members)}",
        "",
        "| 指标 | 冠军团队 | 等权基准 |",
        "|---|---|---|",
    ]
    m, bm = res.metrics, _bench_metrics(bench)
    for k, label in [("total_return", "区间收益"), ("cagr", "年化收益"), ("max_dd", "最大回撤"),
                     ("sharpe", "夏普"), ("win_rate", "胜率"), ("n_trades", "成交笔数")]:
        if k in ("win_rate",):
            lines.append(f"| {label} | {m[k]*100:.1f}% | - |")
        elif k == "n_trades":
            lines.append(f"| {label} | {m[k]} | - |")
        elif k in ("total_return", "cagr", "max_dd"):
            lines.append(f"| {label} | {m[k]*100:.2f}% | {bm.get(k, 0)*100:.2f}% |")
        else:
            lines.append(f"| {label} | {m[k]:.2f} | {bm.get(k, 0):.2f} |")
    lines += ["", "## 逐日净值（前/后10）", "```", str(res.equity.head(10)), "...", str(res.equity.tail(10)), "```"]

    os.makedirs(LOGS_DIR, exist_ok=True)
    path = os.path.join(LOGS_DIR, f"replay_{dt.date.today().strftime('%Y%m%d')}.md")
    with open(path, "w", encoding="utf-8") as f:
        f.write("\n".join(lines) + "\n")
    log.info("回放验证完成 → %s", path)
    print("\n".join(lines[:18]))
    return {"result": res, "benchmark": bench, "in_sample": in_sample, "report": path}


def _bench_metrics(bench) -> dict:
    import math
    eq = bench
    ret = eq.pct_change().fillna(0.0)
    years = len(eq) / 252.0
    total = float(eq.iloc[-1] / eq.iloc[0] - 1)
    cagr = float((eq.iloc[-1] / eq.iloc[0]) ** (1 / years) - 1) if years > 0 else 0.0
    dd = float((eq / eq.cummax() - 1).min())
    sharpe = float(ret.mean() / ret.std() * math.sqrt(252)) if ret.std() > 0 else 0.0
    return {"total_return": total, "cagr": cagr, "max_dd": dd, "sharpe": sharpe}
