# PA1E_PREMIUM_EVENT 预注册：ETF 对齐溢价持续段事件窗批（T-16 deliverable-8 · 跑前写死）

> 令源：O-20260924-1155（CEO 令「基金和港股套利什么的也都研究建立一下」）· ARB-1 线 P-A1 §8 既定指针（r55 判负归因：「QDII 溢价事件时间稀疏被 40+ 平价员逐日全截面 IC 稀释=口径固有披露非机制证伪，事件窗口径另开预注册」）
> 认领：**MSG-20260924-1907-bm-c-pa1e-prereg**（先于本批 commit，F-04）· T-16 deliverable-8（bm-c 自 r51 持续持有）
> 性质：**因子/统计层事件研究批**（零引擎跑→引擎账本 N 不动；IC≠策略，**本批不注册交易员不接线策略**；PASS 仅入候选货架，策略转化另走预注册+G1' v2 门禁链）
> **命名消歧**：批号 PA1E（P-A1 Event-window 延伸）——避开三重撞名：playbook §一 P-A2=LOF 折价面（r56-57 在制）、research/shortline/PA2_LHB_SYNTH.md（LHB 族另一 PA2）。r55 PA1 §8 行文「P-A2 事件窗口径」以本批为准。

## §0 批件身份【必填·跑前】

- **批名/批号**：pa1e_premium_event；**批内格数（N_eff）=56**：1 primary（H1 溢价段事件 @h10）+5 报告列（th5% 阈/th2% 阈/minlen5 折算段长/H2 折价段镜像/跨境族子集——全部同源报告列非独立假设，不判不独立计格）+50 matched-design null；primary 过 V1 后 h5/h20 报告列 +2（上限 58）。
- **认领**：F-04 先行——fleet/inbox/MSG-20260924-1907＋任务板引用=T-16（deliverable-8）。
- **部门归属**：dept:数据+研究（T-16 lane affinity 同 PA1）。
- **算力预算**：48 员×1632 日面板全向量化+K=50 圆移位 null，单进程预估 <3min（R41 免后台化）；批报告必带 audit 段（无 audit 段结果件不入账本）。

## §1 α 机制段【必填·D6——四选一】

- [ ] 风险溢价：
- [ ] 行为偏差：
- [x] **结构性**：同 PA1 §1 逐字沿用（申赎机制结构性执行溢价回归；偏离持续=套利受限——QDII 外汇额度冻结创造/跨境交收摩擦/最小申赎单位机构门槛；我方只二级市场）。**本批口径修正**：持续溢价段（≥3%×≥3 连续日）=配额受限政体的事件化测量——PA1 逐日全截面 IC 把时间稀疏政体稀释进 1212 期×47 员格；本批条件于段事件，直接检验「段内溢价追入者在段后窗口付出代价」。信号付费方=段位追入的行为性买方（放大器）+套利受限期为溢价交易提供流动性的挂单方。
- [ ] 微观结构：

**同族相关性准入检查【必填·D6】**：
- 本批与 PA1 同 premium_adj 血缘但**测量口径正交**（连续全截面 IC vs 段条件事件窗 AR）——PA1 §8 明文指针授权，非重跑非翻案（premium_z 连续口径判负维持不变；premium_chg_5d 单列不构成翻案的条款同样适用于本批：本批不是单列翻案，是新口径首测）。
- 批内冗余（冻结披露）：5 报告列全部同源于 prem_al 触发族（阈值/段长/镜像侧/子集四维变换），**同族=报告列不独立计假设**，N_eff 已按此记 56。
- 策略级比较：零（本批不产策略函数）；若 PASS 转化批须另开预注册过 D6 逐对名单+ETF 域成本模型（XSTOCK_SYNTH §1 先例）。

## §2 数据与面板【必填·跑前探针事实，非结果】

