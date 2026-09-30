# D-20260930-27 Q4 marks 瘦身落地简报（r480 · bm-a）

**修前 vs 修后对账（审计 Q4 判据 · 逐日实测）**

| 日 | ticks | 修前全量落盘 | 修后可抑制 | 抑制率 |
|---|---|---|---|---|
| 2026-09-28 | 3 | 3 | 2 | 67% |
| 2026-09-29 | 1 | 1 | 0 | 0% |
| 2026-09-30 | 62 | 62 | 60 | **97%** |
| 合计（3 日窗） | 66 | 66 | 62 | **93.9%** |

审计 Q4 单日读数 410/475（86%）与本探针 93.9% 同向（本探针=逐交易员口径：任一交易员 ≥5bp 即保留，比审计口径更保守的抑制面更窄，实测反而更高=噪声更重）。

**保留律（一条不丢证据面）**——以下 tick 恒落盘，永不抑制：
- 首 tick（当日锚：session_open 开盘价证据=T-35 d2-c 开盘成交验证的取数面）
- settle 面（15:00 结算恒写，幂等门 `_settle_done` 不变）
- 状态变化（cash/持仓 symbol/quantity/cost_price/pending_watch 任一变动）
- 任一交易员权益变动 ≥5bp（审计 Q4 阈值）
- unpriced 面（未定价持仓/权益锚缺失=证据面，恒保留+披露）
- `--force` 操作员显式覆盖

**实现**：`scripts/update_intraday_marks.py` `_tick_redundant()` + `_last_written_tick()` + run() 写盘前门；selftest S10-S13 新例全过（PASS）；抑制=零写盘+stdout 一行留痕+rc 0（合法 no-op）。 suppressed tick 不落盘 → 下次比较基准=最后一张已写 tick（探针同语义）。

**诚实注记**：
1. 首次实弹抑制=下一交易日第二张 intraday tick（今日 16:2x 在窗外 no-op，无法当日实弹；selftest 7 例已覆盖门逻辑）。
2. 历史冗余行（已落盘 410/475 等）按 append-only 证据律**不回删**——瘦身只对新写入生效。
3. 审计面信噪比收益：按今日 97% 抑制率推算，marks 日增量 ~62 行 → ~2-6 行（首 tick+settle+状态/5bp 面）。

**探针**（决策数据件，确定性可重跑）：`results/_r480bma_q4_marks_slim_eval.py` → `results/_r480bma_q4_marks_slim_eval.json`（3 日窗 66 ticks 读数）。
