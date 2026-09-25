# MF_IC_P1 — EM 主力资金流面板 首场因子参照批预注册（T-2026-09-25-46 slice-1）

> 按 research/PREREG_TEMPLATE.md 起草；判据权=BACKTEST_SCIENCE.md v2 族冻结常数；三铁律照旧（随机基线+样本外盲+成本恒开）。
> 车道：dept:研究（因子参照批）｜令源：QUEUE_BANDIT event-attention-factors 臂 open 候选（R58 点名 mf_main_net_5/10/20·MF_COLLECTOR §4 第 2 腿·O-1620 GM 已批资金流域内）｜S3 水位 next_pick advisory 面（O-1819 队列永不清空）。
> 认领：**commit 2c0958bd（claim lock，先于本件）**＋MSG-20260925-0810（F-04 先行声明）；票 T-2026-09-25-46（bm-b）。
> 性质：**因子参照批**（IC 计数入因子账本）——零引擎跑、交易员账本 N 不动、本批通过≠注册资格（PC_L2 §0 逐字）。判据口径声明：G1'/G2 与 v2 引擎门不适用；判据=本族（P-A/P-1c/P-1d/PC_L2/THS-AGG）冻结常数 V1/V2/V3 三线+同掩码 K=50 null（§4 逐字冻结，recorded constants），跑后禁调线禁换口径。
> **跑前冻结**：本件 commit 后批跑件方可对真面板执行任何命令（R99 律）；跑后只许回填 §7/§8。

## §0 批件身份【跑前冻结】

- 批名/批号：**MF-IC-P1**；批内格数（cells）=**5**（h10 门控面：mf_main_net_pct_5/10/20 + mf_xl_net_pct_10/20）；h5/h20=报告列不入 cells（snooping 折价声明）。
- 算力预算：评估批 <2min 纯 CPU 单进程（≤5,222 股×≤150 有效日面板 IC 向量化；THS B 相同型轻批，不入 runnable_pool）；批报告必带 audit 段（无 audit 段不入账本）。
- 车道裁决（冻结）：①判据/脚本/预注册=bm-b 本轮交付；②采集面=**零触**（update_moneyflow.py=bm-a T-39 车道一字不动，R31 判例）；③bandit 候选登记面翻格=MSG-20260925-0810 请求 bm-a（queue 单写者车道，r119 请求制律）；④批跑门=面板完备（§2 完备门），执行机=持完备面板机（数据局部性；bm-a 面板先完备且本机不可得→按 T-29/T-32 yield 惯例让渡执行，判据零字节改动）。

## §1 α 机制段【D6——四选一】

**机制=微观结构（订单流不平衡）**。EM 主力净流入=超大单+大单主动买卖差；`主力净流入-净占比`=大单订单流不平衡占成交额强度，是订单流不平衡的直接可观测代理（THS_AGG_P1 §1 同构立论）。超额来源：不平衡的主动大单由挂单流动性提供方吸收，吸收方为此收取价差与逆向选择补偿；短窗内不平衡携带价格压力延续信息，**由追单方付出价差成本**。竞争解释=行为偏差（注意力拥挤反转，PC_L2 读法）——本批为参照批=两侧竞争实测，不以行为面立论。

**镜像构造披露（冻结）**：EM 四桶净占比恒等 `主力+中单+小单=0`（每笔成交买卖双方金额守恒、按主动侧归类）→ 中单/小单净占比=主力净占比的镜像列；补镜像因子=重复计权，**禁入本批**；后续任何镜像因子须另开预注册。

**同族相关性准入检查【D6·跑前冻结对清单】**：B 相评估时逐日横截面 Spearman corr（双方有效且 n≥5 对，PC_L2 逐字口径）：

| # | 门控对（max|corr|≥0.7 → 拒收） | 定义 |
|---|---|---|
| 1 | vs ths_net_ratio | THS 全单聚合不平衡率（净额(元)/成交额(元)，THS_AGG_P1 §3 逐字；材料=data/ths_ggzjl/daily/） |
| 2 | vs ths_net_ratio_ma5 | 上式 5 日滚动均值 |
| 3 | vs lhb_count_20 | LHB 20 日上榜计数（去重 max-成交额行、shift1，P-A 逐字口径；PC_L2 同构；材料=Money02/data/lhb/lhb_detail.parquet） |

- `max|corr| ≥ 0.7` → **该因子 d6_reject**（同源订单流/注意力冗余，防 N 膨涨；确有新机制主张须另开预注册论证）；对照面材料不在执行机或同日有效重叠 <30 日=**弱检查声明**如实入 audit 非跳过（PC_L2 §5 逐字）；对 1/2 的解析消费=THS_B 相脚本车道（bm-a），本件脚本仅读取其面板原始面（万/亿后缀解析器内嵌于本脚本 D6 腿，只读不改其库）。

