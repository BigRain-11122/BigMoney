# E250 — the shared negative lag-1 lead *is* the book's own aggregate turnover

**Card:** E250 · **Runner:** `scripts/e250_book_turnover_echo.py` (selftest 15/15) ·
**Face:** `results/state_tilt/BOOKECHO-2026-10-29.json` + `bookecho_latest.json` ·
**Evidence cutoff:** 2026-10-29 · **S6 leg:** `book_echo` · **NO BILL.**

## The question E249 left open

E249 read all five columns of the star row and found every one of them negative at comparable
magnitude (spread 0.352 inside a 0.384 within-column band), in every era. That killed the
star-specific naming, but it did not name the mechanism: something makes each member's move
respond negatively to *any* member's previous turnover. The candidate: the five columns are all
proxies for ONE book-level quantity — aggregate turnover — and the book's next move loads on it.

## What was measured

Three designs, same members, same rows, same estimator:

| design | row |
|---|---|
| A | `dy_m = a + b_own·dx_m[t] + b1_c·dx_c[t-1]` (E249's per-column row) |
| B | `dy_m = a + b_own·dx_m[t] + c1·dagg[t-1]` |
| C | `dy_m = a + b_own·dx_m[t] + b1_c·dx_c[t-1] + c1·dagg_exC[t-1]` |

`dagg[t] = log Σ_s turnover_s(t) − log Σ_s turnover_s(t−1)` on the common grid, built from
**levels** (a sum of log-differences is not a log-difference of sums). `dagg_exC` drops the
column itself from the sum.

## The answer

Headline cell (`all_five`, 1,328 sessions, 2020-11-17 → 2026-10-29):

* **c1 = −0.521**, against a 200-draw shuffled-aggregate band of **[−0.206, 0.201]** — outside it.
* Per-column lag-1 shrinks toward zero once the leave-one-out aggregate is in the row:
  **mean share 0.913** (0.10 → 1.32 per column). The inclusive-sum share is 1.409, which is the
  E238 denominator-contains-the-numerator artefact, published beside it and never quoted alone.
* Across the six cells c1 runs −0.50 … −0.68, negative and outside its own band in **5 of 6**;
  the exception is `era_2020_2022` (−0.316 inside [−0.376, 0.237]) — inside the band, so that
  cell is silent, not contrary.

So: the shared lead is a **book-wide** quantity, and it is the book's previous aggregate
turnover. No sleeve may be billed for it.

## The one thing the aggregate does NOT take

The star column `sh588000` keeps ~90% of its −0.805 reading once the leave-one-out aggregate is
in (share 0.10), against 0.10–0.60 for the other four. The star is therefore *not* merely the
column the fit reads most cleanly: it carries an own component the book-wide number does not
explain. That residual is the only sleeve-attributed part of the E248/E249 reading left standing,
and it is what E251 is for.

## Identification caveat (published on the face)

E240 read this regressor in a **cross-sectional** design where date fixed effects absorbed it.
This is the **time-series** version, and date effects cannot be included because the regressor of
interest *is* per-date. The two numbers must never be quoted against each other. The
omitted-variable amplification factor (1+(k−1)ρ−kρ²)/(1−ρ²) is published per cell: **2.19** at
headline (k=5, ρ=0.424), 1.52–2.30 across cells.

## Two traps this face paid for in-window

1. **The increment-date grid is one row short.** Building the aggregate series from
   `panel["dates"]` (the increment dates) instead of the level dates produced 1,327 values against
   1,328 panel rows, so every lag slid by one session — and the first burn came out with c1 =
   **+0.644** (a positive coefficient, comfortably outside the band, on a panel whose columns are
   all negative). The alignment assertion in `cell()` and a selftest length leg now refuse it.
2. **A column inside the sum is not evidence.** The first draft's "share absorbed" used the
   aggregate the column sits inside, and three columns read a share > 2. That is the E238 family:
   the denominator contains the numerator. The leave-one-out sum is the readable number; both are
   published so the arithmetic channel is visible rather than hidden.

## Handoff

* E250 row closed with `result_ref`; **E251-STAR-OWN-COMPONENT** seeded ready.
* Do **not** re-read E240's cross-sectional number beside this one.