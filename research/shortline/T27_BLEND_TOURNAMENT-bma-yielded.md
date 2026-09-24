> **[SUPERSEDED / YIELDED 2026-09-24 r85 bm-a]** 本文件为撞认领让路的**后到方补充卷**，已被 bm-c 正典预注册 `research/T27_BLEND_TOURNAMENT.md`（claim 133b522 %ci=18:31:16 先于 bm-a ~18:34:13，fleet README §4 commit 时间序裁定）**取代**——同批名唯一判据集=bm-c 版；本卷零格跑动零账本（p-hacking 防混淆：两套冻结判据并存时以正典为准，本卷仅留档增量设计（S28 全池层+月界前向锁协议）供 bm-c item4 增补评估）。rebase 后对应 commit=952bb79（认领+让路）/fb8df8f（本卷冻结）。

# T27_BLEND_TOURNAMENT —— 五法组合锦标赛预注册（跑前冻结）

> 权威：research/BACKTEST_SCIENCE.md（v2 判据唯一权威）＋ BACKTEST_PLAN.md 三铁律 ＋ research/COMPUTE_AUDIT.md（批纪律）。
> 模板：research/PREREG_TEMPLATE.md（T-02 6/7 载体）。本文件冻结后跑批；跑后只许回填占位节（§7/§8），改判据要重跑。

## §0 批件身份【必填·跑前】

- 批名 / 批号：`T27_BLEND_TOURNAMENT`（组合方法锦标赛；CEO 令 O-20260924-1702；票 T-2026-09-24-27，r85 bm-a 认领）
- 认领：F-04 先行——fleet/inbox/MSG-20260924-1834-bm-a-t27-claim.json（commit 626af05 即锁）；任务单引用：T-2026-09-24-27-P1
- 部门归属（dept:组合+研究）：组合与资金部＋研究部（票面 lane affinity：portfolio lane，IV6/EW6/corr-watch 谱系 bm-a R35-37）
- 算力预算：预估 <10min 单机（20 组合格 + 56 成员重放腿，BelowNormal 池，分离进程+checkpoint，R41 教训）；批报告必带 audit 段
- 格身份：5 方法 × 2 层（S6 canon / S28 全池）× 2 成本面（x1/x2）＝**20 组合格 = N_eff 20**（零假设账本：格=试验）；成员腿 56 次 = 记录格重放（t24_prospect_onboard 先例，ledger_trials_added=0，engine_runs=56 披露）

## §1 伪机制段【必填·D6】

**本批不注册新信号函数**——五候选全部为**权重变换**（对在册成员收益流的再分配），不新增 SIGNAL_BUILDERS、不进注册池。诚实边界（票面逐字）：blending does not create alpha（P3 verdict：IV shrinks risk only）——真实收益面=分散化 benefit + 政体稳健性；因子准入门（D1-D7）零改动。

- 四选一：不适用声明（非新信号批；无新 α 机制主张——组合层收益主张=分散化/风险重分配，上句已载）。
- **同族相关性准入检查（D6 披露律照跑）**：本批产物为组合方法而非新信号，`max|corr|≥0.7 拒收门`不触发；改跑**披露律**——①五法组合日收益两两 max|corr|（皮尔逊，日收益口径，sleeve-tag 先例）逐对披露；②胜者组合 vs 在位 IV6 canon 组合（results/portfolio_ew6.json 同窗重derive）max|corr| **≥0.95 = 同构改名披露**：canon 更替需胜者在三面（benefit/dd/x2 边际）全面 ≥ 平，否则 canon 维持 IV6（防「换名不换实」）。

## §2 数据与面板【必填·跑前探针事实，非结果】

