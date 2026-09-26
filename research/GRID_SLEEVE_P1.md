# GRID_SLEEVE_P1 预注册（CN 网格引擎 sleeve·交易管理解锁 unlock-4）· T-2026-09-26-78 s5a · O-20260926-0958

> 本件按 `research/PREREG_TEMPLATE.md` 起草，跑前 commit 冻结；跑后只回填 §7/§8，禁改判据禁重跑。
> 纪律锚（O-0958 ③c/③d）：网格=**独立 sleeve+独立判决面**（grid capture rate / chop-vs-trend 分段 / 趋势中 whipsaw 成本），不触 house engine 冻结面（engine/grid_sleeve.py=新增独立模块，backtester/exit_rules 零改动）；五步律=设计(本件)→冻结→跑数→判决→纸面接线（s5b 起）。
> 反重复声明：与 `research/GRID_P1.md`（A 层网格收割**因子**批，已跑=诚实负 0 生存者、收线禁翻案）不同面——本批=**交易机械**面（单 ETF 价格网格引擎），GRID_P1 的诚实负作先验引用（§5-2），不重建其因子面。

## §0 批件身份

- 批名 / 批号：**GRID-SLEEVE-P1**（批内格数 N_eff＝5 instrument cells + 50 nulls + 5 passive ＝ **60** 计 N_eff；x2 压测面不入 N_eff，EXIT_OVERLAY 先例）；
- 认领：任务板 `fleet/tasks/T-2026-09-26-78-P1.json`（bm-b r240 认领 CEO 即时票；本件=s5a 设计+冻结；s5b=runner 跑数判决；s5c=GRID-* 纸面接线）；
- 部门归属：dept:工程（网格引擎机械）+ 策略部（sleeve 设计·冻结律内）+ 组合与资金部（独立判决面）联合；
- 算力预算：5 cells×~1630 bars 单遍模拟 + 50 nulls 串行预计 <5 分钟，inline 合法（O-2100 阈下）；批报告必带 audit 段。

## §1 α 机制段【D6】

- [x] **行为偏差**：锚定效应的机械化收割——平静区间品种内价格往返穿越等距网格位，网格在格位低吸高抛一格一单位＝向「区间内追涨杀跌的往返流量」提供流动性并收割其错位成本（CN 网格原典「网格是震荡市武器」；与 GRID_P1 §1 同源机制、不同实施面：因子批=池内选员收割，本批=单品种价格机械）。
- [ ] 风险溢价 / [ ] 结构性 / [ ] 微观结构。

**同族相关性准入检查【必填·D6】**：每 cell 日收益序列与在册 6 员（VOLATILITY/COMPOSITE×2/ENGULF/NEEDLE/DROUGHT）+ 同批全部 cells 的 `max|corr|` 由 runner 批内计算（sleeve-tag 先例）；**`max|corr| ≥ 0.7` → 拒收**（不入 GRID 纸面候选，诚实披露数值）。GRID_P1 实测其网格因子面 max 0.24–0.33（argmax=VOLATILITY-CE-01）——本批机械面预期同带（低相关性由「单品种区间持有 vs 池内趋势轮动」的构造差异保证，预测见 §5-1）。

## §2 数据与面板【跑前探针事实】

- 宇宙/池：**冻结 6 只**（资产类覆盖规则选样，零业绩窥探）：510300（宽基沪深300）/ 510500（宽基中证500）/ 512880（证券行业）/ 159915（创业板 20cm）/ 518880（黄金）/ 511010（国债）——CN 网格民间原典的震荡面谱；数据=仓内 `data/daily/*.csv` 全史（2020-01-02 起 ~1630 bars），**零新数据源**；
- **基金事件守卫（冻结·r239 坑律）**：单日 `|r1| > 10.5%`（10cm 品种；159915 按 20cm 用 20.5%）**且**当日宇宙中位 `|r1| < 3%` ⇒ 品种隔离（不入 cells，诚实披露）。**跑前探针实勘**：510500 2022-08-29 `-12.7%` vs 当日宇宙中位 `|r1|=0.72%`（n=47，p90=2.03%）=基金事件实锤 ⇒ 510500 守卫隔离；512480/159995（-48%~-50% 级，r239 已实勘）不在冻结选样内；159915 2024-09-30/10-08 ±20% 为 20cm 真市极限非事件（≤20.5% 阈不触发）。**活 cells=5**：510300/159915/512880/518880/511010；
- 窗口与 **evidence_cutoff（前向锁盒 D2）**：面板全史截断到 runner 读取日最新完整 bar（惯例 cutoff=`2026-09-24`，smoke freshness 同源）；cutoff 后新 bar 锁定不回流本批；结果 JSON 顶层必带 `science_gates.cutoff_meta(cutoff)`；
- 数据完备门（不过门禁跑批）：`live.paper.self_test_patches()` PASS＋活 cells 5/5 OHLCV 可读＋守卫披露面在产物 JSON 内。

## §3 方法学【冻结 v1】

