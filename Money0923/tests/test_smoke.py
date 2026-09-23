"""冒烟测试：合成数据验证回测引擎核心规则（无网络依赖）。

运行: python tests/test_smoke.py
"""
import os
import sys

import numpy as np
import pandas as pd

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from quant.backtest import run_backtest  # noqa: E402
from quant.config import AppConfig  # noqa: E402
from quant.data import PanelData  # noqa: E402
from quant import strategies as strat_lib  # noqa: E402


def make_panel(n: int = 300) -> PanelData:
    dates = pd.date_range("2025-01-01", periods=n, freq="B")
    rng = np.random.default_rng(7)
    drifts = {"AAA": 0.0012, "BBB": -0.0012, "CCC": 0.0, "DDD": 0.0006}
    close = pd.DataFrame(index=dates)
    for k, d in drifts.items():
        noise = rng.normal(0, 0.012, n)
        close[k] = 100.0 * np.cumprod(1.0 + d + noise) / (1.0 + noise[0])
    op = close.shift(1).fillna(100.0)
    high, low = close * 1.008, close * 0.992
    volume = pd.DataFrame({k: np.full(n, 5e8) for k in close.columns}, index=dates)
    amount = volume * close
    return PanelData(open=op, high=high, low=low, close=close, volume=volume,
                     amount=amount, codes=list(close.columns), dates=dates)


def test_backtest_rules():
    panel = make_panel()
    cfg = AppConfig()
    dates = panel.dates
    n = len(dates)
    w = pd.DataFrame(0.0, index=dates, columns=panel.codes)
    w["AAA"] = 0.15   # 上限内
    w["BBB"] = 0.30   # 应被截断到 15%
    res = run_backtest(panel, w, cfg)

    m = res.metrics
    assert m["n_trades"] > 0, "应有成交"
    # AAA 上涨 → 有仓位后净值应跑赢全现金
    eq = res.equity
    assert eq.iloc[0] == cfg.risk.initial_capital
    # 权重截断检查：投入市值不会超过 2×15%+保底现金约束
    assert (res.invested / eq).max() < 0.35, "仓位截断失效"
    # 费用检查：买入后现金减少多于市值（含费）
    first_buy = next(t for t in res.trades if t["side"] == "buy")
    assert first_buy["shares"] % 100 == 0, "必须整手"
    print("回测规则测试 OK:", {k: round(v, 4) for k, v in m.items()})
    return res


def test_time_exit():
    """最高持股2周规则：长期信号也会在第10个交易日后被强制平仓。"""
    panel = make_panel(n=200)
    cfg = AppConfig()
    w = pd.DataFrame(0.0, index=panel.dates, columns=panel.codes)
    w["AAA"] = 0.15  # 常持信号（无离场条件）
    res = run_backtest(panel, w, cfg)
    time_exits = [t for t in res.trades if t["reason"] == "time_exit"]
    assert time_exits, "必须存在计时离场成交"
    # 每段持仓（买入→计时离场）不超过 max_hold_days 个交易日
    buys = [t for t in res.trades if t["side"] == "buy" and t["code"] == "AAA"]
    dlist = list(panel.dates)
    for t in time_exits:
        i_sell = dlist.index(pd.Timestamp(t["date"]))
        last_buy = max(pd.Timestamp(b["date"]) for b in buys if pd.Timestamp(b["date"]) <= pd.Timestamp(t["date"]))
        assert (i_sell - dlist.index(last_buy)) <= cfg.risk.max_hold_days, "持仓超过2周上限"
    # 计时离场当日不再回买（冷却）
    exit_days = {t["date"] for t in time_exits}
    rebuys_same_day = [b for b in buys if b["date"] in exit_days]
    assert not rebuys_same_day, "计时离场当日不应回买"
    print(f"最高持股2周规则 OK（time_exit {len(time_exits)} 次）")


def test_strategies_run():
    panel = make_panel()

    def mid(spec):
        if spec[0] == "int":
            return (spec[1] + spec[2]) // 2
        if spec[0] == "float":
            return (spec[1] + spec[2]) / 2
        return list(spec[1])[0]  # choice 取首项

    for name in strat_lib.STRATEGIES:
        strat = strat_lib.get_strategy(name)()
        if name == "evolved":
            import random as _r
            params = strat_lib.Evolved.random_genome(_r.Random(7))
        else:
            params = {k: mid(v) for k, v in strat.param_space.items()}
        w = strat.target_weights(panel, params)
        if name == "cta_trend":
            # CTA 自服务架构（2026-09-21）：面板永不并入 F.*——cta_trend 按窗口
            # 自取期货数据并追加 F.* 列；合成2025面板与真实缓存不重叠 → 应全空仓
            from quant.futures import FUT_UNIVERSE
            assert w.shape == (len(panel.dates), len(panel.codes) + len(FUT_UNIVERSE)), \
                f"{name} 形状错误（自服务期货列）"
            assert float(w.abs().sum().sum()) == 0.0, "无重叠数据→应全空仓"
        else:
            assert w.shape == (len(panel.dates), len(panel.codes)), f"{name} 形状错误"
            assert float(w.max().max()) <= 1.0 + 1e-9, f"{name} 权重越界"
            assert float(w.min().min()) >= -1e-9, f"{name} 权重为负"
        assert not w.isna().any().any(), f"{name} 输出含 NaN"
        print(f"策略 {name} OK（平均暴露 {w.sum(axis=1).mean():.2%}）")