- 宇宙/池：core48 裸码面板（live.paper.load_core，48 ETF，1631 bars，2020-01-02..**evidence_cutoff 2026-09-23**）；cutoff 后新 bar 锁定不得回流本批
- 结果 JSON 顶层必须带 `science_gates.cutoff_meta(cutoff)` 字段（缺字段=science_audit C2 VIOLATION）
- 成员池（冻结清单，跑时若漂移=中止）：
  - **S6 canon 层＝注册 6 员**：COMPOSITE-CE-01/02、DROUGHT-CE-01、ENGULF-CE-01、NEEDLE-DE-01、VOLATILITY-CE-01（全 INTERN；PAPER_LEVELS 面）
  - **S28 全池层＝6+22 PROSPECT**（firm/traders/ 全量枚举 2026-09-24 探针 28 员）；PROSPECT **研究域权重**（组合评估面），实盘 allocation 恒 0 硬边界不变（hr.py 断言照跑）
- 探针产物：results/shortline/t27_grid_probe.json（格数/成员清单/线值快照/窗界），跑前冻结计数=跑时漂移门（p5c 普查漂移门先例：活面板不复现冻结计数即中止）
- 数据完备门（不过门要跳批）：成员 28/28 文件在位＋params.entry 键 ∈ SIGNAL_BUILDERS＋smoke 23/23

## §3 方法论【必填】

- 成员腿：28 成员 × {x1, x2} = 56 次成员级重放（p3_portfolio.member_run 路径=t24 先例；CE 成员 = CE 参数合并 + ExitPatch loss_time_days 16 逐字）；重放=门非试验（账本 0）
- **统一月界前向锁协议**（五法同规，票面 §4 迭代循环纪律直接入批）：每月界 m（面板月首 bar）重算权重，输入=**严格 m 前数据**（trailing 63 交易日）；月内权重持有不动；warmup（首 63 交易日）内一律 EW（计数披露）；权重数据不足月=该月 EW（计数披露）
- 五法冻结定义（层内归一，long-only，Σw=1）：
  - **A. IV 风险预算（在位 canon）**：iv_weights()（p3_portfolio 原函数逐字）作用于 trailing 63d 成员日收益
  - **B. 最大分散化 MDP**：最大化 (wᵀσ)/√(wᵀΣw)，σ/Σ=trailing 63d；scipy SLSQP long-only Σ1，确定性初值=EW；收敛失败月=EW（计数披露）
  - **C. 逆波动×动量混合**：w_i ∝ (1/σ_i)·max(m_i,0)，σ_i/m_i=trailing 63d vol/return；m_i≤0 成员该月剔除；全剔除月=纯逆波动回退（计数披露）
  - **D. 政体条件双册切换**：状态源=v3_state_series（T-21 calibration import-replay 原语，月界取 m−1 收盘态）；GREEN→全层逆波动；YELLOW/ORANGE/RED→仅防御册（trailing 252d max_dd ≥ −10% 成员，m−1 数据）逆波动；防御册 <2 员→全层逆波动（计数披露）
  - **E. EW 对照**：恒 1/N
