# T33_ATTACK_WAVE · 进攻军团招募波（预注册，跑前写死）· T-2026-09-24-33 deliverable-2

> 2026-09-24 20:57 写死于任何回测运行之前（本批零格已跑）。预注册纪律：跑后不改门、不换口径、不重跑
> （BACKTEST_PLAN 铁律③）；跑后只许回填 §7/§8 占位节。判据节调 `science_gates` 共享库，禁手抄判线（T-02 6/7）。

## §0 批件身份

- 批名 / 批号：`t33_attack_wave` · 20 候选 × 2 成本面（base + x2）= **40 格**（每格计入 N_eff，扩容即买单）；
  认领：T-2026-09-24-33 已由 bm-c 认领（commit 4eeb56a，F-04 MSG-20260924-2031 先行，claim 内已声明 d2=本波）；
  车道：研究部（dept:研究）+ 策略；bm-a R91 让路裁定=T-33 正典归 bm-c。
- CEO 令源：O-20260924-2012（风格军团架构·进攻军团 CEO 第一优先）；候选面由票面 spec 逐字圈定。
- 算力预算：40 全窗格 + 6 在册锚定复现（1x+x2，复现门非新试验，t24 先例 ledger+0）；单格全窗 ~2-8s，
  并行 workers=floor(核×0.8) BelowNormal（O-1136 满载低优先池）；**后台分离批 + JSONL checkpoint**（R41），
  批报告必带 audit 段。

## §1 α 机制段【四选一】

- [x] **行为偏差**：动量/突破族的超额=反应不足与追涨杀跌行为的可命名偏差——信息扩散慢（散户注意力稀缺、
  处置效应捂盈利仓）使价格对新趋势反应不足，突破后延续；代价支付方=迟钝的配置盘与反应过慢的散户。
  - PROSPECT 三族（VOB 放量突破/IBB 内包线突破/DUCK 鸭头）= zoo §九既有机制行（ta_vol_breakout/
    s10_patterns 族，判定过筛带档）；#81-83=波-1 过筛登记（zoo §十三 #81/#82/#83）。
  - 库存趋势族（trend/momentum/composite 模块）= P1 海选同机制（J7 时代 α 段沿用）。

**同族相关性准入检查【D6】**：批内 20 候选两两 + 对 6 在册员，日收益序列口径（全窗对齐）：
- 数值与对照清单：跑前不可得（须先跑引擎）→ **批内计算+按优先序合并条款（冻结）**：组序 A（CEO 点名
  PROSPECT 进攻族：VOB→IBB→DUCK）＞ B（digest 波-1：#81→#82→#83）＞ C（库存趋势族：P1 网格序）；
  同组内按列序。`max|corr| ≥ 0.7` → 后列者并入前列者（D6-merged 状态披露，族代表继续判定）；
  对在册员 ≥0.7 仅披露不拒收（本批=G1' 招募非注册，注册门另有 G2）。

## §2 数据与面板

- 宇宙/池：**core48**（48 裸码 ETF，`live.paper.load_core`，零管线改动）；基准 csi300.csv（P1 先例，
  dual_mom_120 / rs_rotation_20 用）。
- 窗口与 **evidence_cutoff = 2026-09-24**（本机 09-24 bar 已落 update_daily+paper 6/6 实证）：面板一律截断
  到 cutoff；结果 JSON 顶层带 `science_gates.cutoff_meta("2026-09-24")`。
- 数据完备门（不过门禁跑批）：48/48 符号在册、面板末日=cutoff、无未来日期、null 池 n=120≥30、
  被动基线 core48 在档、6 在册员锚定复现全 PASS（任一 FAIL=批 void，live.paper.anchor_gate 口径）。

## §3 方法学

- 候选网格（固定 20，零搜索零调参）：
  - **A 组（5）CEO 点名 PROSPECT 进攻族**（成员件冻结参数，`SIGNAL_BUILDERS[params.entry]` 同键构造）：
    PROS-VOB-CE-01 `vol_breakout(20/1.5/20/10)`+CE；PROS-IBB-01 `inside_bar_breakup()`default；
    PROS-IBB-CE-01 同键+CE；PROS-DUCK-01 `duck_head()`default；PROS-DUCK-CE-01 同键+CE。
    CE 契约=t24 冻结常量（time_decay 25/0.05 + trailing 0.1 + ExitPatch loss_time_days=16）。
    cutoff 覆写：probe 字典 evidence_cutoff→本批 2026-09-24（成员件原值 09-22 留 lineage 披露）。
  - **B 组（3）digest 波-1 动量族**（zoo §十三 #81/#82/#83；runner 内参数化变体，**零新引擎件零库文件改动**，
    momentum/composite_rotation 骨架机制位）：
    - `slope_r2_rotation_25_top3_r8`：25 日 log(close) OLS 回归斜率年化×R² 评分，横截面 Top3；
      **min-hold 8d 用 8 日非重叠再平衡窗近似**（composite_rotation.rebal 机制参数化）；sizing
      max_positions=3, position_size_pct=0.95/3=0.3167。**换手预算（duck_head 标本律·必列）：
      年化入场次数 ≤ 50/年**，超线=本波不合格资格披露（非引擎门， Corps 部署可执行性条款）。
    - `dual_momentum_etf_20_60_top3`：20 日相对动量排名 Top3 + 60 日绝对动量>0 过滤；无人达标切防御
      =argmax 20 日动量于 {511260, 518880}（zoo 原文含 511880 但其非 core48 裸码——**池法优先**，披露）；
      防御腿 20 日动量≤0 → flat（现金）。sizing 同 0.95/3。
    - `gem_ashare_m12`：月频（每月最后交易日信号→次月生效）：12 个月动量比较 {510300, 513100, 513180}
      持胜者；胜者 12m 动量 ≤ 0 → 防御 511260（core48 内唯一国债腿；511880 缺席同上披露）。
      sizing max_positions=1, position_size_pct=0.95。
  - **C 组（12）库存趋势族**（STRATEGY_LIBRARY §一 trend.py 5 + momentum.py 5 + composite_rotation.py 2；
    **P1 缺省参数口径逐字复刻**——donchian_20_10 / dual_ma_5_20 / triple_ma_5_20_60 / parabolic_sar /
    supertrend_10_3（sym 类，引擎缺省 sizing max_positions=5/0.10）；xsec_mom_120_20 / dual_mom_120
    (bench=CSI300) / ts_mom_200 / rs_rotation_20 (bench=CSI300) / mom_accel_20_120（panel 类，缺省
    sizing）；composite_top5 / composite_top8（top_n_rotation，P1 sizing 0.95/n）。
    - **正典迁移披露**：P1 曾以 G1 v1 固定线（OOS≥0.8）判负全 12 族；本批按票面令以现行 v2 正典重判=
    判据迭代非跑到达标（P1 历史判罚留档不推翻；D1 多重校正负担由 N_eff 计入 40 格买单）。
