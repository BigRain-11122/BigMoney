# D-2026-10-30 r1275 bm-b — the negative lead is book-wide, not the star's flow

**Face** `results/state_tilt/LEADCOUNTER-2026-10-29.json` (evidence_cutoff 2026-10-29)
**Runner** `scripts/e249_lead_counterfactual.py` — run / selftest 18/18, face ~14s
**Card** `knowledge/METHODOLOGY_ASSETS.md` E249

## The question

E248 extended the distributed-lag row to lags 1..5, spent a 200-draw shuffled null, and found
exactly one crossing: lag 1, negative, **-0.586** on the star column (sh588000), family-wise line
0.351. Two readings survive that result and the row cannot separate them, because it only ever
fits ONE column of interest:

- (a) that sleeve's flow is **absorbed** — its turnover spikes and the book's next move is
  smaller, a source with a negative sign; or
- (b) **every column pays the same lag-1 negative** because a book-wide liquidity proxy
  mean-reverts, and the star is simply the column the fit reads most cleanly.

## The counterfactual

Refit the same row with **each member as the column of interest** (the other four are the rows),
give every column its **own** 200-draw shuffled band (E248's estimator, E248's family-wise line,
E248's star rule — reused verbatim, nothing re-implemented), and compare the column-to-column
spread against the measured within-column band.

## The answer

Headline cell, 1,328 sessions:

| column | lag-1 | clears own null |
|---|---|---|
| sh510050 | −0.233 | no |
| sh510300 | −0.238 | yes |
| sh510500 | −0.280 | yes |
| sh512100 | −0.303 | yes |
| sh588000 | **−0.586** | yes |

- **All five columns are negative.** The star is the largest of five negatives, not a lone signal.
- **spread 0.352 vs median within-column band 0.384 → spread/band 0.92.** The columns differ from
  each other by less than the measurement noise of one column.
- Verdict `book_wide_same_sign`: **a book-wide number, so no member may be billed for it.**
- Cross-face identity: this sweep reproduces E248's published star lag-1 **−0.585816805073** to
  twelve digits. Same design, same data — the difference is the question asked.

### The six counted cells

| cell | sessions | verdict | columns (lag-1) |
|---|---|---|---|
| all_five | 1328 | book_wide | −0.233 / −0.238 / −0.280 / −0.303 / **−0.586** |
| pre2020_four | 891 | column_specific* | −0.276 / −0.315 / −0.181 / −0.042 |
| era_2020_2022 | 474 | column_specific* | −0.143 / −0.132 / −0.196 / −0.173 / **−0.422** |
| era_2023_2024 | 446 | book_wide | −0.316 / −0.227 / −0.319 / −0.329 / **−0.682** |
| era_2025_now | 408 | book_wide | −0.214 / −0.384 / −0.304 / −0.332 / **−0.695** |
| early_three | 831 | book_wide | −0.442 / −0.259 / −0.184 |

\* Both starred cells are **power readings, not channels**. Their other columns carry the same
sign and sit just inside their own nulls; the lone crossing's gap to their median is a fraction of
one band width (0.441 and 0.509). The frozen vocabulary is kept and a **post-hoc separation block**
reclassifies both to `book_wide_same_sign` and names them; post-hoc rollup = `book_wide_same_sign`
in 6 of 6 counted cells. Spread/band ratio across every cell: 0.56 / 0.65 / 0.87 / 0.90 / 0.92 /
1.01 — never more than one band.

## What this changes

E246/E248 named a star-specific negative channel. **It does not survive as a channel.** The
negative lag-1 lead is present on every column at comparable magnitude in every era, which is what
a book-wide mean-reverting liquidity proxy looks like. Consequence: the family's single negative
exponent stays a **price without a bill** — and now it cannot be billed to a sleeve at all.

## Laws (card E249)

1. **One column, one reading.** A channel claim needs the other columns as controls; the cheapest
   control is refitting with the column of interest moved.
2. **Specificity needs a separation test, not a crossing count.** "Exactly one column crossed" is
   a statement about power. The gap to the other columns must clear one band width.
3. **Compare a spread to a measured band, never to a constant.** The same five readings are
   `multiple_crossings_differ` against a 0.05 band and `book_wide_same_sign` against 0.60.

## Not done / not claimed

No bill, no adoption, no re-pricing (the face carries its `no_bill` line). GPU untouched (parked
by C-20261014-01); no cloud calls; nothing deleted or quarantined; `bm-a`/`bm-c` lane collectors
honoured their guards. The face says nothing about *why* every column is negative — a book-wide
liquidity proxy is the leading candidate and is not tested here.