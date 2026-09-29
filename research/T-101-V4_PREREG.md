# T-101-V4 预注册（锦标赛版本批 v4 · A2 前导臂完整冻结 + A1 头号臂骨架车道标注）

> 依据：PREREG_TEMPLATE.md · BACKTEST_SCIENCE.md v2 · BACKTEST_PLAN.md 三铁律 · TRIAL_LABOR_LAW §2 两段制 · DECISION_CHAIN v1.2 §四.7 锦标赛节拍（freeze-before-W8-verdict：W8 JUDGE verdict 未出窗内冻结 v4 = 预先承诺姿态合法）
> 供给触发：compute_audit supply_gap（池 ready=1<3）· r432 next 指针 (a) · TRIAL_LABOR_LAW §1 常供律
> 臂表源：research/DECISION_CHAIN_BENCHMARKS.md v0.2 §5（A1-A8，r432 定稿）

## §0 批件身份

- 批名：**T-101-V4-A2-PRESCREEN**（A2 RSV 双门政体门臂·廉价初筛面）；批内格数＝**10**（2 门 × 5 员；null 对照面 K=200/格如实另计披露，不膨胀策略格）；
- 认领：F-04 先行＝`fleet/inbox/MSG-20260929-1500-bma-t101v4-prescreen.md`；任务板引用＝T-101（v3 批 done 票；v4=版本批新代）；
- 部门归属：dept:研究（链条研究线）；
- 算力预算：分钟级单进程 pandas（≤2min），不入池；批报告带 audit 段（脚本 stdout 自带时长/行数）；
- 车道：**bm-a**（本机 data/daily ETF/基金面板）。A1 臂（C1 双温度计，v4 头号臂）＝**bm-b 车道**（全 A 日线面板物理仅在 bm-b·跨机硬约束钉版），本批只冻结其语法骨架（见 §3-A1），不烧不占，bm-b 车道机全量冻结归其自执；
- 语法查重：TRIAL_GRAMMAR_LEDGER W1-W8 已核——W8 tstate 轴 oversold_rsv＝**个股入场过滤**语法；本批 A2＝**政体门择时**用法（门级择时、全仓门控非个股选择），非同语法重跑。

## §1 α 机制段（D6）

- [x] **行为偏差**：恐慌过度反应＋处置效应——超卖区（RSV<0.2）内恐慌抛售者被自身锚定与止损压力驱动交出筹码，T+1 制度下当日无法止损放大次日开盘割肉（国内结构性放大器），门策略承接过度反应卖方的均值回归腿。国内民俗判据形式化：超卖修复打法（CEO 研究导向律 O-1522：国内打法=方向盘）；
- 上游证据链（外源→独立验证，借力三律）：gate_verify 09-29 批（toolstack/research/gate_verify.json 冻结面）RSV60/RSV30 双门 **PASS**（OOS med_diff_net +1.081%/+0.811%，pos_share 75.9%/71.5%，成本 0.1% 往返+stride-20 不重叠三控）——20 日前向窗口径；本批＝把该门从「前向持有验证」升格为「连续政体门择时策略臂」进锦标赛判决。

**同族相关性准入检查（D6·初筛面实算）**：
- A2 双门策略日收益 vs 五员 B&H 日收益（beta 同源主险）逐对列数：**跑后 §7 实测披露**（初筛脚本 D6 段输出，判线 max|corr|≥0.7 拒收恒在）；
- 同批双函数互 corr（RSV60 门策略 vs RSV30 门策略，每员 1 对）：同上实测；
- 在册 6 员对照：机制差异声明（在册=战术/轮动/网格族，A2=宽基门控择时族）+初筛面尝试读 paper_export equity 日序列实算；不可得则全量判决面补测并在 §7 如实标注（初筛面判负处置照 §4）。

## §2 数据与面板

- 宇宙：五员冻结宇宙 O-1555＝{510300, 510050, 510500, 512100, 588000}（两 T1+三 T2 层）；
- **数据锚面定义四元组（G-ANCHOR-FACE）**：`data/daily/sh<码>.csv` ＋ `pd.read_csv`（raw 直读，非引擎池面）＋ **2012-01-01 全史起算**（510300 实际首行 2012-05-28，以文件首行为准）＋ RSV60 预热 60 bar→首有效信号第 61 bar；588000 上市 2020-11（科创50），全史短窗如实披露；
- evidence_cutoff（前向锁盒 D2）＝**2026-09-28**（最新完整 bar 日；510300 尾行实测 2026-09-28）；cutoff 后新 bar 锁定不得回流本批；结果 JSON 顶层必带 `science_gates.cutoff_meta(evidence_cutoff)`；
- 探针-锚同面断言：runner 实载路径＝`data/daily/sh<码>.csv` 逐位比对锚声明路径，一面不等＝配置错配 VOID；
- 数据完备门：5 员 csv 全在位且尾行＝2026-09-28（缺一员＝fail-closed 拒烧）；
- 面板口径：raw OHLCV 日线（qfq 前向采集面板，T-87 族），未用引擎 `load_core`。

