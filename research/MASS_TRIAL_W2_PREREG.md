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

## §7 跑后实证（2026-10-03 16:5x-17:2x bm-c·一次定稿·freeze ec9a49711 后三执行体接力烧毕·r422 四代收口）

- **4836 候选全筛 → 806 存活（16.67%）**；75 对照 + 20 nulls + 2 signal_error（DEF-26/27=month 必填位缺陷行·与 w1 逐字同缺陷冻结携带·候选面零误差）；账本 617500→622336（+4836·LOWAMP-P1/P2 voids 随链带入）。
- **null 面**：p50=0.4667·p95=0.5333·max=0.55——全数 < 0.60 初筛线 ✓，裕量 0.05 与 w1（0.047）同薄如实披露；随机入场靠熊窗现金态刷近线的结构性友好不变，stage-1 只当漏斗非判决。
- **R 轴效应**：bear 573/1650=34.7% vs none 142/1644=8.6% vs bull 91/1542=5.9%——bear/none≈**4.03×**（w1 36.7% vs 9.0%≈4.1× 复现）；S=delever 21.2% vs full 12.1%、T=weekly 20.1% vs daily 13.1%（方向与 w1 全同）。
- **存活族谱**：seasonal 33% / event 22% / folk 20% / patterns 19% / ta 17% / sentiment 14% / mean_reversion 12% / volatility 11% / macro 11% / momentum 10% / trend 9%——反转/形态/日历/民间支配、趋势/动量弱，w1 判决面富集方向全复现。
- **对照面 5/75 过线**：low_vol_long 0.6167 · island_reversal 0.60 · morning_star 0.60 · vol_drought_reversal 0.6333 · ants_climb 0.60。
- **对照面 w1→w2 漂移注记（诚实披露·归因实证）**：67/75 默认行 beat 值位移（非一致方向）——同 evidence_cutoff 2026-09-22 同默认参数下不同值=评估栈窗内变更所致，非数据面污染：**RW-1 出场前视修复**（出场由 close 时点改 T+1 开盘成交·eaed0a1d7 r472 bm-a 09-30）+ **D-38 一字板买拒/卖延**（58ff49bf1 r479）+ **RW-3 引擎缺省翻面 full-pnl & strict_open_fills**。w2=修正引擎上首个 mass 面；w1 对照读数=旧前视引擎历史面按冻结纪律不回改；注册员底座族 ENGULF/NEEDLE 的 OOS Sharpe 在 RW-1 修复披露表内已示大降（0.3835→0.1686 / 0.4089→0.1927），与本波两族默认行跌线（0.5833 vs 线 0.60·差 1 窗）同因一致。
- top 读数仅披露不采信：最高 beat 0.6667 两席（W2-13005 momentum.relative_strength_rotation bull/t7/full/weekly·Sharpe 0.26；W2-51025 patterns.doji_at_low bear/t7/full/weekly·Sharpe 0.63）。

## §8 批后复盘（r422 四代执行体收口·16:0x-17:2x）

- **预测对账（§5 六条）**：①存活率 10-18%→实测 16.67% **对**（w1 17.0% 同带）；②bear/none 2-4×→实测 4.03× **上缘擦边过**；③族谱方向→**对**；④null p50∈[0.30,0.50]→0.4667 **对**、p95<0.60→0.5333 **对**；⑤默认对照 5-12 带内→5=**带下缘对**，但「四底座默认再过线」**部分错**（low_vol/drought 过、engulf/needle 差 1 窗跌出=RW-1 修复后估值降格的自然后果·非筛面杀已证族）；⑥跨波去重坍缩预期 0-5→实测 206+73=**279·错 55×**（机制如预测=枚举/小整数参数空间离散碰撞，但规模严重低估——Sobol 延拓窗与首帧同参数范围重抽·大枚举族面碰撞规模化发生；按 prereg 预设披露路径如实上报）。
- **损耗账**：gate_attrition.json 追加行（delta 4836·eliminated 4030·ledger_total_after 622336）；生成端=拒收 8 · 波内 param_dupes 370 · signal_dupes 1071 · dead_signal 221 · 跨波 param 206/signal 73 · quota_short 3 族（holiday_effect 28 / gap_fill 29 / inside_bar_breakup 27）→ enrolled 4836 ≤ 4950 ceiling；判线三条款（0.60/30/−0.35）全批恒定未调。
- **复跑纪律**：w2_screen_checkpoint.jsonl 4931 行逐行留存（候选 4836+对照 75+null 20）；finalize 幂等复跑确认（prev complete 含 ledger→链线性保持零重计）；§9 s3 段冻结前禁烧存活者。
- **跨波可比性注记**：w1 screen=旧出场前视引擎面（09-27）、w2 screen=RW-1 修正引擎面（10-03）——两波筛面读数**非同栈可比**（对照漂移 67/75 行为实证）；s3 判决面（≤10-06/10-08 锚）将在修正栈上烧，w2 存活者与修正栈同栈零迁移成本；w1 存活者判决面历史结果（0/166）按当时冻结口径收档不重开。

## §9 s3 全量判决面段冻结位（占位——具体判线/种子/分片在 s3 跑前以追加节 commit 冻结后才许烧）

- 与 w1 §9/§9.1 同构：T-22 caliber 逐虚拟起点 × {6m,12m,24m} × x2 成本 × bear/bull/chop 分段 × 双 nulls≥2000；波级多重校正强制（**N_eff 跨波累计不重置**：链头实读——w1 SCREEN 975+w1 JUDGE 166+本波 SCREEN N_w2 全计入）；判据调 science_gates.g1_prime_v2/g2_registration_v2 共享库禁手抄；出场轴门同 §3 声明；新 judge 种子带届时按 R250 一步律注册。
- **排产锚**：本段冻结+池面判决烧录在飞 ≤2026-10-06（O-2115 验收「千人 wave-2 判决面在飞」10-08 治理日前置）。

