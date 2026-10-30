# r1357 — the ruler reaches the card sheet, and says which face of the pair it is

**Ask.** r1356 put the live-width ruler on the beta ticket (`ORDER-<bar>.md`). The other
document a reader can hold — `ORDER-<bar>-card.md`, issued from the production card's own
config — carried the width disclosure but not the ruler. Two sheets, one operator, only one
of them answering "what did the other sheet measure".

**What a paired number is.** `results/etf_book_live_width_ruler.json` is built by pairing
the two live faces phase by phase:

| face | names | rule | median CAGR (20 phases) |
|---|---|---|---|
| ticket | 5 | beta 0.20 | 9.13% |
| card | 12 | vol 8% target | 9.645% |

Paired median difference **+0.09pp** across 20 phases (10 up / 10 down, range −2.05 … +2.89,
sd 1.255). The same 5→12 rung on the second engine reads **−1.53pp** and the atlas engine
reads **+0.515pp**, so the engines disagree by **2.045pp with the sign flipping**. The
paired gap is **4.4%** of that disagreement.

**The finding is not the number, it is the ownership of the number.** The gap is *between*
the two faces. A card-sheet that printed it as "this sheet vs the card" would be quoting a
difference between two other books — and it would read as if the card had a defect. So
`live_width_ruler(..., sheet="card")` returns `sheet_role`, derived from the face's own
priced widths: this sheet is `measured_card`, the beta ticket is `measured_ticket`, and
anything else is `None`. If the face prices a width the live faces no longer run, the role
becomes **`unverified`** and the page says so instead of printing the clean reading — the
same family as r1280 (a label that outlives its numbers is a receipt, not a gate).

**Reading on the card sheet.** "本单就是卡片那一本书（12 名 / vol 8%），所以这个差不是「本单 vs
卡片」，而是「5 名 beta 覆盖那张单 vs 本单」：中位 +0.09pp（20 相位，10 上 10 下，−2.05 ~ +2.89）；
同一档在另一台引擎上 −1.53pp，分歧 2.045pp（方向相反）。这 0.09pp 只有引擎分歧的 4.4%，所以两张单
之间选哪张读不出收益差——读得出来的是要在哪一档波动预算上：β 覆盖固定杠杆，本单按 8% 目标只降不升。"

**Verified.** `scripts/etf_book_order.py --selftest` 52 → **56/56 PASS** (leg42 the role is
derived and never free; leg42b moved widths ⇒ unverified; leg42c the card page prints the
other sheet's gap and says so; leg42d an unverified sheet cannot print the clean reading).
One smoke leg (**product: E271**) recomputes the coin-flip verdict from the ruler face and
requires the same median *and* the same disagreement string on **both** order documents —
if the face moves, both pages fail. Both artefacts were regenerated, not patched.

**Pitfall.** The two renderers spelled the disagreement differently (`%.2f` on the beta
page, `%+.2f` on the new card block) — invisible while only one document printed it. A
cross-document assertion is what surfaces a spelling difference, the same way a fixture only
proves a shape (r1290 leg16 family).

Card: **E271**.