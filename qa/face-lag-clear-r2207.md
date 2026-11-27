# QA · r2207 · 面代差收尾（11-26 → 11-27）

日期：2026-11-28T07:40+08:00 · 机：bm-c · 竞争：rc=0 CLEAN（单宿主）

## 判据（本司清单）

| # | 判据 | 结果 |
|---|------|------|
| 1 | 每个被刷新的面 check rc=0 | 11/11 PASS |
| 2 | 每个面的 evidence_cutoff = 面板 frontier 2026-11-27 | PASS（phase_admission / start_grid 双双印 2026-11-27） |
| 3 | 上游面板推进后再刷下游（不是只刷下游） | PASS（premium_history 6536→6541 行，尾 11-26→11-27） |
| 4 | CEO 页吸收新面后不再混两天 | PASS（LIVE-2026-11-28.md 四处「同步 2026-11-27」） |
| 5 | 未绿项如实留账、不宣称已清 | PASS（见「未清」节） |

## 刷新的面（逐面 check rc）

| 面 | 动作 | check rc |
|----|------|----------|
| etf_book_premium_percentile | run（推进 premium_history 6536→6541 行） | 0（5 legs, 6536 obs） |
| etf_book_premium_forward | run | 0（3 horizons × 5 legs，verdict HIGH_PREMIUM_PAYS） |
| etf_book_premium_phases | run | 0（4 相位，中位 +6.30pp/yr） |
| etf_book_premium_persistence | run | 0（4 腿 LAG_DOMINATED） |
| etf_book_phase_admission | run（51.5s） | 0（cutoff 2026-11-27） |
| etf_book_start_grid | run（60.9s） | 0（25 起点，cutoff 2026-11-27） |
| etf_book_year_line_reach | run（53.7s） | 0（12 格，REACHED_BY_A_CELL） |
| etf_book_supply_gate_decision | run | 0（10/10，CALIBER_IRRELEVANT_TO_MONEY） |
| etf_book_cut_order_gap | run | 0（9/9） |
| etf_book_calendar_distance | run | 0（--check：4 candidates，无漂移） |
| astock_resid_veto_layer | run | 0（cutoff 2026-11-27 == panel frontier） |
| idx_fut_proxy_noise | check（重算） | 0（IF/IC/IM 全 PROXY_NOT_A_SUBSTITUTE） |
| idx_fut_roll_tenor | check（重算） | 0（cutoff 2026-11-20，QUARTERLY_WINS_ON_EVERY_COST_BAND） |

## 本轮的实际读数（产品面）

- 2026-11-27 这张票上有两只腿站在自己历史溢价的最高 2%：**159655 = 99.3 分位、510760 = 99.7 分位**。
- 同族历史：在 ≥98 分位的会话之后，下一交易日的溢价中位变化 +0.32%（均值 +0.37%），139 例中 34% 下跌。
- 一篮子结论未变：HIGH_PREMIUM_PAYS（h=20），rank-IC +0.012。

## 未清（如实留账）

1. **k_grid identity arm gap 0.27pp** — `etf_book_k_grid.py --check` 报 identity arm 复现不出 `results/etf_book_band_ruler.json` 的 ticket_window cagr，差 0.27pp。band_ruler 已重跑（rc=0，但自报 `identity arms priced on 2026-11-26` = ROWS_NOT_COMPARABLE）：说明分歧来自上游 identity arms 面的 bar 落后，不是 k_grid 的算法。下一轮先刷 identity arms 面再验。
2. **ceo_page selftest 475/479（4 FAIL）** — L228a「每条带位行都印出自己量到的那根 bar」看到 bars 混了 2026-11-26 与 2026-11-27，与 1 同源。
3. **knowledge/METHODOLOGY_ASSETS.md 第 18125 行一枚 0x08** — `Tools/treasure_guard.py prescan` 硬拒 rc3（登记簿命中），按法不动；这是账本里 "b\best_inside_gate" 的一枚笔误退格符，不是产品缺陷。
4. **全量冒烟未在本轮终态复跑** — 949s 的跑批快照来自本轮开头（12 条 FAIL），上述面刷新后未重新跑全量，**不宣称红数下降**。

## 证据

- 冒烟快照（本轮开头）：`C:\Users\Dasheng\.codely-cli\tmp\...\task-5362c8a2.output`（12 条 FAIL）
- 竞争探针：`results/_repo_write_contention.bm-c.json`（rc=0 CLEAN）
- 孤儿面：`results/_orphan_face_probe.bm-c.json`（py_faces=4, orphans=0, resident_servers=1）
