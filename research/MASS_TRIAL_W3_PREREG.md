# MASS_TRIAL_W3 预注册 · 千人试用期大考 wave-3（阶段一初筛面·Sobol 延拓第三帧）· T-2026-10-03-158 消费面

> 令链：T-2026-10-03-158 post-judge 消费面（W2 判决已落·票面 note「N1 supply reopen via engine tick」=本波 prereg 冻结后生成器才有米）＋ **O-20261004-1440 §3 供料预置令**（CEO 直令点名「千人 W3」=FUND 三炉 finalize 10-05/10-06 后的下一波预置件·禁收口即断供）＋ 常设律 O-2026-09-27-2250 firm/TRIAL_LABOR_LAW.md v1.0 §1（板空/池饿/无在飞判决批=默认开下一波）＋ W2 预注册 §10 消费面预留（census 存活腿「到位后并入」顺延·非阻塞）。
> 冻结纪律（R99）：本件 commit 冻结先于任何 screen run；generate（语法延拓+去重·零回测零判据读取）与 prereg 同 commit 冻结（w1/w2 先例）。席位公示=MSG-2026-10-04-1520-bmc-ALL（15:20 先行·防撞双扫零命中）。
> 类别：**候选搜索漏斗 stage-1 = 廉价初筛面**（TRIAL_LABOR_LAW §2 两段制第一段）——单轴、单面、零判决宣称；存活者全量判决面（s3）=**独立段冻结**（§9 占位，跑前再 commit 后才许烧）。

## §0 批件身份

- 批名：MASS_TRIAL_W3 · 批内格数 = **≤4950 候选格**（75 族 × 66 上限·ceiling-not-quota）+ 75 家族默认对照 + 20 随机 nulls（对照/nulls 不计候选 N）；总帽 ≤5000（w1 §10「5000 人扩容」=上限非凑数·三波同帽）。
- 认领：票 T-2026-10-03-158（bm-c 在册·本波=该票 post-judge 消费面的供给重启腿）；机队分工面（15:0x 实读）=bm-a LHB 普收/引擎线、bm-b FUND 三炉 NULLS 烧录+finalize 10-05/10-06 正主——**本波零撞线**（F-04 席位 MSG-1520 已发）。
- 部门归属：dept:策略（生成语法延拓）+ dept:研究（初筛判据）联合。
- 算力预算（w2 实测修正·诚实锚）：w2 screen 实测 **~6.4s/行单核**（4931 行 8.8h·RW-1/RW-3 修正引擎面·非 w1 时代 0.33s 旧锚）→ 本波 ~5045 行 ≈ **9h 单核** = **长活必池件**（O-20260924-2100 分离纪律·screen 分片入池·禁轮内内联代跑·w2 三执行体接力=纪律缺口本波修正）；generate ~6500 次信号构建 ≈ 15-25min = 短批轮内合法（冻结 commit 后同轮跑）。
- 意义门三问：①研究问题=「同族 Sobol 序列第三帧 [1024,1536)（前两帧已耗 2/3 序列空间·w1 存活 166→判决 0、w2 存活 806→判决 0）是否藏有前两窗采样遗漏的存活者」——w2 §5 预测对账实证延拓窗与首帧同分布（存活率 16.67% vs 17.0%），第三帧=空间覆盖的自然延深+跨波去重基扩大到 5811 员的碰撞面测量；②消费方=千人题库供给+锦标赛臂+月考面（O-2115 指名·不变）；③语法登记簿查重=grammar_registry.jsonl 在册 w1/w2 行（本波=同面延拓新窗·非新语法·wave=w3 行同册追加）；若本波再零判决存活=族线第三连负→按负发现照报+族线关线须附新证据增量声明（U3 律）。

## §0.5 禁开方向闸【冻结时跑 Tools/banned_direction_gate.py --prereg】

- 本批机制面=冻结语法库序列延拓，正文零新数据面零禁向词面；冻结时闸退出 0 放行，命中即按闸 JSON 补例外三件套（r494 合同律），禁绕闸。

## §1 α 机制段（D6 四选一）

- [x] **行为偏差**＋[x] **风险溢价**（家族混合面·与 w1/w2 §1 逐字同源）：候选池=11 流派 75 冻结信号族（机制主张随族携带·本批不新增机制主张）；本波=**同一语法空间的序列延拓第三帧填充**——不改变机制面，只延深参数空间采样。
- **同族相关性准入（D6）**：w1/w2 判例延续=生成端参数向量哈希+信号矩阵 sha256 双层去重（坍缩即除名·如实计数），**本波跨波去重基=w1 全部 975 员 ∪ w2 全部 4836 员**（同语法禁重跑的跨波执法·任何复现即除名如实计数）；存活者入 s3 前再过逐对 |corr|≥0.999 收益序列去重（§9 段冻结时定）。

