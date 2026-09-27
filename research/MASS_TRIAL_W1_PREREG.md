# MASS_TRIAL_W1 预注册 · 千人试用期大考 wave-1（阶段一初筛面）· T-2026-09-27-94 s1+s2

> 令链：CEO 直令 O-2026-09-27-2245（千人试用期交易员令）＋ O-2026-09-27-2250（常设律 firm/TRIAL_LABOR_LAW.md v1.0）· 票 T-2026-09-27-94-P1 · bm-a R362 认领即开跑。
> 冻结纪律（R99）：本件 commit 冻结先于任何 screen run；本批 seed base `mass_trial_w1=20283000` 已于同一冻结窗先注册（science_gates.SEED_REGISTRY，撞带扫描零命中）。
> 类别：**候选搜索漏斗 stage-1 = 廉价初筛面**（TRIAL_LABOR_LAW §2 两段制第一段）——单轴、单面、零判决宣称；存活者的全量判决面（s3）= **独立段冻结**（本件 §9 追加节，跑前再 commit）后才烧。

## §0 批件身份

- 批名：MASS_TRIAL_W1 · 批内格数 = **975 候选格**（每格计入 N_eff）+ 75 家族默认对照 + 20 随机 nulls（对照/nulls 不计候选 N）。
- 认领：F-04 MSG-20260927-2305-bma-mass-trial-w1（开工声明）；票 T-2026-09-27-94-P1 已 claimed by bm-a（commit 900e90eb 即锁）。
- 部门归属：dept:策略（生成引擎）+ dept:研究（初筛判据）联合。
- 算力预算：实测 **0.31-0.34s/候选**（3 行 pre-freeze 机器探针·results/_r362bma_screen_probe.py·零行留存）；1070 行 × workers 25 ≈ **<2 min**（短批·轮内合法；>10min 才强制后台池化）。

## §1 α 机制段（D6 四选一）

- [x] **行为偏差**＋[x] **风险溢价**（家族混合面）：候选池=11 流派 75 冻结信号族（趋势/均值回归/动量/波动率/情绪/日历/事件/宏观/经典技术/K 线形态/民间手法），机制主张随族携带（STRATEGY_LIBRARY §一 各族判定史）；千人批性质=**机制面普查**——每族先验已在册（G1'/G2/NSP1 批次史），本批不新增机制主张、只做参数×轴系的系统性空间填充。
- **同族相关性准入检查（D6）**：以 **T-84 s3 去重门代替逐对 corr 预检**（千人规模逐对不可行·法有明文）：生成端 = 参数向量哈希 + 信号矩阵 sha256 双层去重（坍缩即除名·如实计数）；初筛存活者入 s3 前再过 **逐对 |corr|≥0.999 收益序列去重**（§9 段冻结）。实测生成端：signal_dupes=4 坍缩、param_dupes=1、无效序拒收=2、死信号=42（诚实损耗账）。

## §2 数据与面板

- 宇宙：**core48 bare-code 面板**（J6 定义·`data/daily/` 48 只·2020-01-02→cutoff），p1_strategy_screen.load_core 镜像加载（open/amount 缺列补全同款）。
- **evidence_cutoff = 2026-09-22**（前向锁盒 D2）：面板一律截断到 cutoff；结果 JSON 顶层带 `evidence_cutoff` + `science_gates.cutoff_meta` 字段。
- 数据完备门：48 文件在位 + 每员 ≥60 行（load_core 内建）；引擎 T+1 开盘执行、V1 legacy 13bp 成本恒开（engine 默认路径）。
- 生成器探针事实：`generate` 已于冻结窗内跑毕=产物系冻结件（roster+candidates 属**语法枚举+去重**、零回测零判据读取——census 先例：roster 与 prereg 同 commit 冻结）；screen run（首次读判据的 run）严格在本件 commit 之后。

## §3 方法学（生成语法·冻结）