## §2 数据与面板【跑前探针事实，非结果】

- 面板：`data/moneyflow/per/<code>.csv`（date+12 值列中文列名冻结，MF_COLLECTOR §1 schema 零改动；append-only；gitignored 机本地可再生）。
- 宇宙：bars 静态快照 5,222 只（后续 IPO 缺席如实披露，P-1c §2 同口径）；面板采集宇宙=rank 5,920∩bars 5,222 join（非 bars 诚实 skipped_not_in_universe 计数）。
- **窗语义（诚实三面）**：①v1 daykline 遗产=53 股 ≤120td 史（源 120 交易日/股滚动窗硬顶，R58 定案：lmt=0 也被源静默截断）；②v2 rank 面=纯前向日频自 2026-09-24 起（横截面无回看）；③**2026-04 前历史结构性不存在**（源窗左沿 2026-04-02 级）。
- **120d 源窗披露条款（MF_COLLECTOR §4 逐字）**：本批为**短窗参照批**，有效信号日 ≤~150 量级，**禁与全史批同口径比较**（P-1c IS n≈8,000 vs 本批；一切读数带此折价）。
- 评估窗（触发式冻结，THS_AGG_P1 §2 逐字）：**信号日资格门=当日 A 掩码截面宽 n≥1,000**（≈19% 宇宙；53-股 daykline 遗产窄段自动排除=窄截面 IC 噪声污染防御，排除日计数入 audit）；**IS=资格日序前 ⌊2/3·N⌋ 日、OOS=余 1/3**（位置分割，分割边界日随跑时数据冻结入结果 audit）；期间门 IS≥100 ∧ OOS≥30（PC_L2/THS 逐字）。
- evidence_cutoff：批跑时冻结=当时面板末位完整 bar 日（前向锁盒 D2）；结果 JSON 顶层必带 `science_gates.cutoff_meta`（缺字段=science_audit C2 VIOLATION）。
- 前瞻收益面（冻结）：Money02 bars 前复权 close（P-1c §2.1 裁定口径=bars 价格已前复权）；fwd_h=close[t+h]/close[t]−1；评估窗短→脚本直读 bars 尾段（无全史缓存依赖）；**面板价格列禁作行情消费**（MF_COLLECTOR §1 逐字：收盘价列复权口径不保证）。
- **完备门（跑批前置，不过门禁跑批=诚实 exit 2）**：`results/moneyflow_update_status.json` panel.complete=true ∧ panel n_symbols≥5,000 ∧ 资格信号日 N≥150（=期间门 2/3 分割的超集：N=150→IS 100/OOS 50）。当前实况（2026-09-25 08:0x）：complete=false、n_symbols=53、mode=refresh source-blocked（conn 级 3 连断，bm-a T-39 车道 30min 自愈在飞）→ **批合法等待**。

## §3 方法学【冻结】

- 因子定义（5 个，全部冻结；信号位 **shift1=T+1 严格滞后**，EM 资金流日线=盘后终值→因子位 T+1，P-A/MF_COLLECTOR §3 同构最保守口径）：

| # | 因子 | 定义（面板列上，min_periods=窗宽严格满窗） |
|---|---|---|
| 1 | `mf_main_net_pct_5` | `主力净流入-净占比` 5 日滚动均值 |
| 2 | `mf_main_net_pct_10` | 同上 10 日（**主口径因子**） |
| 3 | `mf_main_net_pct_20` | 同上 20 日 |
| 4 | `mf_xl_net_pct_10` | `超大单净流入-净占比` 10 日滚动均值 |
| 5 | `mf_xl_net_pct_20` | 同上 20 日 |

- IC=Spearman，**先掩码后排名**（J7 坑律；复用 `pa_lhb_ic.rank_rows/ic_from_ranks/fwd_ret` 与 `composite_ic.stats_block` 逐字，禁重写）。掩码=单一 A（因子有效 ∧ fwd10 有效 ∧ bars close 有效）∧ 截面宽门。
- null：**K=50 同掩码白噪声**，rng(58_500+k)，seed 基=**58_500**（新族 `mf_ic_p1` 与本件同 freeze commit 登记 SEED_REGISTRY；band 58_500-58_549 全仓 rg 扫描零占用 2026-09-25 08:0x——im_ic_pair 58_000 带外、p4_batch3_dca 56_500 间距先例）；IS 段统计取 p95|IC| 与 p95|IR|。
- 成本口径：因子参照批零引擎——交易成本不适用（声明）；任何策略化消费须全新预注册＋成本压测（V1/V2 按届时口径）。
- 账本：跑批时 `science_gates.append_ledger(batch_name='mf_ic_p1', batch_trials=5, file_name='results/shortline/mf_ic_p1.json', evidence_cutoff=...)`（dict schema 唯一，禁手抄 prev）；IC 计数=5 因子+50 null 入因子账本，引擎账本 N 不动。

