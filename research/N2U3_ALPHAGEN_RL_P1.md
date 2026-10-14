# N2U3-ALPHAGEN-RL-P1 —— N2 U3 通道①「全新语法」alphagen RL 公式因子主考批（预注册 FROZEN）

> 【状态：FROZEN——冻结窗翻面（bm-b r892·2026-10-11 18:4x）·冻结 commit=本窗】**N2 U3 channel-1 drafting window 开窗依据**=E16_ALPHAGEN_RG_CENSUS_P1 判读线 `census_holds=true`（obs family max |ICIR| 0.455 > null family p95 0.077·n_ok 200/200·r888 finalize·results/alphagen_rg/CENSUS-2026-10-09.json）——E16 §3 判读线 verbatim「holds→RL build licensed（N2 U3 channel-1 drafting window 经 PREREG_TEMPLATE 正门合法开窗）」；承接链=T23 slice-1 POSITIVE-with-riders（DIGEST-20261010 三骑士：R1 血统负先验披露·本节 §1 执法／R2 语料面板门控=E16 面板已完备·已解／R3 RL 引擎宣称未核=本批 leg 序先建后烧诚实核）。
> **冻结门五条件全过收口（N2-W15 冻结门先例·r892 实跑回执）**：
> 1. leg-1 runner 建+selftest 全绿 ✅——scripts/alphagen_rl_p1.py（r891 建·七子命令）+冻结窗复跑 selftest **45/45 PASS**（r892 18:4x）；
> 2. 种子带 `seed_admit_gate` rc0 ✅——`seed_admit_gate rc0 base=20625000 span=1001 checked=1001 verdict=FREE`（三键位全覆盖 gen 20625000/scrnull 20625500/unc 20626000；起草窗 span500 预验→冻结窗 span1001 全带收口）；
> 3. `banned_direction_gate --prereg` rc0 ✅——回执 `decision=ADMIT`（registry v1.0·matched=[]·reason=no banned direction claimed·r892 冻结窗实跑）；
> 4. 判据节共享库引用核 ✅——§4 判线全引用共享库零手抄（g1_prime_v2/g2_registration_v2/m1_t_value_gate·`science_gates` import）＋runner freeze_gate/gate 腿机械消费同一 `sg` 面（selftest L10 族 judged 门腿+L11 账本腿在 45/45 内）＋env-probe 同窗复跑 admit_rc=0/banned_rc=0；
> 5. 意义门三问+令面 ✅——§0.9 三行作答在案（冻结窗作答）；授权面=O-20260930-2340 常供面令（N2 常供面·无需新署名）+TRIAL_LABOR_LAW §1 常设线+E16 §3 判读线（holds→RL build licensed）+T23 slice-1 承接令；本窗令面核对=fleet/orders 差集 **0**（dec 81f27c6d+ord 69090314 双零 delta·r892 S0.5 canonical probe）。
> 6. 冻结窗执行面=prereg 翻面 FROZEN＋三带登记三键 ✅——`scripts/science_gates.py` SEED_REGISTRY 登记 `n2u3_alphagen_rl_gen=20_625_000 / n2u3_alphagen_rl_scrnull=20_625_500 / n2u3_alphagen_rl_unc=20_626_000`（冻结 commit 面内·env-probe bands 3/3 true·freeze_gate posture ok）。
> **evidence_cutoff=2026-10-09（冻结窗写死）**——面板完备末 bar 实锚（panel gate ready·per_files 5219==状态件 5219·roster_sha16 1d06d218b2cbf870 ok·census 锚恒等 TOP-8/200·r892 env-probe 回执）；cutoff 后新 bar 锁定不得回流本批。
> **冻结门后纪律（原文延续）**：跑前只许状态翻面（本行已翻），跑后只许回填 §7/§8，禁改判据禁重跑（工程修复重跑须双跑留痕）。
> 【批型】**主考批（judged）**——RL（强化学习）表达式树搜索在 E16 幸存语法空间上生成 top-K 公式 → core48 消费面全起点虚拟时点 judged 判决；判线=BACKTEST_SCIENCE v2 共享库（g1_prime_v2/g2_registration_v2）；负即止（G2 fallback·学术引用面·EXCLUSION_BOOK 复活总律）。

