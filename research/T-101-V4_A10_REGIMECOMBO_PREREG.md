# T-101-V4-A10-REGIMECOMBO 预注册 —— 政体门「组合/输入特征」用法首测（v4 政体门臂·组合信息聚合子线）

> 血统：r231 §4 预案兑现（「66 KILL+6 D6-REJECT 门=C1 输入特征面注记保留·择时判负不借判候选资格」→ 单门全仓择时两子线〔A2 r433 / A158-FV r441〕均关后，组合/输入特征路线=指名下一步）。指名输入锚=r441：`588000|VSUMD30_q90` beat6m/12m/24m=0.694/0.728/0.835·×2 成本超额仍 +10.5%·bootstrap ci_lower_positive。
> 状态：**FROZEN——冻结于跑前·2026-09-29 19:0x·bm-a r442（起草机同轮一次冻结·臂线批先例 r441：一次冻结即烧·非 TRIAL_LABOR 波线协议面）**。本冻结 commit 同窗含 SEED_REGISTRY 两键注册（R250 一步律）+runner。

## §0 批件身份【必填·跑前】

- 批名：**T-101-V4-A10-REGIMECOMBO**·批内格数：**16**（组合器 2 形态 × 成员 5 × 成本 2——C1 形态仅 3 员有 accept 门族→C1=3 员×2 成本=6 格 + C2=5 员×2 成本=10 格）；null 对照 K=200/格·另计不膨胀策略数。本批=**试验判决批**（入 trials_ledger，batch_trials=16）。
- 部门归属：dept:研究（链条研究线·T-101 v4 政体门臂）。
- 算力预算：est 1-4 min 单进程（5 员 157 因子派生 + 16 格连续权重回测 + 3,200 随机门 null 组合 + 双 nulls B=2000/P=2000 + PBO CSCV 16 格）—trivial compute in-round 合法（O-2100·r441 58.3s 同族先例）；worker 数 1；批报告必带 audit 段。
- 车道：**bm-a**（五员面板 data/daily in-repo·lane-free·本机直跑）。
- 语法查重/防重跑：组合用法=**未被消费面**——prescreen 85 格=单门 0/1 开关用法已消费；A158-FV 9 格=单门全仓择时全量判决已消费；本批=同门态源在「多门连续权重组合器」用法面的首测（非同语法重跑）；同语法重跑须新 prereg（本冻结 commit=防重跑锚·BACKTEST_SCIENCE 重跑律）。

**§0-C1 组合器形态【冻结·禁搜参·全冻死】**：
- **C1「ACCEPT 门族均值」**：成员 m 的 r441 冻结 9 格塌缩表中该成员的全部格子门态的算术均值 → w_t∈[0,1]。冻结分组成员表（r441 §0-C 实算·上游公开面）：510300={RANK30_q90, STD20_q90}·510500={CNTN20_q10, RANK30_q90, RSQR10_q90, SUMN10_q10}·588000={STD10_q90, STD20_q90, VSUMD30_q90}；510050/512100 无 accept 格 → C1 不适用（诚实跳格，不造格）。
- **C2「17 门库均值」**：成员 m 的 RECHECK-CONFIRM 17 门（`results/gate_recheck_a158.json::library_entries`·r231 同门逐字）全部门态算术均值 → w_t（跨门信息聚合强版本——含非自身指名门，机制宣称=门族整体信息而非单门挑选）。
- **禁搜参声明**：两形态的权重=等权均值，无任何权重搜索/优化/排序选择；门池=上游冻结表逐字；θ 阈值类参数零引入。

**G-ACCEPT 门（fail-closed）**：runner 实读 `results/gate_timing_prescreen_a158.json` 提取 SURVIVE∧D6-ACCEPT 格集==冻结 13 表（逐位）∧ r441 §0-C 塌缩规则再 derive==冻结 9 表（逐位）∧ `results/gate_recheck_a158.json::library_entries`==冻结 17 门表——任一不符=exit 2 拒烧（上游漂移≠数据腐坏）。

## §1 α 机制段【必填·D6】

四选一：**[x] 风险厌恶环**——指针引用 GATE-TIMING-PRESCREEN-A158 prereg §1（同机制同环：因子自身极端状态入场持续性状态回归红移假设）。本批子假设=**组合信息聚合**：多门开态的等权均值携带比任何单门更多的下一期条件信息（单门信息=A2/A158 两子线已证伪；聚合降噪面从未测过）；若聚合权重的全量风险调整表现不过批自随机门组合 null 池 → 组合子线判负，与单门子线合流=「政体门族择时用法全谱关闭」合法结论。

**同族相关性准入检查【D6】**：
- vs r441 A158-FV 9 格单门线（同门态源=beta 同源族·预声明 r433 0.9424 判例）：本批逐格与 9 格单门日收益序列 pairwise intersection max|corr|≥0.7 → 该组合格 REJECT（beta 重复·非独立臂资格）；<0.7 如实披露。
- 批内互相关：16 格间日收益 |corr| 矩阵逐格落 JSON（冗余裁决=上游披露面授权·r231 先例：批内不越权 kill、跨批 D6 归准入面）。
- vs 在册六员：paper_export 无日序列（r434 CORRSOURCE 实证）→ D6 绑定门归 s4 intake 切片（W10 先例）——本批如 FV-PASS 照此 defer 注记。

