# N2-MP1 预注册（素材池消费批 wave-1）——**FROZEN v1.0（2026-10-11 bm-b r868 冻结窗·五条件门全绿证链）**

> **FROZEN v1.0 五条件证链（r868）**：①selftest 复跑——`scripts/mp1_tsgate_probe.py selftest` **30/30 PASS**（七腿 hermetic：parser round-trip 96 池式全过+逐算子手树、t23.evaluate 单标的手值〔DELTA/MA/CORR 数值断言+CSRANK 单标的常量退化〕、门构造 decidable 律+NaN 伪影禁用+常数序列边界不开、统计腿 IS/OOS 切分+成本+stride+判定四态、确定性双跑恒等、G-ANCHOR-MP1 实数据锚 3341/390/149 复现+G-PANEL/G-CUTOFF+shard 分割、refuse-if-exists 幂等）；②数据完备门 probe 复跑——`results/_r867bmb_mp1_draft_probe.json` 复跑实证 pool 96/96 跨波 overlap=0·CSRANK 7 排除·可算 89·178 门·E[FP]=8.9·面板五员 cutoff 2026-10-09 同面；③banned_direction_gate --prereg 本件 **ADMIT rc0 matched=[]**（回执 results/_r868bmb_banned_gate.txt·随冻结 commit）；④origin 写前复核——git show origin/main:research/N2_MP1_PREREG.md=DRAFT 态（HEAD=origin tip 零漂移）；⑤状态翻面 FROZEN 与 runner 交付（scripts/mp1_tsgate_probe.py）+checkpoint gitignore 面**同 commit**。冻结后禁改 §0-§6 判据面；跑后只回填 §7/§8，要改判据要重跑。

> 模板=research/PREREG_TEMPLATE.md 结构镜像（§0-§8）；批型=**判别力探针/供应普查**（gate_census→gate_verify 血统·A158-TSGATE-P1 逐字先例）——**非策略回测批**：G1'v2/G2v2 机械面不适用（无策略收益序列·§4 如实申报），判读线=gate_verify 三控判线逐字镜像（A158-TSGATE-P1 §3 同源）；跑前 commit 冻结；跑后只回填 §7/§8，要改判据要重跑。
> 通道/谱系授权=W19 §8+W20 §8 消费侧指针（**「任何消费（输入特征路线/注册面）须全新预注册+成本压测·A158-TSGATE-P1/A10 先例门」**未关线）+W20 §0 素材池消费评估窗 **≤2026-10-13**（独立轨道）+TRIAL_LABOR_LAW §1 常设线（板空/池饿=默认供料）+O-1819 队列永不清空；tech.md **T24 行**（r867 登记·queue_seed_gate rc0 hits=[] status=open）。
> 消费对象=**N2 因子素材池 96 存活员**（W19 48+W20 48·TREASURE_REGISTRY 2026-10-11 两行在册·带波次血统标签+120d 短窗折价族级校准标签）——本批=池的**首次消费**；池成员已在 W19/W20 波入账（试验账本不重复入账·§3）。
> 统摄律：BACKTEST_SCIENCE.md v2 + COMPUTE_AUDIT.md 批件纪律 + pit-95/r431 decidable 掩码律 + r433 同门换用法判例（截面/时序两用法=独立假设独立判决不互相翻案）+O-20260925-1105 例外三问（judged face 另开票）。

## §0 批件身份【跑前填·冻结时核】

