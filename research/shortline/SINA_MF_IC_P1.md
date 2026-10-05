# SINA_MF_IC_P1 — sina 四档资金流「散户吸收面」首场因子参照批预注册（FROZEN·T-2026-10-05-170）

> 按 research/PREREG_TEMPLATE.md 起草；判据权=本族（P-A/P-1c/P-1d/PC_L2/THS-AGG/MF_IC_P1）冻结常数 V1/V2/V3 三线＋同掩码白噪声 null；三铁律照旧。
> 车道：dept:研究（因子参照批）｜令源：watermark next_pick **claimed**（bm-a r717 claim：moneyflow IC reference batch——EM 面板 source-blocked 53/5222 自 09-25 起，sina 面=在册唯一活资金流面）＋ bandit event-attention-factors 臂。
> 谱系：r718 廉价普查（results/sina_mf_ic_census_p1.json·TRIAL_LABOR_LAW §2 cheap-screen-first）→ **CENSUS_ENRICHED：small_share-d5 h10（t=−3.024·p=0.00043）∧ h20（t=−5.049·p=0.00007）**→ 本批=存活者参照级确认（存活者全量判决的因子参照层；策略化消费须另立预注册）。
> 性质：**因子参照批**（IC 计数入因子账本）——零引擎跑、交易员账本 N 不动、本批通过≠注册资格（PC_L2 §0 逐字）。G1'/G2 与 v2 引擎门不适用（MF_IC_P1 同律）。
> **跑前冻结**：本件 commit 后批跑件方可对真面板执行任何命令（R99 律）；跑前探针=results/_r719bma_sina_mf_ic_p1_probe.json（覆盖面事实，零 IC 零结果检视）；跑后只许回填 §7/§8。
> 认领：ticket T-2026-10-05-170 claim commit 先于本冻结 commit（THS_AGG_P1 两 commit 范式）。

## §0 批件身份【跑前冻结】

- 批名/批号：**SINA-MF-IC-P1**；批内格数（cells）=**10**＝5 面位 × 2 门控视界（h10/h20，双门控设计=两普查富集面全测，见 §1 披露）；h5=报告列不入 cells（snooping 折价声明，家族律）。
- 算力预算：单进程 <5min（5228 csv 单遍加载 ~15s＋200×2 null IC 序列 ~90s＋实格 10×(1 门控+通过者 2 报告列)~10s；O-2100 轮内短批先例）；批报告必带 audit 段；CEO CPU 余量律（单进程 BelowNormal 面已由会话壳承担）。
- 部门归属：dept:研究。
- consumer_plan（O-1820(3)）：①参照确认面——census 富集在 T+1 可交易口径+同掩码 null+位置分割下是否存续（判读入因子库素材池/诚实停泊双出口）；②若过线→P-2 式合成预注册=**新事务**（策略面+出场轴显式三选一+CN-C7 股票成本列）；③不过线→面诚实停泊（census 富集=筛选面读数非参照级证据，如实收线）。

## §0.5 禁开方向硬闸【跑前】

- `python Tools/banned_direction_gate.py --prereg research/shortline/SINA_MF_IC_P1.md` → **ADMIT rc0**（跑前实跑回执入轮报告）。
- 逐向自证：本批=资金流档位构成因子（同档行内单位自洽份额），非 BAN-01/02（ETF 截面动量/反转语义词面——本批为股票级 5111 名宽截面资金流构成面）；非 BAN-03（非单名择时，为截面因子 IC）；非 BAN-04/05/06/08（四操作性向零涉及，逐向不展开——本批为纯因子参照面）；非 BAN-07（**非 size 型因子**——因子分子分母同行同档分解，任何 size 面零使用；BAN-07 否证的是 size 因子本身，与本面构造不同构；**size 邻近性未测=消费侧警示如实披露**，见 §1）；非 BAN-09（非风格延续押注）。

## §1 α 机制段【D6 四选一】

