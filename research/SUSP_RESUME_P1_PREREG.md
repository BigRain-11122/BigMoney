# SUSP-RESUME-P1 预注册（短停牌复牌事件多头）· T-02 6/7 · D6 机制门槛载体

> 依据：research/BACKTEST_SCIENCE.md v2 ＋ BACKTEST_PLAN.md 三铁律 ＋ research/PREREG_TEMPLATE.md
> 起点：r1059 E20 census（短停 5-19 会期 2021+ 是唯一未死的复牌轴）＋ r1061 前向 watch 面。
> 冻结：本文件 commit 后即冻结；跑后只许回填 §7/§8，禁改判据禁重跑。

## §0 批件身份

- 批名/批号：SUSP_RESUME_P1（batch_id=susp_resume_p1；批内格数=3＝持有期 {3,5,10} 三格，进 N_eff）
- 认领：本机 bm-b 轮内直执（r1062；fleet 板/pool 无他人认领，census 与 watch 均由 bm-b 建）
- dept：研究＋策略
- 算力预算：单进程 CPU，预估 <120s（面板 8745×5225 一次装载，null K=2000 向量抽样）；无跨轮 checkpoint 需求
- 产物：`scripts/susp_resume_p1.py`（selftest 内建）＋ `results/susp_resume_p1/RESULT-<cutoff>.json`

## §0.5 禁开方向硬闸

- 过闸命令：`python Tools/banned_direction_gate.py --prereg research/SUSP_RESUME_P1_PREREG.md`（rc0 放行）
- 命中编号：无（BANNED_DIRECTIONS 无停牌复牌事件面条目）

## §1 α 机制段【D6】

- [x] **结构性**：A 股停牌/复牌制度摩擦——停牌期间信息公开化（重组/重大事项/核查结论），复牌首日撮合把累积信息一次性定价，但散户限价单/涨跌停制度造成次日仍有余价；卖方案例：停牌前持有者被强制锁定，复牌当日流动性冲击由抢筹方承担。
- [x] **行为偏差**（次）：处置效应＋注意力稀缺——复牌首日是天然注意力事件，追涨资金在 T+1 继续出价；对价为冷静期卖压。
- **散户凭什么赢**：**容量**＋**制度**——单事件名义额小（复牌股流动性差、单票挂单深度浅），机构资金容量装不下；同时散户与机构面对同一涨跌停/复牌撮合制度，无速度劣势。答得出，本批受理。
- **同族相关性准入（D6，跑前申报，脚本实测回填）**：候选函数日收益序列 vs 在册交易员（`firm/traders/*.json` 经 ew6 member_run 复算）逐对 corr；**拒绝线 max|corr| ≥ 0.7**。实测值见 §7 回填与 results JSON `d6` 段。
- **闭合族对号**：family_key=`SUSP_RESUME_P1`；`science_gates.CLOSED_FAMILIES` 不在册（9 族无关键）→ open 照跑，`closed_family_check` 回执随结果件。

## §2 数据与面板【跑前探针事实】

- 面板：`data/cache/p1c_local`（qfq 全 A 股，meta.shape=[8745, 5225]，meta.cutoff=2026-10-19，meta.start=1990-12-19，source=data/astock_daily/per）
- **数据锚面定义四元组**（每个锚）：
  1. 事件计数：`data/cache/p1c_local/{close,open}.npy` / `scripts/susp_resume_census.detect_events`＋`missing_runs` / 起算 1990-12-19 / 预热 0（缺 bar 即停牌代理）
  2. 收益窗：同面 / `np.load` 直读（非引擎 load_core）/ 起算 1990-12-19 / 预热 0（要求 entry open 与 exit close 双有效）
  3. 市场对照：同面 / `susp_resume_census.market_median`（同日横截面中位）/ 起算 1990-12-19 / 预热 0
