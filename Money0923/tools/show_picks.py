#!/usr/bin/env python
"""只读：给定 策略/仓位基因，从联赛认证者中选样本外最优个体，列出其当前目标持仓。

用法: python tools/show_picks.py [strategy] [sizing]   （默认 low_vol ma_risk）
不写 state、不烧配额；目标权重为策略口径，实盘下单前仍经风控资产上限与曝光缩放。
"""
from __future__ import annotations

import json
import os
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROOT)


def main() -> None:
    from quant.config import load_config
    from quant.state import load_state
    from quant import data as qdata
    from quant import strategies as strat_lib
    from quant.sizing import get_sizing
    from quant.backtest import run_backtest
    from quant.evolve import Evolver, composite_score

    strategy = sys.argv[1] if len(sys.argv) > 1 else "low_vol"
    sizing = sys.argv[2] if len(sys.argv) > 2 else "ma_risk"

    cfg = load_config()
    state = load_state()
    _, panel = qdata.full_panel(cfg)
    ev = Evolver(cfg, panel, state, persist=False)  # 只取 holdout_dates
    d0, d1 = ev.holdout_dates[0], ev.holdout_dates[-1]

    quals = [q for q in (state.get("arena", {}).get("qualified") or [])
             if q.get("strategy") == strategy and (q.get("sizing") or "equal") == sizing]
    if not quals:
        print(f"无 {strategy}/{sizing} 认证者")
        return

    best, best_score, best_w = None, -1.0, None
    sub = panel.window(d0, d1)
    for q in quals:
        try:
            strat = strat_lib.get_strategy(q["strategy"])()
            w = strat.target_weights(panel, q["params"])
            sz = get_sizing(q.get("sizing") or "equal")()
            w = sz.apply(w, panel, q.get("sizing_params") or {})
            res = run_backtest(sub, w.astype(float), cfg)
            sc = composite_score(res.metrics, cfg)
            if sc > best_score:
                best, best_score, best_w = q, sc, w
        except Exception as ex:  # noqa: BLE001
            print(f"评估失败({q.get('strategy')}): {repr(ex)[:100]}")

    if best is None:
        print("全部评估失败")
        return
    w_last = best_w.iloc[-1]
    picks = w_last[w_last > 0.001].sort_values(ascending=False)
    print(f"认证者 {len(quals)} 个 | 样本外最优分 {best_score:.3f}"
          f"（holdout {d0.date()}~{d1.date()}）")
    print(f"参数: {json.dumps(best.get('params') or {}, ensure_ascii=False)}"
          f" | 仓位: {best.get('sizing')}"
          f"/{json.dumps(best.get('sizing_params') or {}, ensure_ascii=False)}")
    print(f"当前目标持仓 {len(picks)} 只（目标权重；下单前仍经资产上限/曝光缩放/负面清单终检）:")
    for code, wgt in picks.items():
        print(f"  {code}  {wgt:.1%}")


if __name__ == "__main__":
    main()
