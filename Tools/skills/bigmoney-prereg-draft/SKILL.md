---
name: bigmoney-prereg-draft
description: BigMoney 批回测预注册起草正典（从 PREREG_TEMPLATE 到跑前冻结 commit 的全链路）。Use when drafting/审查任何新批预注册（回测/因子/组合/数据验证批）、做 D6 同族相关性准入检查（max|corr|≥0.7 拒收）、调 science_gates g1_prime_v2/g2_registration_v2 共享判据库、写 evidence_cutoff/cutoff_meta、或跑后回填 §7/§8 与 gate_attrition 损耗账。
---

# BigMoney 批预注册起草（bigmoney-prereg-draft）

一切新批（策略/因子/组合/数据验证）先预注册后跑批。权威链=`research/BACKTEST_SCIENCE.md`（v2 判据唯一权威）+`research/BACKTEST_PLAN.md` 三铁律（样本外恒盲+成本恒开+每批同跑随机 null 基线并计 N）+`research/COMPUTE_AUDIT.md`（批件纪律）。

## 工作流（按序，跳步=批不受理）

1. **认领先行（F-04 律）**：开工前 `fleet/inbox/` MSG 声明批名+任务板引用——双机在制窗口互不可见=撞车根源；>10min 批必须后台化+跨轮 checkpoint（R41 教训）。
2. **复制模板**：`research/PREREG_TEMPLATE.md` → `research/<BATCH_ID>.md`，逐节填齐 §0-§6 后**跑前 commit 冻结**；§7 跑后实证跑前必须为空（占位纪律：写数字即造假）。
3. **§1 α 机制段四选一必填**（D6 无机制段=批不受理）：风险溢价/行为偏差/结构性/微观结构——一句话论证「为什么该信号应该有超额、由谁付出代价」。
4. **D6 同族相关性准入**：新策略函数入批前算 `max|corr|`（vs 在册交易员全部成员+在队/同批全部函数，日收益序列口径），逐对列数值与对照清单；**`max|corr| ≥ 0.7 → 拒收**（防 N 膨胀放大 D1 校正负担；确有新机制主张须另开预注册论证相关性来源）。
5. **§2 evidence_cutoff（前向锁盒 D2）**：面板一律截断到 cutoff；cutoff 后新 bar 锁定不得回流本批；结果 JSON 顶层必带 `science_gates.cutoff_meta(cutoff)` 字段（**缺字段=science_audit C2 VIOLATION**；共享库对 results/ 扫描须容忍非 dict 顶层形态——r239 律）。
6. **§3 账本**：`science_gates.append_ledger(batch_name, batch_trials, file_name, evidence_cutoff=...)`——dict schema 唯一，禁手抄 prev。null seed 新基先登记 `science_gates.SEED_REGISTRY` 再跑。
7. **§4 判据禁手抄判线**：G1' v2=`science_gates.g1_prime_v2(sharpe_full, returns, batch_cells, n_trades, n_entries)`；G2=`science_gates.g2_registration_v2(g1_pass, dsr, pbo)`（DSR≥0.95 用 `deflated_sharpe_ratio` 原始收益跑，禁 dsr_from_stats 充数；PBO≤0.25 用 `screening/pbo.py` CSCV 8 块）。批报告逐列披露 skill_line/bootstrap_ci/trade_gate 全输入；缺输入=诚实拒收。
8. **硬界设计三件套**（数据腐坏/健康检测类判线必填·D-20260925-01①）：(a) 分布界（median/p99.9）承担检测主责，禁裸 max 作主判；(b) max 硬界须配危机日感知（如双面 |r1|<5% 才计入）或豁免单列披露；(c) §5 跑前预测必含极端日先验（实证：REGIME_GUARD 深回放 D-C 被 2015 救市/2016 熔断等 12 真实极端日击穿 max≤200bp=界设计失误非数据问题）。
9. **成本口径**：新批建议 V2（ADV20 三层滑点+1%ADV 帽，knowledge/rules.py）；历史锚点复现恒用 V1 双轨防漂移。§5 预测≥3 条写死于跑前，跑后对账。
10. **跑后**：§7 一次定稿（工程修复重跑双跑留痕；确定性引擎产物写 bug 的合法重执行≠结果重跑）；§8 批后复盘必带 `results/gate_attrition.json` 追加一行（**消费面读 `entries` 列表——写错列表名=行静默丢失 r248 律**）+判线 v2 当批读数；注册新员另走注册件+live/paper SIGNAL_BUILDERS 接线+smoke 锚定门复跑。

## 红线速查

- 跑前冻结后**禁改判据禁重跑**；跑后只许回填占位节。
- 判据节禁手抄数值判线（漂移面=共享库唯一权威）；模板=research/PREREG_TEMPLATE.md。
- 新维度/新资产类开线必先过 `firm/PRODUCT_MATRIX.md` 缺口清单（防拍脑袋立线）+外源证据面扫描先行（O-1721 借力律）。
- P1 级新方向须署名任务单才开工（总经理署名即有效；实盘开闸/红线增废/使命变更/重大资源承诺仍须 CEO）。