## §0 批件身份【必填·跑前】

- 批名/批号：**N2U3-ALPHAGEN-RL-P1**（N2 U3 通道①「全新语法」主考批·judged 面 K=32 格；RL 训练搜索面不计试验·nulls 校准不计试验·账本口径 §3）。
- 认领：F-04 先行——冻结窗前 fleet/inbox/ MSG 声明（防双机撞建 runner）；队列行=state/queue/explore.md 新行（T-19 seed gate 注册闸 rc0 后登记）；起草窗=本文件（bm-b r889·E16 holds 开窗指针承接）。
- 部门归属：dept:研究（alphagen 范式评估线·T23→E16→本批三段链第三段）。
- 算力预算：leg-1=runner 纯工程零烧录；leg-2=短窗训练探针估 30-60min（入池分离烧录·BelowNormal·workers=min(worker_cap(),8)）；leg-3=完整训练估 2-6h（入池·跨轮 checkpoint·per-episode 断点续跑）；judged 面=引擎全起点虚拟时点批（入池）；**全链 >5min 一律池面禁轮内代跑（O-20260924-2100 执行面分离律）**；批报告必带 audit 段。
- evidence_cutoff（前向锁盒 D2）=**2026-10-09（冻结窗写死·r892）**——冻结 commit 时点面板完备末 bar 实锚（panel gate ready·per_files 5219==状态件·r889 起草窗预估面 2026-10-09 或 10-12 → 实锚落 2026-10-09）；cutoff 后新 bar 锁定不得回流本批；结果 JSON 顶层必带 `evidence_cutoff` + `science_gates.cutoff_meta` 字段。

## §0.5 禁开方向硬闸【必填·跑前·D-20260930-41 §1.2】

- 跑前实跑：`python Tools/banned_direction_gate.py --prereg research/N2U3_ALPHAGEN_RL_P1.md` → 回执记入冻结 commit message。
- 本批命中 BAN-__：无（冻结窗实跑回执为准）。
- R1 血统负先验披露（骑士执法·非阻烧亦不借判）：A158 系 157/158 ETF/基金截面判负（GTJA 0/183 core48·WQ 0/82 strict·A9 0/9·A10 0/16）——本批与先验差异面=**搜索机制**（RL 反馈搜索 vs 固定清单/随机采样）＋**语料**（股票宽截面因子测量+core48 消费 vs ETF 截面直接注册）＋**判读**（全起点虚拟时点 judged vs 截面 IC），三差异如实披露；先验历史墙高在 §5 P2 预测面承载。

## §0.9 意义门三问【冻结窗作答·r892】

- ①研究问题=「RL 反馈搜索（自举预训练+PPO 微调·协同池边际 rank-IC 奖励）在 E16 幸存语法空间上是否比无反馈采样基线产出更高边际 IC 的 top-K 公式集，且 judged 消费面（core48·全起点虚拟时点）能否过 G1'v2」——反馈搜索杠杆在该语法空间至今零判读（T23 无反馈随机族 null p95 0.077→E16 census 测量 obs 族 max 0.455→本批=反馈机制首烧·负即止）。
- ②消费方=本批 top-32 公式 judged 读数→N2 U3 通道①收口决策（正=RL 搜索线留任待 leg-3 完整训练+D6 注册面·负=EXCLUSION_BOOK 收口·G2 fallback 学术引用面）；存活公式逐字随件→因子素材池（血统标签 RL-search·P3 预测面=RL 边际增益诚实披露）·任何后续消费（输入特征路线/注册面）须全新预注册+成本压测（A158-TSGATE-P1/A10 先例门）。
- ③语法登记簿查重=research/TRIAL_GRAMMAR_LEDGER.md alphagen 行=**0**（r892 冻结窗 Select-String 机证零行·本批=该语法族在 RL 反馈搜索机制下首烧；E16 随机 census 式与 W18/W19/W20 beam 族由 T-84s3 指纹去重在绘制时排除·E16 幸存者 TOP-8 为协同池目标面非重烧面）。

