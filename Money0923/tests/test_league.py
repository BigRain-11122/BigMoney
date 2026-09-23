"""联赛机制冒烟测试：合成数据验证随机窗口开局、多样性前10、稳定前10认证。

运行: python tests/test_league.py（不触碰真实 state.json）
"""
import copy
import os
import sys

import numpy as np
import pandas as pd

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from quant import arena  # noqa: E402
from quant.backtest import run_backtest  # noqa: E402
from quant.config import AppConfig  # noqa: E402
from quant.data import PanelData  # noqa: E402


def make_panel(n: int = 420) -> PanelData:
    dates = pd.date_range("2024-01-01", periods=n, freq="B")
    rng = np.random.default_rng(11)
    drifts = {"AAA": 0.0015, "BBB": -0.0008, "CCC": 0.0004, "DDD": 0.0010,
              "EEE": -0.0012, "FFF": 0.0}
    close = pd.DataFrame(index=dates)
    for k, d in drifts.items():
        noise = rng.normal(0, 0.015, n)
        close[k] = 100.0 * np.cumprod(1.0 + d + noise) / (1.0 + noise[0])
    op = close.shift(1).fillna(100.0)
    volume = pd.DataFrame({k: np.full(n, 5e8) for k in close.columns}, index=dates)
    return PanelData(open=op, high=close * 1.008, low=close * 0.992, close=close,
                     volume=volume, amount=volume * close, codes=list(close.columns),
                     dates=dates)


def fresh_state(cfg) -> dict:
    """构造与真实 state 结构一致的临时状态（测试不落盘）。"""
    return {"arena": {}, "evolution": {"population": []}, "team": [], "champion": None}


def main() -> None:
    cfg = AppConfig()
    cfg.arena.size = 16
    cfg.arena.round_days = 120       # 合成数据缩短考核窗（机制同构）
    cfg.arena.qualify_streak = 2
    cfg.arena.qualify_floor = 0.0    # 合成行情宽松门槛，验证认证路径可触发
    cfg.arena.max_family_top = 3
    cfg.arena.max_sel_corr = 0.85
    cfg.evolve.workers = 0           # 测试串行
    state = fresh_state(cfg)
    panel = make_panel()

    players = arena.spawn_players(cfg, state, persist=False)
    assert len(players) == cfg.arena.size, "派员人数不符"
    # —— 2026-09-20 赛制：每队100万 + 5风格谱系各占1/5席位 ——
    assert all(p["capital"] == 1_000_000.0 for p in players), "每队资金必须为100万"
    style_counts: dict[str, int] = {}
    for p in players:
        style_counts[p["style"]] = style_counts.get(p["style"], 0) + 1
    assert set(style_counts) == set(arena.STYLE_ORDER), f"风格席位不全: {style_counts}"
    assert max(style_counts.values()) - min(style_counts.values()) <= 1, "风格席位应均衡（±1）"
    assert all(p["style"] in arena.TEAM_STYLES for p in players), "存在未定义风格"
    # style_cfg 风控参数覆盖验证（极稳 vs 激进 必须差异极大）
    cs = arena.style_cfg(cfg, "极稳")
    ca = arena.style_cfg(cfg, "激进")
    assert cs.risk.max_position_pct == 0.05 and ca.risk.max_position_pct == 0.40
    assert cs.risk.stop_loss_pct != ca.risk.stop_loss_pct
    assert arena.TEAM_STYLES["极稳"]["scale"] < arena.TEAM_STYLES["激进"]["scale"]
    print(f"风格席位: {style_counts} | 极稳单票{cs.risk.max_position_pct:.0%} vs 激进{ca.risk.max_position_pct:.0%}")

    for i in range(4):
        rec = arena.run_round(cfg, state, panel=panel, persist=False)
        assert rec is not None, f"第{i+1}局无结果"
        top = rec["top10"]
        assert len(top) <= 10, "前10人数越界"
        fams: dict[str, int] = {}
        for t in top:
            fams[t["strategy"]] = fams.get(t["strategy"], 0) + 1
        assert all(v <= cfg.arena.max_family_top for v in fams.values()), f"同族超限: {fams}"
        # 晋级者 streak 与 top10_hist 一致性
        by_id = {p["id"]: p for p in state["arena"]["players"]}
        for p in state["arena"]["players"]:
            hist = p.get("top10_hist") or []
            assert len(hist) == p.get("rounds", 0) or len(hist) == i + 1, "历史长度异常"
        print(f"第{i+1}局 {rec['window']} 均分{rec['mean_score']:.3f} | "
              f"前10: {' '.join(t['strategy'][:8] for t in top)} | "
              f"新认证: {rec['qualified'] or '无'}")

    # 认证机制：连续2局前10应有选手被认证（合成数据漂移行情下大概率存在）
    qualified = state["arena"].get("qualified") or []
    print(f"稳定前10认证: {len(qualified)} 名 "
          + ", ".join(f"{q['id']}({q['strategy']})×{q['streak']}" for q in qualified))
    # 认证者必须真的连续N局在前10（历史自检）
    for q in qualified:
        p = next((x for x in state["arena"]["players"] if x["id"] == q["id"]), None)
        if p:
            tail = (p.get("top10_hist") or [])[-q["streak"]:]
            assert all(v == 1 for v in tail), "认证选手的连续前10历史不成立"

    # 认证基因必须注入 GA 种群
    if qualified:
        keys = {arena._ind_key({"strategy": i["strategy"], "params": i["params"]})
                for i in state["evolution"]["population"]}
        for q in qualified:
            k = arena._ind_key({"strategy": q["strategy"], "params": q["params"]})
            assert k in keys, f"认证选手 {q['id']} 基因未注入GA种群"

    # 换血后风格谱系须在场且不塌缩（Top10保留机制允许赢家风格有超额席位，但5档不能缺位）
    sc: dict[str, int] = {}
    for p in state["arena"]["players"]:
        sc[p.get("style") or "均衡"] = sc.get(p.get("style") or "均衡", 0) + 1
    assert set(sc) == set(arena.STYLE_ORDER), f"换血后风格缺位: {sc}"
    target = cfg.arena.size // len(arena.STYLE_ORDER)
    assert min(sc.values()) >= max(1, target - 2), f"风格席位塌缩: {sc}"
    assert max(sc.values()) <= target + 5, f"单一风格吞噬全场: {sc}"
    print(f"换血后风格席位: {sc}")

    # 多样性相关性检查函数
    a = pd.DataFrame({"X": [1.0, 0.0, 1.0], "Y": [0.0, 1.0, 0.0]})
    b = pd.DataFrame({"X": [1.0, 0.0, 1.0], "Y": [0.0, 1.0, 0.0]})
    c = pd.DataFrame({"X": [0.0, 1.0, 0.0], "Y": [1.0, 0.0, 1.0]})
    assert abs(arena._wcorr(a, b) - 1.0) < 1e-9, "相同权重相关性应为1"
    assert abs(arena._wcorr(a, c) + 1.0) < 1e-9, "相反权重相关性应为-1"
    print("联赛机制冒烟测试通过（随机窗/5风格谱系/多样性/连胜/认证/基因回馈 全链路）")


if __name__ == "__main__":
    main()