## §4 判据【跑前写死，禁看结果调线】

- **h=10 唯一门控**；h5/h20=报告列（passers only，非门控，snooping 折价声明照旧）。
- V1 = |IS IC| > max(0.02, null p95|IC|)；V2 = |IS IC_IR| ≥ 0.30；V3 = OOS 同号 且 |OOS IC| ≥ 0.5×|IS IC|（本族 P-A/P-1c/P-1d/PC_L2/THS-AGG 冻结常数逐字）。
- 期间门：IS n_periods ≥ 100 且 OOS n_periods ≥ 30；资格日截面宽门（§2）。
- pass = V1∧V2∧V3∧期间门；**全门=描述性参照判据**，通过者仅入因子库素材池（带 120d 短窗折价标签），禁直接注册禁策略化直接使用。
- D6 §1 三对门控，max|corr|≥0.7 → d6_reject；重叠 <30 日或材料缺席=弱检查声明。
- 跑后禁令：禁调门槛/禁换口径/禁加因子重跑；失败=失败，诚实收线。

## §5 跑前预测【≥3 条＋极端日先验，写死于跑前】

1. 方向两侧竞争（压力延续 vs 拥挤反转）无强先验；主口径 mf_main_net_pct_10 |IS IC| 落 **[0.005, 0.03]**，过 V1 概率 ~50%（THS §5① 同构）。
2. 窗宽 5→20 单调衰减概率 60%（流量信号短半衰期先验）；**反向例外披露**：若 20d 反强=PC_L2「该域信号在慢速档」再现，读数时如实对账。
3. 超大单族强度 ≥ 主力族概率 55%（更纯机构足迹；主力含大单噪声稀释）。
4. D6 主风险面：vs ths_net corr 0.4-0.7 概率 70%（同源订单流、聚合桶含主力桶，THS §5③ 镜像）；vs lhb_count_20 corr 0.2-0.5（PC_L2 实测 0.28-0.55 同带先验）；max|corr|≥0.7 全因子拒收概率 ~35%——**拒收=合理收线非失败**（冗余证据亦为收线成果，THS §5③ 逐字）。
5. null p95|IC| ≈0.01-0.02，宽截面（≥1,000 名/日）下 **V1_FLOOR=0.02 地板主导概率 80%**（THS §5④ 同构）。
6. IC_IR |IR|≥0.30=预期约束瓶颈（PC_L2 0/4 同型：宽宇宙日频 IC 信噪低；THS §5⑤ 同构）。
7. **极端日先验**：评估窗整体落 2026 政体（ORANGE，hs300<MA200 当前态、breadth 0.77）；窗内极端微观结构日形态=单日大面积同向流（恐慌抛售/政策日脉冲）→ 主力净占比截面离散度骤扩、单日 IC 尖峰；本批判线为均值/IR 型**无单点 max 硬界**（硬界设计三件套 (a)(b) 对 IC 参照批不适用，如实声明）；极端日对 IS IC 均值的杠杆风险=少数极端日可搬运均值，audit 段带各因子 IC 序列五数概括（min/q25/median/q75/max）供事后检视。

## §6 产物

- 脚本：`scripts/mf_ic_p1.py`（run/selftest 两子命令；**run 完备门未达=诚实 exit 2 禁跑**（面板 blocked 态原样上报勿掩盖）；selftest=hermetic 合成面板+bars 离线自检（tmp 沙箱零真数据依赖，r116 hermetic 律），复用件=pa_lhb_ic/composite_ic/science_gates 导入零重写）。
- 结果：`results/shortline/mf_ic_p1.json`（顶层 `science_gates.cutoff_meta`；audit 段含 seed/掩码/截面宽分布/资格日排除计数/D6 对清单读数+弱检查声明/IS-OOS 分割边界日/IC 五数概括/ledger 声明）＋`research/shortline/mf_ic_p1_results.csv`＋本件 §7 回填。
- 幂等：同机同数据复跑数字逐位相同（全确定性 rng，PC_L2 §8 逐字）。

## §7 跑后实证【跑前必须为空——写数字即造假】

（占位：批跑后一次定稿回填——判线实况/逐因子 V1/V2/V3/期间门/D6 读数/机制判读/处置。）

## §8 批后复盘【必填·s7-T】

（占位：预测对账（对/部分/错）＋门禁链损耗账（`results/gate_attrition.json` 追加 MF-IC-P1 行）＋判线当批读数（null p95|IC| 数字）＋回执入轮报告与 CODELY.md。）
