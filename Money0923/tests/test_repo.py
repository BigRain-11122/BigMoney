# 国债逆回购现金管理回归测试（用户指令2026-09-22"现金加入国债逆回购赚隔夜收益"）
# 全部隔离：利率文件/实盘路径全部 monkeypatch 到临时目录，不碰真实 state.json 与 data/。
# 运行：python -m pytest tests/test_repo.py -q  （或 python tests/test_repo.py）
import datetime as dt
import os
import sys
import tempfile

import numpy as np
import pandas as pd

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from quant.backtest import run_backtest                     # noqa: E402
from quant.config import AppConfig                          # noqa: E402
from quant.data import PanelData                           # noqa: E402
from quant.decide import account_equity                    # noqa: E402
from quant import repo as qrepo                             # noqa: E402


def _mk_panel(n_days: int = 40):
    rng = np.random.default_rng(7)
    dates = pd.bdate_range("2024-01-02", periods=n_days)
    codes = ["AAA", "BBB"]
    close = pd.DataFrame(100.0 + np.cumsum(rng.normal(0, 0.4, (n_days, 2)), axis=0),
                         index=dates, columns=codes)
    op = close * 1.001
    return PanelData(open=op, high=close * 1.01, low=close * 0.99, close=close,
                     volume=pd.DataFrame(1e8, index=dates, columns=codes),
                     amount=pd.DataFrame(1e10, index=dates, columns=codes),
                     codes=codes, dates=dates)


def _with_rate_file(tmp, dates, rate=5.0):
    """把利率缓存指到临时文件（恒定利率便于闭式核对），并清进程缓存。"""
    df = pd.DataFrame({"date": [d.strftime("%Y-%m-%d") for d in dates],
                       "rate": [rate] * len(dates)})
    path = os.path.join(tmp, "repo_daily.csv")
    df.to_csv(path, index=False)
    qrepo._REPO_FILE = path
    qrepo._rmap_cache = None
    qrepo._rmap_mtime = -1.0


def test_lend_amount_threshold():
    assert qrepo.lend_amount(999.0) == 0.0, "不足1000不借"
    assert qrepo.lend_amount(1000.0) == 1000.0
    assert qrepo.lend_amount(19999.0) == 19000.0, "1000整数倍"
    assert qrepo.lend_amount(0.0) == 0.0


def test_interest_math():
    cfg = AppConfig()
    # 2%年化 借10000元 1天：息 10000×0.02/365=0.5479；费 10000×1e-5=0.1
    assert abs(qrepo.interest(10_000, 2.0, 1, cfg) - 10_000 * 0.02 / 365) < 1e-9
    assert abs(qrepo.fee(10_000, cfg) - 0.1) < 1e-12
    net = qrepo.net_interest(10_000, 2.0, 1, cfg)
    assert abs(net - (10_000 * 0.02 / 365 - 0.1)) < 1e-9, "净利息=息-费"
    # 3天占款（周五）利息×3
    assert abs(qrepo.interest(10_000, 2.0, 3, cfg) - 3 * 10_000 * 0.02 / 365) < 1e-9


def test_lend_days_calendar():
    # 2026-09-25是周五 → 下一交易日周一 → 占款3天（真实交易日历）
    assert qrepo.lend_days(dt.date(2026, 9, 25)) == 3
    # 周二 → 周三1天
    assert qrepo.lend_days(dt.date(2026, 9, 22)) == 1


def test_overnight_yield_series():
    cfg = AppConfig()
    with tempfile.TemporaryDirectory() as tmp:
        panel = _mk_panel()
        _with_rate_file(tmp, panel.dates, rate=5.0)
        strs = [d.strftime("%Y-%m-%d") for d in panel.dates]
        y = qrepo.overnight_cash_yield(strs, cfg)
        assert y is not None and len(y) == len(panel.dates)
        for i in range(len(panel.dates) - 1):
            days = (panel.dates[i + 1].date() - panel.dates[i].date()).days
            expect = 5.0 / 100.0 * days / 365 - 1e-5   # 占款按自然日（跨周末=3天）
            assert abs(y[i] - expect) < 1e-12, f"第{i}日收益率应按{days}天占款计息"


