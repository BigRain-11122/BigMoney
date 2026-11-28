# QA · r2215 · 溢价面的日期证据（label ≠ proof）

轮号：2215（2026-11-28，bm-c）
产物：`scripts/etf_premium_face.py`（+`results/etf_premium/PREMIUM-2026-11-27.{json,md}` 重渲染）

## 缺陷

`leg_face()` 判「这一腿的分母是不是本场」只用 `nav_session` 一个字段，而该字段是**整批一个抓取戳**。
r2213 已把真相量出来：同一张 `2026-11-27` 标签下 1,439 行可判日，其中 1,371 在当日价格路径上、
**8 行实际在昨收**、59 行越界。溢价的执行闸与 CNY 金额全部建立在这个判断上。

## 修法（四个状态，各有一条行为腿）

| 证据情形 | 现在的行为 | 腿 |
|---|---|---|
| 路径证明在当日 | 照旧 `iopv+same-day-nav`，页面标「路径证明在当日」 | L41 反例 / L46 |
| 路径说昨日而标签说当日 | **路径赢**：改按跨日处理，有本场公布净值则换基，否则无 CNY | L41 / L42 |
| 路径判不了日（价动 <1%） | 数照印、CNY 照算，标 `label-only` 并把歧义幅度 `date_ambiguous_pp` 印出 | L43 |
| 定日面缺件 / 属于另一场 | 退回旧行为并分别点名 `no-evidence-face` / `evidence-face-other-session` | L44 / L47 |
| 板面没有这一腿 | 表里点名另一源带日期的净值，且不拿它定价 | L45 |
| 页面 | 必须印「分母日期证据」分类行并逐腿点名 | L46 |

## 验证（本机实跑，2026-11-28）

- `python scripts/etf_premium_face.py selftest` → **56/56 PASS**（新增 L41–L47 七条行为腿）
- `python scripts/etf_premium_face.py render` → 重渲染 `results/etf_premium/PREMIUM-2026-11-27.md`
  - 票面 5 腿：2 腿路径证明在当日（510760 / 512040）、3 腿只算标签（159655 价动 2.83%、513690 −0.72%、159519 换基后仍 −0.30%）
  - 页面新行：`分母日期证据：本单 5 腿里，价格路径证明在当日 2 腿、…、按本场公布净值换基 1 腿、路径判不了日 3 腿`
- `python Tools/premium_leg_session_audit.py --check` → rc0，27 面 / 146 腿零红
- `python Tools/s6_chain_bmc.py 2215 --only=etf_premium` → 1/1 rc0（周六 no-op）
- `python scripts/attrition_ledger_guard.py scan` → CLEAN（4 账本 3 历史缩行 healed）
- `python scripts/pool_dualrun_reconcile.py run` → ZERO-DRIFT（747 条，streak 51）

## 未做（如实记）

- 全量冒烟未跑（~950s，超出单轮预算；且链会中途重写共享面）
- 执行闸仍只按金额说话，`label-only` 的腿在闸的口径里未被单独点名（下轮）
