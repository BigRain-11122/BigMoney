# E227 — the sign ordering is a property of the (cadence, width) cell, not of the factors (r1339 bm-c)

**Card:** E227 in `knowledge/METHODOLOGY_ASSETS.md`.
**Code:** `scripts/etf_sign_cells.py` — selftest 11/11, S6 chain leg `etf_sign_cells` (~180s),
artifact `results/etf_sign_cells.json`, smoke leg that re-derives the verdict from the
per-cell arm tables.
**Question frozen before the run:** every published number on the ETF book line is produced
at one cell, `REBAL=20, N_HOLD=12`. But 20 and 12 are not physical constants — the
walk-forward on this line selects among `N3/5/8 × R10/20/40`, i.e. cadence and width were
*also* picked on the sample. E207/E218/E219 priced the sign choice but evaluated every arm
at that one cell. So: does the sign ordering survive the cells it was chosen among?

## Design

Three declared cells — `R20_N12` (the primary), `R10_N8`, `R40_N5` — each with all 2^6 = 64
sign sets. Same panel (5,268 bars × 1,609 symbols), same eligibility, same engine
(`fast_next_open`), same 10bp/side, same `START=2020-01-01`. The only thing that differs is
`(rebal, n_hold)`. Verdict rule recomputed by the gate from the arm tables, never typed.

## Reading

| cell | production rank | production CAGR | median arm | spread |
|---|---|---|---|---|
| R20_N12 | **6/64** | +6.14% | −1.63% | 20.8pp |
| R10_N8 | **4/64** | +6.42% | −4.85% | 28.6pp |
| R40_N5 | **5/64** | +5.54% | −1.70% | 37.3pp |

Per-factor main effect, pp/yr (the full factorial makes each one a difference of half-means):

| factor | R20_N12 | R10_N8 | R40_N5 | sign stable? |
|---|---|---|---|---|
| `vol_60` | −4.87 | −5.76 | −4.87 | **yes** |
| `intraday_range` | −3.65 | −4.49 | −3.80 | **yes** |
| `mom_12_1` | −1.37 | −0.81 | −0.94 | **yes** (published `+` is a drag *everywhere*) |
| `adx_14` | +2.01 | −0.17 | −0.48 | no |
| `drawdown_60` | +1.06 | +0.63 | −0.45 | no |
| `price_position` | +1.15 | +3.09 | **−3.30** | no |

Gate verdict: **`sign_order_cell_dependent`** — 3 of 6 factors keep their direction across
the three cells.

## What this changes

1. **The top-decile result replicates, the ordering does not.** The production arm is in the
   top decile at every cell (ranks 4–6 of 64) and the no-hindsight median is negative at every
   cell. So "the published book sits near the sample optimum" is not an artefact of R20×12.
2. **Only the low-volatility pair is a real direction.** `vol_60−` and `intraday_range−` are
   worth −3.7 to −5.8pp/yr each at every cell, and they are the two effects E219 already
   identified as carrying the edge (8.5 of 11.4pp). Everything else moves by 1–3pp and one
   factor (`price_position`) flips sign outright.
3. **Momentum is the exception that matters for the card:** the published `mom_12_1` sign is
   `+` and the effect is negative at every cell — it is a drag that survives the cell choice,
   i.e. the one published direction that is *consistently* wrong rather than sometimes wrong.
4. **Consequence published:** no per-factor direction other than the two low-volatility signs
   may be quoted as a property of the factor. The card may say "the book is near the sample
   optimum at every cell we measured" and "the edge is a low-volatility tilt"; it may not say
   "factor X pays in direction Y" on the strength of the R20×12 table alone.

## Honest limits

- Three corners of the grid, not the full nine cells — declared and echoed in the payload, so
  "unstable" means unstable across *these* cells.
- All six arms' numbers are in-sample by construction; this compares three in-sample optima.
- The top decile does **not** reduce to "get the two low-vol signs right": 5/7, 4/7 and 5/7 of
  the top-seven arms carry both, so the remaining four directions are still doing work — just
  work that cannot be *attributed* to a factor.
- ETF pool is today's listed set (survivorship), unchanged caveat.

## Why the gate is the deliverable, not the table

The number a reader takes away is `3/6 stable`. The gate re-derives that count from the
per-cell `main_effect_pp` maps, re-derives each cell's `active` flag from its own trade
census (all 64 arms traded, spread ≥ the declared floor), and re-derives each production rank
from that cell's arm table. A stored verdict cannot outlive a panel move, and the two fixtures
were measured before the run: one factor flipping reads `partly_stable`, alternating whole
cells read `cell_dependent`, a flattened or untraded grid is refused rather than called stable.