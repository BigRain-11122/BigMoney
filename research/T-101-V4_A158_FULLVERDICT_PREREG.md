# T-101-V4-A158-FULLVERDICT 预注册 —— A158 择时 13 格合格面·簇坍缩 9 格全量判决（v4 政体门臂锦标赛判决面）

> 【状态：FROZEN——跑前 commit 冻结】本件=T-101 v4 政体门臂「A158 量化门择时」线的全量判决批预注册。上游链：GATE-RECHECK-A158（bm-a r439·17 门 RECHECK-CONFIRM 库）→ GATE-TIMING-PRESCREEN-A158（bm-c r231·85 格初筛→SURVIVE-D6-ACCEPT **13 格**·r433 律必经关已过）→ **本批（13 格簇坍缩→9 格全量判决）**。跑前冻结于烧批前；跑后只许回填 §7/§8，禁改判据禁重跑（工程修复重跑须双跑留痕）。
> 令源/车道：MSG-20260929-1800-bm-c-ALL（「bm-a's v4 arm prereg drafting (multi-gate combination design) remains bm-a's next-step lane」·D-20260929-02 双信号法：声明已落 origin+本件冻结 commit=双信号）；任务板血统=T-101（v3 done 票·v4=版本批新代·A2 先例引法同面）。
> 统摄律：BACKTEST_SCIENCE.md v2 · BACKTEST_PLAN.md 三铁律 · TRIAL_LABOR_LAW §1-§4 · RANDOM_LARGE_SAMPLE_LAW v1.0 · O-1820(3) consumer_plan 必填 · O-2115 三态标注 · W10 冻结法「PBO 族<8=insufficient 如实→G2 不可过」。

## §0 批件身份【必填·跑前】

- 批名 / 批号：**T-101-V4-A158-FULLVERDICT**·批内格数＝**9**（13 合格格簇坍缩后·坍缩规则见 §0-C·null 对照 K=200/格另计不膨胀策略格）；本批=**试验判决批**（入 trials_ledger，batch_trials=9）。
- 部门归属：dept:研究（链条研究线·T-101 v4 政体门臂）。
- 算力预算：est 1-4 min 单进程（9 格×K=200 同掩码 null≈1,800 次 daily_returns 直积+双 nulls 向量化 B=2000/P=2000+窗网格纯算术+5 员×17 列 PBO CSCV 70 组合）·trivial compute in-round 合法（O-2100·r231 85 格 30.4s 同族先例）；worker 数=1；批报告必带 audit 段。
- 车道：**bm-a**（五员面板 data/daily in-repo·lane-free·本机直跑）。
- 语法查重/防重跑：候选集=上游已落地 13 格（零生成步零参数网格——配置全冻结于 RECHECK 库+本件 §0 表）；同语法重跑须新 prereg（本冻结 commit=防重跑锚·BACKTEST_SCIENCE 重跑律）；TRIAL_GRAMMAR_LEDGER W1-W10 已核——本批择时语法=GATE-TIMING-PRESCREEN 已消费面的**判决升格步**（同配置不同判据面），非同语法重跑。

**§0-C 簇坍缩规则（跑前冻结·坍缩输入=上游已落地公开面）**：
- 规则：对每员的 accept 集内，以 prescreen `d6.intra_library_disclosure` 的策略日收益 |corr|≥0.7 为边建连通分量；每分量保 **1 格=该分量内 `oos_excess_vs_bh` 最高者**（并列取门名字典序最低）；坍缩剔除格=冗余披露非判负（上游判据面维持有效）。
- 实算（输入=r231 已落地 JSON·r441 bm-a 探针复核）：588000 accept 7 格中 {RESI60_q90, SUMN10_q10, VSUMD10_q90, VSUMD20_q90, VSUMD30_q90} 经 ≥0.7 边连通成一分量（RESI60–SUMN10 0.7653·RESI60–VSUMD30 0.7166·VSUMD10–VSUMD20 0.8242·VSUMD10–VSUMD30 0.7434·VSUMD20–VSUMD30 0.8054）→保 **588000|VSUMD30_q90**（超额 +11.96% 分量内最高）；STD10/STD20 max|corr|=0.667/0.552<0.7 独立保留。510300 两格（互 corr 0.2674）与 510500 四格（max 0.5527）零坍缩。
- **冻结 9 格表**（成员|门）：`510300|RANK30_q90 · 510300|STD20_q90 · 510500|CNTN20_q10 · 510500|RANK30_q90 · 510500|RSQR10_q90 · 510500|SUMN10_q10 · 588000|STD10_q90 · 588000|STD20_q90 · 588000|VSUMD30_q90`。