- **探针-锚同面断言**：runner 加载路径＝锚声明路径逐位比对（`PANEL` 常量单一来源），一面不等＝VOID 拒烧。
- 停牌代理声明：面板无官方停牌标志，**缺失 bar=停牌代理**（census 同口径，r1059 已披露）。
- 事件定义：`valid(resume) & prev_missing_run ∈ [5,19]`，resume 行首有效（`rows > first_valid`），**信号在 resume 日收盘可得**。
- 冻结计数（跑前探针）：短停总事件 8,102；**2021+ 事件 805**；持有期有效可执行数：hold3=800 / **hold5=794** / hold10=784。
- 窗口：primary = 2021-01-01 .. 2026-10-19（evidence_cutoff=**2026-10-19**，面板字节 derive）；full-history 仅描述性披露，不作判据。
- 数据完备门：`valid.sum()>0`、事件数≥300、主格可执行≥30；任一不满足=诚实 no-op 不烧。
- cutoff 后新 bar 锁定不回流；结果 JSON 顶层带 `science_gates.cutoff_meta(cutoff)`。
- **探针种子选位律**：null 种子串起点 = **94801**（首扫 94001 命中 N1 wave-137 band 94001-94200＝BLOCKED，顺延至带外首个净点；`seed_admit_gate rc0 base=94801 span=1 verdict=FREE` 2026-10-20 实测随冻结提交）；带闸探针簇 95_000..95_003 合同保留簇不动。

## §3 方法学【冻结】

