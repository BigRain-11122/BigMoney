# P-1a GTJA191 因子批测 IC（预注册 · 2026-09-23 · 研究部自主域）

> playbook §6 P-1 首批（O-20260923-1545 建立 / O-20260923-1620 后研究线）。
> 纪律：本文件在跑数前写死方法与门槛；跑后禁调门槛禁重跑（工程 bug 修复重跑须双跑留痕，按 SLEEVE_P3 先例）。

## §1 目的与范围

- 对 `research/shortline/external/gtja191_alpha191.py` **全集 191 个因子函数**在 core48 ETF 池全史上做横截面 IC 批测，产出有效因子池候选（供 P-2 合成）。
- 本批=**因子级筛选，非策略引擎跑**：策略账本 N=1073 不动；P-2 合成骨架须另走 G1'/G2 回测级门禁（回测级 OOS 门槛为最终裁判，J6 定案口径）。
- WorldQuant101 无 cap 子集依赖 polars（未装），**不在本批**——移植批测=下轮预注册。

## §2 数据与工程

- 宇宙=core48（`data/daily` 裸码 CSV，同 `composite_ic.load_universe("core")` 口径），全史（2020-01 起）。
- 宽面板 date×symbol：open/high/low/close/volume/amount 原始 + **vwap=amount/volume 派生**（51 处引用）。
- `turn`（3 处）/`liquidity_value`（1 处）无数据 → 该因子诚实记 `skip_missing_field`，不造数据。
- 导入 shim（研究环境零新重依赖，playbook §2.2「缺则降级，不必装 qlib」）：
  - `talib` 未装 → stub（调用即抛 → 该因子记 `skip_talib`）；
  - `factors.ops.rolling` 缺失 → 纯 numpy 实现 `_wma/_max_distance/_min_distance/_alpha191_143`；
  - `qlib` 未装 → 库自身 try/except 降级，调用 rolling_* 的因子记 `skip_qlib`；
  - `lib.*` 三件按原名注册 `sys.modules`。
- 复用 `scripts/composite_ic.py` 的 `ic_series`（逐日 spearman，≥5 符号）/`stats_block`（≥30 期）/`IS_END=2024-12-31`，禁重写。

## §3 方法

- IC：因子值 vs 未来 h 日收益，h∈{5,10,20}；分段 full/IS(≤2024-12-31)/OOS(≥2025-01-01)。
- 因子方向不可知（负 IC 因子在合成中可负权使用）→ 门槛一律取 |值|。
- **随机对照（playbook gamble 纪律）**：K=50 个白噪声因子面板（seed=20260923..20260972，正态，同面板形状），同一套 IC 统计 → IS 段 null 分位线：
  - `p95_abs_ic[h]` = 50 个 null 的 |ic_mean_IS| 的 95 分位
  - `p95_abs_ir[h]` = 50 个 null 的 |ic_ir_IS| 的 95 分位
  - 已知局限（如实记）：白噪声 null 是逐日横截面噪声线，未含真实因子的 IC 自相关致宽效应 → null 线偏松方向，靠 P-2 回测门兜底。

## §4 门槛（跑前写死）

因子入池须在**至少一个 h** 上同时满足：

| 门 | 条件 |
|---|---|
| A1 | `|ic_mean_IS| > p95_abs_ic[h]` |
| A2 | `|ic_ir_IS| > p95_abs_ir[h]` |
| A3 | `n_periods_IS ≥ 500` |
| A4 | OOS 同号存活：`sign(ic_mean_OOS)==sign(ic_mean_IS)` 且 `|ic_mean_OOS|>0` |

- 强档（合成优先序用）：再加 `|ic_mean_OOS| ≥ 0.5 × |ic_mean_IS|`。
- 跳过因子不入池也不销毁，逐个记录原因（talib/qlib/missing_field/not_implemented/运行异常，异常取首行短消息）。

## §5 预注册预测（跑前写死，跑后对照）

1. 跳过数：**5–15 个**（qlib 引用 5 处、talib ops 若干、turn/liquidity 4 处、unfinished pass ≥1）。
2. 入池数：**5–25 个**（GTJA191 为个股横截面设计，48 名 ETF 池削弱 RANK 类；时序类更可能存活；2025+ 政体切换杀 OOS 同号率）。
3. null 线：p95_abs_ic ∈ [0.005, 0.03]（IC 自相关不确定性大，区间放宽）。
4. 强档数 < 入池数一半（OOS 半衰是常态，J6 复合因子先例）。

## §6 会计

- 因子账本：191 计算位 + 50 null 位 × 3 期限，全记录于 JSON；跑后本节追加 §7 实证。
- 禁令：跑后禁调门槛、禁挑口径、禁跑到达标为止；「更绿的另一口径」可记录不翻案。

## §7 实证（2026-09-23 16:5x 跑毕定稿）

### 7.1 工程三跑留痕（预注册允许的 bug 修复重跑，全记录）

