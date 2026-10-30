# E244 -- the spread sits on WHO you single out, and the two signs are not two channels

**Round** r1270 bm-b · **Face** `results/state_tilt/PAIRHET-2026-10-29.json` (twin `pairhet_latest.json`)
**Card** `knowledge/METHODOLOGY_ASSETS.md` E244 · **Runner** `scripts/e244_pair_heterogeneity.py` (selftest 15/15)
**Source** `results/state_tilt/addos_latest.json` (E243, machine-read with its sha256 recorded -- nothing transcribed)

## The question E243 left open

E243 killed the additivity verdict but named no structure: on its headline cell 9 of 20 ordered pairs
have their own interval clear of zero, **with both signs**. A mixed-sign pair set is three different
objects -- a few counterparties that genuinely pay differently, one cell's noise seen through twenty
windows, or two quantities wearing one name. This face asks where the spread lives: on the
counterparty identity (`one_of`, the name the difference is measured against), on the own identity
(`own_of`, whose return is explained), or nowhere repeatable.

## Answer

**`two_members_pay_differently`.**

| counterparty | decisive pairs | cells | mean diff (decisive) | signs |
|---|---|---|---|---|
| sh588000 | 22 / 28 | 8 | **+0.800** | + only |
| sh512100 | 9 / 31 | 6 | **-0.498** | - only |
| sh510050 | 14 / 31 | 10 | -0.543 | mixed (-1, +1) |
| sh510500 | 9 / 31 | 10 | -0.166 | mixed |
| sh510300 | 6 / 31 | 9 | +0.140 | mixed |

Variance over the 152 published pairs: **counterparty identity 50.7% / own identity 0.1% / residual 49.5%**.
Read the two numbers together: the heterogeneity is almost entirely about *which name you single out*
and almost not at all about whose return is being explained -- but half of it is still pair
idiosyncrasy, so "one carrier plus a mirror" would be an over-claim on this grid.

## The mechanic that changes the reading of E243

`diff = b_one - b_rest3`, so a **positive** difference means the sum of the remaining members pays
more than the singled counterparty. A member that pays *more* than the rest therefore produces a
**positive** reading when it is the counterparty and a **negative** reading for every ordinary member,
because the deviant sits **inside the sum** the ordinary member is priced against.

That mirror is arithmetic, not a second channel. The fixture pins it: on a book with one member at
0.9 and the rest at 0.02, positive-decisive pairs are overwhelmingly the ones where the deviant is
the counterparty, and the ordinary members read the mirror. The deviant has exactly three roles --
own, counterparty, inside the sum -- and only the third one casts the mirror. So the sign count alone
can never distinguish one deviant from several; the classification therefore requires a repeatable
name on *each* side before it calls a split, and publishes the mirror ratio (1.61 against a frozen
floor 1.50).

On the live book the two carriers are the two members whose own response differs from the pooled
channel in opposite directions: the newest member (sh588000, printing from 2020-11-16) reads positive
-- when it is singled, the sum of the others pays more -- while sh512100 reads negative, its own
single response exceeding the sum channel.

## Caveats carried, not resolved

* **The cells overlap in time.** Era and leave-one-out cells are subsets of the headline window, so
  the 152 rows are *repeats*, not independent replications. Published as
  `overlap.independent_observations = false`, with every cell's span.
* **Carrier thresholds are frozen** (decisive in ≥50% of the cell set, ≥2 decisive pairs, ≥1 sign,
  |mean| ≥ 0.30) and the floor sits at half of E243's own 0.60 resolution scale.
* **No bill.** This classifies where a published spread sits; it re-prices nothing and adopts no arm.
* The unsummed object -- each member regressed on every other separately, no sum regressor -- is the
  card this face seeds as **E245**; publishing it here would have been a second burn of the same
  intervals.

## Pits caught in-window

1. **A noiseless fixture makes every pair decisive.** The first synthetic book carried no error term,
   so every regression fit exactly, every interval had zero width and *every* pair "excluded zero" --
   the carrier test named three carriers on a book with one. Fix: noise in the fixture (sd 0.6), which
   is the same defect family as E238's degenerate-panel refusal.
2. **A single deviant produces both signs.** The first classification read "one positive + many
   negative" as two channels. The mirror leg showed the negative side is the deviant sitting inside
   the sum; the verdict vocabulary was rebuilt around members, not signs.
3. **The first mirror assertion was false.** "Ordinary-vs-ordinary pairs read ~0" is wrong: they read
   the mirror too (-0.29), because the deviant is in their sum. The correct statement is about the
   deviant's three roles, and small-sample stragglers off the deviant are counted rather than denied.