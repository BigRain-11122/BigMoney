# Index-futures roll days: how many the mask finds, and what the misses cost

Face `results/idx_fut_roll_gap.json` · evidence cutoff **2026-11-17** · verdict **ROLL_MASK_INCOMPLETE**

## Why the mask is not optional

The panel is a main-contract continuous series. On the day it switches contracts
the series jumps by the price difference between them — but a holder who rolls
does not book that jump: they sell the old contract and buy the new one with the
same money. The jump is a level reset (like a split), not a return. So the
roller's return is the series with the splice days masked, and what those
surviving days add up to is the carry. The unmasked price series is printed below
only to show what happens when a splice is left in: on IF it reads
+0.15%/yr against a carry of +5.84%/yr.

## What the published detector actually finds

| pair | published mask days | calendar roll days | missed | missed share | carry under published mask | carry under calendar mask | gap | state |
|---|---|---|---|---|---|---|---|---|
| IF | 26 | 118 | 92 | 78% | +1.88%/yr | +5.84%/yr | +3.97 | MASK_INCOMPLETE |
| IC | 22 | 118 | 96 | 81% | +2.88%/yr | +9.80%/yr | +6.93 | MASK_INCOMPLETE |
| IH | 34 | 118 | 84 | 71% | +1.56%/yr | +5.39%/yr | +3.83 | MASK_INCOMPLETE |
| IM | 18 | 51 | 33 | 65% | +5.88%/yr | +12.01%/yr | +6.13 | MASK_INCOMPLETE |

The index futures expire once a month. The published rule (`8x the median basis
step and above 0.5%`) fires a few times a year, so most splices stay in the
series as losses nobody masked — and the carry reading is short by roughly the
size of the misses.

## The roll step itself

| pair | rolls | per year | step median | step mean | sum %%/yr | positive steps | months covered |
|---|---|---|---|---|---|---|---|
| IF | 118 | 12.1 | -0.387% | -0.448% | -5.41 | 1/118 | 99.2% |
| IC | 118 | 12.1 | -0.619% | -0.757% | -9.14 | 1/118 | 99.2% |
| IH | 118 | 12.1 | -0.273% | -0.415% | -5.01 | 1/118 | 99.2% |
| IM | 51 | 11.9 | -0.511% | -0.932% | -11.09 | 0/51 | 96.2% |

A negative step is the discount the next contract hands you; the month after pays
it back as it converges. That is why the step is not a cost to add on top — it is
the other half of the convergence.

## What the misses did to the r1690 three-arm verdict

Same arms, same leash, same costs, same roll-cost charge; the only difference
is which splice days are left in the return series.

| pair | A published | A calendar | B published | B calendar | B-A published | B-A calendar |
|---|---|---|---|---|---|---|
| IF | +3.95 | +5.45 | +5.14 | +5.25 | +1.20 | -0.20 |
| IC | +3.66 | +5.94 | +3.72 | +4.01 | +0.05 | -1.93 |
| IH | +4.07 | +5.56 | +5.17 | +5.71 | +1.10 | +0.14 |
| IM | +3.74 | +5.40 | +1.97 | +2.73 | -1.77 | -2.67 |

The published run reproduces r1690's B column to the last decimal and its A
column to within the extra roll charge (one calendar roll a month instead of
the two or three a year the detector caught). Under the complete mask the
waiting arm's margin moves by **-1.18pp** median (A-over-B +1.18pp, range +0.91 .. +1.98).

W1 asks for +0.50pp. The margin the published reading gave the waiting arm on
IF and IH is smaller than this movement and has the same sign as it, so the
HOLD-ALWAYS verdict survives -- but it now survives for a mechanical reason:
the always-in arm was under-credited by 4-7pp a year of carry the mask left in
the series as losses.

## Caveats

- main-contract continuous panel only: which contract the series switched to is not recorded, so the splice is measured as a basis step, not as a contract pair
- the calendar detector assumes the mainland index-futures expiry (third Friday); a month with no panel day inside the window is reported as missing, not guessed
- the open-interest column is unusable before 2019 (all zero) and flat from 2025 (no contract switch), so it is not used as a detector
- masking a roll day sets that day's spread to zero, which charges the roller the index return with no convergence -- the direction is conservative (it understates carry by well under 1bp per roll)
- the arm re-runs are a sensitivity, not a re-declared verdict: W1/W2/W3 and the halves check were frozen against the published reading, so a re-declaration needs its own prereg
