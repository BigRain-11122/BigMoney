# 六个起点里有一个是复印的：那张逐季路径表读的是什么

上游 `results/etf_book_cadence_regime_split.json` 已经把「节奏差是起跑日的属性还是行情段的属性」回答成 **REGIME_DOMINATES | BOTH_CHANNELS_READ**。它留下的逐季表在 2025H2 从 ~1.5 pp 跳到 5.21 / 10.28 pp，上一轮把问题写成「把每格的 bar 数印在 spread 旁边」。本轮实读：bar 数没问题（季度切片对每本书都是同一批 bar），问题是**格本身重复**，以及**四分位极差是秩间隙统计量**。

实物：`scripts/etf_book_cadence_cell_independence.py`（selftest 13/13）+ `results/etf_book_cadence_cell_independence.json` + 本文件。

## 一、复印的那一格

| 季度 | 重复的起点对 | 印出的 Δ（pp） | 两条腿收益最大差 |
|---|---|---|---|
| 2024Q2 | 2022-09-01 = 2024-03-01 | -0.328616 | 0.0e+00 |
| 2024Q3 | 2024-03-01 = 2022-09-01 | 5.750432 | 3.4e-14 |
| 2024Q4 | 2022-09-01 = 2024-03-01 | -4.867754 | 5.5e-14 |
| 2025Q1 | 2022-09-01 = 2024-03-01 | -2.520448 | 4.4e-14 |
| 2025Q2 | 2022-09-01 = 2024-03-01 | 0.930719 | 0.0e+00 |
| 2025Q3 | 2022-09-01 = 2024-03-01 | -0.169865 | 0.0e+00 |
| 2025Q4 | 2022-09-01 = 2024-03-01 | -7.999998 | 5.5e-14 |

这不是巧合：同一对起点在 8bp 与 1bp 两个成本档、在 2024Q2 起的每一个季度都给出同一个 Δ（最大差 1.5e-13），两条腿的收益也一致到同样量级 —— 从 2024Q2 起它们是**同一本书**。上游把六本当六个独立读数，实际第五个起就是五个。

## 二、为什么一格的复印能把数翻倍

| 季度 | 印出的 spread | 去重后 | 去掉最具影响一格 | 该格的 Δ | 印出/去重 mspd |
|---|---|---|---|---|---|
| 2023Q2 | 1.02 | 1.02 | — | — | 1.37 / 1.37 |
| 2023Q3 | 1.87 | 1.87 | — | — | 3.45 / 3.45 |
| 2023Q4 | 2.52 | 2.52 | 1.19 | 4.78 (2023-09-01) | 6.49 / 6.49 |
| 2024Q1 | 1.59 | 1.59 | 1.32 | 2.33 (2022-03-01) | 2.31 / 2.31 |
| 2024Q2 | 1.33 | 1.39 | 1.16 | 1.06 (2022-03-01) | 3.88 / 4.51 |
| 2024Q3 | 3.30 | 4.08 | 0.97 | 1.67 (2023-03-01) | 4.82 / 5.54 |
| 2024Q4 | 1.73 | 1.97 | 1.00 | -2.90 (2021-09-01) | 6.15 / 7.22 |
| 2025Q1 | 1.50 | 2.00 | 0.74 | -3.78 (2022-03-01) | 3.46 / 4.08 |
| 2025Q2 | 1.55 | 2.06 | 0.29 | 2.70 (2021-09-01) | 1.48 / 1.69 |
| 2025Q3 | 5.21 | 6.74 | 0.65 | 11.71 (2022-03-01) | 5.54 / 6.33 |
| 2025Q4 | 10.28 | 2.75 | 2.75 | -8.00 (2022-09-01) | 7.46 / 6.21 |

n=6 时四分位位置落在 1.25 与 3.75，也就是第 1-2 名与第 3-4 名的间隙里。2025Q4 的排序是 [-8.00, -8.00, 2.84, 3.20, 5.59, 6.16]：把两个 -8.00 去掉一个，q1 就从 -5.29 跳到 2.84，spread 从 10.28 掉到 2.75 —— 市场没变，是插值跨过了一个 10.8 pp 的间隙。2025Q3 的 5.21 则是另一回事：该格去掉后只剩 0.65 pp。

复印不一定把数做大 —— 它把这格拉到哪个秩就往哪边推。2024Q3（3.30→4.08）、2024Q4（1.73→1.97）、2025Q1（1.50→2.00）、2025Q2（1.55→2.06）、2025Q3（5.21→6.74）都是去重后**变大**，只有 2025Q4 变小（10.28→2.75）。所以正确的读法不是「路径风险被高估」，而是「这条序列读的是六格里的秩间隙，不是那条路径的离散度」。

注：去掉一格需要 n≥5，所以 2023Q2/2023Q3（n=4）没有这一列，印 —，不是 0。

## 三、结论没有被推翻，被推翻的是那张表的读法

| 通道 | 印出（中位 spread） | 去重后 |
|---|---|---|
| 路径通道（同一季度换起跑日） | 1.73 pp | 2.00 pp |
| 行情段通道（同一本书换季度） | 4.45 pp | 5.13 pp |

**2025Q4:COPY_AND_ONE_CELL | 2025Q3:ONE_CELL_CARRIES_IT | WIDENING_IS_NOT_STRUCTURAL**。上游的 REGIME_DOMINATES 在去重后仍然成立（比例反而变大），但逐季 spread 不能读成「路径风险在 2025H2 升高」—— 它读的是六格里的秩间隙。

## 四、这个面不做什么

- this face re-reads one published table; it does not re-open the upstream question (start date vs market segment), and it does not touch the production ticket
- a collapsed copy is only evidence that two books hold the same portfolio from that quarter on; this face does not prove WHY they converged, it proves they are the same book to 1e-13 in both leg returns and both cost variants
- the IQR is kept (not replaced) so the printed table stays comparable; mspd is printed beside it because the IQR of 5-6 points is a rank-gap statistic and mspd is not
- MOSt influential cell is chosen by the smallest leave-one-out spread, i.e. it answers 'which single cell is carrying this number', not 'which cell is wrong'

## 五、下一步（需竞争窗关闭才动共享面）

1. 上游 `etf_book_cadence_regime_split.py` 的 `channels()` 应在建网格时先折叠 1e-9 内重复的格，并把 `n_independent` 印在逐季表里 —— 这是共享代码面改动，本轮同树另有宿主在动，未动。
2. 该面接 S6 链 + 两条冒烟腿（一：去重后路径中位仍低于行情段中位；二：任何季度出现复核仍被当作独立格时腿红），同样等竞争窗。

