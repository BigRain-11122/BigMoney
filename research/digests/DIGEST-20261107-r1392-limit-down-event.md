# DIGEST 2026-11-07 r1392 bm-c — the sell side of the forced-trade clock: the discount is also paid at the next open

**Family.** zoo #92 `limit_down_event`. r1391 measured the buy side of the only free axis
left after breadth was priced as a tax: a bar sealed at the board ceiling forces the name to
trade tomorrow, and the premium is paid at that open (median gap +12.29%). The question this
round asked is the other side: a bar sealed at the **floor** (close == low at the board limit)
means the sellers could not get out today — does the buyer who steps in at the next open get
paid for taking that paper?

**Construct (frozen).** Same engine as zoo91 (panel reader, forward-return matrix, pool
benchmark, adjacency exclusion, same-exposure null are imported, not copied — the only
difference is the event mask). Panel = `data/astock_daily/per/*.csv` (qfq), 5,215 symbols ×
1,653 bars, 2020-01-02..2026-10-30. Event = `close/prev_close − 1 ≤ −(limit − 5bp)` **and**
`close ≤ low + 1e-9`. Limit from the board prefix (300/301/688/689 → 20%, 4/8/920 → 30%,
else 10%). Entry = `open[t+1]`, exit = `close[t+h]`, h ∈ {5,10,20}. Benchmark = cross-sectional
mean of the same h-bar return on the same date. Cost = 2 × 13.041bp. Null = 200 draws of the
same per-date event counts from cells that are neither an event nor within h bars after one.

**Readings.**

| h | events | gross excess | net excess | null mean | z vs null | hit rate | median event excess |
|---|---|---|---|---|---|---|---|
| 5  | 28,101 | −0.54pp | **−0.80pp** | −0.02pp | **−14.53** | 41.4% | −1.59pp |
| 10 | 27,981 | −0.71pp | **−0.97pp** | −0.17pp | −8.75 | 40.1% | −2.28pp |
| 20 | 27,803 | −0.48pp | **−0.74pp** | −0.47pp | **−0.10** | 40.6% | −3.08pp |

Per-year h=5 gross: 2020 −0.89pp, 2021 −0.90, 2022 −0.08, 2023 −0.54, 2024 **+0.05**,
2025 −0.46, 2026 −1.52pp. Verdict: **REFUSE_AS_CANDIDATE** (all four admit conditions fail;
1 of 7 years positive).

**The h=20 row is the finding.** At twenty bars the event's excess is −0.48pp while a
same-exposure random cell on the same date returns −0.47pp — z = −0.10. Over that horizon a
sealed floor is not a weak signal, it is **not an event at all**. The information in the
floor has a half-life shorter than 20 bars, and at 5 and 10 bars it is actively worse than
buying a random cell of the same name-universe (z −14.5 / −8.8).

**The entry price, again.** Median next-open gap over the sealed close is **−12.84%**, and
99.6% of events open more than 5% lower. The discount is real and it is the market's price,
not a gift: the panic that was blocked at the floor is already in the first bar you can buy.

**Method lessons (card E389).**

1. "It fell a lot, so it is cheap" is a **price** hypothesis, not an **information**
   hypothesis. Both sides of the clock lose, but for different reasons — the chase pays a
   premium, the knife-catch pays a discount — so a sign measured on one side cannot be read
   into the other.
2. When the largest horizon's excess converges on its null, that convergence is itself the
   reading. Writing it as "not significant" throws away the stronger statement that the
   event carries no information at that scale.
3. The null sampler must survive thin dates: on the sell side a date can have fewer eligible
   cells than events (sparse names + adjacency exclusion), and `choice(replace=False)` raised
   `ValueError: Cannot take a larger sample than population`, turning the whole batch into
   zero output. Correct handling is to fall back to sampling with replacement (the null is a
   mean of draws, not a set of distinct cells) while keeping the original path for the
   exactly-equal case so published zoo91 numbers do not move.

**Consumable face (negative).** Any candidate list or paper book should exclude or down-weight
names that sealed a **floor** within the last h bars — together with E388's ceiling filter it
becomes one rule: no entry during a sealed-bar window, on either side, with a measured cost
in both directions.

**Artifacts.** `scripts/zoo92_limit_down_event_probe.py` (selftest 7/7) ·
`scripts/zoo91_limit_up_event_probe.py` (shared engine; selftest still 7/7 after the
direction/low parameterisation) · `results/supply_berth/zoo92_limit_down_event_probe.json`
(evidence_cutoff 2026-10-30) · card E389 · smoke leg `product: limit-down event supply probe`.