# MASS_TRIAL_W2 预注册 · 千人试用期大考 wave-2（阶段一初筛面·Sobol 延拓）· T-2026-10-03-158

> 令链：CEO 直令 O-20261002-2115 sec.一.3（「wave-1 166 存活者→判决漏斗推进+mass wave-2 生成烧批」·「尽快」提速排产令）＋ 常设律 O-2026-09-27-2250 firm/TRIAL_LABOR_LAW.md v1.0 §1（板空/池饿/无在飞判决批=默认开下一波）＋ wave-1 预注册预留面（MASS_TRIAL_W1_PREREG §3「wave-2 延深=Sobol 序列延拓=新候选非重评」＋ §10「wave-2=5000 人扩容」）。
> 冻结纪律（R99）：本件 commit 冻结先于任何 screen run；generate（语法枚举+去重·零回测零判据读取）按 census 先例与 prereg 同 commit 冻结（w1 §2 同款）。
> 类别：**候选搜索漏斗 stage-1 = 廉价初筛面**（TRIAL_LABOR_LAW §2 两段制第一段）——单轴、单面、零判决宣称；存活者全量判决面（s3）=**独立段冻结**（§9 占位，跑前再 commit 后才烧）。

## §0 批件身份

- 批名：MASS_TRIAL_W2 · 批内格数 = **≤4950 候选格**（75 族 × 66 上限·ceiling-not-quota）+ 75 家族默认对照 + 20 随机 nulls（对照/nulls 不计候选 N）；总帽 ≤5000（§10 语言「5000 人扩容」=上限非凑数）。
- 认领：票 T-2026-10-03-158-P1（bm-c 轮 422 认领即开跑·origin 票号核验零撞）；机队分工面=bm-a QUALITY-SENS 烧批在飞+settle-bug 线、bm-b 三族 NULLS 烧录在飞+moneyflow IC 认领（r620/621 报告实证）——**本波零撞线**。
- 部门归属：dept:策略（生成语法延拓）+ dept:研究（初筛判据）联合。
- 算力预算：w1 实测 0.31-0.34s/候选 × ~5045 行 / 25 workers ≈ **2-4 min**（短批·轮内合法；workers=floor(核×0.8)=25·BelowNormal·O-1136+CPU 10% 余量令）。

## §1 α 机制段（D6 四选一）

- [x] **行为偏差**＋[x] **风险溢价**（家族混合面·与 w1 §1 逐字同源）：候选池=11 流派 75 冻结信号族（机制主张随族携带·本批不新增机制主张）；本波=**同一语法空间的序列延拓填充**——不改变机制面，只延深参数空间采样。
- **同族相关性准入（D6）**：w1 判例延续=生成端参数向量哈希+信号矩阵 sha256 双层去重（坍缩即除名·如实计数），**本波加跨波去重**：param_hash 与 signal_sha256 集合并入 w1 全部 975 员（同语法禁重跑的跨波执法·w1 员任何复现即除名如实计数）；存活者入 s3 前再过逐对 |corr|≥0.999 收益序列去重（§9 段冻结时定）。

## §2 数据与面板

- 宇宙：core48 bare-code 面板（w1 §2 逐字同源·data/daily 48 只 2020-01-02→cutoff）；**evidence_cutoff=2026-09-22**（D2 前向锁盒·与 w1 同锚）；引擎 T+1 开盘执行、V1 legacy 13bp 成本恒开；数据完备门=load_core 内建。

## §3 方法学（生成语法·冻结）

- **家族集**：与 w1 逐字同源（strategies/ 11 模块 75 信号函数·源码 sha256 逐族锚定·w2_roster.json 再锚）；排除集=∅。
- **Sobol 序列延拓（w1 §3 预注册语义）**：每族生成器种子不变（SEED_BASE=20283000+族序·已注册带零新种子），抽取窗=[512,1024)——首帧 [0,512) 为 w1 已耗面，延拓窗点集与首帧不相交（探针三验 2026-10-03：前缀恒等 ✓/延拓不相交 ✓/轴流前缀恒等 ✓）；轴值抽自同族 RNG 流 [SEED_BASE+族序, 7919] 的 1024 长度窗取 [512:]。
- **参数范围与成对序拒收**：与 w1 §3 机械规则表逐字同源（int/float/枚举范围+PAIR_ORDER 拒收）。
- **轴系（REFINE_BENCH_LAW §2 四轴·冻结）**：R∈{none,bull,bear}×X∈{own,t5,t7,t10,t20}×S∈{full,delever}×T∈{daily,weekly}——与 w1 逐字同源。
- **入册律（ceiling-not-quota）**：每族延拓窗内前 **66** 个通过双层去重+跨波去重的 draw 入册（75×66=4950≤5000）；语法消耗登记簿 grammar_registry.jsonl 追加 wave=w2 行（append-only）。
- **对照与 null**：75 家族默认对照行（w1 同款）+ 20 随机入场 null（p∈{0.02,0.05}×10·seeds=20283120..20283139=SEED_BASE+120..+139——w1 null 用 +100..+119，本波顺延同带空闲段·扫描零占用实证）。
- **出场轴显式门（O-20261001-1108）**：本批出场轴=**③ template_default 按设计测**——引擎缺省出场栈（RW-7 冻结优先级：signal_reversal>stop_loss>take_profit>time_decay>loss_time_stop>global_hard_limit·loss-8d/硬止-8% 随栈携带）=被测设计组成面（W1-W14 先例）；X=own/tN 的候选级出场信号走 signal_reversal 层叠加。**本批 75 族零 ALWAYS-ON 家族**（全部=信号驱动入场/出场，非 LOWAMP-P1 判例的常开面），故不走②禁用栈路径；缺省栈与候选信号的相互作用=本批漏斗面如实测量对象。