- 成本口径：**V1 legacy 锚定复现**（13bp×2）；x2 面=CostPatch(2.0) 乘子语义（R2c 已验 p5c L217/L306 逐字同 idiom）；月界重算不引入新成本事件（权重变换=簿记面）
- null 对照：**K=0 不适用**（P3 先例逐字：无新信号、无参数搜索→随机基线不重跑；对照组=在位 canon A 法＋E 法 EW 基线，二者本批内格）；无新 seed 登记（无 null 族；CI seed=20260923 = g1_prime_v2 缺省共用，SEED_REGISTRY 查毕 2026-09-24 不占新基）
- 窗族（披露维度·三窗）：**full**（warmup→cutoff）/**IS2**（2025-01-01..cutoff；j13v2_mill IS2_START 与 live.paper OOS_START 同日 2025-01-01，双名同窗披露）/**政体分段**（510300 收盘 vs MA200 三态代理——bear=close<MA200；chop=close≥MA200 且 MA200≤其 20bar 前值；bull=close≥MA200 且 MA200 升；MA200/前值无效期=na 诚实桶。**本代理为披露用 PROXY，与 REGIME_GUARD v3 重放不同源，不参与门判**——T-22 预注册 §2 逐字复刻）
- 账本：`science_gates.append_ledger('T27_BLEND_TOURNAMENT', 20, <结果文件>, evidence_cutoff=...)`（dict schema 唯一，要按 prev；成员重放腿不入 N）

## §4 判据【必填·跑前写死，禁看结果调线】

每法×层×面格跑六条款（EW6/IV6 六条款先例＋v2 共享库）：

- **c1 line_ok**：组合 full Sharpe > skill_line_v2（数据驱动线，**禁手抄数**——O-2250 单源律；探针快照 N_eff=20 时 0.9408 仅供探针留痕）
- **c2 ci_ok**：stationary bootstrap CI 下界 > 0（g1_prime_v2 内嵌，ci_seed=20260923）
- **c3 trade_gate**：entries ≥ 30（T6 双口径 entries_ok 基准；组合口径=Σ成员 entries 于该窗）
- **c4 x2_survive**：x2 面 full > vi_bar(0.4004) **且** x2 面 IS2 Sharpe > 0（sleeve_p3 c4 先例逐字）
- **c5 benefit > 0**：组合 full Sharpe − 加权均值成员 Sharpe（权重=该格 full 窗时间均值权重）
- **c6 DR > 1**：c5 同分母商

**法级 PASS** = 六条款全过（**在 S6 canon 层 x1+x2 双面**）；S28 层=稳健性披露层（同判据照算照报，不选优——禁跑后择层）。
**描述性条款照报**（批级披露非门）：年化>0、IS2 双正、回撤≥−35%、无崩年（≤−30% 年）、逐年稳定——v2 门不替代。

**排名律（冻结局）**：PASS 法集合内（S6 x1 面）三面合成排名——benefit 面 / drawdown 面（max_dd 浅者优）/ x2 边际面（x2 full − vi_bar 大者优）——每面名次 1..K，**合成=三面名次和，低者胜**；平手裁决链冻结局：benefit 名次→x2 边际→drawdown→DR。**稳健性共必要**：胜者 IS2 双正（Sharpe>0 ∧ 年化>0）+ OOS(=IS2 同窗) Sharpe>0 + 政体分段全披露（无门，段读数如实）。
**胜者即 paper-canon 组合方法**（与 IV6 采纳谱系 co-report，GM 批准+7 天否决窗）；败者=政体轮换储备册登记不删（票面逐字）。§1 同构改名披露律适用。**canon 更替落地=另行接线票**（月界重算进 S6 链），本批止于判定。

## §5 跑前预测【必填·≥3 条·跑后对账】

1. **A 法（IV canon）六条款 PASS**（在位 canon 曾过 G2 注册面；S6 层）
2. **E 法（EW）benefit 面 ≥ A 法**（等权=分散化最纯载体；P3 先例 EW 为 verdict 族）但 DR 面大概率低于 A（IV 压风险≠增收益）
3. **B/C 法 line_ok 风险**：MPD/动量混合在 6 员小池易过拟合 trailing 63d 噪声——预测至少一法 c1 或 c2 挂
4. **D 法政体段读数**：ORANGE/YELLOW 态防御册收缩后 bear 段 dd 浅于 A 法（机制预期）；全段 Sharpe 不显著异于 A（册收缩=收益面中性）
5. **S28 vs S6**：PROSPECT 22 员混入后组合 Sharpe 降（多数成员 full Sharpe < 注册员；等权/逆波动都会被拖）——S28 层任一法 line_ok FAIL 概率高

## §6 产物

- runner：scripts/t27_blend_tournament.py（run/status/selftest 子命令；selftest=离线确定性门：五权重函数数学性质＋月界前向锁断言＋漂移门＋账本契约）
- results/shortline/t27_blend_tournament.json（顶层 evidence_cutoff＋audit 段：engine_runs=56/ledger+0/账本 +20）
- research/shortline/t27_blend_tournament_results.csv（逐格六条款＋三窗＋分段读数）
- 本文件 §7/§8 回填＋票面 note＋CODELY.md 行级追加

## §7 跑后实证【必填·跑前必须为空——占位纪律：写数字即造假】

（空）

## §8 批后复盘【必填·§7-T】

（空；跑后回填：预测对账逐条＋gate_attrition 一行＋账本读数＋canon 裁定建议）
