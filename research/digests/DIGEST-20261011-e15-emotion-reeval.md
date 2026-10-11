# DIGEST-20261011-e15-emotion-reeval —— E15 情绪族近失复判：FDR4D 改革判线 2/4 过门（2026-10-11 bm-b r876）

> 批件：E15_EMOTION_REEVAL_P1（research/E15_EMOTION_REEVAL_P1.md FROZEN @265d65754·重估 derive 面·零重模拟）；真值源：results/emotion_reeval/E15-REEVAL-2026-09-22.json（evidence_cutoff 2026-09-22·m=4·E[FP]=0.2 名义·ledger/attrition 双零）。

## 一、结论一句话

mass trial 千人题库近失残留 4 员（旧 G2 全局 DSR 处刑 0.24-0.53 落选）在改革判线（批内 BH FDR m=4 q≤10% + 四维合成 + D6）下重估：**2 员过注册口径**（W3-27009 seasonal.trend_by_season 合成分 0.54875·全段政体正；W2-23057 sentiment.turnover_surge 0.54625），2 员批内簇塌缩拒收（W3-23027/W3-46133）——改革正典「批内折减替代全局处刑」的首个 mass 面复判实证：**全局 DSR 从 0.24-0.53 → 批内 0.999 饱和（anti_luck 维失去区分度），区分度由 ret/robust/anti_overfit 三维承载**。

## 二、判决面要点

| 员 | 族 | fdr(bh_q) | D6 max|corr| | 合成分 | eligible | 上岗序 |
|---|---|---|---|---|---|---|
| W3-27009 | seasonal.trend_by_season | 0.0 ✓ | 0.1428（DROUGHT-CE-01） | 0.54875 | ✓ | 1 |
| W2-23057 | sentiment.turnover_surge | 0.0013 ✓ | 0.2664（ENGULF-CE-01） | 0.54625 | ✓ | 2 |
| W3-23027 | sentiment.turnover_surge | 0.0 ✓ | 0.2699 | 0.5425 | ✗ 批内簇塌缩 | — |
| W3-46133 | ta.strong_close | 0.0015 ✓ | 0.1749 | 0.3625 | ✗ 批内簇塌缩 | — |

- **FDR 4/4 过**（m=4 单步上调后全 ≪0.10）；D6 拒收 2 员均来自**批内互相关簇塌缩**（vs 注册六员 max|corr| 全 <0.7——非注册撞线）；sentiment 双员同族互塌保 batch_dsr 高者 W2-23057。
- **regime 面是分水岭**：W3-27009 唯一全段正（bear 2.60/bull 0.87/chop 1.08→robust 维 0.75 头名）；其余三员 bull 段全负（-0.21/-0.96/-0.23）——熊窗现金态策略的 bull 段结构性弱点被 robust 维如实压分。
- **绝对收益诚实披露**：4 员年化 1.40%-3.10% 全部低于五员 EW 基线 4.68%（ceiling 全负）——批内百分位合成不掩盖可投被动面败北；上岗≠激活（月界 s4 intake + 前向月考真终审不变·CEO 唯一门不变）。

## 三、方法学新面（工程实录）

1. **零重模拟复判通道**：冻结判决分片件（w2/w3_judge_shard_*.jsonl）逐员携 `legL_daily_returns` n=1631 全序列——复判批四维材料=冻结件 verbatim 携带+日收益纯派生，唯一引擎触面=注册六员 D6 对照 6 次轻重放（r876 首证→METHODOLOGY_ASSETS E56）。
2. **轻量 L1 批 vs 池面**：autofill 多核门（O-20260930-2355 law-1）拒单线程 runner——60-120s 单遍 derive 批走 R41 <5min 轮内烧（供给链后续腿的 runner 设计输入：ProcessPool 转换或轮内烧二选一）。
3. core48 面板本体=leg-L 全窗（2020-01-02..cutoff·1631 bar）非五员 2012 深窗——重放窗基 wbase=0 合法（探针实证·首跑死因修复 5a011ef7c 双跑留痕）。

## 四、消费与续作

- onboard 2 员 → **月界 s4 intake**（D6 binding→STRATEGY_LIBRARY 注册行+TRIAL-* 纸盘泊位+SIGNAL_BUILDERS 接线+smoke 锚定门复跑）；**48h CEO 呈报钟已起计（due 2026-10-13 11:2x）**。
- 预测对账 5✓1MISS（P5 batch_dsr 饱和带上沿失手——批容量近零时 DSR 维无区分度，如实入档）；supply floor：E15 entry 已消费（done）→ready 回 0，floor ≥3 by 10-13 待目录后续腿。
