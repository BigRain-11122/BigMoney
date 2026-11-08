# ETF book -- after the swap, when do I have to look again?

session `2026-11-06` | ticket `TICKET-2026-11-06.json` | source `results/etf_book_sibling_gap.json`

**act on this bar: the one-off part of 8,222 CNY is unmeasured -- no comparable episode in the panel ever healed, so nothing here says the window waits. After execution the only number that can bring the decision back is the round-trip toll: re-read this face on the next decision bar, and act again only if a pair's gap exceeds 0.16 pp (2 x 8 bp per side).**

触发价 = 来回成本 0.16 pp（2 × 8 bp/边）。这不是分位数，是「再动一次要付多少」。

| 腿（书里持有） | 换到 | 今日价差 | 历史均值 | 一次性部分 | 可重复部分 | 超过触发价占比 | 这次尾部多久回均值 | 判词 |
|---|---|---|---|---|---|---|---|---|
| 159501 | 159513 纳斯达克100ETF大成 | +8.67 pp | +0.83 pp | ¥5,039 | ¥574 | 63% | — | **ACT_ON_THIS_BAR** |
| 513100 | 159513 纳斯达克100ETF大成 | +6.29 pp | +1.41 pp | ¥3,183 | ¥966 | 85% | 中位 22 次（1 例，1 未愈合） | **WINDOW_ALWAYS_OPEN** |
| 159577 | 513850 美国50ETF易方达 | +0.19 pp | -0.08 pp | — | — | 39% | 中位 3 次（27 例，1 未愈合） | **NOT_ACTIONABLE** |

- 159501 → 159513：this episode is a tail of the pair's own history and either heals inside one rebalancing grid or was never healed inside the panel -- the one-off part does not wait for the next decision bar
- 513100 → 159513：the pair trades wider than the round-trip toll on almost every session: this is a standing condition, so the swap is a permanent re-tickering and there is nothing to watch between decision bars
- 159577 → 513850：the gap does not clear the round-trip toll: swapping would pay more to move than it saves, so the trigger is the gap itself (re-read on the next decision bar)

## 读法

- 决策时钟和价差时钟是两块表。书每 20 个交易日重排一次，那一天换票会被重新决定；两次决策之间，唯一能动的是价差，所以真正的「再看一次」不是日历而是价格。
- 已经换过去的票不需要天天看：每一对的均值（159501→159513 +0.83 pp、513100→159513 +1.41 pp、159577→513850 -0.08 pp）就是「这只票历来更便宜多少」，只有它自己变成了贵的那一只、且价差越过来回成本，才需要再动。
- 「尾部多久回均值」是实测：拿每一次跟今天同等宽的价差，数它回到自己均值用了几个交易日；还没愈合的算作 censored 单独列出，不当 0 次。
- 出处：`scripts/etf_book_swap_trigger.py`；上游 `results/etf_book_sibling_gap.json`（同一份重建，不另算一遍）。

## 不能从这张面读出来的

- the trigger is priced in pp of notional and compared against the round-trip cost only; it does not price tracking difference, fee, size or FX-hedge policy between the two tickers
- episode lengths are measured on the reconstructed gap, which inherits the single IOPV anchor of the gap face; censored episodes are reported, never scored as zero
- a 'window always open' reading means the pair is structurally wide, not that the swap has to be repeated: the book only has to hold it once
