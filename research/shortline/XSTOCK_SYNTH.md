# XSTOCK_SYNTH 预注册：股票池跨库小K合成（LHB × GTJA191 × WQ101 × 扩展槽，日频 IC 层）

- **批号**：XSTOCK_SYNTH（cross-library stock-pool synthesis，小K）
- **车道**：bm-b 研究部（认领 MSG-20260924-0905，commit cb8f03d 先行锁定）
- **日期**：2026-09-24 09:0x（跑前冻结——**冻结时点早于 WQ finalize 完成**：素材选择按规则写死（pool_h10 活读 finalize 产物），不看 WQ 谁过线，杜绝成分窥探窗口）
- **上游**：r80/r82 指针「收割后=股票池跨库合成 prereg」——本批把 prereg 提前到收割前（规则先行=预注册纯度升级，非偏离）；素材=PA2（r41-42，股票域合成第 1 次试验，LHB×内部因子 FAIL）之后**新增的三个素材库**（P-1c GTJA 严口径 21 员 finalize 09-24 03:30、WQ 腿 finalize 待落、P-1d dzjy_amt_share_20 r60）
- **多重性声明（前置第二眼）**：本批=**股票域合成第 2 次试验**（PA2 为第 1 次，素材=LHB×J6内部四因子，FAIL IR 0.224/0.198）；ETF 域合成线已三判收线（P-2/XLIB/PS2 系），与本批素材不相交。**若本批 FAIL：股票域跨库合成线收线，无新素材库不得重开**（禁止跑到达标为止）；LHB/扩展槽维持单因子用法（P-A/P-S 定案不变）。
- **账本**：零引擎跑（引擎 N 不动）；因子账本 added=1 primary+2 敏感性列+2000 null+（primary 过 V1 后 h20 报告列 1）；成员序列复现**不计账**（XLIB/PS2/g25 先例）。

## §0 批件身份

- **批内格数（N_eff）**=3 评估（1 primary+2 敏感性）+2000 null 评估；h20 报告列若产出 +1。
- **算力预算**：成员复现门 ~2-3min（26-35 员 × 源约定 IC）+ 主合成/敏感 ~3 评估 + **null 2000 抽 × ~2-4s/抽（5129 列日频面板逐日 rank IC）≈ 70-130min 单 worker**→ parallel_runner 12 workers ≈ **6-11min 墙钟**；**>10min 风险→强制后台化+跨轮 checkpoint**（R41 律）；批报告必带 audit 段（compute_audit CLEAN 否则不入账）。
- **部门**：dept:研究（playbook §6 P-2 型合成线，股票域）。

## §1 α 机制段（D6 四选一）

**机制=行为偏差（注意力稀缺×短期反转×过度反应修正的跨库去冗余组合）**。一句话论证：股票域各库幸存者的可命名行为机制高度互补——LHB=注意力稀缺（上榜≈散户火力聚焦→反转，count_20 |IR| 0.84=全项目最强单因子证据）、GTJA 严口径头部=短期反转 DNA（081/070 簇，宽截面 null p95 0.0016 下过三线）、WQ 量价类=波动率-相关/趋势延续族、dzjy_amt_share=机构大宗火力占比（「占比类>方向类」跨源第二证）；合成仅当四类机制跨族去冗余后仍有增量 IR 时成立——**XLIB 机制定案#1（IR 墙=材料刻度）是本批的科学动机：ETF 货架最强成员 IR 0.270→墙不可越；本货架含 0.5-0.84 档成员，材料刻度上有真实数学空间**。

**在批内同族去冗余（冻结）**：成员按 h10 IS 段 IC 序列两两相关（pairwise-complete，重叠≥200 交易日）聚类，阈值 corr≥0.5，贪心=按 |IS IC| 降序逐个归入首个 corr≥0.5 既有簇否则自成一簇；簇代表=簇内 |IS IC| 最大者（XLIB §1 逐字沿用）。

**D6 披露**：本批为因子层合成，无策略级在册比较（策略转化须另开预注册先过 D6 逐对名单+股票域成本模型）；批内同族冗余由聚类条款承担。已知同源风险如实入档：P-A 判 count_20 与 days_since=同一衰减钟镜像（预期聚为一簇）；P-A 判 amt_share_20 独立正信号（预期独立簇）。

