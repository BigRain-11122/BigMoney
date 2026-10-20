# TRIAL_LABOR_W21 — 条件化隔夜/入场语法 GENERATE 供料批

> 批号：TRIAL_LABOR_W21（wave-21 entry-syntax GENERATE regression batch）
> 部门：dept:研究+工程
> 冻结窗：bm-b r1077（2026-10-20）；本件冻结 = runner `scripts/trial_labor_w21.py` 的 G-GRAMMAR pin 与种子登记同窗一步（R250 一阶律）
> 队列出处：`state/queue/explore.md` E18 行（TRIAL-LABOR-W21 供料批，r1076 bm-b 登记，T-19 seed gate rc0）
> 上游供给面：E21 leg-3 条件化隔夜普查 `results/overnight_gap_census/LEG3-2026-10-19.json`（sha16 `c3eecf0facec0c85`）+ leg-1/leg-2

## §0 批件身份

- 批名/批号：TRIAL_LABOR_W21；格数 18（census 全枚举 8+4+6）＋ K=200 同构随机 null = 218 screen trials（每格计入 N_eff）。
- 认领：本轮 bm-b r1077 登记+认领同轮（T-18 队头探针 CLEAR；T-19 seed gate hits=[] rc0）。
- 算力预算：screen 218 格 × leg-L 单配置回测，分 4 分片入 `results/runnable_pool.json`（每片 <5min/核），CPU-only，≤8 worker（核数 16，余量律 10% 保留）。批报告必带 audit 段。
- 判据库：`science_gates.g1_prime_v2` / `g2_registration_v2` / `deflated_sharpe_ratio` / `m1_t_value_gate` 共享库（禁手抄判线）。
- 出场轴显式声明（O-20261001-1108 三选一）：**③ template_default** —— 引擎缺省出场栈按设计测（X=template_default 为 W17 消费面，本批唯一测试维度=入场 mask）。

## §0.5 禁开方向硬闸

- 跑前闸：`python Tools/banned_direction_gate.py --prereg research/TRIAL_LABOR_W21_PREREG.md`（回执 `results/_r1077bmb_banned_gate.json`）。
- 命中编号：**BAN-03、BAN-04**（字面模式命中；逐条裁定如下）
  - **BAN-04（Grid trading）**：命中类型 = 字面误报。本件「网格」一词全部指 **census 枚举网格**（18 格全枚举），不是 grid trading——本批无阶梯加仓、无固定买卖带、无摊平补仓；每个格是把一个入场 mask 喂进引擎缺省出场栈的单变量 census。
  - **BAN-03（Single-name timing reversal or momentum at 5/10/20 days）**：**部分真实命中**——`gap_reversal_gate` 族确实机制化了「深跌 gap 后的反转入场」，故按例外通道申报。
- 例外类型：**new_mechanism**（同时携带 new_data 证据面）
- 原否证不可能看见的东西：BAN-03 的否证面（`docs/audits/retail-quant-conclusions-v2-20260930.md#3`）测的是 18 组 5/10/20 日动量/反转组合在 ETF 上的静态横截面期望，其数据面**没有隔夜/日内收益分解**。本次例外依据 = E21 三腿普查（2026-10 实测，15,110,598 obs / 5,199 文件）：①隔夜腿在全样本结构性为负且与持有期线性发臭（−8.9bp/日，H=1/5/20 不变），日内腿为正；②按自身流动性分位分层后隔夜收费单调放大 10 倍（q1 −1.93bp → q5 −19.36bp/bar）；③深跌 gap（<−2%）次日隔夜腿 −44.65bp，是全 gap 桶中唯一次日 NET 为负者。这三面在 2026-09-30 否证时**不存在**（leg-3 盘 2026-10-20 才落地），因此「反转在 5/10/20 日无正期望」不等于「隔夜折价在 1 日事件桶上不可捕获」。
- 本批仍为**零宣称供料 census**（18 格 + 200 null 全枚举、判据照 v2 门禁跑）；例外申报只用于取得开烧资格，不构成任何正期望主张。若 screen 全军覆没，则该方向按负发现收口并入 EXCLUSION_BOOK。

## §1 α 机制段