- **家族集（零发明）**：strategies/ 11 模块 75 信号函数全枚举（源码 sha256 逐族锚定·w1_roster.json）；排除集=∅（None 默认参数=held at 内部默认不采样，如 low_vol_long.rebal_days）。
- **kind 派发（P1 面逐字镜像）**：sym（逐员 Series 调用·pos>0 / pos≤0）／panel（截面权重帧·w>0 / w≤0）／mask（市场级掩码广播）／macro（MA(5,20) 交叠过滤·P1 macro_panel 同款）。
- **参数采样（RLSL §2 空间填充）**：每族 **Sobol 512-draw 帧**（2^9≥500·seed=20283000+族序）；参数范围=机械规则表：int 默认 d→[max(2,⌈d/2⌉), 2d]；float d→[0.5d, 2d]（保号）；枚举表 month[1,12]/weekday[0,4]/oversold[15,40]/overbought[60,85]/entry_j[15,35]/exit_j[65,85]；成对序拒收（fast<slow、n1<n2<n3、oversold<overbought、entry_j<exit_j）。
- **轴系（REFINE_BENCH_LAW §2 四轴·冻结）**：R∈{none, bull(510300≥MA200), bear(<MA200)}×X∈{own(函数配对出场), t5/t7/t10/t20(上升沿入场+N 交易日时间止)}×S∈{full, delever(熊态 0.5 名义·engine entry_size_scale·T-21 因果合同 shift(1))}×T∈{daily, weekly(周首交易日)}——轴值由每族同种子 RNG 流抽样。
- **入册律（ceiling-not-quota）**：每族前 13 个通过去重的 draw 入册（低差异前缀·确定性·零成绩窥视）→ **975≤1000**；语法消耗登记簿 `results/mass_trial/grammar_registry.jsonl` append-only（同语法禁重跑=防疏浚；wave-2 延深=Sobol 序列延拓=新候选非重评）。
- **对照与 null（BACKTEST_PLAN 三铁律）**：75 家族默认参数对照行（P1 面校准）+ 20 随机入场 null（p∈{0.02,0.05}×10 seeds 20283100..20283119）。
- 账本：`science_gates.append_ledger("MASS_TRIAL_W1", 975, ...)` 于 finalize 内嵌 `trials_ledger` 键（r252 律；完成态 summary 的链头永不重算防双计）。

## §4 判据（stage-1 初筛线·跑前写死）

- **screen_pass = beat_rate_6m ≥ 0.60 AND n_trades ≥ 30 AND max_drawdown ≥ −0.35**（全期·engine 口径）。
- beat_rate_6m：全史单次 engine 跑（T+1+13bp 恒开）权益曲线 vs 同窗 **EW48 被动**（日再衡等权）——滚动 126 交易日窗、步长 21、起点 ≥ 位置 252（T-22 caliber 暖机），胜窗占比；**60 窗实测**。
- 诚实披露：单曲线开窗 beat-rate 是**筛面近似**（非 T-22 逐起点独立引擎重跑——那是 s3 全量判决面的事）；null p50/p95 随批披露；0.60 为漏斗线（低于 0.70 判决 caliber），过线≠判决≠注册。
- 预期损耗如实：粗参数×轴系组合大量应为垃圾（探针首行 beat 0.083/dd−74% 即典型）；存活数十至上百皆合法，**零存活=合法产出**。

## §5 跑前预测（写死于跑前）

1. 存活率预测 **5-15%**（975 候选 → 50-150 存活）：族先验悬殊（注册员底座族存活率应显著高于判负族）。
2. R 轴（regime gate）应为最强轴（REFINE-BENCH 首炉定谳：熊市闸=第一杠杆）；bear 门行应系统性优于同族 none 行。
3. null beat_rate p50 ≈ 0.3-0.5（随机入场 vs 被动常态亏损面）；**null p95 < 0.60 预期**——若 null p95 ≥ 0.60 = 初筛线失效信号，如实上报并冻结待裁。
4. 极端日先验：2024-09-30/10-08 级别的单日 ±8-10% 指数日会击穿个别候选的窗收益对比；无 max 硬界承担主责（本批判线全为分布/占比面），无豁免单列需求。
5. 家族默认对照应复现 P1 面量级（Sharpe −1.5~+2 族谱；donchian_20_10 默认≈P1 史读数）。

