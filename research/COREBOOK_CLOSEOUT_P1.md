# COREBOOK-CLOSEOUT-P1 预注册 · 核心仓验证收口批（T-2026-10-06-174-P1 · O-20261006-1218 P1 面 · D-41 §4 五交付 · 裁定型零烧批）

> 令源：CEO 令 O-20261006-1218（SYNTHESIS-R1 主件 §四 P1「核心仓验证收口批·全计划唯一必烧项（≤300 试·入 D-41 ≤500/30d 账）」）；票 T-2026-10-06-174-P1（bm-a r774 认领）。主件=docs/synthesis/SYNTHESIS-METHODS-PLANS-R1-20261006.md。
> **批件性质（跑前写死）**：**裁定/汇编面（adjudication），非注册批，零新回测零新试验**——五交付面全部为仓内已冻结件的引用消费；唯一计算=确定性 L1 判定映射（判据族逐字对照冻结读数）。CEO ≤300 试预算=上限非配额（O-1901 意义性律：已判定的不重烧）；本批 **+0 试验**，D-41 §6-C 账维持 **324/500**（预算节省如实披露）。CROSS-START-ROBUSTNESS §1 效力边界先例（结论裁定型·非注册批）逐字适用。
> 模板=research/PREREG_TEMPLATE.md（§0-§8 全节）；跑前 commit 冻结；跑后只许回填 §7/§8。

## §0 批件身份【必填·跑前】

- 批名/批号：**COREBOOK-CLOSEOUT-P1**；批内格数=**0**（裁定面零格——引用级消费不产生任何新格；扩容即买单条款对面不适用，本批禁扩容为烧批）。
- 认领：F-04 已先行 `fleet/inbox/MSG-2026-10-06-135x-bma-ALL-corebook-closeout-claim.md`；任务板引用=T-2026-10-06-174-P1（claimed_by=bm-a·r774）。
- 部门归属：dept:研究（核心仓裁定面）／策略（消费面=配置指导）。
- 算力预算：单机内联 <1min（纯 JSON 读取+判定映射）；无 >10min 面；批报告带 audit 段。

## §0.5 禁开方向硬闸【必填·跑前】

- 跑前必须过闸：`python Tools/banned_direction_gate.py --prereg research/COREBOOK_CLOSEOUT_P1.md` → 退出 0=放行。
- 本批零新策略方向：一切被引数字均为**已判负/已交付冻结件**的引用（N1-N7 排除书面文字为引用面非执行面）；本批不开任何新回测、不重跑任何已冻结批（LOWAMP-P1/P2/P3 与 CROSS-START/ALLOC/EXCLUSION 冻结件本身禁重跑不变）。

## §0.6 出场轴显式声明【O-20261001-1108 立法·TRIAL_LABOR_LAW §4·本批强制节】

- 本批零新回测 → 三选一映射=**不适用（N/A-by-zero-burn）**；消费面出场轴逐源声明（本批零改动零重跑）：
  - E1-ETF 源批 LOWAMP-P3=ExitPatch 双通道（loss_time_days/global_hard_limit 两键·live.paper 契约·§0.6 冻结）；
  - E2/E1-stock 源批 CROSS-START-ROBUSTNESS=月频再平衡/月末日信号 T+1 开盘（Face A/B §3 冻结）；
  - ②③ 源批=ALLOCATION_POLICY_SCAN／EXCLUSION_MARGINAL 各自冻结出场轴；④⑤=L1 派生件无出场轴。

## §1 α 机制段【必填·D6】

- 机制勾选（引用面·各源批已论证，本批不新立主张）：**结构性**（四资产配置=纪律化再平衡的波动收割；排除规则=机构因 mandate/跟踪误差约束做不到的动作）＋**行为偏差**（低波防御=彩票偏好散户的对手盘补偿；行为护栏=基民 −7.43%/年行为损耗的制度化对冲）。逐源指针：ALLOCATION_POLICY_SCAN_PREREG §1／EXCLUSION_MARGINAL_PREREG §1／LOWAMP-P1 §1／BEHAVIOR_GUARDRAILS 冻结件。
- **散户凭什么赢【§1.2·必填】**：制度＋行为——①配置维度容量无限零拥挤（ORDER 定谳「唯一可赢」）②排除=机构做不到散户做得到（第一铁律）③成本-换手-税真实入账后仍站立者为真站立（统一货币 M4）；本批「赢」=把已验证结论以全起点+成本统一货币计价收口成核心仓正典。
- **同族相关性准入检查【D6】**：本批=裁定面非注册面，per-cell max|corr| 申报 **N/A 不计算**（CROSS_START_ROBUSTNESS §1 先例逐字适用——无任何单格准入/入册决策产生；消费面各源批自带 D6/probe 面：P3 d6 面/LOWAMP-P1 probe.json）。
- M1 t 面【申报】：引用面照录不重算——P3 M1 t=2.945<3.0（其 judged-negative 判据之一）；Face A t_info=2.973（informational declared non-gating）。本批无新策略主张=无新 t 面。