| 跑 | 状态 | 计算位 | 池 | 判定 |
|---|---|---|---|---|
| r1 | einsum 标签 bug（'w' 同时当符号轴+权重轴→WMA/DECAYLINEAR 族 15 因子全灭于 broadcast error） | 170 | 85 | **作废**（缺陷在 shim 不在外部库；14 个"广播 error"初判 pandas3 陷阱是误诊） |
| r2 | _wma 改 tensordot 修复；None 返回记账漏判（143/030 两个 unfinished 存根被误标 ok） | 185* | 89 | 数字有效、记账缺陷 |
| r3 | 与 r2 逐位一致（diff cells=0，剔除 compute_s 计时列）——确定性实证 | 185* | 89 | 同上 |
| r4（终） | None 返回分支补上 | **183** | **89** | **定稿** |

*r2/r3 的 185 含 2 个误标 ok 的 None 存根，真实计算位与 r4 相同=183；池/强档数 r2→r4 稳定 89/83 未变（143/030 从未入池）。

**shim 自检门禁已固化进脚本**（跑批前硬校验 _wma/_max_distance/_min_distance vs pandas rolling 参考，任一 False 即中止）——本批最大教训：IC 快速路径有等价自检而 numpy shim 没有，einsum bug 正是从无门禁处漏进去的。

### 7.2 终盘数字

- 191 函数 → **183 计算位 + 8 跳过**（全记录于 CSV）：error=1（alpha191_005，外部库 pandas3 相容性 Rolling.rank(axis) 废弃，非 shim 之过）；skip_qlib=3（rolling_slope 引用）；skip_missing_field=2（turn，无换手率数据不造）；skip_not_implemented=2（030/143 unfinished 存根）。
- **null 线（K=50 白噪声）**：p95_abs_ic = 0.0078/0.0082/0.0070（h5/h10/h20），p95_abs_ir = 0.052/0.055/0.047。
- **池（A1-A4 任一 h）=89/183（48%）；强档（OOS≥0.5×IS）=83**；per-h 过门：h5=52 / h10=61 / h20=72。
- IC 等价自检：fast vs 参考 ic_series max|diff|=3.33e-16（1551 期逐位）；批间确定性：diff cells=0。
- 头部因子（IS |IC| 排序，h20）：alpha191_100/081/165/097（IS -0.074~-0.078、IR -0.29~-0.33、OOS -0.036~-0.050，**负 IC=反转族主导**）；正侧最强 alpha191_166（IS +0.047、OOS +0.054）。量级与内部最佳单因子 vol_60 的 0.064 同档，未及复合因子 0.1205。

### 7.3 预注册预测对照（§5）

| 预测 | 实际 | 判定 |
|---|---|---|
| 跳过 5–15 | 8 | ✓ |
| 入池 5–25 | **89** | **大错**——机制见下 |
| null 线 [0.005,0.03] | 0.007–0.0082 | ✓ |
| 强档 < 池半 | 83/89=93% | **错** |

### 7.4 两个预测错的机制读数（重要，P-2 设计输入）

1. **白噪声 null 大幅低估真实因子的噪声带**（预注册 §3 已声明局限，本次实锤）：p95_abs_ic≈0.008 是逐日横截面噪声线（T_IS≈1550 日、每日 48 名）；真实因子值有时序自持性→IC 序列自相关→有效样本远小于 1550→真实"纯噪声"分位线高得多。89/183 过门（48%）说明 A1/A2 是**宽筛门**——89=候选池不是有效因子名单。P-2 若要池内再分档，须换 overlap/block-bootstrap null 或直接跳到回测级 G1'/G2 终审（预注册 §1 既定路径）。
2. **强档 83/89 的 OOS"存活"是弱证据**：OOS 段仅 ~174 日，h20 前窗重叠→独立窗口 ≈9 个；同号+半衰条款在如此薄的样本上近乎必然宽松。如实记录、不当作稳健性证明。
3. 附带诚实声明：GTJA191 为个股横截面设计，48 名 ETF 池本就窄（预注册 §2.2 已声明）；top4 因子公式高度同族（负 IC 反转 DNA），**P-2 合成前必须做相关性聚类**，89 候选直接加权=重复计权同一信号。

### 7.5 会计与产物

- 因子账本：183+50 null 位 ×3 期限，全量在 JSON/CSV；**策略引擎账本 N=1073 不动**（本批零引擎跑）。
- 产物：`scripts/shortline_p1_ic.py`（含 shim 自检+等价自检双门禁）、`research/shortline/gtja191_ic_results.csv`（191 行全字段）、`results/shortline/gtja191_ic.json`（机器可读，候选上面板）。
- 禁令照旧：本批跑后禁调门槛禁重跑；「更绿的另一口径」不翻案。

### 7.6 续作指针

1. **P-2 合成预注册**（研究部自主域）：89 池先相关性聚类（预计簇数≪89）→ 每簇代表因子 z 合成 → 骨架 → G1'/G2（回测级 OOS 终审+随机基线同跑+账本记账恢复）。
2. WorldQuant101 无 cap 子集批测：polars→pandas 移植，另开预注册。
3. 外部库 pandas3 移植候选：alpha191_005（Rolling.rank axis）——不修不销毁，只登记。
