# PA1_PREMIUM_IC 预注册：ETF 场内折溢价因子批（T-16 P-A1 · 跑前写死）

> 令源：O-20260924-1155（CEO 令「基金和港股套利什么的也都研究建立一下」）· ARB-1 线 P-A1 假说（research/ARBITRAGE_PLAYBOOK.md v0.1 §一）
> 认领：**MSG-20260924-1436-bm-c-pa1-prereg**（先于本批 commit，F-04）· T-16 deliverable-6（bm-c 自 r51 持续持有）
> 性质：**因子层 IC 批测**（零引擎跑→引擎账本 N 不动；IC≠策略，**本批不注册交易员不接线策略**，策略/合成转化另走 P-2 型预注册+G1' v2 门禁链）
> 本轮交付=本预注册冻结；跑批=后续轮（跑前本件已 commit，§7/§8 占位为空）

## §0 批件身份【必填·跑前】

- **批名/批号**：pa1_premium_ic；**批内格数（N_eff）=53**：1 primary（premium_z）+2 敏感性报告列（premium_adj 原始水平 / premium_chg_5d）+50 matched-mask null；primary 过 V1 后 h5/h20 报告列 +2（上限 55）。敏感性列与 primary 同源于 premium_adj 序列（水平/变化/截面 z 三种变换），**非独立成员不独立计格**（XSTOCK_SYNTH primary+敏感性范式）。
- **认领**：F-04 先行——fleet/inbox/ MSG-20260924-1436（防双机在制窗口互不可见撞车）＋任务板引用=T-16（deliverable-6）。
- **部门归属**：dept:数据+研究（T-16 lane affinity：数据面板=本机产线 r51-53，研究面=套利线勘探批）。
- **算力预算**：48 员×1632 日×3 列+50 null 全向量化，单 worker 预估 <5min（远低于 10min 后台化阈值，R41 免适用）；批报告必带 audit 段（compute_audit 纪律，无 audit 段结果件不入账本）。

## §1 α 机制段【必填·D6——四选一】

- [ ] 风险溢价：
- [ ] 行为偏差：
- [x] **结构性**：ETF 溢价的存在与回归由**申赎机制**结构性执行——溢价超阈值→授权参与商一级创造份额→供给压制价格向 NAV 收敛；偏离能持续=套利受限（QDII 外汇额度冻结创造、跨境交收摩擦、最小申赎单位 50-100 万份=机构级门槛，playbook §二.1 明文我方只二级市场）。**溢价高且未被套利消除的成员，其偏离 NAV 锚的程度本身携带「需求冲击×套利约束」信息**（QDII 额度紧张期 513100 p95|premium| 11.9% 实证）——信号付费方=溢价峰值追入的行为性买方（放大器非主机制）与套利受限时为溢价交易提供流动性的挂单方。
- [ ] 微观结构：

**同族相关性准入检查【必填·D6】**：
- 本批为因子层 IC 批（零策略函数）：**无策略级在册比较**——策略转化须另开预注册先过 D6 逐对名单+ETF 域成本模型（XSTOCK_SYNTH §1 先例逐字沿用）。
- 批内冗余（冻结披露）：premium_adj / premium_chg_5d / premium_z 三列同源于 premium_adj 序列（水平/5 日变化/截面标准化），**同族=按敏感性列处理非独立格**，N_eff 已按此记 53。
- 跨批亲缘披露（跑后附 IC 序列相关，不设门）：premium 反转方向若成立，与 PC_L2 人气因子（注意力面）在 ETF 域概念亲缘；与在册 27 内部因子（价格派生族）数据面正交（premium=NAV 锚派生，全项目首见信息源）。若 max|corr|≥0.7（日 IC 序列口径 vs 任一在册 ETF 域因子 sleeve）→ 如实披露且**不作为拒收依据**（因子层无在册比较条款），但为合成货架聚类（corr≥0.5 贪心）预埋证据。

## §2 数据与面板【必填·跑前探针事实，非结果】

