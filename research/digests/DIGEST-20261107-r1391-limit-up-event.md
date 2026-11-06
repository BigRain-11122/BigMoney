# DIGEST 2026-11-07 r1391 bm-c — the limit-up event berth: the premium is paid at the next open

**Family.** zoo #91 `limit_up_event` — the first EVENT berth. r1390 measured
cross-sectional breadth as a tax (−10.01pp/yr for a 10-of-1,700 reversal book, with
a same-exposure random-rank null itself averaging −3.38pp/yr), which left "WHEN a
specific name is forced to trade" as the only free axis. A sealed limit-up bar is the
cheapest such clock this panel can see: the exchange stops the tape at the ceiling,
so everyone who wanted in today did not get in.

**Construct (frozen).** Panel = `data/astock_daily/per/*.csv` (qfq), 5,215 symbols ×
1,653 bars, 2020-01-02..2026-10-30. Event = `close/prev_close − 1 ≥ limit − 5bp`
**and** `close ≥ high − 1e-9` (sealed at the close), limit from the board prefix
(300/301/688/689 → 20%, 4/8/920 → 30%, else 10%). Entry = `open[t+1]`, exit =
`close[t+h]`, h ∈ {5,10,20}. Benchmark = cross-sectional mean of the same h-bar
return on the same date; excess is per-event and then averaged (date-neutral). Cost =
2 × 13.041bp. Null = 200 draws of the **same per-date event counts**, sampled from
cells of that date that are neither an event nor within h bars after one.

**Readings.**

| h | events | gross excess | net excess | null mean | z vs null | hit rate |
|---|---|---|---|---|---|---|
| 5  | 95,857 | −0.92pp | **−1.18pp** | +0.03pp | **−49.96** | 37.6% |
| 10 | 95,568 | −1.82pp | **−2.08pp** | +0.10pp | −60.89 | 34.2% |
| 20 | 95,119 | −2.92pp | **−3.18pp** | +0.24pp | −80.60 | 31.5% |

Per-year h=5: 2020 +0.16pp, 2021 −0.18, 2022 −1.29, 2023 −1.28, 2024 −1.54,
2025 −1.40, 2026 −0.74pp. Verdict: **REFUSE_AS_CANDIDATE** (all four admit
conditions fail; 1 of 7 years positive).

**The mechanism is the entry price.** Median next-open gap over the sealed close is
**+12.29%**, and 97.2% of events open more than 5% higher. The limit-up day's
information is fully priced at the first bar you can actually trade. That single
fact is what flips the sign: measured from the (unfillable) limit-day close the same
events look like a gain; measured from the next open they lose 1.2pp over five bars
against simply owning the tape.

**Method lessons (card E388).**

1. An event study must treat the ENTRY BAR as an object of study, not an assumption.
   State its position relative to the event bar in the construct block.
2. Sealing needs three conditions: return at the board limit, close at the high, and
   a board-specific limit from the code prefix. Return-only counts blown-up intraday
   touches; 10%-only misses the whole 20% board. ST names trade at 5% and therefore
   never enter the event set — disclosed as a coverage boundary.
3. The same-exposure null must be date-matched AND exclude cells within h bars after
   an event, otherwise the null re-imports the events' own post-event drift.

**Consumable face (negative).** Any candidate list or paper book should exclude or
down-weight names that sealed a limit-up within the last h bars: this is a filter with
a measured cost, not a signal — the buyer who chases pays a 12% gap to underperform by
1.2pp.

**Artifacts.** `scripts/zoo91_limit_up_event_probe.py` (selftest 7/7) ·
`results/supply_berth/zoo91_limit_up_event_probe.json` (evidence_cutoff 2026-10-30) ·
card E388 · smoke leg `product: limit-up event supply probe`.