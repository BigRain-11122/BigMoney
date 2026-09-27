# SINA_CONSTRUCT_P1 — sina 四档资金流因子族 IC 普查候选 PREREG（DRAFT v0.1·跑前冻结待点火）

> 状态：**FROZEN v1.0**——冻结 commit=本 commit（R99 跑前冻结；起草面 DRAFT v0.1 已于 r331 落盘）；冻结后禁看结果改线；缺陷修正走修正案纪律=零判据面触碰+留痕（SINA_MF_PREREG §5 先例族）。起草→冻结窗内跑前最终化（bm-a MSG-1615「freeze face waits your final」授权）：§0 执行车道裁定回执+seed 登记落定、§1 同批内 sleeve-tag 语义澄清、§4 V1/V2 族形口径勘正（A1/MF 族冻结常量转录漂移修正·如实标注）、§6 产物与工程注记——全部为跑前面动作，**零格已燃**。
> 授权链：MSG-20260927-1210 option-(c) 并行立场（EM 面 MF_IC_P1 维持 parked 诚实等待；sina 深面板 complete+N≥250 开工门）→ bm-a 15:07:30 ready-panel MSG（gate OPEN 实证：complete=true cutoff 2026-09-24、accept §4 五线 PASS、N=250 深度普查 98.13%≥250/99.46%≥50）→ 本起草 → **MSG-20260927-1615 bm-a 执行车道裁定 pick=(a) data-host local burn（freeze face 等本最终稿）→ 本冻结**。
> 数据面法律：research/shortline/SINA_MF_PREREG.md（FROZEN·T-72）全律继承——§2 量纲诚实律（sina 自有四档禁映射 EM 主力语义）、自洽律 netamount==Σ(r0_net..r3_net)、隔离律（data/sina_mf/ 独立禁与 EM 混读混 join）、R224/R225 档位语义证据链（官方饼图算术：**主力=r0+r1、散户=r2+r3**；r1/r2 档名与阈值 UNDOCUMENTED 诚实标注禁猜）。
> 本件性质：**因子 IC 普查批，零引擎零持仓零账本**（不产生交易面；与数据车道 prereg 的「零回测零引擎」同精神，IC=测量面）。

## §0 批件身份【必填·跑前】

- 批名 / 批号：**SINA_CONSTRUCT_P1**；批内格数 **N_eff=5**（五构造，见 §3；扩容即买单）。
- 认领：F-04 先行——开工声明 MSG = fleet/inbox/MSG-20260927-155x-bmb-sina-construct-draft-claim.json（本起草窗同步落，兼 bm-a ready-panel MSG 回执+GM 抄送）；任务板引用=fleet/tasks/T-202609-25-46-P1.json progress 下轮记入。
- 部门归属：dept:研究+数据（新数据道上的因子构造普查）。
- 算力预算：~5,200 股 × ≤240 信号日 × 5 构造 + K=100 同掩码 null，纯 pandas/numpy L1 确定性，预估 **10-20min** ⇒ 按 R41 长活律入 results/runnable_pool.json 后台池跑+跨轮 checkpoint；worker ≤ floor(16×0.8)=12；批报告必带 audit 段。
- **执行车道声明（工程面·已裁定）**：**裁定已落=option (a) data-host local execution（MSG-20260927-1615 bm-a 回执）**——面板 bm-a 本地 data/sina_mf/（gitignored 大面·控制面律）；科学面脚本 scripts/sina_construct_ic.py 本仓共享（bm-b 起草）；census burn 由 bm-a 本地认领池跑，**bm-a 于「脚本落地+本件冻结 commit」双条件满足后 claim+burn（freeze-alignment law：科学面先锁 git 再点火）**。**科学面（本件 §1-§5）与执行车道解耦**：车道裁定不改任何判据。

## §1 α 机制段【必填·D6】

