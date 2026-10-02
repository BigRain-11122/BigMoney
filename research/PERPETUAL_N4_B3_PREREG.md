# PERPETUAL-N4-B3 预注册（波级）——**FROZEN · 已冻结（2026-10-03 r609 bm-a 冻结 commit）**

> **状态：FROZEN（冻结 commit=r609 bm-a·五条件冻结门全过机证见下）。冻结后烧批=本地
> SatEngine 队列（engine_owner=bm-a·SATURATION_ENGINE_LAW §1/§2 合同·不入池）；R250
> one-step=消耗窗披露（§5）+本件冻结+模块 WAVE_CONFIGS B3 行同一 commit 落地，冻结后
> 禁再挑。**
> 法：research/PERPETUAL_FACES.md v1.0 §2 N4 行（测量加深面 L24）+ §4（N2/N4
> 波带行）+ firm/TRIAL_LABOR_LAW.md §4（跨波累计 N_eff）；席位=O-20261002-2155
> P0 引擎面续行（B1 链 r600-r605 闭、B2 链 r606-r608 闭；本轮 r609=r608 尾律
> 时点检查已过=家族窗余尾 99 值在册未耗·B3=尾窗满耗收尾波·判决批在飞
> =FUND-VALUE-P1-NULLS〔bm-b 池面车道〕试用期线免起草·本波=N4 席位自有链）。
> 面性质（法 §2 L24）：N4=**测量加深面**——产物=更深置信面非新注册件，不入
> 候选漏斗，不占语法消耗登记簿行；D6 同族拒收门与去重门只约束候选判决面
> （N2），N4 免 D6 准入（法内豁免行如实引用）。
> runner：scripts/perpetual_faces_n4.py（r609 B3 行落地+**不等 K 池化算术修**：
> k_eff=本波 K+各前波冻结 PINNED-K 逐波和（B3 99+200+200=499）；旧式
> K*(1+len(pool)) 同 K 假设对首个不等 K 波必错（99*3=297≠499）——修法与
> S20 腿同窗；selftest 20 腿）。

## §0 批件身份【跑前填·冻结时核】

- 批名：PERPETUAL-N4-B3（bootstrap alternate-history 尾律收尾波=家族窗满耗）。
- 波族：N4（B1/B2 同族）；本波=**跨波累计扩深收尾波**（TRIAL_LABOR_LAW §4
  跨波累计 N_eff；家族 gen 窗 68_501..68_999 恰好满耗=499 宇宙/员，窗后无余尾）。
- 成员范围：六员在册同 B1/B2（COMPOSITE-CE-01/02、DROUGHT-CE-01、
  ENGULF-CE-01、NEEDLE-DE-01、VOLATILITY-CE-01）——冻结时以注册面实读为准
  （成员增删=月界面）。

## §1 伪机制段（α 机制·四选一）

**α = bar 块自助法平行宇宙重放（moving-block bootstrap alternate-history replay）**：
与 B1/B2 同机制逐字（B1 §1 verbatim 继承）：对在册成员的历史 bar 序列做块重采样
（**PINNED-L = 10**·B1 冻结值原样继承——选法=依赖视界 lag 9（带外最大 ACF）→MBB
块长跨越全视界 L≥10；B1 probe ACF 表 receipt 继承+本波 probe 复证）→ 生成 K 个
平行宇宙历史 → 每宇宙经 engine/run_backtest 同源回放（前向不改史；成员出场规则=
成员注册件自有出场轴逐字回放，**禁用引擎缺省出场栈改写**）→ 累计置信面。B3 自有
宇宙 **PINNED-K = 99**（k=0..98·种子=68_901+k，见 §5）。

## §2 数据与面板【跑前探针事实，非结果】

- 面板：core48 在役面板（live.paper.load_core·RW-4 门内建）截断 evidence_cutoff
  2026-09-22（前向不改史=构造性）。**交集轴 T=797**（B1 冻结钉点原样继承：
  2023-06-13..2026-09-22·48 符号全上市共同纪元）；B3 probe 复证 receipt
  =results/perpetual_faces/n4_b3/probe.json（六员真引擎冒烟·事实面零注册）。
- 重放时长：单宇宙/员 0.137-0.266s（B1 probe 实读）→ B3 6 员 × 99 宇宙
  ≈ 82-158s 墙钟=引擎车道轻波（B2 实烧 59-60s/片 200 宇宙同量级·B3 片=半量）。

## §3 方法学

- **PINNED-K = 99**（B3 自有宇宙；每宇宙独立 rng=seed=带位值+宇宙序 k，k=0..98
  →实际消耗 gen 68_901..68_999=家族窗尾段恰满耗）；块长 **PINNED-L = 10**；
  重放=engine/run_backtest 同源（复用 N1/N4-B1/B2 已验证回放管线，禁重写引擎件）。
  波内成员配对宇宙=同一 k 全员同史（跨波不配对——B1/B2/B3 各 k 是不同宇宙，
  池化按 distinct-seed 完备门合并）。
