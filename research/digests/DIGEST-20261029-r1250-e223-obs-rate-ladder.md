# E223 -- more observations are not more resolution (r1250, bm-b)

Date: 2026-10-29 · cutoff 2026-10-28 · primary sh510300 (3,503 sessions, 2012-05-28..2026-10-28)

## The question E222 left open

E222 closed the turn-of-month overlay with REJECT *and* a power statement: settling a
4.40bp calendar gap needs 1,317 months (~110 years), because a calendar rule is observed
once per month. The obvious successor is to anchor the rule more often -- a weekly anchor
gets 52 observations a year instead of 12. This face asks whether that actually buys
resolution, by running the identical accounting on a ladder of anchors.

## The ladder, frozen before reading

| arm | anchor | periods/yr | min OOS |
|---|---|---|---|
| `month_turn` | first + last session of each month | 12 | 24 months |
| `week_h1` | first session of each ISO week | 52 | 104 weeks |
| `week_h2` | first two sessions of each ISO week | 52 | 104 weeks |
| `week_h3` | first three sessions of each ISO week | 52 | 104 weeks |

One round trip (2 sides at 13.041bp flat) per **period**, not per held session -- the
anchor decides the period, so a weekly anchor pays weekly. Excess per period =
(held − toll) − all sessions of that period. First 60% of periods in-sample, rest out.
Decision rule frozen in code, four-way Bonferroni bar 2.50.

## What came out (primary, sh510300)

| arm | periods | excess OOS bp/yr | t | MDE @80% bp/yr | verdict |
|---|---|---|---|---|---|
| `month_turn` | 173 | +428.97 | 0.65 | 1860.6 | REJECT (`oos_t`) |
| `week_h1` | 738 | −1100.57 | −1.63 | 1888.2 | REJECT (net excess ≤ 0) |
| `week_h2` | 738 | −1239.24 | −2.38 | 1461.9 | REJECT (net excess ≤ 0) |
| `week_h3` | 738 | −1255.65 | −2.79 | 1261.1 | REJECT (net excess ≤ 0) |

Five-ETF equal-weight arm: same shape -- monthly +289.21 (t 0.36, MDE 2261.2), weekly
−1213.87 / −1434.15 / −1303.81, all rejecting on the toll.

## The load-bearing reading

The 52-a-year arms carry **4.3x** the observations of the 12-a-year anchor, and their
annual resolution is **0.68x to 1.01x** the monthly anchor's. The extra observations do
not resolve a calendar question, because the quantity that sets resolution is not the
observation count but `sd_per_period * sqrt(periods_per_year)`:

    MDE_ann = z * per_year * sd_per_period / sqrt(n_periods)
            = z * sd_per_period * sqrt(per_year / years)

Shrinking the holding window shrinks the per-period signal and the per-period dispersion
together, so the annual bar barely moves. `week_h1` -- the highest-frequency rung with
the thinnest exposure -- is in fact **worse** than the monthly anchor (1888 vs 1861), and
only `week_h3`, which holds 60% of the week, gets to 0.68x of it.

Second finding, independent of the first: the weekly arms are not merely unresolvable,
they are **negative** -- −1100 to −1256 bp/yr at t = −1.63 to −2.79, i.e. a fixed
weekly toll paid for a holding window that carries no per-week premium. Observation
rate moves the toll count 4.3x faster than it moves anything else.

## Carry-forward

- A frequency ladder must be priced in `MDE_ann`, never in "how many observations".
- The honest successor to a rejected calendar rule is not a faster calendar rule; it is
  a rule whose *number of independent observations* rises without cutting the exposure
  per observation (a state/volatility gate sampled continuously, not a shorter hold).
- `week_h3` at 0.68x is the only rung that improved resolution, and it still needed
  ~7,700bp/yr of true effect to clear its own bar -- three orders above anything this
  panel has produced.

## Pieces

- `scripts/e223_obs_rate_ladder.py` (`run` / `selftest`, 26 hermetic legs)
- face `results/obs_rate/OBSRATE-20261028.json` + `latest.json`
- S6 leg `obs_rate_ladder` after `tom_overlay`
- smoke leg re-derives every rung's MDE from its own published dispersion and OOS count
- pit: the first selftest fixtures wrote 1%/2%/3%/4% and expected 100bp -- bp is 1e4, so
  the correct expectation was 1000bp; and the ladder fixture must carry **all four**
  rungs or the summary raises KeyError instead of reporting a short ladder