- 批名/批号：**N2-MP1**（素材池消费批 wave-1·时序分位门换用法普查面）。非试验账本批（marks +0·SEED +0·零 rng 消费=**无种子带登记面**——96 式全部冻结在案+门机械确定性，无任何随机绘制；冻结窗=跑前 commit 冻结+状态翻面，无 SEED_REGISTRY 三带步）。
- 批性质：**判别力探针/供应普查**——测量「素材池成员在 ETF/基金面板单标的时序分位门用法下对 20 日前瞻收益有无净差判别力」；PASS 仅获独立复核资格，零注册效力（A158-TSGATE-P1 分诊语义逐字）。
- **出场轴显式声明（三选一·如实申报）**：本批=探针批无持仓无模拟无出场事件——**不适用**（测量面豁免论证·A158-TSGATE-P1 同构：无策略收益序列/无 trade 流）。runner 无引擎调用面=构造性保证（纯统计机械）。
- 认领：tech.md T24 行（r867 bm-b 登记+同轮认领）；lane-free（素材池=W19/W20 波均 bm-b 产出·本机血缘最近·他机健康可烧不拦）。
- 部门归属：dept:研究。
- **consumer_plan（O-1820(3) 必填）**：PASS 门→gate_verify 式独立复核资格（下一关·独立 OOS 复核+D6 邻接审计）→T-101 v4 政体门候选臂库（A158-TSGATE-P1 §8 同构通道）；PARTIAL 门→C1 输入特征候选清单（gate_verify PARTIAL 降格先例）；FAIL=该池员时序门用法关线（合法产出·与截面 IC 参照面互为独立假设）。次级消费：T-74 L5 仓位阶梯特征面。
- 算力预算：本地 CPU 确定性普查——178 门 × 1,013 工具（MIN_BARS=500 面）估单机串行 ~4-8min（A158-TSGATE-P1 314 门 ~6min 实测同机械量级缩放）→**池批面**（>120s 短批帽）：入池 `results/runnable_pool.json` 条目 `N2-MP1`（lane_owner=null·workers 并行 BelowNormal·O-2130 多核律）；autofill 续烧合法。
- 意义审计三验：①可判负假设（门判别力 OOS 净差不显著=关线·预期多数门 FAIL=合法产出）✓；②指名消费面（上文 consumer_plan）✓；③判负处置预案（FAIL=关线照报·PARTIAL=降格输入特征·全 FAIL=池时序门用法面整体关线=素材池消费轨道 wave-1 负收口，注册面通道另议）✓。

## §0.5 禁开方向硬闸【冻结窗跑】

- 冻结 commit 前必过：`python Tools/banned_direction_gate.py --prereg research/N2_MP1_PREREG.md` 退出 0（decision=ADMIT·matched=[]·registry_version=v1.0）。
- 本批正文不引任何禁向词面（换用法普查面·零新策略宣称·条件化极端态门=A158-TSGATE-P1 判例面非 BAN-03 族短窗反转/动量策略面）；r867 起草窗实跑初版曾误触 BAN-03 「日内」子串（CSRANK 语义描述「截日内跨股票排名」措辞碰撞·非禁向宣称）=词面误触已改正文措辞（「按日期截面跨股票排名」），如冻结窗再命中外来词面按 missing_fields 补例外三件套（r494 合同律）禁绕闸。

## §1 α 机制段【四选一+D6】

- **[x] 微观结构**（主·素材池公式树=价量微观结构代理面·W19/W20 §1 血统照携）——**行为偏差**（辅）：单标的 252 日分位极端态=过度反应/恐慌态识别面（「超跌反弹」vs「急跌不接飞刀」族内方向矛盾在册=条件化门价值主张而非方向宣称·A158-TSGATE-P1 §1 逐字）；**风险源价**：极端态逆势接刀者/恐慌跟随者。
- **D6 同族相关性准入（邻接披露·本批为普查面无注册轴·A158-TSGATE-P1 同构）**：
  - ①**换用法独立假设（r433 判例逐字）**：素材员在 A 股截面 IC 参照面存活（W19/W19 族判线）≠ETF 单标的时序门判别力——两用法独立假设独立判决，本批读数不借截面 IC 面翻案、截面面亦不借本面。
  - ②**选择偏差披露（本批特有·诚实先验）**：96 员非公式空间随机样本=按截面 |ICIR| 存活选出（W19/W20 波 T-84s3 去重源排除后存活面）→时序门面读数携选择偏差先验；本批判读线（gate_verify 三控）不因此调整，族级多重检验税按**本批实际检验面 N=178 门**计（非按公式空间大小计）。
  - ③A158-TSGATE-P1 PASS 门族（STD20_q90/RSQR20_q90 等=A158 固定清单语法）与本批池公式（公式树自由表达式语法）**语法面不同源**——两批门名零撞（A158 名单 <因子名>_q90 vs 本批 <树指纹>_q90·命名空间隔离）；ROC20_q10 门=A158-TSGATE-P1 面 FAIL 在册——本池 96 式无 ROC 构造（r867 探针 leaves_used 面可验）=零撞如实注记。
