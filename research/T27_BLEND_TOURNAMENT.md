# T27_BLEND_TOURNAMENT — 五法混合锦标赛预注册（跑前冻结）

> 任务单：T-2026-09-24-27-P1（GM 署名 O-20260924-1702；bm-c r63 认领，commit 133b522）。
> 权威链：research/BACKTEST_SCIENCE.md（判据唯一权威）＋ BACKTEST_PLAN.md 三铁律 ＋ 本模板 §协议。
> 跑前冻结：本文件 commit 先于任何跑批（iron rule 3）；跑后只许回填 §7/§8，禁改判据禁重跑。

## §0 批件身份【跑前】

- 批名 / 批号：T27-blend-tournament（N_eff 计数 42 格，见 §3 账本节）。
- 认领：F-04 先行 MSG-20260924-1835-bm-c-ALL-T27-claimed.md（fleet/inbox/）＋票面 flip（claimed 18:31，commit 133b522）。
- 部门归属：dept:研究＋组合与资金（票面 joint owner；bm-c 执行）。
- 算力预算：12 引擎格（6 成员 × x1/x2，anchor-cum-sleeve 复用）＋派生评估；workers=min(worker_cap(),12)（O-1612 满载池纪律=parallel_runner 现行 worker_cap 口径）；预估 <10min；分离 pythonw 后台跑＋自写日志（零窗律），轮内收割或下轮指针。

## §1 α 机制段【D6】

- [x] **风险溢价**：混合不创造 α（P3 裁定：IV 只缩风险）——候选收益=分散化收益（横跨成员特异风险的重组）＋制度段稳健性；由结构性分散支付，无人付账（诚实边界，票面 spec 原文照录）。
- 同族相关性准入检查：**N/A——本批零新信号函数**（成员池=在册 6 员不变，五候选均为同一组 sleeve 上的权重规则）。替代披露：五候选组合日收益序列两两 corr 矩阵（描述性披露，不作门）；成员层 corr 沿用 IV6 记录口径（双胎门复算对账）。

## §2 数据与面板【跑前事实】

- 宇宙/池：core48 bare-codes（load_core）；成员=在册 6 员（与 portfolio_iv6.json roster 逐员相等，不等=VOID）；PROSPECT 不入本批（T-24 slice-2 bm-a 在飞；月界 intake 归票面 item4 常设节律）。
- 窗口与 evidence_cutoff：成员 sleeve 截断于各自注册 evidence_cutoff（存储字段优先，预期 2026-09-22）；cutoff 后新 bar 不回流本批；结果 JSON 顶层 evidence_cutoff=成员 cutoff 最大值＋science_gates.cutoff_meta。
- 数据完备门：①roster 相等门 ②双胎确定性门 vs portfolio_iv6.json（成员统计/corr/EW 静态再推导/IV 权重与组合，|d|<1e-9 全等；data-drift tripwire，破=VOID 无修补重跑）③anchor/x2 锚定门（全员 anchor_ok+x2_ok，破=VOID）。

## §3 方法学【冻结】

- 成员 sleeve：member_run_iv6 原样复用（report_num_entries=True 加性披露键；ExitPatch/CostPatch 复用零重写）。
- 五候选权重规则（全部 IS 段=OOS_START 前估计，因果；x2 面沿用 x1 冻结权重）：
  - **A. IV risk-budget（现行正典）**：w_i=(1/σ_i,IS)/Σ(1/σ_j,IS)（iv6_portfolio.iv_weights 逐字复用）。
  - **B. Maximum diversification**：Σ_IS⁻¹σ_IS 闭式解归一（σ_IS=IS 段成员日收益波动向量，Σ_IS=协差阵）；任一分量≤0 → 确定性回退=投影梯度上升 DR 目标（2000 迭代·步长 0.005·EW 初始·循环序冻结），回退即披露「局部最优非全局证明」。
  - **C. Inverse-vol × momentum 混合**：raw_i=(1/σ_i,IS)×(1+m_i)，m_i=成员 x1 sleeve IS 段累计收益；raw 负值截 0 后归一。
  - **D. 制度条件切换**：defensive=A 权重；offensive=w_i∝max(S_i,0)（S_i=成员 x1 sleeve IS 段 Sharpe；全≤0 回退 EW 披露）；state(t−1)=major_bear（firm/risk/regime.py bear_series 单源·因果）→defensive，否则 offensive；首日状态缺省=normal（EW6 overlay 先例），披露。
  - **E. Equal-weight（对照）**：w_i=1/6。