- 信号：resume 日收盘后确认（缺失 bar 连续数 ∈ [5,19]），**T+1 开盘入场**（禁同 bar 执行；涨跌停无法成交者按缺 bar/不可执行如实剔除）。
- 出场：**策略自有出场 ①**——固定持有 H ∈ {3,5,10} 个交易日，于 entry_idx+H−1 收盘出场；**显式不使用引擎缺省出场栈**（runner 不 import live.paper / exit_rules）。
- 收益：`r = close(exit)/open(entry) − 1 − mkt_h(entry_date)`，mkt_h = 同日横截面中位（同 H 窗、同可用性口径）。
- 组合：按入场日等权（当日事件均值）→ 日收益序列（仅事件日有点，非事件日 0 仓）。
- null：**K=2000**，每次从同窗口可执行单元全集（valid entry & 全窗有效）均匀抽 n_events 个（date,symbol），同成本同市场调整，同按入场日聚合 → null Sharpe 分布；p=(1+#{null≥real})/(K+1)。seed=94801。
- 成本口径：**V1 legacy 单边 13.041bp × 2 + 股票档附加**（`knowledge/rules.py fee_schedule_for` 股票前缀路由：过户费 0.1bp 双边、印花税 5bp 仅卖边）⇒ 买边 13.141bp / 卖边 18.141bp / **往返 31.282bp**；名义额 ¥20,000 档时 ¥5 最低佣金恰好等于 2.5bp 费率（不额外加价），更小单披露佣金率上浮。
- 账本：`science_gates.append_ledger("SUSP_RESUME_P1", 3, ...)`（三格各计 1 trial）。
- PBO：三格（hold3/5/10）日收益矩阵 → `screening.pbo.cscv_pbo`（CSCV 8 块）。

## §4 判据【跑前写死】

- G1' v2：`science_gates.g1_prime_v2(sharpe_full, returns, batch_cells=3, passive_override=<同窗股票等权 1 日 Sharpe>, n_trades=n_events, n_entries=n_events)`——需 line_ok ∧ ci_lower_positive ∧ entries_ok(≥30)。
- G2：`science_gates.g2_registration_v2(g1_pass, dsr, pbo)`——DSR≥0.95（`deflated_sharpe_ratio` 原始日收益，n_trials=ledger_total+3）∧ PBO≤0.25；缺输入=诚实拒收。
- t 面：`science_gates.t_from_sharpe(sharpe_annualized, n_days)` → `m1_t_value_gate`（t≥3.0）申报。
- 主格 = hold5；hold3/hold10 为格族成员（进 N_eff 与 PBO）。
- 描述性条款（不替代 v2 门）：年化>0、净收益均值>0、无崩年、成本×2 压测同号。

## §5 跑前预测【跑前写死】

1. hold5 净收益均值落在 +1.5% ~ +3.5%（census 2021+ ret5 净 +3.22% 的上界收缩），胜率 45%–55%。
2. Sharpe_full(年化) 在 0.5 ~ 1.2 区间；skill_line（含 N_eff 校正）大概率**高于**该值 ⇒ **预计 G1 不过线**（2021+ 样本仅 794 事件、日序列宽度不足）。
3. null p 值预计 < 0.05（方向上真实事件优于随机同日单元），但 p<0.05 不等于 G1 过线（两套门不同）。
4. 极端日先验：复牌日涨跌停锁死会造成单笔 ±10%/±20% 跳变（ST/创业板），hold 窗内单事件最大贡献可能达 ±20% ⇒ 单笔最大收益剔除敏感性（top-1 剔除后重算）随报告披露；硬界不作主判（分布界承担检测）。
5. 相关性：与在册技术面交易员（CE 系）预期 |corr|<0.3；与 fund_divlowvol 低相关（事件稀疏、非截面排序）。

## §6 产物

- `scripts/susp_resume_p1.py`（`--selftest` 离线自检 + 主跑）
- `results/susp_resume_p1/RESULT-2026-10-19.json`（顶层 evidence_cutoff、cells、d6、pbo、dsr、g1、g2、null、ledger 回执）
- 本文件 §7/§8 跑后回填

## §7 跑后实证【跑后一次定稿】

跑：`python scripts/susp_resume_p1.py`（selftest 8/8，run 108.4s，rc0），产物 `results/susp_resume_p1/RESULT-2026-10-19.json`（evidence_cutoff=2026-10-19）。

- 事件：2021+ 短停（5-19 会期）805 例；持有期可执行 hold3=800 / **hold5=794（主格）** / hold10=784。
- 三格净收益（成本 31.282bp、市场同日中位调整）：hold3 mean +0.430%/win 44.3%/Sharpe 0.544；**hold5 mean +1.256%/win 42.6%/Sharpe 1.154**；hold10 mean +3.405%/win 41.8%/Sharpe 1.800。
- 主格分布：min −32.28% / p5 −19.69% / p25 −9.80% / **p50 −2.09%** / p75 +6.25% / p95 +41.06% / max +106.60%；mean_cost_x2 +0.943%（×2 成本仍正号）。**均值=右尾驱动，中位为负**。
- null（K=2000，seed 94801，747 次有效抽样）：mean 0.891 / sd 0.612 / p95 1.848；**real 1.154 → p=0.3436**（事件 Sharpe 与随机同窗单元不可分）。
- G1' v2：**fail**（line 1.1558，real 1.1544 差 0.0014；`ci_lower_bound_positive=false`；trade_gate entries 794 ≥30 ok）。
- DSR=0.0（n_trials=1,049,144）；PBO=**0.0**（3 格 CSCV，低过拟合）；M1 t=**1.713**（<3.0 fail）；G2 v2 = **ineligible**（g1 未过）。
- D6：在册交易员逐对 corr max|0.0700|（PROS 系），远低于 0.7 → **ADMIT**（与在册成员近正交，机制独立性成立）。
- 分年净均值：2021 +1.18% / 2022 −0.59% / 2023 −0.12% / 2024 +5.25% / 2025 +1.05% / 2026 +1.96%；滚动 3 年窗 +0.16%/+1.51%/+2.06%/+2.75%。
- 账本：`(+3)` prev 1,049,141 → **total 1,049,144**；gate_attrition 追加一行（kind=judgment）。
- **判读：NOT_REGISTERED**——r1059 census 的正向先验（2021+ 短停 ret5 净 +3.22%）**在成本+市场调整+null 校准的组合面上不复现**；不复现根因=原 census 为事件级裸均值（未做组合聚合、未对随机同日单元做零分布），右尾主导使均值虚高。不注册、不接线 live/paper。

## §8 批后复盘

- 预测对账：①预测 mean +1.5~3.5% → 实测 +1.256% **错（低于带下沿）**；②预测 Sharpe 0.5~1.2 且 G1 不过线 → 实测 1.154/G1 fail **对（窄距 0.0014 未过）**；③预测 null p<0.05 → 实测 0.344 **错（本批最重要负发现：事件面与随机同窗无差别）**；④极端日先验：top1 剔除 1.256%→1.123% 无单笔主导，但 p95 +41% 说明右尾厚；⑤相关性预测 |corr|<0.3 → 实测 0.07 **对**。
- 门禁链损耗账：`results/gate_attrition.json` 追加 judgment 行（3 trials；eliminated=794）；attrition guard CLEAN。
- skill_line_v2 当批读数：**1.1558**（batch_cells=3，passive_override=同窗等权 0.4992，null_term 1.1558）。
- 全起点分布：见 §7 分布与滚动 3 年窗（四窗全正但 2021-2023 仅 +0.16%，多数窗不显著）。
- 试验量归因：本批新增 **3** trials（hold 3/5/10），≤100 免单独归因。
- 后续：短停轴**不升 judged 主线**；census 先验须带 null 校准才能进预注册——本批负结论写入 teardown 指针供后续事件面复用（禁止再用裸均值先验）。