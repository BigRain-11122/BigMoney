# DIGEST 2026-10-21 — E65: is the off-cycle penalty the calendar, or lateness?

Runner: `scripts/e39_panel_census.py entrydelay` (new leg, selftest 96/96, +2 hermetic legs).
Faces: `results/e44_midmonth/ENTRYDELAY-20261020.json`, `ENTRYDELAY-20261020-s20130101.json`.
Evidence cutoff 2026-10-20. Descriptive census: zero prereg, zero judgement, zero ledger booking, trial_count 0.

## Question

E59 put five off-cycle dates all 55-88bp/yr behind month-end with identical turnover; E63
switched the fee off (x0) and every gap shifted 0.0bp. So neither the calendar day nor the
trading cost explains it. The remaining candidate is lateness itself: hold the spec, universe
and rank cache fixed and move the month-end decision forward by 1/3/5/10 sessions.

Honest limit: the lag moves the **decision session** as well as the entry, so the delayed book
is re-ranked on the delayed date. This prices "decided and bought k sessions later".

## Result — newest era is a cliff, the full window is not a curve

Gaps versus month-end, annualised, bp/yr:

| lag | full window (2020 start) | full window (2013 start) | newest era 2024_now |
|-----|--------------------------|--------------------------|---------------------|
| +1  | -27 | -18 | **-43** |
| +3  | -17 | -34 | **-74** |
| +5  | -35 | -35 | **-74** |
| +10 | -70 | -47 | **-91** |

- The 2024_now column is **bit-identical between the two window starts** (-43/-74/-74/-91), the
  same start-invariance the E59/E63 newest-era columns showed, so it is the only column quotable
  on its own.
- One session late already costs 43bp; by three sessions the book has lost **74bp**, i.e. the
  entire off-cycle penalty (E59 dates: -56..-88bp). The boundary therefore behaves as a **cliff
  with a ~3-session lip**, not as a gradual distance-to-month-end slope.
- The full window is **non-monotone** (-17 at +3 is the mildest, -70 at +10 the deepest at a
  2020 start; -18/-34/-35/-47 at 2013) so lag sensitivity is not a stable full-sample property.
- Era signs disagree at a 2013 start: pre2017 -60/-112/-81/-89, 2017_2020 +7/+16/-11/-15,
  2021_2023 +26/+17/+15/-5. Lateness is era-signed; only the newest era is uniformly negative.

## Channels re-checked in the same run

Turnover 0.585-0.589 turns/yr (2020 start) and 0.569-0.576 (2013 start), x1 fee 7.6-7.7bp/yr —
both inside the band E59/E63 already priced, so lag does not change how much the book trades.
Month-end x1 full-window annualised: 0.86% (2020 start) / 7.95% (2013 start), falling to 0.16%
and 7.48% at +10 sessions.

## Reading

The month-end date is not one of six equally good calendars (E59) and not a fee artefact (E63);
it is a **timing point with a sharp right-hand cliff**. Whether the left-hand side is symmetric
(the open question E66 prices: -1/-3/-5/-10 sessions) decides whether month-end is a point or a
deadline.

## Pits

- A lag ladder that only looks forward cannot tell a cliff from a one-sided slope: the newest
  era reads monotone, the full window reads non-monotone, so publish both or the lag effect looks
  orderly when it is era-local.
- The lag moves the decision date, not just the fill: without an execution-lag hook in the
  engine, "the same names bought later" is not measurable here and must not be claimed.