- **宇宙**：core48 全体 48 员（面板即 core48 全员；无扩池无白名单）。
- **面板**：`data/fund_premium/panel/panel.csv`（r53 建成：76,025 行×48 员，2020-01-02..2026-09-23，1632 td，gates PASS；列=date/code/close/nav/nav_date/nav_lag_td/premium_raw/ex_div_flag/div_per_unit/cons_flag/cons_ratio/premium_adj/premium_z/premium_chg_5d）。
- **evidence_cutoff=2026-09-23**（前向锁盒 D2：cutoff 后新 bar 锁定不得回流本批）；结果 JSON 顶层必须带 `science_gates.cutoff_meta(evidence_cutoff)` 字段（缺字段=science_audit C2 VIOLATION）。
- **可用性口径（冻结——T-16 r52 QDII 发现的正式定案）**：premium(t)=close(t) vs **as-of NAV**（`nav_date<close_date` 严格不等、per-fund 最新可得）——信号日 t 只用 nav_date<t 的 NAV，零未来数据；**无统一 T-1 假设**（nav_lag_td 中位 1 td、全体 48 员 max_of_max=1）；QDII 三员（513050/513100/513500）build-time gap 1 td 属数据固有披露项（NAV 无披露时刻戳，可用性口径归 P-A1 冻结）。
- **除息守卫**：premium_adj 已内建除息加回（sina 累计列逐行差分实证，510300 2026-01-19 raw −2.56%→adj −0.03% 复原验证）；T-19 折算=**纯披露不加回**（NAV 面同边重述，21 处 cons 与分红面重合事件跳过加回防双计）。
- **数据完备门（不过门禁跑批）**：①NAV 覆盖≥95%（r52 gate 实测 100% PASS）；②面板 summary gates PASS（r53）；③premium_adj 零 NaN（r53 实测）；④IS 段有效期数≥500（跑时实测为准，预检 2020-01-02..2024-12-31≈1211 交易日预期过门）。
- 样本窗诚实披露：close 面起点 2020-01-02 → premium 面仅 6.75 年（2020 结构牛/2021-2022 震荡/2023-2024 下行/2025+ 修复），政体覆盖有限；QDII 溢价事件（2020-2021 额度冻结、2025+ 跨境热门）部分落于 OOS 段。

## §3 方法学【必填】

- **因子定义（冻结，全部=面板原生列零重算）**：
  - primary `premium_z`：premium_adj 逐日截面 z（ddof=0，<2 有效员=NaN）；
  - 敏感性列 `premium_adj`（原始水平）、`premium_chg_5d`（5 日变化）。
- **前瞻收益（冻结）**：fwd_ret_h = **分红包容收益** =（close[t+h] + Σ_{t<d≤t+h} div_per_unit[d]）/ close[t] − 1，全部取自面板列（与 premium_adj 同一加回口径）；**cons 窗排除**：(t, t+h] 内该员 cons_flag=1 任一日 → 剔除该 (t,员) 对（21 事件总量，样本损失<0.1%；折算对收益面是机械缩放污染，排除优于调整）。h10=主口径门控；h5/h20=仅 primary 过 V1 后补报告列（非门控防窥探）。
- **掩码（冻结）**：t 日有效 = premium_z(t) 非 NaN ∧ close(t) 非 NaN ∧ fwd_ret_h10(t) 可算（窗完整落面板内）∧ 窗内无该员 cons 事件；**null 用同一掩码**（窄截面必须同掩码带，P-A 教训）。
- **IC**：逐日截面 spearman，**先掩码后排名**（J7 坑族），逐日交集 ≥5 员，零方差→NaN；快路径=`shortline_p1_ic._ic_series_fast` 复制；**等价门禁先行**：探针因子（**−60d 动量@core48 ETF close 面**，零接触 premium 列）随机 400 日子样本 vs `composite_ic.ic_series` 参考实现 max|diff|≤1e-6，不过门不跑批（PA_LHB 范式）。
- **IS/OOS**：IS≤2024-12-31（`composite_ic.IS_END` 全公司口径），OOS=2025-01-01→cutoff；样本外恒盲。
- **null**：K=50 白噪声因子面板（**seed=20260925+i，i=0..49；已登记 `science_gates.SEED_REGISTRY["pa1_premium_ic"]=20260925`**——日期式基：53_x00 带=j13v2_mill 逐 run 梯占用、54_000=t18_deep_axis（bm-b 13:2x）占用，registry+rg 扫描 2026-09-24 14:3x 确认空闲），逐日同掩码遮蔽后算 IC，V1 用该掩码 null p95。
- **成本口径声明**：IC 层零成本（因子信息量口径）；可交易性另批（届时 V1 legacy 13bp×2 压测或 V2 ADV 三层滑点按知识库声明）。
- **账本**：零引擎跑→引擎账本 N 不动；因子账本 added=53（±2 报告列）——`science_gates.append_ledger("pa1_premium_ic", batch_trials, file_name, evidence_cutoff=...)`（dict schema 唯一，禁手抄 prev）；IC 计算数入 results JSON audit 段。