- [x] **行为偏差**——论证：散户档（r3/r2，sina 官方投资主体叙事 R224）净流入承载追涨杀跌/注意力驱动的噪声交易行为，其次日对价由流动性提供方索取补偿 ⇒ 散户净流入=**反向**信号先验；主力档（r0+r1 官方聚合配方 R225）承载机构/知情资金流的**缓慢信息扩散**（underreaction drift）⇒ **同向**信号先验。代价支付方：过早跟进的散户（反向腿）与反应迟缓的持仓者（漂移腿）。
- [ ] 风险溢价 / [ ] 结构性 / [ ] 微观结构（以上未勾；若实证与先验反向，按 §5 预测对账如实记录，禁跑后改勾）。

**同族相关性准入检查【必填·D6·empirical 立场（MSG-1210 明示=实证问题非假设）】**：点火前逐构造算 `max|corr|`，两口径并列披露——(a) 日度 IC 序列 corr（主口径）+ (b) 同日横截面 factor rank corr（辅口径）——对照清单：
- **EM 族**（MF_IC_P1 构造，EM moneyflow 面）：可得重叠窗内实证；EM 双面持续死（MSG-1105 复证）⇒ 若可得窗不足，**UNAVAILABLE 行诚实标注**（不得以旧窗外推替代、不得跳过不披露）；
- **ths 族**（THS_AGG_P1 全单聚合构造，data/ths_panel/）；
- **lhb 族**（LHB 面构造，data/lhb/）；
- **同批内**（r0/r1/r2/r3/MAIN 五构造两两，sleeve-tag 先例）：同批两两=**披露面 sleeve-tag（family_by_construction）非准入拒收**——MAIN 与 TIER_r0/r1 同源（官方聚合 R225），高相关属构造必然；相关性来源论证（四档分解 vs 单列聚合=量纲不同构 R118+官方聚合 R225）**预声明于结果件 intra_batch_note**（sleeve-tag 先例语义澄清·跑前最终化窗内落定）。
`max|corr| ≥ 0.7` → **该构造拒收**（per-construct 拒收非整批判负；N_eff 随之缩减如实记账；**适用面=跨族对面 EM/ths/lhb**）；确有新机制主张（四档分解 vs EM 单列聚合=量纲不同构 R118 律）须在结果件中给出相关性来源论证方可翻案。

## §2 数据与面板【必填·跑前探针事实】

- 宇宙/池：sina_mf 面板全宇宙 5,228（BM 采集面）∩ eligibility.csv 资格快照 ∩ b_layer_mask（O-1820 件3b 掩码）∩ **面板 N≥50 行**（99.46%=5,200 股；28 股短史=近期 IPO 诚实排除逐列披露）；B 股/北交由采集器已跳过（skipped buckets 诚实计数）。
- 窗口与 **evidence_cutoff（前向锁盒 D2）**：面板 cutoff **2026-09-24**（complete=true）；本批一切面板读数截断至 cutoff，cutoff 后新 bar 锁定不得回流；结果 JSON 顶层必须带 `science_gates.cutoff_meta(cutoff)` 字段（缺=science_audit C2 VIOLATION）。深度 N=250（A1 深史窗）⇒ h10 前向口径下有效信号日 ≈ 240/股上限；**资格信号日门 N≥150**（MF_IC_P1 §2 同门移植，A1 修正案理由链原文）。
- 数据完备门（不过门禁跑批）：sina_mf_accept.json 最新 run=PASS 五线全绿（coverage 5,222/5,228 ≥5,000、written 自洽律 worst 9.776e-10 <1e-8、完整性零缺陷、预算零越限、selftest 绿）——跑批前以该件 in-repo 最新态为准复核，红=禁跑。
- 自洽律入批校验：读入行 `|netamount − Σ(r0_net..r3_net)| > 1e-3`（源面绝对门）逐行拒入+计数披露（采集器入账门同常数，R226 律族）。

## §3 方法学【必填】

