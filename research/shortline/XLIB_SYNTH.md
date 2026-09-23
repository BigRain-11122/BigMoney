# XLIB_SYNTH 预注册：跨库小K合成复评（GTJA191 × WQ101，core48 ETF 域）

- **批号**：XLIB_SYNTH（cross-library synthesis re-eval，小K复评）
- **车道**：bm-a 研究部（认领 MSG-20260924-0512，commit 5aa8159 先行锁定）
- **日期**：2026-09-24（跑前冻结）
- **上游**：P-2（bm-b，GTJA191 K=20 合成，诚实判负 IS IR 0.236<0.30）§11 开放指针「小 K 复评须另开预注册+多重性记账」；P-1a/P-1b 货架=本批唯一素材；PS2 货架效应/nullA 带教训为设计输入
- **多重性声明（前置第二眼）**：本批=ETF 域外部库合成第 2 次试验（P-2 K=20 为第 1 次）；股票域 LHB 合成线（P-S/P-S v2/PA2）已三判收线，与本批素材不相交。**若本批 FAIL：ETF 域外部库合成线与 P-2 合流收线，无新材料不得重开**（禁止跑到达标为止）。
- **账本**：零引擎跑（引擎 N=2791 不动）；因子账本 prev=3238（P-1d 链头），added=本批新合成评估数（公式：1 primary + 2 敏感性列 + 1000 nullA + 1000 nullB + primary 过门后 h20 报告列 1）；成员序列复现**不计账**（P-1a/P-1b 已计，PS2/g25 记录格复现先例）。

## §1 素材与 α 机制（D6 机制段，四选一）

**机制=行为偏差（短期反转/过度反应修正）**：GTJA 货架头部为短期反转族（081/100/097/165，P-1a 实证同族），WQ 货架头部 alpha018 为波动率-相关类（P-1b §7.4 判非反转 DNA 但与反转簇存在中度同向叠加风险=本批聚类的正主要务）；166/040/006 等正侧成员为趋势延续族。一句话论证：宽基 ETF 域上外部库的可复制 α 集中于过度反应修正与趋势延续两类行为偏差，合成仅在前二者跨族去冗余后仍有增量 IR 时成立。

**在批内同族去冗余规则（冻结）**：成员按 h10 IS 段 IC 序列两两相关（pairwise-complete，重叠≥200 交易日）聚类，阈值 corr≥0.5；贪心法=成员按 |IS IC| 降序逐个分配到首个 corr≥0.5 的既有代表簇，否则自成一簇新代表。簇代表=簇内 |IS IC| 最大者。

**D6 披露**：本批为因子层合成，无在册策略/在队候选的直接同族比较（策略级转化须另开预注册先过 D6 逐对名单）；在批内以聚类条款承担同族冗余控制。

## §2 宇宙与窗口（冻结）

- 宇宙=core48 裸码（48 只，`shortline_p1_ic.load_panels` 既有口径，价格列 ffill）；
- **evidence_cutoff=2026-09-22**：活面板截断到该日再计算（R27 数据漂移坑律：一切 vs 记录件逐位比对的门禁必须截断到录制时点；P-1a/P-1b 记录件即此口径）；
- IS 段 ≤2024-12-31（composite_ic.IS_END），OOS 段 2025-01-01→cutoff；h10 主口径，h20=仅 primary 过门后的报告列（snooping 折价标签）；
- 成员复现门禁（硬门，先于一切数字）：货架 125 员全部重算 h10 IS IC，与 P-1a/P-1b 记录值 |Δ|≤1e-4（记录值 4 位小数舍入容差）；任一员超差=整批 VOID 中止不产数。

## §3 素材货架与主合成（冻结）

- 货架 = P-1a pool（89，`results/shortline/gtja191_ic.json`）∪ P-1b pool（36，`results/shortline/wq101_ic.json`），命名不相交（alpha191_* vs alpha0xx），共 125 员；
- 聚类按 §1 规则在 h10 IS 段 IC 序列上执行；
- **primary = Top-4 簇代表**（按代表 |IS IC| 排序取前 4），逐员按其 IS IC 符号定向（sign-orientation），等权 z 合成（逐日横截面 z，≥5 名生效；composite_z min_valid=3）；
- 敏感性列（报告非门）：K=3（Top-3 代表，min_valid=2）与 K=5（Top-5 代表，min_valid=3）。

## §4 null 与门禁（冻结，跑前写死）

- **nullA（货架带，V1 主判线）**：从 125 员货架抽 K=4（无放回）1000 次，逐员按 IS 符号定向+等权 z（min_valid=3，与 primary 同构造同偏同秤），取 IS 段 |IC| 的 p95；
- **nullB（全总体带）**：从两库全部 computed 员（GTJA 183 ∪ WQ 82=265）抽 K=4 同构造 1000 次，IS 段 |IC| p95；
- seed 家族：nullA=46000+i、nullB=47000+i（i=0..999，全新注册，与 SEED_REGISTRY 既有 42k/43k/45k/20260923 系不冲突）；
- **门禁（h10 主口径，全 |绝对值| 判）**：
  - V1：primary IS |IC| > max(0.02 地板, nullA p95, nullB p95)；
  - V2：primary IS |IR| ≥ 0.30（P-2/PS2 同墙）；
  - V3：OOS IC 与 IS 同号 且 |OOS IC| ≥ 0.5×|IS IC|（PS2 同式）；
  - 期数门：IS 段 n_periods ≥ 500；
  - PASS = V1∧V2∧V3∧期数门。PASS → 策略级转化另开预注册（G1' v2 共享库门）；FAIL → 收线（多重性声明条款）。
- 判据引用：因子层门禁为 P-1a/P-2/PS2 连续口径（V1/V2/V3+null）；本批零策略级评估，不触及 science_gates.g1_prime_v2（其属策略级转化批）。

## §5 预注册预测（跑前写死，跑后 §7 对账）

1. 复现门禁：125/125 员 |Δ|≤1e-4 全过（同面板同管线确定性）；
2. 聚类结构：GTJA 反转四强（081/100/097/165）塌缩为单簇；WQ 018 与该簇 corr 落 [0.25, 0.60] 自成一簇；Top-4 代表预测={081 系, 018 系, 166 系, 127/054/095/132/061 五者之一}；
3. nullA p95 ∈ [0.035, 0.065]（货架强于总体、PS2 货架效应在更低 IC 刻度的转移；125 员大货架带宽于 PS2 的 28 对）；
4. primary IS |IC| ∈ [0.050, 0.085]、IS |IR| ∈ [0.25, 0.45]；**V2 为绑定约束**，判 PASS 概率约 45-55%；
5. OOS 留存 ∈ [0.4, 1.1]（P-2「合成增益在 OOS 端」模式若延续则留存可 >1）；
6. h20（若产出）|IC| 高于 h10（P-1a 反转族 h20 更强的既有模式）。

## §6 结果（跑后回填，跑前必须为空）

## §7 批后复盘（跑后回填：预测对账+门禁链损耗+结论）

## §8 产物与账本（跑后回填）

- 产物：scripts/xlib_synth.py；research/shortline/xlib_synth_results.csv；results/shortline/xlib_synth.json（顶层 evidence_cutoff=2026-09-22，cutoff_meta 口径）；
- audit：elapsed、ic_computations、workers=1、cpu_cap_policy=O-20260923-1738 单进程向量化（批内估算 <90s，无需 parallel_runner）。
