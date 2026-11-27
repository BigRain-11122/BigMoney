# QA · carry-entry-window-yield · r2196 (bm-c)

日期：2026-11-28 01:0x +0800 · 审判面：`results/carry_entry_window_yield.json`
页面：`results/carry_entry_window_yield.md` + `research/CARRY_ENTRY_WINDOW_YIELD.md`
脚本：`scripts/carry_entry_window_yield.py`

## 判据清单

| # | 判据 | 证据 | 结果 |
|---|---|---|---|
| 1 | 面可生成（rc0） | `python scripts\carry_entry_window_yield.py` → headline `THE_CARRY_BOOK_CARES_LESS_ABOUT_WHEN_YOU_START_THAN_THE_ETF_BOOK`，rc0，用时 0.8s | PASS |
| 2 | 自检全绿 | `selftest` → **31/31 PASS** | PASS |
| 3 | 漂移守卫可用 | `check` → `{"ok": true, "notes": [], "diffs": []}` rc0 | PASS |
| 4 | **复现腿 basis** | 父面窗口 2017-01-18..2026-11-25 · 2390 bar：sharpe 2.972 / cagr 10.069 / vol 3.2463 / mdd -1.8896 / days 2390 五项逐位 = `idx_fut_carry_kill_rule_economics.products.IC.baseline` | MATCH |
| 5 | **复现腿两臂** | 2018-10-22..2026-11-20 · 1961 bar：对冲残差 **1.4162**、不带对冲 **0.5057** 逐位 = `idx_fut_carry_search_rent.cells` | MATCH |
| 6 | 复现失败即不发布 | 两条复现腿任一 MISMATCH → `judgement.headline=UNREADABLE` 且 exit 2（main 分支实装） | PASS（代码路径；本样本 MATCH） |
| 7 | 双臂日序列的日期对齐 | 两臂序列长度 1961 = 父面窗口日期 1962 − 1（锚日不产收益）；不等即 return None → 不发布（禁按行号猜） | PASS |
| 8 | 同一把尺 | 三条线统一换成「一手资本日分数」：basis=名义额收益率；两臂=点数×200÷1,137,862.5 | PASS |
| 9 | 执行口径与 r2195 一致 | `entry_lag=1`（起点收盘决策、i+1..i+h 持有）；selftest 腿 `entry_lag` 断言 `to == dates[244]` | PASS |
| 10 | 求和口径 vs 复利口径不混用 | selftest：同批窗口 simple 求和 2.44 vs compound 1.01^244−1=10.3348 两条腿分别钉死；复利读数只对 basis 印 | PASS |
| 11 | 重叠窗口不称独立 | 分布只描述起点；另印不重叠整年块（basis 9 块 / 两臂各 8 块），未声称 p 值 | PASS |
| 12 | **排序量必须对得上 r2192** | 按窗内 Sharpe 排（与 1.4162/0.5057 同一量）：basis>对冲残差>不带对冲 **83.46%**（1433/1717）；按钱排 **24.34%** 且主导排序翻成 `carry_unhedged>basis>excess` | PASS |
| 13 | 两种排序并列印 | `ordering.money` 与 `ordering.sharpe` 双面 + `why_two_orderings` 说明；selftest 腿 `money_vs_sharpe_differ` 用合成序列证明二者可相反 | PASS |
| 14 | 输入字节动 = STALE | selftest 行为腿 `classify_stale`：改 inputs_digest → 含 `STALE` | PASS |
| 15 | 改判词 = CHECK FAILED 且不带 STALE | selftest 行为腿 `classify_check_failed` | PASS |
| 16 | 改读数 = CHECK FAILED | selftest 行为腿 `classify_number_drift`（改中位 8.0→8.5） | PASS |
| 17 | 元数据不算漂移 | selftest 行为腿 `volatile_fields_ignored`（generated/sources 改掉仍 ok） | PASS |
| 18 | check 锚在外部字节 | `inputs_digest` 含六张源面 sha256 + `data/daily/sh510300.csv` 尾 bar 日期；不复用自家算术 | PASS |
| 19 | 零网络零重测 | 只跑本地 `CS.replay` / `CP.position_series` / `CP.per_lot_daily` + 读六张已发布面 | PASS |
| 20 | 不改任何已发布面 | 只写 `results/carry_entry_window_yield.{json,md}` + `research/CARRY_ENTRY_WINDOW_YIELD.md` | PASS |
| 21 | 跨书比较不越界 | ETF 读数只取 r2195 已发布值；明写绝对 pp 跨书不可比（波动不同），可比的是 spread/median 与亏钱起点占比 | PASS |
| 22 | 不可买的线不冒充可执行 | `basis_nominal` 每表每节都标 r2190 不可买，只作参照 | PASS |

## 本轮读数（cutoff 2026-11-26 · IC · 一年 = 244 bar）

| 线 | 起点数 | 中位 | p10 | p90 | 最差 | 最好 | 亏钱起点 | p90-p10 | 跨度/中位 | 路径回撤中位 | 最深 |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| basis_nominal（不可买） | 2147 | 9.64% | 5.49% | 14.76% | 3.34% | 16.55% | 0.0% | 9.27pp | 0.96x | -1.14% | -1.9% |
| excess_hedged（可买） | 1717 | 8.61% | 3.23% | 14.48% | -1.31% | 17.04% | 0.1% | 11.25pp | **1.31x** | -2.32% | -6.4% |
| carry_unhedged（可买） | 1717 | 16.61% | -11.96% | 41.22% | -33.2% | 68.97% | 27.1% | 53.18pp | 3.20x | -17.62% | -46.67% |

- 排序（窗内 Sharpe）：`basis > 对冲残差 > 不带对冲` **83.46%**（1433/1717），翻转 284 窗全是「不带对冲 > 对冲残差」
- 排序（窗内钱）：`不带对冲 > …` 占 62%，canonical 仅 24.34% → 钱排序被波动放大，不能拿来比 r2192
- 与 ETF 书同一把尺：carry 对冲臂 **1.31x** vs ETF vt08 **3.56x**；亏钱起点 0.1% vs 5.6%

## 自捕（本窗实弹）

1. **首版拿「钱」的排序去比 r2192 的「Sharpe」排序**，得出「排序只在 24.34% 的窗口成立」这一假矛盾——r2192 量的是风险调整收益，钱会被波动放大；已改为双量并列（Sharpe 83.46% / 钱 24.34%），并加合成序列行为腿把这条钉死。这正是 r1934「判据词是合同」的同一族坑：比之前先问「对面对的是哪个量」。
2. `check` 首跑把自己内部的 `_reads`（发布时 pop 掉）算成 30 处漂移 → 假 CHECK FAILED；已把 `/_reads` 列入 volatile，复跑 rc0。
3. 页面首版把 `worst_decile_start_months` 的 Python dict repr 直接印给读者（`{'2023-03': 22}`），已改为 `2023-03×22 / …`。
