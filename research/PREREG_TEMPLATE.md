# 预注册模板（新批必填）· T-02 6/7 · D6 机制门槛载体

> 权威：research/BACKTEST_SCIENCE.md（v2 判据唯一权威）＋ BACKTEST_PLAN.md 三铁律 ＋ research/COMPUTE_AUDIT.md（批件纪律）。
> 适用：本件入库（2026-09-23 O-20260923-2215）后冻结的一切新批预注册。入库前已冻结批次按 §8 过渡条款（存量复现用 recorded_lines 历史常数）。
> 用法：复制本模板为 `research/<BATCH_ID>.md`，逐节填齐后 **跑前 commit 冻结**；跑后只许回填占位节，禁改判据禁重跑。

## §0 批件身份【必填·跑前】

- 批名 / 批号（批内格数＝每格计入 N_eff，扩容即买单）：
- 认领：F-04 先行——开工前 fleet/inbox/ MSG 声明（防双机在制窗口互不可见撞车）＋任务板/任务单引用：
- 部门归属（dept:研究/策略/交易/风控/数据/工程/舰队）：
- 算力预算：预估时长/worker 数（≤floor(核×0.8)；>10min 批必须后台化+跨轮 checkpoint，R41 教训）；批报告必带 audit 段（无 audit 段的结果件不入账本）。

## §1 α 机制段【必填·D6——无机制段=批不受理】

四选一（勾选）+ 一句话论证（为什么该信号在该品种上**应该**有超额、由谁付出代价）：

- [ ] **风险溢价**：持有不适风险/流动性风险/行为风险的补偿——论证：
- [ ] **行为偏差**：锚定/处置效应/追涨杀跌/注意力稀缺等可命名偏差——论证：
- [ ] **结构性**：指数调样/申赎机制/涨跌停制度/披露时滞等结构摩擦——论证：
- [ ] **微观结构**：买卖价差/成交约束/订单流不平衡——论证：

**同族相关性准入检查【必填·D6】**：新策略函数入批前算 `max|corr|`（与在册交易员全部成员＋在队/同批全部函数，日收益序列口径，sleeve-tag 先例）：
- 数值与对照清单（逐对列出）：______；`max|corr| ≥ 0.7` → **拒收**（防 N 无限膨胀放大 D1 校正负担；确有新机制主张须另开预注册论证相关性来源）。

## §2 数据与面板【必填·跑前探针事实，非结果】

- 宇宙/池（core48 或声明口径；扩池须申明白名单与核名状态）：
- 窗口与 **evidence_cutoff（前向锁盒 D2）**：面板一律截断到 cutoff ______；cutoff 后新 bar 锁定不得回流本批；
  结果 JSON 顶层必须带 `science_gates.cutoff_meta(cutoff)` 字段（缺字段=science_audit C2 VIOLATION）。
- 数据完备门（不过门禁跑批）：______

## §3 方法学【必填】

- 因子/信号定义（冻结参数）、滞后规则（披露时点→信号可用日，禁未来数据）：
- null 对照：K=______ 同掩码随机 null（seed 基=______；新基先登记 `science_gates.SEED_REGISTRY` 再跑）＋被动基线（池已校准者）；
- 成本口径声明：**V1 legacy（13bp×2 压测）或 V2（ADV20 三层滑点+1%ADV 帽）**——新批建议 V2（knowledge/rules.py）；历史锚点复现恒用 V1 双轨防漂移；
- 账本：`science_gates.append_ledger(batch_name, batch_trials, file_name, evidence_cutoff=...)`（dict schema 唯一，禁手抄 prev）。

## §4 判据【必填·跑前写死，禁看结果调线】

- **G1' v2 = `science_gates.g1_prime_v2(sharpe_full, returns, batch_cells, n_trades, n_entries)`**：
  全期 Sharpe > skill_line_v2（数据驱动=max(被动+0.10, μ_null+σ_null·√(2·ln N_eff))）**且** 平稳 bootstrap CI 下界 > 0 **且** entries≥30（F6 双口径，(entries_ok) 为准）；批报告逐列披露 skill_line/bootstrap_ci/trade_gate 全输入。
- **G2 注册资格 v2 = `science_gates.g2_registration_v2(g1_pass, dsr, pbo)`**：G1' 过线 **且** DSR≥0.95（`deflated_sharpe_ratio` 原始收益跑，禁用 dsr_from_stats 充数）**且** 家族 PBO≤0.25（`screening/pbo.py` CSCV 8 块，同族网格=g25_retro 先例）；缺输入=诚实拒收。
- 保留历史描述性条款（批级披露）：年化>0、OOS 双正、回撤≥-35%、无崩年、成本压测（×2/×3 或 V2 视口径）逐年稳定——描述条款不替代 v2 门。
- **硬界设计三件套【数据腐坏/健康检测类判线必填·D-20260925-01①·F-20260924-11】**：(a) **分布界（median/p99.9）承担检测主责**——腐坏/健康判线以分布界口径设计，禁裸 max 作主判；(b) **max 硬界须配危机日感知或豁免单列**——如双面 |r1|<5% 才计入、或命中先记危机日志+豁免路径=单点删除优先于整批判负，豁免逐日单列披露；(c) **跑前预测（§5）须给极端日先验**。实证：REGIME_GUARD_DEEP_REPLAY D-C 批 12 真实极端微观结构日（2015-07 救市 510300 涨停锁价 +9.99% vs 指数 +6.40%｜Δr1|=461.6bp、2016-01 熔断、2026-01-19 极端溢价）击穿 max≤200bp 硬界，三方佐证（原始行真市场价/D-A 全过/D-D 三矩阵贴合）定非腐坏=界设计失误非数据问题；跑前只测 median 未测 max 尾部=预测盲区。
- 因子批（IC 型）沿用 V1=max(0.02, null p95)/V2=IC_IR≥0.30/V3=OOS 同号留存三门口径＋h 口径跑前冻结（h10 主口径，换口径=数据窥探红线）。

## §5 跑前预测【必填·写死于跑前，跑后对账】

（方向/量级/门槛读数，≥3 条；含**极端日先验**——本批数据窗内可能击穿 max 硬界的极端微观结构日形态与量级，硬界设计三件套 (c)·D-20260925-01①）

## §6 产物

（script + results JSON 顶层 evidence_cutoff + CSV + 本文件 §7 回填）

## §7 跑后实证【跑前必须为空——占位纪律：写数字即造假】

（一次定稿；工程修复重跑须双跑留痕如实记账；确定性引擎产物写 bug 的合法重执行口径≠结果重跑）

## §8 批后复盘【必填·s7-T】

- 预测对账（对/部分/错）＋门禁链损耗账（`results/gate_attrition.json` 追加一行）＋判线 v2 当批读数（skill_line_v2 数字）；
- 回执入轮报告＋CODELY.md 行级追加；若注册新员：注册件带 evidence_cutoff＋live/paper SIGNAL_BUILDERS 接线＋smoke 锚定门复跑。
