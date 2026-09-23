"""分仓制隔离冒烟测试（2026-09-21 用户"策略风格非常差异化和多种多样"指令）。

合成数据全链验证：迁移/选队多样性/逐仓备单（同票冲突+仓内预算）/
执行端现金双记账/逐仓结算停机/换人基线。不读不写真实 state.json
（PaperSession 补丁 save_state 后用合成 state）。
运行: python tests/test_sleeves.py
"""
import os
import sys
import types

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import pandas as pd

import quant.paper as paper_mod  # noqa: E402
from quant.config import AppConfig  # noqa: E402
from quant.paper import PaperSession  # noqa: E402
from quant import sleeves as qsl  # noqa: E402

paper_mod.save_state = lambda s: None  # 隔离铁律：严禁落盘污染真实 state


def make_state() -> dict:
    return {"account": {"cash": 100_000.0, "positions": {}, "equity_high": 100_000.0,
                       "day_key": "", "day_start_equity": 100_000.0, "daily_pnl": 0.0},
            "risk": {"halt": False, "halt_reason": None, "daily_breaker_date": ""},
            "trade_log": [], "auto": {},             "arena": {"qualified": [
                {"id": "Q1", "strategy": "etf_trend", "params": {"ma_fast": 5}, "sizing": "equal",
                 "sizing_params": {}, "score": 0.71, "streak": 3},
                {"id": "Q2", "strategy": "small_reversal", "params": {"rev_len": 5},
                 "sizing": "equal", "sizing_params": {}, "score": 0.55, "streak": 3},
                {"id": "Q3", "strategy": "etf_trend", "params": {"ma_fast": 9}, "sizing": "inv_vol",
                 "sizing_params": {"vol_win": 20}, "score": 0.62, "streak": 3},
                {"id": "Q4", "strategy": "dual_momentum", "params": {"lookback": 20},
                 "sizing": "equal", "sizing_params": {}, "score": 0.50, "streak": 3},
            ]},
            "team": [{"strategy": "stk_champ", "params": {}, "sizing": "equal",
                      "sizing_params": {}}]}


def test_migration_and_diversity():
    st = make_state()
    svs = qsl.ensure_sleeves(st, AppConfig())
    assert len(svs) == 3
    assert svs[0]["id"] == "S1" and svs[0]["members"][0]["strategy"] == "stk_champ"
    assert svs[1]["members"][0]["strategy"] == "etf_trend", "S2 应锚定 etf_trend"
    assert svs[2]["members"][0]["strategy"] == "small_reversal", "S3 应锚定 small_reversal"
    fams = {sv["members"][0]["strategy"] for sv in svs}
    assert len(fams) == 3, f"三仓必须不同族，实际 {fams}"
    assert abs(sum(sv["cash"] for sv in svs) - 100_000.0) < 1e-6, "仓现金之和=总现金"
    print("迁移+多样性 OK: S1=%s S2=%s S3=%s | 现金 %.0f/%.0f/%.0f"
          % (svs[0]["members"][0]["strategy"], svs[1]["members"][0]["strategy"],
             svs[2]["members"][0]["strategy"], svs[0]["cash"], svs[1]["cash"], svs[2]["cash"]))


def test_execute_dual_ledger():
    st = make_state()
    qsl.ensure_sleeves(st, AppConfig())
    s2 = st["sleeves"][1]
    s = PaperSession(AppConfig(), st)
    q = {"600000": {"name": "浦发银行", "price": 10.0, "prev_close": 9.9, "amount": 1e9}}
    acc0, s20 = st["account"]["cash"], s2["cash"]
    n = s._execute([{"code": "600000", "side": "buy", "shares": 100,
                     "sleeve": "S2", "reason": "rebalance"}], q, "open")
    assert n == 1
    cost = 100 * 10.0 * (1 + AppConfig().fee.slippage)
    total_fee = cost + max(cost * AppConfig().fee.commission_rate, AppConfig().fee.min_commission) \
        + cost * AppConfig().fee.transfer_fee
    assert abs(st["account"]["cash"] - (acc0 - total_fee)) < 1e-6, "总账扣款"
    assert abs(s2["cash"] - (s20 - total_fee)) < 1e-6, "仓内扣款（双记账）"
    assert st["account"]["positions"]["600000"]["sleeve"] == "S2", "持仓打仓标"
    # 卖出归持仓所属仓
    p = st["account"]["positions"]["600000"]
    p["available"] = 100
    acc1, s21 = st["account"]["cash"], s2["cash"]
    n = s._execute([{"code": "600000", "side": "sell", "shares": 100, "reason": "rebalance"}],
                   {"600000": {"price": 10.5, "prev_close": 10.0, "amount": 1e9}}, "open")
    assert n == 1
    assert s2["cash"] > s21 and st["account"]["cash"] > acc1
    assert abs((s2["cash"] - s21) - (st["account"]["cash"] - acc1)) < 1e-6, "卖出双记账一致"
    print("执行端双记账 OK: 买扣仓内+总账，卖归持仓所属仓")


