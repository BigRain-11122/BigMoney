# GATE-RECHECK-A158 预注册 —— A158 时序分位门 48 PASS 独立复核批（D6 邻接审计+五员落地性复核·v4 候选库唯一升格通道）

> 本批=A158-TSGATE-P1（FROZEN bm-a r438 commit 7032c5802·§8 指针「48 PASS → 下批 GATE-RECHECK-A158（gate_verify 纪律独立复核·冻结后烧）=v4 政体门臂候选唯一升格通道」）的直接消费批。跑前冻结于烧批前（R99 律）；判据节禁看结果改线。

## §0 批件身份。【跑前】

- 批名/批号：**GATE-RECHECK-A158**。非试验账本批（marks +0·SEED +0·无策略曲线·不 append trials_ledger——census/verify 先例）；算力=本地 CPU 确定性（48 门×5 员×~3,000 bars·秒级·<5min 轮内合法面=O-2100 执行面分离豁免·A6 探针 r437 先例·零 token 零网络）。
- 认领：lane-free（复用 P1 lane-free 血统）；算力平凡不入池（轮内内联完成·与 pool 无交互）。
- 部门归属：dept:研究（T-101 v4 政体门候选库供料线）。
- **consumer_plan（O-1820(3)）**：RECHECK-CONFIRM 门→**T-101 v4 政体门候选库入册清单**（唯一升格通道·P1 §8 冻结指针）；CLUSTER-COLLAPSED→簇表披露（簇代表入册·非代表不重复入册=D6 簇坍缩律）；REGISTERED-CLONE→拒收（与在册 RSV 绝对门同交易）；RECHECK-FAIL→C1 输入特征降格清单（gate_verify PARTIAL 降格先例）。次级消费：T-74 L5 特征面。
- 意义审计三验：①可判负假设（PASS 门五员落地面不复核确认=降格·D6 簇内非代表=坍缩）②指名消费面（上文）③判负处置预案（FAIL→C1 降格照报·CLONE→拒收·均合法产出）——全过。

## §1 伪 α 机制段。【四选一+D6·承 P1 §1 同根】

- **[x] 行为偏差**（主）——风险源价（辅）：与 P1 同根（极端态过度反应/恐慌识别面·机制不重复声明·本批=P1 同假设的**独立复核面**非新假设）。本批增量=**邻接结构**：P1 §7 实证 SUMD/SUMP/SUMN 构造恒等（SUMP+SUMN=1·SUMD=2SUMP−1）+VSUM* 同构+CNT 族+5/10/20/30/60 窗高相关→48 PASS 有效独立族数≪48——**簇内取代表前禁整簇入册**（P1 §7/§8 冻结原话）。
- **D6 同族相关性准入（本批核心面）**：①对在册门：vs `RSV30_low<0.2` 与 `RSV60_low<0.2`（gate_verify PASS2 在册绝对门·09-29 GM 批）——**max|corr|≥0.7=REGISTERED-CLONE 拒收**（PREREG_TEMPLATE §1 D6 门槛逐字）；②候选间 48×48 簇结构（|corr|≥0.7 连通分量·并查集）→每簇取代表=最高 P1 OOS med_t（实读 results/a158_tsgate_p1.json·并列取名字序）。
- 消费面邻接披露：r433 同门换用法反向证伪律在册——本批复核的是**门候选资格**（政体门输入特征面）非全仓择时用法；择时用法面判负不借判本面、本面亦不宣称择时用法（510050|RSV30 D6 0.9424 beta 同源判例=择时用法面的独立判决）。

## §2 数据与面板。【跑前探针事实】

- 宇宙=**五员冻结宇宙（O-1555）{510300,510050,510500,512100,588000}**·正典件 `data/daily/sh<code>.csv`（P1 双名卫生发现披露面：bare 名与 sh 名并存·本批一律取 sh 正典件=v4 消费面同源）；MIN_BARS=500 gate_verify 逐字（五员全 ≥3,400 行·全部入样）。
- **evidence_cutoff=2026-09-22（P-5C 冻结口径 binding·与 P1 同锚）**：面板一律先截断（510300 截断后 3,483 行）；结果 JSON 顶层 `science_gates.cutoff_meta("2026-09-22")`（C2 合法键）。
- 因子库=**import `scripts/a158_tsgate_probe.py` 单源复用**（alpha158_factors 157 因子 qlib-verbatim·gate_universe 314 门构造·零重实现=反重复铁律）；门定义/预热窗/decidable 掩码与 P1 逐字同（252/120·q10/q90·pit-95 notna 派生）。
- PASS 门清单=**实读 `results/a158_tsgate_p1.json` verdicts**（PASS==48 实数对账·≠48=refuse）；每门 P1 读数（OOS med_t/med_net）同源实读作簇代表排序轴。
- 在册门信号=RSV30/RSV60 **绝对门** `f<0.2`（gate_verify 构造·非分位门）——decidable=f.notna()。
- **前瞻收益**：h=20·`fwd = close.shift(-21)/close.shift(-1) − 1`（P1 逐字·T+1 无未来数据）。
- 数据完备门（fail-closed exit 2·不过即 VOID 零写）：**G-P1**（P1 results json 在位 ∧ verdict_counts.PASS==48 实读）+ **G-PANEL**（五员 sh 件全在位）+ **G-ANCHOR-ROC20**（510300 三元组 dec==3,344 ∧ open==374 ∧ 首可判==139·P1 同锚逐位）+ **G-FACTORS**（157 因子在锚上 ≥500 有效）。