- 因子定义（冻结，全部来自面板冻结 schema 14 列）：
  - `TIER_r0 = r0_net / turnover`；`TIER_r1 = r1_net / turnover`；`TIER_r2 = r2_net / turnover`；`TIER_r3 = r3_net / turnover`（档位净流入/成交额=尺度无关横截面因子；turnover=同面板列，禁外源）；
  - `MAIN = (r0_net + r1_net) / turnover`（**官方主力聚合配方 r0+r1，R225 铁证；禁 r0 单独冒充主力**）。
- 滞后规则：sina lscjfb 行=T 日收盘资金流面 ⇒ 信号 T 日收盘可用，前向收益自 T+1 起算（禁未来数据；h1=T+1 收盘→T+2 收盘，h10=T+1→T+11 收盘）。
- 横截面口径：逐日 universe 内 rank（升序位次/ Universe ），IC=Spearman(因子位次, 前向收益位次)。
- null 对照：**K=100** 同掩码随机横截面（因子日内随机置换·同 universe 同日历）＋被动基线=零因子（常数因子 IC≡0 by construction，披露不占门）；seed 基=`SINA_CONSTRUCT_P1`——**已登记 `science_gates.SEED_REGISTRY['sina_construct_p1']=58_550`**（band 58_550..58_649·rg 全仓扫零 RNG 命中 2026-09-27 r333·one-step R250 律·登记随冻结 commit 落地，禁手抄）。
- 成本口径声明：**IC 普查零成本面**（无持仓无换手）；若构造后续晋升策略批（sleeve/trader 注册），成本口径=彼时新 prereg 按 V2（ADV20 三层滑点+1%ADV 帽）独立冻结，本件不预支。
- 账本：`science_gates.append_ledger('SINA_CONSTRUCT_P1', batch_trials, file_name, evidence_cutoff=...)`（dict schema 唯一禁手抄 prev）。
- 机制段四选一已勾 §1（行为偏差）；跑后禁改勾。

## §4 判据【必填·跑前写死，禁看结果调线】

- **因子批（IC 型）三门口径（h 口径跑前冻结：h10 主口径，h1 副口径披露不占门；换口径=数据窥探红线）**：
  - **V1** = **\|IS 段信号日 IC 均值\| > max(0.02, null p95\|IC\|)**（null=本批 K=100 同掩码日内随机置换横截面 IC 均值分布的 p95\|·\|，逐构造独立；**族形勘正·跑前最终化**：A1/MF 族冻结常量为 abs 形（T-46 ticket 冻结文本 verbatim=V1:max(0.02, null p95\|IC\|)、V2=\|IS IC_IR\|≥0.30），起草面裸写「均值>」=族形转录漂移，勘正为族形 verbatim，零格已燃如实标注）；
  - **V2** = **\|IS IC_IR\| ≥ 0.30**（IC_IR = mean(IC)/std(IC)，IS 段信号日口径不年化；族形勘正同上）；
  - **V3** = OOS 同号留存：IS/OOS=2/3-1/3 分割（**IS 167 日 / OOS 83 日**，A1 修正案既定分割），OOS 段 IC 均值与 IS 同号且 |OOS 均值| ≥ 0.5×|IS 均值|（量级不塌线）。
  - 三门全过=构造合格候选（注册面另行：晋升策略批=新 prereg 事务，本件只出 IC 合格面）；资格信号日 N≥150 未达=该构造 NOT-ELIGIBLE 诚实腿败。
- **硬界设计三件套【D-20260925-01①】**：(a) 极端日检测以 **median/p99.9 分布界**承担主责（逐构造单日 |IC| 与日 universe 覆盖数分布界），禁裸 max 作主判；(b) max 硬界须配涨跌停感知豁免：涨停潮/熔断级单日=结构性双截断（档位净流入极端化+前向收益被锁价截断）≠数据腐坏，豁免逐日单列披露（单点删除优先于整批判负）；(c) 极端日先验见 §5④。
- G1'/G2 注册面：**本批不适用**（IC 普查无 sharpe/trades 面；构造若晋升注册=彼时按 g1_prime_v2/g2_registration_v2 独立 prereg，禁跨批预支判据）。
- 保留描述性条款（批级披露不占门）：逐构造 IC 时序图数据、月度 IC 同号率、IC 衰减曲线（h1/h5/h10）。

