# 国债期货当防守腿（bench cell 4）

evidence cutoff 2026-11-20 | generated 2026-11-22T22:46:09+08:00

**判决 NO_EDGE**

- 债券腿：+4.88%/年 · 夏普 0.644 · 回撤 -13.86% · 样本外 +7.74%
- 现金腿（data/repo_daily/GC001.csv median(last 250 bars)）：+1.38%/年
- 与沪深300日相关：-0.187
- 权益最差两年：{'2018': {'csi300_pct': -25.31, 'bond_pct': 11.16}, '2022': {'csi300_pct': -21.63, 'bond_pct': -1.07}}

判据：{"H1_net_ge_3pct": true, "H2_corr_le_0.25": true, "H3_positive_in_both_bear_years": false, "H4_drop_best_ge_2pct": true, "H5_beats_cash_by_1pp": true}

## 这次没有回答的问题

- 没有做保证金占用与移仓成本的全部口径（只按 1.5bp/边计）。
- 没有把现券/存单与国债期货做合成比较（本地无现券曲线）。