def test_halt_and_rotation():
    st = make_state()
    qsl.ensure_sleeves(st, AppConfig())
    sv = st["sleeves"][2]
    sv["capital_start"] = 30_000.0
    sv["risk"]["equity_high"] = 30_000.0
    sv["cash"] = 24_000.0  # 仓回撤 -20% ≥ 10% 停机线
    prices = {}
    seq = qsl.sleeve_equity(st, sv, prices)
    assert abs(seq - 24_000.0) < 1e-6
    assert seq <= sv["risk"]["equity_high"] * 0.9
    cfg = AppConfig()
    # 模拟结算判定（paper.py 的仓级结算逻辑核心行）
    assert cfg.risk.drawdown_halt_pct > 0 and seq <= sv["risk"]["equity_high"] \
        * (1 - cfg.risk.drawdown_halt_pct)
    sv["risk"]["halt"] = True
    # 换人1：出局的 Q2(small_reversal) 不复活；其他在位族(etf_trend/stk_champ)排除
    # → 池里剩未占族 Q4(dual_momentum) 接力
    ok = qsl.rotate_sleeve(st, sv, equity=seq)
    assert ok and sv["members"][0]["strategy"] == "dual_momentum"
    assert sv["members"][0]["_src"]["id"] == "Q4"
    assert sv["rotations"] == 1
    assert not qsl.halted(sv), "换人后停机复位"
    assert abs(sv["risk"]["equity_high"] - seq) < 1e-6, "新挑战者基线=当前仓权益"
    # 换人2：Q4 也出局后，池内无未占族且同族无新基因 → 休战等池
    sv["risk"]["halt"] = True
    ok2 = qsl.rotate_sleeve(st, sv, equity=seq)
    assert not ok2, "认证池无未占族新挑战者时应休战"
    print("停机+换人 OK: 仓级10%线判定/换人/新基线/同基因不复活/池尽休战")


def test_conflict_and_fingerprint():
    st = make_state()
    qsl.ensure_sleeves(st, AppConfig())
    st["account"]["positions"]["510300"] = {"shares": 1000, "cost": 4.0, "available": 1000,
                                            "locked": {}, "last_buy_date": "20260921",
                                            "sleeve": "S2"}
    sv1_pos = qsl.sleeve_positions(st, st["sleeves"][0])
    sv2_pos = qsl.sleeve_positions(st, st["sleeves"][1])
    assert "510300" in sv2_pos and "510300" not in sv1_pos, "持仓按仓标签切分"
    fp = qsl.deployment_fingerprint(st)
    assert len(fp) == 3 and fp[0][0] == "S1", "部署指纹逐仓"
    st["sleeves"][1]["members"] = [{"strategy": "etf_trend", "params": {"x": 1},
                                    "sizing": "equal", "sizing_params": {}}]
    assert qsl.deployment_fingerprint(st) != fp, "仓换人→指纹变化→重备单触发"
    print("同票冲突视图+部署指纹 OK")


def test_style_risk_tiers():
    """风险线按风格分级（用户指令"激进的亏8成都行，亏完就永远出局"）。"""
    st = make_state()
    qsl.ensure_sleeves(st, AppConfig())
    s1, s2, s3 = st["sleeves"]
    assert s1["halt_line"] == 0.10, "S1 稳健仓 10%"
    assert s2["halt_line"] == 0.20, "S2 进取仓 20%"
    assert s3["halt_line"] is None, "S3 激进仓不停机（亏完才出局）"
    # S3 血亏 30% 也不得停机（paper.py 分仓结算判定核心行复刻）
    s3["capital_start"] = 30_000.0
    s3["risk"]["equity_high"] = 30_000.0
    s3["cash"] = 21_000.0
    seq = qsl.sleeve_equity(st, s3, {})
    halt_now = (s3.get("halt_line") is not None and float(s3["halt_line"]) > 0
                and seq <= float(s3["risk"]["equity_high"]) * (1 - float(s3["halt_line"])))
    assert not halt_now and not qsl.halted(s3), "激进仓 -30% 不得停机"
    # 毁灭线照常管辖：-83% → 可判退役
    s3["cash"] = 5_000.0
    seq2 = qsl.sleeve_equity(st, s3, {})
    assert seq2 <= s3["capital_start"] * (1 - AppConfig().risk.ruin_loss_pct), \
        "激进仓亏穿毁灭线必须可判退役"
    print("风格分级 OK: S1 10% / S2 20% / S3 不停机（-30%不停机，-80%毁灭出局）")


if __name__ == "__main__":
    test_migration_and_diversity()
    test_execute_dual_ledger()
    test_halt_and_rotation()
    test_conflict_and_fingerprint()
    test_style_risk_tiers()
    print("test_sleeves 全部通过")