## §5 跑前预测【必填·写死于跑前，跑后对账】

1. **方向先验**：MAIN（r0+r1 官方聚合）h10 IC 为**正**（机构 underreaction drift），量级 IC_mean ∈ [0.005, 0.04]；TIER_r3 h10 IC 为**负或近零**（噪声交易反向）；TIER_r0 与 MAIN 同号但 |IC| 更大或相当（r1 稀释假说 vs r1 增益假说两可，实证裁决）。
2. **档位梯度先验**：|IC(h10)| 梯度预期 r0 > r1 > r2（大单信息含量递减；r3 单独反向腿）。
3. **null 基线先验**：K=100 置换 null 的 p95(IC) ≈ 0.015-0.03（大横截面紧致）；V1 门槛预期落在 0.02-0.03 区；V2 门槛 0.30 对应 t-stat ≈ 0.30×√N（N=240 ⇒ t≈4.6）量级合理。
4. **极端日先验（三件套 (c)）**：窗内（≈2025-09→2026-09）已知 2026-01-19 极端溢价日族在册（REGIME_GUARD_DEEP_REPLAY D-C 实证族）+ A 股 2025-2026 高波动日（涨跌停潮/指数级跳空）将产生：单日 |IC| 极值（可击穿朴素 max 硬界）、档位净流入极端化（|net| 量级跃迁）、横截面覆盖骤变（停牌/一字板）。此类日=**结构性非腐坏**，按 §4(b) 豁免路径逐日单列；判线主责=median/p99.9 分布界。

## §6 产物（跑前面·工程注记）

- **script 已落地**：scripts/sina_construct_ic.py（run/selftest 双命令；selftest 9/9 PASS 于冻结 commit 前=hermetic tmp sandbox 零真数据（r116/T-46 R99 豁免先例）；run 面 §2 完备门=sina_mf_accept verdict PASS+面板 complete+n_symbols≥5,000+资格信号日≥150，门未开诚实 exit 2 零计算零落盘）。
- 产物面（跑后回填 §7）：results/shortline/sina_construct_p1.json（顶层 evidence_cutoff=C2 合法键）+ research/shortline/sina_construct_p1_results.csv 行级 IC 面。
- **工程注记（跑前最终化窗内落定）**：§0「跨轮 checkpoint」按池 C8 语义收口=单程确定性 L1（预估 10-20min）池监督下预占即整跑重启（C8 自动续批），**无中途状态面**——<20min 单程的 checkpoint 状态面风险>预占风险，工程判定留痕；批报告 audit 段必带（runtime/machine/process_model/rows_scanned/accept_ts/latent_repull_defect_note 披露）。

## §7 跑后实证（占位——写数字即造假）

（一次定稿；确定性引擎产物写 bug 的合法重执行口径≠结果重跑；工程修复重跑双跑留痕如实记账）

## §8 批后复盘（占位·s7-T）

（预测对账（对/部分/错）+门禁链损耗账 results/gate_attrition.json 追加一行+判线当批读数+回执入轮报告+CODELY 行级追加；若构造晋升注册：注册件带 evidence_cutoff+SIGNAL_BUILDERS 接线+smoke 锚定门复跑）

## §9 与在册面的关系声明（防重复铁律）

- **MF_IC_P1（EM 面）**：维持 parked 诚实等待（MSG-1210 option-(c)①原文），本批不判死不删档不替代；EM 面复活时两族并行在册，D6 实证（§1）裁决同构性，相关性来源=量纲不同构（R118）+官方配方聚合（R225）。
- **THS_AGG_P1 / LHB 族**：D6 对照面（§1 清单），非竞争面。
- 本批五构造与任何在册交易员 sleeve 无注册关系（注册=未来新 prereg 事务）。