## §1 α 机制段【必填·D6——无机制段=批不受理】

- 四选一：**[x] 行为偏差**（主）——E16 census 幸存者族=量能/换手截面（TOP-8 全族：LOW(turnover,30) |ICIR| 0.455·LOW(volume,10) 0.432·QTLD(volume,20) 0.426·VMA(volume,60) 0.408·ROC(volume,20) 0.389·SUMN(volume,60) 0.388·ROC(turnover,20) 0.387·RANK(amount,60) 0.386——IC 符号面：量能/换手低=前瞻收益高），可命名行为面=注意力与放量行为（CORR/VSUM*/WVMA 族）+处置效应与超卖反弹（QTLD/SUMP 族）+追涨杀跌（ROC 族）；代价支付者=截面上过度反应/反应不足的散户与追涨资金。**诚实披露**：RL=语法空间搜索器非机制宣称——机制段勾选=语法空间主导族先验（E16 §1 同律延续），本批唯一宣称=top-K 生成公式在冻结判线下的 judged 读数。
- **散户凭什么赢【§1.2】**：**行为**——日线级宽截面无速度/容量/制度优势可主张；散户优势面=纪律化系统捕获他人行为偏差（E16 §1.2 verbatim 延续），RL 杠杆=把搜索纪律化的算力交给机器——不新增优势面主张，只压缩人工因子工程成本。
- **同族相关性准入检查【D6】**：judged 注册面逐幸存者 `max|corr|`（与在册交易员全部成员＋同批全部已判函数，日收益序列口径，sleeve-tag 先例）——`max|corr| ≥ 0.7` → **拒收**；RL 协同池=对在册成员+E16 幸存者+同批已判幸存者的**边际 rank-IC** 目标（alphagen 协同池律·防重复发现已发现信号）——D6 与协同池双面在 runner 判据节执法。

## §2 数据与面板【必填·跑前探针事实——E16 同源实锚 r878/r877，冻结窗复跑复核】

- **因子语料面（测量面·E16 四元组 verbatim）**：①`data/astock_daily/per/<code>.csv`（gitignored bm-b 车道件·R31）②`pd.read_csv` 直读 ③每员全史截 ≤cutoff 后取 [首个 ≥2018-01-01 行−130, 末] 窗 ④预热 130 行——r878 实锚：5,219 件·首 1991-04-03/末 2026-10-09·9 列 schema；宇宙=（①`scripts/stock_face_furnace._universe()` 单源 ②eligibility.csv 码表∩b_layer_mask ok_static∩盘上文件 ③r878 探针 n=3,514 ④P4_BATCH2 动态逐日资格条款 verbatim〔rev_osc_stock_p1 常量：close≥PRICE_MIN·amt20≥AMT20_MIN·listed≥LISTED_MIN·fresh≤FRESH_MAX·board≠other〕t23 load_panel 同律）；eligibility <24h 快照旗漂移面=E16 §2 已披露坑，烧录宇宙钉死 sff._universe() 稳定码表面+panel cache 冻结。
- **消费面（judged 面）**：core48（`data/daily/sh<code>.csv`·in-repo 冻结面板）——**消费路线=时序分位门/输入特征**（A158-TSGATE-P1+A10 先例·long-only T+1 成本）；股票截面因子值→core48 消费的映射=冻结窗 runner 探针实锚后写死（分位门参数/特征构造机械·探针-锚强制同面断言 G-ANCHOR-FACE 律）。
- **数据完备门（fail-closed exit 2）**：G-PANEL（t23 gate_face 逐字 import：astock per-files 盘真计数 vs 状态件声明·**盘面胜出**=r840 假新鲜死锁根治律）＋G-CUTOFF（面板 cutoff==冻结锚）＋G-CAL（窗行数逐位）＋G-UNIVERSE（|uni|∈[3,400,3,600]）＋G-SEEDS（SEED_REGISTRY 键==冻结登记值）＋G-CONSUME（core48 面板完备门）——一面不相等=配置错配 VOID 拒烧（报「面错配」非「数据腐坏」）。
- **零网络**：全在库零采集；eligibility/b_layer_mask 只读消费。

