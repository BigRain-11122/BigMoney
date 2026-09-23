# research/SCIENCE_AUDIT_PREREG.md — science_audit.py 月度科学审计·判据预注册（先写死后首跑）

> 权威：research/BACKTEST_SCIENCE.md §7-M（O-20260923-2215）+ T-2026-09-23-02-P1 交付件 5/7。
> 纪律：**审计判据先写死后首跑（防审计器自放水）**——本件 §1-§6 在首场实跑前冻结；§7=首跑结果区，跑前必须为空（P-A §6 占位纪律同源）。
> 改审计判据 = 预注册 + 7 天否决窗（BACKTEST_SCIENCE §7 末行）。审计=查账层：**只报不裁、不阻断任何车道、CEO 仅收通知零动作**（O-2205 口径）。
> 节律：每月首轮 OS 轮执行（BACKTEST_SCIENCE §7-M）；首场（本件 §7）= 机制落地的基线建立跑，此后月度滚动。
> 扩展槽：本审计器设计为**检查注册表制**——每检=独立函数+冻结判据；后续新增检查（如 REGIME_GUARD 月检第 6 项·O-2315 T-05 车道）=新预注册追加，不动既有五检判据。

## §1 检一：null μ/σ 重算（滚动漂移）

- 数据源：science_gates.null_sharpes() 现算（采集器 v0.1 覆盖面=p2_calibration 随机族 120 值，覆盖缺口如实报）。
- 漂移基线：上一快照——优先取 results/science_audit.json 上一条 history 条目的 null 池块；无历史（首场）则取 results/science_gates_v2.json 的 null_pool_coverage。
- 冻结判据：
  - `mu_drift_flag`：|μ_now − μ_prev| > 0.25·σ_now
  - `sigma_drift_flag`：σ_prev>0 且 |σ_now − σ_prev|/σ_prev > 0.20
  - `pool_change`：n_now ≠ n_prev（信息项；null 池只能经采集器扩展或标定文件改动而变——**无代码变更说明的池变动=WARN**）
- 裁定：零旗=OK；任一旗=DRIFT（动作=报告披露；判线刷新由检五同轮执行）。

## §2 检二：锁盒越权扫描

- 扫描宇宙：results/ 顶层全部含 `trials_ledger` 的批件 JSON（现行 20 件，数据驱动枚举非写死）。
- 合法截断元数据键（任一即视为已声明）：`evidence_cutoff` / `history_end` / `panel_end` / `data_cutoff`。
- 冻结判据：
  - **VIOLATION**：非白名单批件（=O-2215 入库时刻 2026-09-23 22:30 之后冻结的批）且无任一合法键 → 判「锁盒元数据缺失」（有无越权读不可证=最重发现；实际截断与否须回溯其预注册与锚定门另行定性，本审计只报不裁）。
  - **VIOLATION**：声明的截断值晚于现行日线数据截止（data cutoff，读 results/update_status.json）→ 「不可能数据」=元数据造假或时钟错乱。
  - **OK-注记**：白名单批件缺键=存量豁免（v2 前时代产物，grandfathered）。
- 存量白名单（19 件，冻结；v2 前批件全量）：p1_screen / p2_calibration / p2_survivors / lowchurn_family / combined_exit / lfc_p1 / new_signal_p1 / g2_nsp1 / p3_portfolio / sleeve_p3 / ce_transfer / shortline_p2_synth / shortline_p4_batch1 / shortline_p4_batch2 / shortline_p4_batch2a / shortline_p4_queue / shortline_p4_folk / shortline_g2_folk / p5_random_entry。
- 新批入律：白名单永不追加；v2 后任何新批件必须带合法截断键（7/7 执行腿落地后由门禁脚本统一写入）。

## §3 检三：在册交易员 DSR 复检

