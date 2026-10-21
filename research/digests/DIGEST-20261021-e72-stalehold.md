# E72 — the stale-hold tail is real but era-local and sign-flipping; in the live era it is worth +1.6bp/yr, so it explains none of the -45bp residual

**Cutoff** 2026-10-21 · **Face** `results/e44_midmonth/STALEHOLD-20261021.json` (start 2020-01-01) and `STALEHOLD-20261021-s20130101.json` (start 2013-01-01) · **Runner** `scripts/e39_panel_census.py stalehold` · **Trial count** 0 (descriptive census, no prereg, no gate, no ledger booking)

## The question E71 left open

E71 measured the last membership channel between the month-end and weekly books: a name the weekly book drops keeps its weight in the monthly book until the next month-end, **20.7 sessions vs 4.9**. E70 had already switched the fee off and left a **-45bp residual** on the full weekly grid against month-end that was neither fee nor (per E71's 0.9993 name overlap) different names. The stale hold was the only candidate left, and E71 counted it but did not price it.

E72 prices it. For every exit event (a name held at one month-end decision and gone at the next), find the last weekly decision that still held it, compound the name's **own** close-to-close return over the extra sessions, and charge it at the dropping book's equal weight `1/n_held_before`. The unit is bp of portfolio. No engine re-run, so the number cannot double-count the calendar gaps E65-E69 already priced.

## Answer: the tail is worth +1.6bp/yr in the live era

Start 2020 (x1 frames, 128 stale events, 12.09 mean extra sessions, 59.4% negative):

| era | events | tail total bp | tail bp/yr |
|---|---|---|---|
| pre2017 | 0 | 0.0 | — |
| 2017_2020 | 0 | 0.0 | — |
| 2021_2023 | 58 | **-516.9** | **-213.3** |
| 2024_now | 70 | **+4.3** | **+1.6** |

Start 2013 (172 events, 12.33 mean sessions, 57.6% negative):

| era | events | tail total bp | tail bp/yr |
|---|---|---|---|
| pre2017 | 19 | **+683.0** | **+282.2** |
| 2017_2020 | 24 | -97.6 | -24.8 |
| 2021_2023 | 59 | **-565.2** | **-226.1** |
| 2024_now | 70 | **+4.3** | **+1.6** |

Three readings:

1. **The newest era is null and start-invariant.** +4.302bp total / +1.615bp/yr at both window starts — bit-identical, the same start-invariance E59/E63/E65-E71 keep finding in this era. Against a -45bp residual the tail explains **nothing** (3.6% of it, wrong sign).
2. **The channel is era-local and flips sign.** It is a *drag* of -213 to -226bp/yr in 2021_2023 and a *gain* of +282bp/yr in pre2017. That is not a mechanism, it is a beta signature: stale names simply carry the market they are stuck in.
3. **E71's 20.7-vs-4.9-session asymmetry is structurally real and economically empty in the live era.** The monthly book does hold dead names four times as long; over 2024-now those names happened to move with the book.

## What this closes

The E70 weekly-book residual is now excluded on three channels: fee (E70: shift equals the extra-turnover fee exactly), names (E71: 0.9993 overlap), and stale tail (E72: +1.6bp/yr). What remains is **session timing** — the 1-3 session offset of the weekly grid, already priced at -19/-24bp (early) and -43/-52bp (late) by E67/E68. E72 therefore closes the E69-E72 chain rather than opening another branch.

## Honest limits

- The tail is charged as name return × equal weight over the extra sessions; it is not either book's P&L.
- An event needs a priced base at the weekly drop and a priced close at the monthly drop. Start 2020 skips 10 unpriced ends, start 2013 skips 16 — disclosed, never charged as a flat hold.
- Names held by the monthly book that the weekly book never holds: **0** at both starts (consistent with E71's `me_only=0`), so no coverage correction is needed.
- `bp_per_year` divides a window total by its calendar span; an era with few events reads noisily. pre2017's +282bp/yr rests on 19 events.
- The -45bp residual is quoted from the E70 face as published; E72 does not recompute it.

## Next

**E74-STALE-TAIL-VS-BOOK** — charge the same events *relative* to the wide book over the identical sessions instead of raw. If the relative tail collapses toward 0 in every era, the sign flips above are pure market beta and the channel is null in both directions, closed for good.