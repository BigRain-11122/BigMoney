# DIGEST 2026-11-08 r1418 — the desk's own book had never faced its own calendar gate

**Card** E422 · **Face** `results/etf_book_year_gate/YEAR-GATE.json` ·
**Producer** `scripts/etf_book_year_gate.py` (selftest 10/10, check 18/18) ·
**Smoke legs** two (`selftest`, `check`)

## What was missing

r1415 created the calendar gate and pointed it at two **candidate** books. The book the
desk actually holds — the bond-free ETF composite with the 8% volatility target
(`results/etf_nobond_vt.json`, `nobond_vt08`, adopted 2026-10-25 as the production
candidate) — was never put through it. A gate that only ever judges candidates is not a
gate on the desk.

## What was done

Repriced three arms with the published engine (imported, never re-implemented), cut
calendar-year returns off each arm's own level curve, and re-issued verdicts through
`candidate_year_gate.admission_block()` — the frozen 70% / −15pp / ≥70%-positive / 20M
capacity lines are **imported**, so the two files cannot drift apart.

One substitution, printed not hidden: the candidate receipts count 60-bar cohorts per
year and mark a year partial below four. A daily book has no cohorts, so the same 60-bar
unit is used as a window count (floor(bars/60)); 2026 lands at 3 and is partial.

## Readings

| arm | verdict | failing check | top-2 share | worst year | CAGR |
|---|---|---|---|---|---|
| nobond_vt08 **adopted** | CONDITIONAL | Y4 top-2 ≤70% | **71.08%** (+1.08pp over) | +1.90pp | 11.46% |
| nobond_base | ADMIT | — | 68.98% | +2.33pp | 15.51% |
| all_classes (published yearly) | CONDITIONAL | Y4 | 77.19% | −1.17pp | — |

Adopted arm: 7/7 positive years, median +5.61pp, capacity 48.67M CNY/day at 5%
participation across the five live slots (512040/159519/515450/510760/515300, asof
2026-11-06).

The cause is printed on the same face — the 8% target's average position scale per year:

```
2020 0.455 | 2021 0.735 | 2022 0.800 | 2023 0.858 | 2024 0.712 | 2025 0.665 | 2026 0.665
```

It cut 2020 to less than half (the year the base book made +22.19%) but only cut 2025 to
0.665, where the book still made +43.06%. Trimming the peak without trimming the peak
year raises calendar concentration. The overlay that made the book "better on all four
axes" (CAGR / Sharpe / drawdown / turnover) is the step that pushed it over the line.

## Reusable

1. A risk overlay has a **calendar** side effect. "Better drawdown and Sharpe" and "narrower
   source of returns" are different claims; an adoption rule that omits the year axis
   cannot see the second.
2. Freeze the line by **import**, not by re-typing it.
3. A **level curve is not a return series**. Cumprod-ing levels printed 3.7e76 → inf in the
   first draft; the selftest leg "each year is last/first on the book's own definition"
   caught it. Any window function over an existing curve must first ask which one it holds.

## Not measurable here

ETF universe is survivorship-biased; 2026 is an 8.6-month stub and is disclosed, never
annualised; capacity is derived from the current five slots, not a declared AUM.