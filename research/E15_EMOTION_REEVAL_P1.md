# E15_EMOTION_REEVAL_P1 —— 情绪族近失残留 4 员 FDR4D 改革判线复判批（预注册）

> 【状态：FROZEN——跑前 commit 冻结】E15 队列行 leg-2（supply-floor chain leg-3 承接件·外源目录第一梯队 #18 判线改革承接件）；bm-b r875 登记+认领同轮（T-18 CLEAR+T-19 seed gate hits=[] 前置双闸），leg-1 roster 探针已交付（scripts/emotion_reeval_roster.py selftest 8/8 + results/emotion_reeval/e15_roster.json）。跑后只许回填 §7/§8，禁改判据禁重跑（工程修复重跑须双跑留痕）。
> 【批型】**档存重估 derive 批（re-evaluation, 新程序非翻案）**——重估对象=mass trial 千人题库近失残留 4 员（report_card passers·g1 过线 g2 落选员），在 REGISTRATION_REFORM_FDR4D（O-20260930-1058）改革判线下重估；**零新候选生成、零 Sobol、零候选曲线重模拟、零账本 append、零 RNG（零种子登记面）**——四维材料全部来自冻结判决件 verbatim 携带 + 冻结日收益序列纯派生（L1 确定性零网络），唯一引擎触面=注册六员 D6 对照重放（REEVAL18 `_registered_window_rets` 同律 6 次轻重放）。
> 【承接面实证】REEVAL18 drill 未覆盖 23027/23057（grep results/reeval18 零命中·E15 行载）；W14/W16 改革首判波已落地=新标准在役；方向线索=sentiment.turnover_surge 双员（W2-23057 DSR 0.5288·oos_sharpe_legL 1.9327／W3-23027 family_pbo 0.1857 全场最低·signflip_p 0.0）=目录 #18 指名的族复发线索，非晋升承诺。

## §0 批件身份【必填·跑前】

- 批名/批号：**E15_EMOTION_REEVAL_P1**（批内成员数 m=4·全部计入 BH FDR 分母；重估面零格数入账本——REEVAL18 §0 先例「重放面 +0 生成试验」同律）。
- 认领：explore 队列 E15 行（bm-b r875 登记+认领·T-18 CLEAR·T-19 hits=[]）；本批无新种子（零 RNG 面）→无 SEED_REGISTRY 登记；F-04 声明=freeze commit 同窗 fleet/inbox/ MSG（防双机撞建 runner）。
- 部门归属：dept:研究（档存重估线·CEO 令改革正典消费面）joint dept:策略（改革注册口径面）。
- 算力预算：单 worker 串行确定性单遍（面板加载 ~15s + 注册六员 6 次轻重放 ~5s + 纯派生秒级，est **60-120s**）；>5min 不适用（R41 短批豁免），仍按 supply-floor 链律入池（O-2100 池面=本批为 supply floor ready 计数腿）；BelowNormal。
- evidence_cutoff（前向锁盒 D2）=**2026-09-22**（与冻结判决面/roster 源同锚·W2/W3 候选件 evidence_cutoff 实测同值）；结果 JSON 顶层必带 `evidence_cutoff` + `science_gates.cutoff_meta(cutoff)` 字段。
- 池 entry：`results/runnable_pool.json` 新 entry **E15-EMOTION-REEVAL-P1-RUN**（status=ready·workers_plan 必带·lane_owner=null 任何合法机可烧）。

## §0.5 禁开方向硬闸【必填·跑前·D-20260930-41 §1.2】

- 跑前实跑：`python Tools/banned_direction_gate.py --prereg research/E15_EMOTION_REEVAL_P1.md` → 回执记入冻结 commit message。
- 本批=已判决成员的档存重估（「档存重估=新程序非翻案」REEVAL18 §1 同律）；重估不豁免任何后续闸——s4 上岗执行面逐员再过禁开方向闸。命中 BAN-__：无（跑前实跑回执为准）。

## §1 α 机制段【必填·D6——无机制段=批不受理】

- 四选一：**不适用声明**（REEVAL18 §1 先例 verbatim）——本批=既有已判决候选的档存重估，α 机制段由各员原 wave prereg 承载（W2-23057→research/MASS_TRIAL_W2_PREREG.md §1；W3-23027/W3-27009/W3-46133→research/MASS_TRIAL_W3_PREREG.md §1·11 流派 75 冻结信号族机制主张随族携带），本批引用不重述。改革判据的机制角色=**批内 BH FDR（m=4）替代全局账本折减 + 四维合成替代 DSR 单一处刑**（科学面改革本体 O-1058），非新 α 主张。
- **散户凭什么赢【§1.2】**：随各员原 wave prereg §1 携带（ETF core48 面散户可执行面），本批不新增主张。
- **同族相关性准入检查【D6】**：本批无新函数入批（4 员全部在库已判决·冻结配置 verbatim）；批内簇去重+注册员撞线=**`trial_labor_w2._d6_admit_core` 全套执法**（max|corr|≥0.7 注册员拒收 + 批内 ≥0.7 簇塌缩保最高 DSR·W1 cmd_intake 谱系），输入=冻结 legL 日收益 vs 注册六员同窗日收益（§3）。