## §3 方法学

**A2 臂（本批·bm-a 车道）**：
- 信号定义（冻结参数）：`RSV_n = (C - LLV_n) / (HHV_n - LLV_n)`，n∈{60,30}，HHV/LLV 用 high/low rolling max/min（gate_verify.py 公式逐字复刻，除零→NaN→门关）；门开＝`RSV_n < 0.2`；
- 执行（T+1 保守代理，O-1132 先例）：信号日 t 收盘算门→t+1 开盘入场；门关→次日开盘出；pos(t)＝gate(t-1) 滞后一日全仓门控；现金腿 0%；
- 成本口径：**0.1% 往返**（gate_verify cost_rt=0.001 同值）：入场腿 0.05%+出场腿 0.05%；
- 分段（判读恒带）：bear/bull/chop 三态＝510300 close vs MA200 与 MA200 60d 斜率（close<MA200 且斜率<0＝bear；close>MA200 且斜率>0＝bull；else＝chop）；
- null 对照：**同掩码循环位移 null**（掩码 np.roll 随机位移量，保持门开天数与持续期结构），K=200/格，seed 基＝**20308000**（SEED_REGISTRY 新基，取号律查 101-key 零冲突后落）；
- 初筛存活判据（跑前冻结，triage 非 G1' 降级——全量判决面 G1' v2/G2 恒在）：① OOS（2017-01-01 起）净年化超额 vs 同窗 B&H >0 ② OOS entries≥15（gate_verify min_ev_per_split 同值）③ 全期最大回撤≥-35%（描述条款）④ 门策略 OOS Sharpe > null Sharpe 中位（同掩码对照）；
- 账本：`science_gates.append_ledger("T-101-V4-A2-PRESCREEN", 10, "t101_v4_a2_prescreen.json", evidence_cutoff="2026-09-28")`。

**A1 臂（骨架冻结·bm-b 车道）**：C1 双温度计＝v3 价量四态（market_clock 政体态）× B+ 游资情绪三轴门复合矩阵（涨停>80/炸板率<10%/高度>5 板全数值判据＝research/WILD_ROUTE_LAB_S1_CARDS.md §一在册件为准·指针引用禁重抄）；全 A 日线面板派生（深史零新管道）→ 车道 bm-b 强制；其批内格数/判线细节由 bm-b 车道机按本模板另开完整 prereg 冻结（版本批同代允许臂级分件冻结，DECISION_CHAIN §四.7 K 假设一预注册并行烧）。

## §4 判据

- **本批（初筛面）**：§3 冻结的 4 条初筛存活判据（triage）；存活者→全量判决面＝{6m,12m,24m} 虚拟起点窗×成本 ×2 压测×分段×双 nulls + **G1' v2**（science_gates.g1_prime_v2 共享库，禁手抄）+ **G2**（g2_registration_v2：DSR≥0.95 原始收益 deflated_sharpe_ratio + PBO≤0.25 CSCV 8 块）——初筛存活≠策略宣称，升格资格≠注册；
- 判负处置（预先承诺）：初筛判负臂＝线关闭如实入 §7 与 gate_attrition 损耗账，禁「换参数再跑」（同语法重跑禁令同源）；政体依赖性（IS/OOS 反号族）如实入面不粉饰；
- 预期假阳性披露：10 格初筛 + 后续全量判决网格，跨波累计 N_eff 照 TRIAL_LABOR_LAW §4 不重置。

## §5 跑前预测（写死于跑前）

1. **方向**：五员中 510500/512100（中证 500/1000 弹性）OOS 超卖修复超额 > 510050（上证 50 低波大盘）；510300 居中（gate_verify 五员面实测 +0.33% 为正）；
2. **量级**：RSV60 门比 RSV30 门稀疏（entries 少 30-50%），OOS 超额中位相近或 RSV60 略优（gate_verify med_t 2.246 vs 1.723 旁证）；
3. **IS 反号风险**：2012-2016 低波慢牛段超卖修复弱（gate_verify IS thin 面双门 -0.6%/-0.4% 已暗示），IS 段超额可能为负或近零——政体依赖性如实入面（非判负理由：初筛判据主判 OOS 段）；
4. **极端日先验（硬界三件套 (c)）**：2015 股灾/2016 熔断超卖密集窗＝门长期开着连续接刀（逆势接刀风险），全期 -35% 回撤界可能被 2015-2016 bear 段击穿；若击穿→bear 分段如实单列披露（政体门本职=识别该政体失效，不豁免不粉饰）。

