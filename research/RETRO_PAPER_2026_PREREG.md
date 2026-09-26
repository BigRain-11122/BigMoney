# RETRO-PAPER-2026 预注册（年内回放纸盘批）· T-79 · O-20260926-1326 CEO 直令

> 跑前冻结件。跑后只许回填 §7 占位节；禁改判据禁重跑（工程修复重跑须双跑留痕）。
> 语义=**纸盘引擎重放**（非裸回测、非新策略搜索）：对**既有在册账户族**按纸盘语义重放 2026 年内窗口，产出每账户完整纸盘台账+一页榜呈 CEO；CEO 认可=实盘模拟盘唯一准入门（本令立法，追加门，位于既有晋升阶梯之上）。

## §0 批件身份

- 批名/批号：**RETRO-PAPER-2026**（回放台账面，批内格数=0 新试验——见 §3 账本政策）；账户族 16 员（A6+B4+C7=17 台账，其中 B 组 4 员含 B_MAXDIV 正典）——台账面非搜索面，N_eff 不适用（零新函数零搜索零 nulls → SEED_REGISTRY +0，T-56 slice-2 marks 范式）。
- 认领：F-04 = fleet/inbox/MSG-20260926-1338-bmb-retro-paper.md；票 T-2026-09-26-79（P1·immediate·claimed bm-b R252，commit b84f8636）；令 O-20260926-1326。
- 部门归属：dept:交易（A 组纸盘引擎面）+组合与资金（B/C 组 blend/alloc 面）+总经办（s2 榜单呈报）+工程（s3 网关预接线）。
- 算力预算：A 组 12 跑（6 员×x1/x2）秒级/跑（paper_run 烟测口径）；B 组 sleeve 56 腿（28 员×x1/x2，T-56 实测分钟级）+blend 秒级；C 组 7 cell（alloc_backtest 全史单跑）。预估总时长 **<5min**（R41 豁免口径，T-28 实测 5.4s 级先例）；超时实况>5min 则转池（O-2100/O-2130 分片律），轮报告如实记。

## §1 α 机制段（D6）

- 本批**零新信号函数、零新成员**——回放对象全部为既有在册/在案账户（6 员 INTERN 注册件 `firm/traders/*.json`（各自注册时已过 D6 机制门槛）+ T-27/T-28 冻结装配 B_MAXDIV + T-56 冻结 AGGR 三账户 + T-66 冻结 ALLOC cells）。四选一勾选：**不适用（无新机制主张）**——各员机制论证见其注册件/预注册（COMPOSITE/CE 族=行为偏差+风险溢价复合，AGGRESSIVE_LAB.md §1，AGGR_FAMILY_PREREG.md §1）。
- 同族相关性准入检查：不适用（无新函数入批）；D6 防重面由「账户族=冻结清单枚举」承担（§2 账户清单冻结=反挑面）。

## §2 数据与面板

- 宇宙/池：core48 在册纸盘面板（`live.paper.load_core()`，48 ETF 无前缀 CSV，烟测口径）；blend 腿= T-27 冻结 28 员 roster（FROZEN_ROSTER，o1600 口径）。
- 窗口与 **evidence_cutoff=2026-09-24**（最新完整 bar；09-25 中秋休市）：**窗首=2026 年首个交易日 2026-01-05**（T-28 W-CUR 先例同锚）。面板一律截断到 cutoff；cutoff 后新 bar 锁定不得回流本批；结果 JSON 顶层必须带 `science_gates.cutoff_meta("2026-09-24")`。
- 账户清单（冻结枚举，全家族如实呈报禁挑面）：
  - **A 组（6 员纸盘引擎重放）**：COMPOSITE-CE-01、COMPOSITE-CE-02、DROUGHT-CE-01、ENGULF-CE-01、NEEDLE-DE-01、VOLATILITY-CE-01（level=INTERN 在册 6 员；PROSPECT 22 员不在册纸盘面不入）。重放口径=注册件 params+exit_overrides 逐字+回放 hire 日 2026-01-05（信号全史暖窗、成交窗口内，paper_run 契约）。
  - **B 组（4 员 blend 台账）**：B_MAXDIV（正典，TOURN_JSON 权重 sha 9b112d51583aeeb7 门）+今晨判决前三（CEO 令原文点名）：AGGR-REGIME（sha b95dab70673f5941/off+3868f2f55bae825e/def，v3 原始态 shift(1) 因果）、AGGR-CONC-TOP2（9a9579482cc1851b）、AGGR-OFFENSE（eac2b583586e8bb3）。sleeve=28 员×{x1,x2}。
  - **C 组（ALLOC 7 cell）**：ALLOC-P1/P2/P3/P3B/P4/P5/P6（工单写 6、接线实况=7 cells 1:1 镜像冻结 s2 cells，P3B 独立 cell 如实并入；alloc_backtest 全史单跑后切窗）。
  - **GRID/CN 族**：就绪即并入、非阻塞（GRID 今晨判 0/5 生存者=未就绪如实披露；CN=T-73 runner 未跑）。不入本批台账，榜单注明缺席原因。
- 数据完备门：cutoff 面板完备（48/48 可读、最新 bar=09-24，烟测 PASS 口径）；alloc P5 slot 510880 stale-leg 披露口径沿用 alloc_paper（ffix in-repo 披露面）。

## §3 方法学