## §4 判据（stage-1 初筛线·跑前写死·与 w1 §4 逐字同源）

- **screen_pass = beat_rate_6m ≥ 0.60 AND n_trades ≥ 30 AND max_drawdown ≥ −0.35**（全期·engine 口径·60 窗滚动 126 交易日步长 21 vs 同窗 EW48 被动）。
- 诚实披露（w1 §4 逐字延续）：单曲线开窗 beat-rate=筛面近似非 T-22 caliber；null p50/p95 随批披露；w1 实测 null p95=0.533 距线 0.047=裕量薄如实携带；过线≠判决≠注册。

## §5 跑前预测（写死于跑前）

1. 存活率预测 **10-18%**（w1 首帧实测 17.0%；延拓窗=同分布空间的更深填充，轴系/族谱不变，中心预期 14% 上下）。
2. R 轴 bear 门行存活率 ≈ none 行的 **2-4×**（w1 实测 36.7% vs 9.0%）。
3. 族谱方向延续 w1：seasonal/patterns/ta/folk/event 支配存活面，trend/momentum 弱（w1 判决面富集方向 HIT 先例：反转/形态/日历/民间 68 vs 趋势/动量 10）。
4. null beat_rate p50 ∈ [0.30,0.50]、**p95 < 0.60**（w1 0.45/0.533）；若 p95 ≥ 0.60 = 初筛线失效信号，如实上报冻结待裁。
5. 默认对照 8/75 过线量级应复现（5-12 带内）；注册员四底座族默认参数应再过线（筛面不杀已证族）。
6. 跨波去重坍缩预期 **0-5 员**（延拓点集与首帧不相交=参数复现仅可能来自枚举型小参数空间的离散碰撞；>5 即如实披露）。

## §6 产物

- `scripts/mass_trial_w1.py` 扩展 `--wave 2`（generate/screen/finalize 三子命令·w1 路径字节不变·selftest w1 腿全保+w2 延拓腿新增）。
- `results/mass_trial/w2_roster.json`（75 族再锚·batch=MASS_TRIAL_W2）+ `w2_candidates.json` + `w2_generate_summary.json`（含跨波去重损耗账）+ `grammar_registry.jsonl` 追加 w2 行。
- `w2_screen_checkpoint.jsonl`（逐行 checkpoint 续跑）+ `w2_screen_summary.json`（顶层 evidence_cutoff+trials_ledger·§7 回填面）。

## §7 跑后实证（占位·跑后一次定稿回填）

## §8 批后复盘（占位·预测对账+损耗账）

## §9 s3 全量判决面段冻结位（占位——具体判线/种子/分片在 s3 跑前以追加节 commit 冻结后才许烧）

- 与 w1 §9/§9.1 同构：T-22 caliber 逐虚拟起点 × {6m,12m,24m} × x2 成本 × bear/bull/chop 分段 × 双 nulls≥2000；波级多重校正强制（**N_eff 跨波累计不重置**：链头实读——w1 SCREEN 975+w1 JUDGE 166+本波 SCREEN N_w2 全计入）；判据调 science_gates.g1_prime_v2/g2_registration_v2 共享库禁手抄；出场轴门同 §3 声明；新 judge 种子带届时按 R250 一步律注册。
- **排产锚**：本段冻结+池面判决烧录在飞 ≤2026-10-06（O-2115 验收「千人 wave-2 判决面在飞」10-08 治理日前置）。

## §10 消费面

存活者 → s3 全量判决（§9 冻结后）→ 终存活者 → STRATEGY_LIBRARY 注册 + TRIAL-* 纸盘上岗 → 月界呈报；**消费方指名（O-2115）**：千人题库供给+锦标赛臂+月考面。语法供给（TRIAL_LABOR_LAW §5）：T-86 census W2A/W2B 存活腿正式落地后并入 wave-3 面（本波开波时点未落地=按 §10「到位后并入」顺延，非阻塞）。