**G-ACCEPT 门（fail-closed）**：runner 实读 `results/gate_timing_prescreen_a158.json` 提取 SURVIVE∧D6-ACCEPT 格集==冻结 13 格表（逐位）；再按 §0-C 规则重derive 坍缩==冻结 9 格表（逐位）——任一不符=exit 2 拒烧（上游漂移·面错配非数据腐坏）。

## §1 α 机制段【必填·D6】

四选一：**[x] 风险溢价**——指针引用 GATE-TIMING-PRESCREEN-A158 prereg §1（同机制同族：因子自身极端态入场连续持有择时·状态回归溢价·17 门全族机制不重复陈述）；本批=该机制在全量判决面（虚拟起点窗×成本压测×双 nulls×G1'/G2）的重测升格步。

**同族相关性准入检查【D6】**：
- vs 五员 B&H：prescreen 已过（13 格 max|corr|<0.7）；本批**逐格复验**同面（pairwise intersection·pit-115 禁五员 inner-join）≥0.7 → 本批 REJECT；
- 批内互相关：§0-C 簇坍缩=跑前处置（唯一 D6 批内预处置先例=r231 披露面授权「冗余裁决权归 v4 prereg 起草轮」）；9 格间跨员互相关披露面照落 JSON（跨员=不同标的非同族复制）；
- vs 在册六员：paper_export 无日序列（r434 CORRSOURCE 实证）→ **D6 绑定门归 s4 intake 切片**（W10 先例：G2 eligible→intake D6 绑定门对在册+存活者两两）；本批如实 defer 注记。

## §2 数据与面板【必填·跑前探针事实】

- 宇宙：五员冻结宇宙 O-1555={510300, 510050, 510500, 512100, 588000}；判决格仅涉 3 员（510300/510500/588000）——512100 无合格格、510050 无合格格（初筛事实·非排除）。
- **数据锚面四元组（G-ANCHOR-FACE）**：`data/daily/sh<码>.csv`+`pd.read_csv` raw 直读截断（`tpl.load_panel` 单源·探针-锚同面断言内建）+全史起算+门预热 rolling(252, min_periods=120)→首可判 bar=第 120 行（0 基）。
- **冻结行数锚（@2026-09-28·r231 同表）**：510300=3486 / 510050=5251 / 510500=3289 / 512100=2405 / 588000=1425；尾行一律 2026-09-28（runner 断言）。
- **evidence_cutoff=2026-09-28**（D2 前向锁盒·r231 同面）；cutoff 后新 bar 不回流；结果 JSON 顶层必带 `science_gates.cutoff_meta`。
- **G-P1 门（fail-closed）**：`results/gate_recheck_a158.json::library_entries`==冻结 17 门表 ∧ 17 门 ⊆ `results/a158_tsgate_p1.json` PASS-48 集（r231 同门逐字）。

## §3 方法学【必填】