## §6 产物

- script：`scripts/t101_v4_a2_prescreen.py`；
- results JSON：`results/t101_v4_a2_prescreen.json`（顶层 evidence_cutoff+science_gates.cutoff_meta）；CSV：`results/t101_v4_a2_prescreen.csv`；
- 本件 §7 回填。

## §7 跑后实证【2026-09-29 r433 bm-a 实跑·一次定稿】

- 实跑：`python scripts/t101_v4_a2_prescreen.py` elapsed=1.7s·cells=10·evidence_cutoff=2026-09-28 实锚（探针-锚同面断言过：五员尾行全=2026-09-28）；
- **初筛判决：1 存活 / 9 判负**（survivors=1）：
  - **SURVIVE**：510050|RSV30_low<0.2（OOS 超额 +0.27%/年·Sharpe 0.394 > null_med 0.030·entries=122·maxdd -33.60%）——唯一过 4 判据格；
  - KILL 9 格主因：OOS 超额≤0（510300 −2.1%/−3.5%·510500 −2.3%/−5.2%·512100 −16.2%/−6.1%·588000 −9.7%/−12.3%·510050 RSV60 −0.6% 反号）+ maxdd 击穿 −35%（510050 RSV60 −41.7%·510500 RSV30 −38.6%·512100 RSV60 −37.3%·588000 双门 −45.2%/−50.1%）+ Sharpe≤null_med（6 格）；
- **D6 同族相关性：max|corr|=0.9424 ≥ 0.7 → REJECT（结构性 beta 同源）**——全仓门控择时与标的 B&H 日收益高度同源（vs_bh 逐对数值在 results JSON d6.vs_bh）；政体门臂的相关性来源=门控时机内嵌 beta 敞口（prereg §1 预声明的「beta 同源主险」被实测证实）；按 D6 规则既定出口：**存活格升格全量判决面前须另开预注册论证相关性来源**（门控时机的增量时机 alpha vs beta 重复——全量判决面用超额+时机贡献分解回应）；双门互 corr=gate_pair（JSON）；
- IS 面如实：IS 段超额普遍弱/负（政体依赖性确认，预测 3 命中；逐员数值在 results JSON cells.*.IS）；
- null 面：同掩码循环位移 K=200/格·seed 20308000·null_med Sharpe 全 10 格为正（+0.03~+0.13）——门掩码本身偏多头暴露，null 面已如实入对照。

## §8 批后复盘【2026-09-29 r433】

- **预测对账**：①「510500/512100 弹性大超额更大」=**错**（全面判负：中证 500/1000/科创 50 在 ETF 连续门控择时用法下=接刀亏损面）；②「RSV60 略优」=**错**（RSV60 0/5 存活 vs RSV30 1/5；OOS 超额 RSV30 优 4/5 员——60 日窗在择时用法下信号过滞）；③「IS 反号/弱」=**命中**；④「−35% 回撤界被 2015-2016 bear 段击穿」=**命中**（5 格击穿，极端日先验实证）；
- **科学结论（同门换用法判负·负结果照报）**：gate_verify 20 日前向持有验证双门 PASS ≠ 连续政体门择时策略（9/10 判负）——RSV 超卖门在「短前向窗超卖修复」有效，在「连续全仓门控择时」（T+1 开盘执行+0.1% 往返成本）判负；与 Alpha158 census「截面→时序换用法」路线对照=该路线在择时用法上反向证伪；
- 损耗账：results/gate_attrition.json 追加一行（entries 列表名 r248 律）；账本 append_ledger batch_trials=10·ledger total=337,630（跨批累计）；
- **A2 臂处置（预先承诺执行）**：9 判负格=线关闭禁换参重跑；1 存活格（510050|RSV30）=升格候选，**但 D6 REJECT 门在前**——升格全量判决面前须另开预注册论证相关性来源（beta 同源分解），未论证前不入全量判决面；A1 臂（C1 双温度计·bm-b 车道）不受本面影响照常待 bm-b 全量冻结；
- 回执入 r433 轮报告+CODELY.md 行级追加。