## §6 产物

- `scripts/mass_trial_w1.py`（generate/screen/finalize/selftest 四子命令·selftest 11/11·byte-stable 复跑已验）。
- `results/mass_trial/w1_roster.json`（75 族冻结 roster·sha 96269ebe766c3fc2）+ `w1_candidates.json`（975 员·sha 907e44d56999b0ab）+ `w1_generate_summary.json`（损耗账）+ `grammar_registry.jsonl`（消耗登记簿首行）。
- `screen_checkpoint.jsonl`（逐行 checkpoint·跨机跨 kill 续跑=跳已记 id）+ `w1_screen_summary.json`（**顶层 evidence_cutoff+trials_ledger**·§7 回填面）。

## §7 跑后实证（2026-09-27 23:1x bm-a·一次定稿·freeze c638f8cf 后 41s 短批烧毕）

- **975 候选全筛 → 166 存活（17.0%）**；2 行 signal_error（DEF-26/27=month 必填位默认对照行，候选面零误差）；账本 286551→287526（+975）。
- **null 面**：p50=0.45·p95=0.533·max=0.55——全数 < 0.60 初筛线 ✓，但**裕量薄（线-null max=0.05）**如实披露：随机入场在熊窗占比高的样本上靠现金态可刷近线 beat-rate——初筛线只做漏斗非判决，s3 全量判决才是真门。
- **R 轴效应实测（预测#2 ✓）**：bear 门行存活 119/324=36.7% vs none 29/322=9.0% vs bull 18/329=5.5%——熊市闸=第一杠杆（REFINE-BENCH 首炉定谳千人面复现）；S=delever（22% vs 12%）与 T=weekly（21.6% vs 12.4%）同为正轴。
- **存活族谱**：seasonal 28% / patterns 21% / ta 20% / folk 18% / event 18% / mean_reversion 15% / volatility 13% / sentiment 11% / macro 10% / trend 8% / momentum 8%——反转/形态/日历类族支配（bear 门 × 低频现金友好面），趋势/动量族弱。
- **对照面**：75 默认行 8 过线=low_vol_long/engulf_reversal/hammer/duck_head/vol_drought_reversal/ants_climb/island/needle_probe——**注册员四底座（VOLATILITY/ENGULF/NEEDLE/DROUGHT）默认参数全过初筛**（筛面健康证：不杀已证族）；composite 双员不在 wave-1 语法（预注册口径）。
- **诚实注记**：beat-rate 面对高现金占用候选有系统性友好（熊窗被动为负、空仓≈0 即胜）——166 存活者中相当部分是「低频+熊门」面而非真α主张；这正是 stage-1 只当漏斗、s3 逐虚拟起点+Sharpe/DSR 全量判决必须跟上的原因。
- top 读数仅披露不采信：最高 beat 0.6667（ta.bb_squeeze_breakout·bear·t10·weekly·Sharpe 0.69/dd −3.4%）。

## §8 批后复盘（s7-T）

- **预测对账**：①存活率 5-15% 预测→实测 17.0% **部分错**（上限低估 1.2 个点，系熊门轴效应强于预估）；②R 轴最强 **对**；③null p50 0.3-0.5/p95<0.60 **对**（0.45/0.533）；④垃圾参数大量死 **对**（探针行 dd−74% 同型）；⑤默认对照复现 P1 族谱 **对**。
- 损耗账：gate_attrition.json 追加行（delta 975·eliminated 809）；判线当批读数=screen 线三条款（0.60/30/−0.35）全批恒定未调。
- 复跑纪律：checkpoint 逐行留存（screen_checkpoint.jsonl 1070 行）；重跑=跳已记 id 幂等空转；§9 s3 段冻结前禁烧存活者。

