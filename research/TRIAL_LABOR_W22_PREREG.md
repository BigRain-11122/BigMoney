# TRIAL_LABOR_W22 — 节前多bar持有（pre-holiday multi-bar hold）GENERATE 供料批

> 批号：TRIAL_LABOR_W22（wave-22；E23 收口后的唯一存活候选方向）
> 部门：dept:研究+工程
> 状态：**DRAFT（未冻结）** — 冻结动作 = runner pin + seed 登记 + 本件 §0 格面 sha16 回填同窗完成
> 队列出处：`state/queue/explore.md` E23 收口行（r1082 bm-b，E23 → W22 交接）
> 上游供给面：E23 `results/seasonal_horizon_stability/CENSUS-2026-10-19.json`（sha16 见 §2 探针断言）
> 机读格面：`results/trial_labor_w22/w22_grammar.json`（derive 脚本 `scripts/w22_prereg_derive.py`，selftest 13/13）

## §0 批件身份

- 批名/批号：TRIAL_LABOR_W22；格面 10（variant × h = 2 × 5）＋ K=200 同构随机 null = **210 screen trials**（每格计 1 N_eff）。
- 认领：bm-b r1084 起草；**冻结需 T-18 队头探针 + T-19 seed gate 复跑 CLEAR**（本草稿不构成开烧资格）。
- 算力预算：screen 210 格 × 单配置回测，切分片进 `results/runnable_pool.json`（每片 <5min/核），CPU-only，≤8 worker（16 核，CEO 10% 余量律）。批报告必带 audit 段。
- 判据库：`science_gates.g1_prime_v2` / `g2_registration_v2` / `deflated_sharpe_ratio` / `m1_t_value_gate`（禁手抄判线）。
- **出场轴显式声明（O-20261001-1108 三选一）**：**①策略自有出场** —— 持有恰好 h bar，第 h bar 收盘时间出场；**引擎缺省出场栈显式禁用**（`engine_default_stack=disabled`，机读面 `w22_grammar.json.exit_axis`）。本批不为 template_default，也不做持有到底声明。

## §0.5 禁开方向硬闸

- 跑前闸：`python Tools/banned_direction_gate.py --prereg research/TRIAL_LABOR_W22_PREREG.md`（r1084 起草窗实测 REJECT→补全本段；冻结前必须重跑至 ADMIT）。
- 命中编号：**BAN-04**（字面模式命中 §3 表头「网格 | 格数」；逐条裁定如下）。
  - **BAN-04（Grid trading）**：命中类型 = **字面误报**。本件「网格」一词全部指 **census 枚举网格**（2 变体 × 5 持有期 = 10 格全枚举），不是 grid trading —— 无阶梯加仓、无固定买卖带、无摊平补仓；每格是把一个日历入场条件喂进**策略自有时间出场**的单变量 census。
- 例外类型：**new_mechanism**（同时携带 new_data 证据面）。
- 原否证不可能看见的东西：否证面（月度/节前日历效应类审计）测的是**月度切换**族的成本后期望（431 spells/35.8yr = 3.14%/yr 成本，tom_start1 净 -0.50%/yr，已判死），其数据面**没有 h≥2 的多 bar 持有**分解——E23 日频等权面（8,638 日 / 5,225 名 / 16.58M stock-days，2026-10-20 才落地）实测 hol_pre1 h=4 超额 +103.4bp（t=3.02）且四时代全正，年成本 ≤0.06%，这是月度切换否证面结构上无法看见的面。
- 本批仍为**零宣称供料 census**（10 格 + 200 null 全枚举，判据照 v2 门禁跑）；例外申报只用于取得开烧资格，不构成任何正期望主张。若 screen 全灭，方向按负发现进 EXCLUSION_BOOK。

## §1 α 机制段

- [x] **行为偏差（假期前风险再定价）**
  - **hol_pre1（节前倒数第 1 个交易日前置入场）**：长假前，机构出于风险预算/流动性管理减仓，散户与短线资金在节前最后一个可交易窗口承接；E23 日频等权面实测 hol_pre1 超额 +26.5bp（t=+1.92），h=4 达 +103.4bp（t=3.02），且**四个时代全为正**（pre2017 +32.4bp / 2017-2020 +15.6 / 2021-2023 +60.2 / 2024-2026 +60.8）——这是 E23 45 格里唯一成本后仍正且时代稳定的面。
  - **hol_pre2（节前倒数第 2 个交易日前置入场）**：更早入场的对照臂，用于分辨「收益来自节前漂移本身」还是「来自最后一日冲击」——若只有 pre1 有效，说明效应集中在最后一日，多 bar 持有无增量；若 pre2 同向，则持有期可扩展。
  - **散户凭什么赢**：不赌速度、不赌数据、不赌容量。假期前减仓是**可预期的日历性风险转移**，散户没有月末/季末风险预算约束，可以用时间换折价，T+1 执行即可，成本可控。
