# PERPETUAL-N4-B2 预注册（波级）——**FROZEN · 已冻结（2026-10-03 r606 bm-a 冻结 commit）**

> **状态：FROZEN（冻结 commit=r606 bm-a·五条件冻结门全过机证见下）。冻结后烧批=本地
> SatEngine 队列（engine_owner=bm-a·SATURATION_ENGINE_LAW §1/§2 合同·不入池）；R250
> one-step=消耗窗披露（§5）+本件冻结+模块 WAVE_CONFIGS B2 行同一 commit 落地，冻结后
> 禁再挑。**
> 法：research/PERPETUAL_FACES.md v1.0 §2 N4 行（测量加深面 L24）+ §4（N2/N4 波带行）+
> firm/TRIAL_LABOR_LAW.md §4（跨波累计 N_eff）；席位=O-20261002-2155 P0 引擎面续行
> （B1 链 r600-r605 已闭；本轮 r606=板空+引擎队列空+无在飞判决批→常设线续波）。
> 面性质（法 §2 L24）：N4=**测量加深面**——产物=更深置信面非新注册件，不入候选漏斗，
> 不占语法消耗登记簿行；D6 同族拒收门与去重门只约束候选判决面（N2），N4 免 D6
> 准入（法内豁免行如实引用）。
> runner：scripts/perpetual_faces_n4.py（r606 多波化：per-wave 面（batch/prereg/rows/
> ckpt/seeds）入 WAVE_CONFIGS 行、访问器按 ACTIVE pin 解析、pool worker ctx 携
> seed_base/batch 防 spawn 重导入错标；selftest 19 腿）。

## §0 批件身份【跑前填·冻结时核】

- 批名：PERPETUAL-N4-B2（bootstrap alternate-history 尾律第二波=K 扩深）。
- 波族：N4（B1 同族）；本波=**跨波累计扩深波**（TRIAL_LABOR_LAW §4 跨波累计 N_eff）。
- 成员范围：六员在册同 B1（COMPOSITE-CE-01/02、DROUGHT-CE-01、ENGULF-CE-01、
  NEEDLE-DE-01、VOLATILITY-CE-01）——冻结时以注册面实读为准（成员增删=月界面）。

## §1 伪机制段（α 机制·四选一）

**α = bar 块自助法平行宇宙重放（moving-block bootstrap alternate-history replay）**：
与 B1 同机制逐字（B1 §1 verbatim 继承）：对在册成员的历史 bar 序列做块重采样
（**PINNED-L = 10**·B1 冻结值原样继承——选法=依赖视界 lag 9（带外最大 ACF）→MBB
块长跨越全视界 L≥10；B1 probe ACF 表 receipt 继承+本波 probe 复证）→ 生成 K 个
平行宇宙历史 → 每宇宙经 engine/run_backtest 同源回放（前向不改史；成员出场规则=
成员注册件自有出场轴逐字回放，**禁用引擎缺省出场栈改写**）→ 累计置信面。B2 自有
宇宙 **PINNED-K = 200**（k=0..199·种子=68_701+k，见 §5）。

## §2 数据与面板【跑前探针事实，非结果】

- 面板：core48 在役面板（live.paper.load_core·RW-4 门内建）截断 evidence_cutoff
  2026-09-22（前向不改史=构造性）。**交集轴 T=797**（B1 冻结钉点原样继承：2023-06-13
  ..2026-09-22·48 符号全上市共同纪元）；B2 probe 复证 receipt
  =results/perpetual_faces/n4_b2/probe.json（六员真引擎冒烟·事实面零注册）。
- 重放时长：单宇宙/员 0.137-0.266s（B1 probe 实读）→ B2 6 员 × 200 宇宙
  ≈ 165-320s 墙钟=引擎车道轻波（B1 实烧 17.7-22.7s/片同量级）。

## §3 方法学

- **PINNED-K = 200**（B2 自有宇宙；每宇宙独立 rng=seed=带位值+宇宙序 k，k=0..199
  →实际消耗 gen 68_701..68_900）；块长 **PINNED-L = 10**；重放=engine/run_backtest
  同源（复用 N1/N4-B1 已验证回放管线，禁重写引擎件）。波内成员配对宇宙=同一 k 全员
  同史（跨波不配对——B1 k=0 seed 68_501 与 B2 k=0 seed 68_701 是不同宇宙，池化按
  distinct-seed 完备门合并）。
