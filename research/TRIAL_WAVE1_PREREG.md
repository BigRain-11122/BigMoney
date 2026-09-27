# TRIAL-WAVE1-1000 · 试用期千人批第一波 · 波级预注册（跑前冻结）

> 令源：O-2026-09-27-2245-bm-a（千人试用期令·T-2026-09-27-94）+ O-2026-09-27-2250-bm-a（TRIAL_LABOR_LAW 常设律）。
> 本件=T-94 s1 波级预注册：生成语法+漏斗规则+判据**全冻结先于任何 burn**（R99 律）。跑后只许回填 §7，禁改判据禁重跑。
> 认领：bm-c 2026-09-27 22:52（commit bf7c2090 落锁）；F-04 声明=MSG-2260-bmc-T94-s1-lane。

## §0 批件身份

- 批名：TRIAL-WAVE1-1000；批号=候选格数 N_eff 计费面=生成后 **结构性互异候选数**（目标 1000=上限非凑数，语义重复不计）；判据面批内格数=初筛存活者判决格数（s3 入判时二次计费）。
- 车道：s1 生成=本机轮内（秒级廉价）；s2 初筛=runnable_pool 分片批（workers_plan 强制）；s3 判决=pool 批。
- 部门归属：dept:策略（生成引擎）+ dept:研究（判决漏斗）联合。
- 算力预算：s1 生成 <10s；s2 初筛 ≈ 28s/候选×1000（J1 先例 616s/22 候选×1253 起点）→ 全量 ≈7.8h 单机、池分片 3 机 ≈2.6h/机（周末夜间合法烧 O-2320）；s3 判决按存活者数实报。

## §1 α 机制段（D6——候选族机制声明）

- [x] **行为偏差**：FAM-REV（oversold_bounce=反转学派模板）——超跌后短期反转溢价由处置效应/锚定付出代价（T-22 分段/T-73 反转律/O-2330 三源一致）。
- [x] **风险溢价+结构**：FAM-ROT（top_n_rotation composite=在册六员工模板族）——强势股轮动承担动量拥挤与回撤风险获得补偿。
- 本批**零新信号函数**：候选=18 注册串词表（SIGNAL_BUILDERS 精确键·未知串硬停）内既有原语 × 出场/时机参数空间随机抽取——无 D6 新机制主张，机制归属两族原语既有判决链。
- 同族相关性：批内参数近邻相关必然存在（构型同源）=N_eff 计费面非准入面；语义重复治理=§3 去重门（T-84 s3 律）。

## §2 数据与面板

- 宇宙：core48 本地日线 CSV（in-repo，零 Money02 争用，J1 先例同源）；MIN_LISTED=24。
- 栅格：**EVIDENCE_CUTOFF_GRID=2026-09-22**（P-5C 冻结两腿共用，T-22 leg-L 同栅格复用律）；FROZEN_CENSUS L={6m:1253, 12m:1127, 24m:875}（r105 探针）；WARMUP_TD/WINDOWS/{126,252,504} 全按 p5c 冻结原语 import，禁重实现。
- 数据完备门：in-runner 复用 p5c G1-G4 门（patch selftest+普查恒等+census 数+被动覆盖）。

## §3 方法学（生成语法+漏斗——冻结）

**生成语法 v1**（两族 × N≥500 抽样/族，RANDOM_LARGE_SAMPLE_LAW §2.2）：

- 族 FAM-REV：entry=`oversold_bounce(lookback=20, drop=-15%, shrink=0.8)`（judged school 模板·反转学派）。
- 族 FAM-ROT：entry=`top_n_rotation(composite, n=5, rebal_days=20)`（在册六员工模板·COMPOSITE-CE-01）。
- 随机轴（桥参+ExitPatch 域，均匀抽样·seed 基=20_920_000（FAM-REV=20_920_000·FAM-ROT=20_920_001·SEED_REGISTRY 在册·带位 rg py 扫零占用 2026-09-27·禁手挑点）：
  - `time_decay_period` ∈ 整数 {8..35}；`time_decay_threshold` ∈ [0.03, 0.09]（4dp）
  - `trailing_stop_activate` ∈ [0.015, 0.07]（4dp）；`trailing_lock` ∈ [0.03, 0.10]（4dp）
  - `take_profit_levels`：k ∈ {1,2,3}，各阶 ∈ [0.04, 0.14]（3dp）严格升序
  - `take_profit_fractions`：k 长单纯形随机（Dirichlet，3dp 归一）
  - `loss_time_days` ∈ {5, 7, 10, 16, 20}（持有期族 5/7/10/20+g2-folk 16 先例）
