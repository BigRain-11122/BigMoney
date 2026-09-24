# T27_BLEND_TOURNAMENT_V2 — 五法混合锦标赛预注册 v2（跑前冻结）

> 任务单：T-2026-09-24-27-P1（GM 署名 O-20260924-1702；bm-c r63 认领，commit 133b522）。
> 前史：v1（research/T27_BLEND_TOURNAMENT.md）run#1 VOID（roster_drift_vs_iv6，零产数，账本块 +42 保留）——bm-a T-24 PROSPECT 22 员 onboard（c87b08b8）恰在 v1 冻结与跑批之间落地；按 IV6 教义「VOID → 新预注册，禁修补重跑」开本 v2。
> 跑前冻结：本文件 commit 先于任何跑批（iron rule 3）；跑后只许回填 §7/§8，禁改判据禁重跑。

## §0 批件身份【跑前】

- 批名 / 批号：T27-blend-tournament-v2（N_eff 计数 86 格，见 §3）；前批 run#1 空转块 +42 已在链上（chain 3119 起点）。
- 认领：F-04 先行 MSG-20260924-1835-bm-c-ALL-T27-claimed.md ＋票面 flip（claimed 18:31，commit 133b522）——本 v2 同票同车道，无新 MSG。
- 部门归属：dept:研究＋组合与资金（票面 joint owner；bm-c 执行）。
- 算力预算：56 引擎格（28 成员 × x1/x2，anchor-cum-sleeve 复用）＋派生评估；workers=min(worker_cap(),12)；预估 <2min；轮内跑（<10min 批免后台化，R41 纪律）；批报告必带 audit 段。

## §1 α 机制段【D6】

- [x] **风险溢价**：混合不创造 α（P3 裁定先例）——候选收益=分散化收益＋制度段稳健性；由结构性分散支付，无人付账（票面 spec 诚实边界原文照录）。
- 同族相关性准入检查：**N/A——零新信号函数**（成员池=已注册 28 员原样，五候选均为同组 sleeve 上的权重规则）。替代披露：28 员成员 corr 矩阵＋五候选组合日收益两两 corr（描述性，不作门）。
- 池构成诚实披露：6 员 INTERN（正典 CE/DE 谱系）＋22 员 PROSPECT（level=PROSPECT、prospect.g1_pass=False、票面 spec「PROSPECT as T-24 lands」条文的直接兑现）；**方法比较在固定池上内部有效**（五法同池同窗），绝对量级读数带池稀释披露（PROSPECT 员注册面含 x2 负 Sharpe 者）。

## §2 数据与面板【跑前事实】

- 宇宙/池：core48 bare-codes（load_core）；成员=**冻结显式清单 28 员**（跑批时 set 相等，不等=VOID）：COMPOSITE-CE-01/02、DROUGHT-CE-01、ENGULF-CE-01、NEEDLE-DE-01、VOLATILITY-CE-01、PROS-ANTS-01/CE-01、PROS-BBS-01/CE-01、PROS-DOJI-01/CE-01、PROS-DUCK-01/CE-01、PROS-HAM-01/CE-01、PROS-IBB-01/CE-01、PROS-IMM-01/CE-01、PROS-MCB-01/CE-01、PROS-OVB-01/CE-01、PROS-RSRS-CE-01、PROS-TMU-01/CE-01、PROS-VOB-CE-01。全员 evidence_cutoff=2026-09-22（存储字段，跑批时逐员披露）。
- 窗口与 evidence_cutoff：成员 sleeve 截断于各自注册 evidence_cutoff（存储字段优先）；cutoff 后新 bar 不回流本批；结果 JSON 顶层 evidence_cutoff=最大成员 cutoff＋science_gates.cutoff_meta。
- 数据完备门（不过门禁跑批）：①冻结清单 set 相等门；②**双 schema 锚定门 28/28**——CE/DE 6 员走 ew6 anchor_checks 原样（in_sample/out_sample/cost_x2 注册面，ANCHOR_TOL=0.002），PROSPECT 22 员走 prospect 记录块锚（full sharpe/max_dd/n_trades＋oos sharpe/oos_trades＋x2 full_sharpe，同 ANCHOR_TOL——其注册面即 bm-a T-24 onboard anchor-repro 22/22 PASS 的记录值）；任一员破=VOID；③**双胎确定性门（CE6 作用域）vs portfolio_iv6.json**——6 员成员统计＋CE6 corr＋静态 EW-repro＋IV 权重与组合，|d|<1e-9 全等（data-drift tripwire，破=VOID 无修补重跑）。

## §3 方法学【冻结】