## §2 数据与面板

- 宇宙：core48 bare-code 面板（w1/w2 §2 逐字同源·data/daily 48 只 2020-01-02→cutoff）；**evidence_cutoff=2026-09-22**（D2 前向锁盒·三波同锚）；引擎 T+1 开盘执行、V1 legacy 13bp 成本恒开；数据完备门=load_core 内建。引擎栈=RW-1/RW-3 修正面（与 w2 screen 同栈零迁移·w1 旧栈史不回改）。

## §3 方法学（生成语法·冻结）

- **家族集**：与 w1/w2 逐字同源（strategies/ 11 模块 75 信号函数·源码 sha256 逐族锚定·w3_roster.json 再锚）；排除集=∅。
- **Sobol 序列延拓第三帧（w1 §3 预注册语义·w2 先例同裂）**：每族生成器种子不变（SEED_BASE=20283000+族序·已注册带零新种子），抽取窗=**[1024,1536)**——首帧 [0,512)=w1 已耗、二帧 [512,1024)=w2 已耗，**三窗序列位置互不相交**（前缀恒等+尾窗内容恒等腿机证）；离散/小整数族在参数元组层面的跨窗复现=w2 §8 已披露枚举碰撞机制（w2 实测 279 员），由跨波去重计数器除名如实计数（§5.6 预测面·selftest 有界性腿机证非穷尽性）；轴值抽自同族 RNG 流 [SEED_BASE+族序, 7919] 的 1536 长度窗取 [1024:]。
- **参数范围与成对序拒收**：与 w1/w2 §3 机械规则表逐字同源（int/float/枚举范围+PAIR_ORDER 拒收）。
- **轴系（REFINE_BENCH_LAW §2 四轴·冻结）**：R∈{none,bull,bear}×X∈{own,t5,t7,t10,t20}×S∈{full,delever}×T∈{daily,weekly}——与前两波逐字同源。
- **入册律（ceiling-not-quota）**：每族延拓窗内前 **66** 个通过双层去重+跨波去重的 draw 入册（75×66=4950≤5000）；语法消耗登记簿 grammar_registry.jsonl 追加 wave=w3 行（append-only）。
- **对照与 null**：75 家族默认对照行（w1/w2 同款）+ 20 随机入场 null（p∈{0.02,0.05}×10·seeds=**20283140..20283159**=SEED_BASE+140..+159——w1 null 用 +100..+119、w2 null 用 +120..+139，本波顺延同带空闲段·SEED_REGISTRY 值域扫描+全仓 rg 字面量扫描双零占用实证 2026-10-04 15:1x）。
- **出场轴显式门（O-20261001-1108）**：本批出场轴=**③ template_default 按设计测**——引擎缺省出场栈（RW-7 冻结优先级：signal_reversal>stop_loss>take_profit>time_decay>loss_time_stop>global_hard_limit·loss-8d/硬止-8% 随栈携带）=被测设计组成面（W1-W14/w2 先例）；X=own/tN 的候选级出场信号走 signal_reversal 层叠加。**本批 75 族零 ALWAYS-ON 家族**，故不走②禁用栈路径；缺省栈与候选信号的相互作用=本批漏斗面如实测量对象。

## §4 判据（stage-1 初筛线·跑前写死·与前两波逐字同源）

- **screen_pass = beat_rate_6m ≥ 0.60 AND n_trades ≥ 30 AND max_drawdown ≥ −0.35**（全期·engine 口径·60 窗滚动 126 交易日步长 21 vs 同窗 EW48 被动）。
- 诚实披露（w1/w2 §4 逐字延续）：单曲线开窗 beat-rate=筛面近似非 T-22 caliber；null p50/p95 随批披露；w1 实测 null p95=0.533 / w2 实测 p95=0.5333——两波同薄裕量（距线 ~0.047）如实携带；过线≠判决≠注册。

## §5 跑前预测（写死于跑前·w2 实测锚更新）

