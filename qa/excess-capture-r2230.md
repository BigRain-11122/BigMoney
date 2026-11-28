# r2230 — excess capture: does the book earn its excess up, down, or only on a few bars?

**Face**: `scripts/etf_book_excess_capture.py`
**Artifacts**: `results/etf_book_excess/capture.json`, `research/ETF_BOOK_EXCESS_CAPTURE.md`
**Generated**: 2026-11-29 (r2230, bm-c). `evidence_cutoff = 2026-11-27`.

## Why it exists

r2229 answered "is the live loss normal" and printed, on the way past, `+2.79pp` of excess
on the live 26-bar window. That number says the work may be right; it does not say *where*
the work is done. A book that beats its basket only by dropping less is insurance; one that
beats it by rising more is selection. Both print the same `+x pp`, and the reader is asked
to add capital on the strength of it.

## What it measures

Same state machine (`etf_book_forward.Forward`), same grid, same next-open fill, carry on
for both arms. Three tapes on the same bars:

| arm | description |
|---|---|
| basket | `F.bench_block` — four-exposure equal weight, the ruler r2229 used |
| base_book | the same selection at full size, **no** vol overlay (the SELECTION arm) |
| production | `F.CONFIG` — 12 names, 8% vol target, 10bp/side (the headline arm) |

Excess is split by the **basket's** bar sign into up-bars / down-bars, and every half
reports bars, both sums, the capture ratio and its pp/yr share of the log excess.

## Readout

**verdict = `NEAR_PARITY_BOTH_SIDES_BUT_CARRIED_BY_FEW_BARS`**

* selection arm vs basket: up capture **1.037** (914 bars), down capture **0.976** (758 bars),
  total **+3.085 pp/yr**
* production vs basket: **-0.554 pp/yr**; the vol target costs **-3.639 pp/yr** of that
  selection edge (mean cash 29.1%)
* concentration: the best 167 bars (10%) carry **953.1%** of the total log excess; removing
  them leaves **-26.322 pp/yr**
* yearly sign (selection): positive in 2021/2022/2025/2026, negative in 2020/2023/2024
* risk yardstick on the same table: basket 9.33% CAGR / 10.6% vol / 0.90 Sharpe / -14.0% DD;
  selection 12.76% / 15.1% / 0.87 / -16.3%; production 8.73% / 9.9% / 0.89 / -13.3%

The honest sentence: the selection edge is **real but thin on both sides** (3.7% / 2.4% of
the half-sums) and **almost entirely carried by a tenth of the bars** — a handful of spread
days on a 12-name book against a 4-ETF basket. That is not a licence to read `+3.1 pp/yr`
as a repeatable annual rate.

## Verification

| check | result |
|---|---|
| `--selftest` | **14/14 PASS** |
| `run` | rc0, 64s (two books + basket over 1,673 bars) |
| `--check` | rc0 — artifact self-consistent, markdown matches artifact byte-for-byte |
| negative control | edited one published number in the `.md` → `CHECK FAILED` rc4; restored → rc0 |
| identity | up + down log excess == total (residual < 1e-12 on this panel) |

## Selftest legs (what each one would catch)

1. halves add to the whole — a split that does not is an attribution of a different book
2. up/down/flat partition the bars — no bar may be counted twice or dropped
3. a half-size book captures 0.5 both ways — the ratio's definition
4. defense-only (1.0 up / 0.5 down) is not called alpha
5. a 3% capture gap → `NEAR_PARITY`, not `ALPHA` (the band that keeps this face honest)
6. a 10% capture gap keeps the alpha word (negative control on the band itself)
7. up-doubling with wider losses → `PAYS_MORE_IN_REVERSALS_THAN_IT_DODGES`
8. one-sided basket → capture `None`, verdict `UNMEASURABLE_ONE_SIDED_BASKET` (never 0 or 1)
9. single-bar excess is 100% concentrated; removing it leaves exactly zero
10. even excess is ≤20% concentrated (the concentration measure is not stuck at 1)
11. yearly signs split at the calendar boundary

## Caveats carried in the artifact

* capture ratios are **sums over a half**, not means — a half with a few violent bars must
  not be averaged against the other half's many quiet bars
* the basket is the same four-exposure ruler r2229 printed +2.79pp on, **not** a 26-bar
  window: the two numbers answer different questions and may not stand in for each other
* the production row's capture is structurally below 1 in up-bars (29.1% mean cash); reading
  that as bad selection is the error this face exists to prevent
* the pool is today's listed ETFs — survivorship inherited from the backtest, not introduced

## Methodology (to be merged into `knowledge/METHODOLOGY_ASSETS.md` next round)

**A ratio within the noise band of 1.0 is parity, not edge.** With ~900 bars per half, a
3–4% gap in the half-sums is one or two ordinary spread days; printing it as "alpha on both
sides" overstates it by an order of magnitude. The face therefore carries an explicit
`NEAR_PARITY_BAND = 0.05` and a selftest leg on each side of the band (3% → parity,
10% → alpha), so the word cannot drift.

**An excess carried by 10% of the bars is not an annual rate.** Printing `+3.1 pp/yr` beside
`-26.3 pp/yr once the best 10% of bars are removed` is the only pairing that lets a reader
see which number is the instrument and which is the arithmetic.