- **同族相关性准入（D6）**：与 `fund_divlowvol_p2` / `rev_osc_std` 两族做日收益 max|corr| ≥ 0.70 拒收（screen-finalize 后按族合并前实测申报，机读 `d6.measured`）。命名空间 `w22_hp` 前缀，与 W16-W21 冻结名册零字面交集（G-ROSTER 三闸 live 复跑）。

## §2 数据与面

- 宇宙/池：leg-L core48（`p5c_virtual_timepoint._load_leg("L")`，与 W16-W21 同面），`G-PANEL` live 断言。
- 数据锚面四元组：
  - 主面：`data/daily/*.csv` 本地 ETF/指数 CSV → `_load_leg("L")`，起算 `LEG_L_FLOOR`，预热 `WARMUP_TD`。
  - 探针面（G-510300-FACE）：`data/daily/sh510300.csv` raw 直读截断 CUTOFF。
  - 日历面：交易日历来自本地 ETF 日历（`data/daily` 主源），**节假日定义 = 日期间隔 ≥3 自然日**（与 E23 `face.holiday_breaks` 同口径，禁引入外部节假日表）。
  - 上游证据面：`results/seasonal_horizon_stability/CENSUS-2026-10-19.json`（`open()` + `json.loads` 全文件读）。
    - 口径披露：上游读数取自 1990-12-19..2026-10-19 日频等权面（8,638 个可用日 / 5,225 名 / 16.58M stock-days）；本批回测在 leg-L 冻结 cutoff 上跑。**上游是机制出处与格面锚，不是本批回测数据。**
- 探针-锚同面断言（`_e23_anchor_gate`）：逐位复核 ①census `evidence_cutoff == "2026-10-19"` ②`hol_pre1@h4` 读数（excess 0.01034421 / t 3.02475578 / n 180）与文件字节一致 ③`w22_grammar.json.grammar_sha16 == "ac29b0715bcbbe06"`（本节冻结面）。一面不等 = 面错 → VOID。
- 窗口律：`evidence_cutoff = 2026-09-22`（`tl1.CUTOFF`，P-5C 绑定），cutoff 后新 bar 锁定不回流；产物顶层带 `science_gates.cutoff_meta(CUTOFF)`。
- 数据完备门：G-PANEL（48 成员、末 bar == cutoff、五列齐）+ G-EXITCFG（A9 缺省表存在但**本批显式禁用**，断言 `exit_axis.engine_default_stack=="disabled"`）+ G-ROSTER / G-SEEDS / G-LINEAGE / G-E23ANCHOR 全过才生成开烧。

## §3 方法面

| family | 定义（frozen） | 网格 | 格数 |
|---|---|---|---|
| `hol_pre_hold` | 信号日 = 长假前第 p 个交易日（p ∈ {1,2}）；entry = 信号日后 t+1 开盘（T+1 保守代理）；exit = 入场后第 h bar 收盘（时间出场，无止损无移动止盈） | p ∈ {1,2} × h ∈ {1,2,3,4,5} | 10 |

- **单执行配置**（全 10 格 + 200 null 相同）：`R=engine-default, X=strategy-own time exit, S=equal_weight, T=daily_signal, 其余 none` —— 入场日历 + 持有期是唯一被测维度。
- 滞后规则：信号只用 t 日及以前的交易日历；入场落 t+1 开盘（无未来数据）。节假日判定用**已发生时点的日期间隔**，不看未来。
- null 对照：K=200 同构随机信号（同网格同配置，rng `[20670000, i]`）；gen 种子 `20670000` 全程 HELD（census 全枚举，零抽样零选择自由度）。**冻结前必跑 `seed_admit_gate` 验 band FREE**（起草时未跑，如实标注）。
- 成本口径：`ce_transfer.COST_X1_RATE` = 13.041bp×2 往返（ETF/指数面统一）。E23 已证：**月度切换** 431 spells/35.8yr = 3.14%/yr 成本 → tom_start1 净 -0.50%/yr；**h≥2 的多 bar 持有把切换次数降到一年 ≤2 次**，annual cost ≤ 0.053%（单臂）——这是本批相对月度切换家族的唯一结构性优势，必须在批报告成本段显式对账。
- 账本：`science_gates.append_ledger("TRIAL_LAB_W22_SCREEN", 210, ..., evidence_cutoff=CUTOFF)`。
- 闭合族对号（M3）：`family_key=TRIAL_LABOR` 不在 `CLOSED_FAMILIES`，open 照跑（G-GRAMMAR `in_closed=false` 断言）。