1. 存活率预测 **10-18%**（w1 首帧 17.0% / w2 二帧 16.67%——同分布实证·第三帧中心预期 ~15% 上下）。
2. R 轴 bear 门行存活率 ≈ none 行的 **2-4×**（w1 实测 4.1× / w2 实测 4.03×）。
3. 族谱方向延续：seasonal/patterns/ta/folk/event 支配存活面，trend/momentum 弱（w1 判决面富集方向 HIT+w2 全复现）。
4. null beat_rate p50 ∈ [0.30,0.50]、**p95 < 0.60**（w1 0.533 / w2 0.5333）；若 p95 ≥ 0.60 = 初筛线失效信号，如实上报冻结待裁。
5. 默认对照 8/75 过线量级应复现（w2 实测 5·带 5-12 内；注册员四底座族默认行读数=修正栈估值面·w2 两族差 1 窗跌线先例如实预期）。
6. 跨波去重坍缩预期 **150-600 员**（w2 预测 0-5 实测 279=错 55× 的教训锚：机制=枚举/小整数参数空间离散碰撞·规模随去重基扩到 5811 员与窗位移动而变——中心预期 ~300·>600 即如实披露触发机制复核）。

## §6 产物

- `scripts/mass_trial_w1.py` 扩展 `--wave 3`（generate/screen/finalize 三子命令·**w1/w2 路径字节不变**·selftest w1/w2 腿全保+w3 延拓腿新增·judge 子命令保持 --wave {1,2}=§9 段冻结后再扩）。
- `results/mass_trial/w3_roster.json`（75 族再锚·batch=MASS_TRIAL_W3）+ `w3_candidates.json` + `w3_generate_summary.json`（含跨波去重损耗账·cross_dedup_vs="w1(975)+w2(4836)"）+ `grammar_registry.jsonl` 追加 w3 行。
- `w3_screen_checkpoint.jsonl`（逐行 checkpoint 续跑）+ `w3_screen_summary.json`（顶层 evidence_cutoff+trials_ledger·§7 回填面）。
- **screen 池件**：MASS-TRIAL-W3-SCREEN-SHARD-{0..3}（4 分片·每片 ~1,261 行·pos 边界按 generate 实际 n 计算后写入 runner_args·workers=worker_cap() BelowNormal·O-1136+CPU 10% 余量令·每片 ~5-6min 墙钟@25 workers）；分片 checkpoint 追加=append-only 单文件多写者（w2 三执行体接力实证安全·finalize 按 id 去重幂等）。

## §7 跑后实证（占位·回填 source=）

- [ ] 存活率/null 面/R 轴效应/族谱/对照面/跨波去重坍缩六对账
- [ ] 损耗账行（gate_attrition.json append·delta=enrolled·eliminated=dupes+dead+rejections）

## §8 批后复盘（占位）

- [ ] §5 六条预测对账+复跑纪律（checkpoint 逐行留存+finalize 幂等复跑确认）
- [ ] 跨波可比性注记（w2/w3 同栈=修正引擎面·两波读数同栈可比——w1 旧栈史不同栈如实注记）

## §9 s3 全量判决面段冻结位（占位——具体判线/种子/分片在 s3 跑前以追加节 commit 冻结后才许烧）

- 与 w1/w2 §9(.1) 同构：T-22 caliber 逐虚拟起点 × {6m,12m,24m} × x2 成本 × bear/bull/chop 分段 × 双 nulls≥2000；波级多重校正强制（**N_eff 跨波累计不重置**：链头实读——w1 SCREEN 975+w1 JUDGE 166+w2 SCREEN 4836+w2 JUDGE 805+本波 SCREEN N_w3 全计入）；判据调 science_gates.g1_prime_v2/g2_registration_v2 共享库禁手抄；出场轴门同 §3 声明；新 judge 种子带届时按 R250 一步律注册（同 commit 登记 SEED_REGISTRY）；|corr|≥0.999 塌缩门+collapse 清单如实披露。
- **排产锚**：本段冻结+池面判决烧录在飞 ≤2026-10-12（千人 W3 判决面=O-2115 治理日常设供给线）。

## §10 消费面

存活者 → s3 全量判决（§9 冻结后）→ 终存活者 → STRATEGY_LIBRARY 注册 + TRIAL-* 纸盘上岗 → 月界呈报；**消费方指名（O-2115）**：千人题库供给+锦标赛臂+月考面。语法供给（TRIAL_LABOR_LAW §5）：T-86 census W2A/W2B 存活腿正式落地后并入下一波面（本波开波时点仍未落地=按 W2 §10「到位后并入」顺延，非阻塞）。