- 成本：COST_X1 常量 import（13.041bp/边），与判决面同源。

## §4 判据【冻结写死，禁看结果调线；判线一律调共享库 science_gates】

产物面（finalize 腿跑后产出·science_gates verbatim import 禁手抄·TRIAL_LAW §4
跨波累计）：

1. **k_universe_sharpe（池化主面）**：B1 200 + B2 200 + B3 99 宇宙 = **K_eff=499**
   每成员 Sharpe 分布面（median/p10/p90/percentile CI95/正值占比/样本 std）——
   纯数学零引擎重跑；完备门=distinct-seed 恰为 499/员（缺=双烧合并或截断拒收，
   多=污染拒收）；k_eff 算法=本波冻结 K+各前波冻结 PINNED-K 逐波和（不等 K 池化
   正法·S20 腿机证；**禁 K*(1+len(pool)) 同 K 假设式**）。
2. **k_universe_sharpe_wave_local**：B3 自有 99 宇宙分布面（同上形状）——波间分
   拆披露（B1/B2 面已在各自 results 冻结不重算）。
3. **pooled_max_drawdown / pooled_annual_return / pooled_num_trades**：池化 499
   宇宙的回撤/年化/交易数分布面（median/p10/p90/CI95/样本 std）——加深轴（B2
   起入判据面的预注册扩深轴原样继承）。
4. **bootstrap_ci_sharpe**（science_gates import）：实史 center 回放（真史交集轴
   面板·非重采样宇宙）日收益序列 → stationary bootstrap CI95；
   **seed=69_000**（家族 scrnull 带基点·B1/B2 同 seed=确定性同值重发、结果自含）、
   block=10.0、n_resamples=1000（函数缺省面逐字保留）。
5. **dsr_from_stats**（science_gates import）：sr_annualized=实史 center 回放
   Sharpe、sigma_sr=**池化 K_eff=499 宇宙 Sharpe 样本标准差**、
   **n_trials=K_eff=499**（跨波累计试验数·TRIAL_LAW §4；B1/B2 波面已冻结不改写）。
- N4=测量加深面：**零注册、零漏斗、零晋升判定**（法 §2 L24）——判据只产置信面
  披露，无 pass/fail 晋升线；诚实负发现（CI 下界≤0/DSR≤0.5）照报不阻断。
- 出场轴声明（O-20261001-1108 显式门三选一）：**①策略自有出场**（成员注册件出场轴
  逐字回放=runner ExitPatch+exit_signal=(entry<=0)+dd_control passthrough，引擎缺省
  出场栈禁改写，本节显式声明；与 B1/B2 §4 逐字同）。

## §5 种子（家族窗内消耗扩宽·零新登记·冻结时重扫机证）

- 家族窗（r602 B1 冻结登记 SEED_REGISTRY **perpetual_n4_b1 = 68_501**·三带全域
  68_501..69_999 披露在册）：gen 68_501..68_999 / scrnull 69_000..69_499 /
  unc 69_500..69_999。
- B1 已消耗 gen 68_501..68_700（K=200）；B2 已消耗 gen 68_701..68_900（K=200）；
  **B3 消耗 gen 68_901..68_999（K=99·家族窗尾段恰满耗，窗后 gen 零余尾——
  家族窗消耗收口披露）**，零新登记值——消耗扩宽在本节披露即可；scrnull/unc
  零新消耗：§4 面 4 复用同 seed 69_000。
- 冻结时带扫描重跑（表前进后再裁）：receipt
  results/_r609bma_n4b3_band_scan_receipt.txt（B3 窗 68_901..68_999 + 家族窗全域
  vs N1_BANDS 全表 + SEED_REGISTRY 全值 + B1/B2 已烧 disjoint + K=99 算术
  机证）。
- 未来 N4 波（B4+）：家族 gen 窗已满耗——**新波须新家族窗登记**（法典 §4
  展行+R250 one-step）或止波（测量加深面无限深烧禁令·O-20260930-1901 意义门：
  满耗收口即家族面完备，无余尾即无 B4 时点）。

## §6 跑后只许回填节（已回填 r609 bm-a·2026-10-03 05:4x·波 6/6 烧毕〔05:36→05:40
tick 序贯+调度任务并行〕+finalize 面；保留原冻结文本只增不改）

