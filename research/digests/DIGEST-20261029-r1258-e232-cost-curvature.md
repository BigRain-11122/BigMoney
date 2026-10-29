# DIGEST 2026-10-29 r1258 (bm-b) -- E232: is the family's toll conclusion a fact about the rule or about the cost model?

Card: E232-COST-CURVATURE. Face: `results/state_tilt/COSTCURVE-2026-10-29.json`.
Runner: `scripts/e232_cost_curvature.py` (run / selftest, 10 hermetic legs).

## What was asked

E226..E231 charge every weight move at a fixed 13.041 bp per unit of |dw|. The whole family
conclusion -- *the toll is the only channel that ever separates these rules from a flat
constant* -- therefore rests on a **linear** charge. E231 removed the last chance of calling
E230's band a path accident; what had never been tested is the charge function itself.

## What was run

`cost = cost_side_bp * |dw| ** gamma` over gamma in 0.75 / 1.00 / 1.25 / 1.50, normalised so
that a full 1.0 weight change costs the same at every point (`1**gamma == 1`). At gamma=1.0
the function reproduces `e228.rows_for` bit-for-bit (selftest leg). Three arms
(binary_low / tilt_step / tilt_linear) x two panels (sh510300, equal-weight basket) x the
three E229 channels, plus E230's deadband re-read at each gamma on the two smallest bands for
all three arms. Bar = |t| >= 3.08 (two-sided 5% over 3 arms x 2 panels x 4 gammas).

## The answer, in three parts

**1. The conclusion survives. The magnitude does not.**
The toll clears its bar on 6 of 6 arm cells at *every* gamma, and remains the *only* channel
past the bar at every gamma in those same 6 cells (selection |t| <= 1.32 throughout). So "the
toll is what separates these rules from a constant" is curvature-invariant. What is not: the
toll's size falls monotonically as the charge turns convex -- tilt_linear -247.3 -> -93.2 bp/yr
on the single (2.6x) and -194.9 -> -75.7 on the basket (2.6x), taking the pair with it
(-788.1 -> -634.0 and -230.6 -> -111.4 bp/yr).

**2. A 0/1 gate is exactly invariant, and that is structural, not luck.**
binary_low's toll is -201.6 bp/yr (single) / -121.6 (basket) at all four gammas to 1e-9,
because its only non-zero |dw| is 1.0 and 1.0**gamma == 1.0 for every gamma. Its basket pair is
+227.0 bp/yr flat -- the only positive pair cell in the family -- and it is positive because
the charge can no longer reach it, not because the rule is good. This is also the honest
answer to the ticket's own premise.

**3. E230's one passing cell was a cost-model artefact.**
The focus cell (primary_single / tilt_linear / band 0.10 sd_is) reads BAND_PAYS at gamma 0.75
and 1.00, then BAND_NOISE at 1.25 and 1.50: its paired improvement falls 281.5 -> 186.9 bp/yr
as the charge turns convex while its standard error does not. BAND_PAYS counts across the whole
ladder: 2 / 1 / 0 / 0 by gamma. Ladder verdicts are stable at every gamma on 9 of 12 cells; the
three that move are exactly the small-band cells whose margin was thin.

## The ticket's premise is backwards (measured, not repeated)

The card that opened this study said a concave charge makes a rule that moves in small steps
"pay relatively less". With |dw| < 1 the opposite holds: 0.5**0.75 = 0.594 > 0.5, so a concave
charge makes a small move *dearer* per unit and splitting one move into n steps costs sqrt(n)
times as much, not less. Selftest legs pin both directions (concave dearer, convex cheaper),
so the face measures the sign of the effect instead of inheriting it.

## Rules worth reusing

1. **A cost model is a design choice, so every conclusion drawn through it owes a curvature
   sweep.** The cheapest possible check: parameterise the charge, keep the unit cost of one
   full move fixed, and require that the *sign* of a claimed channel survive every point in
   the sweep. Significance survived here; a single band's fix did not.
2. **Discrete rules are degenerate cases of graded rules and must be flagged as such.** A 0/1
   gate cannot feel curvature at all (`1**gamma == 1`), so any comparison between a gate and a
   tilt arm is partly a comparison between two different exposure to the impact model. Publish
   that as an invariant, and never read the gate's flatness as robustness.
3. **Selection and sizing are cost-free by construction, so they are the control.** Because
   neither touches the charge, `pair(g) - pair(g') == toll(g) - toll(g')` exactly. Pinning that
   in a selftest means any cross-gamma movement in the pair is attributed to the charge and
   cannot be re-narrated as skill later.