### §9.1 s3 全量判决面段冻结【2026-10-03 18:0x bm-c r423 起草·本 commit 后才许烧·append-only·占位节留档】

- **触发与身份**：本节=§9 占位的具体化（跑前 commit 冻结·R99 纪律）；对应批件=**MASS_TRIAL_W2_JUDGE**（第二段判决批·judged cells 入账本）；排产锚=冻结+池面烧录在飞 ≤2026-10-06（O-2115 验收 10-08 治理日「千人 wave-2 判决面在飞」）。
- **判决对象与入场去重门（§1 承诺门）**：**806** stage-1 存活者（冻结清单=`results/mass_trial/w2_screen_summary.json` survivor_ids·candidates sha16 锚=**1a8751ed16a9c641** 实读禁手抄）→ 入场前**逐对 |corr|≥0.999 leg-L base-face 日收益序列塌缩**（代表=确定性最低 candidate_id·坍缩/保留清单如实披露·audit 段全量保留原始变体）→ **N_judge=塌缩后格数**（跑前零宣称）。
- **判决网格（全 import 禁重实现禁手抄·与 w1 §9.1 逐字同构）**：虚拟起点=`scripts/p5c_virtual_timepoint.py` `FROZEN_CENSUS` 双腿全网格（L 6m/12m/24m=1253/1127/875·D=3104/2978/2726·`EVIDENCE_CUTOFF_GRID`=2026-09-22 与本批 binding 同栅）× 窗 {126,252,504} × 成本 {x1=13bp 引擎默认·x2=CostPatch(2.0)（t22 Erratum-1 multiplier 律·禁直引常数）} × 政体分段 bear/bull/chop+na（T-22 §3 冻结 3-way proxy 逐字）× 双 nulls：block bootstrap **B=2000**（block=20 交易日循环块·拼样截回 n 长）+ sign-flip 置换 **P=2000**（逐日符号独立·双侧）。
- **候选重放口径**：每格=存活者冻结配置（family fn+params+axes·`w2_candidates.json` sha16 1a8751ed16a9c641 实读禁手抄）经判决机械全网格重放；被动基准=起点日已上市成员 EW buy&hold 零再平衡（p5c `passive_rel` 机械·w1 §9.1 同款）；引擎面=T+1 开盘保守代理（O-1132）·退出优先级冻结禁改；出场轴=§3 声明（③ template_default 按设计测·修正栈与 w2 screen 同栈零迁移）。
- **种子**：`mass_trial_w2_judge`=**20285200**（band 20285200..20285499·派生 `default_rng([20285200, cell_idx])`·rng 流仅限双 nulls 重采样面禁挪用·w1 judge 用途钉死先例；rg --type py 全仓扫描+SEED_REGISTRY 撞带扫描 2026-10-03 r423 零命中；**本 commit 同步登记 SEED_REGISTRY**·R250 一步律）。
- **波级多重校正（TRIAL_LABOR_LAW §4 强制·§9 承诺面）**：①N_eff **跨波累计不重置=链头实读**（sg.ledger_head() 活链头 total——w1 SCREEN 975+w1 JUDGE 166+本波 SCREEN 4836 及链上一切在批全计入 DSR 折减底数·禁手抄常数）；②**E[FP]=0.05×N_judge**（名义 α=5% 口径）如实披露——DSR≥0.95 门即按累计 N 折减后的校正门·通过者=校正后存活非名义面；③波级 PBO 聚合读数另列（跨族·CSCV 8 blocks·family=11 策略模块·<8 cells 诚实 n/a）；④跨波 N_eff 合并呈报面（w1a/w1b/w2 各自 prereg 下分立追踪+链头累计折减单源）。
- **执行面**：runner=`scripts/mass_trial_w1.py` judge 三子命令 `--wave 2`（judge-prep/judge/judge-finalize·**本冻结 commit 同窗扩展**·w1 路径字节不变·ckpt 前缀 `w2_judge_shard_*` 与 w1 shard 文件零混淆·selftest 强制 hermetic·byte-stable 复跑·import-face 复用 p5c/T-22 机械禁重写）；池批 id=**MASS-TRIAL-W2-JUDGE**·shards=4（~N_judge/4 格/片·多机分片合法）·workers ≤floor(核×0.8) BelowNormal·lane_owner=null；judge-prep（塌缩+passive 预计算·短批）冻结 commit 后即可跑·judge 烧录一律池面（长活禁轮内内联·O-20260924-2100）。
- **账本**：`science_gates.append_ledger("MASS_TRIAL_W2_JUDGE", N_judge, "mass_trial/w2_judge.json", evidence_cutoff="2026-09-22")`（prev=活链头实读禁手抄·单发守卫=complete 产物永不重计·refinalize env=MASS_TRIAL_W2_JUDGE_REFINALIZE）。
- **消费面声明**：judged 存活者 → STRATEGY_LIBRARY 注册 + TRIAL-* 纸盘上岗=**月界呈报**非本批自动面（§10 消费链不变）；本批零注册效应直至 §10 链走完。

## §10 消费面

存活者 → s3 全量判决（§9 冻结后）→ 终存活者 → STRATEGY_LIBRARY 注册 + TRIAL-* 纸盘上岗 → 月界呈报；**消费方指名（O-2115）**：千人题库供给+锦标赛臂+月考面。语法供给（TRIAL_LABOR_LAW §5）：T-86 census W2A/W2B 存活腿正式落地后并入 wave-3 面（本波开波时点未落地=按 §10「到位后并入」顺延，非阻塞）。