- **A 组**：`live.paper.paper_run(t_retro, prices_trunc, P)`，t_retro=注册件副本+created="2026-01-05"；exit_overrides 经 ExitPatch 逐字（r241 律：断言走 `_eb.ExitConfig` 消费面）；x2 腿=CostPatch(2) 同窗重跑（cost_x2_check 同构）；初始资本=引擎默认 ¥1,000,000（与在册纸盘/AGGR/ALLOC 统一）。
- **守卫 shadow（令原文口径）**：regime_mask=None+fill_guard=None（legacy 记账=与 2026-10-01 前生产纸盘实况一致）；v3 政体态序列（v3_state_series，因果）**逐日随台账记录**（shadow 只记不干预）供 §4 政体段分解消费。
- **B 组**：sleeve=aggressive_lab 口径（`_sleeve_worker` 28 员×{x1,x2}，截断 cutoff 2026-09-24）；blend=`_blend_daily_ret`/`_regime_blend`（REGIME 账户 v3 态 shift(1)）逐日收益→`_accrue_marks(start=2026-01-05, initial=1e6)` 逐日结算；AGGR-NOCASH 风险预算字段不适用（本批仅前三账户+NOCASH 未入选）。
- **C 组**：alloc_backtest 冻结 s2 cells 机制（monthly/daily-threshold 模式逐字）全史算→切窗 2026-01-05 起；side_cost_v2 v2_main 口径与 s2 判决面恒等（alloc_paper L6 同款）。
- 逐月记分：`live.paper.monthly_aggregate(equity, 1e6, "2026-01-05")`（hire 窗首月不计、足月才计——冻结口径逐字）。
- null 对照：不适用（零搜索面，无判线主张——见 §4）；被动基线=B_MAXDIV 正典即榜内（对照面=正典再锚，T-56 canon_verification_face 先例）。
- 成本口径：**V1 legacy（13bp×2 压测）双面 x1/x2**——历史锚点复现恒用 V1 双轨防漂移（模板 §3 律；t28/aggressive_lab 全族同口径）。
- **账本政策：`append_ledger('RETRO-PAPER-2026', 0, ...)` +0**（marks/台账面非试验，T-56 slice-2 范式；零注册零判线主张；真前向纸盘 09-23 起在跑双轨互证）。

## §4 判据（描述性榜单面·跑前写死）

- **本批不主张任何注册/晋升判线**（0.70 J-line 不在本批主张面——票 note 原文；准入=CEO 认可门，O-1326 立法）。榜单列（每账户×{x1,x2}）：
  1. 累计收益（窗口净额，含成本）；
  2. 年化 =（1+累计）^(252/窗口交易日数)−1（冻结公式）；
  3. 最大回撤（月度路径口径 max_drawdown + marks 口径 _marks_dd 双披露）；
  4. **月度正收益率** = 正收益足月数/足月数（monthly_aggregate counted 口径；足月数<3 时如实标 insufficient）；
  5. 政体段分解 = bull/chop/bear 三段累计（_seg_classes，v3 态 shift(1) 因果）；
  6. 交易数（A 组=engine trades 计数；B/C 组=blend/alloc 面无离散交易单，如实标 blend-face n/a）。
- 排序出榜（主键=月度正收益率，次键=x1 累计收益——令原文「排序出榜」的确定性落法，跑前冻结）。
- 诚实标注（**榜内原文必载**）：本窗与策略 OOS 开发窗重叠=历史纸盘重放证「纸盘语义下成立」，非前向新证据；真前向纸盘 09-23 已在跑、双轨并行互证；判负照报。

## §5 跑前预测（写死于跑前）

1. B_MAXDIV x1 窗口累计 ≈ **+0.9%**（T-28 实测 0.00943@09-23 窗，延 1 bar 至 09-24 预期同量级 |Δ|<0.5%）；x2 ≈ +0.4~0.6%（成本拖累 0.94%→0.48% 先例）。
2. 2026 窗=ORANGE_COOL 震荡政体 → 保守 blend 面预期低个位数正/负收益；AGGR-OFFENSE（进攻军集中）波动更大，判负概率不低——判负照报。
3. 月度正收益率预期 3~7/8 足月（2026-01-05 起 9 个月窗，首月不计→足月≤8）；无一账户预期 100% 正月。
4. 极端日先验：2026-01-19 极端溢价日（D-C 批先验）在窗内——sleeve 级单日 |r| 可达 ~5%；窗内无 2015 级危机日；本批无 max 硬界判线（描述面），极端日以台账逐日明细如实呈现。
5. A 组 6 员：注册 OOS Sharpe 0.38~2.06（烟测锚面），回放窗横跨 IS/OOS 开发窗——预期多数员正收益但不保证，全部如实入榜禁挑。

## §6 产物

- `scripts/retro_paper_2026.py`（runner+selftest；--shard 池就绪口径备用）
- `results/retro_paper_2026/<ACCOUNT>_ledger.json`（逐日权益/逐月表/回撤序列/交易单/政体段/守卫 shadow 记录/_cutoff_meta 顶层字段）
- `results/retro_paper_2026/LEADERBOARD.json` + `docs/daily_report/`外独立呈报页 `results/retro_paper_2026/LEADERBOARD.md`（一页榜+诚实标注原文）
- s3：`docs/CEO_APPROVALS.md`（追加式认可台账，建册空表候 CEO 名单）+ 网关预接线注记（PLAN P4 通道，QMT/Ptrade——名单落地后才接线）
- 轮报告回执+心跳 orders_ack+CODELY.md 行级记录。

## §7 跑后实证（占位——写数字即造假）

- （跑后回填：每账户六列读数+足月数+与 §5 预测对账一句话）

## §8 批后复盘

- 预测对账（对/部分/错）；audit 段（compute_audit 采样如实）；判线主张=无（§4）；若 CEO 认可名单落地→CEO_APPROVALS 台账开账+网关接线队列开动（工程部 mandate）。
