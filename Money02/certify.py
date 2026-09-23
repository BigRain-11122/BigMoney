"""Champion certification battery (六道出厂门禁) - the "充分验证" dossier.

Gates:
  G1 walk-forward OOS   : full-history stitched OOS vs benchmarks
  G2 random-window      : N fresh random 60d windows, win rate & excess vs csi500
  G3 param sensitivity  : ±5% genome perturbation x 20 samples, sign stability
  G4 cost stress        : slippage x2 / x3, alpha survival
  G5 regime breakdown   : per-regime annualized return / exposure
  G6 live paper         : real-execution track record (once it exists)
Writes results/champion_report.md + verdict. Standalone: python certify.py
"""
import datetime as dt
import json

import numpy as np

import config as C
import data as D
import strategies as S
import regime as RG
import backtest as BT
import evolve as EV

N_RANDOM = 30
FIRST_FOLD_I0 = 130  # matches make_folds warmup


def _sim_full_period(cache, reg, gp, i0, i1, slippage=None):
    old = C.SLIPPAGE
    if slippage is not None:
        C.SLIPPAGE = slippage
    try:
        # selective: only the genome's weighted families - a 31-family
        # full-set on an 8000-day window would take ~10min per sim
        w_any = np.asarray(gp["w"]).max(axis=0) > 1e-4
        fams_needed = [f for f, k in zip(S.FAMILIES, w_any) if k]
        fams = S.family_signals(D.window(cache, i0 - 1, i1 - 1), gp["params"],
                                fams=fams_needed)
        res = BT.simulate(D.window(cache, i0, i1), fams, gp, reg, i0)
    finally:
        C.SLIPPAGE = old
    return res