- 评估语义（统一帧）：五候选一律**按目标权重日再平衡**于 inner-join 成员 sleeve 日收益（port_ret(t)=Σ w_i(t)·r_i(t)）；与正典静态 combine（buy-and-hold）语义不同=有意披露（可变权重的唯一一致因果实现；正典连续性由双胎门的静态再推导腿保障，不进排名面）。D 的 benefit/DR 代表权重=时间平均权重 ā_i。
- null 对照：**零**（5 固定候选零搜索；skill_line_v2 以 batch_cells=42 计多重试验线）；无新随机族→SEED_REGISTRY 零登记（g1_prime_v2 内嵌 bootstrap CI 用库正典 ci_seed=20260923，非 null 族）。
- 成本口径：V1 legacy（13bp×2 压测，x1/x2 双面）；账本=science_gates.append_ledger("T27-blend-tournament", 42, ...)（dict schema 禁手抄 prev）。

## §4 判据【跑前写死】

- 主门（逐候选，全部满足才 eligible）：**G1' v2**=g1_prime_v2(Sharpe_full, 日收益, batch_cells=42, n_trades=成员和, n_entries=成员和)——line_ok＋CI 下界>0＋entries_ok；六条款（EW6 先例 g1_clauses：i>p95 线·ii 年化>0·iii dd≥门·iv 交易数≥门·v IS2 双正·vi>被动）；benefit>0；DR>1；x2 存活（x2 full Sharpe>vi_bar 且 x2 IS2 Sharpe>0）；稳健（IS Sharpe>0 且 worst_year>−0.30）。
- 三面排名（仅对 eligible 集）：benefit（降序）／drawdown=full max_drawdown（降序=更浅）／x2 margin=x2 full Sharpe−vi_bar（降序）；**winner=三面中位秩最优，平手→benefit 面秩**；零 eligible→无 winner，正典 IV 保留（诚实披露，不降门）。
- winner 采纳=票面 item3 路线：与 IV6 采纳谱系共报告、GM 批准＋7 天否决窗后才接 paper 正典；本批零引擎改动零接线。落选者留注册为制度轮换储备，不删。
- 每格入账（零假设账本）：12 引擎格＋10 排名帧格（5 法×2 成本面）＋20 窗口格（5 法×IS/IS2/bear/normal 段）=42。

## §5 跑前预测【冻结】

1. E 对照在日再平衡帧的 full Sharpe 与静态正典 EW6 记录差 |Δ|<0.15（成员波动同量级→语义差小）。
2. A（IV）在统一帧下仍 benefit>0（IV6 静态正典 benefit 为正的语义稳健性）。
3. B（MDP）drawdown 面优于 E（分散化率目标缩回撤）。
4. D 的 x2 margin ≥ A（防守腿在成本压测下占优方向）。
5. 至少一候选倒在三面之外的某主门（42 格 N_eff 下 line 抬升；五法非全部同质）。

## §6 产物

scripts/t27_blend_tournament.py（selftest/run/status 子命令）＋ results/portfolio_blend_tournament.json（顶层 evidence_cutoff＋cutoff_meta＋audit 段）＋ research/shortline/t27_results.csv ＋ gate_attrition.json 追加行（tournament 条目）＋本文件 §7/§8 回填。

## §7 跑后实证【跑后回填——run#1 唯一产数跑】

- run#1（2026-09-24 18:39:38）：**VOID（roster_drift_vs_iv6）**——冻结后 S0 拉取带入 bm-a R84（c87b08b8）T-24 PROSPECT 22 员 onboard（firm/traders/ 6→28），票面 spec 预期的「PROSPECT as T-24 lands」恰在冻结与跑批之间落地；roster 相等门（§2 门①）诚实跳闸。
- run#1 计算足迹=**零**（roster 门在任何引擎跑之前跳闸；elapsed 0s、sleeve 零格、CSV 0 行）；账本块 +42 保留为已尝试批件身份（EW6 voided-attempt 先例对完成计算者计数；本例零计算=保守方向的诚实披露，未来 skill_line 因 N_eff 增大只会更严不会更松）；chain 3077→3119；gate_attrition 条目 #13（void=true 如实）。
- 无修补重跑：按 IV6 双胎门教义「mismatch => batch VOID, no verdict, no repair-rerun (new prereg instead)」→ 预注册 v2（research/T27_BLEND_TOURNAMENT_V2.md，池=冻结 28 员显式清单）。
- run#1 产物存档：results/portfolio_blend_tournament_run1_void.json（v2 跑批前改名保全）。

## §8 批后复盘【s7-T】

- 预测对账：**N/A**（零产数跑，五预测原样转入 v2 §5 继续对账）；门禁链损耗账：gate_attrition #13 已入（kind=tournament·void）；skill_line_v2 当批读数：未触达（roster 门前跳闸）；回执入轮报告 r63 bm-c＋CODELY 行级追加：已入。
- 根因坑录（P0/E1 级）：**预注册 §2 的池定义引用了跑批时刻会漂移的活状态（在册名单）而非冻结显式清单**——bm-a T-24 onboard 与本批同窗竞速（合法双车道），冻结的 roster 断言在跑批时已被正典推进推翻；v2 修正=显式 28 员 ID 清单冻结（r62「消费冻结探针的批必设普查漂移门」坑律的 roster 版）。

