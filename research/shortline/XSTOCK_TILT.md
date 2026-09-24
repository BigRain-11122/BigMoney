# XSTOCK_TILT — XSTOCK 合成幸存者策略转化批（B 层·股票池·低频倾斜）预注册

> 跑前冻结（2026-09-25 bm-b round 151）。模板=research/PREREG_TEMPLATE.md；权威=BACKTEST_SCIENCE.md v2 判据 + BACKTEST_PLAN 三铁律；判线=science_gates 共享库活读（O-2250 单源律，禁手抄数字）。
> 认领：MSG-20260925-0625-ALL-xstock-tilt-claim.md（F-04 先于本件 commit 已推送 c5d0cd9d）。
> 上游预授权：XSTOCK_SYNTH.md §8（股票域跨库合成第 2 次试验 PASS：primary IS IC 0.1078/IR 1.03、OOS 留存 0.895；h20 条件报告列 0.1245/1.158 snooping_discount=true）——「策略级转化须另开预注册（G1'v2 共享库门+股票域成本模型 P4_BATCH2 先例，含 B 层宇宙 3517 过滤与 T+1/成本实盘级压测），转化批前不得入册」=本件。
> 墙先验（诚实置顶）：P4_BATCH2 0/19 + P4_EXT_TILT 0/5=「26bp+T+1 摩擦墙在 B 层对所有长多倾斜族成立」两条前判定案；本批科学问题=**素材刻度 3-4×（复合 IC 0.108-0.125 vs gdhs 0.03-0.04）+h20 半频减摩擦能否翻墙**。判负即收线，复活条款见 §8。

## §0 批件身份【跑前】

- 批名/批号：`XSTOCK_TILT`（dept:研究·策略部，bm-b 车道）。
- **批内格数 N_eff=44**：主格 4（h20_top5/h20_top10/h10_top5/h10_top10）+ 随机 null 40（h20 频 20 + h10 频 20，全部 K=10 口径）。被动基线**不重跑**——`stock_b_layer` 池已在 science_gates.passive_baseline 注册（P4_EXT_TILT 产物活读），计入判线不计入新格。
- 结构：本轮=纯 spec 冻结（P4_EXT_TILT r67 先例）；实现+探针+跑数=后续轮（探针先行单格计时；>5min 算力腿一律 runnable_pool 入池+checkpoint，O-2100 执行/算力分离律，禁轮内内联代跑）。批报告必带 audit 段（compute_audit CLEAN 否则不入账）。
- 算力预算：成员格重建 4 员×全史面板（xstock_synth 构建器，估 10-25min）+ 复合投影 join + 44 引擎格（P4_EXT_TILT 47 格同量级，估 30-90min 墙钟）→ **后台化+跨轮 checkpoint 强制**（R41 律）；worker ≤ floor(16×0.8)=12（O-1738 bm-b 上限）。

## §1 α 机制段【D6 四选一】

- [x] **行为偏差**（XSTOCK_SYNTH §1 机制段逐字继承）：注意力稀缺×短期反转×过度反应修正的跨库去冗余组合——LHB 上榜=散户火力聚焦→反转（count_20 |IR| 0.84=全项目最强单因子证据）；GTJA 081/070 簇=短期反转 DNA；由追涨上榜股的散户与过早交筹的处置效应散户付出代价。合成层证据已过三线（§8 PASS）；本批问的是**该行为偏差在 26bp 股票回合+T+1 摩擦下扣除成本后是否仍有净残余**。
- **同族相关性准入检查【必填·实现轮先于跑数执行】**：4 主格 vs 在册 6 交易员（VOLATILITY/COMPOSITE-CE-01/02/ENGULF/NEEDLE/DROUGHT）日收益序列 max|corr| 逐对列出（ew6_portfolio member_run 复用，EXT_TILT 同法）；批内 4 格=同族双频双 K 格（家族内部相关由 G2 PBO 治理，非 D6 拒收项）。预期 0.02-0.10（EXT_TILT 0.026-0.056 同域参照：股票池 vs core48 ETF）；**max|corr| ≥ 0.7 → 拒收该格**。

## §2 数据与面板【跑前探针事实】