def test_backtest_cash_accrues_repo():
    """空仓组合的现金也必须按真实利率隔夜增值（三端一致：现金不是死钱）。"""
    cfg = AppConfig()
    panel = _mk_panel()
    w = pd.DataFrame(0.0, index=panel.dates, columns=panel.codes)
    with tempfile.TemporaryDirectory() as tmp:
        # 关闸对照：repo_enabled=False → 权益恒等于本金
        cfg_off = AppConfig()
        cfg_off.risk.repo_enabled = False
        _with_rate_file(tmp, panel.dates, rate=5.0)
        res_off = run_backtest(panel, w, cfg_off)
        assert np.allclose(res_off.equity.to_numpy(), cfg_off.risk.initial_capital), \
            "关闸时现金收益必须为0"

        # 开闸：恒定5%年化，占款天数跨周末3天 → 逐夜复利乘积闭式核对
        yields = qrepo.overnight_cash_yield(
            [d.strftime("%Y-%m-%d") for d in panel.dates], cfg)
        prods = [1 + v for v in yields[:-1]]      # 最后一夜的利息落在窗外不计
        res = run_backtest(panel, w, cfg, start_cash=1_000_000)
        expected = 1_000_000 * float(np.prod(prods))
        assert abs(res.equity.iloc[-1] - expected) < 0.01, \
            f"复利核对: {res.equity.iloc[-1]:.2f} vs {expected:.2f}"
        assert res.metrics["n_trades"] == 0
    qrepo._rmap_cache = None


def test_paper_lend_return_roundtrip():
    """模拟盘借出/归还双记账闭环：仓内现金与总账同步；权益含在途本金。"""
    cfg = AppConfig()
    state = {
        "account": {"cash": 20_000.0, "positions": {}},
        "sleeves": [
            {"id": "S1", "cash": 4_500.0},
            {"id": "S3", "cash": 15_500.0},
        ],
    }
    today = dt.date(2026, 9, 22)
    with tempfile.TemporaryDirectory() as tmp:
        _with_rate_file(tmp, [today], rate=2.0)
        opened = qrepo.paper_lend(state, cfg, today)
        # S1借4000、S3借15000，总20000；双记账：Σ仓内现金 == 总账现金
        assert [r["amount"] for r in opened] == [4_000.0, 15_000.0]
        assert state["sleeves"][0]["cash"] == 500.0
        assert state["sleeves"][1]["cash"] == 500.0
        assert abs(state["account"]["cash"] - 1_000.0) < 1e-9, "总账同步扣减"
        assert abs(sum(sv["cash"] for sv in state["sleeves"])
                   - state["account"]["cash"]) < 1e-9, "双记账不变式"
        # 在途本金计入权益（借出≠浮亏）：1000现金 + 19000在途 = 20000
        assert abs(account_equity(state, {}) - 20_000.0) < 1e-9

        # 次日归还：本息入账，不变式保持（现金簿按分位round，容差0.02）
        returned = qrepo.paper_return(state, "20260923")
        assert len(returned) == 2
        total_back = sum(r["amount"] + r["interest"] - r["fee"] for r in returned)
        assert abs(state["account"]["cash"] - (1_000.0 + total_back)) < 0.02
        assert abs(sum(sv["cash"] for sv in state["sleeves"])
                   - state["account"]["cash"]) < 1e-9
        assert abs(qrepo.total_interest_earned(state)
                   - sum(r["interest"] - r["fee"] for r in returned)) < 0.02
        assert qrepo.open_principal(state) == 0.0
        # 不该归还的不动（占款期未到）
        state["repo_open"] = [{"date": "2026-09-25", "sleeve": "S1", "amount": 1000.0,
                               "rate": 2.0, "days": 3, "interest": 0.16, "fee": 0.01,
                               "return_date": "20260928"}]
        assert qrepo.paper_return(state, "20260923") == []
    qrepo._rmap_cache = None


def main():
    test_lend_amount_threshold()
    test_interest_math()
    test_lend_days_calendar()
    test_overnight_yield_series()
    test_backtest_cash_accrues_repo()
    test_paper_lend_return_roundtrip()
    print("test_repo 全部通过：门槛/计息/占款/引擎复利/双记账闭环")


if __name__ == "__main__":
    main()