## §2 素材货架（规则冻结——写死于 WQ finalize 之前）

| 源库 | 成员规则（冻结） | 数量 |
|---|---|---|
| P-A LHB | `pa_lhb_ic.json` 记录的 V1∧V2∧V3 全过者（count_20/days_since/amt_share_20；netbuy_amt_60 FAIL 不入） | 3（已闭批，显式点名） |
| P-1c GTJA191 | `p1c_stock_ic.json` finalize 后 `pool_h10` 列表中 `alpha191_*` 员（h10 严口径三线，活读） | 21（finalize 已落） |
| P-1c WQ101 | 同上 `pool_h10` 列表中非 `alpha191_` 员（finalize 落地时自动并入，**数量跑前未知=规则制**） | TBD（0-12 预测带） |
| P-1d 扩展槽 | `p1d_ext_slots_ic.json` 记录的 dzjy_amt_share_20（V1∧V2∧V3 唯一过线员，r60） | 1（已闭批，显式点名） |
| P-1d gdhs | **不入本批**：季度频与日频合成面板错配（r66 专用季度口径已判；P4_EXT_TILT 策略转化已判负），如实披露排除理由 | 0 |

- 货架规模 = 25 + WQ_TBD（若 WQ finalize 为 0 员，货架=25 照跑；规则对结果鲁棒）。
- **成员复现门禁（硬门，先于一切数字）**：每员按其**源库约定**重算 h10 IS IC 与记录值 |Δ|≤1e-4——LHB 员用 P-A mask-A 掩码 IC、GTJA/WQ 员用 P-1c harness 面板 IC、dzjy 员用 P-1d B_dzjy 掩码 IC；任一员超差=整批 VOID 中止不产数（XLIB §2 逐字沿用）。

## §3 宇宙、面板与滞后（冻结）

- **面板** = P-1c Stage-A 股票缓存（Money02/data/cache/p1c_stock/，open/high/low/close/volume/amount/pct_chg float32 T×N；**688/689 volume/amount 双归一已在缓存内建**，r49 口径）；**宇宙=缓存 ok 集（5129）**（与 P-1c 因子批同口径；b_layer 3517=策略级宇宙，因子层不用，如实披露）；日期轴截断到 **evidence_cutoff=2026-09-22**（与全部成员批记录口径一致）。
- IS 段 ≤2024-12-31（composite_ic.IS_END），OOS 段 2025-01-01→cutoff；h10 主口径；h20=仅 primary 过 V1 后报告列（snooping 折价标签）。
- **滞后规则（各源各自冻结约定，面板对齐=「t 日已知值」语义）**：GTJA/WQ 收盘 t 可算→panel[t]；LHB T 盘后披露→panel[t+1]（P-A lag_trade_days=1）；dzjy T+1 盘后披露→panel[t+2]（P-1d r47 定案）。禁未来数据：实现轮必须过 truncate-and-compare 因果自检（合成面板在 cutoff 内逐日可复算）。
- **稀疏员表示（PA2 股票域先例沿用）**：LHB/dzjy 事件类员在全宇宙 0-填补（0=无事件基线，count_20=0 是真实信息非缺失）；dense 员（GTJA/WQ 价格类）天然全覆盖。全部员在 ok 宇宙逐日横截面 z 化。
- 合成 = 逐日横截面 z 等权均值，min_valid=3（K=4 时 ≥3 员有值才出值；XLIB/PS2 同构造）。

## §4 null 与门禁（冻结，跑前写死）

- **nullA（货架带，V1 主判线）**：从货架全员（§2 表）抽 K=4（无放回）×1000 次，逐员**按其源库记录 IS IC 符号定向**+等权 z（min_valid=3，与 primary 同构造同偏同秤），取 IS 段 |IC| p95。定向偏置对称性=P-2「定向即偏差」教训的 matched-null 解。
- **nullB（全总体带）**：从四源库全部 computed 日频员（GTJA ok 181 ∪ WQ ok ~82 ∪ LHB 4（含 netbuy）∪ dzjy+margin 7（gdhs 季频员不入，与货架排除对称）≈274）抽 K=4 同构造 ×1000 次，IS |IC| p95。
- **seed 家族**：nullA=51_000+i、nullB=52_000+i（i=0..999；已登记 SEED_REGISTRY；51_100 弃用=与 51_000+i 在 i=100 相撞）。
- **门禁（h10 主口径，全 |绝对值| 判）**：
  - V1：primary IS |IC| > max(0.02 地板, nullA p95, nullB p95)；
  - V2：primary IS |IR| ≥ 0.30（P-2/XLIB/PS2 同墙）；
  - V3：OOS IC 与 IS 同号 且 |OOS IC| ≥ 0.5×|IS IC|（PS2 同式）；
  - 期数门：IS 段 n_periods ≥ 500；
  - **PASS = V1∧V2∧V3∧期数门**。PASS → 策略级转化另开预注册（G1' v2 共享库门+股票域成本模型 P4_BATCH2 先例）；FAIL → 收线（多重性声明条款）。