## §2 数据与面板【必填·跑前探针事实】

- 宇宙/池：零新数据加载。七源件（全部仓内冻结）：
  1. `results/lowamp_p3/lowamp_p3_results.json`（LOWAMP-P3·bm-b r533 finalize·E1-ETF 全起点分布源）；
  2. `results/cross_start_robustness/scan.json`（Face A·bm-c r284·E2 裁定源）；
  3. `results/cross_start_robustness/face_b.json`（Face B·bm-b r497·E1-stock 裁定源）；
  4. `results/allocation_policy_scan/scan.json`（②配置政策扫描·bm-b r474）；
  5. `results/exclusion_marginal_scan/scan.json`（③排除边际·bm-b r497）；
  6. `results/account_cost_tax.json`（④成本-换手-税·bm-a r483）；
  7. `results/behavior_guardrails/guardrails.json`（⑤行为护栏·bm-c r291）。
- **数据锚面四元组【G-ANCHOR-FACE】**：各源件的市场数据锚四元组=其各自冻结 prereg 自带（指针见上）；本批自身数据锚=七源件路径（引用锚面律：runner 记录各源件 sha256 于结果件，锚=文件路径+raw `json.load` 直读+零起算窗+零预热窗）。
- 窗口与 evidence_cutoff：**本批 evidence_cutoff=2026-09-22**（市场面源件绑定盒继承：P3/FaceA/FaceB/ALLOC/EXCL 全=2026-09-22，runner 断言）；④⑤=L1 派生件自带 cutoff 2026-09-29（零市场数据重载·如实逐面记录不并账）。本批零回流风险（不加载任何新 bar）。
- 数据完备门（不过门禁跑）：七源件全部存在+schema 键+判定键在位（P3 `starts_12m_dist`+`rolling_worst`+`verdict`；scan `conclusion_A.verdict`；face_b `conclusion_B.verdict`；ALLOC `summary.n_pass`；EXCL `cells.FULL/NONE`；COST/GRD schema 键）——任一缺失=fail-closed VOID。

## §3 方法学【必填·冻结】

- 判定映射（确定性 L1·冻结）：
  - **E1-ETF（低振幅防御袖面）**：读 LOWAMP-P3 冻结读数 `starts_12m_dist`（n=1,128 个 12m 完整窗·positive_share/median）与 `rolling_worst`（3y/5y）→ 对照 §4 三判据族；判定=guidance 面保留/撤回。
  - **E2（四资产配置底仓）**：逐字引用 `conclusion_A.verdict`（A-EQW·criteria_reads 照录）。
  - **E1-stock（低量选股）**：逐字引用 `conclusion_B.verdict`（B-FULL·criteria_reads 照录）。
  - **②③④⑤**：读各源件 verdict/summary/cells 键照录（交付态判定=键在位+数字照录；缺件=not-found 如实记）。
- null 对照（引用面零新 null）：P3 自带 same-mask K=2,000/block bootstrap B=2,000/sign-flip P=2,000；Face A/B 自带 RAND 族（A-RAND×3/B-RAND）——本批照录指针不重算。
- 成本口径（引用面照录）：ETF Face A 单线 13.041bp/边=往返 **26.082bp**（knowledge/cost_spec.py X1_RATE import 派生·各源件冻结）；股票面 V2（fee_schedule_for 前缀路由）。
- 账本（r776 三步律）：`science_gates.append_ledger(batch_name="COREBOOK-CLOSEOUT-P1", batch_trials=0, file_name="results/corebook_closeout_p1/corebook_closeout_p1.json", evidence_cutoff="2026-09-22", note=...)` → **返回块嵌入本批结果 JSON `trials_ledger` 键（写盘之前）**→ 写盘后断言 total==prev+0 → 跑后核 `ledger_head()` file 指向本批件。
- **闭合族对号声明【M3】**：本批 family_key=**corebook_closeout_adjudication**——不在 `science_gates.CLOSED_FAMILIES` 在册（open 照跑·裁定面零烧）；**被引源族 `lowamp_daily_xs`/`lowamp_deep_xs` 在册**=本批为纯引用消费面：**零重开零重跑零新证据主张**（重开通道=new_evidence_new_prereg 原样不动；本批判定为 guidance 面裁定，非族重开）。