- **入场过滤轴与 sizing 轴 v1 延后如实披露**：SIGNAL_BUILDERS=精确键注册表，入场参变体须新注册串（新信号面治理）→ 入场参随机化与仓位法变体归 wave-2 语法扩容（TRIAL_LABOR_LAW §5 供给面：T-86 存活腿就绪后并入）。
- **去重门**（T-84 s3 律）：①生成面结构指纹=canonical JSON sha256（entry+params+exit_overrides），重复重抽（上限 10×，仍不足=诚实少于 500/族）；②报告面任意两格日收益 |corr|≥0.999 塌缩一格（sha256 持仓指纹+诚实 dedup 披露，禁转译收敛叙事）。
- 语法消耗登记簿：wave 语法哈希入册 research/TRIAL_GRAMMAR_REGISTRY.md（append-only，同语法禁重跑=防疏浚）。

**漏斗（冻结）**：

- **s2 初筛（廉价面·漏斗级非判决级）**：全史 base 面 6m 窗 × 1253 冻结起点，逐候选 beat_rate_6m（复用 T-22 leg-L 被动 checkpoint 零重算）；**初筛线=beat_rate_6m ≥ 0.55 且有效格覆盖 ≥95% census**——初筛过线≠任何判决宣称，仅进 s3 资格（funnel 披露律）。
- **s3 全量判决（存活者）**：双面（x1/x2）× {6m,12m,24m} × bear/bull/chop 分段 × 双 nulls≥2000（block bootstrap+sign-flip 并列，RANDOM_LARGE_SAMPLE_LAW §3）；G1'/G2=共享库 `science_gates.g1_prime_v2/g2_registration_v2`（禁手抄判线）；K≥1000 虚拟起点=census 1253 ✓。
- **波级多重检验强制**：DSR 按跨波累计总试验数 N 折减（TRIAL_LABOR_LAW §4·禁波间重置）；PBO 波级报告（screening/pbo.py CSCV 8 块）；预期假阳性数如实披露。N_eff 计费=初筛候选全数入计（无论过线与否）+判决格二次入计。
- **s4 上岗**：最终存活者（十至几十人量级预期，零存活=合法结局）→ STRATEGY_LIBRARY 注册 + TRIAL-<FAM>-<NN> 纸盘（O-2045 机制复用）+ 48h CEO 呈报。
- 账本：`science_gates.append_ledger` 批名 TRIAL-WAVE1-1000。

## §4 判据（引用共享库·零新判线）

- 初筛=漏斗级（0.55 线为供给闸非判据线，如实标注）；判决线全按 g1_prime_v2（skill_line 数据驱动+bootstrap CI+entries≥30）+ g2_registration_v2（DSR≥0.95·PBO≤0.25）；描述条款（年化>0/OOS 双正/回撤≥-35%/无崩年/成本压测）批级披露不替代 v2 门。
- 硬界三件套：本批候选面无健康检测判线（NAV 无检测线）→ 不适用如实披露；§5 仍给极端日先验。

## §5 跑前预测（≥3 条+极端日先验）

1. FAM-REV 族 beat_rate_6m 中位数 ∈ [0.35, 0.55]（反转原语 22 员 PROSPECT 先例 0/22≥0.70、分布重心低）——多数候选初筛不过 0.55 线=诚实大概率。
2. FAM-ROT 族 beat_rate_6m 中位数 ≥ FAM-REV（轮动族在 ORANGE 政体下相对占优面）。
3. 初筛存活者 ∈ [0, 80] 区间宽预测（参数空间近邻相关塌缩后有效族数有限）；判决存活预期 0-5 人（skill_line 数据驱动线+N 折减后极难）。
4. 极端日先验：2015-07 救市、2016-01 熔断、2024-09-30/10-08 暴涨窗——极端日 take_profit/trailing 参数面收益离散极宽，x2 成本面在这些窗的 beat 判定可能翻面；分段 bear 面长持有（20d）候选 maxDD 可达 -20% 级。

## §6 产物

- 引擎 `scripts/trial_wave_gen.py`（生成+结构去重+selftest）；
- `results/trial_wave1/candidates.jsonl`（逐候选 {cand_id, family, entry, params, exit_overrides, fp}）+ `manifest.json`（族计数/seed/语法哈希/去重披露）；
- s2 跑批件 `results/trial_wave1/screen_*.jsonl` + 汇总 JSON（顶层 evidence_cutoff=2026-09-22）；
- 账本 append + 本件 §7 回填 + 语法登记簿追加。

## §7 跑后实证（跑前必须为空——占位纪律：写数字即造假）

（待 s1 生成实跑后回填；§8 批后复盘跑后回填。）