- **面板**：P4_BATCH2 r38-a 缓存面板（T=2850×N=5212×7 列 float32，2015-01-01→**evidence_cutoff=2026-09-22**，gitignored 可再生）；688/689 volume/amount 双归一坑（r49）已内建——消费 amount 列按缓存口径（EXT_TILT §2 同款声明）。
- **宇宙（冻结）**：`b_layer ok_static` 3517（O-1820 件3b）∩ **P4_BATCH2.md §2 动态资格条款逐字**（20 日均额≥5000 万、上市≥20 bars、价格≥1 元、末 bar≤250td、ST 滚动段剔除）+ EXT_TILT §2.5 修订门逐字（**逐日资格中位 ≥1000** 哨兵门 + **首再平衡日因子可得数 ≥500**）。r68 探针同公式中位实况 1524——本批探针轮复测记入 JSON（漂移>2σ 上报不跑）。
- **IS/OOS 切分**：IS ≤2024-12-31（面板起点 2015-01-01 起），OOS 2025-01-01→cutoff（XSTOCK_SYNTH §3 同锚）。
- **数据完备门（不过禁跑）**：①成员格复现门——4 员在原生合成网格重建后与 xstock_synth 冻结构造逐位一致（构建器 import 零重写=构造性保证，实现轮断言 min_valid/era 门/lag 与合成件常量逐字相等）；②宇宙门（上文）；③引擎 smoke 20/20 + fill_guard 自检（P4_BATCH2 §3.1 验收门逐字）。

## §3 方法学【冻结】

- **复合信号（零重写=值投影）**：4 成员格用 xstock_synth 冻结构建器在**原生 p1c 缓存网格**（全 5222 列，era 门内 0-fill、LHB +1 披露滞后、逐日横截面 z、等权、min_valid=3、方向定向=构建器内嵌）重建 → 复合值按 (date, code) **join 投影**到 batch2 策略面板（值查找非重建：两网格同源 bars，join 键双射；两侧 code 集差（5222 vs 5212）逐码披露）。复合[t]=t 收盘全知（GTJA/WQ panel[t]、LHB panel[t+1] 即 t-1 盘后披露）→ 入场 t+1 开盘（T+1）零未来数据；实现轮过 truncate-and-compare 因果自检。
- **格子结构（EXT_TILT 语义逐字复用）**：固定频再平衡（h20=每 20 交易日、h10=每 10 交易日，`range(W-1, T, W)`）日对合格内 **top-K 复合值**（降序，高=好，tie→低代码优先）选出名单；entry pulse=再平衡日新入选，exit pulse=落选日（frames_from_selections 同构造）；引擎退出机（loss 8d 强平/分层止盈/−8% 硬停）+ T+1 + fill_guard（涨跌停拒单/顺延）+ 26bp 股票回合成本（P4_BATCH2 §3.2 逐字）全激活。**本批不加缓冲带/波段持有结构**——最小改动律；若判负，「不同持有结构」（rank-band 滞回）=§8 复活条款另开预注册，本批不预支。
- **K 口径**：主格 K∈{5,10}（引擎 10% 仓位特性：top5=50% 仓、top10=100% 仓，全格含 null 平等待遇如实记）；null 全部 K=10。
- **null（K=40）**：h20 频 20 条（seed=**57_000**+i，i<20）+ h10 频 20 条（seed=**57_100**+i，i<20）——合格宇宙内同再平衡日**均匀无放回随机抽 K=10**（「选择无信息」零假设，EXT_TILT _null_selection 同构造）；种子族已登记 SEED_REGISTRY（xstock_tilt_h20/xstock_tilt_h10，带 57_000..57_019/57_100..57_119 rg 扫描空，2026-09-25 06:2x）。
- **被动基线**：不重跑；`pool="stock_b_layer"` 活读注册池（P4_EXT_TILT 产物 monthly EW Sharpe 0.4606/quarterly 0.454 → strict-max 口径）。
- **账本**：`science_gates.append_ledger("XSTOCK_TILT", 44, "<results JSON>", evidence_cutoff="2026-09-22")`（dict schema 唯一，prev 活读禁手抄）。

## §4 判据【跑前写死，禁看结果调线】

- **G1' v2 = `science_gates.g1_prime_v2(sharpe_full, returns, batch_cells=44, pool="stock_b_layer", null_pool=<本批 40 null 全体>, n_trades, n_entries)`**：全期 Sharpe > skill_line_v2（数据驱动=max(被动+0.10, μ_null+σ_null·√(2·ln 44))，own-null 池校准）**且** 平稳 bootstrap CI 下界 > 0 **且** F6 双口径 entries≥30；逐列披露 skill_line/bootstrap_ci/trade_gate 全输入。
- **G2 注册资格（仅当任一主格 G1' v2 过线）= `g2_registration_v2(g1_pass, dsr, pbo)`**：DSR≥0.95（`deflated_sharpe_ratio` 原始收益，禁 dsr_from_stats 充数）+ 同批 4 主格家族 PBO≤0.25（screening/pbo.py CSCV 8 块；4 格家族 J19 先例）。缺输入=诚实拒收。
- **描述性条款（批级披露，不替代 v2 门）**：年化>0、OOS 双正、回撤≥−35%、无崩年、成本压测 ×2≈52bp/×3≈78bp 逐年稳定（信息列）。
- **判负处置**：0/4 过线=**XSTOCK 策略转化线收线**（合成线素材证据维持因子级用法不收回；EXT_TILT「因子级 IC≠策略级可转化」定案加第三证）；跑后禁调门槛禁重跑（工程 bug 修复重跑须双跑留痕 R9/SLEEVE_P3 先例）。
- **成本口径声明**：V1 型股票日程 26bp（P4_BATCH2 §3.2 逐字；股票域连续口径，EXT_TILT/BATCH2 同锚）；×2/×3=描述性压测列。

