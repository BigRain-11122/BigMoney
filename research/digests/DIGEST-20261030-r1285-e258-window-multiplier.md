# DIGEST 2026-10-30 r1285 bm-b — E258: each window has its own draw multiplier

**Question.** E257 established that the shuffled band's 5% endpoint is still rising at 1920 draws,
then had to apply that fact to sixteen published rows using a multiplier it could only BORROW: the
ladder had been measured inside `era_2025_now` (head/tail families), and a fixed published window is
neither. So E257 widened every band by a range (1.098..1.664) and re-judged each row at all fourteen
values. What is each window's multiplier when it is measured in that window?

**Design.** Not arithmetic on published faces this time — the band is rebuilt inside each published
window. Three pins make the measurement the same object as the band it widens:

1. **Window** = the published cell's own first/last dates.
2. **Star** = the star that cell published (`cell.star`); re-naming would price another sleeve's null.
3. **Members** = the cell's own member list. `early_three` is a three-member window; measuring it on
   the five-member basket intersects five level series over 2013-2016 and returns zero sessions.

Draw grid `(60,120,200,480,960,1920)`, prefix-nested per seed (one stream at the top count read back
at every smaller count), 3 seeds. `m = edge(top)/edge(the row's own published draw count)`, published
with its per-seed scatter. Every published row is then re-judged with its own window's multiplier
and published beside E257's borrowed-range verdict; disagreements are named, not averaged.

**Reading (cutoff 2026-10-29).**

| window | sessions | star | m at that window's own base |
|---|---|---|---|
| all_five | 1328 | sh588000 | 1.317 (base 200) |
| early_three | 831 | sh510050 | 1.838 (base 60) |
| era_2023_2024 | 446 | sh588000 | 1.473 (base 60) |
| era_2025_now | 408 | sh588000 | 1.644 (base 60) |

Two windows were skipped and both are honest skips: `pre2020_four` and `era_2020_2022` publish **no
star at lag 0**, so there is no sleeve whose shuffle null the band would be (the same four rows E257
already carried as unjudgeable).

- Spread over all eight window/base cells: 1.267..1.838, median 1.404, **ratio 1.45** — the
  multiplier is not one object across windows.
- **Same-base comparison (the one that counts): 0 of 12 judged rows fall outside the range E257
  actually applied to that row.** Each of those ranges was the ladder read at the row's own published
  draw count, so it is comparable; every measured window multiplier lands inside it.
- What the measurement buys is **resolution, not correction**: the median borrowed range the rows
  were judged against is **0.820 wide** (82 percentage points of multiplier), while the median
  per-window seed width is **0.256** — the per-window measurement is **3.2x tighter**. E257's range
  was wide because it spanned ladder rung lengths the row never had.
- Re-judged rows (16): **8 survive outside**, 2 stay inside, **2 flip only for some seeds**, 4
  unjudgeable. The two that flip are one coefficient (b = -0.4942, early_three), published twice by
  E252's cross row and E251's star lag-1 residual — two rows, one coefficient, as E257 already
  warned.
- Agreement with E257's borrowed-range verdicts: 10 same, 2 same-shape-different-axis, 4 not
  comparable. No row's published flag had to be quarantined.

**A claim I had to withdraw.** The first draft of this face reported "early_three's multiplier sits
10.5% above E257's borrowed maximum, so exactly the window that mattered was under-widened". That
compared a multiplier measured at **60 draws** against a table range read at **200 draws** — two
bases, one subtraction. Re-read at the same base, early_three's own borrowed range was
**1.105..1.925**, and 1.838 is inside it. The cross-base block is still published (it is where the
error lived), but it now carries a `BASIS_WARNING` and the same-base block is the headline. A
comparison across base counts is not a comparison; it is arithmetic that happens to produce a
number.

**The line that matters.** At the widest multiplier E257 applied to that row (1.925) b = -0.4942 is
inside its band; at the narrowest (1.105) it is outside. The per-window measurement says the honest
answer is "depends": the three seeds give 2.232 / 1.402 / 2.246 at 60 draws, so two of three clear
the edge. A three-stream median is not a distribution, and the verdict says so instead of picking the
median and calling it a flip.

**Pits (all caught inside the round).**

1. The first cut passed the whole five-member basket to every window. `early_three` came back as
   "window has 0 sessions" — a data-shaped failure that was really a universe mistake. Anything
   pinned from a published cell must pin dates **and** star **and** members.
2. `published_verdicts()` returned only the verdict string, and a later `rec.update({...})` wrote
   `e257_verdict: r.get("verdict")` (= None) over the value just attached. The comparison column
   existed and printed `n/a..n/a` for all sixteen rows — worse than absent, because it reads as
   "E257 has no range". The fix was to carry the whole published row and to copy the field from
   `rec`, not from the un-augmented source row.
3. **Names come from the card, not from me.** The seeded card declared
   `scripts/e258_band_multiplier_per_window.py` and `results/state_tilt/BANDWINMULT-<cutoff>.json`;
   I wrote `..._in_each_window.py` and `WINDOWMULT-2026-10-29.json`. Left alone that is a phantom
   card (`runner_absent`, the defect r1283 found on two of bm-c's cards) plus a deliverable nobody
   looks for. Both were renamed to the card's own paths, the S6 leg / smoke leg / digest / card were
   re-pointed, and the stale `WINDOWMULT-*` faces deleted rather than left as a second surface for
   one study.

**Product.** `scripts/e258_band_multiplier_per_window.py` (run / selftest 21/21 / verify OK),
`results/state_tilt/BANDWINMULT-2026-10-29.json` + `bandwinmult_latest.json`, S6 leg
`band_multiplier_in_each_window` (spot-ran 7/7 with the whole star/band leg family), smoke leg,
methodology card E258.

**Cost.** ~85s for 4 windows × 3 seeds × 1920 draws — cheap enough to re-run whenever a new window is
published, which is the point: the borrow should not have to be permanent.