- [x] **行为偏差 + 微观结构（复合，单一批内分族）**
  - **liq_rank_gate（流动性态门）**：当个股成交额在自身 250 日窗内的相对分位跨过阈值，代表注意力/参与度进入 episode。E21 leg-3 实测：overnight 收费随自身流动性分位单调放大（q1 −1.93bp → q5 −19.36bp/bar，q5/q1 = 10.0×，t −211 vs −37），即「高流动性状态下持仓的隔夜代价是低流动性状态的十倍」——这是流动性状态对隔夜风险的定价，谁在隔夜承担了流动性风险谁收租，散户在日内了结即可避开。
  - **gap_reversal_gate（深跌 gap 反转门）**：隔夜跳空 < −2% 的次日，overnight 腿 −44.65bp（vs 中性桶 −5.09bp），且是全 gap 桶中唯一次日 NET 为负者（−8.27bp）——跳空深跌=被迫卖方在开盘集中出清，隔夜端把折价一次性释放；该项测的是「深跌后次日开盘接回」的可捕获腿。
  - **on_share_rank（隔夜占比秩门）**：leg-1/leg-2 证明隔夜淤血与持有期线性（H=1/5/20 均 ≈ −8.9bp/日，不会在持有期内洗净或反转）；个股自身「隔夜占比」在 250 日窗内排序低 = 该名的收益主要在日内赚到，持有它付的隔夜税更低，因此作为名级 toll-avoidance 选择面。
- **散户凭什么赢**：本批不赌速度/数据/容量，赌**行为与结构**——机构在隔夜承担流动性风险以换取日内择时/规模，散户可以日内了结、可以按自身流动性状态让路、不承担被迫卖方的隔夜折价；三个族都不需要盘中信息、不需要融券、不需要 T+0，只需 T+1 收盘/开盘执行。
- **同族相关性准入（D6）**：三族机制命名空间 runner-native（`w21_lq` / `w21_gp` / `w21_on`），与 W16 58-fn 冻结名册、W20 31 格名册零字面交集（G-ROSTER 三闸 live 复跑）；与在册交易员日收益相关 max|corr| 在 screen 后按族合并前实测申报（>0.7 拒收）。

## §2 数据与面板

- 宇宙/池：leg-L core48（`p5c_virtual_timepoint._load_leg("L")`，与 W16/W17/W18/W19/W20 同面），成员 48，`G-PANEL` live 断言。
- **数据锚面四元组**：
  - 主面板 = `data/daily/*.csv` 本地 ETF/指数 CSV 池 → `live.paper.load_core` → `_load_leg("L")` → 起算窗 `LEG_L_FLOOR` → 预热窗 `WARMUP_TD`。
  - 探针面（G-510300-FACE）= `data/daily/sh510300.csv` → raw `pd.read_csv` 直读截断 CUTOFF → 3,483 行，首行 2012-05-28。
  - 上游条件化事实 = `results/overnight_gap_census/LEG3-2026-10-19.json` → `open()` + `json.loads` 全文件读 → 证据面 cutoff 2026-10-19（**口径披露：上游读数取自 2026-10-19 面板，本批回测在 leg-L 冻结面 cutoff 2026-09-22 上跑——上游是机制出处，不是本批回测数据**）。
- **探针-锚同面断言**：`_leg3_anchor_gate` 逐位复核 ①leg-3 文件 sha16 与两枚头条读数（gap<−2 r_on = −0.00446465 / liq q1 r_on = −0.00019276） ②`_liq_rank` 与 leg-3 自相对分位的一阶原理逐 bar 相等（探针面 3,483 行上全命中，零容差）。一面不相等 = 面错配 VOID。
- 窗口律：`evidence_cutoff = 2026-09-22`（`tl1.CUTOFF`，P-5C 绑定），cutoff 后新 bar 锁定不回流；产物顶层带 `science_gates.cutoff_meta(CUTOFF)`。
- 数据完备门：G-PANEL（48 成员、末行 == cutoff、五列齐）＋ G-EXITCFG（A9 引擎缺省表）＋ G-ROSTER/G-SEEDS/G-LINEAGE/G-LEG3ANCHOR 全过才生成/开烧。

## §3 方法学

| family | 定义（frozen） | 网格 | 格数 |
|---|---|---|---|
| `liq_rank_gate` | `liq_pct(t)` = amount(t) 在自身 250 bar 窗内百分位（min 60）；mask = `liq_pct >= thr`（mode=level）或其严格 onset（mode=onset） | thr ∈ {0.60,0.70,0.80,0.90} × mode ∈ {level,onset} | 8 |
| `gap_reversal_gate` | `gap(t) = open(t)/close(t-1) − 1`；mask = `gap <= -depth` | depth ∈ {0.005,0.01,0.02,0.03} | 4 |
| `on_share_rank` | `share(t) = mean_n(on) / (mean_n|on| + mean_n|in|)`，on = open/prev_close−1，in = close/open−1；share 在自身 250 bar 窗内百分位；mask = `rank <= thr` | n ∈ {20,60} × thr ∈ {0.20,0.35,0.50} | 6 |

