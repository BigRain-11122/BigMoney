# P-1e 幸存者近邻相关检验规格（消费前置·machinery-check·跑前写死）

> 机器/车道：**bm-b 循环轮**（dept:研究）· r227 认领，F-04 声明=`fleet/inbox/MSG-20260926-0610-bm-b.md`（本 commit 锁）。
> 令链：P-1e 批一次定稿（r226：`P1E_ZOO_BEHAVIOR_IC.md` §7 L121 入册前置）→ STRATEGY_LIBRARY §四 Zoo 行（同文冻结）→ r226 state.next 指针③（近邻 corr 检验 spec·合成批消费前置·开放池认领制）。
> 类别：**machinery-check（检验机件）**——零引擎跑、零账本 append、零门写、零货架翻面（收割轮人工回填库行）；本检不产出策略判定，只产出「合成素材可否作独立列」的前提读数。

## §0 检件身份【跑前】

- 检名：**P-1e survivor neighbor-corr check**（stv/coin_team × 冻结名单近邻）。
- 动机：P-1d/P-S v2「货架效应」教训——同形态高相关对的合成增益可能只是 √2 分散而非新信息；故两员幸存素材入合成批消费前必查近邻相关（D6 同族 max|corr|≥0.7 拒收律，PREREG_TEMPLATE §1 机制门槛同源）。
- 产物：`results/shortline/p1e_neighbor_corr.json`（runner=scripts/p1e_neighbor_corr.py；确定性幂等，重跑数值恒等）。
- 执行：>5min（面板装载主导，r219 探针 365.8s 同构）→ **池化 runnable_pool + autofill 续批**（O-20260924-2100；lane=bm-b，p1c_stock 缓存机本地 r188 律）。

## §1 冻结协议【跑前写死】

- **材料（受检侧）**：`zoo85_stv`、`zoo92_coin_team`（P-1e pool_h10 幸存者，r226 判定面）。
- **判定面近邻（frozen 名单，两处前置文同文）**：
  - stv ↔ `zoo85_terrified`（同 #85 家族·掩码共享面）
  - coin_team ↔ `alpha191_070`、`alpha191_081`（P-1c GTJA 反转簇·负号族）
  - coin_team ↔ `lhb_count_20`（在册注意力反转·项目最强单因子证据 IR −0.84）
- **披露面对（advisory only·不进判定）**：stv↔{070, 081, lhb_count_20}、coin_team↔terrified——合成批聚类信息面（P-1c §8 ⑤ 先例），任何值仅披露不拒收。
- **相关面双计（r219 探针口径）**：
  - F1 = 截面 Spearman 逐日序列的时序均值（`_xs_spearman_series`，成对交集、n≥5/日）；
  - F2 = IC10 序列 Pearson（h10 主口径·`_ic_series_fast`，共同期数披露）。
- **窗口：IS-only（≤ IS_END 2024-12-31）**——OOS 面零触碰（r219 探针先例；样本外恒盲的保守读法，相关面非判读亦不偷看）。
- **数据/构造（零新逻辑·全复用）**：p1c_stock 缓存面板（T=8792×N=5222，evidence_cutoff=2026-09-22，缓存零刷新冻结面）+ turnover_derived sidecar（r219 物化·冻结公式）+ p1e_factors 冻结构造器（selftest-gated）+ GTJA vendor（alpha191_070/081）+ LHB 事件栅格（`xstock_synth._lhb_event_grids` PA2-verbatim 核心：dedup max-成交额行、rolling20、**shift1 T+1 可得性已含**；`LHB_PATH/W_COUNT` 自 pa_lhb_ic）。
- **方向口径**：原值相关不翻转（|corr| 对方向不敏感）；两员已知负号 IC 事实在披露面记录，不入相关计算。
- **判线（D6 律）**：判定面对上 max|corr|（F1/F2 全面取最大）**≥ 0.7 → REJECT**（该对视为同族重复：涉事材料在联合合成批内禁作独立列，按同族簇合并披露）；**< 0.7 → PASS**（前提满足，全值披露）。无 watch 带、无软线——硬线 0.7 一次定读。
- **探针锚校验（构造保真腿）**：r219 探针已实 measu 的 F1 面（stv↔terrified、stv/coin↔070/081、coin↔terrified 等 6 对 xs_spearman_mean）必须逐位复现（|Δ|≤1e-4 容差=4dp 舍入界）——锚漂移=fail-closed exit 1 零产物（r157 配对律：复用件漂移=病，非容忍面）。

