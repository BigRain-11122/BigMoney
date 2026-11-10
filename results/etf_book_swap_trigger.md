# ETF book -- after the swap, when do I have to look again?

session `2026-11-10` | ticket `TICKET-2026-11-10.json` | source `results/etf_book_sibling_gap.json`

**act on this bar: the one-off part of 6,170 CNY is unmeasured -- no comparable episode in the panel ever healed, so nothing here says the window waits. After execution the only number that can bring the decision back is the toll of the exchange it would have to make: re-read this face on the next decision bar, and act again only if a pair's gap exceeds 0.16 pp (2 sides x 8 bp). Getting the book back where it came from pays that same exchange once more, so the whole manoeuvre is 0.32 pp (4 sides) -- that number answers 'did the discount pay for the trip', never 'may I act'.**

触发价 = **换这一次**要付的过路费 0.16 pp（2 边 × 8 bp/边）。这不是分位数，是「今天再动一次要付多少」。整趟一来一回是 0.32 pp（4 边）——换回来还要再付一次，那个数只回答「这趟折扣够不够补回全部成本」，不当门槛（r1529/r1531）。

| 腿（书里持有） | 换到 | 今日价差 | 历史均值 | 一次性部分 | 可重复部分 | 超过触发价占比 | 这次尾部多久回均值 | 判词 |
|---|---|---|---|---|---|---|---|---|
| 159501 | 159513 纳斯达克100ETF大成 | +7.08 pp | +0.48 pp | ¥3,798 | ¥290 | 47% | — | **ACT_ON_THIS_BAR** |
| 513100 | 159513 纳斯达克100ETF大成 | +5.09 pp | +1.01 pp | ¥2,372 | ¥616 | 76% | 中位 21 次（2 例，1 未愈合） | **ACT_ON_ANY_BAR** |
| 159577 | 513850 美国50ETF易方达 | -0.13 pp | -0.15 pp | — | — | 31% | 中位 2 次（48 例，1 未愈合） | **NOT_ACTIONABLE** |

- 159501 → 159513：this episode is a tail of the pair's own history and either heals inside one rebalancing grid or was never healed inside the panel -- the one-off part does not wait for the next decision bar
- 513100 → 159513：the gap clears the toll of making the exchange (0.16 pp, 2 sides) but is not a perishable tail -- any bar inside the next grid may be used without paying for the delay (the whole manoeuvre is 0.32 pp (4 sides -- the unwind pays the exchange again))
- 159577 → 513850：the gap does not clear the toll of making the exchange (0.16 pp, 2 sides): swapping would pay more to move than it saves, so the trigger is the gap itself (re-read on the next decision bar; the whole manoeuvre is 0.32 pp (4 sides -- the unwind pays the exchange again))

## 读法

- 决策时钟和价差时钟是两块表。书每 20 个交易日重排一次，那一天换票会被重新决定；两次决策之间，唯一能动的是价差，所以真正的「再看一次」不是日历而是价格。
- 已经换过去的票不需要天天看：每一对的均值（159501→159513 +0.48 pp、513100→159513 +1.01 pp、159577→513850 -0.15 pp）就是「这只票历来更便宜多少」，只有它自己变成了贵的那一只、且价差越过来回成本，才需要再动。
- 「尾部多久回均值」是实测：拿每一次跟今天同等宽的价差，数它回到自己均值用了几个交易日；还没愈合的算作 censored 单独列出，不当 0 次。
- 出处：`scripts/etf_book_swap_trigger.py`；上游 `results/etf_book_sibling_gap.json`（同一份重建，不另算一遍）。

## 不能从这张面读出来的

- the trigger is priced in pp of notional and compared against the toll of ONE exchange (0.16 pp, 2 sides) only; the whole manoeuvre (0.32 pp, 4 sides) is published next to it and is never the threshold. It does not price tracking difference, fee, size or FX-hedge policy between the two tickers
- episode lengths are measured on the reconstructed gap, which inherits the single IOPV anchor of the gap face; censored episodes are reported, never scored as zero
- a 'window always open' reading means the pair is structurally wide, not that the swap has to be repeated: the book only has to hold it once