## §9 s3 全量判决面段冻结位（跑前追加 commit 后才许烧）

存活者全量判决=TRIAL_LABOR_LAW §2 第二段：T-22 caliber 逐虚拟起点引擎重跑 × {6m,12m,24m} × x2 成本面 × bear/bull/chop 分段 × 双 nulls≥2000；**波级多重校正强制**：DSR 按累计波试验数 N_eff 折减、PBO 波级报告、预期假阳性数如实披露；判据调 `science_gates.g1_prime_v2/g2_registration_v2` 共享库禁手抄。**本节为占位——具体判线/种子/分片在 s3 跑前以追加节 commit 冻结。**

### §9.1 s3 全量判决面段冻结【2026-09-28 00:4x bm-b r350 起草·本 commit 后才许烧·append-only·占位节留档】

- **触发与身份**：r349 owner adjudication（MSG-20260928-0030）采纳双波结构后本节=§9 占位的具体化（owner face·跑前 commit 冻结）；对应批件=**MASS_TRIAL_W1_JUDGE**（第二段判决批·judged cells 入账本）；CEO 48h 呈报钟不变（2026-09-29 22:45 前·O-2245）。
- **判决对象与入场去重门（§1 承诺门）**：166 stage-1 存活者（冻结清单=`results/mass_trial/w1_screen_summary.json` survivor_ids·同 §6 产物 sha 锚定）→ 入场前**逐对 |corr|≥0.999 日收益序列塌缩**（保留代表=确定性最低 candidate_id·坍缩/保留清单如实披露·audit 段全量保留原始变体）→ **N_judge=塌缩后格数**（跑前零宣称）。
- **判决网格（全 import 禁重实现禁手抄）**：虚拟起点=**P-5C 冻结栅格** `scripts/p5c_virtual_timepoint.py` `FROZEN_CENSUS` 双腿全网格（L 6m/12m/24m=1253/1127/875·D=3104/2978/2726·`EVIDENCE_CUTOFF_GRID`=2026-09-22 与本批 binding 同栅——wave-1b §9.3 同源口径）× 窗 {126,252,504} × 成本 {x1=13bp 引擎默认·x2=CostPatch(2.0)（t22 Erratum-1 multiplier 律·禁直引常数）} × 政体分段 bear/bull/chop+na（T-22 §3 冻结 3-way proxy 逐字）× 双 nulls：block bootstrap **B=2000**（block=20 交易日循环块·拼样截回 n 长）+ sign-flip 置换 **P=2000**（逐日符号独立·双侧）。
- **候选重放口径**：每格=存活者冻结配置（family fn+params+axes·`w1_candidates.json` sha 907e44d56999b0ab 实读禁手抄）经判决机械全网格重放；被动基准=起点日已上市成员 EW buy&hold 零再平衡（p5c `passive_rel` 机械·wave-1b §9.3 同款）；引擎面=T+1 开盘保守代理（O-1132）·退出优先级冻结禁改。
- **判据（共享库引用零手抄）**：
  - **G1' v2=`science_gates.g1_prime_v2(sharpe_full, returns, batch_cells, pool="core48", n_trades, n_entries)`**：全期 Sharpe>skill_line_v2（数据驱动线·N_eff=活链头+本批格）∧ 平稳 bootstrap CI 下界>0 ∧ entries≥30（F6 entries_ok 为准）。
  - **G2 注册资格 v2=`science_gates.g2_registration_v2(g1_pass, dsr, pbo)`**：G1' 过线 ∧ DSR≥0.95（原始收益跑·**n_trials=累计账本总试验数活链头实读·跨波不重置**——链头 287,526（2026-09-28 实读·跑时以活值为准）已含本波 SCREEN +975）∧ 家族 PBO≤0.25（`screening/pbo.py` CSCV 8 块·**家族=策略模块 11**（ta/patterns/seasonal/folk/mean_reversion/volatility/sentiment/event/momentum/macro/trend·同族波内候选 base 面 Sharpe 向量=g25_retro 先例；<8 格族=insufficient 如实 n/a→G2 不可过））；缺输入=诚实拒收（missing_inputs 机制）。
  - **样本充足律（RANDOM_LARGE_SAMPLE_LAW §3）**：n_eff≥500 起点 ∧ bear/bull/chop 三段各≥100 起点窗（na 桶披露）——不足→verdict=insufficient-sample 禁算 pass。