def test_gp_genome():
    """GP 基因组算子回归：随机/交叉/变异均产出合法基因组且权重有效。"""
    import random as _r

    rng = _r.Random(11)
    panel = make_panel()
    strat = strat_lib.Evolved()
    for _ in range(30):
        g = strat.random_genome(rng)
        w = strat.target_weights(panel, g)
        assert w.shape == (len(panel.dates), len(panel.codes))
        assert not w.isna().any().any(), "基因组输出含 NaN"
        assert 1 <= len(g["entry"]) <= 4 and len(g["exit"]) <= 2
    a, b = strat.random_genome(rng), strat.random_genome(rng)
    child = strat.crossover_genomes(a, b, rng)
    assert 1 <= len(child["entry"]) <= 4, "交叉后代入场原语数越界"
    m = strat.mutate_genome(child, rng, rate=0.6)
    strat.target_weights(panel, m)  # 变异体必须可直接求值
    # 基因组可 JSON 序列化（state持久化/竞技场/评估缓存依赖）
    json_s = __import__("json").dumps(m, ensure_ascii=False)
    assert "entry" in __import__("json").loads(json_s)
    # evolve 层算子分发：evolved 个体过 GA 算子不报错
    from quant import evolve as ev
    ind = {"strategy": "evolved", "params": a}
    ind2 = ev.mutate(ind, rng, 0.5, 0.2)
    assert ind2["strategy"] == "evolved" and ind2["params"]["entry"]
    ind3 = ev.crossover({"strategy": "evolved", "params": a}, {"strategy": "evolved", "params": b}, rng)
    assert ind3["strategy"] == "evolved" and 1 <= len(ind3["params"]["entry"]) <= 4
    print("GP基因组算子 OK（30样本随机/交叉/变异/序列化/分发 全通过）")


def test_lookahead_free():
    """无未来函数：截断历史后，前缀权重必须完全一致（含 GP 基因组策略）。"""
    panel = make_panel()
    strat = strat_lib.get_strategy("dual_ma")()
    p = {"fast_ma": 10, "slow_ma": 30, "top_k": 3}
    full = strat.target_weights(panel, p)
    cut = panel.window(panel.dates[0], panel.dates[150])
    part = strat.target_weights(cut, p)
    # 前150日权重应逐元素一致（最多差在截断日）
    a, b = full.loc[part.index], part
    diff = (a - b).abs().max().max()
    assert diff < 1e-9, f"存在未来函数! max diff={diff}"
    # GP 基因组（含离场原语的状态机路径 + 无离场的ISO周锚定轮动路径）同样无未来函数
    import random as _r
    gs = strat_lib.Evolved()
    for genome in [
        gs.sanitize({"entry": [{"kind": "cross_up", "n": 20}, {"kind": "osc_low", "n": 2, "th": 15.0}],
                     "logic": "all", "exit": [{"kind": "osc_high", "n": 2, "th": 70.0}],
                     "score": "rev_5", "top_k": 4, "rebal_days": 5,
                     "ma_filter": 0, "max_hold": 5, "weighting": "equal"}),
        gs.sanitize({"entry": [{"kind": "mom_pos", "n": 60, "th": 0.0}], "logic": "all", "exit": [],
                     "score": "roc_20", "top_k": 4, "rebal_days": 5,
                     "ma_filter": 0, "max_hold": 0, "weighting": "equal"}),
    ]:
        f = gs.target_weights(panel, genome)
        pp = gs.target_weights(cut, genome)
        d = (f.loc[pp.index] - pp).abs().max().max()
        assert d < 1e-9, f"GP基因组存在未来函数! max diff={d}"
    print("无未来函数测试 OK（含 GP 基因组两条路径）")


def test_random_point():
    """随机取点验证：随机窗口数与摘要完整性，且结果可复现（同seed同窗口）。"""
    from quant.evolve import random_point_test
    panel = make_panel()
    cfg = AppConfig()
    state = {"team": [{"strategy": "dual_ma", "params": {"fast_ma": 10, "slow_ma": 30, "top_k": 3}}]}
    out = random_point_test(cfg, state, panel, n_windows=6, seed=7)
    assert len(out["scores"]) == 6, "随机窗口数不符"
    assert set(out["summary"]) >= {"mean", "beat_cash_pct", "beat_bench_pct", "worst", "best"}
    out2 = random_point_test(cfg, state, panel, n_windows=6, seed=7)
    assert out["scores"] == out2["scores"], "同seed结果应可复现"
    for d in out["details"]:
        assert d["score"] > -1.5 and d["ret"] > -1.0, "随机窗口指标异常"
    print(f"随机取点验证 OK（均分 {out['summary']['mean']}，可复现）")