- **机制=行为偏差（注意力拥挤/追涨吸收）**：small/散户档净流入占比高=散户群正在吸收供给（对高价/热门面的追涨足迹）→ 注意力驱动买盘在不利价位成交，后续跑输；超额来源=**追涨散户付出的价差与逆向选择成本**（被吸收方=机构/做市商收取补偿）。竞争解释=微观结构（订单流不平衡的延续面，MF_IC_P1 主力侧立论）——r718 普查已两侧同测：主力/中档族在预测方向显著反向（super_share-d5 h10 t=−4.589 预测向 p=0.99973=反向显著），本批聚焦富集的散户侧。档位语义=sina 自有四档分解（**R224/R225 官方 JS 证据链：r0=主力/r3=散户、官方聚合配方主力=r0+r1/散户=r2+r3；档名阈值 UNDOCUMENTED**；R118 禁映射 EM 律）。
- **§1.2 散户凭什么赢**：**数据+行为**——四档分解=散户人群足迹的可测数据面（典型散户不可得的档位级拆解）；行为律「散户吸收先于跑输」=可命名偏差（追涨/处置效应），本批为其形式化数值门（CEO 研究导向律 O-1522：国内民俗判据形式化）。涉机构已验证结论引用：无（本面无 RETAIL_QUANT_TRACK §三引用项）。
- **镜像构造披露（冻结）**：r0_net+r1_net+r2_net+r3_net=netamount（自洽律 1.29M 行 100% 实证）⇒ 主力群份额+散户群份额=netamount/buy_total≈净比尺——**主/群两员=近镜像，禁同批双载**：本批只载散户侧（small_share 各窗+retail_group 官方配方 r2+r3），主力侧反向显著事实=r718 普查披露在册非本批主张；net_ratio（sina 自有比列）不重载。
- **双门控视界设计披露（冻结）**：r718 普查申报格阵（6 因子×2 平滑×3 视界全 36 胞）公开报告，富集门申明于 h10 主口径 12 胞——**h10（t=−3.024）与 h20（t=−5.049）两视界同为普查申报面**；本批对两者全测=富集面全确认（h20 更强面不测=更差科学），多重检验账按 10 胞如实计。
- **同族相关性准入检查【D6·跑前冻结对清单】**（逐日横截面 Spearman，双方有效且 n≥5 对，PC_L2 逐字）：

| # | 门控对（max|corr|≥0.7 → 拒收） | 材料 | 探针实况 |
|---|---|---|---|
| 1 | vs lhb_count_20（P-A 逐字口径，去重 max-成交额行，W=20，shift1(0.0)） | Money02/data/lhb/lhb_detail.parquet | **强检查可用**（窗内 20,759 事件，2007-01-04..2026-09-30） |
| 2 | vs ths_net_ratio（THS_AGG_P1 §3 逐字） | data/ths_ggzjl/daily/ | **弱检查申报**（面板 4 文件 2026-09-24..09-30，与本批评估窗 2025-09-15..2026-09-22 **重叠 0 日**→weak_check_insufficient_coverage 如实入 audit 非跳过） |
| 3 | vs ths_net_ratio_ma5 | 同上 | 同上弱检查 |
| 4 | vs EM mf_main_net_pct_10（跨源同域面） | data/moneyflow/per/（53/5222 blocked） | **范围外申报**（隔离律 R118：sina 档位≠EM 档位同构；EM 面板 source-blocked 无有效重叠——跨源相关=实证问题待 EM 面板完备后另批，本批不量不猜） |

- **size 邻近性警示（BAN-07 邻域·非判据面）**：散户档占比可能与 size 面经济相关（未测）；本批无 size 列、不做 size 声明——消费侧若策略化须在新预注册带 size 控制面（ADV/size 分层稳健性），如实披露非跳过。

## §2 数据与面板【跑前探针事实，非结果——探针=results/_r719bma_sina_mf_ic_p1_probe.json】

- **价格面（G-ANCHOR 四元组）**：`Money02/data/cache/p1c_stock`＋`np.load dates.npy(us-epoch)/close.npy memmap`+bars parquet roster（r717 谱系加载）＋1990-12-19 全史起算＋评估窗自 2025-09-15（sina 最早行）——**T=8792·N=5222·cutoff=2026-09-22**（dates.npy=微秒 r717 钉律）。close **不 ffill**：停牌名 NaN=掩码排除（普查律，严于 harness ffill 口径）。前向锁盒 D2：cutoff 后新 bar 禁回流（sina 尾行 2026-09-23/24=10,444 行不可消费，探针在册）。
- **因子面（G-ANCHOR 四元组）**：`data/sina_mf/per/*.csv`＋`pd.read_csv usecols`（普查加载器逐字）＋每股 ~250td 滚动窗（2025-09-15 起）＋d5 min_periods=3→首可判 2025-09-18（shift1 后）/d20 min_periods=12→2025-10-09。面板自洽律（|netamount−Σr\*_net|≤1e-3 相对）：**1,294,199/1,294,199 行 100%**（探针实读）。sina-only 6 新股结构性排除（不入 p1c 宇宙）。
- **完备门（跑批前置，不过门诚实 exit 2）**：sina 文件 ≥5,000 ∧ 小股东 d5@h10 资格日 ≥150 ∧ IS≥100∧OOS≥30（位置分割）。探针实读：5,228 文件/235 资格日（width 门 1,000 下）/IS 156·OOS 79——**过门预期成立**（跑时实读为准）。
- **截面宽门=1,000 名**（家族常数 MF_IC_P1 WIDTH_GATE）：探针中位 5,108–5,112 名/日（p25≈5,102），全窗无窄段——门三候选 {300,500,1000} 资格日数恒等（235/235/235）=门不约束本批（如实注记）。
- **D6 材料锚**：lhb parquet（2007-01-04..2026-09-30·窗内 20,759 事件）；ths daily（2026-09-24..09-30·4 文件·窗内 0 日=弱检查）。