## §2 产物契约【跑前】

- JSON 结构：meta（检名/规格/车道/构造源指针/elapsed）/ cutoff 面（顶层 `evidence_cutoff`=2026-09-22 + `science_gates.cutoff_meta`，C2 合法键）/ verdict（pass|reject + max|corr| + argmax 对与面）/ pairs（逐对 F1/F2 值+n_dates/n_common+verdict_in_face 标志）/ probe_anchor（6 对锚校验读数）/ coverage（各构造器 IS 覆盖，探针同口径）/ advisory 全值。
- 幂等：结果件存在且自洽（json.loads 过 + verdict/pairs/evidence_cutoff/probe_anchor 四键全）→ skip 保留原件（房式 exists=skip checkpoint 纪律，kill/restart 安全）；损坏件 → 重算覆盖。判定面数值零墙钟依赖（时间戳仅 meta 层）。

## §3 selftest 面【hermetic·入池前置】

1. F1/F2 数学腿：合成因子对（已知 corr 构造）上 F1 复现手算截面 spearman、F2 复现手算 pearson（容差 1e-12 级）。
2. LHB 栅格腿：合成日历+合成事件手算 count20+shift1（T+1 可得性语义：事件日 t 的计数在 t+1 才可见）。
3. IS 切窗腿：IS_END 边界行恰含/恰排（≤ 语义）。
4. 判线边界腿：0.6999→PASS、0.7000→REJECT（≥ 语义）；advisory 对越线不触发 REJECT（verdict face 隔离）。
5. 幂等守卫腿：存在件+自洽→skip 路径；损坏件→重算覆盖。
6. 锚校验腿：罐装探针锚（4dp 记录值 vs 构造重算值）容差内 PASS / 漂移 FAIL 二形态。

## §4 预测登记【跑前·防看结果调判据】

- 已见面（r219 探针 IS-only，非本检新读数）：stv↔terrified F1 0.3365 / F2 0.4384；coin↔070 F1 0.2584；coin↔081 F1 0.2028；stv↔070 F1 0.2408——全距 0.7 线远。
- 本检新增面=lhb_count_20 相关（stv/coin 双侧）+ 全判定对的 F2 补全。预测：**全判定面对 < 0.7 → PASS** 主概率——lhb_count_20 为稀疏事件栅格（20 日窗计数，A 股上榜覆盖率低）vs stv/coin_team 全市场连续值因子，构面差异大；主不确定性=F2 IC 序列面（两因子在共同有效子集上的 IC 波动可能同向放大相关，事件稀疏面尤其如此）。
- 若 coin_team↔lhb_count_20 ≥ 0.7（任面）：coin_team 归注意力反转簇同族披露，联合合成批内与 lhb_count_20 禁双列（选一或同簇代表制）；若 stv↔terrified ≥ 0.7：stv 的独立列资格撤销（terrified 主腿 V2 差线+snooping 折价档），stv 降为 #85 家族内变体注记。此为判前写死的两分支处置，跑后按读数走，禁第三种解读。

## §5 收割轮处置【跑后·轮做非本检】

- PASS：STRATEGY_LIBRARY §四 Zoo 行「入册前置=近邻 corr 检验」子句标记 **SATISFIED**（带 max|corr| 读数+指针本件）；材料取得联合合成批独立列资格（合成批仍另开预注册，本检零授权）。
- REJECT：涉事对按 §4 分支处置改写 Zoo 行（同族簇注记），轮报告披露；合成批预注册起草时受 D6 簇约束。
- 翻面：池 shard→done（r203 轮做律）；本规格件与结果件互引（result JSON meta.spec_ref=本文件路径）。