- **单执行配置**（全部 18 格 + 200 null 相同）：`R=engine-default, X=template_default, S=equal_weight, T=daily_signal, 其余 16 轴 none`——入场 mask 是唯一被测维度（X/S/T 三轴消费红利：W17/W18/W19 三代已消费）。
- 滞后规则：全部信号只用 t 日及以前的收盘/开盘/成交额；entry 落在 t+1 引擎语义（无未来数据）。
- null 对照：K=200 同构随机信号（同网格同配置，rng `[20660500, i]`，p_on regime 先抽后同流抽信号矩阵）；gen 种子 `20660000` 全程 HELD 零消费（census 全枚举，零抽样零选择自由度）。三带：`20660000/20660500/20661000`，带 [20660000, 20662500)，`seed_admit_gate rc0 base=20660000 span=1500 verdict=FREE`（registry+rg scanned free）。
- 成本口径：引擎 V1 legacy 单边 `ce_transfer.COST_X1_RATE` = 13.041bp×2 往返（ETF/指数面统一，波段 ETF 口径）；股票面另计印花税不适用本批（core48 池为 ETF/指数）。
- 账本：`science_gates.append_ledger("TRIAL_LAB_W21_SCREEN", 218, ..., evidence_cutoff=CUTOFF)`。
- **闭合族对号（M3）**：`family_key=TRIAL_LABOR` 不在 `science_gates.CLOSED_FAMILIES` → open 照跑（G-GRAMMAR 内 `in_closed=false` 断言）。

## §4 判据（跑前写死，禁看结果调线）

- **G1' v2** = `science_gates.g1_prime_v2(sharpe_full, returns, batch_cells, n_trades, n_entries)`：全期 Sharpe > skill_line_v2（数据驱动 max(被动+0.10, μ_null+σ_null·√(2·ln N_eff))）**且** 平稳 bootstrap CI 下界 > 0 **且** entries ≥ 10。
- **G2 注册资格 v2** = `science_gates.g2_registration_v2(g1_pass, dsr, pbo)`：G1' 过线 **且** DSR ≥ 0.95（原始收益跑 `deflated_sharpe_ratio`）**且** 家族 PBO ≤ 0.25（CSCV 8 块）。
- **M1 t 面**：新因子族必须有 t 统计面（`t_from_sharpe` 派生，批内申报 SR_ann 与 T）；判据 `science_gates.m1_t_value_gate`（t ≥ 3.0）；缺 t = missing_input 拒收。
- **screen 生存线**（批内既有语法）：`beat6m_rate` vs 同起点被动基线（`>=` 字面），k/n + binom_z/p 全披露；家族级 axe=族内至少 1 格过线才整族进 judge（块完整性律）。
- 描述性条款（批级披露，不替代 v2 门槛）：年化为正、回撤 ≥ −35%、成本 ×2 压测、无崩年。

## §5 跑前预测（写死于跑前）

1. **liq_rank_gate**：存活格 1–3 个，且集中在 onset 模式高阈（0.80/0.90）——level 模式会把整个高流动性区间当信号、稀释成持仓噪声，onset 才对上「episode 起点」的行为语义。
2. **gap_reversal_gate**：深度 0.02/0.03 两格最可能存活，0.005 格预计信号过密（接近日均噪声）→ beat6m 接近 0.5；族级预测 0–2 格存活，且即使存活也**不期待** G1' 过线（E14/E20 同型结论：可捕获腿被成本吃穿）。
3. **on_share_rank**：最弱族，预计 0–1 格存活——名级隔夜占比是慢变量，6m 窗口内区分度低；若撞上则说明隔夜税可作选股维度（需另开 judged）。
4. **null 家族**：200 个随机信号 beat6m_rate 分布 p95 落在 [0.50, 0.53] 带（承 W16-W20 同带观察），高于 0.55 则视为面板/配置异常信号而非null 噪声。
5. **极端日先验**：本批数据窗（leg-L 起算窗至 2026-09-22）含 2015-07 救市（510300 涨停锁价）、2016-01 熔断、2020-02 疫情跳空——gap 族在 2015/2016 段会命中极端 gap，预计个别格回撤触及 −35% 描述线（记录不阻断，v2 门槛才是判据）。

## §6 产物

- runner：`scripts/trial_labor_w21.py`（selftest 21/21，hermetic 零面板零网络零 burn）
- 语法面：`results/trial_labor_w21/w21_grammar.json`（sha16 见 §7 回填）
- 格面：`results/trial_labor_w21/w21_candidates.json`（18 格 + fingerprint/mask_days census）
- screen：`results/trial_labor_w21/w21_screen.json` + `w21_screen_cells.csv`
- judge（若开）：`results/trial_labor_w21/w21_judge.json` + `w21_reform_face.json`
- 台账：`TRIAL_GRAMMAR_LEDGER` wave-21 行（generate 同窗 append）
- 本文 §7/§8 跑后回填

## §7 跑后实证

（跑前必须为空）

## §8 批后复盘

（跑后回填：预测对账 + 门禁链损耗账 + 判据 v2 读数 + 全起点分布 + 试验量归因）