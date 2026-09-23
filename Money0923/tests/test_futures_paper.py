"""模拟盘期货撮合+规划器接线冒烟（2026-09-21 全品种指令，闸后惰性代码）。

合成数据隔离测试：不读不写 state.json（patch 掉 paper.save_state）。
覆盖：①plan_orders 期货手数规划（多头/空头/预算缩减/股票分流）
     ②PaperSession._execute 期货撮合（开平/翻向/已实现盈亏/涨跌停拒开/保证金缩量）
     ③account_equity 期货盯市（现金池模型：成交瞬间只掉手续费）
运行: python tests/test_futures_paper.py
"""
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import quant.paper as paper_mod  # noqa: E402
from quant.config import AppConfig  # noqa: E402
from quant.decide import account_equity  # noqa: E402
from quant.futures import futures_meta  # noqa: E402
from quant.paper import PaperSession  # noqa: E402
from quant.risk import RiskManager  # noqa: E402

# 隔离铁律：_execute 内部 save_state 严禁落盘（2026-09-20 16:35 state 污染事故教训）
paper_mod.save_state = lambda s: None

TODAY = "20260921"


def make_state(cash: float = 1_000_000.0) -> dict:
    return {"account": {"cash": cash, "positions": {}},
            "risk": {"halt": False, "daily_breaker_date": ""},
            "trade_log": [], "auto": {}}


def q(price: float, up: float = 4869.2, dn: float = 3984.0) -> dict:
    return {"F.IF": {"name": "沪深300股指主力", "price": price, "prev_close": 4426.6,
                     "amount": 1.2e8, "up_limit": up, "dn_limit": dn}}


def test_plan_futures():
    cfg = AppConfig()
    rm = RiskManager(cfg, make_state())
    prices = {"F.IF": {"price": 4500.0}, "600000": {"price": 10.5}}
    orders = rm.plan_orders({"F.IF": 0.5, "600000": 0.15}, {}, prices,
                            1_000_000.0, 1_000_000.0, TODAY)
    fut = [o for o in orders if o["code"] == "F.IF"]
    stk = [o for o in orders if o["code"] == "600000"]
    # 多头：0.5×1M ÷(300×4500×0.12)=3.08 → 3手
    assert fut and fut[0]["side"] == "buy" and fut[0]["shares"] == 3 \
        and fut[0]["reason"] == "fut_open", fut
    assert stk and stk[0]["side"] == "buy" and stk[0]["shares"] % 100 == 0, stk
    # 空头：负权重 → 开空单（0.3×1M÷162000=1.85→1手）
    orders2 = rm.plan_orders({"F.IF": -0.3}, {}, prices, 1_000_000.0, 1_000_000.0, TODAY)
    o2 = [o for o in orders2 if o["code"] == "F.IF"]
    assert o2 and o2[0]["side"] == "sell" and o2[0]["shares"] == 1 \
        and o2[0]["reason"] == "fut_open", o2
    # 保证金总预算：多品种超权益 → 逐手缩减后 Σ占用 ≤ 权益
    prices3 = {"F.T": {"price": 109.0}, "F.TF": {"price": 106.5}, "F.IF": {"price": 4500.0}}
    orders3 = rm.plan_orders({"F.T": 0.5, "F.TF": 0.5, "F.IF": 0.5}, {}, prices3,
                             1_000_000.0, 1_000_000.0, TODAY)
    usage = sum(o["shares"] * futures_meta(o["code"])["mult"]
                * prices3[o["code"]]["price"] * futures_meta(o["code"])["margin"]
                for o in orders3)
    assert usage <= 1_000_000.0 + 1e-6, f"预算缩减失效: {usage}"
    assert len(orders3) == 3, orders3
    print("期货规划器 OK: 多头3手/空头1手/股票分流/预算缩减（占用 %.0f ≤ 100万）" % usage)