## §2 数据与面板【必填·跑前探针事实，非结果——r875/r876 探针已跑·实测落稿】

- **花名册（冻结源钉死）**：`results/emotion_reeval/e15_roster.json` sha16=**0f23cf678db4697e**（4 员 3 族·近失档案 honesty 逐字携带·source_evidence_cutoff=2026-09-22）。
- **冻结判决件（携带源）**：
  - 候选配置：`results/mass_trial/w2_candidates.json` sha16=**44a31ed2444ebf23**（W2-23057=family sentiment.turnover_surge·kind panel·params{n:13,threshold:2.868716}·axes{R:bear,X:t5,S:full,T:daily}）；`results/mass_trial/w3_candidates.json` sha16=**b5316ddf0a608e2e**（W3-23027 params{n:27,threshold:3.160676}·W3-27009 seasonal.trend_by_season params{ma_n:400,month:4}·W3-46133 ta.strong_close params{pos_th:0.516373,vol_len:10,vol_mult:2.563805}）。
  - 判决汇总件：`results/mass_trial/w2_judge.json` sha16=**ae58310f8d411dab**／`w3_judge.json` sha16=**2b9773bcd0a47c4f**（g1/g2 判读+族 PBO 权威面）。
  - **判决分片件（日收益携带源·本批核心新材料）**：w2 shard0-3 sha16=**0a632731bd5b3fbb/f569aaaa07a1d198/323ecb681ab09249/a63a8f2e7c7bc5a2**；w3 shard0-3 sha16=**fdc2b37ee4fe7cc1/e449cea17d74047d/11b42dbdb0bc5ea3/b77cae0139f939b6**——4 员所在分片行各携 `legL_daily_returns` **n=1631 恒等**（实测 W2-23057@w2shard2／W3-23027@w3shard0／W3-46133@w3shard2／W3-27009@w3shard3）+ `legs.L.{x1,x2}` 双成本腿读数 + `dual_nulls`（bootstrap_ci+signflip_p）。
- **数据锚面定义四元组【G-ANCHOR-FACE 律】**：
  - leg-L 索引=`scripts/mass_trial_w1._load_leg('L')`（p5c leg 面板 wholesale import）＋`load_core()`（live.paper raw pd.read_csv 直读族）＋起算 2020-01-02（LEG_L_FLOOR）＋截 2026-09-22（EVIDENCE_CUTOFF_GRID）——实测 **1631 bar·首 2020-01-02·末 2026-09-22·census {6m:1253,12m:1127,24m:875}==FROZEN_CENSUS['L'] 逐位恒等**（r876 探针实证）；runner 门=长度 1631+首末日期+census 三断言，任一失配=面错配 VOID（fail-closed 报「面错配」非「数据腐坏」）。
  - 日收益序列=上述分片件 `legL_daily_returns`＋`json.load` 直读＋首 bar 起（bar0=0.0 by eq.pct_change().fillna(0.0) 构造）＋无预热（判决面现役口径 verbatim）；**探针-锚同面断言**：由冻结日收益重建 eq 复算 Sharpe==分片件 `legs.L.x1.sharpe_full`（4 位舍入恒等）——G-REPRO 锚，失配=VOID。
  - 注册六员重放面=`live.paper.load_core`→截 2026-09-22→`build_panels`（48/48·末 bar==cutoff·OHLCV 齐）＋`trial_labor_w1.run_candidate_curve`（A_TEMPLATES×DEFAULT_AXIS 语法默认轴通道·REEVAL18 `_registered_window_rets` 同律）＋v3_state_series 政体面；窗口切片=leg-L 1631 bar 同窗（reindex 对齐）。
  - 五员 EW 天花板基线=O1555 冻结宇宙 {510300,510050,510500,512100,588000} `data/daily/sh<码>.csv` raw pd.read_csv 截 2026-09-22（W14 `_five_member_ew_baseline_annualized` 同律·EQUAL_WEIGHT 每日跳过缺数员）。