## §4 判据【必填·跑前写死·禁看结果调线——本节为 CEO 令 2.4 措辞的直接映射】

- **E1-ETF 三判据（判据族=CROSS_START_ROBUSTNESS §4 冻结形态逐字·CEO 措辞「多数起点成立才留否则撤回」）**：
  1. `allstart_pos_share ≥ 0.50`（多数起点成立）——映射 P3 `starts_12m_dist.positive_share`；
  2. `allstart_median_cagr > 0`——映射 P3 `starts_12m_dist.median`（12m 窗=年化窗，cagr 口径披露）；
  3. `worst5y_cagr > 0`（滚动 5 年最差年化为正·Face A/B 判据族沿用法）——映射 P3 `rolling_worst["5y"]`。
  - 三全过 → **保留（guidance 面）**；任一不过 → **撤回（照报不粉饰）**。
  - **强制双标签（跑前写死·防粉饰）**：①注册面=LOWAMP-P3 verdict **judged-negative 逐字保留**+族键 `lowamp_daily_xs` CLOSED_FAMILIES 在册不动+PBO/DSR/skill_line 判负读数照录；②炉面宣称（「2,675 格显著·验证窗 +176%」）=勘探富集读数**降级披露**（N7 浅门槛律：富集≠严判确认）——核心书期望值=本批裁定面冻结读数，禁沿用 +176% 作预期。
- **E2**：`conclusion_A.verdict` 逐字（retained=保留；任何其他值=如实照录并按 CEO 措辞处置）。
- **E1-stock**：`conclusion_B.verdict` 逐字（withdrawn=撤回照报）。
- **②③④⑤**：交付态判定=源件判定/汇总键在位+数字照录（ALLOC 277/300 类读数；EXCL FULL vs NONE 读数；COST/GRD schema 交付键）；缺件=not-found 如实记（不得以引用件缺席为由静默跳过——DATA_GAP 显式律）。
- 无 G1'/G2/DSR/PBO 注册问（非注册批·CROSS-START §1 效力边界先例）；§1.4 扣搜索条款=本批零新主张面不适用，试验量归因见 §8。

## §5 跑前预测【必填·写死于跑前·跑后对账】

（源件冻结读数已 pre-read 为裁定面固有形态——预测=判定映射的预期输出，非数据预测；零未来数据风险：cutoff 2026-09-22 远在窗前）
1. **E1-ETF 三判据全过 → 保留**（预期读数带：positive_share ≈0.86≥0.50·12m 中位 ≈+3.3%>0·滚动 5y 最差 ≈+15%>0——源=P3 §7 冻结读数；若映射读数任一不过=撤回照报）。
2. **E2=retained／E1-stock=withdrawn**（与 RETAIL_QUANT_TRACK §二 #1 记录一致性预期）。
3. **七源件 cutoff 断言**：市场面五件全=2026-09-22；④=2026-09-29；⑤=anchor_evidence_cutoffs 逐面（2026-09-22/29 混合如实录）。
4. **极端日先验**：N/A（零新回测零新数据加载；引用面极端日已在各源批披露）。

## §6 产物

- `scripts/corebook_closeout_p1.py`（probe/run/selftest 子命令）；
- `results/corebook_closeout_p1/corebook_closeout_p1.json`（顶层 evidence_cutoff+science_gates.cutoff_meta+trials_ledger 块+五面判定+CEO 白话判定块）；
- 本文件 §7/§8 回填；票 T-2026-10-06-174-P1 result_ref 更新。

## §7 跑后实证【跑后回填·2026-10-06 bm-a r777】