- 判据引用：因子层门禁=股票域连续口径（V1/V2/V3+matched null，P-1c/P-A/P-1d 三线同式）；本批零策略级评估，不触及 g1_prime_v2（其属策略转化批）。
- **预测对照与判线当批读数**强制入 §7/§8（s7-T：gate_attrition.json 追加行+skill/门线当批数字披露）。

## §5 跑前预测（写死于跑前，跑后 §7 对账）

1. 复现门禁：全员 |Δ|≤1e-4 过（确定性管线）；
2. WQ 严口径过线员 ∈ [0, 10]，点估计 ~3（ETF 域 WQ 0/82 但股票域截面宽 4×、null p95 低 4×；量价类在反转 DNA 支配域多为弱负迁移）；
3. 聚类：count_20|days_since 合并单簇（衰减钟镜像）；amt_share_20 独立簇（P-A 独立正信号）；GTJA 反转簇聚合；**Top-4 代表预测={LHB 簇, GTJA 反转簇, dzjy_amt_share_20, WQ 最强员或 GTJA 第二簇}**；
4. nullA p95 ∈ [0.04, 0.09]（货架含 0.84-IR 档成员→带宽显著高于 XLIB 125 员带的 0.0509；PS2 K=2 强员带 0.0957 参照）；
5. primary IS |IC| ∈ [0.055, 0.115]、IS |IR| ∈ [0.30, 0.70]（最强成员 IR 0.84 × 去冗余后分散化增益；PA2 失败教训=其内部腿弱且被 0-填补稀释，本货架无此问题）；**V2 预计不再是绑定约束，绑定约束移向 V1 vs 抬高的货架带**；整体 PASS 概率 35-50%；
6. OOS 留存 ∈ [0.4, 1.1]（P-2/XLIB OOS 端增益模式）。

## §6 产物

script `scripts/xstock_synth.py`（gates/run/selftest 子命令；复用 pa2_lhb_synth 0-填补面板件+p1c harness 面板+p1d 掩码 IC+xlib_synth 聚类/合成/null 结构，禁重写）+ `results/shortline/xstock_synth.json`（顶层 evidence_cutoff=2026-09-22=science_gates.cutoff_meta）+ `research/shortline/xstock_synth_results.csv` + 本文件 §7 回填。

## §7 跑后实证（跑前必须为空——占位纪律：写数字即造假）

跑批=r109 继电器接力链（PID 24856，19:21:22→20:50:54，5370s，logs/xstock_post_r109.log）；跑前冻结 sha256=5e252aae…43de 与产物内 prereg_sha256 逐位一致。

