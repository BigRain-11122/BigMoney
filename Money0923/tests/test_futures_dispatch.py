"""期货分流接线回归测试（2026-09-21 全品种指令）。

run_backtest 按权重矩阵分流：非零列全为 F.* → 期货专用引擎（保证金/双向/按手/T+0）；
混合股票+期货权重 → 空仓曲线+留痕（防股票引擎错误撮合期货列）；纯股票路径零污染。
运行: python tests/test_futures_dispatch.py
"""
import os
import sys

import numpy as np
import pandas as pd

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from quant.backtest import run_backtest  # noqa: E402
from quant.config import AppConfig  # noqa: E402
from quant.data import PanelData  # noqa: E402


def make_mixed_panel(n: int = 30) -> PanelData:
    """合成面板：F.IF 温和上行 + 600000 走平（期货列与股票列共存）。"""
    dates = pd.date_range("2025-03-03", periods=n, freq="B")
    if_close = 3900.0 * np.cumprod(1.0 + np.full(n, 0.004))
    if_open = np.concatenate([[3900.0], if_close[:-1]])
    st = np.full(n, 10.5)
    close = pd.DataFrame({"F.IF": if_close, "600000": st}, index=dates)
    op = pd.DataFrame({"F.IF": if_open, "600000": st}, index=dates)
    high, low = close * 1.002, close * 0.998
    volume = pd.DataFrame({c: np.full(n, 1e7) for c in close.columns}, index=dates)
    amount = volume * close
    return PanelData(open=op, high=high, low=low, close=close, volume=volume,
                     amount=amount, codes=list(close.columns), dates=dates)


def test_pure_futures_routes():
    panel = make_mixed_panel()
    cfg = AppConfig()
    w = pd.DataFrame(0.0, index=panel.dates, columns=panel.codes)
    w["F.IF"] = 0.5   # 保证金份额（100万本金 → IF 约3手）
    res = run_backtest(panel, w, cfg, start_cash=1_000_000)
    reasons = {t["reason"] for t in res.trades}
    assert reasons and all(r.startswith("fut_") for r in reasons), f"必须路由到期货引擎: {reasons}"
    assert all(t["code"] == "F.IF" for t in res.trades), "只允许期货列成交"
    assert res.metrics["n_trades"] > 0
    assert res.equity.iloc[-1] > 1_000_000, "IF 温和上行+多头应盈利"
    assert res.invested.iloc[-1] > 0, "invested 应为名义市值（期货为带符号市值）"
    print("纯期货分流 OK:", {k: round(v, 4) for k, v in res.metrics.items()
                            if isinstance(v, float)})


def test_mixed_weights_flat():
    panel = make_mixed_panel()
    cfg = AppConfig()
    w = pd.DataFrame(0.0, index=panel.dates, columns=panel.codes)
    w["F.IF"] = 0.5
    w["600000"] = 0.15
    res = run_backtest(panel, w, cfg, start_cash=1_000_000)
    assert res.trades == [], "混合权重必须空仓（暂不支持）"
    assert np.allclose(res.equity.to_numpy(), 1_000_000), "空仓=权益恒等于本金"
    assert res.metrics["n_trades"] == 0
    print("混合权重空仓防护 OK")


def test_stock_only_unchanged():
    panel = make_mixed_panel()
    cfg = AppConfig()
    cfg.risk.repo_enabled = False   # 本测试验证期货分流隔离；逆回购计息另见 tests/test_repo.py
    w = pd.DataFrame(0.0, index=panel.dates, columns=panel.codes)
    w["600000"] = 0.15
    res = run_backtest(panel, w, cfg)
    assert res.trades and all(t["code"] == "600000" for t in res.trades), "股票路径成交"
    assert all(not t["reason"].startswith("fut_") for t in res.trades)
    assert res.trades[0]["shares"] % 100 == 0, "股票整手"
    assert abs(float(res.equity.iloc[-1]) - cfg.risk.initial_capital) < 300.0, \
        "走平股≈持平（差额=手续费+滑点成本）"
    print("股票主路径零污染 OK")


def test_selfserve_engine():
    """CTA 自服务架构：纯股票面板（无 F.* 列）+ F.* 权重 → 分流引擎按窗口自取真实缓存。"""
    from quant.futures import _fut_cache_df
    df = _fut_cache_df("IF")
    assert df is not None and len(df) >= 60, "期货日线缓存缺失（等 auto 日更或先跑 futures 日更）"
    dates = df.index[-150:]
    n = len(dates)
    close = pd.DataFrame({"600000": np.full(n, 10.5)}, index=dates)
    op = close.copy()
    high, low = close * 1.002, close * 0.998
    volume = pd.DataFrame({"600000": np.full(n, 1e7)}, index=dates)
    panel = PanelData(open=op, high=high, low=low, close=close, volume=volume,
                      amount=volume * close, codes=list(close.columns), dates=dates)
    w = pd.DataFrame(0.0, index=dates, columns=["F.IF"])
    w["F.IF"] = 0.5
    res = run_backtest(panel, w, AppConfig(), start_cash=1_000_000)
    reasons = {t["reason"] for t in res.trades}
    assert reasons and all(r.startswith("fut_") for r in reasons), reasons
    assert res.metrics["n_trades"] > 0, "真实缓存窗口内必须有成交"
    assert abs(float(res.equity.iloc[-1]) - 1_000_000) > 1.0, "真实IF波动→权益必变化"
    print("自服务引擎 OK: 无F.*列面板→按窗口自取，成交 %d 笔，期末权益 %.0f"
          % (res.metrics["n_trades"], float(res.equity.iloc[-1])))


if __name__ == "__main__":
    test_pure_futures_routes()
    test_mixed_weights_flat()
    test_stock_only_unchanged()
    test_selfserve_engine()
    print("test_futures_dispatch 全部通过")
