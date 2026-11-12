# 换票这一节，每个面该停在哪根 bar（r1530）

STALE: 3 of 10 faces are older than the 2026-11-12 close -- worst sibling_entry on 2026-11-11 (1 session(s) behind the 2026-11-12 close). waiting on data/etf_premium/snap/2026-11-12.csv (newest copy here: 2026-11-11, written 2026-11-11T16:25:44; lane owner bm-c writes it; this copy cannot)

- 该到位的 bar：**2026-11-12**（官方交易日历，收盘受理时点 15:30）
- 判词：**STALE**（陈旧 3 / 不一致 0）

| 面 | bar | 落后（交易日） | 状态 | 原因 | 生产者 |
|---|---|---|---|---|---|
| sibling_entry | 2026-11-11 | 1 | STALE | 1 session(s) behind the 2026-11-12 close | `scripts/etf_book_sibling_entry.py` |
| sibling_gap | 2026-11-11 | 1 | STALE | 1 session(s) behind the 2026-11-12 close | `scripts/etf_book_sibling_gap.py` |
| swap_trigger | 2026-11-11 | 1 | STALE | 1 session(s) behind the 2026-11-12 close | `scripts/etf_book_swap_trigger.py` |
| swap_stack | 2026-11-12 | 0 | FRESH | on the 2026-11-12 close | `scripts/etf_book_swap_stack.py` |
| swap_toll | 2026-11-12 | 0 | FRESH | on the 2026-11-12 close | `scripts/etf_book_swap_toll.py` |
| toll_scope | 2026-11-12 | 0 | FRESH | on the 2026-11-12 close | `scripts/etf_book_toll_scope.py` |
| swap_convergence | 2026-11-12 | 0 | FRESH | on the 2026-11-12 close | `scripts/etf_book_swap_convergence.py` |
| swap_effect | 2026-11-12 | 0 | FRESH | on the 2026-11-12 close | `scripts/etf_book_swap_effect.py` |
| swap_units | 2026-11-12 | 0 | FRESH | on the 2026-11-12 close | `scripts/etf_book_swap_units.py` |
| swap_track | 2026-11-12 | 0 | FRESH | on the 2026-11-12 close | `scripts/etf_book_swap_track.py` |

**这三条还在等谁**：waiting on data/etf_premium/snap/2026-11-12.csv (newest copy here: 2026-11-11, written 2026-11-11T16:25:44; lane owner bm-c writes it; this copy cannot)

## 为什么这张面存在

票面写「今日价差」而入场/价差/触发三面停在四个交易日之前——它们在链里只有 `check` 没有 `run`，而 `check` 只能证明一个面与它被造出来的那个世界自洽。每轮链都能发现它们不对，打印 NONZERO 就往下走（r1345 为另外三条腿写过同一句话）。

## 自证

- The bar-to-be comes from the official exchange calendar, never from this chain's own panels: a panel cannot say which session should already be printed (r1286).
- A face AHEAD of the calendar is not stale -- its producer would not make it true, so the chain must keep it red instead of paying a refresh (r1345).
- Freshness is not correctness: a face on the right bar can still be wrong, and each producer's own check is what refuses that.