## §5 跑前预测【写死于跑前，跑后 §7 对账】

1. **主格全期 Sharpe 带 [−0.30, +0.55]，点估 h20_top10 ≈ +0.1~+0.25**：复合 IC 0.108-0.125=gdhs 素材 3-4×+h20 半频（~12 次/年×名单更替 50-80%×26bp ≈ 1.6-2.5%/年成本 drag）；但长多倾斜只收 IC 尾差一小半（EXT_TILT 定案 a），Sharpe 0.56 线远高于点估。
2. **G1' v2 过线主格 0-1（点估 0；整批 PASS 概率 15-25%）**：skill line ≥0.5606（passive+0.10 主导项压倒 own-null 项 μ~−0.14+σ~0.15×√(2·ln 44)≈0.31）；两前批 0/19+0/5 墙先验。
3. **h20 格 ≥ 同 K 的 h10 格**（IC 0.1245>0.1078+成本减半）——**snooping 折价披露**：h20 数字系合成批条件报告列（snooping_discount=true），本预测受窥视污染如实记；h10 格若反超=折价教训实录。
4. **null 读数**：h20/h10 频随机倾斜 μ ≈ −0.14±0.05（EXT_TILT 20 日频同域）、p95 ∈ [0.10, 0.16]；两频 null μ 差 <0.05（同摩擦不同频）。
5. **宇宙门**：eligible 中位 ∈[1200, 1900]（r68 同公式 1524 参照）；首再平衡复合值可得数 ≈ 当日 eligible 数（GTJA dense+LHB era 内 0-fill→min_valid=3 全日可出）≥500 门宽过；2015 年初首再平衡日最小（上市家数少）——若探针实测 <500 即 §2.5 门红=批拒跑如实上报。
6. **极端日先验（硬界三件套 c）**：窗内极端段=2015-06 股灾（千股停牌→fill_guard 卖出顺延重击+选样稀薄+反转格重仓跌深股连吃跌停）、2016-01 熔断（流动性枯竭）、2018-10 政策底 V 反、2024-09-24 起 9 日暴力反弹（反转 DNA 踏空+exit 咬合）、2025+ OOS（regime ORANGE breadth 弱）。单日组合极端 |r| 可达 ±4-6%（top5 20% 仓×板 ±10%）；**max 回撤带 [−28%, −48%]**（EXT_TILT −33.3% 参照，反转 DNA 2015-06 段更险）；−35% 描述条款有真实击穿风险=预测其可能红。
7. **D6**：4 主格 vs 在册 6 员 max|corr| ∈ [0.02, 0.10]（EXT_TILT 0.026-0.056 同域），<0.7 全过预期。

## §6 产物

`scripts/xstock_tilt.py`（selftest/gates/probe/run/status 子命令；复用 p4_batch2_screen 面板+fill_guard+CostPatch+exec、xstock_synth 成员构建器+复合构造、p4_ext_tilt 排程/脉冲/own-null/D6 语义，禁重写）+ `results/shortline_xstock_tilt.json`（顶层 evidence_cutoff=2026-09-22=science_gates.cutoff_meta）+ `research/shortline/xstock_tilt_results.csv` + `results/xstock_tilt_runs.jsonl`（checkpoint）+ 本文件 §7 回填 + gate_attrition.json 追加行 + STRATEGY_LIBRARY §九 行收线标注。

## §7 跑后实证【跑前必须为空——占位纪律：写数字即造假】

（2026-09-25 06:36 跑后回填 · bm-b r153 · 52 引擎格全跑 348s/8 workers · 账本 60784→60828 · evidence_cutoff=2026-09-22）

**判定：0/4 过线 → XSTOCK 策略转化线收线**（§4 判负处置；复活=§8 条款另开预注册，同素材重跑禁）。