- **执行机器零重实现（import 单源）**：`t101_v4_a2_prescreen`（tpl：load_panel/position_series/daily_returns/sharpe/ann_ret/max_drawdown/count_entries/regime_segment·T+1 开盘代理 O-1132）+ `a158_tsgate_probe`（probe：alpha158_factors/gate_universe·157 因子 qlib-verbatim port·门构造 rolling(252, min_periods=120).quantile 冻结）+ `science_gates`（sg：g1_prime_v2/g2_registration_v2/deflated_sharpe_ratio/append_ledger/SEED_REGISTRY）+ `screening.pbo.cscv_pbo`（CSCV 8 块冻结）。
- 基础面：连续门控择时（gate open→全仓/gate closed→现金腿 0%）·成本 0.05%/腿（0.1% 往返·r231 同面）·IS≤2016-12-31/OOS≥2017-01-01（588000 全史 OOS·is_n=0 如实）。
- **成本 ×2 压测**：压测腿 0.10%/腿（0.2% 往返）——`daily_returns` 循环体模板逐字镜像+cost 参数化（r366 镜像律：selftest 断言 cost=0.0005 时与 `tpl.daily_returns` 逐位恒等）；压测判线=OOS 超额（×2 成本）>0。
- **同掩码循环位移 null**：K=200/格·seed 基=`SEED_REGISTRY["t101_v4_a158_fv_scrnull"]`=**20313000**（本批登记·三步法 r441 过：114 int 基零撞值/首元素零撞/rg 命中=数据巧合非种子面）·rng 每 cell 重init（模板语义）；1,800 null Sharpe 全收=**批自 null 族池**（P4_EXT_TILT 面：择时域批自校准线·替代 stock 域 collector 缺位）。
- **双 nulls（W1 `_dual_nulls` 语义逐字）**：块自助 B=2000·block=20 circular（均值 CI）+ 符号翻转 P=2000（双侧 p）·seed=[`SEED_REGISTRY["t101_v4_a158_fv_unc"]`=**20313500**, cell_idx]·cell_idx=冻结 9 格表序。
- **虚拟起点窗网格（三窗+持有期族）**：{6m=126, 12m=252, 24m=504} 交易日窗·起点=每交易日 p∈[120, n−w]（W1 同径日频起点·重叠窗如实披露：推断主责归 nulls/skill line 非窗计数）；每窗策略曲线收益 vs **同员 B&H 同窗收益**（逐格批自被动=REPO_CALENDAR_P2 面）；段=起点日 510300 MA200 政体（bear/bull/chop·政体未定义=na 桶）；n_eff_start_windows=三窗总计数·sample_sufficient=W1 口径（n_eff≥500 ∧ bear/bull/chop 各≥100）。
- **G1' v2（共享库禁手抄）**：`sg.g1_prime_v2(sharpe_full, returns_full, batch_cells=9, n_trades, n_entries, null_pool=批自 null 族池, passive_override=同员 B&H 全期 Sharpe)`——skill line N_eff=ledger 活头+9 数据驱动；被动=逐格批自（三员三历·REPO_CALENDAR_P2）。
- **DSR**：`sg.deflated_sharpe_ratio(returns_full, n_trials=本批 append 后活头)`——活锚头数据驱动（跨波不重置·W2 律同面）；禁 `dsr_from_stats` 充数。
- **G2 注册资格 v2（共享库）**：`sg.g2_registration_v2(g1_pass, dsr, pbo)`；**PBO 族面（跑前冻结）**：族=A158 量化门择时模块·**PBO 网格=每员 17 门已试配置全网格**（n=17≥8·完整自历矩阵零对齐损耗·Bailey-LdP CSCV 本义=全已试宇宙非仅存活者；判格承本员网格 PBO）；判格子网格（每员 2/4/3<8）按 W10 冻结法如实记 insufficient 披露行（非 G2 输入）。跨员判格集无完整公共历（对齐截断>50% 禁律）→ 批级单矩阵不立。
- 分段恒带：bear/bull/chop（510300 MA200+slope60·模板逐字）OOS 逐段年化（≥30 日段才计）。
- 账本：`sg.append_ledger("T-101-V4-A158-FULLVERDICT", 9, "t101_v4_a158_fv.json", evidence_cutoff="2026-09-28")`（finalize 时落·链式线性）。

## §4 判据【必填·跑前写死，禁看结果调线】