- **宇宙**：core48 全体 48 员（面板即全员，无扩池无白名单）。
- **面板**：`data/fund_premium/panel/panel.csv`（r53 建成 76,025 行×48 员 2020-01-02..2026-09-23·1632 td；列含 close/nav/nav_lag_td/premium_raw/ex_div_flag/div_per_unit/cons_flag/premium_adj/premium_z）。
- **evidence_cutoff=2026-09-23**（前向锁盒 D2 同 PA1）；结果 JSON 顶层必须带 `science_gates.cutoff_meta(evidence_cutoff)`。
- **去污染重构（本批新增口径·冻结）**：裸 premium_adj(t)=close(t)/NAV(t−1)−1 含当日行情混入（close(t) 对 NAV(t−1) 的差=真溢价(t−1)+当日的板块涨幅——高波动员单日 ±3% 穿越=行情事件非溢价事件，探针实证：512480 裸口径 th3/minlen3 穿越 139 次全为行情混入，对齐口径后归零级）。**对齐溢价**：`prem_al(t) = (1+premium_adj(t))/(1+ret_close(t)) − 1 = close(t−1)/NAV_asof(t) − 1`，仅取清洁行（ex_div_flag=0 ∧ cons_flag=0 ∧ ret 有限 ≠−1；除息日加回属当日 close 不属 t−1，故除息日触发一律剔除）。**信息时点**：prem_al(t) 的两个输入（close(t−1)、NAV(t−1)）均于 t−1 日终前发布 → **信号于 t−1 收盘后即已知，入场 close(t) 晚信号一整日（保守披露：晚于可用性一日的执行滞后）**，零未来数据。
- **触发定义（冻结）**：H1 溢价段事件日 t=成员 prem_al 于 t−2/t−1/t 三连续清洁信号日全部 ≥+3%（持续段≥3），且该员此前 10 td 内无更早事件起点（冷却防重叠窗膨胀）；H2 折价段镜像 ≤−3%（报告列）。NaN 日断段（断点重置 run 计数）。
- **跑前探针事实（2026-09-24 19:1x 采样·样本量非结果）**：H1 hi3/minlen3：283 起点（IS≤2024-12-31=208 / OOS=75）·24 员·234 唯一日期（低聚簇）；成员集中=513100:88/513500:66/513050:54/513520:31/159985:18（跨境族占 84%+，§1 机制对上）。H2 lo3：33 起点（欠功效→报告列）。敏感性探针：th5=173/th2=409/minlen5=212。IS/OOS 切分=composite_ic.IS_END 全公司口径。
- **数据完备门（不过门禁跑批）**：①NAV 覆盖≥95%（行口径）②面板 summary gates PASS 且 evidence_cutoff=2026-09-23 ③premium_adj 零 NaN ④IS 段 H1 事件数≥60（冻结 n-gate）。
- 样本窗诚实披露：同 PA1 §2（6.75 年政体覆盖有限；QDII 段事件 2020-2021 额度冻结/2025+ 跨境热门部分落 OOS）。

## §3 方法学【必填】

- **前瞻收益（冻结，同 PA1 逐字）**：fwd_ret_h=分红包容=(close[t+h]+Σ_{t<d≤t+h} div_per_unit[d])/close[t]−1；cons 窗排除：(t,t+h] 内该员 cons_flag=1 任一日→剔除该 (t,员) 对。h10=唯一门控期限；h5/h20=primary 过 V1 后报告列（snooping 折价标签）。
- **AR（异常收益·冻结）**：AR(t,m)=fwd_ret_h(t,m)−benchmark(t)，benchmark(t)=同日**非触发员**（该日无 H1/H2 触发的成员）中有效者（fwd 有限∧close 有限∧无 cons 窗）的 fwd_ret_h 均值；基准员数<5→该日 AR=NaN 丢弃。截面的同日去均值吸收市场/板块公共移动。
- **估计量**：IS 池化 mean AR（primary 判据）+OOS 池化 mean AR（V3）+披露：median/t 值（t=mean/SE）/聚簇披露（唯一日期数/最大同日事件数）/跨境族子集列（族=全样本 H1 起点数≥10 的成员，冻结清单：513100/513500/513050/513520/159985——跑前按探针规则冻结，非事后择优）。
- **null（matched-design 圆移位·冻结）**：K=50；对每 null i（**seed=20260926+i，i=0..49；新基先登记 `science_gates.SEED_REGISTRY["pa1e_premium_event"]=20260926`**（rg 全 repo 扫描 2026-09-24 19:0x 确认空闲，非 registry-only 双查 r54 坑律））：每成员 prem_al 序列按交易日格圆移位随机偏移∈[60, T−60]（保持溢价序列的持续性与分布结构，只切断与收益的对齐——白噪 null 会低估触发聚簇，圆移位=匹配设计）；移位后同规则重算触发（同持续段+同冷却）→在实际收益面上算 AR→IS 池化 mean AR。V1 阈=max(0.5%, K null 的 |IS mean AR| p95)。
- **成本口径声明**：AR=信息层零成本；经济地板 0.5%≥legacy 往返 26bp×2 头寸空间披露；可交易性（QDII 段内流动性/创造暂停日/冲击成本）归策略转化批届时 V2 ADV 口径。
- **账本**：零引擎跑→引擎账本 N 不动；因子账本 added=56（±2 报告列）——`science_gates.append_ledger("pa1e_premium_event", ...)`（dict schema 唯一禁手抄 prev；prev=max(results, results/shortline) 双目录 r60 惯例）。

