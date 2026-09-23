# P-A2 LHB 幸存者合成（PA2_LHB_SYNTH，预注册，跑前写死）

> 令源：O-20260923-1819 queue-never-empty 条款（r40 state next_pointer fallback 二选一之 LHB 线）+ P-A 续作指针①；认领：MSG-20260923-2030（先于本批 commit，F-04）
> 性质：**因子层 IC 合成**——零引擎跑，引擎账本 N 不动；本批不注册交易员（IC≠策略）。股票池策略跑仍在 O-1820 R38 硬门挡（research/shortline/R38_RUN_CLEARANCE.md）后，本批零触碰；**COMP 过门≠策略素材自动转正，转策略另开预注册带 snooping 折价**。

## §1 数据与复用口径（全部 P-A 逐字复用，禁重推导）

- 事件源：`Money02/data/lhb/lhb_detail.parquet`（265,831 行）；去重=同 (代码,上榜日) 取龙虎榜成交额最大行→227,662 股-日事件；**事件日网格构建后整体下移 1 交易日**（signal 位 t 只含 ≤t-1 事件，榜单 T 盘后披露），前向收益自 t 收盘起算；榜前N日前瞻列一律未用
- 面板：`Money02/data/cache/p1c_stock`（本机 2026-09-23 20:17 重建 STAGE-A PASS：T=8792/N=5222/ok=5130/short=92，bars=T-01 双侧 Verify 同源；WORKERS=12=O-1738 §六 本机 cap，bm-a 构建器原样零改动）
- IC：逐日 spearman=**先掩码后排名**（J7 坑族），逐日交集≥5 名，零方差→NaN；**h10=唯一门控期限**；h5/h20 仅过门者报告列（非门控，防窥探）
- IS≤2024-12-31 / OOS=2025+（composite_ic.IS_END 公司口径）
- 复用方式：`scripts/pa_lhb_ic.py` 的 rolling_sum/shift1/rank_rows/ic_from_ranks/fwd_ret/seg_stats **原样 import**（冻结构造防漂移）；面板装载与事件落位段自其 main() 逐字复制，复制忠实性由 §2 锚定门禁裁决

## §2 锚定门禁（先行，不过门不跑批）

三幸存者 h10 注册证据（results/shortline/pa_lhb_ic.json）逐位复现；判定=round(ic,4)/round(ir,3)/n_periods 三者全等（IS 与 OOS 双段）：

| 因子 | mask | IS ic/ir (n) | OOS ic/ir (n) |
|---|---|---|---|
| lhb_count_20 | A | -0.0642/-0.840 (4373) | -0.0647/-0.790 (409) |
| lhb_days_since | C | +0.0632/+0.723 (4372) | +0.0674/+0.736 (409) |
| lhb_amt_share_20 | B | +0.0643/+0.567 (4373) | +0.0618/+0.854 (409) |

## §3 合成设计（跑前冻结；禁第三变体/禁权重搜索/禁跑后换点）

素材=P-A 三幸存者。**镜像条款**（P-A §6 机制1：count 与 days_since=同一衰减钟镜像，机械反相关）→ 每复合内择一：

- **COMP-A（主判定）**：`z(-lhb_count_20) + z(lhb_amt_share_20)` @ mask A（当日有 bar 全截面）
- **COMP-C（次判定·机制对照）**：`z(lhb_days_since) + z(lhb_amt_share_20)` @ mask C（近252日有事件截面）
- z=逐日掩码内截面 z-score（ddof=0；std=0 行→z=0），两腿等权平均（小 K 先验等权=J6 精选先例；P-2 弱尾稀释教训=不掺第 3 腿、不设 cap）
- **amt_share 0-填补条款**：近20日无事件股 share=0 为**真值非插补**（LHB成交额=0→占比=0）；P-A mask-B NaN 为筛选期保守选择，合成期取真值语义；0-并列块对 rank IC 的影响如实承担
- 主/次判定先验声明：COMP-A=主（mask A 全截面=与可交易域对齐）；**COMP-C 过门不翻案为主判定**——其若过门=素材证据+1，转策略另开预注册

## §4 null 与门（结构化 null=本批关键设计）

- K=50 对腿白噪声（seed=20260923+1000+k，与 P-A 的 +0..49 错开防碰撞）；**结构复制**：noise2 仅在 B-支撑（count_s≥1）取值、其余置 0——复制 0-填补的并列块支撑结构（纯 iid 会错置有效自由度）；noise1 全支撑 iid；同 z 等权同构合成
- 逐复合 mask 算 IS 段 p95|IC|→**V1**=|IS IC| > max(0.02, null p95)；**V2**=|IS IC_IR|≥0.30；**V3**=OOS 同号且 |OOS IC|≥0.5×|IS IC|；**期数门**=IS 有效期数≥500（mask A 中位截面 2553/mask C 1937 先验满足，如实复核）
- 方向性 null 偏差（P-2 §6 定案「定向即偏差」）如实记录：null 与真复合同构同偏同秤=诚实秤
- 判定=过全四门；跑后禁调门槛禁换口径

## §5 机制读数（跑前登记读法）