- 成本：COST_X1 常量 import（13.041bp/边），与判决面同源。

## §4 判据【冻结写死，禁看结果调线；判线一律调共享库 science_gates】

产物面（finalize 腿跑后产出·science_gates verbatim import 禁手抄·TRIAL_LAW §4
跨波累计）：

1. **k_universe_sharpe（池化主面）**：B1 200 宇宙 + B2 200 宇宙 = **K_eff=400** 每
   成员 Sharpe 分布面（median/p10/p90/percentile CI95/正值占比/样本 std）——纯数学
   零引擎重跑；完备门=distinct-seed 恰为 400/员（缺=双烧合并或截断拒收，多=污染拒收）。
2. **k_universe_sharpe_wave_local**：B2 自有 200 宇宙分布面（同上形状）——波间分
   拆披露（B1 面已在 n4_b1_results.json 冻结不重算）。
3. **pooled_max_drawdown / pooled_annual_return / pooled_num_trades**：池化 400 宇宙
   的回撤/年化/交易数分布面（median/p10/p90/CI95/样本 std）——加深轴（宇宙行自 B1
   起即携带全指标，本波为首次入判据面的预注册扩深，非事后补测）。
4. **bootstrap_ci_sharpe**（science_gates import）：实史 center 回放（真史交集轴
   面板·非重采样宇宙）日收益序列 → stationary bootstrap CI95；
   **seed=69_000**（家族 scrnull 带基点·B1 同 seed=确定性同值重发、结果自含）、
   block=10.0、n_resamples=1000（函数缺省面逐字保留）。
5. **dsr_from_stats**（science_gates import）：sr_annualized=实史 center 回放
   Sharpe、sigma_sr=**池化 K_eff=400 宇宙 Sharpe 样本标准差**、
   **n_trials=K_eff=400**（跨波累计试验数·TRIAL_LAW §4；B1 波 200 试验面已冻结
   于 n4_b1_results.json 不改写）。
- N4=测量加深面：**零注册、零漏斗、零晋升判定**（法 §2 L24）——判据只产置信面披露，
  无 pass/fail 晋升线；诚实负发现（CI 下界≤0/DSR≤0.5）照报不阻断。
- 出场轴声明（O-20261001-1108 显式门三选一）：**①策略自有出场**（成员注册件出场轴
  逐字回放=runner ExitPatch+exit_signal=(entry<=0)+dd_control passthrough，引擎缺省
  出场栈禁改写，本节显式声明；与 B1 §4 逐字同）。

## §5 种子（家族窗内消耗扩宽·零新登记·冻结时重扫机证）

- 家族窗（r602 B1 冻结登记 SEED_REGISTRY **perpetual_n4_b1 = 68_501**·三带全域
  68_501..69_999 披露在册）：gen 68_501..68_999 / scrnull 69_000..69_499 /
  unc 69_500..69_999。
- B1 已消耗 gen 68_501..68_700（K=200）；**B2 消耗 gen 68_701..68_900**（K=200·
  家族窗内未用尾段，零新登记值——消耗扩宽在本节披露即可；scrnull/unc 零新消耗：
  §4 面 4 复用同 seed 69_000）。
- 冻结时带扫描重跑（表前进后再裁）：receipt
  results/_r606bma_n4b2_band_scan.py 输出（B2 窗 68_701..68_900 + 家族窗全域 vs
  N1_BANDS 全表 + SEED_REGISTRY 全值 + 保留面 disjoint 机证）。
- 未来 N4 波（B3+）按法典 §4 尾律另行展行时机验防撞。

## §6 跑后只许回填节（已回填 r608 bm-a·2026-10-03 05:1x·波 6/6 烧毕〔04:28→04:51
tick 序贯〕+finalize 面；保留原冻结文本只增不改）