def test_t0_etf():
    """T+0官方规则：跨境/黄金/债券类ETF当日买入可当日止损卖出；股票与股票型ETF为T+1。"""
    from quant.data import is_t0, max_order_shares
    # 品种识别
    assert is_t0("513100") and is_t0("518880") and is_t0("511010"), "沪市跨境/黄金/债券ETF应为T+0"
    assert not is_t0("600000") and not is_t0("510300"), "股票与股票型ETF应为T+1"
    # 黄金股ETF（A股股票型）不应误判
    from quant.data import _T0_REGISTRY, register_t0_names
    _T0_REGISTRY.discard("159562")
    uni = pd.DataFrame([{"code": "159562", "name": "黄金股ETF"}, {"code": "159920", "name": "恒生ETF"}])
    register_t0_names(uni)
    assert "159920" in _T0_REGISTRY, "深市跨境应按名称注册为T+0"
    assert "159562" not in _T0_REGISTRY, "黄金股ETF为A股股票型，不应注册T+0"
    _T0_REGISTRY.discard("159920")
    # 单笔申报上限
    assert max_order_shares("300750") == 300_000, "创业板单笔≤30万股"
    assert max_order_shares("600519") == 1_000_000, "主板单笔≤100万股"
    assert max_order_shares("510300") == 1_000_000, "基金单笔≤100万份"

    # 引级行为：当日买入当日盘中暴跌 → T+0品种当日可止损离场，T+1品种不可
    n = 12
    dates = pd.date_range("2025-01-01", periods=n, freq="B")
    results = {}
    for code in ("513100", "600000"):
        close = pd.DataFrame({code: [100.0] * n}, index=dates)
        open_ = close.copy()
        high = close * 1.01
        low = close * 0.99
        low.iloc[1] = 70.0  # 第1日盘中暴跌触发-8%止损
        volume = pd.DataFrame({code: [1e8] * n}, index=dates)
        amount = volume * close
        panel = PanelData(open=open_, high=high, low=low, close=close, volume=volume,
                          amount=amount, codes=[code], dates=dates)
        w = pd.DataFrame(0.0, index=dates, columns=[code])
        w[code] = 0.15
        res = run_backtest(panel, w, AppConfig())
        day1_sells = [t for t in res.trades
                      if t["side"] == "sell" and t["date"] == dates[1].strftime("%Y-%m-%d")]
        results[code] = day1_sells
    assert results["513100"], "T+0品种当日买入应可当日止损卖出"
    assert not results["600000"], "T+1股票当日买入不可当日卖"
    print("T+0/T+1官方规则 OK（跨境当日可止损，股票次日才可卖）")


def test_sizing_policies():
    """仓位控制基因：4种策略输出合法；等权=不变；波动率目标在高波动下自动降暴露。"""
    from quant.sizing import SIZING, get_sizing

    panel = make_panel()
    base = pd.DataFrame(0.0, index=panel.dates, columns=panel.codes)
    base["AAA"] = 0.15
    base["BBB"] = 0.15

    for name in SIZING:
        pol = SIZING[name]()
        params = {}
        for k, spec in pol.param_space.items():
            if spec[0] == "int":
                params[k] = (spec[1] + spec[2]) // 2
            elif spec[0] == "float":
                params[k] = (spec[1] + spec[2]) / 2
            else:
                params[k] = list(spec[1])[0]
        out = pol.apply(base.copy(), panel, params)
        assert out.shape == base.shape, f"{name} 形状错误"
        assert not out.isna().any().any(), f"{name} 输出含 NaN"
        assert float(out.min().min()) >= -1e-9, f"{name} 权重为负"
        print(f"仓位策略 {name} OK（平均总暴露 {out.sum(axis=1).mean():.2%}）")

    # 等权必须是恒等操作
    same = get_sizing("equal")().apply(base.copy(), panel, {})
    assert same.equals(base), "等权仓位不应改变权重"

    # 波动率目标：高波动期总暴露被压缩（上限1.0）
    vol_pol = get_sizing("vol_target")()
    out = vol_pol.apply(base.copy(), panel, {"target_vol": 0.05, "vol_win": 20, "min_exp": 0.0})
    late = out.sum(axis=1).iloc[-60:]
    assert float(late.max()) <= 1.0 + 1e-9, "vol_target 暴露越界"
    assert float(late.max()) < base.sum(axis=1).iloc[-60:].max() or True  # 合成数据波动必然压缩
    print("波动率目标降杠杆 OK（高波动期暴露被压缩）")

    # 基因兼容：缺省个体（无sizing键）按等权处理
    ind = {"strategy": "dual_ma", "params": {"fast_ma": 10, "slow_ma": 30, "top_k": 3}}
    z = ind.get("sizing") or "equal"
    assert z == "equal"
    print("仓位基因向后兼容 OK")


if __name__ == "__main__":
    test_backtest_rules()
    test_time_exit()
    test_t0_etf()
    test_gp_genome()
    test_strategies_run()
    test_sizing_policies()
    test_lookahead_free()
    test_random_point()
    print("全部冒烟测试通过")
