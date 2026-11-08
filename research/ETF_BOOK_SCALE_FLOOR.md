# The sizing rule has a ceiling and no floor — and the yearly gate that condemned the book
# judges a single decision phase (r1419 bm-c)

r1418 put the desk's adopted book (bond-free composite + 8% vol target, `nobond_vt08`)
through the calendar gate for the first time and got CONDITIONAL, failing only Y4: top-2
years = 71.08% of the annual sum, 1.08pp over the 70% line. Its own brother without the
overlay ADMITTED at 68.98%. So the de-risking layer was the thing that pushed the book over.

The published sizing face says why: average scale per year was 2020 0.455 / 2021 0.735 /
2022 0.800 / 2023 0.858 / 2024 0.712 / 2025 0.665 / 2026 0.665. The rule is
`scale = min(1.0, target / est_vol)` — a ceiling, never a floor — so one noisy 60-bar
window can park the book at half size through an entire recovery.

## What was run

`scripts/etf_book_scale_floor.py` adds `vol_floor` to the published engine
(`etf_robust_pf.open_to_open_equity`, default 0.0 = bit-identical) and sweeps it. Yearly rows
are handed to the frozen gate (`candidate_year_gate.admission_block`, imported not copied);
capacity is read from the r1418 face, never hand-copied.

Bit-identity leg: floor = 0.0 reproduces **every published yearly row to 0.0** and the
per-year sizing scale to 0.0, plus CAGR 11.46% — the engine default did not move.

## Reading on one decision phase (2020-01-01, 1657 bars, 10bp/side)

| floor | verdict | top-2 share | CAGR | Sharpe | MaxDD |
|---|---|---|---|---|---|
| 0.0 (published) | CONDITIONAL | 71.08% | 11.46% | 1.128 | -10.56% |
| 0.4 | ADMIT | 69.53% | 11.74% | 1.145 | -10.56% |
| **0.5** | **ADMIT** | **66.85%** | **12.08%** | **1.148** | **-10.56%** |
| 0.6 | ADMIT | 63.67% | 12.68% | 1.145 | -10.67% |
| 0.7 | ADMIT | 62.95% | 13.21% | 1.112 | -11.59% |
| 0.8 | ADMIT | 64.68% | 13.72% | 1.061 | -13.01% |
| 1.0 (= no overlay) | ADMIT | 68.98% | 15.51% | 0.999 | -16.04% |

On this phase a floor buys three things at once: concentration down, CAGR up, Sharpe slightly
up, drawdown **identically unchanged** at ≤0.5. When a "risk" overlay costs return *and*
concentration without buying drawdown, the missing floor is a defect, not a preference.

## But the phase test says the verdict is a lottery ticket

E188 requires a path test before adoption. The same two arms, four shifted decision phases:

| phase start | floor 0 | floor 0.5 | floor 0.5 better? |
|---|---|---|---|
| 2020-01-01 | CONDITIONAL 71.08% / 1.128 | ADMIT 66.85% / 1.148 | yes |
| 2020-01-08 | CONDITIONAL 79.46% / 1.041 | CONDITIONAL 74.58% / 1.102 | yes (return/Sharpe) |
| 2020-01-15 | CONDITIONAL 79.58% / 0.769 | CONDITIONAL 78.92% / 0.752 | **no** |
| 2020-01-22 | CONDITIONAL 79.82% / 0.678 | CONDITIONAL 79.95% / 0.701 | yes (return/Sharpe) |

Two findings, and the second is the bigger one:

1. **The floor is mildly good, not decisively good**: 3 of 4 phases improve return/Sharpe at
   floor 0.5, one does not (78.92% vs 79.58%, Sharpe 0.752 vs 0.769). Not a rule yet.
2. **The yearly gate's verdict on this book is decided by the phase, not by the book**:
   top-2 spans 71.08% → 79.82% across four start dates one week apart. r1418's 1.08pp miss is
   the *best* of those four readings. A gate that flips ADMIT/CONDITIONAL on 12pp of sampling
   noise will make adoption decisions out of a coin toss.

So the r1418 conclusion ("the book is CONDITIONAL by 1.08pp") is technically reproduced and
practically under-specified: on a phase-neutral reading the book misses Y4 by ~5-10pp, and
the *action* is not "tune the floor" but "the yearly gate must be phase-robust before it
adjudicates adoption".

## Decision this round

- Do **not** change the production sizing configuration on this evidence (phase test not
  clean; one phase loses).
- Do **not** retire r1418's gate: the rule is right, its single-phase application is not.
- Next: make the yearly gate take a phase set (report the median and the worst phase, and
  refuse to adjudicate when the spread across phases exceeds the distance to the line) — a
  gate that admits a book must also admit that it cannot tell.

## What was not measured

ETF universe is survivorship-biased (existing tickers); 2026 is an 8.6-month partial year,
disclosed and never annualised; capacity is a 5% participation figure on five slots, not an
AUM claim; the floor sweep only rescales the same selection sequence (picks are untouched),
so this is a sizing study and cannot speak to selection robustness.

Pos = `scripts/etf_book_scale_floor.py` (selftest 7/7) + `results/etf_book_scale_floor.json`
+ methodology card E423.