- 腿间相关：逐日 spearman(count_s, share_s) @ B∩A 支撑，IS 均值——注意力强度 vs 火力占比的机械相关；COMP-A 若被腿对冲（正相关→z(-count)+z(share) 相消）如实记为机制发现
- COMP-C=同号腿互强读数（days_since + 与 share +）
- h5/h20 报告列仅对过门者计算（P-A 惯例：观察 h20 最强惯性）

## §6 跑前预测（写死于跑前，跑后对账；对=机制理解，错=记录教训）

1. COMP-A IS IC ∈ [-0.075, +0.010]；方向不确定（腿对冲风险），55% 置信为负
2. COMP-C IS IC ∈ [+0.045, +0.090]（同号腿互强）
3. V2（IR≥0.30）：COMP-C 过门 60% / COMP-A 35%
4. OOS 保留≥0.5：两复合均过（LHB 族 96-107% 实证惯性）
5. 腿间相关 IS 均值 ∈ [+0.15, +0.55]（活动度孕育火力）
6. 全四门：COMP-C 45% / COMP-A 25%
7. 若 COMP-C 过门，h20 报告列 |IC|>h10（P-A 实证 h20 最强惯性）

## §7 跑后实证（跑前必须为空——占位纪律，写数字即造假）

> 本节由 round 41 抢救轮回填（2026-09-23 20:40）：原轮 20:10 点火→批跑完成、JSON 于 20:35 落盘后被 25min 超时击杀于 commit 前，数字全部来自已落盘产物（results/shortline/pa2_lhb_synth.json + pa2_lhb_synth_results.csv），未重跑。

- **锚定门 3/3 PASS**：三幸存者 h10 IS/OOS ic/ir/n 与注册证据（results/shortline/pa_lhb_ic.json）逐位相等（tol_mean=5e-5/IR 5e-4）。
- **COMP-A（主判定，mask A 全截面+0-填补给腿）**：IS IC +0.0090 / IR 0.224（n=4373）；OOS IC **-0.0058**（n=409，符号翻转）。V1 FAIL（<0.02 地板）/ V2 FAIL（0.224<0.30）/ V3 FAIL（OOS 反号）。**全四门 FAIL。**
- **COMP-C（次判定·机制对照，mask C）**：IS IC +0.0127 / IR 0.198（n=4373）；OOS +0.0029（n=409，留存 23%）。V1/V2/V3 全 FAIL。**全四门 FAIL。**
- 结构化 null（K=50，0-填补给腿并复制块支撑）：COMP-A p95|IC|=0.0007、COMP-C 0.0007——null 极低但 V1 由 0.02 地板主导，两复合死于地板而非噪声带。
- **腿间相关（§5 机制读数）：IS 均值 -0.1123**——与预测 [+0.15,+0.55] 方向性大错：上榜次数（注意力强度）与成交额占比（火力占比）在事件支撑内**弱负相关**，非「注意力哺育火力」；COMP-A 腿对冲风险未兑现为腿相消（z(-count)+z(share) 的正交增益也没兑现——IS IC 0.009 ≪ count 单因子 |0.0642|）。
- **预测对账（§6 九条）**：1 范围命中但方向判错（55% 负→实 +0.009，区间下沿擦进）；2 大错（+0.0127 ≪ [+0.045,+0.090]）；3 双错（V2 60%/35% 全灭）；4 大错（COMP-A OOS 反号、COMP-C 留存 23%≪50%）；5 大错（腿相关 -0.1123 负号）；6 大错（全四门 0/2 vs 45%/25%）；7 条件未触发（COMP-C 未过门→h5/h20 按预注册仅对过门者计算=未计算，JSON ic_computations=3+2+100+1=106 自洽）。
- **机制归因（双复合同判）**：0-填补把 share 腿在全截面上稀释成近常数（日均有事件股 ~1-2%），composite rank 由 count 腿主导又被 z 等权折半——「强对合成 shelf 效应」（P-S v2 e499e1a 独立实证）在 0-填补全截面掩码上**不成立**，合成增益连最强单因子都到不了。与 bm-a GM 会话 P-S v2（事件支撑内 exhaustive 28-pair null，lhb_pair IC 0.0943<null p95 0.0957 同判 FAIL）**双独立代码路径同判收线**：LHB 材料维持单因子用法（count_20 主证据 |IR|0.84 不破）。
- **裁决：双 FAIL → LHB 合成线收线**（fail-branch 兑现），素材池留档，任何复用=新预注册+snooping 折价。引擎账本 N 不动（零引擎跑）。

## §8 产物与禁令

- `scripts/pa2_lhb_synth.py`（一次性定稿）→ `research/shortline/pa2_lhb_synth_results.csv` + `results/shortline/pa2_lhb_synth.json`（含 null 阈值/门判定/audit 段）+ §7 回填
- IC 计算数（3 锚定+2 复合+100 结构 null+1 腿间相关+过门者 h5/h20）计入 JSON audit 段；引擎账本 N 不动
- 禁令：跑后禁调门槛/禁换口径/禁重跑（产物写崩=确定性重执行例外，数字须逐位相同）；本批零注册
- 续作（候选，另开预注册）：COMP 过门者→股票池策略化（O-1820 门后择机）；双 FAIL→LHB 合成线收线记录（单因子证据仍立，素材池留档）