## §4 判据【必填·跑前写死，禁看结果调线】

- **h10=唯一门控期限**（持有语境 3-15d；h5/h20 报告列带 snooping 折价标签）。
- **V1** = |IS IC_mean| > max(0.02 地板, 同掩码 null p95 |IC|)；
- **V2** = |IS IC_IR| ≥ 0.30（P-2/XLIB/PS2/P-1c/P-A 全线同墙）；
- **V3** = OOS 同号 且 |OOS IC_mean| ≥ 0.5×|IS IC_mean|；
- **期数门** = IS 段 n_periods ≥ 500；
- **PASS = V1∧V2∧V3∧期数门**（primary 判；敏感性列只报告不判——同族变换非独立假设）。
- 判据引用：因子层门=公司连续口径（V1/V2/V3+matched null）；本批零策略级评估**不触及 g1_prime_v2/g2_registration_v2**（共享库门属策略转化批，届时引用禁手抄判线）。
- **PASS →** premium_z 入 ETF 域合成素材货架（后续 P-2 型合成批另开预注册，聚类条款 corr≥0.5 贪心）+策略级转化另开预注册（G1' v2+成本模型）；**FAIL →** P-A1 因子判负如实收线（premium 面板数据资产保留：T-16 S6 维护链照常供 P-A2/P-B1 复用，判负≠数据作废）。
- 批后必做：`results/gate_attrition.json` 追加损耗账一行（s7-T）+判线当批读数披露（V1 地板/null p95 实测值）。

## §5 跑前预测【必填·写死于跑前，跑后 §7 对账】

1. **premium_z 方向=负**（高溢价→h10 跑输：申赎机制回归假说；QDII 溢价异常员为主要贡献群）——置信 55%。
2. IS IC 量级：|IC| ∈ [0.01, 0.05]（48 员窄截面噪声大；P-1a/P-1b 公共因子库同域 0/183+0/82 全灭先例锚定低预期；但 premium=NAV 锚派生全项目首见信息源非价格派生，故给非零带宽）。
3. OOS 留存：QDII 溢价政体 2025+ 变化大（额度政策驱动），V3 留存门是真风险——预测 |OOS IC| 衰减至 IS 的 0.3-0.8×。
4. **过门预测：0-1/1 primary**（V2 IR≥0.30 在 48 员截面最难：逐日 IC 噪声 σ≈1/√(n−1)≈0.15，需 |IC_mean|/IC_σ 比值 0.30 → |IC_mean| 需 ~0.045 级别，为预测带上半区）。
5. 敏感性列：premium_adj 与 premium_z 同向同量级（同源变换）；premium_chg_5d 方向不定（需求冲击延续 vs 回归二力对冲），预期 |IC|<primary。
6. null 带预判：44 员级截面逐日 IC 噪声 σ≈0.152，IS 段 ~1211 期 → null p95 |IC| ≈ 0.006-0.012 → **V1 由 0.02 地板主导**（与 P-A/P-1c 同象），V2 为真门。
7. 多重性声明：本批=ARB-1 线**首次**因子批测（P-A1 假说第一次受检）；T-16 数据勘探批已产不计 N（数据工程口径）。若 primary FAIL，premium_chg_5d 单独翻案须另开预注册——**禁止跑到达标为止**。

## §6 产物【必填】

- `scripts/pa1_premium_ic.py`（一次性定稿：等价门禁→null→主批→门判定→账本，全链一脚本）；
- `research/shortline/pa1_premium_ic_results.csv` + `results/shortline/pa1_premium_ic.json`（顶层 evidence_cutoff+`science_gates.cutoff_meta`+null 阈值/门判定四线全输入/audit 段）；
- verdict 入轮报告+CODELY.md 行级留痕；`gate_attrition.json` 追加行。

## §7 跑后实证【跑前必须为空——占位纪律：写数字即造假】

（2026-09-24 15:0x r55 一次定稿回填；判据零改动；工程双跑留痕见末行）