- §6.1 实跑数字（K/L/时长/行数）：**K=200/员 × 6 员 = 1,200 B2 自有宇宙行**（每员
  universes-<ID>.jsonl 200 行·k-set 0..199 完备；六分片 receipt shard-<i>-of-6.json
  全过 _shard_valid）；**L=10**（PINNED·B1 冻结值继承）；SatEngine 引擎车道六分片墙钟
  **59-60s/片**（ledger 行 04:28:05→04:29:04 / 04:34:06→04:35:04 / 04:42:05→04:43:04
  / 04:48:05→04:49:04 / 04:49:04→04:50:04 / 04:50:04→04:51:04；点火窗 04:28→04:51
  tick 序贯 n4B2-0..5of6）；finalize 3.8s（六员真史交集轴 center 回放 + science_gates
  verbatim import；池化宇宙行 2,400 = B1 1,200 + B2 1,200·distinct-seed 400/员完备门
  全过）。
- §6.2 置信面产物指针：**results/perpetual_faces/n4_b2_results.json**（§4 五产物齐：
  池化 K_eff=400 k_universe_sharpe 主面 + wave_local 200 波内拆分 + pooled
  maxdd/ann/ntrades 加深轴 + bootstrap_ci_sharpe（seed 69_000·**与 B1 逐字同值=确定性
  同值重发机证**）+ dsr_from_stats（sr=center 回放 Sharpe·sigma=池化 400 宇宙样本 std·
  **n_trials=K_eff=400**））；分片 receipts=results/p2cal_ext/n4_b2/shard-<i>-of-6.json
  × 6；宇宙行=results/perpetual_faces/n4_b2/universes-<ID>.jsonl × 6；引擎账本行=
  results/saturation_engine/ledger_bm-a.jsonl（face=N4·key n4B2-<i>of6）。
  **诚实读数**（测量加深面·§4 冻结=零 pass/fail 晋升线·判读归月界科学面）：真史
  center 回放 bootstrap CI95 下界>0 者=COMPOSITE-CE-01（+0.153）与 VOLATILITY-CE-01
  （+0.414）两员（与 B1 同两员·同值）；其余四员跨零（CE-02 −0.108 / DROUGHT −0.020
  / ENGULF −1.161 / NEEDLE −0.721·四值与 B1 逐字恒等）；池化 400 宇宙分布 CI95 下界
  六员全负（−0.318..−1.071·平行宇宙脆弱性如实披露）；正值占比 CE-02 0.9225 / CE-01
  0.910 / VOLATILITY 0.7975 / NEEDLE 0.605 / ENGULF 0.580 / DROUGHT 0.525；DSR 六员
  0.0015-0.0024（K_eff=400 试验数下较 B1 波 0.003-0.005 更深度紧缩面如实产出）。

## 冻结门（条件，冻结 commit 前逐条机证）——**五条件全过（r606 bm-a·2026-10-03 04:1x-04:2x）**

1. runner 多波化落地 + selftest 全绿：**19/19 PASS**（S17 访问器恒等〔B1 行=冻结值
   逐字保持〕+S18 B2 针烧标〔batch=PERPETUAL-N4-B2·seed 68_701+k 实证〕+S19 池化
   种子门+前波行 r570 双门；S13/S15 cfg 化后 B1 行为逐字保持）。
2. probe 真引擎面实证：**results/perpetual_faces/n4_b2/probe.json**（面板事实复证
   T=797 交集轴+六员真引擎冒烟 1.34s·probe_wall 1.49s·X1 费率咬合）。
3. 种子带扫描重跑：**results/_r606bma_n4b2_band_scan_receipt.txt**（leg1 家族窗
   68_501..69_999 全三带 vs 现表 N1_BANDS 112 行+SEED_REGISTRY 165 int 全净+leg2
   B2 窗 68_701..68_900 净且与 B1 已烧 68_501..68_700 disjoint+leg3 K=200 算术恒等）。
4. §3/§4 判据写死（判线一律 import science_gates 共享库，禁手抄——§4 面 4/5 两处
   verbatim import 声明在案）。
5. banned_direction_gate 过闸：**results/_r606bma_n4b2_banned_gate_receipt.txt**
   （matched=[]·「no banned direction claimed」·rc0）。