## §3 方法学【必填·冻结窗钉死】

- **RL 环境机械（leg-1 待建·本节=机械冻结面声明）**：
  - 语法空间=E16 verbatim 底座（vendored A158 29 滚动算子 × 8 底座输入 {open,high,low,close,volume,amount,vwap,turnover} × 5 窗 {5,10,20,30,60}·depth≤2·泛化规则=E16 §3 verbatim：价格类字段槽→采样输入 X·$volume 槽保持原 volume）；`research/shortline/external/qlib_alpha158_loader.py` sha16=814b7f7ab3d418ae 单源。
  - 搜索器=自举预训练（表达式树采样·E16 rng 机械复用面）+PPO 微调（论文宣称未核面=R3 骑士——**实现按仓内机械最小可复现集，论文超参不照抄，逐超参披露仓内值**；训练种子=冻结窗登记键）。
  - 协同池=对在册成员+E16 幸存者+同批已判幸存者的边际 rank-IC（alphagen 协同池律）；IC 机械=`scripts/t23_random_grammar_census.py` pa_lhb_ic rank_rows+ic_from_ranks+fwd_ret **逐字 import 禁重写**（E16 同机械律·h=1 唯一口径）。
  - NaN 政策/去重=IE16 §3 verbatim（全窗规则·MIN_CROSS=100·MIN_PERIODS=30·同流拒绝重抽）。
- **产出面**：训练产出 top-K=**32** 公式（协同池边际 IC 排序）→ judged 消费面；公式串逐字随件（n_unique 披露）。
- **judged 消费模板**：core48 时序分位门（A158-TSGATE-P1 先例·门参数=冻结窗探针实锚写死·long-only T+1·全起点虚拟时点 P-5/P-5B 冻结口径·成本 x1/x2/x3）。
- **null 对照**：K=32 同掩码随机 null（t23 `_permute_ranks_within_mask` 逐字·per-date 同掩码置换）——seed 提案带 **20_625_000 族**（t23 20_615_000→E16 20_620_000→本批 +500 顺延范式·**冻结窗 `seed_admit_gate` 实跑 rc0 后登记三键**：gen/scrnull/unc）＋被动基线（core48 成员持有·池已校准者）。
- **成本口径**：V2 主口径（ADV20 三层滑点+1%ADV 帽·knowledge/rules.py）+V1 legacy 双轨历史锚防漂移；**往返成本 bp 申报【CN-C7】**：ETF=26.082bp/往返（面 A=`knowledge/cost_spec.py` 派生恒等）；单笔名义额档位=¥20,000 临界披露。
- **账本**：`science_gates.append_ledger("N2U3_ALPHAGEN_RL_P1", 32, file_name=…, evidence_cutoff=…)`——judged 32 格计入 ≤500/30d 预算（30d 窗已耗 E16 200·余额内）；RL 搜索面与 nulls 校准不计数（E16 §3 trial_budget_law 同律）；E[FP] 名义=0.05×32=1.6。
- **出场轴显式门（O-20261001-1108）三选一**：**③template_default 按设计测**——RL 公式作为 core48 **时序分位门/输入特征**消费（A158-TSGATE-P1 先例·门条件开仓），出场走宿主模板缺省出场栈按设计测（非①策略自有出场·非②持有到底声明）；冻结窗如改判①/②须 changelog 留痕（=面定义澄清·非判据放宽）。
- **闭合族对号声明【M3】**：family_key=**alphagen_rl_grammar**——`science_gates.CLOSED_FAMILIES` 无此键（r889 实查 9 族零撞号·在册=open 照跑）；近邻披露：alphagen_random_grammar（E16 测量面·census_holds=true 开窗面）与本批=同语法不同搜索机制（RL 反馈 vs 无反馈采样）独立假设；A158 ETF 截面判负族=§0.5 血统披露非本批否证面。

## §4 判据【必填·跑前写死，禁看结果调线】