- **数据门**：①nav_cov=1.0000（行口径）②面板 summary verdict=PASS（cutoff 2026-09-23）③premium_adj NaN=0 行——三门全过；矩形缺口 2,311 格=晚上市 (fund,date) 无行（掩码职责非数据病，data_gates.rect_gap 披露）。
- **掩码 h10**：中位截面 47 员、有效格 75,310、cons 排除 202 格（21 事件×窗）。
- **等价门**：−60d 动量探针 400 日子样本，ref/fast 共同 379 期，max|diff|=2.22e-16 ≪ 1e-6——**PASS**。
- **null（K=50 同掩码，seed 20260925+i）**：IS 段 p95|IC|=0.0083、p95|IR|=0.0558 → V1 阈=max(0.02, 0.0083)=**0.02 地板主导**（§5.6 预测命中）。
- **primary premium_z @h10**：IS IC_mean=**+0.0033**、IC_IR=**0.011**（n=1212 期，期数门过）；OOS IC_mean=**+0.0369**（n=410）。V1：0.0033>0.02 **FAIL**；V2：0.011≥0.30 **FAIL**；V3：同号且 0.0369≥0.00165 **PASS**；**总判 FAIL**——h5/h20 报告列按冻结协议未解锁。
- **敏感性列（报告不判）**：premium_adj IS +0.0033（与 primary 同值=同源变换自洽）；premium_chg_5d IS **−0.0032**（反向小量级）。
- **账本**：因子链 5600→**5653**（+53 格=1 primary+2 敏感+50 null）；引擎账本 N=3077 不动（零引擎跑）；audit 段 verdict=CLEAN flags=[]；gate_attrition 已追加 PA1_PREMIUM_IC 行。
- **工程双跑留痕（如实）**：run#1 于数据门③中止——门实现口径 bug（pivot 矩形 78,336 格 vs 预注册行口径 76,025 行，2,311 晚上市缺失格被误计 NaN），**零数字产出、账本未动、判据未动**；修复=改行口径后 run#2 为唯一产数跑。判线/种子/掩码全程零改动。

## §8 批后复盘【必填·s7-T】

（2026-09-24 15:0x r55 回填）

**§5 预测逐条对账**：
1. 方向负（55% 置信）→ **未中**：实测 IS +0.0033 正向微小（申赎回归假说未获支持）；OOS 亦正。
2. |IC|∈[0.01,0.05] → **未中**：实测 0.0033 低于预测带下沿约 3×（P-1a/P-1b 同域全灭先例锚定不足，下修至地板下）。
3. OOS 留存 0.3-0.8× → **未中**：实测 0.0369/0.0033=11.2×（留存>1），但两侧均微小、IS 已死于 V1/V2，留存读数无决策意义。
4. 过门 0-1/1 → **命中**（0/1）。
5. 敏感性：premium_adj 同向同量级 **命中**（+0.0033 同值）；premium_chg_5d 方向不定 **命中**（实测反向 −0.0032，量级与 primary 相当）。
6. null 带 0.006-0.012 → **命中**（0.0083 带内）；V1 地板主导 **命中**。
7. 多重性：首测即判，零重跑 ✓。

**判线当批读数**：V1 地板 0.02｜null p95 0.0083｜V1 阈 0.02（地板主导）｜V2 IR 0.011 vs 墙 0.30。

**损耗账**：1 primary 死于 V1+V2 双杀（0.0033 vs 0.02；0.011 vs 0.30）——结构性余量 6×/27×，无近线争议；2 敏感列报告不判；50 null 基线落在预期带内=掩码与实现健康；h5/h20 未解锁（V1 fail 即冻结协议止步）。

**机制层诚实归因**：core48 以国内平价 ETF 为主，除息加回后的截面 premium 水平在 47 员窄截面上近乎无信息（|IC|≈null 带）；§1 结构性机制的主贡献群（QDII 溢价事件）为**时间稀疏事件**，在逐日全截面 IC 口径下被 40+ 平价员稀释——因子层口径不利于事件型溢价信号，此为口径固有披露非机制证伪（事件窗口径另属 P-A2/事件研究面）。

**收线**：P-A1 因子判负如实收线；premium 面板数据资产保留（T-16 S6 维护链照常）；premium_chg_5d 反向读数**不构成翻案**——任何单列翻案须另开预注册（§5.7 条款，禁止跑到达标为止）；P-A1 线后续指针=P-A2 事件窗口径勘探（QDII 溢价事件面）或 P-B1，均须新预注册。
