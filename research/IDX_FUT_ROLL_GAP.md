# Index-futures roll days: how many the mask finds, and what the misses cost

Face `results/idx_fut_roll_gap.json` · evidence cutoff **2026-11-13** · verdict **ROLL_MASK_INCOMPLETE**

## Why the mask is not optional

The panel is a main-contract continuous series. On the day it switches contracts
the series jumps by the price difference between them — but a holder who rolls
does not book that jump: they sell the old contract and buy the new one with the
same money. The jump is a level reset (like a split), not a return. So the
roller's return is the series with the splice days masked, and what those
surviving days add up to is the carry. The unmasked price series is printed below
only to show what happens when a splice is left in: on IF it reads
+0.14%/yr against a carry of +5.79%/yr.

## What the published detector actually finds

| pair | published mask days | calendar roll days | missed | missed share | carry under published mask | carry under calendar mask | gap | state |
|---|---|---|---|---|---|---|---|---|
| IF | 26 | 117 | 91 | 78% | +1.88%/yr | +5.79%/yr | +3.92 | MASK_INCOMPLETE |
| IC | 22 | 117 | 95 | 81% | +2.88%/yr | +9.79%/yr | +6.91 | MASK_INCOMPLETE |
| IH | 34 | 117 | 83 | 71% | +1.55%/yr | +5.32%/yr | +3.77 | MASK_INCOMPLETE |
| IM | 18 | 50 | 32 | 64% | +5.86%/yr | +11.95%/yr | +6.09 | MASK_INCOMPLETE |

The index futures expire once a month. The published rule (`8x the median basis
step and above 0.5%`) fires a few times a year, so most splices stay in the
series as losses nobody masked — and the carry reading is short by roughly the
size of the misses.

## The roll step itself

| pair | rolls | per year | step median | step mean | sum %%/yr | positive steps | months covered |
|---|---|---|---|---|---|---|---|
| IF | 117 | 12.0 | -0.385% | -0.448% | -5.36 | 1/117 | 98.3% |
| IC | 117 | 12.0 | -0.620% | -0.762% | -9.13 | 1/117 | 98.3% |
| IH | 117 | 12.0 | -0.271% | -0.414% | -4.96 | 1/117 | 98.3% |
| IM | 50 | 11.7 | -0.544% | -0.947% | -11.07 | 0/50 | 94.3% |

A negative step is the discount the next contract hands you; the month after pays
it back as it converges. That is why the step is not a cost to add on top — it is
the other half of the convergence.

## What the misses did to the r1690 three-arm verdict

Same arms, same leash, same costs, same roll-cost charge; the only difference
is which splice days are left in the return series.

| pair | A published | A calendar | B published | B calendar | B-A published | B-A calendar |
|---|---|---|---|---|---|---|
| IF | +4.00 | +5.48 | +5.15 | +5.25 | +1.15 | -0.23 |
| IC | +3.77 | +6.05 | +3.72 | +4.02 | -0.05 | -2.03 |
| IH | +4.08 | +5.55 | +5.16 | +5.70 | +1.08 | +0.15 |
| IM | +4.07 | +5.73 | +1.97 | +2.73 | -2.10 | -3.00 |

The published run reproduces r1690's B column to the last decimal and its A
column to within the extra roll charge (one calendar roll a month instead of
the two or three a year the detector caught). Under the complete mask the
waiting arm's margin moves by **-1.16pp** median (A-over-B +1.16pp, range +0.90 .. +1.98).

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