- **G1' v2 = `science_gates.g1_prime_v2(sharpe_full, returns, batch_cells, n_trades, n_entries)`**：全期 Sharpe > skill_line_v2（数据驱动=max(被动+0.10, μ_null+σ_null·√(2·ln N_eff))）且平稳 bootstrap CI 下界>0 且 entries≥30（F6 双口径·(entries_ok) 为准）；批报告逐列披露 skill_line/bootstrap_ci/trade_gate 全输入。
- **G2 注册资格 v2 = `science_gates.g2_registration_v2(g1_pass, dsr, pbo)`**：G1' 过线 且 DSR≥0.95（`deflated_sharpe_ratio` 原始收益跑·禁 dsr_from_stats 充数）且族 PBO≤0.25（`screening/pbo.py` CSCV 8 块·同族参数族=g25_retro 先例）。
- **M1 t 面【必填】**：因子面=批内 IC t/ICIR 直接面优先（t≥3.0·`science_gates.m1_t_value_gate`·Harvey/Liu/Zhu 多重检验门槛）；缺 t 面=missing_input 拒收。
- 描述条款（批级披露不替代 v2 门）：年化>0·OOS 双正·回撤≥-35%·无崩年·成本压测 x2/x3 逐年稳定。
- **硬界设计三件套**：(a) 分布界（median/p99.9）承担检测主责禁裸 max；(b) max 硬界须配危机日感知或豁免单列；(c) §5 极端日先验。
- 判线全部引用共享库（T-02 6/7 律·禁手抄）。

## §5 跑前预测【必填·写死于冻结前·DRAFT 稿冻结窗钉死】

- P1：RL top-32 公式截面 |ICIR| 集中于量能/换手族邻域 **[0.2, 0.5]**（E16 幸存者族先验延续·协同池边际目标不改变族分布形状）。
- P2：judged 消费面（core48·全起点）G1'v2 过线 **0/32 概率 >70%**（R1 血统墙高：GTJA 0/183 core48·WQ 0/82——消费面历史全灭先验；正=意外惊喜面）。
- P3：RL 训练边际 IC 曲线上升**优于**无反馈采样基线（E16 幸存者族均值面）；若不升=RL 无增益诚实披露·判读线=negative 即止（G2 fallback）。
- P4：极端日先验（三件套 (c)·E16 §5 P6 同窗）：2024-09-24/09-30 政策脉冲·2025-04-07 外生缺口·2026-01-19 极端量日——全市场同向日截面区分度塌缩→单日 IC 趋 0/NaN；judged 面同窗（core48 上同日涨跌停/缺口形态随件披露）。
- P5：n_unique_formulas==32（去重后）；skip 率 <10%（E16 MAX_SKIP_FRAC 同值·超限=机制嫌疑 exit 2 诚实拒判）。

## §6 产物

- runner：`scripts/alphagen_rl_p1.py`（leg-1 建·subcommands：env-probe / pretrain / train / export-topk / judge / status / selftest；`__main__` 守卫=Windows mp 坑律；selftest=hermetic 离线腿：语法确定性/协同池机械/去重/null 置换确定性与同掩码不变性/分片切分/门腿/账本块形状）。
- 池 entry：leg-2 训练探针 / leg-3 完整训练 / judged 面分离入池（`results/runnable_pool.json`·lane_owner=bm-b·workers_plan 8 BelowNormal·host_gates=§2 完备门）。
- 产物：训练日志+top-32 公式表（公式串逐字）+judged `results/alphagen_rl_p1/JUDGED-<cutoff>.json`（顶层 evidence_cutoff+cutoff_meta+audit 段）；机器本地件（gitignored）=per-episode checkpoint+panel cache。
- F-04 MSG：冻结 commit 同窗 fleet/inbox/ 声明。

## §7 跑后实证【跑后一次定稿·r933 bm-b 2026-10-14 13:5x】

