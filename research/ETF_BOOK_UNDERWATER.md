# ETF book — depth and duration are different risks (r1230 bm-a)

**Question.** Every published face of this book states how much it earns (CAGR, Sharpe) and
one states how deep it falls (max drawdown point, plus its bootstrap distribution). None
states **how long a holder waits**. "−16.6% max drawdown" reads very differently if it is a
three-month dip or a four-year hole, and until r1230 nothing in the repo could tell the two
apart.

**Face.** `scripts/etf_book_underwater.py` (selftest 14/14, `--check` OK), artifact
`results/etf_book_underwater.json`, chain leg `etf_book_underwater`, smoke legs
(exit-code contract + verdict re-derived from the published rows).

It reads one curve — the production engine's own — and publishes three things:

1. **Underwater episodes** (peak → trough → recovery), each named by date, with the ones that
   never healed inside the data kept as `recovered: false`.
2. **Time-to-recover for every entry bar** (1652 entries), with censored entries counted,
   never scored as zero.
3. **Forward 1/2/3 **calendar**-year** returns from every entry (min / p5 / p50 and the share
   of negative starts), because "worst calendar year" is not "worst 12 months you could have
   bought into".

**Frozen before the run.** The control arm is the published `n12_vt08` cell and must
reproduce its CAGR and max drawdown to 5e-5 or the face refuses to publish
(`CONTROL_MISMATCH`). An entry that has not recovered on the last bar is censored, not zero.
Horizons are calendar years via `DateOffset` (the engine's bar spacing is not assumed to be
252/year). The verdict is descriptive: no threshold decides whether the book is good.

## Live reading (cutoff 2026-10-30, 1652 bars)

| Quantity | Value |
|---|---|
| Control | **CONTROL_REPRODUCED** (CAGR 9.60%, maxdd −11.77%, tol 5e-5) |
| Longest underwater episode | peak 2021-09-14 → trough 2022-11-01 (−11.77%) → **healed 2023-03-02**, 350 bars |
| Episodes / healed | 54 / 53 (one still open on the last bar) |
| Median episode length | 4 bars |
| Worst entry | 2021-09-14 (the peak) → recovery 351 bars |
| Median / p90 recovery | 1 bar / 14.9 bars |
| Censored entries | 10 / 1652 = 0.61% (all at the end of the window: no future yet) |
| 1-year forward | min **−7.51%**, p50 +8.12%, **8.0%** of entries negative |
| 2-year forward | min −0.02%, p50 +6.75%, 0.09% negative |
| 3-year forward | min **+0.78%**, p50 +6.86%, **0%** negative |

**What this says, plainly.** The book's worst realistic experience is not the drawdown depth
(−11.8%) but the wait: an investor who bought the 2021-09 peak sat under water for **351
trading bars (~17 months)** before getting even. Losses on any 3-year horizon never happened
in this sample — but the sample starts in 2020 and is 6.8 years long, so this is a statement
about a rising sample, not a promise (see the caveats below).

**Honest boundaries.**

- 2020-01 → 2026-10 only; the pre-2020 leg is priced separately (`etf_book_pre2020`) and is
  not pooled here — the instruments are different books.
- Survivorship: the ETF pool is the set of ETFs that exist today (already disclosed on the
  card and by `etf_equity_alpha`).
- "Recovered" means nominal equity regained, not real (no inflation deflator, no funding
  cost on the cash leg).
- The median recovery of 1 bar and the median episode of 4 bars are properties of a curve
  that spends most of its bars near a new high; they are not a claim that drawdowns end
  quickly. The numbers to read are the p90 (15 bars), the 53rd episode (350 bars) and the
  worst entry (351 bars).
- This face does **not** test a rule. It measures the shipped book. Any guard ("go to cash at
  −X") is priced by `etf_book_drawdown_guard`, not here.