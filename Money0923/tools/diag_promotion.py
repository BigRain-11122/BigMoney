#!/usr/bin/env python
"""晋升管道只读诊断：候选宇宙 vs 5% 样本外回撤硬闸。

背景：2026-09-20 实测——晋升配额 12/12 全被 etf_trend 满仓型候选烧掉
（样本外回撤 -19.8%~-20.6% 全撞死在 5% 闸上），种群 48 个体 100% 单化为
etf_trend，恢复机制（移民）依赖的冠军体检因无团队被跳过 → 死锁。

本脚本回答一个问题：把联赛认证者、经典种子、种群低仓变体全部放到部署
holdout 窗口上重评，到底有谁能同时过 5% 回撤闸 + 0.40 绝对分门槛？

只读保证：不写 state、不烧晋升配额、不刷新数据；与 Evolver.holdout_eval
完全同口径（策略→sizing→全规则回测→复合分）。
"""
from __future__ import annotations

import os
import sys
import json
import multiprocessing as mp
from concurrent.futures import ProcessPoolExecutor, as_completed

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROOT)

_CTX: dict = {}


def _worker_init(panel, d0, d1, cfg):
    _CTX.update(panel=panel, d0=d0, d1=d1, cfg=cfg)


def _holdout_one(ind: dict):
    from quant import strategies as strat_lib
    from quant.sizing import get_sizing
    from quant.backtest import run_backtest
    from quant.evolve import composite_score
    try:
        strat = strat_lib.get_strategy(ind["strategy"])()
        w = strat.target_weights(_CTX["panel"], ind["params"])
        sizing = get_sizing(ind.get("sizing") or "equal")()
        w = sizing.apply(w, _CTX["panel"], ind.get("sizing_params") or {})
        sub = _CTX["panel"].window(_CTX["d0"], _CTX["d1"])
        res = run_backtest(sub, w, _CTX["cfg"])
        return ind, composite_score(res.metrics, _CTX["cfg"]), res.metrics, None
    except Exception as ex:  # noqa: BLE001
        return ind, 0.0, {}, repr(ex)[:120]


def main() -> None:
    from quant.config import load_config
    from quant.state import load_state
    from quant import data as qdata
    from quant.evolve import Evolver, GA_SEEDS

    cfg = load_config()
    state = load_state()
    _, panel = qdata.full_panel(cfg)
    ev = Evolver(cfg, panel, state, persist=False)  # 只拿 holdout_dates，不落盘
    d0, d1 = ev.holdout_dates[0], ev.holdout_dates[-1]
    print(f"holdout 窗口: {d0.date()} ~ {d1.date()}（{len(ev.holdout_dates)} 日）")
    print(f"{cfg.meta.team_member_max_dd:.0%} 回撤闸 + floor={cfg.meta.team_member_floor} | 团队规模 {cfg.meta.team_size}")

    # ---- 组装候选宇宙 ----
    cands: list[dict] = []
    seen: set[tuple] = set()

    def add(ind: dict, src: str):
        key = (ind.get("strategy"), ind.get("sizing") or "equal",
               json.dumps(ind.get("params") or {}, sort_keys=True, default=str))
        if key in seen:
            return
        seen.add(key)
        cands.append({**ind, "_src": src})

    # 1) 联赛认证者：每族×sizing 组合采样最多 2 个（认证=随机窗稳定前10，真实战绩群体）
    quals = state.get("arena", {}).get("qualified") or []
    buckets: dict[tuple, list] = {}
    for q in quals:
        buckets.setdefault((q["strategy"], q.get("sizing") or "equal"), []).append(q)
    for k, lst in sorted(buckets.items()):
        for q in lst[:2]:
            add({"strategy": q["strategy"], "params": q["params"],
                 "sizing": q.get("sizing") or "equal",
                 "sizing_params": q.get("sizing_params") or {}}, "qualified")

    # 2) 经典种子（GA 起点）
    for s in GA_SEEDS:
        add(s, "seed")

    # 3) 种群低仓变体：vol_target 按 target_vol 从小到大取 8 + ma_risk 全部（种群已单化为 etf_trend）
    pop = state.get("evolution", {}).get("population") or []
    vt = [p for p in pop if (p.get("sizing") or "equal") == "vol_target"]
    vt.sort(key=lambda p: (p.get("sizing_params") or {}).get("target_vol", 99))
    for p in vt[:8]:
        add(p, "pop-lowvol")
    for p in pop:
        if (p.get("sizing") or "equal") == "ma_risk":
            add(p, "pop-ma_risk")

    print(f"候选宇宙: {len(cands)} 个（qualified 采样 {sum(1 for c in cands if c['_src'] == 'qualified')}"
          f" / 种子 {sum(1 for c in cands if c['_src'] == 'seed')}"
          f" / 种群 {sum(1 for c in cands if c['_src'].startswith('pop'))}）\n")

    # ---- 并行 holdout（同 maybe_update_team 口径，但只读不烧配额）----
    rows = []
    with ProcessPoolExecutor(max_workers=2, initializer=_worker_init,
                             initargs=(panel, d0, d1, cfg)) as pool:
        futs = {pool.submit(_holdout_one, c): c for c in cands}
        done = 0
        for fut in as_completed(futs):
            ind, score, metrics, err = fut.result()
            done += 1
            if err:
                print(f"  [{done}/{len(cands)}] {ind['strategy']}/{ind.get('sizing')} 出错: {err}")
                continue
            rows.append({"strategy": ind["strategy"], "sizing": ind.get("sizing") or "equal",
                         "src": ind["_src"], "score": score,
                         "mdd": float(metrics.get("max_dd", 0.0) or 0.0),
                         "cagr": float(metrics.get("cagr", 0.0) or 0.0)})
            if done % 10 == 0:
                print(f"  ... {done}/{len(cands)}")

    # ---- 报表：按回撤升序（最接近过闸的排前面）----
    rows.sort(key=lambda r: r["mdd"], reverse=True)
    gate = cfg.meta.team_member_max_dd
    floor = cfg.meta.team_member_floor
    print(f"{'策略':<18}{'仓位':<11}{'来源':<11}{'分数':>7}{'回撤%':>8}{'CAGR%':>8}  闸")
    for r in rows:
        dd_ok = r["mdd"] >= -gate if gate > 0 else True
        fl_ok = r["score"] >= floor
        mark = ("PASS" if (dd_ok and fl_ok) else
                ("dd_ok" if dd_ok and not fl_ok else
                 ("floor_ok" if fl_ok and not dd_ok else "REJECT")))
        print(f"{r['strategy']:<18}{r['sizing']:<11}{r['src']:<11}"
              f"{r['score']:>7.3f}{r['mdd'] * 100:>8.1f}{r['cagr'] * 100:>8.1f}  {mark}")

    n_pass = sum(1 for r in rows
                 if (r["mdd"] >= -gate if gate > 0 else True) and r["score"] >= floor)
    n_dd = sum(1 for r in rows if r["mdd"] >= -gate) if gate > 0 else len(rows)
    n_fl = sum(1 for r in rows if r["score"] >= floor)
    print(f"\n汇总: 双过(可入队) {n_pass}/{len(rows)} | 仅过{gate:.0%}闸 {n_dd} | 仅过floor {n_fl}")
    if rows:
        best = rows[0]
        print(f"最小回撤: {best['strategy']}/{best['sizing']} {best['mdd'] * 100:.1f}%（{best['src']}）")


if __name__ == "__main__":
    mp.freeze_support()
    main()