- judged 落地：`results/alphagen_rl_p1/JUDGED-2026-10-09.json`（114KB·2026-10-14 07:42:26 落地·leg-3 训练 4096 eps 断点续跑毕→export-topk n_unique=32/n_skip=0→judged K=32 格全判零 skip）；账本 940,789→**940,821** 单调 +32 EXACT（judged 格计入；RL 搜索面与 nulls 校准不计=E16 trial_budget_law 同例）。
- 门禁链逐环：D6 拒收 **18/32**（vs 在册成员 max|corr| 0.706–1.000）→ M1 t≥3 过 **9/32**（t 10.416–13.227·全部 d6_ok 正 t 格）→ G1'v2 过 **0/32**（best `QTLD(low,60)` sharpe_full_x1 **0.5435** vs **skill_line_v2 2.952** @ n_eff 940,821·批内自有 scrnull 池 n=32 μ=-0.2571/σ=0.6119；bootstrap CI95 [-0.1707, 1.2811] 下界≤0）→ G2 注册 **0**（DSR max **0.2355** < 0.95 且 family PBO **0.2714** > 0.25 双 fail）→ **registered 0/32**。
- 预测对账：**P1=错**（预测集中量能/换手族邻域 [0.2,0.5]——实测 RL 收敛全部价格字段 {close 13/high 7/open 6/low 3/vwap 3}，零量能/换手/成交额字段；|ICIR| med 0.178/max 0.363，带内 14/32 仅部分）；**P2=对**（预测 G1' 0/32 概率>70%——实测 0/32 且差距巨大 best 0.54 vs 判线 2.95）；**P3=错**（leg-2 训练边际 IC flat 0.0001–0.0002 无上升信号=RL 反馈不优于 E16 无反馈基线→license 问题判负）；**P4=过**（极端日门 2024-09-24/09-30/2025-04-07/2026-01-19 全 false 无坍缩；成本 x2/x3 逐年稳定 32/32）；**P5=过**（n_unique_formulas=32、n_skip=0<10%、n_excluded_dup=0）。
- 全起点分布（best 格 `QTLD(low,60)`·judged 消费面全起点虚拟时点 P-5/P-5B）：fullstart_6m best **+0.1753** / p25 **-0.0043** / 中位 **+0.0193** / p75 **+0.0402** / worst **-0.1301**；滚动最差 3y **-0.0201** / 5y **+0.0228** / 10y null；beat_rate 3m 0.5708 / 6m 0.5337 / 12m 0.4906；逐年 2022 -0.0692 / 2026 -0.0429 负年；max_dd_x1 **-13.71%**。

## §8 批后复盘【必填·s7-T】

- 预测对账（P1-P5）：P1 错（族向收敛证伪）/P2 对/P3 错（核心 license 面判负）/P4 过/P5 过——**一句话定谳：RL 反馈搜索在该语法空间不产生高于无反馈采样的可注册信号**；门禁链损耗账=`results/gate_attrition.json` + `gate_attrition.bm-b.json` 各追加 N2U3_ALPHAGEN_RL_P1 一行（32 eliminated 全灭·r933）；判线当批读数=skill_line_v2 2.952 / DSR max 0.2355 / family PBO 0.2714 / null 池 μ=-0.2571 σ=0.6119。
- 回执：轮报告 r933 bm-b + CODELY.md 行级追加；**零新注册员**（无注册件/无 live/paper SIGNAL_BUILDERS 接线/smoke 锚定门无涉——负结果链合法零动作）。
- **全起点分布【§1.3】**：见 §7（best 格五分位+滚动窗+逐年+回撤齐备；批最差格 `VSTD(ROC(close,60),10)` sharpe -1.0795）。
- **试验量归因【§1.4】**：本批新增试验数=**32**（judged 格·计入 ≤500/30d 预算；E16 census 200 同窗先烧）；一句话归因：E16 census 已证语法空间存在 |ICIR|>0.4 信号面，RL 搜索=把 E16 无反馈采样升级为反馈搜索的最小承诺主考（top-32 格）——**判负落地：负即止步 RL 线（EXCLUSION_BOOK 收口·G2 fallback 学术引用面·same-grammar rerun FORBIDDEN judgment single-shot 律）**；语法登记簿 `research/TRIAL_GRAMMAR_LEDGER.md` alphagen RL 首烧行已回填（§0.9③ 冻结窗承诺兑现）。