- **货架**：36 员（LHB 3 + GTJA 21 + WQ 11 + dzjy 1）；总体 274 员；WQ finalize 落地 11 员并入（规则制兑现）。
- **复现门**：p1c_shelf_max_delta_is=0.0（≤1e-4 硬门过）；LHB 腿 3/3 PASS（is_ic -0.0642/-0.0647 等 6 值全对齐）；dzjy 腿 PASS（0.0424 对齐，rows=316436）。
- **聚类**：14 族；top 代表序=alpha191_070(-0.0906,9员) > alpha191_042(0.073,4) > lhb_amt_share_20(0.0644,1) > lhb_count_20(-0.0614,2) > wq101_alpha088(0.0549,1)。**dzjy_amt_share_20 归入 070 族**（机构大宗火力与 GTJA 反转 DNA corr≥0.5 同簇）；lhb_days_since 归入 042 族（与 count_20 分族=衰减钟镜像假设证伪）。
- **primary（K=4，min_valid=3）**：IS IC=0.1078 / IS IR=1.03 / IS n=4373；OOS IC=0.0965 / OOS IR=0.581 / OOS n=409；full IC=0.1069；pandas 交叉核验=0.0。
- **敏感性**：K=3 IS IC 0.0876/IR 0.634；K=5 IS IC 0.091/IR 0.627（OOS 0.0965 不降）——K=4 非择优孤点。
- **h20 报告列（V1 过后披露，snooping 折价）**：IS IC 0.1245 / IS IR 1.158 / OOS 0.11。
- **null（seed 51000/52000 家族，各 1000 抽）**：nullA p95=0.0888（36 员货架带）；nullB p95=0.0630（274 员全总体带）；流式真缓存等价门 worst=0.00e+00 / mismatches=0。
- **门禁读数（h10 主口径）**：V1 ✓（0.1078 > max(0.02 地板, nullA 0.0888, nullB 0.0630)=0.0888，边际 0.019）；V2 ✓（1.03 ≥ 0.30，边际 0.73）；V3 ✓（同号且 0.0965 ≥ 0.5×0.1078=0.0539，留存 0.895）；期数门 ✓（4373 ≥ 500）——**PASS**。
- **账本（统一链，audit CLEAN 门过 audit_counted=true）**：prev=58070 → +2004（1 primary+2 敏感+2000 null+1 h20 报告列，与 §0 冻结口径逐项一致）→ **total=60074**。prev 读点=r114 S0 pull（落地 bm-a T-22 finalize 58070=22177+35893）后数秒、链内 ledger 读前——读的是最新统一头，无重复计数；链头双面复算 60074 与产物逐位一致。

## §8 批后复盘（s7-T 必填）

**预测对账（§5 六条：3 对 / 2 部分 / 1 错）**：
1. 复现门禁全员 ≤1e-4：**对**（实达 0.0，确定性管线）。
2. WQ 过线员 ∈[0,10] 点估 ~3：**错**——实达 11（§2 规则面 0-12 带覆盖、§5 判定带差 1 员破上沿）；「量价类在反转 DNA 支配域弱负迁移」机制推断被股票域宽截面证伪（ETF 域 0/82 → 股票域 11/82）。
3. 聚类：**部分**——amt_share_20 独立簇 ✓、GTJA 反转簇聚合 ✓（070 族 9 员/042 族 4 员）；count_20|days_since 合并单簇 ✗（分入 042 族与 count_20 族，衰减钟镜像在 corr≥0.5 阈下不成立）；Top-4 预测含 dzjy 独立代表 ✗（并入 070 族）、WQ 最强员 ✗（alpha088 居第 5，未入 primary）。
4. nullA p95 ∈[0.04,0.09]：**对**（0.0888，贴上沿——0.84-IR 档成员抬带与预判同向）。
5. primary IC/IR 带：**部分**——IS |IC| 0.1078 ∈[0.055,0.115] ✓；IS |IR| 1.03 **破上沿 47%**（跨四族去冗余分散化增益大于建模）；「V2 不再绑定、绑定移向 V1 vs 抬高货架带」✓（V1 边际 0.019 << V2 边际 0.73）；PASS 落在 35-50% 预测窗内 ✓。
6. OOS 留存 ∈[0.4,1.1]：**对**（0.895）。

**损耗账**：gate_attrition.json 已追加 XSTOCK_SYNTH 行（kind=measurement，cells_ledger_delta=2004，ledger_total_after=60074）；成员序列复现不计账（§0 冻结）。

**科学结论**：股票域跨库合成第 2 次试验 **PASS**——PA2 失败归因（内部腿弱+0-填补稀释）被跨库货架机制否定；四族互补（GTJA 反转×2 + LHB 注意力×2）在 h10/h20 双口径、K=3/4/5 三规格、nullA/nullB 双带下稳定过线。**多重性声明兑现：本批 PASS → 股票域合成线继续（下次素材= gdhs 季频解冻或新库）；策略级转化须另开预注册**（G1'v2 共享库门+股票域成本模型 P4_BATCH2 先例，含 B 层宇宙 3517 过滤与 T+1/成本实盘级压测），转化批前不得入册。

**回执**：r114 轮报告 + CODELY.md 行级记录；T-11（负面事件消费）解锁认领（gate=本 finalize 落地已满足）。