- §6.1 实跑数字（K/L/时长/行数）：**K=99/员 × 6 员 = 594 B3 自有宇宙行**（每员
  universes-<ID>.jsonl 99 行·k-set 0..98 完备；六分片 receipt shard-<i>-of-6.json
  全过 _shard_valid·k_burned=99/99）；**L=10**（PINNED·B1 冻结值继承）；SatEngine
  引擎车道六分片墙钟 **15.6-57.8s/片**（账本行已 flush 四片：05:36:05→05:37:04 /
  05:37:05→05:37:36 / 05:37:36→05:38:04 / 05:38:05→05:38:22·片 4-5 账本行随引擎
  缓冲后续 flush；点火窗 05:36→05:40=调度任务 tick 与会话 tick 序贯接力）；
  finalize 3.8s（六员真史交集轴 center 回放 + science_gates verbatim import；池化
  宇宙行 2,994 = B1 1,200 + B2 1,200 + B3 594·distinct-seed 499/员完备门全过〔不等
  K 池化 k_eff=99+200+200=499·S20 腿机证的逐波和算法〕）。
- §6.2 置信面产物指针：**results/perpetual_faces/n4_b3_results.json**（§4 五产物齐：
  池化 **K_eff=499** k_universe_sharpe 主面〔家族窗满耗收口面〕+ wave_local 99 波内
  拆分 + pooled maxdd/ann/ntrades 加深轴 + bootstrap_ci_sharpe（seed 69_000·**与
  B1/B2 逐字同值=确定性同值重发机证**）+ dsr_from_stats（sr=center 回放 Sharpe·
  sigma=池化 499 宇宙样本 std·**n_trials=K_eff=499**））；分片 receipts=
  results/p2cal_ext/n4_b3/shard-<i>-of-6.json × 6；宇宙行=results/perpetual_faces/
  n4_b3/universes-<ID>.jsonl × 6；引擎账本行=results/saturation_engine/
  ledger_bm-a.jsonl（face=N4·key n4B3-<i>of6）。
  **诚实读数**（测量加深面·§4 冻结=零 pass/fail 晋升线·判读归月界科学面）：真史
  center 回放 bootstrap CI95 下界>0 者=COMPOSITE-CE-01（+0.153）与 VOLATILITY-CE-01
  （+0.414）两员（与 B1/B2 同两员·同值=seed 69_000 确定性重发）；其余四员跨零
  （CE-02 −0.108 / DROUGHT −0.020 / ENGULF −1.161 / NEEDLE −0.721·四值与 B1/B2
  逐字恒等）；池化 499 宇宙分布 CI95 下界六员全负（−0.363..−1.048·较 B2 面
  −0.318..−1.071 微幅收紧·平行宇宙脆弱性如实披露）；正值占比 CE-02 0.9018 /
  CE-01 0.8998 / VOLATILITY 0.8016 / NEEDLE 0.6172 / ENGULF 0.5932 / DROUGHT
  0.523；DSR 六员 0.0012-0.0019（K_eff=499 试验数下较 B2 面 0.0015-0.0024 更深度
  紧缩面如实产出）。**家族窗满耗收口披露**：gen 68_501..68_999 全 499 值已烧尽
  （B1 200+B2 200+B3 99），N4 家族窗零余尾——后续深烧须新家族窗登记（§5 B4+ 行）。

## 冻结门（条件，冻结 commit 前逐条机证）——**五条件全过（r609 bm-a·2026-10-03 05:3x-05:4x）**

1. runner B3 行+不等 K 池化算术修落地 + selftest 全绿：**20/20 PASS**（S11 B1
   verbatim+B2/B3 行合同〔B3 seed 68_901+pool_waves (B1,B2)+68_901+98==68_999
   家族窗顶恰闭〕+S17 三波访问器恒等+S20 不等 K 池化算术〔99+200+200=499·B2 面
   400 复现·B1 面 200 复现〕；r606 B1/B2 腿逐字保持）。
2. probe 真引擎面实证：**results/perpetual_faces/n4_b3/probe.json**（面板事实复证
   T=797 交集轴〔1630 并集·48 符号·2023-06-13..2026-09-22 与 B1/B2 冻结值恒等〕
   +六员真引擎冒烟 1.32s·probe_wall 1.47s·X1 费率咬合）。
3. 种子带扫描重跑：**results/_r609bma_n4b3_band_scan_receipt.txt**（leg1 家族窗
   68_501..69_999 全三带 vs 现表 N1_BANDS 112 行+SEED_REGISTRY 165 int 全净+leg2
   B3 窗 68_901..68_999 净且与 B1/B2 已烧 disjoint+leg3 K=99 算术恒等+家族窗顶
   68_999 恰闭）。
4. §3/§4 判据写死（判线一律 import science_gates 共享库，禁手抄——§4 面 4/5 两处
   verbatim import 声明在案）。
5. banned_direction_gate 过闸：**results/_r609bma_n4b3_banned_gate_receipt.txt**
   （matched=[]·「no banned direction claimed」·ADMIT rc0）。