- 成员 sleeve：member_run_iv6 原样复用（report_num_entries=True 加性披露键；ExitPatch/CostPatch 复用零重写）。
- 五候选权重规则（全部 IS 段=OOS_START 前估计，因果；x2 面沿用 x1 冻结权重；公式逐字同 v1）：
  - **A. IV risk-budget（现行正典）**：w_i=(1/σ_i,IS)/Σ(1/σ_j,IS)（iv6_portfolio.iv_weights 逐字复用）。
  - **B. Maximum diversification**：Σ_IS⁻¹σ_IS 闭式解归一；任一分量≤0 → 确定性回退=投影梯度上升 DR 目标（2000 迭代·步长 0.005·EW 初始·best-seen 跟踪），回退即披露「局部最优非全局证明」。
  - **C. Inverse-vol × momentum 混合**：raw_i=(1/σ_i,IS)×(1+m_i)，m_i=成员 x1 sleeve IS 段累计收益；raw 负值截 0 后归一；raw 和≤0 回退 EW 披露。
  - **D. 制度条件切换**：defensive=A 权重；offensive=w_i∝max(S_i,0)（S_i=成员 x1 sleeve IS 段 Sharpe；全≤0 回退 EW 披露）；state(t−1)=major_bear（firm/risk/regime.py bear_series 单源·因果）→defensive，否则 offensive；首日缺省=normal（EW6 overlay 先例），披露。
  - **E. Equal-weight（对照）**：w_i=1/28。
- 评估语义（统一帧）：五候选一律**按目标权重日再平衡**于 28 员 inner-join sleeve 日收益（port_ret(t)=Σ w_i(t)·r_i(t)）；与正典静态 combine（buy-and-hold）语义差异=有意披露；正典连续性由 §2 门③的静态再推导腿保障，不进排名面。D 的 benefit/DR 代表权重=时间平均权重 ā_i。
- null 对照：**零**（5 固定候选零搜索；skill_line_v2 以 batch_cells=86 计多重试验线）；无新随机族→SEED_REGISTRY 零登记（g1_prime_v2 内嵌 bootstrap CI 用库正典 ci_seed=20260923，非 null 族）。
- 成本口径：V1 legacy（13bp×2 压测，x1/x2 双面）；账本=science_gates.append_ledger("T27-blend-tournament-v2", 86, ...)（dict schema 禁手抄 prev）。
- 每格入账（零假设账本）：56 引擎格＋10 排名帧格（5 法×2 成本面）＋20 窗口格（5 法×IS/IS2/bear/normal 段）=86。

## §4 判据【跑前写死】

- 主门（逐候选，全部满足才 eligible）：**G1' v2**=g1_prime_v2(Sharpe_full, 日收益, batch_cells=86, n_trades=28 员和, n_entries=28 员和)——line_ok＋CI 下界>0＋entries_ok；六条款（EW6 先例 g1_clauses）；benefit>0；DR>1；x2 存活（x2 full Sharpe>vi_bar 且 x2 IS2 Sharpe>0）；稳健（IS Sharpe>0 且 worst_year>−0.30）。
- 三面排名（仅对 eligible 集）：benefit（降序）／drawdown=full max_drawdown（降序=更浅）／x2 margin=x2 full Sharpe−vi_bar（降序）；**winner=三面中位秩最优，平手→benefit 面秩**；零 eligible→无 winner，正典 IV 保留（诚实披露，不降门）。
- winner 采纳=票面 item3 路线：与 IV6 采纳谱系共报告、GM 批准＋7 天否决窗后才接 paper 正典；本批零引擎改动零接线；落选者留注册为制度轮换储备，不删。
- 月度节律（票面 item4）：月界权重重算=仅用月前数据（前向锁纪律，science-audit 检查）＋成员 intake/exit 评审随月度四件套——均为 winner 批准后的常设机制，不在本批实现。

## §5 跑前预测【冻结】

1. E 对照在日再平衡帧的 full Sharpe 与静态正典 EW6 记录（6 员 1.1438）差 |Δ|≥0.15——28 员池含 PROSPECT 稀释（注册面 Sharpe 0.2-0.6 档 vs CE 档更高），方向=显著低于 6 员记录。
2. A（IV）在统一帧下仍 benefit>0（IV6 静态正典 benefit 为正的语义稳健性）。
3. B（MDP）drawdown 面优于 E（分散化率目标缩回撤）。
4. D 的 x2 margin ≥ A（防守腿在成本压测下占优方向）。
5. 至少一候选倒在三面之外的某主门（86 格 N_eff 下 line 抬升；PROSPECT 稀释压低全体绝对量级）。
6. 零 eligible 为现实可能结局（PROSPECT 员 x2 负 Sharpe 者拖累 x2 存活与 vi_bar 面）——若发生即「无 winner、正典 IV 保留」诚实收线，不降门。

## §6 产物

scripts/t27_blend_tournament.py（v2 化：冻结清单门＋双 schema 锚＋CE6 作用域双胎门；selftest/run/status 子命令）＋ results/portfolio_blend_tournament.json（顶层 evidence_cutoff＋cutoff_meta＋audit 段）＋ research/shortline/t27_results.csv ＋ gate_attrition.json 追加行（tournament-v2 条目）＋本文件 §7/§8 回填＋run#1 存档 results/portfolio_blend_tournament_run1_void.json。

## §7 跑后实证【跑前为空——占位纪律】

## §8 批后复盘【s7-T】

- 预测对账：______；门禁链损耗账：gate_attrition 追加行 ts=______；skill_line_v2 当批读数：______；回执入轮报告＋CODELY 行级追加：______。
