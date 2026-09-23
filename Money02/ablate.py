"""Ablation: per-family isolated full-period backtests of the live champion
genome (2017-07..2026-09, all costs), vs the champion's blended weights."""
import json

import numpy as np

import config as C
import data as D
import strategies as S
import regime as RG
import backtest as BT
import evolve as EV

live = json.loads((C.RESULTS_DIR / "live_genome.json").read_text(encoding="utf-8"))
gp = EV.decode(live["genome"])
cache = D.load_cache(mmap=False)
T = int(len(cache["dates"]))
reg = RG.compute(cache["bench_sse"], cache["breadth"])
i0 = 610  # first OOS fold start, 2017-07
i1 = T

names = S.FAMILIES
rows = []
for f in list(names) + ["CHAMPION"]:
    gp2 = {k: (v.copy() if isinstance(v, dict) else
               (v.copy() if hasattr(v, "copy") else v)) for k, v in gp.items()}
    if f == "CHAMPION":
        w = gp["w"]
    else:
        w = np.zeros_like(gp["w"])
        w[:, names.index(f)] = 1.0
    gp2["w"] = w
    fams = S.family_signals(D.window(cache, i0 - 1, i1 - 1), gp2["params"])
    res = BT.simulate(D.window(cache, i0, i1), fams, gp2, reg, i0)
    m = res["metrics"]
    rows.append((f, m))

print(f"现役冠军基因组消融对比（区间 2017-07 ~ 2026-09 共 {i1 - i0} 交易日，"
      f"100万本金，含全部成本）")
print(f"{'策略':　<14}{'总收益':>9}{'年化':>8}{'夏普':>7}{'最大回撤':>9}"
      f"{'胜率':>7}{'交易数':>6}{'均持日':>7}")
for f, m in rows:
    cn = {"CHAMPION": "★冠军混权组合"}.get(f, f)
    print(f"{cn:　<14}{m['total']*100:8.1f}%{m['cagr']*100:7.1f}%"
          f"{m['sharpe']:7.2f}{m['maxdd']*100:8.1f}%{m['win_rate']*100:6.1f}%"
          f"{m['n_trades']:6d}{m['avg_hold']:7.1f}")

print("\n冠军的市场状态权重矩阵（4状态×8家族）:")
hdr = "状态\\策略"
for f in names:
    hdr += f" {f[:8]:>9}"
print(hdr)
for i, rname in enumerate(RG.NAMES):
    line = f"{rname:>10}"
    for j in range(len(names)):
        line += f"{gp['w'][i, j]*100:8.0f}%"
    print(line)
print("各状态仓位暴露:", {RG.NAMES[i]: f"{x*100:.0f}%" for i, x in enumerate(gp["exposure"])})
print("风控: K(最大持仓数)=%d 止损=%.1f%% 跟踪止盈=%.1f%% 最长持有=%d日"
      % (gp["K"], gp["stop"]*100, gp["trail"]*100, gp["hold"]))
print("家族参数:", json.dumps(gp["params"], ensure_ascii=False))