## §4 判据（跑前写死，禁看结果调线）

- **G1' v2**：`g1_prime_v2(sharpe_full, returns, batch_cells, n_trades, n_entries)` — 全窗 Sharpe > skill_line_v2（N_eff=210 的 null 校准）+ 平稳 bootstrap CI 下界 > 0 + entries ≥ 10。
- **G2 v2**：`g2_registration_v2(g1_pass, dsr, pbo)` — G1' 过线 + DSR ≥ 0.95 + 家族 PBO ≤ 0.25。
- **M1 t 门**：t ≥ 3.0（`m1_t_value_gate`）；t = missing_input 拒收。
- **screen 生存线**：`beat6m_rate` vs 同起点被动基线（`>=` 字面），k/n + binom_z/p 全披露；族级 axe = 族内至少 1 格过线才整族进 judge。
- 描述性条款（披露不阻断）：年化为正、回撤 ≤ -15%、成本 ×2 压测、无崩年。
- **D6 门槛**：族级合并日收益 vs `fund_divlowvol_p2` / `rev_osc_std` max|corr| ≥ 0.70 → 整族拒收。

## §5 跑前预测（写死于跑前）

1. **h=4 应为本批最强格**（E23 实测 +103.4bp，t=3.02），但**不预期** G1' 过线：日频超额 10bp 量级 vs 年化波动，Sharpe 提升远低于 v2 skill line（E14/E20 同型结论）。
2. **h=1 应最弱**：E23 hol_pre1@h1 超额仅 +26.5bp（t=1.92），单 bar 持有把效应稀释成噪声；若 h=1 反而最强，说明收益集中在节前最后一日，多 bar 持有无增量——那是**与 E23 方向相反的负发现**，照报。
3. **hol_pre2 应持续弱于 hol_pre1**（更早入场只承担风险不享受折价），预计 0-1 格存活；若 pre2 与 pre1 相当，说明效应是「长假前一周漂移」而非「最后一日冲击」。
4. **null 家族**：200 个随机信号 beat6m_rate 分布 p95 落在 [0.50, 0.53] 带（W16-W21 同带），高于 0.55 视为面/配置异常。
5. **成本段**：h≥2 的年度成本 ≤0.06%（单臂），远低于月度切换 3.14%/yr；若实测成本段与此不符，先查切换次数口径再判读数。
6. **极端窗**：2015-07 救市 / 2016-01 熔断 / 2020-02 疫情三段落在 holiday 窗附近，预计个别格回撤触及 -15% 描述线（记录不阻断）。

## §6 产物

- 格面 derive：`scripts/w22_prereg_derive.py`（selftest 13/13，hermetic 零面板零网络）→ `results/trial_labor_w22/w22_grammar.json`（sha16 `ac29b0715bcbbe06`）
- runner（冻结时落地）：`scripts/trial_labor_w22.py`（selftest + burn）
- 语法面：`results/trial_labor_w22/w22_grammar.json`（已生成，DRAFT 态）
- 格面：`results/trial_labor_w22/w22_candidates.json`
- screen：`results/trial_labor_w22/w22_screen.json` + `w22_screen_cells.csv`
- judge（若开）：`results/trial_labor_w22/w22_judge.json` + `w22_reform_face.json`
- 台账：`TRIAL_GRAMMAR_LEDGER` wave-22 行（generate 同窗 append）
- 本文 §7/§8 跑后回填

## §7 跑后实证

（跑前必须为空）

## §8 批后复盘

（跑后回填：预测对账 + 门禁链损耗账 + 判据 v2 读数 + 全起点分解 + 试验量归因）