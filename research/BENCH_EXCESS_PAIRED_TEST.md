# 超额是差，不是和：配对检验 vs 臂自己的 MDE

generated 2026-11-26T23:36:20+08:00 | 面 17 | 臂 59 | 重建复现（±0.05pp）59 条 / 未复现 0 条

只读面：面板 + `results/bench_*.json`，不改判决、不重写任何 bench 面。

## 一句话

臂自己的 MDE 是「臂年化均值」的标准误，而超额是两本书之差的均值——量错了对象。本轮把差自己的标准误算出来（17 面 / 59 臂，59 条重建臂全部对上出版年化、零条失配）：**不是尺子太严，是方向不定**——配对宽度中位是臂 MDE 的 1.38 倍，38 条更宽、21 条更窄。**判决一条没变**：换成任一条候选尺子，GO 都从 4 变 0、没有旧臂被重新打开；而 59 条臂里没有一条能证明跑赢「直接持有同篮子」，另有 3 条**显著跑输**。

| 读数 | 臂数 |
|---|---|
| 两条尺都说过线（BOTH_RULERS_SEE_IT） | 0 |
| 两条尺都说不过（NEITHER_RULER_SEES_IT） | 59 |
| **臂 MDE 说看不见、配对 t 说看得见**（HEURISTIC_HID_A_VISIBLE_EXCESS） | 0 |
| 臂 MDE 说看得见、配对 t 说看不见（HEURISTIC_ADMITTED_WHAT_PAIRED_CANNOT_SEE） | 0 |
| 无法判（UNDECIDABLE） | 0 |

## 旧尺子的误差往哪边偏

臂自己的 MDE 是「臂年化均值」的标准误；配对宽度是「臂 − 同价基准」日差的标准误，两者只在两本书完全同向时才相等。本轮 59 条臂里，配对宽度中位数是臂 MDE 的 **1.38 倍**：**38 条更宽**（臂 MDE 低估了差的不确定性）、21 条更窄。所以拿臂 MDE 当超额的宽度，方向是不确定的——不是「太严」，是「量错了东西」。

## 待决问题：H1 改成超额过 MDE 吗

| 读数 | 数值 |
|---|---|
| 今天打印的 GO 行 | 4 |
| 换成「超额 ≥ 臂 MDE」后仍是 GO | 0 |
| 换成配对 t ≥ 1.96 后仍是 GO | 0 |
| 两条候选尺子下新开闸的旧臂 | 0 / 0 |
| 两条尺子给出同一判决集 | 是 |

在这张 bench 上，两条候选尺子给出完全相同的判决：GO 集两边都被清空，没有一条旧臂被重新打开——所以今天的判决不是尺子造成的。配对数字真正补充的是：臂自己的 MDE 在两边都量错了（中位 1.38 倍，38/59 条更宽），把它当成「差的宽度」来读，读的是一个跟差无关的数。

本轮**没有**改闸：`bench_generic` 是共享面，本轮在写入竞争下行进（r1907），换尺子留给拥有工作树的轮次。

## 配对后显著跑输「直接持有同篮子」的臂

| 面 | 臂 | 超过基准年化 | t | 原判决 |
|---|---|---|---|---|
| census_bond_futures | ma_cross\|{'fast': 20, 'slow': 60}\|long | -2.94 | -2.03 | NO_EDGE |
| pair_bond_curve_60d | pair_bond_curve_60d | -6.77 | -2.67 | NO_EDGE |
| reversal_commodity_5d | reversal_commodity_5d | -8.0 | -2.77 | NO_EDGE |

这三条不是「没找到边」，是**显著把钱做少了**——它们与「什么都不做」的差比噪声大三倍上下（−2.9pp / −6.8pp / −8.0pp/年）。

## 4 条 GO 在配对尺下