## §2 数据与面板【必填·跑前探针事实】

- 宇宙：五员冻结宇宙 O-1555={510300, 510050, 510500, 512100, 588000}；判决格仅涉 5 员全量（C2）；C1 仅 3 员（510300/510500/588000）——512100/510050 无 accept 门族为初筛事实非排除。
- **数据锚四元组（G-ANCHOR-FACE）**：`data/daily/sh<码>.csv` + `pd.read_csv` raw 直读截断（`tpl.load_panel` 单源·探针-锚同面断言内建）；全史起算+门预热 rolling(252, min_periods=120)→首可判 bar=第 120 行（0 基）。
- **冻结行数锚（@2026-09-28·r231 同表）**：510300=3486 / 510050=5251 / 510500=3289 / 512100=2405 / 588000=1425；尾行一律 2026-09-28（runner 断言）。
- **evidence_cutoff=2026-09-28**（D2 前向锁·r231 同面）；cutoff 后新 bar 不回流；结果 JSON 顶层必带 `science_gates.cutoff_meta`。

## §3 方法学【必填】

- **执行机器零重实现（import 单源）**：`t101_v4_a2_prescreen`（tpl：load_panel/regime_segment/sharpe/ann_ret/max_drawdown·T+1 开盘代理 O-1132）；`a158_tsgate_probe`（probe：alpha158_factors/gate_universe·157 因子 qlib-verbatim port·门构造 rolling(252, min_periods=120).quantile 冻结）；`science_gates`（sg：g1_prime_v2/g2_registration_v2/deflated_sharpe_ratio/append_ledger/SEED_REGISTRY）；`screening.pbo.cscv_pbo`（CSCV 8 块冻结）。
- **连续权重回测语义（本批新面·冻结定义）**：w_raw,t = 该格门池门态算术均值（t 日门态·因子窗口全预热后）；生效权重 w_eff,t = w_raw,{t-1}（T+1 开盘代理·同 tpl.shift 语义·w_raw NaN→0 预热零仓）；日收益 r_strat,t = w_eff,t × r_t − |w_eff,t − w_eff,{t-1}| × cost_rate。**成本口径（保守冻结）**：cost_rate=0.001/每单位 |Δw|（0.1% 往返/满换手——与 0/1 门控等价口径〔0.05%/腿〕的 2 倍保守面：0→1→0 完整开关周期按 |Δw|=2 收 0.2%）；×2 压测腿=0.002/单位 |Δw|。IS≤2016-12-31 / OOS≥2017-01-01（SPLIT 同面）。
- **trade/entries 口径（G1 双口径输入·冻结定义）**：trade event=|Δw_eff,t|≥0.10 的交易日数（阈值冻结·连续权重版的「开平仓事件」代理）；n_entries=OOS trade events；entries_ok=OOS trade events≥15（tpl.MIN_OOS_ENTRIES 同值）。
- **随机门组合 null（批自 null 族池）**：K=200/格·每 null=从 probe.gate_universe 314 门池随机抽 K_gates 门（K_gates=该格门池大小：C1 成员=该成员 accept 格数·C2=17）等权均值→同构造连续权重回测；seed 基=`SEED_REGISTRY["t101_v4_a10_combo_scrnull"]`=**20314000**（本批注册·三步律 r441 过：118 int 基零撞·band 20314xxx-20315xxx 全空·首元素 Sobol 0.7516/0.2982 与全部既有带基互异·rg 全仓命中=data\daily\sz159529.csv volume 列数值巧合=69 批先例排除面）；3,200 null Sharpe 全收=**批自 null 族池**（P4_EXT_TILT 语义）。
- **双 nulls（W1 `_dual_nulls` 语义逐字）**：块自助 B=2000·block=20 circular（均值 CI）；符号翻转 P=2000（双侧 p）；seed=[`SEED_REGISTRY["t101_v4_a10_combo_unc"]`=**20314500**, cell_idx]·cell_idx=冻结 16 格表序。
- **虚拟起点窗网格（三窗·描述面恒带）**：{6m=126, 12m=252, 24m=504} 交易日窗；起点=每交易日 p∈[120, n−w]（W1 同径日频起点·重叠窗如实披露：推断主责归 nulls/skill line 非窗计数）；每窗策略收益 vs **同员 B&H 同窗收益**（逐格批自被动=REPO_CALENDAR_P2 语义）；段=起点日 510300 MA200 政体（bear/bull/chop·tpl.regime_segment 逐字）。
- **G1' v2（共享库禁手抄）**：`sg.g1_prime_v2(sharpe_full, returns_full, batch_cells=16, n_trades, n_entries, null_pool=批自 null 族池, passive_override=同员 B&H 全期 Sharpe)`——skill line N_eff=ledger 活头+16 数目驱动；逐格批自（三员三谳 REPO_CALENDAR_P2）。
- **DSR**：`sg.deflated_sharpe_ratio(returns_full, n_trials=本批 append 后活头)`（跨波不重置·W2 同面；禁 dsr_from_stats 充数）。
- **G2 注册资格 v2（共享库）**：`sg.g2_registration_v2(g1_pass, dsr, pbo)`。**PBO 族面（跑前冻结）**：本批网格=组合器 2 形态×成员×成本——族=每成员「同门态源已试配置全网格」（C1 成员格+C2 成员格+上游 prescreen 17 门单门格=该员门族已试配置并集·完整自历矩阵零对齐损）→ 判格承本员网格 PBO；成员子网格数<8 按冻结法如实记 insufficient 披露行（非 G2 输入）。跨员判格集无完整公共历 → 批级单矩阵不成立。
- 分段恒带：bear/bull/chop OOS 逐段年化（≥30 日段才计）。
- 账本：`sg.append_ledger("T-101-V4-A10-REGIMECOMBO", 16, "t101_v4_a10_regimecombo.json", evidence_cutoff="2026-09-28")`（finalize 时落·线性）。