- **散户凭什么赢【§1.2】**：本批=探针批无直接交易面（可交易账户面=core48 ETF/基金白名单·只做多——池公式=股票截面出身，r840 L2 已裁定不可直接策略化）；可用消费=v4 政体门候选臂/输入特征（consumer_plan），PASS 也只获独立复核资格。答不出直接赢面=如实申报非批不受理项（探针批豁免论证·冻结窗核）。

## §2 数据与面板【跑前探针事实·G-ANCHOR-FACE 四元组律·r867 起草探针实测】

- 宇宙/池：**全面板 data/daily/*.csv（ETF/基金面板·1,724 码·本机在位实证 r867 探针）·MIN_BARS=500 入样（gate_verify 逐字）→ 1,013 工具**（r867 探针实测=与 A158-TSGATE-P1 §7 漏斗同面同数）；五员冻结宇宙（O-1555）{510300,510050,510500,512100,588000}=次级描述面。
- **evidence_cutoff=2026-10-09**（面板当前真值：五员末 bar 全=2026-10-09·全面板 last_date ≤2026-10-09 实证；W19/W20/census 同刻）：面板一律先截断到 cutoff（截断后 510300=3,490 行·2012-05-28→2026-10-09）；结果 JSON 顶层 `science_gates.cutoff_meta("2026-10-09")`（C2 缺字段=VIOLATION）。
- **因子库=素材池 96 式 → 可算子集 89 式**（r867 探针实测）：**7 式含 CSRANK（截面算子·沿 axis1=按日期截面跨股票排名）单工具时序面不可算=诚实排除如实披露**（探针实证：[n_dates,1] 面单一常量退化·n_unique=1）；排除面零代烧零判读（不进 178 门）。池读数：96 员=48+48·跨波 overlap=0（T-84s3 构造性零交·r867 探针复核）；M1 正方向 t≥3.0 候选带 9 员（W19 波）**全在可算子集**（r867 探针 m1_positive_computable 面逐式在册）。
- **leaf 构造逐字镜像 t23**（单标的 [n_dates,1] 面）：VWAP=AMOUNT/VOLUME·RET=CLOSE/prev−1·WARMUP=61（t23 L89 同值）；面板列 date/open/high/low/close/volume/amount（r867 探针实测·amount 列在位）。
- **门定义（冻结·A158-TSGATE-P1 逐字）**：每式两侧——低分位门 `f < f.rolling(252,min_periods=120).quantile(0.10)`；高分位门 `f > …(0.90)`→**178 门**。decidable 掩码=f.notna()∧qref.notna()（pit-95/r431）；预热窗 gate-closed 诚实。
- **前瞻收益**：h=20（消费面=v4 政体门 20 日族·gate_verify 同口径）：`fwd = close.shift(-21)/close.shift(-1) − 1`（信号日收盘信息集·T+1 次日收盘买·持有 20 日·无未来数据）。
- **数据锚面四元组**：510300 锚=（①data/daily/sh510300.csv ②pd.read_csv 直读 ③全史起算 2012-05-28 ④预热窗 252/min_periods=120+DELTA30→首可判 bar-idx==149）——**G-ANCHOR-MP1（新锚·r867 探针逐位）**：`DELTA(VOLUME,30)_q10` @510300：**decidable==3341 ∧ open==390 ∧ 首可判 bar-idx==149**（r867 起草探针只读读数·in-run fail-closed 复现·锚式=池员最强 |h1_ic_ir| 可算员）。
- 数据完备门（fail-closed，不过即 VOID 拒烧）：**G-PANEL**（csv 数≥1,500·五员全在位）+ **G-CUTOFF**（截断后五员末行≤2026-10-09·510300 截断行数==3,490）+ **G-ANCHOR-MP1**（上三元组逐位）+ **G-FACTORS**（89 式全序列非全 NaN·每式≥1 工具 decidable≥500）——runner 探针与锚**强制同面断言**（探针加载路径与锚声明路径逐位比对·一面不相符=配置错配 VOID 拒烧）。

## §3 方法论【冻结】

- 判别力统计（**A158-TSGATE-P1 §3 逐字镜像**·gate_verify 血统）：分段 IS≤2016-12-31 / OOS≥2017-01-01；每工具每段门事件≥15（MIN_EV=15）；门内/门外 20 日前瞻均差=diff；**diff_net=diff−0.10% 往返成本**（ETF 保守值）；**不重叠控制=stride-20 双组内抽稀**（thin(pin)/thin(pout)→diff_net_thin）；每工具每段 t=Welch 双样本。**桶定义（pit-95/r431 严口径）**：in=open∧decidable∧fwd 有效；out=（¬open）∧decidable∧fwd 有效——两桶均 AND decidable。
- 聚合（每门）：全面板 per-inst 中位 diff_net（IS/OOS）+正份额 pos_share（OOS）+中位 t（IS/OOS）+中位 diff_net_thin（OOS）+|t|>2 工具占比；五员次级面逐员读数表；**波次血统标签分组披露**（W19 员门 vs W20 员门两组计数——消费面读数按池血统可溯）。
- **判读线（跑前写死·gate_verify 逐字·A158-TSGATE-P1 同线）**：`PASS = OOS med diff_net>0 ∧ pos_share≥0.55 ∧ IS med diff_net>0`；`PARTIAL = OOS med diff_net>0`；`FAIL = else`；`N/A = OOS n_inst<30`。分层闸语义=普查→候选资格分诊，**非策略宣称**。
- **多重检验税披露（O-2245 精神）**：N_gates=178·E[FP]=0.05×178=**8.9 门**量级预期假阳——PASS 门升格 v4 候选前必过独立复核面（D6 邻接审计+独立 OOS 复核），普查面零注册效力。
- 幂等：结果件在位=refuse 重跑（refuse-if-exists）；确定性双跑字节恒等（selftest 腿·唯一运行时元数据=generated/elapsed 独立段）；checkpoint=per-shard jsonl 断点续跑（跨机 kill 复活律）。
- 账本：**非试验账本批不 append trials_ledger**（census/verify/TSGATE 先例）——池成员试验量已在 W19/W20 波入账（496+496），消费普查=零新试验零重复入账；marks +0·SEED +0。

## §4 判据【跑前写死·冻结窗核】

- 本批判据=§3 gate_verify 三控判线逐字冻结——**G1'v2/G2v2 不适用声明**：本批无策略收益序列/无 trade 流（探针批型），机械套用=类别错配；判读线等价强度=OOS 盲段+成本+不重叠三控（与 gate_verify 同门同线）。
- 描述条款（批级披露不替代判线）：OOS 正份额/中位 t/五员逐员读数/IS-OOS 反号门单列/波次血统分组计数。
- 硬界设计三件套 (c)：本批无策略 max 线——**极端日先验面**=七极端微观结构日（2015-07 股灾/2016-01 熔断/2024-02 微盘崩/2024-09-24·09-30 政策脉冲/2025-04-07 外生缺口/2026-01-19 极端量日）门态披露列（各门在七日的开/关态随结果表披露·A158-TSGATE-P1 §4 同面）。
- 跑后禁令：禁调门槛/禁换口径/禁加式重跑；失败=失败，诚实收线；全 FAIL=池时序门用法 wave-1 关线（素材池消费轨道负收口如实入 §8）。

## §5 跑前预测【写死于跑前·≥3 条·冻结窗核】

1. **锚门复现（确定性·非预测）**：DELTA(VOLUME,30)_q10 @510300 open==390/decidable==3341/首可判 bar-idx==149（r867 起草探针同 cutoff 同构造逐位；不符=fail-closed VOID）。
2. **PASS 门数 ∈ [0, 12]**：E[FP]=8.9 假阳量级+真信号先验刻意不膨胀（换用法独立假设+选择偏差不外推）→模态结局=低个位真信号+假阳噪声面=PASS 门全部待独立复核方可升格；**PASS+PARTIAL 合计 ≤ 40**（判别力稀疏预期·A158-TSGATE-P1 314 门 PASS+PARTIAL=190 面的关联簇结构在公式树独立式面不可比——本批式间相关性未知如实披露，簇内成片通过风险由 §1.② 选择偏差披露与独立复核面兜底）。
3. **多数门 FAIL 预期（≥120/178）**：截面 IC 存活面与时序门面独立性强先验——大面积平塌=合法关线产出（省未来臂）。
4. **M1 正向 9 员带零特殊先验**：9 员全可算入 178 门——时序门面读数与截面 t 面无方向先验可借（换用法独立假设）·M1 带员 PASS 率不高于池基率=无信息先验声明（禁以截面 t 面预判时序门结果）。
5. **极端日门态先验**：量能类池员（DELTA(VOLUME,30)/DELTA(AMOUNT,30) 等低分位门）在 2026-01-19 极端量日/2024-09-24·09-30 政策脉冲日开窗聚集（量能极端态=低分位门天然触发面）；价类 DIV(LOW,*) 族门态逐日披露验证。

## §6 产物【起草窗核·冻结窗复核】

- runner：`scripts/mp1_tsgate_probe.py`（subcommands：run[--shard k --shards n --workers N]/finalize/status/selftest；`__main__` 守卫=Windows mp 坑律；**A158-TSGATE-P1 runner 克隆+因子面换装**——r836 克隆律全参数显式：BATCH/PREREG/CUTOFF='2026-10-09'/SPLIT/H=20/COST=0.10%/MIN_BARS=500/MIN_EV=15/STRIDE=20；**新面=素材池公式评估器**：formula_str 逆解析器（parse_formula·r867 探针 round-trip 96/96 实证）+t23 evaluate **import 单源零重写**（[n_dates,1] 单标的面·CSRANK 7 式构造性排除）+池装载腿（W19/W20 结果件 records 读取·h1_ok∧¬skip·fp_canon 去重）；selftest=hermetic 合成面：①parser round-trip 腿（96 池式全过+逐算子手值）②评估器单标的手值腿（DELTA/MA/CORR 数值断言+CSRANK 单标的退化断言）③门构造腿（分位边界/decidable NaN 伪影禁用·pit-95）④统计腿（IS/OOS 切分/cost/stride-20 thin/verdict 四态）⑤确定性双跑字节恒等腿 ⑥G-ANCHOR-MP1 实数据锚腿（510300 三元组逐位）⑦refuse-if-exists 幂等腿。
- 产物：`results/mp1_tsgate_p1.json`（顶层 cutoff_meta+prereg 块+178 门 IS/OOS 聚合+verdicts+五员次级表+波次血统分组+极端日门态披露+audit 段）+ `research/MP1_TSGATE.md`（可读供应面：判定表+PASS/PARTIAL 候选清单+诚实注记）+ checkpoint `results/mp1_tsgate_p1/`（gitignored·per-shard jsonl 断点续跑）。
- 池路由：入池 `N2-MP1`（lane_owner=null·lane-free·workers_plan=shard 内 worker_cap 并行 BelowNormal）；~4-8min 串行估计=池批面（autofill 续烧合法）；finalize=烧后合并腿。

## §7 跑后实证。【跑后回填·占位】

（冻结后烧录窗回填：漏斗全链/§5 预测对账/锚门复现/消费面主发现/诚实注记。）

## §8 批后复盘。【跑后回填·占位】

（跑后回填：消费面指名回执/关线清单/独立复核队列指针/素材池消费轨道处置（正收口=PASS 员入独立复核队列·负收口=wave-1 关线）/轮报告与 CODELY.md 回执。）

## 附：slice 分工账（防重复开发·跨窗接力·W18/W19/W20 同构）

- **slice-1（r867 bm-b 本窗·起草+探针）**：本件 DRAFT + `results/_r867bmb_mp1_draft_probe.py`（六腿只读探针：池读数/可算分类/面板在位/解析器 round-trip/单标的评估腿/锚候选读数——回执 `results/_r867bmb_mp1_draft_probe.json`）+ tech.md T24 登记+同轮认领。
- **slice-2（r868 bm-b 本窗·runner+冻结窗·已落地）**：`scripts/mp1_tsgate_probe.py` 交付（selftest 30/30 全绿+七腿 hermetic）+五条件机证全过（selftest 复跑+数据完备门 probe 复跑+banned_direction_gate --prereg rc0 ADMIT+origin 写前复核 DRAFT 态+状态翻面 FROZEN 同 commit）——回执=标题 FROZEN v1.0 证链+results/_r868bmb_banned_gate.txt。
- **slice-3（烧录窗·冻结同轮或后续轮）**：池条目入 runnable_pool→烧录（autofill 或轮内）→finalize 合并→§7/§8 回填+TREASURE_REGISTRY 出入记录（素材池消费首读面）+轮报告/CODELY.md 回执。**评估窗 ≤2026-10-13（W20 §0 令面）——slice-2/3 须在窗内落地，逾期=轨道窗口失效须重议**。