## §3 方法学【冻结】

- **因子定义（5 面位，全部冻结；单位自洽=同行同档分解任何公共量纲因子相消）**：small_share=r3_net/(r0+r1+r2+r3)（分母=同行四档买入和）×窗 {d1,d5,d10,d20}；retail_group_share_d5=(r2_net+r3_net)/买入和×d5（**官方聚合配方 R225 律：散户=r2+r3**）。平滑=日历格 trailing 均值，min_periods=**ceil(0.6×w)**（d1=1 原始/d5=3=普查面逐字/d10=6/d20=12——60% 覆盖率统一律，d5 位与普查富集面恒等保连续性）。
- **信号位 shift1=T+1 严格滞后**（家族律：资金流日线=盘后终值→因子位 T+1；**普查为同日口径=乐观面，本批为可交易口径——两者差异如实披露，普查读数不构成本批预期上限**）。
- IC=Spearman 逐日横截面（**先掩码后排名**，J7 坑律；复用 shortline_p1_ic._ic_series_fast——唯一 IC 方法学，等价自检门在册；统计块=composite_ic.stats_block≥30 期地板）。掩码=单一 A（因子有效∧fwd 有效∧截面宽≥1,000）；fwd_h=close[t+h]/close[t]−1。
- **null 对照（三铁律一）**：K=200×2 视界同掩码白噪声（逐日重抽=与实因子同重叠结构，null 线内含 fwd 重叠效应——普查朴素 t 的重叠膨胀由此正法吸收）；h10 带=rng(58_700+k)·h20 带=rng(58_800+k)，k<200；IS 段统计取 p95|IC|/p95|IR|。**SEED_REGISTRY 新键 `sina_mf_ic_p1`=58_700（带 58_700..58_999，rg 全仓扫描零 RNG 命中 2026-10-05 09:5x——唯一命中=期货成交量/ETF 码 588000 等数据文件数字巧合非 RNG，t34 先例；注册随本冻结 commit·R250 一步律）**。
- **成本口径**：因子参照批零引擎——成本不适用（声明）；策略化消费须全新预注册＋CN-C7 股票面往返 bp 申报（fee_schedule_for 前缀路由）＋V1/V2 压测。
- **账本**：`science_gates.append_ledger(batch_name='sina_mf_ic_p1', batch_trials=10, file_name='results/shortline/sina_mf_ic_p1.json', evidence_cutoff='2026-09-22')`（dict schema 唯一禁手抄 prev）；IC 计数=10 胞+400 null 入因子账本，引擎账本 N 不动。
- **闭合族对号【M3】**：family_key=**sina_mf_tier_ic**（新族，CLOSED_FAMILIES 九键零命中=open 照跑；`science_gates.closed_family_check` 跑前过闸）。
- **出场轴显式门【TRIAL_LABOR_LAW §4·必答】**：本批=因子参照批**零引擎零出场面——出场轴不适用（N/A by construction）**；§0 consumer_plan 已声明策略化消费须另立预注册且届时三选一显式声明（①策略自有出场/②持有到底+runner 禁用缺省栈/③template_default），无声明=新预注册冻结门拒。

## §4 判据【跑前写死，禁看结果调线】

