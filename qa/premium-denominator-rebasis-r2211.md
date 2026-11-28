# qa — 溢价腿分母换基（r2211 bm-c）

## 本轮修的缺陷（r2210 已定谳的 P0）

`results/etf_premium/PREMIUM-2026-11-27.json` legs[4] 159519：

- 修前：`trust: iopv+same-day-nav` + `nav_session: 2026-11-26` + `premium_pct: -0.7305` + `over_nav_cny: -635.17`
- 实况：该行的分母（sina 11-27 快照里的 1.6974）是 11-26 的净值；净值板 11-27 已公布 **1.7010**
  （本轮 `ak.fund_etf_fund_daily_em()` 实取：159519 `2026-11-27-单位净值 = 1.7010`，
  159655 `2026-11-27-单位净值 = ---`）。
- 修后：`trust: nav-rebased-same-day`，`nav_session: 2026-11-27`，`denominator_nav: 1.7010`，
  `premium_pct: -0.9406`，`over_nav_cny: -817.83`，板面原读数保留在
  `board_reading{raw_premium_pct: -0.7305, raw_nav: 1.6974, raw_nav_session: 2026-11-26}`。
- 159655（无当日公布净值）保持 `unverified` / 无金额，并进了 `denominator.legs_lagging` 披露列。

## 判据与验收

| 检查 | 命令 | 结果 |
|---|---|---|
| 生产者自检（含 3 条新行为腿 L15b/L15c/L15d） | `python scripts/etf_premium_face.py selftest` | **49/49 PASS** |
| 全场 premium 站点日期可定位 | `python Tools/premium_session_guard.py` | 27 面，0 undatable |
| 逐腿分母会话审计（本轮缺陷的发现者） | `python Tools/premium_leg_session_audit.py --check` | **rc0**，27 面 / 146 腿 / 零红（修前 1 RED = MONEY_ON_FOREIGN_NAV） |
| 审计工具自检 | `python Tools/premium_leg_session_audit.py --selftest` | 15/15 |
| 面重渲染（无网络路径） | `python scripts/etf_premium_face.py render` | rc0，5 腿全印 |

## 未验/未做（如实）

- 全量 `smoke_test.py` 本轮未跑：本机 `Tools/s6_chain_bmc.py 2209` 自 09:04 起在飞（10:09 时 133/415 腿），
  整跑会读到被链改写中的共享面（r1861 UNVERIFIED 族），且 r2210 遗留 33 条红未收。
- `results/etf_book_premium_choice.json` 仍印 -635.17：它是本面的**下游**（链腿 ~207，本场未到），
  会随链重生于修正后的面；本轮不手改下游面。
- 未做的是「净值板与 sina 同日净值不一致」的另一族（513690：板 1.1161 vs sina 1.1137，同日两个值），
  与本缺陷同族但不是同一判据，留给下一轮。
