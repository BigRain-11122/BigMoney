# DIGEST-20261030-r1281-e254-band-exponent-inside-cell

**Study** E254 — does the shuffled band really shrink as 1/sqrt(n) inside one era?
**Runner** `scripts/e254_band_exponent_inside_cell.py` (run / selftest 15/15 / verify) · **Face** `results/state_tilt/BANDEXP-2026-10-29.json`
**Verdict** `exponent_undetermined_inside_the_cell` (reason: r2 below floor in at least one family)

## What was asked

E253 turned E252's bands into session counts and had to assume edge(n') = edge(n)*(n/n')**gamma with gamma = 1/2 frozen. It checked that assumption across four heterogeneous eras and got 0.244 (r2 0.28) instead of 0.5, moving the star's self-row target from 516 to 660 sessions — but a cross-era fit is as likely era heterogeneity as a wrong exponent.

## What was done

Inside era_2025_now only, the shuffled band is rebuilt at n = 100/150/200/250/300/350/408, in two families (HEAD = first n sessions; TAIL = last n, fixed endpoint), each point the median over 7 seeds of the min over 60 permutations. No coefficient is re-priced; the star is pinned to the whole-era name so every rung measures one sleeve.

## What it says

- The band DOES shrink within the cell: HEAD 0.3186 (r2 0.67), TAIL 0.6854 (r2 0.85); leave-one-seed-out ranges [0.276, 0.352] and [0.604, 0.735].
- HEAD's r2 is under the frozen 0.80 floor → the exponent is published as UNDETERMINED, not as 0.5 and not as 0.244.
- E253's target becomes a range: 434 / 420 sessions (measured exponents), 442 / 424 (reference exponents 0.244 / 0.5). "Short by 108, ETA 2027-04-23" reads "short by 12..26, no calendar".
- Draw-count sensitivity (60 → 200 draws, 3 rungs): HEAD 0.200, TAIL 0.758. Endpoint noise binds, not the exponent → E255 asks whether draws or rungs are the constraint.

## Defects found and fixed in-window

1. The first published face failed its own `verify` ("family tail has no gamma"): the face was written before the script's last edit. `run` and `verify` must be run as a pair before a face is published.
2. `verdict_reason` was published as `null` although the rule returned a reason: the sensitivity loop rebound the local name `why` after the rule had set it. Renamed the two bindings (`skip`, `sens_skip`); the face now publishes "r2 below floor in at least one family" and the smoke leg pins `verdict_reason` to `verdict_from(...)[1]`.

## Not done

No bootstrap (the face never moves b), no re-pricing of any coefficient, no extension of the window (408 sessions is all era_2025_now has). GPU untouched (parked C-20261014-01); cloud untouched.
