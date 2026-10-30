# E269 -- does the tight end of another window transfer as badly as its wide end?

**Face** `results/state_tilt/BANDTIGHT-2026-10-29.json` (+ `bandtight_latest.json`)
**Runner** `scripts/e269_tight_end_transfer.py` (run / verify 0 problems / selftest 35/35)
**Source** E259's published intervals (p05 *and* p95 per window/leg/base) and E262's 16 resolved row
records. No band rebuilt, no shuffle drawn, no panel, no bill.

## The question

E262 / E264 / E266 / E267 / E268 all swept the **wide** end (p95): borrow another window's p95,
judge a row with it, count the verdicts that move. Every arm also publishes a **p05** and every row
a `verdict_tight`, so the tight half of the same question had never been scored. It is not implied
by the wide answer: the wide end decides rejections on the side a row already sits beyond, the tight
end decides how much a row can be over-credited, and both are drawn from the same shuffle stream but
from opposite tails.

Same population, same machinery, opposite tail: the 48 ordered donor/recipient pairs inside each
(leg, base count).

## Answer

| reading | tight end (p05) | wide end (p95, published in E262) |
|---|---|---|
| ordered pairs | 48 | 48 |
| pairs moving a verdict | **0** | 2 |
| rejections invented / lost | 0 / 0 | 0 / 2 |
| arms ranked | 2 of 4 groups have a strict minimum | 4 of 4 groups have a strict maximum |
| spread across windows | **10.08%** max | 16.79% max |
| pooled single number ("use the tightest" = group minimum) | 0 moves | 2 moves |
| pooled loose twin (group maximum) | 0 moves | -- |
| rows judged outside their band | **10 of 12** | 8 of 12 |

The tight verdict is the *stricter* one -- 10 of 12 rows sit outside their own tight band, versus 8
outside their wide band -- and yet no window's p05 moves any of them. Windows disagree about their
tight tail by up to 10.1%, and that disagreement still changes nothing.

## Why "zero moves" is a measurement here, not a tautology

This is the r1261 shape one tail over: two numbers agreeing because neither side did anything. So
the face publishes, per row, the **multiplier at which its verdict flips** (`flip_multiplier`; band
is `(lo*m, hi*m)`, so "outside" reduces to `m < m_flip` on the side the row sits on) and compares it
against the range of p05 values the row's own group actually published:

| group | p05 range | spread | rows | could move at any published p05 | nearest flip, % outside the range |
|---|---|---|---|---|---|
| cross:200 | 1.0000 .. 1.0000 | 0.00% | 2 | **0** | 63.0 |
| cross:60 | 1.0000 .. 1.1008 | 10.08% | 6 | **0** | 38.9 |
| self:200 | 1.0000 .. 1.0688 | 6.88% | 1 | **0** | 54.2 |
| self:60 | 1.0095 .. 1.1065 | 9.61% | 3 | **0** | 13.5 |

Every row sits at least **13.5%** outside the widest swing its group contains. So the correct verdict
is not "the tight end transfers cleanly" -- that would claim a validated substitution -- but
`the_tight_end_is_inert_on_this_population`: the tight end cannot transfer badly because it cannot
move anything on these 16 rows. The tight half is **untested**, not safe, and needs cheaper
resolution (rows sitting within ~10% of their tight boundary) before anyone borrows it.

`cross:200` is worth its own line: all four windows publish **exactly the same** p05 = 1.0000 for
that group, i.e. the tight tail is degenerate there while the wide tail is not.

## What this changes operationally

The instruction a reader takes away is now narrower than before and in a useful direction: **do not
borrow the wide end** -- E262's 2 moves are wide-end moves. Nothing on this table argues against
borrowing the tight end; nothing argues for it either. Anyone who wants a single number per group
can take the pooled minimum p05 without changing a verdict on any published row (0 moves), with the
disclosure that it moved nothing to begin with.

Face supply downstream: E270 (does every published face a screen reads actually carry the guard's
inputs) and E271 (does the moved set depend on *which* donor, not only how wide) stay ready.

## Engineering pits (all caught in-window)

1. `BANDTRANSFER`'s `rows` are E262's **already-resolved records**, not the raw source rows.
   Re-running `e262.row_records` on them looks for `band_draws`, misses it, and marks **all 16**
   unjudgeable -- which the face then published as `no_tight_rows_measured` with 0 rows measured and
   48 pairs. The tell was a face that happily reported a verdict on zero rows; `verify` agreed with
   the bug (it re-derives the same wrong answer), so only reading the printed run output caught it.
2. The `p05_spread_pct_max` comprehension referenced `d` inside its own filter clause -- a
   `NameError` at run time that compiles clean (same shape as r1294's ordering pit: `verify` cannot
   see it).
3. A selftest fixture put the flip exactly on the boundary (`b=-0.45`, `lo*m = -0.45*1.5`), where
   binary floating point put it *below* the edge and the leg asserted a move that never happened.
   Correct code, wrong fixture -- fixed by moving the fixture off the tie, not by loosening the leg.
   (Fourth sighting of the r1281 family.)
4. PowerShell still has no heredocs: the first patch attempt through `python - <<EOF` was parsed as
   PowerShell and failed before reaching Python. Patches go through the edit tool.