## §4 判据【必填·跑前写死，禁看结果调线】

- **n-gate**：IS 段 H1 事件数 ≥60（探针 208 预期过门）。
- **h10=唯一门控期限**（h5/h20 报告列带 snooping 折价标签）。
- **V1（经济+null 门·单侧 H1 方向）**：IS 池化 mean AR_h10 ≤ −max(0.005 地板, 同设计 null p95 |mean AR|)；
- **V2（统计墙）**：IS t 值 ≤ −2.0（t=mean AR/(std/√n)，聚簇披露不设门：唯一日期/最大同日事件数如实报）；
- **V3（留存）**：OOS mean AR < 0 且 |OOS mean AR| ≥ 0.5×|IS mean AR|；
- **PASS = n-gate∧V1∧V2∧V3**（primary 判；5 报告列只报告不判——同族变换非独立假设）。
- 判据口径声明：本批为事件研究口径（因子层三门口径的事件化变体：V1 经济地板+null p95 / V2 统计墙 / V3 OOS 留存，模板 §4 末行「因子批（IC 型）沿用三门口径」的 AR 版）；**零策略级评估不触及 g1_prime_v2/g2_registration_v2**（共享库门属策略转化批）。
- **PASS →** 段条件溢价回归信号候选入 ETF 域素材货架（策略转化另开预注册：G1' v2+DSR+PBO+成本模型）；
- **FAIL →** 溢价子线双口径收线（P-A1 连续因子判负 r55 + PA1E 事件口径判负 → ARB-1 溢价线在 playbook §一 记「连续+事件双口径已测皆负」收线留痕；P-A2 LOF/P-B1 AH 不受影响；premium 面板数据资产保留供 S6 维护链与后续复用）。**禁翻案条款**：任何阈值/段长/期限变体翻案须另开预注册——禁止跑到达标为止。

## §5 跑前预测【必填·写死于跑前，跑后 §7 对账】

1. **H1 方向=负**（段后回归：段内溢价追入者在 h10 窗付出代价）——置信 60%（机制对齐+段事件时 QDII 溢价崩段史实 2021 春/2024-2025 多段；但基准去均值可能吸收部分段效应）。
2. 量级：|IS mean AR_h10| ∈ [0.5%, 3%]（QDII 段溢价峰值 10-20% 级，回归即使部分兑现也应显著超 0.5% 地板）。
3. OOS 留存：0.3-1.0×（2025 段事件仍发生；政策驱动方差大）。
4. **过门预测：0-1/1 primary**（n≈200+段效应真实则 V2 t≤−2 可达；null p95 预估 0.3-0.6% → V1 地板 0.5% 大概率主导；V2 为真门）。
5. 报告列预测：th5（更强段）|AR| > th3（剂量响应）；th2 < th3；minlen5 ≈ th3；H2 折价段镜像方向=正但 n=33 欠功效 null 带宽大；跨境族子集承载大部分效应（族外同号更小）。
6. 聚簇披露预测：唯一日期≈事件数 80%+（段事件多员同期=跨境族同政体）；最大同日事件数<10。
7. 多重性声明：溢价族事件口径**首测**（PA1 §8 指针落地）；若 FAIL 溢价子线收线，报告列读数不构成任何翻案。

## §6 产物【必填】

- `scripts/pa1e_premium_event.py`（一次性定稿：数据门→selftest（自然 JSON 面合成 fixture：重构/触发/冷却/AR 去均值/null 确定性五查）→null→primary+报告列→门判定→账本，全链一脚本；selftest 子命令跑数前先跑）；
- `research/shortline/pa1e_premium_event_results.csv` + `results/shortline/pa1e_premium_event.json`（顶层 evidence_cutoff+`science_gates.cutoff_meta`+null 阈值/门判定全输入/audit 段）；
- verdict 入轮报告+CODELY.md 行级留痕；`gate_attrition.json` 追加行；playbook §一 P-A1 行按 verdict 更新（PASS=候选货架注记/FAIL=双口径收线注记）。

## §7 跑后实证【跑前必须为空——占位纪律：写数字即造假】

（占位）

## §8 批后复盘【必填·s7-T】

（占位）