- 滞后规则：信号 T 日收盘真值 → T+1 开盘执行（引擎内建，全候同口径）；月频 GEM 信号=月末日 → 次月首
  交易日执行。
- null 对照：**K=0 本批自有 null**（core48 池已校准——skill_line_v2 内部消费共享 null 收集器
  n=120，μ=−0.0332/σ=0.2429 跑前实读）＋被动基线=core48 校准件（跑前实读 0.3792）；随机基线律由
  共享 null 池承载（t27/T-28 同口径先例）。
- 成本口径：**V1 legacy（13bp×2）主面 + CostPatch(2.0) x2 压测面**（PROSPECT/在册证据全部 V1 口径，
  可比性优先；V2 ADV20 建议留档：本批不启用，注册前 G2 深化时按惯例再议）。
- 账本：`science_gates.append_ledger("t33_attack_wave", 40, file_name="results/t33_attack_wave.json",
  evidence_cutoff="2026-09-24")`（dict schema 唯一，prev=跑时链头数据驱动，禁手抄）。

## §4 判据【跑前写死】

- **G1' v2 = `science_gates.g1_prime_v2(sharpe_full, returns, batch_cells=40, n_trades, n_entries)`**：
  pass_v2 = 全期 Sharpe > skill_line_v2（数据驱动）**且**平稳 bootstrap CI 下界 > 0 **且**
  dual_trade_gate entries_ok（≥30 入场）；批报告逐列披露 skill_line / bootstrap_ci / trade_gate 全输入。
- 批级描述性条款（披露非门）：全期年化>0；OOS(2025+) Sharpe>0 且年化>0（双正）；全期回撤≥−35%；
  x2 压测面全期 Sharpe 披露；换手预算 ≤50 入场/年（超线=Corps 资格不合格披露）。
- 硬门（任一红=批 void）：6 在册锚定复现全 PASS；48/48 面板完备 @cutoff；无未来日期。
- **诚实零**：0/20 过 G1' v2 = 合法终判（CEO 令原文「honest zero if none pass」）。
- 每候选必报（D7 段纪律）：全期 Sharpe/距线差、CI 下界、entries/年、x2 面、OOS 双正、dd。

## §5 跑前预测【写死于跑前】

1. **线条款近乎全员处死**：skill_line_v2 在当前链头（58,070）+40 格下 ≈ 1.10 全期 Sharpe（跑前实读
   1.1046）；五名 PROSPECT 记录全期 Sharpe 0.2694-0.6817、库存 12 族 P1 记录全期 ≤0.4327——
   **预测 0/20 过线条款**（本波大概率诚实零；波的价值=距线差量化+D6 族结构+证据行）。
2. DUCK-01（记录全期 0.6817）为离线最近者；VOB-CE（0.4665）OOS 1.267 最强但全期面弱。
3. `gem_ashare_m12` 月频 → 全窗 entries 大概率 <30 → F6 双口径 FAIL（教科书族首次月频标定的已知风险）。
4. D6 合并预期：composite_top5↔top8 ≥0.7（同族近亲）；xsec_mom↔dual_mom↔rs_rotation 同动量域高相关；
   #81↔#82（皆短窗动量排名）≥0.7 风险高 → 后列并入前列。
5. `slope_r2_rotation`（8d 再平衡）entries/年 可能破 50 预算线 → 换手预算条款大概率触发披露。
6. x2 面：PROSPECT 记录 x2 全期 −0.07~0.26 → 本批 x2 面预期同步弱正或负。

## §6 产物

- script `scripts/t33_attack_wave.py`（run/status/finalize/selftest；分离后台+checkpoint 断点续跑）；
- results JSON `results/t33_attack_wave.json`（顶层 evidence_cutoff+audit 段+账本 dict+40 格全披露）；
- CSV `research/t33_attack_wave_results.csv`；本文件 §7/§8 回填；gate_attrition 追加行；
  T-33 票面 note 更新。

## §7 跑后实证【跑前必须为空——写数字即造假】

（占位：一次定稿；工程修复重跑须双跑留痕如实记账）

## §8 批后复盘【跑后回填】

（占位：预测对账 + 门禁链损耗账（gate_attrition 行）+ skill_line_v2 当批读数 + 回执轮报告）