- **门控视界=h10 ∧ h20 双门**（双门控设计披露 §1）；h5=通过者报告列。
- **V1**=|IS IC| > max(0.02, null p95|IC|)；**V2**=|IS IC_IR| ≥ 0.30；**V3**=OOS 同号 ∧ |OOS IC| ≥ 0.5×|IS IC|（本族 P-A/P-1c/P-1d/PC_L2/THS-AGG/MF_IC_P1 冻结常数逐字）。
- 期间门：IS n≥100 ∧ OOS n≥30（位置分割 2/3，分割边界日随跑时冻结入 audit）；资格日截面宽门 1,000。
- **pass=V1∧V2∧V3∧期间门**；全门=描述性参照判据，通过者仅入因子库素材池（带「T+1 口径·~250td 短窗·市值邻近未测」三折价标签），禁直接注册禁策略化直接使用。
- **M1 t 面【D-20260930-37 必答】**：每胞报 IS 段朴素 one-sample t（因子面直接面），判据=`science_gates.m1_t_value_gate`（Harvey/Liu/Zhu **|t|≥3.0**）；**重叠视界膨胀警示如实载**（h20 逐日 IC 序列相邻日共享 19/20 收益窗，朴素 t 高估显著；null 校准 V1 线=本批主判线，M1 面为 claimable 层额外披露非替代）；M1 过=「可主张层」标记，不过=如实标 below_hlz_line。
- **§1.3 全起点分布**：因子参照批无多起点语义（单一面板单一起点）——**不适用申报**（策略面消费时在新预注册补）。
- D6 门：lhb 对 max|corr|≥0.7 → d6_reject；ths 两对=弱检查声明（audit 载 days=0）；跑后禁令照旧（禁调门槛/禁换口径/禁加格重跑；失败=失败诚实收线）。

## §5 跑前预测【写死于跑前·跑后对账】

1. **T+1 漂移**：d5 平滑因子日度缓变→shift1 漂移温和；方向（散户吸收→跑输，负 IC）存续概率 ≥80%。
2. **h10 面**：|IS IC| ∈ [0.012, 0.020] → **V1 地板 0.02 主导大概率 FAIL**；IR ∈ [0.12, 0.22] < 0.30 → V2 大概率 FAIL（普查同日面 0.0184/0.197 为上界参照）。
3. **h20 面=判决主面**：|IS IC| ∈ [0.024, 0.038] → V1 过线概率 ~70%（地板 0.02 主导）；IR ∈ [0.28, 0.40] → V2 边缘（普查 0.336）；**V3 OOS 留存=决定门，五五开**（2026 政体 OOS 段 ~79 日的留存风险如实）。
4. **null 线**：5,111 名宽截面下 p95|IC| h10 ≈ [0.003, 0.008]·h20 ≈ [0.005, 0.012] → **V1_FLOOR=0.02 双视界地板主导概率 ~90%**（THS §5④ 同构）。
5. **窗族单调性**：|IC| 随平滑窗单调增（d1≪d5<d10≤d20，普查 d1/d5 面在册）；d20@h20 为窗族最强候选但 min_periods=12 预热丢 15 日→期间门边缘风险如实。
6. **retail_group_d5 ≈ small_share_d5**（r2 增量噪声，同向高相关）→判读趋同；两员同批=官方配方载面非镜像重复（镜像律 §1 主/散侧只载一）。
7. **D6**：vs lhb corr ∈ [0.05, 0.30]（注意力族 PC_L2 带先验）→ok；全族 d6_reject 概率 ~10%。
8. **M1**：h20 胞 IS 朴素 t ∈ [3.0, 5.5]（普查全窗 −5.049·IS 段折减 ~√(156/226)）→d5/d20 面可主张层有戏；**重叠膨胀警示=读数时以 null 校准线为准绳**。
9. **极端日先验**（§4 硬界三件套 (c)）：评估窗 2025-09-15..2026-09-22 含 2026-01-19 深度回撤/2026-04-07 关税冲击族极端微观结构日（大面积单日同向流→单日 IC 尖峰）；本批判线=均值/IR 型无单点 max 硬界（家族声明）——audit 带各胞 IC 序列五数概括供事后检视。

## §6 产物

- 脚本：`scripts/sina_mf_ic_p1.py`（run/selftest 两子命令；run 完备门未达=诚实 exit 2；selftest=hermetic 合成面板离线自检 tmp 沙箱零真数据依赖，复用件=_ic_series_fast/stats_block/science_gates 导入零重写）。
- 结果：`results/shortline/sina_mf_ic_p1.json`（顶层 science_gates.cutoff_meta=cutoff 2026-09-22；audit 段含 seed/掩码/截面宽分布/资格日排除计数/D6 对清单读数+弱检查声明/IS-OOS 分割边界日/IC 五数概括/M1 t 面/ledger 声明）＋`research/shortline/sina_mf_ic_p1_results.csv`＋本件 §7 回填。
- 幂等：同机同数据复跑数字逐位相同（全确定性 rng）。

## §7 跑后实证【跑前必须为空——写数字即造假】

（占位：批跑后一次定稿回填。）

## §8 批后复盘【必填·s7-T】

（占位：预测对账＋门禁链损耗账（results/gate_attrition.json 追加 SINA-MF-IC-P1 行）＋判线当批读数（null p95|IC| 双视界数字）＋回执入轮报告与 CODELY.md。）
