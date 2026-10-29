# E229 — sign-stability is a statement about direction, not sufficiency: the two quotable signs alone are a losing book (r1341 bm-c)

**Card:** E229 in `knowledge/METHODOLOGY_ASSETS.md`.
**Code:** `scripts/etf_lowvol_book.py` (`run` / `check` / `selftest`, 9 hermetic legs),
artifact `results/etf_lowvol_book.json`, S6 chain leg `etf_lowvol_book`, smoke leg that
recomputes the verdict from the per-cell tables.
**Question frozen before the run:** E227 left exactly two directions quotable
(`vol_60-`, `intraday_range-`) and four that move 1–3pp across cells (one flips outright).
Its published consequence was "the edge is a low-volatility tilt". A consequence that is
never priced is a slogan, so: **what does the book that uses ONLY those two directions do**
against the published six-sign vector, across the full 9-cell grid (N 3/5/8 × R 10/20/40)?

## Design

Two arms per cell, nothing else, same panel (5,269 bars × 1,612 symbols), same
eligibility, same engine (`fast_next_open`), same 10bp/side, same `START=2020-01-01`:

- `PROD` = the published six-sign vector (what the card runs today);
- `LV2` = `vol_60 -1`, `intraday_range -1`, the other four zero — `score_from` drops a zero
  factor and re-normalises by the number of active factors, so this is a genuine 2-factor
  score, not a zeroed 6-factor one.

Cells: the **full 9-cell grid**, not three corners — E227's own honest limit was
"unstable across THESE cells", and the low-vol pair is the claim that was supposed to
survive it, so the claim gets the whole grid. Verdict rule frozen in the source, echoed in
the payload, recomputed by the gate from the per-cell `d_cagr` / `d_sharpe` columns.

## Reading

| cell | PROD CAGR | PROD SR | PROD maxDD | LV2 CAGR | LV2 SR | LV2 maxDD | ΔCAGR |
|---|---|---|---|---|---|---|---|
| R10_N3 | +4.10% | 0.474 | −15.1% | −1.45% | −4.091 | −9.5% | **−5.55pp** |
| R20_N3 | +5.88% | 0.633 | −19.6% | −0.81% | −2.806 | −5.4% | **−6.69pp** |
| R40_N3 | +5.19% | 0.545 | −13.1% | −0.41% | −1.732 | −2.8% | **−5.60pp** |
| R10_N5 | +5.34% | 0.572 | −18.9% | −1.07% | −2.695 | −7.1% | **−6.41pp** |
| R20_N5 | +7.86% | 0.809 | −15.4% | −0.59% | −1.704 | −4.0% | **−8.45pp** |
| R40_N5 | +5.53% | 0.583 | −12.8% | −0.33% | −0.995 | −2.2% | **−5.86pp** |
| R10_N8 | +6.39% | 0.674 | −16.6% | −0.52% | −0.458 | −4.4% | **−6.91pp** |
| R20_N8 | +6.84% | 0.688 | −14.0% | −0.02% | −0.018 | −2.2% | **−6.86pp** |
| R40_N8 | +3.59% | 0.394 | −13.3% | +0.54% | 0.552 | −1.2% | **−3.05pp** |

Gate verdict: **`lowvol_worse`** — LV2 beats PROD on return at **0 of 9** cells, is inside
the 1pp tolerance at 0 of 9, and beats it on Sharpe at 1 of 9 (the slowest cell). Median
ΔCAGR **−6.41pp/yr**. The OOS block (≥2024-01-01, reported and never used by the verdict) is
negative at all nine cells, −6.5 to −15.4pp.

## What this changes

1. **E227's consequence is half wrong and gets corrected.** "The edge is a low-volatility
   tilt" is true as an *attribution* statement and false as a *construction* statement:
   the two low-volatility signs are the only ones you may name, and they are not enough to
   build the book with. The card may keep the six-sign vector and must stop implying the
   other four are decoration.
2. **E219's "8.5 of 11.4pp is the low-vol pair" and this result do not contradict.** That
   was a main-effect decomposition *inside* a full factorial where the other four directions
   were present; it never said removing them costs nothing. The difference between a factor's
   attributable share and its contribution to a reduced book is exactly what this face prices:
   ≈6.4pp/yr of the book lives in the interaction, not in any single direction.
3. **The mechanism is visible in the risk column.** LV2 is not a return book with a loss —
   it is a *defensive* book: maxDD falls from −13…−20% to −1.2…−9.5% and turnover falls from
   1.02–1.28 to 0.21–0.75. Its gross return is ≈0 and the 10bp/side toll consumes the rest.
   Sharpest form of the same reading: LV2's Sharpe is monotone in turnover (R10_N8 −0.458 at
   0.209 turns → R40_N8 **+0.552** at 0.327), i.e. a low-information score dies of its own
   transaction cost, and only the slowest cell leaves it above water.
4. **Operational consequence:** LV2 is not a cheaper alternative to the production book and
   must not be shipped as one. What it *is* good for is stated positively: if a defensive
   sleeve is ever wanted, the low-vol pair buys the drawdown reduction (−4 to −14pp of maxDD)
   far more cheaply than the full vector does, and that is a different product, not a
   substitute.

## Honest limits

- Both arms are in-sample (the six published signs were chosen on this panel, r1335); this
  compares two sign vectors, it does not estimate a live return.
- LV2 was not optimised here — it is the subset E227 already certified as sign-stable — but
  it was still selected on the same panel, so the honest reading is "fewer knobs, no
  measured loss **for the six-sign book's competitors**", not a fresh out-of-sample arm.
- One cell family, one panel, one cost level. Turnover sensitivity is shown but only at
  10bp/side; the sign of that sensitivity (LV2 improving as turnover falls) is robust,
  its slope is not measured.
- ETF pool is today's listed set (survivorship); engine is the reference one (no impact
  cost, no gap risk). Unchanged caveats.

## Why the gate is the deliverable

The number a reader takes away is "0 of 9" and the sentence it kills. The gate re-derives
every `d_cagr` / `d_sharpe` from the arm tables, re-derives each cell's `active` flag from
its own trade census, echoes the declared grid, and recomputes the verdict from the frozen
rule; a hand-edited delta, a dropped cell or a stale verdict string all fail the gate
(three of the nine selftest legs are exactly those). The selftest also caught a live bug in
this round's own code: `d_sharpe` of exactly 0.0 was being read through `x or -9e9` and
counted as missing, which silently demoted `lowvol_replaces_production` to
`lowvol_no_material_loss` — zero is a legitimate delta, never a null.