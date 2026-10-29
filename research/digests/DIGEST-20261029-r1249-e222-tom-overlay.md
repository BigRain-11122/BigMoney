# E222 — the turn-of-month shape is not tradable at this panel's resolution

Round 1249, bm-b. Runner `scripts/e222_tom_overlay.py`, face
`results/tom_overlay/TOMO-20261028.json`, card E222.

## Why this exists

E221 measured the month boundary over the whole ETF universe and closed honestly:
the mass sits on the **turn of the month** (last session +19.20bp t=2.13, first
session +27.47bp t=2.69, the pair +23.32bp t=3.43), but that shape was found after
looking at a 21-cell ladder, so it shipped as *a pre-registerable candidate, not a
finding*.

E222 asks the only question that matters to a book: **if you actually traded it,
would it survive?** Same calendar shape, one tradable instrument, costs, a frozen
in-sample / out-of-sample split, and the decision rule in code.

## The rule under test, frozen before the numbers

Hold only during the month's two boundary sessions — its FIRST and its LAST. Because
the last session of month M is adjacent to the first session of M+1, that is one
contiguous hold across the boundary and costs **one round trip per month** (2 sides
at 13.041bp). Cash earns 0% (this omission favours the overlay).

Decision rule, frozen in code and echoed on the face for a gate to check:
ADOPT iff OOS months ≥ 24 **and** OOS net excess/yr > 0 **and** OOS t ≥ the 3-way
Bonferroni bar (2.39) **and** the arm is still net at double costs.

## What was measured

`sh510300`, 3,503 sessions, 173 months, cutoff 2026-10-28; IS = first 60% (103
months), OOS = 70 months. Time in market 9.9%.

| variant | net bp/month | OOS net excess/yr | OOS t | at x2 costs | verdict |
|---|---|---|---|---|---|
| turn-of-month (first+last) | +21.84 | **+429.0** | 0.65 | +116.0 | REJECT |
| last session only | -4.03 | +42.5 | 0.06 | -270.5 | REJECT |
| first session only | -0.21 | +328.5 | 0.43 | +15.6 | REJECT |
| always-in (benchmark) | — | 554.0bp/yr | — | — | — |

Equal-weight five-ETF basket arm: same verdict on all three variants (turn-of-month
excess +289.2bp/yr, t=0.36, always-in 650.9bp/yr).

## The load-bearing readings

1. **Over the whole sample the overlay loses to simply holding.** Net +262.1bp/yr on
   9.9% time in market against 554.0bp/yr for buy-and-hold: excess **-291.9bp/yr**.
   The premium the boundary sessions carry does not pay for twenty round trips a year.
2. **The sign flips between in-sample and out-of-sample.** IS excess -65.1bp/month,
   OOS +35.7bp/month. An effect whose sign disagrees with itself across the split is
   not a rule, it is noise sampled twice.
3. **Settling it would take 110 years.** sd of the monthly excess is 463bp, so a
   35.7bp/month excess needs **1,317 months (~109.7 years)** at 80% power. The panel
   has 173 months. This is the same wall E219 hit from the other side: a calendar rule
   is observed once per MONTH, so width buys nothing and history is the only currency —
   and this instrument does not have enough of it.

## Pits worth keeping

* **The wall is not the instrument, it is the calendar.** Widening from one ETF to the
  five-ETF basket changed the excess by a factor of 1.5 and the t from 0.65 to 0.36 —
  noise movement, not resolution.
* **Zero-variance fixtures make the REJECT branch unreachable.** A deterministic
  constant premium has se == 0, so the verdict came back `oos_series_unusable` and the
  REJECT path was never exercised; the leg now asserts dispersion first, then the
  verdict (r1261 family).
* **Dropping unpriced months after the split reads one month short.** The panel's first
  session has no previous close, so month 1 has no `first_bp`; filtering inside the arm
  rather than before the split made OOS read 23 against a 24 floor. Usable months are
  now filtered *before* the split, and a leg pins the count.
* **A month boundary is session-adjacent by construction** — the calendar has no holes,
  so "adjacency violations" is a vacuous check. The face publishes `single_session_months`
  instead, which is the case that actually breaks the two-session reading.

## Pieces

`scripts/e222_tom_overlay.py` (`run` / `selftest`, 24 hermetic legs); face
`results/tom_overlay/TOMO-<cutoff>.json` + `latest.json`; S6 leg `tom_overlay` right
after `dom_profile`; smoke leg that recomputes the excess identity and rejects an ADOPT
that never cleared the bar; card E222.