- **网格引擎 v1（`engine/grid_sleeve.py`，本轮新增独立模块）**：
  - 带定义：`band_win=250` 交易日 trailing 窗 `[t−250, t−1]` 收盘 `[min, max]`——**不含当日收盘**（当日收盘对照昨日既成带；带离场「收盘<带下沿」因含当日的滚动 min 结构性不可达=死码，故带窗排除当日，因果性与逐日重算保持）；warmup（<250 bars）=空仓不交易；
  - 网格距：等距 `n_grids=10` 格，`level_k = lo + k*(hi-lo)/10`；
  - 每格仓位：`unit_cash = NAV_0 / n_grids`（初始 ¥1,000,000 镜 AGGR 惯例）；收盘 t 跌穿 `level_k`（前收≥该位>今收）⇒ t+1 开盘以 `unit_cash` 买入一格；
  - 卖出：每手（FIFO lot 记 buy_level）于收盘 t 升穿 `buy_level + 一格距` ⇒ t+1 开盘整手卖出（一格收割）；
  - **带离场**：收盘 t < `band_lo` ⇒ t+1 开盘**清仓全部**（whipsaw 成本诚实入账），空仓等待；收盘回到 `band_lo` 上方 ⇒ 重新武装；
  - 上沿外：全部售罄后不追（经典纪律）；
  - T+1 合规：信号恒 close t、成交恒 open t+1；lot 最早卖出=买入后次日起（构造性满足）；
  - 成本：**V1 legacy 13bp/边** + `CostPatch(2.0)` x2 压测面（GRID_P1 同构）；现金零息；分数股允许（house 权重面惯例，披露=实盘 100 股整数 lot 的简化）；
  - 已知发散（披露）：ETF 分红（-1%~-3% 级小跳）不入 10.5% 守卫面——带宽 250 日窗内自然吸收、lot 盈亏按真实价记账=诚实 marks。
- null 对照：**K=50 布局敏感 null**（活 5 品种各 10）＝同引擎、带宽随机相位偏移 `uniform(-1,+1) 格距`（seed 基=**62_500**，跑前登记 `science_gates.SEED_REGISTRY['grid_sleeve_p1']`）——检验「布位本身是否有信息」（随机布位同优=带宽定义无增益）；+ passive 5 面＝各自 buy-hold（一致性 info）；
- 账本：`science_gates.append_ledger("GRID-SLEEVE-P1", batch_trials=实测, file_name="results/grid_sleeve_p1.json", evidence_cutoff=...)`（dict schema 唯一，禁手抄 prev）。

## §4 判据【跑前写死】

- **G1' v2 = `science_gates.g1_prime_v2(sharpe_full, returns, batch_cells, n_trades, n_entries)`**（共享库零手抄判线）：全期 Sharpe > skill_line_v2（数据驱动=max(passive+0.10, μ_null+σ_null·√(2·ln N_eff))）**且**平稳 bootstrap CI 下界>0 **且** `n_round_trips ≥ 30`（F6 双口径，round trips=完整收割回合）；批报告逐列披露 skill_line/bootstrap_ci/trade_gate 全输入；
- **GATE-A（网格专家主张·机械面专属门）**：chop 窗累计网格收益 > 同窗 passive 收益（chop 窗定义=§5-4 分段器；网格的钱主张=震荡收割，趋势面只作披露不作门）；x2 压测面复评 GATE-A＝描述性披露（稳定性面）；
- 描述条款（批级披露不替代门）：年化>0、回撤≥−35%、趋势上窗机会差额/趋势下窗 whipsaw 成本/格捕获率（Σ lot 盈亏 / NAV_0）逐段披露；
- **生存者=过 G1'v2 且 GATE-A 的 cell** ⇒ GRID-* 纸面候选（s5c 接线）；**判决 FAIL ≠ 机械废弃**：GRID 纸面家族按 CEO 令 O-0958「GRID accounts paper-wired」以**实验观察账户**接线（AGGR-MOM 复活注册败者先例），风险预算字段逐账户申报，独立车道 `results/grid_paper/` 不入 t35/scorecard CEO 面；科学主张面（震荡收割优越性）按数据判，败者照报。

## §5 跑前预测【写死于跑前】

1. **相关性**：与在册 6 员 max|corr| 落 0.15–0.45 带（GRID_P1 因子面实测 0.24–0.33 同带先验），≥0.7 拒收概率低；同批 cells 间（国债 vs 创业板）低相关；
2. **量级与方向**：行业/黄金（512880/518880）chop 收割小幅为正；159915 受 2024-09-24 趋势上窗大额机会差额拖累、全期 Sharpe 难过线；511010 带宽过窄（年化 σ ~1%）格距≈成本 2.6×(13bp×2) ⇒ 边际化甚至为负；**预期生存者 ≤2/5，诚实负为主基调**（GRID_P1 因子面诚实负同向先验）；
3. **门槛读数**：skill_line_v2 近批带 1.10–1.46；网格单品种全期 Sharpe 预测 0.2–1.2，多数 cell line_ok=False；
4. **分段先验**：2020-2024 A 股含 2021 核心资产下坡/2022 双杀/2024-02 微盘崩/2024-09-24 政策脉冲（趋势窗）/2025-04-07 关税跳空——chop 窗在 512880/518880 内占比预计 ≥50%，在 510300/159915 内 40–50%；
5. **极端日先验**：159915 的 2024-09-30/10-08 ±20%（20cm 真市极限）将造成趋势上窗大额机会差额与提前全清仓；本批无 max 硬界（纯收益门），极端日只入 Sharpe/CI 读数不构成 VOID。

## §6 产物

- `engine/grid_sleeve.py`（v1 机械+离线 selftest，本轮 s5a 交付）＋ `scripts/grid_sleeve_p1.py`（runner：patch selftest→守卫→cells→nulls→passive→gates→D6→JSON+CSV，s5b 交付）；
- `results/grid_sleeve_p1.json`（顶层 evidence_cutoff＋gate 全输入＋audit 段）＋ `research/grid_sleeve_p1_results.csv`；
- 本文件 §7/§8 回填＋`results/gate_attrition.json` 追加一行。

## §7 跑后实证【跑前必须为空——写数字即造假】

（占位）

## §8 批后复盘【必填·s7-T】

（占位）