- **五面判定落盘**（results/corebook_closeout_p1/corebook_closeout_p1.json·schema corebook_closeout_v1）：
  - **E1-ETF 低振幅防御袖=retained-guidance**（三判据全过：`starts_12m_dist.positive_share`=0.8635≥0.50 ✓·12m 窗中位 +3.29%>0 ✓·`rolling_worst["5y"]`=+15.04%>0 ✓·n=1,128 窗）；**双标签照跑前写死落账**：注册面=P3 verdict judged-negative 逐字（skill_line 1.9722/headline Sharpe 1.158/M1 t 2.945/DSR 0.2695/PBO 0.4857/deep 轴 beat 46.5% 照录）+族键 lowamp_daily_xs CLOSED 在册不动；炉面宣称（+176%/2,675 格）=勘探富集读数降级（N7）——核心书期望值=0.86 正窗占比/中位 +3.29%（12m 窗）/滚动 5y 最差 +15.04%/零崩年。
  - **E2 四资产配置=retained**（conclusion_A.verdict 逐字·A-EQW·cagr +5.69%/worst5y 为正）。
  - **E1-stock 低量选股=withdrawn**（conclusion_B.verdict 逐字·pos_share 1.0 ∧ 中位 +11.04% ∧ **worst5y −1.53% 败**→撤回；原 14.80% 单起点结论撤回照报）。
  - **②③④⑤=delivered**（ALLOC 277/300 格·n_trials 302／EXCL FULL 中位 +15.09% vs NONE +8.69%＝排除规则集 +6.4pp／COST schema 交付·cutoff 2026-09-29 如实分记／GRD 护栏交付·anchor cutoffs 混合面照录）。
- **七源件 cutoff 断言全过**（市场面五件=2026-09-22 ✓·COST=2026-09-29 ✓·GRD=anchor_evidence_cutoffs 逐面）；源件 sha256 前 16 位落结果件（引用锚面）。
- **账本三步律（r776）执法**：append_ledger 返回块**先嵌后写**→写后断言 total==prev+0（750,812==750,812 ✓）→head 复核无回退 ✓；**本批 +0 试验**，D-41 §6-C 账维持 **324/500**（CEO ≤300 额度零动用=预算节省面）。
- audit：machine=bm-a·runner=scripts/corebook_closeout_p1.py·selftest 3/3（正/负/边界三态）·banned_direction_gate ADMIT（rc0·零命中）。

## §8 批后复盘【跑后回填·2026-10-06 bm-a r777】

- **预测对账（§5 vs §7）**：①全对——E1-ETF 三判据全过 retained-guidance（0.86/3.29%/15.04% 与预期带逐位符）；②全对——E2 retained/E1-stock withdrawn 与 RETAIL_QUANT_TRACK §二 #1 记录一致；③全对——七源件 cutoff 断言按预测形态（市场面 09-22/COST 09-29/GRD 混合）；④N/A 面未触发。**4/4 对·零 MISS**。
- **门禁链损耗账**：`results/gate_attrition.json` 追加一行（kind=adjudication·零烧裁定面：banned_direction ADMIT→freeze 4f60b9d1a→probe 7/7→run rc0——零损耗零逃逸）。
- **试验量归因【§1.4/D-41 §6-C】**：本批新增试验 **0**（裁定面=已判定不重烧·O-1901 意义性律执法；CEO ≤300 预算零动用·账 324/500——30 天窗余额 176 留给 10-31 月界考面与纸盘晋升面）。
- **核心书收口读数（CEO 白话）**：站住的=四资产配置（保留）+低振幅防御袖（保留作配置指导·不能当在册策略）+第一铁律排除规则（+6.4pp 成立）；撤回的=低量选股 14.80%（滚动 5 年最差为负）；已交付=配置扫描/排除边际/成本税账/行为护栏。**期望值修正**：核心仓预期=配置+排除的温和正收益（+5.7%/年中位·零崩年口径），非炉面 +176% 勘探读数。
- **下游消费面**：10-31 月界首考（六员+SYSTEM-V1 判决）与纸盘晋升面按本批判定件消费；E1-ETF 注册重开通道=new_evidence_new_prereg 不变。
- 回执入轮报告 r777；票 T-2026-10-06-174-P1 result_ref=results/corebook_closeout_p1/corebook_closeout_p1.json。

- **跑前冻结=本件 commit**（freeze hash=4f60b9d1a）；冻结后禁改判据；回填限 §7/§8。
