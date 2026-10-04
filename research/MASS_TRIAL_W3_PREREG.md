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

## §7 跑后实证（2026-10-04 16:0x-16:3x bm-a finalize·freeze c2141d6c1 后四机四分片接力烧毕 bm-c 0-2 r482 + bm-a 3 r685·分片三收养=burner-side session r488/r489 律）

- **4814 候选全筛 → 785 存活（16.3%）**；75 对照 + 20 nulls + 2 signal_error（DEF-26/27=month 必填位缺陷行·与 w1/w2 逐字同缺陷冻结携带·候选面零误差）；账本 641985→646799（+4814·LOWAMP-P1/P2 voids 随链带入）。
- **null 面**：p50=0.45·p95=0.5333·max=0.55——全数 < 0.60 初筛线 ✓，裕量 0.0467 与 w1（0.047）/w2（0.047）三波逐字同薄如实披露；随机入场靠熊窗现金态刷近线的结构性友好不变，stage-1 只当漏斗非判决。
- **R 轴效应**：bear 565/1555=36.3% vs none 140/1626=8.6% vs bull 80/1633=4.9%——bear/none≈**4.22×**（w1 4.1× / w2 4.03× 三波连续 ~4× 稳定带）；S=delever 19.2% vs full 13.5%、T=weekly 19.6% vs daily 13.1%（方向与 w1/w2 全同）。
- **存活族谱（顶 5）**：seasonal.trend_by_season 33/66=50% / sentiment.turnover_surge 25/66=38% / patterns.piercing_line 25/66=38% / seasonal.month_seasonality 24/66=36% / event.breakout_confirm 23/66=35%——日历/情绪/形态/事件支配；trend/momentum 弱（triple_ma 3% / parabolic_sar 2% / cross_sectional_momentum 2%），w1 判决面富集方向三波全复现。
- **对照面 5/75 过线**：vol_drought_reversal 0.6333 · low_vol_long 0.6167 · island_reversal 0.60 · morning_star 0.60 · ants_climb 0.60——**与 w2 五席逐字同值**（同 evidence_cutoff 2026-09-22+同修正栈 RW-1/D-38/RW-3）=**首例同栈跨波对照复现实证**（w1→w2 漂移 67/75 行的对面：同栈零漂移）；w1 旧栈读数=历史面按冻结纪律不回改。
- **跨波去重坍缩**：916 param + 358 signal = **1274 员**（入册窗 r481 已按 §5.6 >600 带披露触发机制复核·坍缩率 21.9% vs w2 28.6%=基数增长一致〔基座 5811〕）。
- **分片三收养**（r685 bm-a）：claim 15:53:07 autofill launch 27b7b826d → burn 78s 1228/1228 [3681,4909) exact → 覆盖探针 0 dup → pool flip done 16:04:54 + claim 文件；**批中坑**：bm-b 在飞分片一重烧 1227 行经 git auto-merge 回流入本地 checkpoint（6136 行·dup-id）→ 按 r482 bm-c 律 keep-first id 去重治愈（elapsed_s-only 方差·零信息损失断言过）→ finalize 前全波 id 唯一性 4909/4909 复验。
- top 读数仅披露不采信：最高 beat 0.6667 两席（W3-36043 ta.bb_squeeze_breakout·W3-72009 folk.rsi_low_flat）+ 0.65 两席（W3-00065 trend.donchian_breakout·W3-08032 mean_reversion.rsi_revert）。
- **损耗账行**：gate_attrition.json 追加 MASS_TRIAL_W3 行（delta 4814·eliminated 4029·ledger_total_after 646799）；生成端=拒收 9 · 波内 param_dupes 417 / signal_dupes 734 · dead_signal 227 · 跨波 param 916 / signal 358 · quota_short 3 族（holiday_effect 24 / gap_fill 24 / inside_bar_breakup 14）→ enrolled 4814 ≤ 4950 ceiling；判线三条款（0.60/30/−0.35）全批恒定未调。

## §8 批后复盘（r685 bm-a 收口·16:0x-16:3x）

- **预测对账（§5 六条）**：①存活率 10-18%→实测 16.3% **对**（三帧 17.0%→16.67%→16.3% 同带缓降）；②bear/none 2-4×→实测 4.22× **上缘擦边过**（三波 4.1/4.03/4.22 连续带）；③族谱方向→**对**；④null p50∈[0.30,0.50]→0.45 **对**、p95<0.60→0.5333 **对**（三波逐字同值）；⑤默认对照 5-12 带内→5=**带下缘对**且与 w2 逐字同值（同栈复现正面证据·修正栈估值面稳定的直接读数）；⑥跨波去重坍缩 150-600→实测 1274=**错 2.1×**（机制如预测=枚举/小整数离散碰撞，但 w2 教训锚上调后仍低估——基座 5811 规模化第三实证，入册窗已触发机制复核披露；按 prereg 预设披露路径如实上报）。
- **复跑纪律**：w3_screen_checkpoint.jsonl 4909 行逐行留存（dedup 后 id-unique 4909/4909 断言）；finalize 幂等复跑确认（prev complete 含 ledger→keep-as-is·SHA256 字节恒等·链线性保持零重计）；§9 s3 段冻结前禁烧存活者。
- **跨波可比性注记**：w2/w3 screen=同修正引擎栈（RW-1 出场前视修复+D-38 一字板+RW-3 引擎缺省翻面）——**两波筛面读数同栈可比**（对照面逐字同值为实证锚）；w1 旧栈史不同栈如实注记；s3 判决面将在同栈上烧，w3 存活者零迁移成本。
- **链完整性注记**：finalize 首跑撞 dup 携带面（6136 行）产出 bogus 账本块——未提交未推送，quarantine 隔离区两件（bogus+wrongprev）·science_gates.ledger_head 增 `_quarantine` 扫描排除（r685 律·selftest 新腿 70/70）；正式块 prev 641,985+4,814=646,799 单次入链幂等复验。

## §9 s3 全量判决面段冻结位（占位——具体判线/种子/分片在 s3 跑前以追加节 commit 冻结后才许烧）

- 与 w1/w2 §9(.1) 同构：T-22 caliber 逐虚拟起点 × {6m,12m,24m} × x2 成本 × bear/bull/chop 分段 × 双 nulls≥2000；波级多重校正强制（**N_eff 跨波累计不重置**：链头实读——w1 SCREEN 975+w1 JUDGE 166+w2 SCREEN 4836+w2 JUDGE 805+本波 SCREEN N_w3 全计入）；判据调 science_gates.g1_prime_v2/g2_registration_v2 共享库禁手抄；出场轴门同 §3 声明；新 judge 种子带届时按 R250 一步律注册（同 commit 登记 SEED_REGISTRY）；|corr|≥0.999 塌缩门+collapse 清单如实披露。
- **排产锚**：本段冻结+池面判决烧录在飞 ≤2026-10-12（千人 W3 判决面=O-2115 治理日常设供给线）。

## §10 消费面

存活者 → s3 全量判决（§9 冻结后）→ 终存活者 → STRATEGY_LIBRARY 注册 + TRIAL-* 纸盘上岗 → 月界呈报；**消费方指名（O-2115）**：千人题库供给+锦标赛臂+月考面。语法供给（TRIAL_LABOR_LAW §5）：T-86 census W2A/W2B 存活腿正式落地后并入下一波面（本波开波时点仍未落地=按 W2 §10「到位后并入」顺延，非阻塞）。
