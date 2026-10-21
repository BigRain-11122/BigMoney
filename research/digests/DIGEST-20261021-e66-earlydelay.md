# DIGEST 2026-10-21 — E66: the month-end boundary is a point, and the right side is twice as expensive

**Unit:** E66-ONE-SESSION-EARLY (pool, cpu-only, bm-b)
**Runner:** `scripts/e39_panel_census.py earlydelay` (selftest 99/99, +3 hermetic legs)
**Faces:** `results/e44_midmonth/EARLYDELAY-20261020.json` (start 2020-01-01),
`results/e44_midmonth/EARLYDELAY-20261020-s20130101.json` (start 2013-01-01). x1, cutoff 2026-10-20, 1,265 names, one universe, one rank cache.

## Question

E65 priced being LATE (+1/+3/+5/+10 sessions past month-end): the newest era loses 43bp at one session late and 74bp by three. This leg prices the same magnitudes on the other side (`me_m1/me_m3/me_m5/me_m10`), so the off-cycle penalty can be read as left/right asymmetry instead of a one-sided lateness law.

## Answer

Early is penalised too, on both windows, at every magnitude — the boundary is a **point**, not a slope that only exists to the right of month-end.

| sessions off month-end | newest era, early | newest era, late (E65) | early − late |
|---|---|---|---|
| 1 | **−19bp** | −43bp | +24bp |
| 3 | −49bp | −74bp | +25bp |
| 5 | −64bp | −74bp | +10bp |
| 10 | −76bp | −91bp | +15bp |

- The newest-era early ladder is **bit-identical at both window starts** (−19/−49/−64/−76) and monotone, while its full-window counterpart is not (start 2020: +8/−65/−88/−68; start 2013: −11/−20/−31/−61). Same signature as E59: the newest era is a start-invariant path, the older eras are not.
- Lateness is roughly **2× the cost of earliness** at one session (43 vs 19bp) and the gap widens to 24–25bp at the 1- and 3-session marks. The five off-cycle dates of E59 (−56..−88bp) sit at or beyond the 10-session late mark: an off-cycle date is a *much* bigger miss than being one session off.
- Turnover is flat 0.566–0.592 turns/yr and the x1 fee is the same ~7.7bp/yr band across every arm, so the cost channel is excluded on the left side exactly as it was on the right (E63).

## Reading

The month boundary behaves like a **publication deadline with a graded shoulder**: arriving early costs something (you buy a book that is already on the shelf), arriving late costs about twice as much, and trading on any other date costs two to four times as much again. "Month-end is best" is therefore not a lateness optimum — it is the one date where neither side of the boundary is paid.

## Honest limits

- The early lag moves the **decision session**, not just the entry: the book is re-ranked on the earlier date on names already eligible then. An entry-only lag would need an execution-lag hook the engine does not have (same limit as E65).
- The late column is **read from the E65 face** at the same cutoff+start, not re-burned in this leg; the two faces share spec, universe and rank cache but are separate burns.
- Era gaps carry their start date: `2021_2023` reads −94/−130/−81bp at a 2020 start and +3/−23/−1bp at a 2013 start, because eligibility is built from the bars visible to the engine at the window start (the r1110 panel-arrival pit). The newest era is the only start-invariant column.
- Descriptive census: no gate, no verdict, no prereg, no trial count.

## Handoff

Next cheap unit seeded: **E67-MONTHEND-NEIGHBORHOOD** (`me_m2`/`me_p2`) — is the one-session penalty a spike on a single session (a true deadline) or the first step of a ramp? Everything else in the ladder already exists, so this is two more arms on the same runner.