| 面 | 臂 | 年化 | 同价基准 | 出版超额 | 臂MDE | 配对均值 | 配对95%宽 | t | 相关 | 配对过线 |
|---|---|---|---|---|---|---|---|---|---|---|
| census_commodity | tsmom\|{'lookback': 120, 'skip': 21... | 4.99 | 3.8 | 1.19 | 3.78 | 1.09 | 5.29 | 0.4 | 0.086 | 否 |
| census_commodity | tsmom\|{'lookback': 250, 'skip': 21... | 5.19 | 3.8 | 1.39 | 3.66 | 1.26 | 5.25 | 0.47 | 0.072 | 否 |
| robust_tsmom_commodity | 120d | 4.99 | 3.8 | 1.19 | 3.78 | 1.09 | 5.29 | 0.4 | 0.086 | 否 |
| robust_tsmom_commodity | 250d | 5.19 | 3.8 | 1.39 | 3.66 | 1.26 | 5.25 | 0.47 | 0.072 | 否 |

## 被臂 MDE 挡住、但配对看得见的臂

(无：本轮没有一条臂出现这种错位)

## 面逐张

| 面 | 臂 | 复现 | 两尺皆过 | 两尺皆否 | 臂MDE藏了可见超额 | 臂MDE误放 |
|---|---|---|---|---|---|---|
| census_bond_futures | 5 | 5 | 0 | 5 | 0 | 0 |
| census_commodity | 14 | 14 | 0 | 14 | 0 | 0 |
| census_index_futures | 20 | 20 | 0 | 20 | 0 | 0 |
| pair_all10_60d | 1 | 1 | 0 | 1 | 0 | 0 |
| pair_bond_curve_60d | 1 | 1 | 0 | 1 | 0 | 0 |
| pair_commodity_60d | 1 | 1 | 0 | 1 | 0 | 0 |
| pair_index_60d | 1 | 1 | 0 | 1 | 0 | 0 |
| reversal_commodity_5d | 1 | 1 | 0 | 1 | 0 | 0 |
| reversal_index_5d | 1 | 1 | 0 | 1 | 0 | 0 |
| robust_donchian_index | 3 | 3 | 0 | 3 | 0 | 0 |
| robust_ma_index | 3 | 3 | 0 | 3 | 0 | 0 |
| robust_tsmom_commodity | 3 | 3 | 0 | 3 | 0 | 0 |
| trend_single_AU_long | 1 | 1 | 0 | 1 | 0 | 0 |
| trend_single_IC_long | 1 | 1 | 0 | 1 | 0 | 0 |
| trend_single_RB_long | 1 | 1 | 0 | 1 | 0 | 0 |
| trend_single_SC_long | 1 | 1 | 0 | 1 | 0 | 0 |
| trend_single_T_long | 1 | 1 | 0 | 1 | 0 | 0 |

## 没审的面（如实列出）

`results/bench_*.json` 里能重建臂的只有 `bench_generic` 的 cell 族——有 `research/cells/<id>.json` 才能不靠猜复现仓位，共 17 面。其余 33 张面由各自脚本直接跑（审计面审的是其中 21 张有臂的），没有可重建的配置，不做半猜检验。

- 无 cell 配置（33）：ah_premium、astock_lowvol、audit_basis_timing、audit_fut_trend、basis_capacity、basis_timing_perm、basis_timing_perm_masks、basis_timing_replicate、basis_timing_size、basis_timing_size_masks、bond_curve、bond_defensive、cash_vehicle_window、cash_window_sensitivity、cb_floor、cmdty_xsec、cost_stamp_census、defensive_sleeve_vehicle、donchian_repair_rerun、donchian_unit_audit、etf_census、fut_pair、fut_trend、go_ruler_audit、ledger_donchian_exposure、live_thread_dedupe、night_rollup、power、queue_truth、repo_ladder、revalidate、signal_scale_invariance、verdict_book

## 这份面不说什么

- 不重跑也不重发判决：`results/bench_*.json` 与 MDE 列一个字未改
- 配对 t 检验的是「这套仓位相对同篮子持有是否稳定跑赢」，不是「这套仓位会赚钱」——持有本身也可能是负的
- 重建复现腿只用 ±0.05pp 判等：面板每天推进，重建用的是今天的面板，与出版时的截止日不同，腿失败会逐条列在 json 的 `mismatched` 里而非静默丢弃
- 配对的通过与否**不能**直接当 GO：它没看样本外、没看前后半、没看剔除最好一年

## 复现

```
python scripts\bench_excess_paired_test.py
python scripts\bench_excess_paired_test.py --face census_commodity
python scripts\bench_excess_paired_test.py --selftest
```
