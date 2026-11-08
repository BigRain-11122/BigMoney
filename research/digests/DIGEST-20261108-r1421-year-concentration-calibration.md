# DIGEST 2026-11-08 r1421 — the concentration line was a Sharpe test wearing a costume

**Card** E425 · **Face** `results/admission/YEAR-CONC-CALIBRATION.json` ·
**Producer** `scripts/year_concentration_calibration.py` (selftest 18/18) ·
**Smoke leg** one (`selftest`)

## What was missing

Three of the five books the desk publishes were refused by one frozen row: **Y4, top two
calendar years ≤ 70% of the annual sum** — `nobond_vt08` 71.08%, `all_classes` 77.19%,
`breadth_ALL` 79.34%. r1418 had already cut Y4's reading down to a single week of decision
phase (71.08 → 79.62 across five starts), but nobody had asked the cheaper question: **what
does the 70% line measure at all?**

The other three frozen lines each mean something on their own (≥70% positive years, worst
year ≥ −15pp, ≥20M CNY of one-day capacity). "Two of seven years" does not, because the
share is **scale-invariant**: a book whose annual returns are draws from a process with mean
*m* and sd *s* has a top-2 share that depends only on *m/s*. If that is true, Y4 is an
annual-Sharpe test in a concentration costume, and "CONDITIONAL" was never evidence about
concentration.

## What was done

`scripts/year_concentration_calibration.py` builds the null Y4 never had and prices five
published books against it. No book is re-priced: every year row is read out of
`results/etf_book_year_gate/YEAR-GATE.json` and `results/admission/CANDIDATES.json`.

* null = stationary iid normal annual returns at the book's own annual Sharpe, 200,000 draws,
  seed 20261108 (120,000 draws per grid point over Sharpe 0.20–3.00);
* a second aggregator per E213: an empirical bootstrap of the book's own seven years;
* a second statistic `C2` = top-2 **|years|** / Σ**|years|**, which does not explode when the
  signed annual sum is near zero;
* inversion: the Sharpe at which the null **median** equals the frozen line;
* a Sharpe-conditional replacement line: pass if the observed share is at or below the null's
  95% quantile at the book's own Sharpe.

## Readings

**1. The line is a Sharpe demand of 0.705.** A book with annual Sharpe 0.705 has a *median*
top-2 share of exactly 70%. Below that Sharpe, Y4 fails by arithmetic even when the years are
exactly independent draws. Share of books failing the line by null Sharpe: 66% at Sharpe 0.50,
42% at 0.80, 20% at 1.10, 1.7% at 1.70.

**2. Every live book is statistically ordinary — the check flags none of them.**

| book | top-2 share | annual Sharpe | implied Sharpe from its own share | percentile under its own null |
|---|---|---|---|---|
| nobond_vt08 (adopted) | 71.08% | 0.799 | 0.685 | **59.5%** |
| nobond_base | 68.98% | 0.871 | 0.725 | 62.1% |
| all_classes | 77.19% | 0.730 | 0.583 | 62.1% |
| smallcap n20 | 69.51% | 0.751 | 0.715 | 53.0% |
| breadth ALL | 79.34% | 0.602 | 0.552 | 54.1% |

Each book's own share implies almost exactly its realised Sharpe (0.685 vs 0.799; 0.725 vs
0.871; 0.583 vs 0.730; 0.715 vs 0.751; 0.552 vs 0.602). The statistic is reporting Sharpe and
nothing else. Both aggregators agree on all five (`typical` × 5) — no disagreement to report.

**3. The check has no power — pinned by a fixture, not asserted.** A book whose two years
carry **95%** of its entire profit (`90/95/2/2/2/2/2`, share 0.949, annual Sharpe 0.63) reads
only the **70th percentile** of peers with its own Sharpe. The fixed line does fire on it, but
so would it on a book built purely from the null — the check cannot tell a 95%-carried book
from an ordinary one at the same Sharpe.

**4. Why it has no power: C1 is unbounded.** The denominator is a *signed* sum, so the
statistic exceeds 1.0 whenever a year is negative. Its own 95% band at the desk's Sharpe range
is 1.66 (0.80), 1.42 (0.87), 1.98 (0.73), 1.87 (0.75), 2.81 (0.60) — i.e. **for every book the
desk holds, the "beyond 95%" threshold is unreachable**. The upper tail is arithmetic, not
concentration.

**5. C2 does the job the line claimed.** C2's null median is nearly Sharpe-flat (0.527 at
Sharpe 0.60 → 0.431 at 2.00, a 9.4pp move) while C1's falls 32.7pp over the same range. Read
against its own null, C2 flags exactly the three ETF arms and none of the A-share books:

| book | C2 | C2 percentile under own null | beyond 95%? |
|---|---|---|---|
| nobond_vt08 | 0.711 | 97.8% | **yes** |
| nobond_base | 0.690 | 96.9% | **yes** |
| all_classes | 0.746 | 99.0% | **yes** |
| smallcap n20 | 0.538 | 58.7% | no |
| breadth ALL | 0.480 | 28.4% | no |

So the concentration is real — but it lives in the ETF books' **magnitudes** (the 2025 year is
a large share of everything that moved), not in the arithmetic of a signed sum that happens to
be small.

## Consequence for the desk

* **No production change.** The adopted book stays where it is; this face moves no line and
  re-prices no book.
* **The three Y4-driven CONDITIONAL verdicts carry no concentration evidence.** They are the
  line firing on books whose Sharpe sits below 0.705. `nobond_vt08`'s 71.08% is the most
  ordinary number in the table (59.5th percentile).
* **The replacement question is now well-posed.** If the desk wants a concentration check, C2
  with a null-calibrated line is the one that discriminates (three of five books flagged, and
  the flag means something). Replacing Y4 is a **law change** and gets its own prereg — not a
  line picked after seeing these numbers.
* **What a reader should stop doing:** quoting "CONDITIONAL: top-2 years carry 71%" as a
  warning about the book. Quote it as "this book's calendar is indistinguishable from seven
  independent draws at its own Sharpe".

## Honest limits

* The null is iid normal. Real books cluster in crises and would be **more** concentrated, so a
  book inside the band is not proof of independence — only that its shape is not unusual.
* Sharpe is plugged in from the same seven years, so the band is narrower than a null that
  accounts for estimation error; the direction of that error makes readings conservative.
* Seven annual observations cannot separate luck from process. The percentile says whether the
  *shape* is unusual for its own Sharpe, nothing more.
* A non-positive annual sum publishes no share; it is never read as 0 or 1.