## §4 判据【必填·跑前写死，禁看结果调线】

**FV-PASS（注册候选资格）= 四条合取（全量判决面）**：
1. **G1' v2 pass**（skill line+bootstrap CI 下界>0+trade 门 entries_ok——共享库逐条）；
2. **DSR ≥ 0.95**（原始收益 deflated_sharpe_ratio·n_trials=append 后活头）；
3. **成本 ×2 压测**：OOS 超额（0.2% 往返口径）> 0；
4. **G2 eligible_v2**（G1∧DSR∧PBO≤0.25·共享库）。
- FV-PASS 格→s4 intake 切片（D6 绑定门对在册六员+存活者两轮→STRATEGY_LIBRARY 注册+纸盘上岗按 W10 §s4 律）；FV-FAIL 格→组合子线关面如实入 §7+attrition（禁换参重跑·同语法重跑要件）；零 FV-PASS=「门态组合等权聚合择时用法判负」合法判决照报不粉饰。
- 多重检验税披露：n_wave=16 判格·E[FP]=0.05×16=**0.80**；N_eff 累计照 TRIAL_LABOR_LAW §4 跨波不重置（活头实读）。
- 描述条款恒带（非判线）：全期 maxdd≥−35% 地板·IS/OOS 反号·政体依赖性·entries 数。
- D6 判线（§1 预声明）：vs 单门 9 格 max|corr|≥0.7=REJECT（beta 重复）；批内冗余披露不 kill。

## §5 跑前预测【必填·写死于跑前】

1. **G1' line 大概率全灭主预期**：同门态源（beta 同源族）+单门两子线已全灭（r433 9/10 判负·r441 0/9）→ 组合线 Sharpe 大概率仍在线下（批自 null 池 μ≈0 附近·skill line 极端项由 σ_null×√(2·ln N_eff) 主导）；**C2 17 门均值≈常数高仓位**（17 门平均开态若长期 >0.5，w 波动小→策略≈高仓位 B&H+成本拖累→OOS 超额预期为负）；C1 少门均值波动大但信息面窄→大概率不过 bootstrap CI。
2. **唯一例外可能面**：聚合降噪后 Sharpe 抬升过批自线（VSUMD30 588000 单格证据外溢）；若出现必落在 588000 C1 格（3 门含指名门），且 D6 vs 588000|VSUMD30 单门格大概率 |corr|≥0.7 → REJECT 兜底（beta 重复预声明处置）。
3. **成本 ×2 分化**：C2 高换手格（门态均值日波动大者）压测翻负主预期；C1 低 entries 格成本拖累小但 Sharpe 低。
4. **D6 主预期**：C1 各员格 vs 该员最强单门格 corr≥0.7 高发（少门均值≈被单门主导）→ 批内 REJECT 高发主预期。
5. **PBO 族面**：门族已试配置中垃圾配置占多数（prescreen 85 格 66 KILL）→ 族 PBO>0.25 主预期（G2 不可过为主预期）。

## §6 产物

- 结果：`results/t101_v4_a10_regimecombo.json`（顶层 evidence_cutoff+cutoff_meta+audit 段+16 判格全量+null 池统计+D6 矩阵+PBO 族面+三窗/分段描述面）
- 轮报告回执行 + `results/gate_attrition.bm-a.json` 追加行 + v4 臂表 A10 行（research/T-101-V4_PREREG.md 臂表）
- 判负处置预案（O-1820 三验③）：FV-FAIL/REJECT 格=C1 输入特征面注记保留（择时判负不借判候选资格·GATE-RECHECK-A158 L17 邻接披露双向生效）；组合线全灭=「政体门族择时用法全谱关闭」结论成立（单门 A2/A158+组合 A10 三子线），C1 路线唯一存活去向=输入特征面（供下游组合器/预测器消费）。

## §7 跑后实证【跑前必须为空——占位纪律：写数字即造假】

- （跑前为空）

## §8 批后复盘【必填·s7-T】

- （跑前为空）