- 宇宙：firm/traders/*.json 全部在册交易员（_template 除外，数据驱动枚举）。
- 复检数学（冻结）：**从 g25 verdict 件存储统计量重推**——不重跑引擎（月审轻量；引擎级复算=g25_retro 职责）。公式与 science_gates.deflated_sharpe_ratio 同源：
  - SR 日频 = sr_annualized/√252；σ_SR 用 verdict 存储值；V[SR_null] = σ_SR²（g25 实跑同约定：var_null 默认项）
  - SR*(N) = σ_SR·((1−γ)·Z(1−1/N) + γ·Z(1−1/(N·e)))，N=现行账本链头（数据驱动）
  - DSR_now = Φ((SR − SR*)/σ_SR)
  - 单一源=science_gates.dsr_from_stats()（本批新增加性函数，审计与未来 g25 复用，禁各处手抄公式）
- 冻结判据：
  - **STALE**：无 results/g25/<ID>.json verdict 件 → 「晋升裁定前必须先跑 g25」（hr 前置会拦，此处披露）。
  - `n_trials`（verdict 记录时链头）≠ 现行链头 → 正常漂移（账本只增），DSR_now 重推值**只降不升**（N 单调）如实报。
  - `dsr_gate_cross`：DSR_now ≥ 0.95 = 过注册门；< 0.95 = 不过（预期全员不过=R28/R29 三检口径，如实报不翻案）。
  - σ_SR 一致性：由存储 skew/kurt/T 重算 σ_SR，与存储值相对偏差 >1e-3 → verdict 件损坏 WARN。
- 输入为 g25 四舍五入存储值 → 重推 DSR 与引擎级原值容差 ±0.005（如实披露，复检精度不构成裁定依据，裁定权重=前向证据）。
- CI/PBO 腿：月审只报 verdict 件存储值与新鲜度，不重算（重算需引擎复现=g25 职责）。

## §4 检四：门禁链损耗账汇总

- 对象：results/gate_attrition.json（BACKTEST_SCIENCE §7-T：批回执必含复盘节，损耗账数据驱动落此件）。
- 冻结判据：文件不存在 → `MISSING`（诚实发现，非违规：尚无批件按 §7-T 新纪律回填机器可读损耗账；首个带损耗账节的批回执创建之）。存在 → 汇总（条目数/最近批/G1'→G2→注册漏斗计数，schema 以首个落件为准如实读取）。

## §5 检五：判线 v2 数值重算

- 现算：science_gates.skill_line_v2(batch_cells=0)（现行账本链头上的当值线）+ recorded_lines() 历史复现常数管辖注记。
- 冻结判据：
  - `line_drift_flag`：与上一快照（同 §1 基线规则）之差 |Δline| > 0.05 → 判线漂移披露（线只随账本头/null 池/被动基线变动）。
  - 自洽门：line == max(passive_term, null_term)（公式完整性）。
  - 链头注记：账本链头文件与 total 数据驱动报告（防账本断裂/双头）。

## §6 输出与节律

- 落件：results/science_audit.json = **滚动台账**（current=本轮五检全量块；history=历史条目追加，永不改写既往条目=进化台账载体）；轮报告+CODELY 行级追加=CEO 通知面。
- 退出码：0=审计完成（含发现项——审计是查账不阻断）；1=审计器自身故障（异常/自洽门红）。**审计发现永不阻断任何车道。**
- 首场后月度节律：每月首轮 OS 轮 S6 链后执行（iteration_prompt 接线随 7/7 执行腿一并落地；本预注册即判据冻结，接线属执行腿非判据）。

## §7 首场实跑结果（跑前必须为空——写数字即造假）

**首跑**：2026-09-24 01:0x（bm-a R30，判据冻结 aeb0164 → 实现 9f15bca 之后）·exit 0（审计完成含发现项）·账本链头 2727（p5b_new_traders.json）·漂移基线=science_gates_v2.json（R24 快照，首场无历史）。产物=results/science_audit.json（history[0]）。selftest 19/19 + science_gates 23/23 先行全绿。

| 检 | 裁定 | 读数 |
|---|---|---|
| C1 null μ/σ | **OK**（首场基线） | n=120 · μ=−0.0332 · σ=0.2429 ·零漂移旗（与 R24 快照逐位同=池静态，采集器未扩） |
| C2 锁盒扫描 | **VIOLATIONS ×1** | p5b_new_traders.json：v2 后批件缺截断元数据键（机读不可证）。**定性补注**：实际截断已由其预注册 P5B_NEW_TRADERS.md 与 g25 verdict inputs（returns_window 止 2026-09-22）旁证=元数据缺口非实际越权读；修复路径=7/7 执行腿（门禁脚本统一写 evidence_cutoff 字段），存量不回改。另 19 件白名单=11 缺键豁免 + 8 件带合法键全 OK（含 ce_transfer 的 history_end 键）。 |
| C3 在册 DSR 复检 | **OK** | 6/6 verdict 件新鲜（n_stale=0）·σ_SR 一致性 6/6 过·现行链头重推 DSR 与记录值差 ≤3.2e-5（远小于 ±0.005 容差）·**dsr_gate_cross=0/6**（VOLATILITY 0.3486 最高，全员 <<0.95，与 R28/R29 三检 FAIL 一致·N 单调只降不升如实应验） |
| C4 损耗账 | **MISSING**（诚实发现） | results/gate_attrition.json 尚无批件回填（§7-T 机器可读损耗账新纪律，首个带损耗账节的批回执创建之；非违规） |
| C5 判线 v2 | **OK** | 线=0.933 @N_eff 2727 ·公式自洽门过·零漂移旗（对 R24 基线 0.933）·passive_term 0.4792 < null_term 0.933=null 校正主导 |

**发现项处置**（只报不阻断）：①p5b 元数据缺口→7/7 执行腿统一修复（新批必带 evidence_cutoff）；②损耗账空→待首个批回执按 §7-T 回填。两项均已挂 T-02 剩余 6/7、7/7 的验收清单。

## §8 判据变更协议

改任何一检的判据/阈值/白名单 = 本件修订 + 新预注册 + 7 天否决窗（BACKTEST_SCIENCE §7 末行原文）。白名单只减不增。

## §9 检六：行情防线完整性（REGIME_GUARD 月检 · 2026-09-24 追加冻结 · 跑前写死）

> 权威链：firm/risk/REGIME_GUARD.md ④ 治理接线（O-2315 入法）+ T-2026-09-23-05-P1 交付件 (5)。本节=检六判据冻结，先于检六首场实跑；§8 变更协议同等适用。既有五检判据零改动。

- 数据面：results/regime_state.json（scripts/market_regime.py 每日 shadow 探测产物）+ scripts/market_regime.py 模块本体 + results/paper/*_paper.json + data/daily/510300.csv（交易日历独立源，零网络）。
- 冻结判据（裁定词汇=OK / DRIFT / GAP / STALE / INCONSISTENT / VIOLATION / MISSING，任一发现如实报、只报不阻断）：
  - **(a) 阈值指纹**：`scripts.market_regime.threshold_fingerprint()`（THRESHOLDS 典范字典 sha256）≠ 本节冻结值 → `DRIFT`（法值被改而未走预注册）。冻结值（2026-09-24 由现行模块算出后写死于此）：
    `368a8d9d2f65669b4ceddf9db6a3efd4661762a4ae6ea3f1fbcfa81977739601`
    覆盖面注记：指纹=声明的典范字典（v1 矩阵映射/急跌三档/恐慌/波动分位/广度两档/防抖 2 绿日/事件日历/窗口常数+v2 重映射留档）；字典未载而行为面漂改由 market_regime._selftest 边界用例守（各自检项互为纵深）。
  - **(b) 状态序列连续性**（读 regime_state.json.history，逐对相邻条目）：
    - 任一 state ∉ {GREEN,YELLOW,ORANGE,RED} → `INCONSISTENT`；
    - asof 非严格递增/重复 → `INCONSISTENT`；
    - 相邻两日非 510300 交易日历连续对（跳过非交易日）→ `GAP`（机器停机日=如实发现非隐瞒）；
    - 状态变更日必有 transitions 条目 {from=前日 state, to=当日 state, asof=当日} 且 days_in_state 当日=1、同态日=前日+1 → 违者 `INCONSISTENT`；
    - history 末条 asof ≠ 510300 独立读数的最后一根 bar 日期 → `STALE`（最新 bar 已落而探测未跑）。
  - **(c) 响应一致性**：
    - state 件 mode=='shadow'（现行纪元）时：任一 results/paper/*_paper.json 的 regime_guard 块 mode≠'shadow' → `VIOLATION`（越权干预）；块 state 与 history 该 asof 读数不符 → `VIOLATION`；**块缺席=诚实注记非发现**（T-05 part5 2026-09-24 引入，各员文件随下一次 paper 刷新携带；n_with_block/n_paper 如实计数）；
    - mode=='enforce'（未来·须校准过门+GM 批+法文件修订三前置）：橙/红日 paper 窗口新开仓须为零——**该腿在 enforce 接线（独立署名单）落地前不实现**，届时=新预注册追加判据；审计器在 mode=='enforce' 且接线缺失时报 `enforce_response_check:not_wired` 诚实注记。
  - state 件不存在（探测从未跑过）→ `MISSING`（诚实基线，非违规）。
- 节律：随月度审计常跑（检六并入五检后的六检制）；发现项永不阻断、CEO 仅收通知（O-2205 口径不变）。