**FV-PASS（注册候选资格）= 四条合取（全量判决面）**：
1. **G1' v2 pass**（skill line+bootstrap CI 下界>0+交易门 entries_ok——共享库逐条）；
2. **DSR ≥ 0.95**（原始收益 deflated_sharpe_ratio·n_trials=append 后活头）；
3. **成本 ×2 压测**：OOS 超额（0.2% 往返）> 0；
4. **G2 eligible_v2**（G1∧DSR∧PBO≤0.25·共享库）。
- FV-PASS 格→**s4 intake 切片**（D6 绑定门对在册六员+存活者两两→STRATEGY_LIBRARY 注册+袖盘上岗另按 W10 §s4 律）；FV-FAIL 格=线关闭如实入 §7+attrition（禁换参重跑·同语法重跑禁令）；零 FV-PASS=合法判决照报不翻案。
- 多重检验税披露：N_wave=9 判格·E[FP]=0.05×9=**0.45**；N_eff 累计照 TRIAL_LABOR_LAW §4 跨波不重置（活头实读）。
- 描述条款恒带（非判线）：全期 maxdd≥−35% 地板·IS/OOS 反号·政体依赖性·entries 数。

## §5 跑前预测【必填·写死于跑前】

1. **G1' line 全灭预期**：批自 null 族池+活头≈344k → skill line 极值项≈σ_null×√(2·ln 344,040)≈4.45σ——W9 判例线 1.1937 处 243 格全灭；本批最高 full Sharpe（VSUMD30 预计≈0.80）大概率在线下→**G1' pass 0/9 预期**（588000 被动项最低=其线最松，为唯一可能例外格）。
2. **DSR 全灭预期**：n_trials≈344k → SR*≈4.5σ_sr（年化≈1.2+）；本批格 Sharpe 0.26-0.81 全在 SR* 下→DSR 0/9 预期。
3. **成本 ×2 压测分化**：高 entries 格（VSUMD30 73 次/VSUMD10 98 次类）×2 成本拖累≈entries×0.1% 追加≈年化 −1.5~-2.5%——高超额格（VSUMD30 +11.96%）仍>0 过压测；低超额格（510500|RSQR10 +0.36%/CNTN20 +1.09%）**预期压测翻负**。
4. **窗网格分段面**：588000 格=深熊回避型（2021-24 科技熊坐 out）→bear 起点窗 beat 率最高·bull 起点窗最低；510500|RSQR10 chop 段 −6.35%（上游实证）→chop 起点窗 beat 率低。
5. **PBO 17 门网格**：每员 17 配置中 14+ 为 KILL 格（负 Sharpe 垃圾配置占多数）→IS-best 常为幸存偏置产物→**PBO>0.25（G2 不可过）为主预期**；哪员网格 PBO≤0.25=该员门选择稳健的证据（如实双向披露）。

## §6 产物

- script：`scripts/t101_v4_a158_fv.py`（import 单源复用·fail-closed G-P1/G-ACCEPT/G-ANCHOR·hermetic selftest 子命令）；
- results：`results/t101_v4_a158_fv.json`（顶层 evidence_cutoff+science_gates.cutoff_meta+audit+cells 9+批自 null 池 coverage+PBO 双面+trials_ledger 块）+ `results/t101_v4_a158_fv.csv`；
- `results/gate_attrition.json` history 追加一行（judgment·cells_ledger_delta=9）；
- 本件 §7/§8 回填+轮报告回执+CODELY.md 行级追加。
- **consumer_plan（O-1820(3) 必填）**：① T-101 v4 臂表判决行（research/DECISION_CHAIN_BENCHMARKS.md §5 A158 行·本批=GATE-TIMING 升格步判决面）；② gate_attrition 损耗账；③ 若 FV-PASS>0 → s4 intake 切片（注册+袖盘）为指名消费面；④ 零 PASS → 「A158 择时用法全量判决关线」入 STRATEGY_LIBRARY 判负库+政体门臂转纯输入特征组合路线（r231 §4 预案）。

## §7 跑后实证【跑前必须为空——占位纪律：写数字即造假】

## §8 批后复盘【必填·s7-T】