- **种子**：`mass_trial_w1_judge`=**20285000**（band 20285000..20285199·派生 `default_rng([20285000, cell_idx])`·rng 流仅限双 nulls 重采样面禁挪用·census §9.1 用途钉死先例；rg --type py 全仓扫描+SEED_REGISTRY 撞带扫描 2026-09-28 00:4x 零命中；**本 commit 同步登记 SEED_REGISTRY**·R250 一步律）。
- **波级多重校正（TRIAL_LABOR_LAW §4 强制）**：①N_wave=SCREEN 975+JUDGE N_judge 逐批披露；②**E[FP]=0.05×N_judge**（判决面名义 α=5% 口径）如实披露——DSR≥0.95 门即按累计 N 折减后的校正门·通过者=校正后存活非名义面；③波级 PBO 聚合读数另列（跨族）；④双波（wave-1a+wave-1b）N_eff 合并呈报面。
- **描述条款（批级披露不替代 v2 门）**：年化>0·OOS(2025+ 恒盲)双正·回撤≥−35%·无崩年·x2 面逐年稳定。
- **执行面**：runner=`scripts/mass_trial_w1.py` 追加 `judge` 子命令（**本冻结 commit 后建**·selftest 强制 hermetic·byte-stable 复跑·import-face 复用 p5c/T-22 机械禁重写）；池批 id=**MASS-TRIAL-W1-JUDGE**·shards=4（~N_judge/4 格/片·多机分片合法）·workers ≤floor(核×0.8) BelowNormal·lane_owner=null；**CPU 物理排序=排 W2A/W2B census 燃批+wave-1b SCREEN 之后**（池 entered_at 序·票内留痕合法排序）；bm-a 分片要约已受（r349·MSG-2335）。
- **账本**：`science_gates.append_ledger("MASS_TRIAL_W1_JUDGE", N_judge, file, evidence_cutoff="2026-09-22")`（prev=活链头实读禁手抄）。
- **跑前预测（写死于跑前）**：①corr-dedup 塌缩 ∈[0,15] 格（生成端 hash 去重已跑·族内近孪生轴/参数变体少量预期）；②G1'v2 过线 ∈[0,20]（筛面 60 窗近似 vs 判决面 T-22 caliber 更严·大量筛面存活者应死——§4 诚实注记的兑现面）；③**G2 eligible ∈[0,3]·模态=零**（DSR 按 N≈287.5k+ 累计折减=极重校正·T-87 五批判负同门先例·零存活=合法产出照报不翻案）；④族富集延续筛面方向（反转/形态/日历/民间族支配·趋势/动量族弱）——方向错=诚实读数不翻案。
- **极端日先验（整窗路径内化·无豁免路径需求）**：2015-07 救市/2016-01 熔断/2024-02 微盘崩/2024-09-24/09-30 政策脉冲/2025-04-07 外生缺口/2026-01-19 极端溢价日——候选曲线尾部 |日收益|>8% 属市场真值非腐坏·危机日计数列随格披露。

## §10 消费面

存活者 → s3 全量判决 → 终存活者 → STRATEGY_LIBRARY 注册 + TRIAL-<family>-<NN> 纸盘上岗（O-2045 机器复用）→ **48h 内呈 CEO**（O-2245 时钟：2026-09-29 22:45 前）；语法供给面（TRIAL_LABOR_LAW §5）：T-86 census W2A/W2B 存活腿到位后并入 wave-2 语法；wave-2=5000 人扩容（水位持续吃得下+语法非空即开）。