def test_execute_futures():
    cfg = AppConfig()
    st = make_state()
    s = PaperSession(cfg, st)
    fee_lot = futures_meta("F.IF")["fee_lot"]

    # 开多3手：现金池流出名义，权益=本金-手续费
    n = s._execute([{"code": "F.IF", "side": "buy", "shares": 3,
                     "reason": "fut_open"}], q(4500.0), "open")
    assert n == 1
    p = st["account"]["positions"]["F.IF"]
    assert p["lots"] == 3 and abs(p["avg_entry"] - 4500.0) < 1e-9
    assert abs(st["account"]["cash"] - (1_000_000 - 3 * 300 * 4500 - 3 * fee_lot)) < 1e-6
    assert abs(account_equity(st, {"F.IF": 4500.0}) - (1_000_000 - 3 * fee_lot)) < 1e-6, \
        "成交瞬间权益只掉手续费"
    print(f"开多3手 OK: 现金 {st['account']['cash']:+,.0f} "
          f"权益 {account_equity(st, {'F.IF': 4500.0}):,.0f}（只掉3手手续费）")

    # 平1手@4600：已实现盈亏=(4600-4500)×300×1-fee
    n = s._execute([{"code": "F.IF", "side": "sell", "shares": 1,
                     "reason": "fut_close"}], q(4600.0), "stop")
    assert n == 1 and st["account"]["positions"]["F.IF"]["lots"] == 2
    assert st["trade_log"][-1]["pnl"] == round((4600.0 - 4500.0) * 300 - fee_lot, 2)
    print("平1手 OK: 已实现盈亏 %+.0f" % st["trade_log"][-1]["pnl"])

    # 翻空：平2手@4700 + 开空2手@4700 → lots=-2 均价4700
    s._execute([{"code": "F.IF", "side": "sell", "shares": 2, "reason": "fut_close"},
                {"code": "F.IF", "side": "sell", "shares": 2, "reason": "fut_open"}],
               q(4700.0), "open")
    p = st["account"]["positions"]["F.IF"]
    assert p["lots"] == -2 and abs(p["avg_entry"] - 4700.0) < 1e-9, p
    # 空头平仓回补@4500：盈亏=(4500-4700)×(-1)×300×2-2×fee = +119,944.8
    s._execute([{"code": "F.IF", "side": "buy", "shares": 2, "reason": "fut_close"}],
               q(4500.0), "stop")
    assert "F.IF" not in st["account"]["positions"], "清零后仓位应移除"
    assert st["trade_log"][-1]["pnl"] == round((4500.0 - 4700.0) * -1 * 300 * 2 - 2 * fee_lot, 2)
    print("翻空+回补 OK: 空头已实现盈亏 %+.0f，仓位清零移除" % st["trade_log"][-1]["pnl"])

    # 撞涨停拒开多
    n = s._execute([{"code": "F.IF", "side": "buy", "shares": 1, "reason": "fut_open"}],
                    q(4869.2), "open")
    assert n == 0, "涨停日开多必须被拒"
    # 撞跌停拒开空
    n = s._execute([{"code": "F.IF", "side": "sell", "shares": 1, "reason": "fut_open"}],
                    q(3984.0, up=4869.2, dn=3984.0), "open")
    assert n == 0, "跌停日开空必须被拒"
    print("涨跌停拒开 OK")

    # 保证金预算缩量：开100手T（占用218万 > 权益100万）→ 逐手缩到45手
    st2 = make_state()
    s2 = PaperSession(cfg, st2)
    tq = {"F.T": {"name": "十年国债主力", "price": 109.0, "prev_close": 109.5,
                  "amount": 5e6, "up_limit": 111.7, "dn_limit": 107.3}}
    n = s2._execute([{"code": "F.T", "side": "buy", "shares": 100, "reason": "fut_open"}],
                    tq, "open")
    m = futures_meta("F.T")
    got = st2["account"]["positions"]["F.T"]["lots"]
    usage = got * m["mult"] * 109.0 * m["margin"]
    assert n == 1 and 0 < got < 100 and usage <= 1_000_000.0, (n, got, usage)
    print("保证金缩量 OK: 100手→%d手（占用 %.0f ≤ 100万）" % (got, usage))


def test_equity_marking():
    st = make_state()
    st["account"]["cash"] = 500_000.0
    st["account"]["positions"] = {"F.IF": {"lots": -2, "avg_entry": 4500.0},
                                   "600000": {"shares": 1000, "cost": 10.0}}
    eq = account_equity(st, {"F.IF": 4400.0, "600000": 11.0})
    # 空头市值=-2×300×4400=-264万；股票1.1万 → 权益=50万-264万+1.1万=-212.9万
    assert abs(eq - (500_000 - 2 * 300 * 4400.0 + 1000 * 11.0)) < 1e-6
    # 行情缺失 → avg_entry 兜底
    eq2 = account_equity(st, {"600000": 11.0})
    assert abs(eq2 - (500_000 - 2 * 300 * 4500.0 + 1000 * 11.0)) < 1e-6
    print("期货盯市 OK: 带符号市值 %.0f / 行情缺失兜底 %.0f" % (eq, eq2))


if __name__ == "__main__":
    test_plan_futures()
    test_execute_futures()
    test_equity_marking()
    print("test_futures_paper 全部通过")
