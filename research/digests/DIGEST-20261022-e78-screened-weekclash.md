# E78 — does the weekly-vs-monthly residual survive the split screen? (r1149 bm-b)

Evidence cutoff 2026-10-21. Face: `results/e44_midmonth/WEEKCLASH-20261021-screened.json`.
Runner: `python scripts/e39_panel_census.py screenweek` (4 universes × 8 books = 32 runs, 39 s, CPU-only).
Loader: `scripts/panel_screen.py` via `run_midsweep(raw=...)` — opt-in, no published WEEKCLASH face rewritten.

## Question

E77 showed the split screen moves the wide book exactly in 2021_2023 and 2024_now —
the two eras the weekly-vs-monthly chain (E63/E69/E70) has been pricing its
residual in for six rounds. So: how much of that residual is unadjusted corporate
actions, and how much is real?

Two books, one universe, one rank cache, two cost levels:

- `week` — the full ISO weekly grid (349 decision days; ~4.3× the month-end rate).
  Its gap against month-end mixes the calendar with the trading frequency.
- `week_near_me` — the SAME weekly grid cut to one decision per month at the weekly
  session nearest the boundary (82 decision days). Frequency held fixed: this is the
  book that prices the DATE, and the one the chain quotes as the residual.

## Answer — the residual is not an artefact; the frequency-mixed book partly is

Frequency-matched residual (`week_near_me` vs month-end, bp/yr):

| cost | unscreened | neutralise (int) | neutralise (all) | drop |
|---|---|---|---|---|
| x1 | −11 | −12 | −9 | −11 |
| x3 | −12 | −12 | −9 | −12 |

Worst correction on the residual: **+3bp** (`x3`, all-adjacent screen) against a
−12bp residual — the residual keeps 75–109% of its size, and **no era flips sign**
under any mode. The weekly-vs-monthly residual is *not* contaminated by the 135
adjacent-impossibility prints.

The frequency-mixed raw weekly book does move, and the movement is where the prints
sit (`week` vs month-end, bp/yr):

| cost | unscreened | neutralise (int) | neutralise (all) | drop |
|---|---|---|---|---|
| x1 | −55 | −48 | −46 | −42 |
| x3 | −61 | −53 | −51 | −47 |

i.e. 7–13bp of the −55bp raw gap is corporate-action arithmetic (13–24%). Era
detail at x1: `2021_2023` −67 → −48/−49/−48, `2024_now` −63 → −62/−59/−49.
`2017_2020` reads exactly 0.0 in every mode (cash-only burn-in slice) and `pre2017`
has no weekly bars — both published as read, not as robustness.

Turnover control (the screen moves the return path, not the traded book):

| book | x1 turnover | x1 cost/yr | screened delta |
|---|---|---|---|
| week | 0.789 | 10.3bp | −0.001 (neutralise), −0.005 (drop) |
| week_near_me | 0.595 | 7.8bp | −0.001…−0.002 |

28 delta cells, 20 non-zero; the two neutralise columns move the residual by
−1…+2bp while the raw weekly gap moves +7…+16bp — the artefact lives in the
frequency-mixed book, not in the boundary-date read.

## Honest limits

- The screen repairs arithmetic impossibility only; a flagged ETF print may be
  genuine, so `neutralise` is a sensitivity face, not truth. Integer-only is stricter.
- `drop` also changes the universe (1,265 → 1,136 names), so its delta mixes the
  correction with a composition change.
- `week_near_me` snaps each month-end to the nearest weekly session, so its decisions
  sit 1–3 sessions inside the boundary; that offset is the price of being on the
  weekly grid, not noise, and it is unchanged by the screen.
- Gapped prints are never repaired, so a residual carried by a behind-suspension
  print would read flat rather than corrected (E75/E76 precedent).
- Descriptive census only: no gate, no verdict, no prereg, no trial booking.

## Pointer

The -11bp residual the chain chased for six rounds stands as a calendar effect, not
a data artefact. What remains unmeasured is which *other* published faces read
per-name returns off the unscreened loader — that enumeration is
E79-PUBLISHED-FACE-CONTAMINATION-SWEEP (queued ready).