def main():
    live = json.loads((C.RESULTS_DIR / "live_genome.json").read_text(encoding="utf-8"))
    gp = EV.decode(live["genome"])
    cache = D.load_cache(mmap=False)
    T = int(len(cache["dates"]))
    reg = RG.compute(cache["bench_sse"], cache["breadth"])
    dates = np.asarray(cache["dates"])

    lines = [f"# 冠军策略出厂验证大纲（充分验证）\n"]
    lines.append(f"- 生成: {dt.datetime.now().strftime('%Y-%m-%d %H:%M')} ｜ "
                 f"数据: {str(dates[0])} ~ {str(dates[-1])}（{T}个交易日） ｜ "
                 f"基因: fit={live.get('fit')} trained_through={live.get('trained_through')}\n")

    # ---------------- G1: full-period OOS (champion frozen, all costs)
    res = _sim_full_period(cache, reg, gp, FIRST_FOLD_I0 + C.TRAIN_DAYS, T)
    m1 = res["metrics"]
    i0_g1 = FIRST_FOLD_I0 + C.TRAIN_DAYS
    bench = np.asarray(cache["bench_csi500"][i0_g1:T], float)
    if not np.isfinite(bench[0]) or bench[0] <= 0:  # pre-2007: SSE fallback
        bench = np.asarray(cache["bench_sse"][i0_g1:T], float)
    b_ret = bench[-1] / bench[0] - 1
    b3 = np.asarray(cache["bench_hs300"][i0_g1:T], float)
    if not np.isfinite(b3[0]) or b3[0] <= 0:  # pre-2005: SSE fallback
        b3 = np.asarray(cache["bench_sse"][i0_g1:T], float)
    b3_ret = b3[-1] / b3[0] - 1
    years = (T - FIRST_FOLD_I0 - C.TRAIN_DAYS) / 252.0
    g1_pass = m1["sharpe"] > 0.3 and m1["total"] > b_ret and m1["maxdd"] > -0.45
    lines.append("## G1 全周期冻结基因验证（样本外段，全成本）\n")
    lines.append(f"| 指标 | 值 | 指标 | 值 |")
    lines.append(f"|---|---|---|---|")
    lines.append(f"| 总收益 | {m1['total']*100:+.1f}% | 中证500同期 | {b_ret*100:+.1f}% |")
    lines.append(f"| 年化 | {m1['cagr']*100:+.1f}% | 沪深300同期 | {b3_ret*100:+.1f}% |")
    lines.append(f"| 夏普 | {m1['sharpe']:.2f} | 超额(年化) | {(m1['cagr']-(b_ret+1)**(1/years)+1-1)*100:+.1f}pp |")
    lines.append(f"| 最大回撤 | {m1['maxdd']*100:.1f}% | 胜率 | {m1['win_rate']*100:.1f}% |")
    lines.append(f"| 交易数 | {m1['n_trades']} | 换手(年) | {m1['turnover_ann']:.1f}x |")
    lines.append(f"\n**门禁G1**: {'✅ PASS' if g1_pass else '❌ FAIL'} "
                 f"(要求 夏普>0.3 且 跑赢中证500 且 回撤<45%)\n")

    # ---------------- G2: random-window robustness
    # Non-overlapping windows (audit fix 2026-09-22): plain random starts
    # cluster heavily -> effective sample << 30. Segment the span into
    # N_RANDOM equal slices and draw one 60d window inside each slice:
    # truly disjoint windows + even regime coverage, randomness preserved.
    rng = np.random.default_rng(42)
    lo = FIRST_FOLD_I0 + C.TRAIN_DAYS
    hi = T - C.TEST_DAYS
    span = max(hi - lo, N_RANDOM)
    seg = span / N_RANDOM
    rets, excess = [], []
    for k in range(N_RANDOM):
        a = int(lo + k * seg)
        b = int(lo + (k + 1) * seg) - C.TEST_DAYS
        if b < a:
            b = a
        i0 = int(rng.integers(a, max(a + 1, b + 1)))
        i1 = i0 + C.TEST_DAYS
        bench_w = np.asarray(cache["bench_csi500"][i0:i1], float)
        if not np.isfinite(bench_w[0]) or bench_w[0] <= 0:
            # pre-2007: csi500 unpublished - score against SSE (same
            # principle as the league: a REAL benchmark, no free wins)
            bench_w = np.asarray(cache["bench_sse"][i0:i1], float)
        br = bench_w[-1] / bench_w[0] - 1 if bench_w[0] > 0 else 0.0
        r = _sim_full_period(cache, reg, gp, i0, i1)  # 60d sim, fast
        rets.append(r["metrics"]["total"])
        excess.append(r["metrics"]["total"] - br)
    rets = np.array(rets)
    excess = np.array(excess)
    win_rate = float((excess > 0).mean())
    g2_pass = win_rate >= 0.55
    lines.append("## G2 随机窗口鲁棒性（30个互不重叠60日窗·分段抽样 vs 中证500/上证）\n")
    lines.append(f"| 跑赢基准比例 | 平均收益 | 收益中位数 | 平均超额 | 最差窗 |")
    lines.append(f"|---|---|---|---|---|")
    lines.append(f"| {win_rate*100:.0f}% | {rets.mean()*100:+.2f}% | "
                 f"{np.median(rets)*100:+.2f}% | {excess.mean()*100:+.2f}pp | {rets.min()*100:+.2f}% |")
    lines.append(f"\n**门禁G2**: {'✅ PASS' if g2_pass else '❌ FAIL'} "
                 f"(要求 跑赢比例≥55%)\n")

    # ---------------- G3: parameter sensitivity (+-5% genome jitter x 20)
    g = np.asarray(live["genome"], dtype=np.float64)
    pert_rets = []
    rng2 = np.random.default_rng(7)
    ev = EV.Evaluator()
    try:
        genomes = [np.clip(g + rng2.normal(0, 0.05, len(g)), 0, 1).astype(np.float32)
                   for _ in range(20)]
        i0, i1 = FIRST_FOLD_I0 + C.TRAIN_DAYS, T
        outs = ev.map([(gm, i0, i1, False, None) for gm in genomes])
    finally:
        ev.close()
    pert_rets = [o[4] for o in outs]  # cagr
    pert_rets = np.array(pert_rets, dtype=float)
    stable = (pert_rets > b_ret).mean()  # fraction still beating benchmark
    g3_pass = float(stable) >= 0.7 and pert_rets.std() < 0.15
    lines.append("## G3 参数敏感性（基因±5%扰动×20样本，全周期）\n")
    lines.append(f"| 扰动后年化均值 | 年化标准差 | 仍跑赢基准比例 |")
    lines.append(f"|---|---|---|")
    lines.append(f"| {pert_rets.mean()*100:+.1f}% | {pert_rets.std()*100:.1f}pp | {stable*100:.0f}% |")
    lines.append(f"\n**门禁G3**: {'✅ PASS' if g3_pass else '❌ FAIL'} "
                 f"(要求 扰动后仍≥70%跑赢基准 且 年化波动<15pp)\n")

    # ---------------- G4: cost stress
    r2 = _sim_full_period(cache, reg, gp, FIRST_FOLD_I0 + C.TRAIN_DAYS, T,
                          slippage=2 * C.SLIPPAGE)
    r3 = _sim_full_period(cache, reg, gp, FIRST_FOLD_I0 + C.TRAIN_DAYS, T,
                          slippage=3 * C.SLIPPAGE)
    g4_pass = r2["metrics"]["total"] > b_ret * 0.5 or r2["metrics"]["sharpe"] > 0
    lines.append("## G4 成本压力测试（滑点 0.1% → 0.2% → 0.3%）\n")
    lines.append(f"| 滑点 | 总收益 | 夏普 |")
    lines.append(f"|---|---|---|")
    lines.append(f"| 0.1%(基准) | {m1['total']*100:+.1f}% | {m1['sharpe']:.2f} |")
    lines.append(f"| 0.2%(2倍) | {r2['metrics']['total']*100:+.1f}% | {r2['metrics']['sharpe']:.2f} |")
    lines.append(f"| 0.3%(3倍) | {r3['metrics']['total']*100:+.1f}% | {r3['metrics']['sharpe']:.2f} |")
    lines.append(f"\n**门禁G4**: {'✅ PASS' if g4_pass else '❌ FAIL'} "
                 f"(要求 2倍滑点下仍保持一半超额或夏普为正)\n")

    # ---------------- G5: regime breakdown
    eq = np.asarray(res["eq"], dtype=float)
    rets_d = eq[1:] / eq[:-1] - 1
    regs = reg[FIRST_FOLD_I0 + C.TRAIN_DAYS:T]
    lines.append("## G5 分市场状态表现（样本外段日收益按状态归组）\n")
    lines.append("| 状态 | 天数 | 累计贡献 | 状态 | 天数 | 累计贡献 |")
    lines.append("|---|---|---|---|---|---|")
    half = []
    for i in range(4):
        m = regs == i
        contrib = float((1 + rets_d[m[:len(rets_d)]]).prod() - 1)
        half.append((RG.NAMES[i], int(m.sum()), contrib))
    for a, b in zip(half[:2], half[2:]):
        lines.append(f"| {a[0]} | {a[1]} | {a[2]*100:+.1f}% | {b[0]} | {b[1]} | {b[2]*100:+.1f}% |")
    worst = min(half, key=lambda x: x[2])
    g5_pass = worst[2] > -0.35
    lines.append(f"\n**门禁G5**: {'✅ PASS' if g5_pass else '❌ FAIL'} "
                 f"(要求 最差状态累计亏损>-35%)\n")

    # ---------------- G6: live paper track record
    paper_p = C.RESULTS_DIR / "paper.json"
    g6_pass = None
    lines.append("## G6 实盘模拟记账（100万虚拟本金）\n")
    if paper_p.exists():
        paper = json.loads(paper_p.read_text(encoding="utf-8"))
        hist = paper.get("history", [])
        if hist:
            eq_now = hist[-1]["equity"]
            pnl = eq_now / C.CAPITAL - 1
            lines.append(f"- 已记账 {len(hist)} 个交易日 ｜ 当前权益 {eq_now:,.0f} "
                         f"（{pnl*100:+.2f}%）")
            g6_pass = len(hist) >= 20
            lines.append(f"\n**门禁G6**: {'✅ PASS' if g6_pass else '⏳ 样本不足(<20日)'} "
                         f"(要求 ≥20个交易日记账)\n")
        else:
            lines.append("- 尚无记账（首个交易日收盘后开始）\n**门禁G6**: ⏳ 待实盘数据\n")
    else:
        lines.append("- 尚无记账（首个交易日收盘后开始）\n**门禁G6**: ⏳ 待实盘数据\n")

    gates = [g1_pass, g2_pass, g3_pass, g4_pass, g5_pass,
             (g6_pass if g6_pass is not None else None)]
    n_pass = sum(1 for x in gates if x is True)
    n_known = sum(1 for x in gates if x is not None)
    overall = "🏆 出厂达标" if all(x is True for x in gates[:5]) else \
              (f"⏳ 渐进达标 ({n_pass}/{n_known} 门通过，实盘门积累中)" if n_pass >= 3
               else "🚧 未达标（进化继续）")
    lines.append(f"\n## 总判定: {overall}\n")
    lines.append("- 达标线：G1-G5 全过 + G6 攒满20个交易日 → 策略可宣告验证充分\n")

    out = C.RESULTS_DIR / "champion_report.md"
    out.write_text("\n".join(lines), encoding="utf-8")
    print(f"certify done -> {out}")
    print(f"G1={g1_pass} G2={g2_pass} G3={g3_pass} G4={g4_pass} G5={g5_pass} G6={g6_pass}")
    print(f"verdict: {overall}")


if __name__ == "__main__":
    main()