- **数据完备门（不过门禁跑）**：G-ROSTER（roster sha16+4 员+batch 名+cutoff）＋G-SHARD（4 员分片行齐·n_daily==1631·判决汇总件同员行在位·sharpe 双件一致）＋G-PANEL（注册重放面 48/48+末 bar==cutoff）＋G-LEGIDX（上列三断言）＋G-REFORM（`science_gates.reform_weight_freeze_integrity()` pass·r876 实测 True）——全 fail-closed exit 2。
- **零网络**：本批零数据采集（全在库）；v3_state_series 活重放（构造保证一致性）。

## §3 方法学【必填·冻结】

- **重估语义**：同面重估——冻结判决面（leg-L x1/x2 双成本腿·evidence_cutoff 2026-09-22·T+1 开盘保守代理·RW-7 冻结退出栈）的 4 员既有判决材料 verbatim 携带 + 冻结日收益序列派生新判线所需增量材料；**零候选曲线重模拟**（判决分片件已携 legL_daily_returns=n1631 全序列——r876 探针首证）；注册六员 6 次轻重放仅服务 D6 对照面。
- **出场轴显式门三选一（O-20261001-1108）**：**① 策略自有出场**——各员出场=原 wave 判决栈 verbatim 携带（MASS_TRIAL_W2/W3 §3 ③ template_default 按设计测+候选 X 轴出场信号·RW-7 优先级 signal_reversal>stop_loss>take_profit>time_decay>loss_time_stop>global_hard_limit）；本批零新出场设计、零出场栈改动、engine/exit_rules.py 零触碰。
- **四维子指标映射（W14 判决面正典映射 verbatim 消费·禁手抄判线 r271 律）**——`member_metrics[cid][dim][sub]`：
  - **ret**（携带+派生混装·逐项 provenance 随产物披露）：
    - `sharpe_full_L`＝**携带**（分片件 legs.L.x1.sharpe_full）
    - `annualized_ret_L`＝**派生**（冻结日收益复合×252/n）
    - `return_ceiling_O1126`＝**派生**（候选年化−五员 EW 同窗年化·REFORM_CEILING_BASELINE=five_member_ew_O1555）
    - `beat6m_rate_L`＝**携带**（分片件 legs.L.x1.beat['6m'].rate）
    - `beat12m_rate_L`＝**携带**（分片件 legs.L.x1.beat['12m'].rate）
  - **robust**：
    - `cost_x2_sharpe_L`＝**携带**（分片件 legs.L.x2.sharpe_full）
    - `regime_min_sharpe_L`＝**派生**（冻结日收益×v3_state_series 政体分段 bear/bull/chop〔REGIME_MAP 3-way proxy：GREEN→bull/YELLOW→chop/ORANGE|RED→bear·T-22 §3 冻结〕逐段 Sharpe·段<20 窗日缺席→在段缺席=renorm·取在段最小）
    - `bootstrap_ci_low_L`＝**携带**（分片件 dual_nulls.bootstrap_ci[0]）
  - **anti_overfit**：
    - `family_pbo`＝**携带**（e15_roster 族 PBO·判决档案权威·CSCV 不可由 n=4 再导·引用非重算——REEVAL18 §3 同律）
    - `d6_max_abs_corr`＝**派生**（冻结日收益 vs 注册六员同窗日收益·`trial_labor_w2._d6_admit_core` 全套执法·同窗对齐=1630 实收益日〔bar0=构造零点剔除·注册重放面无该日收益〕；ann/regime/dsr 面仍用 1631 全序列=判决面现役口径）
  - **anti_luck**：
    - `batch_dsr`＝**派生**（`science_gates.deflated_sharpe_ratio(冻结日收益, n_trials=4)`·批容量 4·O-1058 改革口径·非全局账本）
- **批内 FDR（L3 改革门第一腿）**：`batch_p_values`＝**携带 signflip_p**（分片件 dual_nulls.signflip_p·全期 leg-L 收益符号翻转显著性双测=P1 标准候选面·W14 改革正典 §5 同源机械）→ `science_gates.bh_batch_fdr(p, q=REFORM_Q_LEVEL=0.10)`·m=4·None 拒收诚实上报禁零填充。
- **合成分与 L3/L4 门**：`science_gates.g2_reform_fdr4d(member_metrics, REFORM_DIM_WEIGHTS, REFORM_SUB_WEIGHTS, batch_p_values, q=REFORM_Q_LEVEL)`——权重/子权/topN 全部冻结常数 import（ret0.30/robust0.30/anti_overfit0.20/anti_luck0.20）；`eligible_reform`=fdr_pass ∧ 合成完备（四维无缺失·缺维拒收零静默填充）∧ D6 admitted；L4 上岗名单=eligible_reform 按合成分降序·每波 top-N=REFORM_TOPN_PER_WAVE(3) 封顶（宽进不滥进·前向月考真终审不变）。
- **E[FP] 名义披露**：0.05×m=**0.2**。
- **幂等与确定性**：产物已存在=no-op exit 0（E15_EMOTION_REEVAL_REFINALIZE=1 唯一重做通道）；全批 L1 确定性零网络零 RNG（携带面零随机·派生面纯函数·注册重放确定性引擎）——**零种子登记面**（R250 一步律不触发）。
- **账本**：零 append（重估面·REEVAL18 §7「ledger_delta 0」先例）；gate_attrition 零行（derive 批无烧格）；如实披露于 §7。

