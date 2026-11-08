# DIGEST 2026-11-08 r1423 — the big year is broad; the quiet year is the bet

**Card** E429 · **Face** `results/etf_book_year_attribution.json` ·
**Producer** `scripts/etf_book_year_attribution.py` (selftest 6/6, `check` PASS) ·
**Smoke legs** two · **cross-check** against `results/etf_book_year_gate/YEAR-GATE.json`

## What was missing

r1421 settled what the frozen top-2-years line measures (annual Sharpe in a costume) and
left one statistic that discriminates: `C2 = top-2 |years| / sum |years|`, which puts the
adopted book at the **97.8th percentile** of its own null. That reading says the
concentration lives in the **magnitudes** — 2025 is a large share of everything that
moved. But no face said **which names produced the magnitudes**. "The book had a big
year" and "one bet had a big year" print the same number and need opposite repairs
(hold the book vs cap a sleeve).

## What was done

One loop copied from `etf_robust_pf.open_to_open_equity` (verified **bit-identical**, a
selftest leg, not a hope) books every bar's log return into (year, name) and (year, asset
class) buckets, with toll kept on its own line:

    bar log return  = log1p(sum_c w_c * (open_next/open - 1))   split by contribution
    decision bar   += -log1p(1 - cost * turnover)               named 'toll'

Per calendar year `sleeves + toll == the year's log return` exactly (max identity gap
6e-7 pp) and the years add up to the book's log growth. Two arms: production
(`nobond_vt08`, 8% vol target) and its un-overlaid twin (`nobond_base`).

Year base, printed rather than hidden: a year runs from the **last bar of the previous
year** to its own last bar, so the entering bar is included; the gate's own rows use
last/first *within* the year. The face carries a `cross_check_vs_year_gate` block with
every row's delta (max 1.94 pp, 2026 partial year; 2025 differs by −0.05 pp).

## Readings (production arm, log points, 10bp/side)

| year | net | log pp | equity | commodity | convertible | toll | avg scale |
|---|---|---|---|---|---|---|---|
| 2020 | +6.46% | 6.26 | **+6.94** | +0.28 | — | −0.97 | 0.455 |
| 2021 | +8.63% | 8.28 | +11.49 | −3.41 | +1.42 | −1.22 | 0.735 |
| 2022 | +3.11% | 3.07 | −3.37 | **+9.55** | −2.04 | −1.08 | 0.800 |
| 2023 | +5.88% | 5.71 | +5.70 | +2.49 | −0.68 | −1.80 | 0.858 |
| 2024 | +14.58% | 13.61 | +1.82 | **+12.85** | +0.29 | −1.36 | 0.712 |
| 2025 | +43.01% | 35.78 | **+17.65** | **+18.56** | +0.89 | −1.32 | 0.665 |
| 2026* | +2.36% | 2.33 | +1.43 | +1.32 | +0.81 | −1.22 | 0.665 |

\* partial year (cutoff 2026-11-06).

**1. The biggest year is the least concentrated one.** 2025's name HHI (on absolute
contributions) is **0.057**, the lowest in the sample, and its top name — 518800, a gold
ETF — carries **11.4%** of everything that moved. Its two engines are roughly equal:
commodity **+18.56 pp** and equity **+17.65 pp**. 2025 was not one bet, it was a broad
year with two sleeves pulling at once.

**2. The single-sleeve years are the quiet ones.** 2024 made 13.61 pp of which commodity
contributed **12.85 pp (94.4%)** and equity **+1.82 pp**, with the top three names all
gold (518800 3.61 / 159937 3.53 / 518880 3.05). 2022 is the same shape in miniature:
commodity **+9.55 pp** while equity −3.37 and convertible −2.04 — the whole year is gold
and non-ferrous (159980, 518800), carried against a losing equity book.

**3. So the top-2 concentration is not "one name in the big year".** It is one broad year
(2025) plus one single-sleeve year (2024). The lever that matches the finding is a
**per-sleeve cap on commodity**, not a per-name cap: a per-name cap would have moved
almost nothing (top name 11% of a year's movement happens in the *broad* year).

**4. The overlay changes size, not selection.** Comparing arms, 2020 goes from 21.12 pp
(base) to 6.26 pp (production) — the largest single loss in the book — while toll falls
from −2.02 pp to −0.97 pp and the top-three names in each year are the same list. The
vol target is a size dial: it cut the best year hardest (scale 0.455 in 2020) and left
2025 at 0.665 while it made +43%.

## Consequence for the desk

* **No production change.** This face re-prices nothing and moves no line.
* r1421's replacement question now has a shape: if the desk wants a concentration
  control, it is a **commodity sleeve cap** with its own prereg and path tests (E188:
  the cap has to be tested across decision phases, not on one sequence), not a per-name
  limit.
* The gold sleeve is the single biggest structural exposure in the book (2024 alone
  94% of a year). That is a fact about the book, not a verdict; 2025 shows the sleeve
  also works alongside equity rather than instead of it.

## Honest limits

* HHI is computed on **absolute contributions**, not weights — a year's name count is
  inflated by rotation (a name held for one 20-bar block still appears).
* "Commodity" here is essentially gold plus one non-ferrous ETF; classification is the
  same keyword+realised-vol rule as `etf_equity_alpha.classify`, so a misnamed ETF would
  mis-file its points.
* Splitting a bar pro rata by contribution attributes the cross-term of a homogeneous
  book correctly; it would not for a book with a large single-bar dispersion (5-name
  equal weights make this benign).
* Year definition differs from the gate's by the entering bar; both are printed.