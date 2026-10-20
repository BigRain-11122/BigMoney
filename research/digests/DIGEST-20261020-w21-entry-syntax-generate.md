# DIGEST 2026-10-20 — TRIAL-LABOR-W21 供料批（条件化入场语法 GENERATE）

**轮次**：bm-b r1077（2026-10-20T17:02–17:28+08:00）
**队列出处**：`state/queue/explore.md` E18（r1076 登记）→ 本轮 done-flip
**上游供给面**：E21 leg-3 条件化隔夜普查 `results/overnight_gap_census/LEG3-2026-10-19.json`（sha16 `c3eecf0facec0c85`）
**判据**：`science_gates.g1_prime_v2` / `g2_registration_v2` / `deflated_sharpe_ratio` / `m1_t_value_gate`（禁手抄）

## 一、本批做了什么（可跑/可查实物）

| 面 | 路径 | 状态 |
|---|---|---|
| runner | `scripts/trial_labor_w21.py` | selftest 21/21 hermetic |
| 预注册 | `research/TRIAL_LABOR_W21_PREREG.md` | FROZEN（banned gate ADMIT rc0） |
| 语法面 | `results/trial_labor_w21/w21_grammar.json` | sha16 `08259059b9302e69` |
| 格面 | `results/trial_labor_w21/w21_candidates.json` | 18 格 + fingerprint/mask_days census |
| 预算面 | `results/trial_labor_w21/prep_state.json` | 1,253 starts + passive 6m |
| 算力面 | `results/runnable_pool.json` | `TRIAL-LABOR-W21-SCREEN-SHARD-0..3`（ready，lane bm-b） |
| 台账 | `TRIAL_GRAMMAR_LEDGER` | wave-21 行已 append |

## 二、三个新族（机制来自 E21 leg-3 实测，不是拍脑袋）

1. **`liq_rank_gate`（8 格）** — 自身成交额 250 日相对分位跨阈（0.60/0.70/0.80/0.90 × level/onset）。
   出处读数：隔夜收费随自身流动性分位单调放大，q1 −1.93bp → q5 −19.36bp/bar（10.0×，t −37 vs −211）。
2. **`gap_reversal_gate`（4 格）** — 隔夜跳空 ≤ −{0.5%,1%,2%,3%} 的次日入场。
   出处读数：gap<−2% 次日隔夜腿 −44.65bp（中性桶 −5.09bp），且是全 gap 桶中唯一次日 NET 为负者。
3. **`on_share_rank`（6 格）** — 自身「隔夜占比」250 日分位 ≤ {0.20,0.35,0.50}（n=20/60）。
   出处读数：隔夜淤血与持有期线性（H=1/5/20 均 ≈ −8.9bp/日，不会在持有期内洗净）。

**单执行配置**：X=template_default / S=equal_weight / T=daily_signal + 16 轴 none——入场 mask 是唯一被测维度（W17/W18/W19 三轴消费红利）。K=200 同构随机 null ⇒ 218 screen trials。

## 三、闸门实况（全过）

- T-18 队头探针 **CLEAR**；T-19 seed gate hits=[] rc0。
- `seed_admit_gate` base=20660000 span=1500 **FREE**；三带登记 20660000/20660500/20661000。
- `banned_direction_gate`：命中 **BAN-03 / BAN-04** → 按例外通道申报后 **ADMIT rc0**（回执 `results/_r1077bmb_banned_gate.json`）：
  - BAN-03（5/10/20 日单名反转/动量）**部分真实命中** → `new_mechanism`：原否证面没有隔夜/日内收益分解，E21 leg-3（15.1M obs）是 2026-10 才存在的新证据面；本批仍为零宣称供料 census。
  - BAN-04（网格交易）字面误报：本件「网格」= census 枚举网格，无阶梯加仓/摊平。
- G-ROSTER（vs W16 58-fn 名册 + W20 31 格名册）零交集；G-SEEDS 带净；G-LINEAGE 五锚（W14/W16/W17/W18/W20）逐位一致。
- **G-LEG3ANCHOR**（本批独有身份门）：leg-3 文件 sha16 + 两枚头条读数逐位相等，且 `_liq_rank` 与 leg-3 自相对分位的一阶原理在探针面 3,483 行上**逐 bar 全等**（零容差）；18 格指纹全唯一。

## 四、诚实面

- 上游读数取自 2026-10-19 面板，本批回测在 leg-L 冻结面 **cutoff 2026-09-22** 上跑——上游是机制出处，不是回测数据（预注册 §2 已披露）。
- screen 是算力批（>5min），按 O-20260924-2100 执行面分离入池，**轮内零引擎格烧**；本件不含任何判据结论。
- 强赎/涨跌停/停牌等可交易性约束在 screen 阶段不建模（沿用 W16-W20 口径），judged 面若开须另过出场轴显式门。

## 五、下一步

screen 4 分片 → `screen-finalize`（生存线 + 家族 axe）→ `judge-prep`（家族块 + 双 null B=2000/P=2000）→ judge → intake。
预测（已冻结在预注册 §5）：liq onset 高阈 1–3 格存活、gap 深阈 0–2 格且大概率 G1' 不过线、onshare 0–1 格、null p95 落 [0.50,0.53]。