## §4 判据【必填·跑前写死，禁看结果调线】

- `eligible_reform`（L3 改革门）= fdr_pass（bh_q≤REFORM_Q_LEVEL）∧ 合成分完备（四维在册子权全在·缺维 None 拒收）∧ D6 admitted（vs 注册六员 max|corr|<0.7 且批内簇塌缩幸存）。
- 上岗名单资格=eligible_reform ∧ 合成分降序 ∧ ≤3 员（REFORM_TOPN_PER_WAVE）。
- 硬披露门（非淘汰线·逐员必带）：携带/派生 provenance 逐子项、G-REPRO 锚读数（重建 Sharpe==冻结 sharpe_full 4 位舍入）、regime 分段逐段 Sharpe+段日数、D6 撞线对象与 max|corr|、旧判线读数对照列（g1_margin/dsr 全局口径/family_pbo）——新旧口径分离披露。
- 全员判负=合法产出（O-1820 三验③：重估面如实档案化，禁为满载改判线）。

## §5 跑前预测【必填·写死于跑前，跑后对账】

- P1：fdr_pass 数 ∈ **[2,4]**（冻结 signflip_p 实读 0.0/0.0/0.001/0.0015·m=4 BH 单步上调后全部 ≪0.10 → 上界 4；下界 2 留分片数据完整性风险余量）。
- P2：D6 注册撞线拒收数 ∈ **[0,2]**（bear 窗策略族与 VOLATILITY-CE-01 低波注册员日收益相关结构未知；sentiment 双员同族批内簇塌缩可能再折损 0-1）。
- P3：eligible_reform 数 ∈ **[0,3]**（P1∩P2 连乘面·合成分完备门新增失败模式留 0 下界）。
- P4：上岗名单规模 ∈ **[0,3]**（top-3 封顶）。
- P5：batch_dsr（n_trials=4）∈ **[0.25,0.95]**（全局口径实读 0.24-0.53·折减底数 12,063→4 的大幅放松面·但 DSR 上限受原始 Sharpe 约束）。
- P6：regime_min_sharpe_L 全员为负概率 **>50%**（bear 窗现金态主导策略 bull 段 Sharpe 结构性弱·descriptive 不判负）。
- 极端日先验：leg-L 窗（2020-01-02..2026-09-22）内 510300 已知极端日=2024-09-24/09-30 暴力反弹、2024-02-28/2025-04-07/2026-01-19 深跌日；日收益序列为冻结判决面材料（已含上述日）——本批零硬界设计（无 max 硬界判线）·crisis_days_gt8pct 携带披露列。

## §6 产物

- runner：`scripts/e15_emotion_reeval.py`（run / selftest / status；exit 0=正常/no-op、1=门败 VOID 零产物、2=机制故障如实上报勿掩盖）。
- 产物：`results/emotion_reeval/E15-REEVAL-2026-09-22.json`（顶层 evidence_cutoff+cutoff_meta·4 员四维全列+provenance+D6+FDR+合成分+eligible_reform+上岗名单+G-REPRO 锚+新旧判线对照）。
- 池 entry：`results/runnable_pool.json` 新 entry E15-EMOTION-REEVAL-P1-RUN（ready·workers_plan{workers:1,priority:BelowNormal}·worker_class=self-contained·lane_owner=null）。
- F-04 MSG：freeze commit 同窗 fleet/inbox/ 声明（防双机撞建）。

## §7 跑后实证【跑前必须为空——占位纪律：写数字即造假】

## §8 批后复盘【必填·s7-T】

（跑后回填：预测对账＋损耗账（零烧格披露）＋判线当批读数＋回执入轮报告与 CODELY.md 行级追加；若注册新员：注册件带 evidence_cutoff＋live/paper SIGNAL_BUILDERS 接线＋smoke 锚定门复跑；捕获律收口步问「本批有无新方法/新宝藏」有则 knowledge/METHODOLOGY_ASSETS.md 或 TREASURE_REGISTRY.md append。）