## §3 方法论。【冻结】

- **面 A·五员落地性复核（gate_verify 式）**：每 PASS 门×每员：OOS（≥2017-01-01）in/out 桶（B2 严口径=pit-95 decidable 双桶 AND·P1 逐字）事件数、均差 diff、**net=diff−0.10%**、正负；聚合=五员 net 中位+正员数。**格点稳定性腿（P1 §3「双组抽稀」B 组=本批消费）**：thin_b(pos)=丢弃首个合格事件后贪心 stride-20（A 组=P1 已消费格点；B 组=错位格点·组内不重叠控制恒在·组间窗口可交叠=同信息集重抽样非完全独立样本——**降独立性宣称为格点稳定性·如实**）；每员 thin_B net（事件 ≥5 双桶·不足=None）；B 腿中位数取有效员（≥2 员有效·不足=确认腿失败）。
- **面 B·D6 邻接审计**：信号面=每员 OOS 开仓指示序列（decidable 掩码内·date 索引 5 列 DataFrame）；**相关=pairwise-complete（pandas df.corr()·pit-115 错期上市禁 inner-join 截史律）**；①48×48 候选间矩阵+②48×2 对在册（RSV30_low/RSV60_low 同面信号）；簇=|corr|≥0.7 连通分量（并查集）；代表=簇内最高 P1 OOS med_t·并列名字序。
- **判读线（跑前写死·四态）**：
  `REGISTERED-CLONE` = max|corr| vs 在册两门 ≥0.7（先判·无论簇位）；
  `CLUSTER-COLLAPSED` = 非本簇代表（簇内取一·其余坍缩）；
  `RECHECK-CONFIRM` = 簇代表 ∧ 面A三腿全过（五员 net 中位>0 ∧ 正员数≥3/5 ∧ thin_B 中位>0）→**v4 候选库入册清单**；
  `RECHECK-FAIL` = 簇代表 ∧ 面A任腿不过 → C1 输入特征降格清单。
- **多重检验税披露**：E[FP]=0.05×n_reps（簇代表数·复核面基数=坍缩后族数非 48）——普查+复核两级筛选后入册门仍须 v4 臂预注册锦标赛再判（本批入册=候选资格非策略宣称）。
- 幂等：结果件在位=refuse 重跑（refuse-if-exists）；确定性双跑字节恒等（唯一运行时元数据=generated/elapsed 独立段）；算力平凡无 checkpoint（单趟原子写）。

## §4 判据。【跑前写死】

- 本批判据=§3 四态判线冻结——**G1'v2/G2v2 不适用声明**（无策略收益序列/无 trade 流·探针批型·P1 §4 同声明）；判读线等价强度=五员落地面+成本+格点不重叠+D6 簇坍缩四控。
- 描述条款（披露不替代判线）：每门五员逐员 net/thin_B 读数表、簇结构表（簇内成员+代表+簇内 max|corr|）、对在册 corr 全列、IS/OOS 反号注记承 P1。
- 硬界设计三件套 (c)：本批无策略 max 线——极端日门态承 P1 披露面（本批不重复计算·指针 results/a158_tsgate_p1.json extreme_day 段）。

## §5 跑前预测。【写死于跑前·≥3 条】

1. **锚复现（确定性·非预测）**：G-ANCHOR-ROC20 三元组逐位复现（3344/374/139）；G-P1 PASS==48 实读对账。
2. **簇数 ∈ [5, 20]**：P1 §7 构造恒等族（SUMD/SUMP/SUMN+VSUM* 同构+CNT 族+窗共线）→48 PASS 坍缩到个位至二十簇内；代表数 n_reps≪48。
3. **STD20_q90 与 RSQR20_q90 = 头两号确认候选**（P1 §7 五员 5/5 与 4/5 全正血统）；至少其一 RECHECK-CONFIRM（簇代表+面A三腿）。
4. **REGISTERED-CLONE ∈ [0, 5]**：PASS 池与绝对 0.2 RSV 门重叠预期低（RSV30/60_q10 在 P1=PARTIAL 非 PASS）——少数簇（量能/波动族）可能与 RSV 绝对门共开窗；≥0.7 拒收如实。
5. **RECHECK-CONFIRM 门数 ∈ [0, 12]**（n_reps 基数×多重税+三腿全过=少数存活·零确认亦合法产出=C1 降格清单照报）。

## §6 产物

- runner：`scripts/a158_gate_recheck.py`（subcommands：run/status/selftest；import a158_tsgate_probe 机制零重实现；`__main__` 守卫；selftest=hermetic 合成面：①门构造 import 同一性腿 ②thin_b 数学腿（首事件丢弃+stride 间距+确定性）③簇并查集腿（≥0.7 连通+代表排序）④在册克隆拒收腿（全同信号 corr=1.0→CLONE）⑤四态判线合成腿 ⑥refuse-if-exists 幂等腿 ⑦确定性双跑字节恒等腿）。
- 产物：`results/gate_recheck_a158.json`（顶层 cutoff_meta+prereg 块+48 门四态+五员逐员读数+簇结构表+对在册 corr 列+audit 段）+ `research/A158_GATE_RECHECK.md`（可读面：四态汇总表+入册清单+簇表+诚实注记）。
- 无 checkpoint（秒级单趟·原子写）；跑后 §7/§8 同窗回填（判决面 owner 一次定稿）。