- **skill_line_v2=0.6238**（被动 stock_b_layer 0.4606+0.10 主导项压倒 own-null 项）；四格 line_ok 全 F、bootstrap CI 下界全不正；F6 双口径全过（entries 709/1416/1402/2803、trades 1179/2313/2185/4345）。
- 主格全期：h20_top5 S **0.1804**（OOS −0.0490·ann +1.13%·mdd −18.13%）／h20_top10 S **0.0606**（OOS −0.4409·ann −0.21%·mdd −36.73%）／h10_top5 S **0.2722**（OOS +0.0713·ann +2.13%·mdd −24.07%）／h10_top10 S **0.2387**（OOS +0.0900·ann +2.58%·mdd −38.22%）。描述条款：两格 mdd 破 −35%。
- **成本压测（信息列）**：×2=52bp 四格全转负（S −0.2018/−0.4333/−0.3482/−0.5067，worst year −17.4%~−47.2%）；×3=78bp 深负（S −0.5419~−0.9471）。26bp 基准已不过线，成本面无翻案空间。
- **null 池**：μ −0.1568/σ 0.1663/p95 0.0949（h20 μ −0.1141 vs h10 μ −0.1995）；主格全胜 own-null（best 0.2722 vs p95 0.0949）=复合选择技能真实存在，但**相对技能≠绝对判线**。
- **D6**（28 员面=在册 6+PROSPECT 22，EXT_TILT 冻结法）：max|corr| 0.3125-0.4642（vs PROS-DOJI-CE-01/PROS-DOJI-01 系，h10_top10 全对面里 RSRS-CE 0.4433/HAM 0.386/VOB-CE 0.367 亦高）——远超预测带 [0.02,0.10]：复合内嵌 GTJA 反转簇 DNA 与 DOJI 系结构相关；全 <0.7 无拒收，相关性面如实披露。
- **家族 PBO=0.7286 fail**（CSCV 8 块·4 格家族）——G2 前置证伪面（即便 G1 过线，家族排名时序亦不稳）。
- 产物：`results/shortline_xstock_tilt.json` + `research/shortline/xstock_tilt_results.csv`（44 行）+ gate_attrition XSTOCK_TILT 行（44 格 0 幸存）+ checkpoint `results/xstock_tilt_runs.jsonl`。
- **墙判定三批定谳**：P4_BATCH2 0/19 + P4_EXT_TILT 0/5 + XSTOCK_TILT 0/4 =「26bp+T+1 摩擦墙对 B 层长多倾斜族成立，且 3-4× 素材刻度（复合 IC 0.108-0.125）+h20 半频不翻墙」；素材证据维持因子级用法不收回（LHB/GTJA 因子池面照旧）。

## §8 批后复盘【必填·s7-T·跑后回填】

- **§5 预测对账（七条）**：①主格 Sharpe 带 [−0.30,+0.55]：实测 0.0606-0.2722 全带内**中**；点估 h20_top10 ≈+0.1~+0.25：实测 0.0606 落点带下沿外**近失**。②过线 0-1（点估 0）：实测 0 **中**（批 PASS 15-25% 未兑现）。③h20 ≥ 同 K h10：**未中**——h10 两格反超（0.2722>0.1804/0.2387>0.0606）；§5 预录的「h20 条件报告列 snooping 折价」教训实证落地（折价列不可作为频率选择依据）。④null μ −0.14±0.05：实测 −0.1568 **中**；p95 [0.10,0.16]：实测 0.0949 略低于下沿近失；两频 μ 差 <0.05：实测 0.0854 **未中**（h10 随机倾斜摩擦更重）。⑤宇宙门：探针中位 1524/首效 751 **中**（r152 全绿）。⑥mdd [−28%,−48%]：h20_top5 −18% 轻于带外，两格破 −35% 兑现「真实击穿风险」**半中**。⑦D6 [0.02,0.10]：实测 0.3125-0.4642**大幅未中**——同域相关性先验须按 DNA 簇（反转/波动族）估算而非「资产面差异」估算，本条与 ③ 同根（复合的 h10 半衰期更短、反转暴露更纯）。
- **判线 v2 当批读数**：skill_line_v2 0.6238（被动+0.10 主导，own-null 项 −0.1568+0.1663×√(2ln44)≈0.286 不 binding）；best 格 h10_top5 0.2722 距线 −0.35。
- **门禁链损耗账**：gate_attrition XSTOCK_TILT 行（cells_run 44→survivors 0）；账本 60828。
- **复活条款（冻结·跑前原文逐字）**：若 0/4 判负——①「不同持有结构」（rank-band 滞回缓冲/事件驱动持有）=另开预注册；②做空腿/更低成本载体=P1 署名门；③同素材重跑=禁（跑后禁调门槛）。**0/4 已兑现 → 本条款生效**。
- **收线处置**：XSTOCK 策略转化线收线；STRATEGY_LIBRARY §九 已翻收线格式；无新员注册（0/4）→ SIGNAL_BUILDERS/live.paper 接线零动作。

—— 2026-09-25 06:2x 冻结 · bm-b r151
