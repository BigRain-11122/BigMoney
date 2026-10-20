# DIGEST 2026-10-21 — E26 band rebalancing: monthly is already free

**Question.** E25 closed the trend-filter family and left one accounting fact behind:
equal-weighting the five-member ladder turns over only 0.32x/yr (4.2bp/yr of cost),
while every filter tried paid 9-38bp/yr of turnover and bought nothing. If the
monthly rebalance is the only remaining cost, would rebalancing *less* — only when a
member's weight drifts outside a band — keep the same exposure for less money?

**Runner.** `scripts/e26_band_rebalance.py` (selftest 10/10). Same panel, same
13.041bp/side cost, same GC001 cash leg, same causal weights as the E24/E25 runner;
the only difference between schemes is the rebalance trigger.

**Face.** `results/e26_band_rebalance/BAND-20261021.json` — 2012-05-28..2026-10-20,
3,497 bars, 13.88y, monthly plus bands 0.5/1/2/5/10pp.

| scheme | ann % | vol % | Sharpe | rebalances | turnover/yr | cost bp/yr | vs monthly bp/yr | t |
|---|---|---|---|---|---|---|---|---|
| monthly | 5.27 | 21.54 | 0.347 | 160 | 0.322 | 4.2 | — | — |
| band 0.5pp | 5.21 | 21.57 | 0.344 | 376 | 0.413 | 5.4 | -5.6 | -0.47 |
| band 1pp | 5.28 | 21.56 | 0.347 | 152 | 0.349 | 4.5 | +1.1 | 0.10 |
| band 2pp | 5.24 | 21.56 | 0.345 | 47 | 0.277 | 3.6 | -2.8 | -0.21 |
| band 5pp | 5.19 | 21.56 | 0.343 | 12 | 0.224 | 2.9 | -7.6 | -0.47 |
| band 10pp | 5.13 | 21.57 | 0.340 | 9 | 0.215 | 2.8 | -13.2 | -0.65 |

**Verdict: HONEST NEGATIVE (wash).** A band saves 0.4-1.4bp/yr of cost and gives back
0-13bp/yr of return, all of it inside noise (|t| ≤ 1.0). Monthly equal-weighting is
already 4.2bp/yr, i.e. there is nothing to optimise on that axis — the drift the
monthly rule corrects is worth about what it costs. Combined with r1094/r1095 (timing
gates lose 74-597bp/yr) and r1097 (hard filters -133..-178bp/yr), the E24-E26 block now
says the same thing three ways: *the ladder edge is a hold effect; every mechanical rule
laid on top of it is a wash or a loss.*

**Method pit (cost the first burn).** The first run of this runner had the band schemes
enter at the first eligible bar while the monthly scheme entered at the next month end.
In 2013-06 that single-date difference put every band variant ~6% behind (the band family
bought the liquidity-crunch top) and produced a fake "-65bp/yr, monotone in band width"
reading that survived a zero-cost control. Fixed by gating the first entry to the same
month-end set for every scheme; selftest leg 9 now asserts both schemes enter on the same
bar. **Lesson: any frequency comparison must pin the entry date first — one unlucky entry
bar can masquerade as a frequency effect and it does not show up in a zero-cost control.**