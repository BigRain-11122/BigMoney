<!-- BEGIN:IDX-FUT-CARRY-HEDGE-CARRY-CLOCK -->

# when does the rounding hand its money back

generated 2026-11-24T19:58:57+08:00 | evidence_cutoff **2026-11-23** | verdict **THE_ROUNDING_BET_HAS_TURNED_ON_IC_vs_IM_AND_IH_vs_IC_AND_IH_vs_IM_AND_IM_vs_IC**

r2007 showed that rounding beta 1.5567 up to 2 lots of IF earned 47,396 CNY
last year, and said in the same breath that the money is a bet on the hedge
leg's own carry. This page prices that sentence. A short futures position is
exactly two things -- `-index return` (direction) and `-(futures return -
index return)` (carry) -- so the windfall can be cut in two, and only the
carry half has an expiry.

## the two legs of last year's windfall

Same window r2007 used, per one lot of extra short. Rolls are removed from
the carry leg by the parent's roll mask; whatever that removal leaves behind
is printed as residual rather than folded into either leg.

| leg | window | days | short total | direction (-index) | carry (-basis) | residual | carry share |
|---|---|---|---|---|---|---|---|
| IF | 2025-11-21..2026-11-20 | 242 | 14.27% | 12.83% | -4.03% | 5.4718% | -28.3% |
| IH | 2025-11-21..2026-11-20 | 242 | 8.63% | 6.56% | -0.60% | 2.6626% | -7.0% |
| IC | 2025-11-21..2026-11-20 | 242 | 12.83% | 12.43% | -9.55% | 9.9445% | -74.4% |
| IM | 2025-11-21..2026-11-20 | 242 | 22.70% | 22.20% | -11.36% | 11.8540% | -50.1% |

`residual` is the roll-day basis jump the mask removes: it is money a short
really made or lost, but it is a contract change, not carry. `carry share`
is the carry leg as a share of the short's total return -- **a negative
share means last year's windfall was not carry at all: the direction leg
paid, the carry leg charged.**

## the carry leg today

Positive = a short is being paid to wait. The 20-day column is annualised;
the bucket columns are compounded over their own length.

| leg | last close | 20d now | 20d median | 20d p10..p90 | share positive | 1m | 3m | 6m | 12m | rolls masked |
|---|---|---|---|---|---|---|---|---|---|---|
| IF | 3,915.40 | 11.811% | -1.103% | -10.294..5.605 | 40.8% | 0.485% | -0.950% | -2.888% | -3.997% | 27 |
| IH | 2,733.80 | 11.773% | -0.893% | -9.840..5.015 | 42.2% | 0.635% | 0.139% | -0.799% | -0.629% | 35 |
| IC | 6,058.00 | -0.929% | -1.666% | -14.172..6.545 | 37.6% | -0.012% | -3.034% | -5.111% | -10.445% | 22 |
| IM | 5,756.00 | -3.444% | -4.537% | -19.215..5.587 | 30.3% | -0.263% | -3.362% | -6.186% | -12.068% | 18 |

## the sign, and how long it has run

| leg | current side | readings on this side | last flip | flipped away from |
|---|---|---|---|---|
| IF | pays_a_short | 1 | 2026-11-19 | negative |
| IH | pays_a_short | 1 | 2026-11-19 | negative |
| IC | costs_a_short | 1 | 2026-11-20 | positive |
| IM | costs_a_short | 1 | 2026-11-20 | positive |

## what the windfall is worth from here

| pair | extra lots | notional CNY | carry now | CNY / year from here | windfall: direction | windfall: carry | windfall: residual | carry share | reading | payback date |
|---|---|---|---|---|---|---|---|---|---|---|
| IC_vs_IF | 0.4433 | 520,689 | 11.811% | 61,499 | 66,808 | -21,000 | 1,588 | -44.3% | STILL_BEING_PAID | - |
| IC_vs_IH | 0.7480 | 613,459 | 11.773% | 72,223 | 40,269 | -3,680 | -2,526 | -10.8% | STILL_BEING_PAID | - |
| IC_vs_IM | 0.9944 | 1,144,730 | -3.444% | -39,425 | 254,175 | -130,046 | 31,472 | -83.6% | BEING_HANDED_BACK | 2030-11-03 |
| IH_vs_IC | 0.7992 | 968,296 | -0.929% | -8,995 | 120,343 | -92,425 | 28,473 | -163.9% | BEING_HANDED_BACK | 2033-02-28 |
| IH_vs_IF | 0.5247 | 616,301 | 11.811% | 72,791 | 79,076 | -24,856 | 1,879 | -44.3% | STILL_BEING_PAID | - |
| IH_vs_IM | 0.8172 | 940,778 | -3.444% | -32,400 | 208,889 | -106,876 | 25,865 | -83.6% | BEING_HANDED_BACK | 2030-11-03 |
| IM_vs_IC | 0.0685 | 83,033 | -0.929% | -771 | 10,320 | -7,926 | 2,442 | -163.9% | BEING_HANDED_BACK | 2033-02-28 |
| IM_vs_IF | 0.6061 | 711,970 | 11.811% | 84,091 | 91,351 | -28,714 | 2,171 | -44.3% | STILL_BEING_PAID | - |
| IM_vs_IH | 0.1013 | 83,092 | 11.773% | 9,782 | 5,454 | -498 | -342 | -10.8% | STILL_BEING_PAID | - |

`CNY / year from here` is the extra short's running rate: positive means it
is still being paid, negative means it now charges and the windfall is handed
back at that rate until the date in the last column. `windfall: carry` and
`carry share` are last year's numbers: a negative share says the windfall was
made by the direction leg and the carry leg charged for it. The residual is
the roll-day jump the mask removes, so the three columns add up to the
windfall rather than hiding a difference in carry.

## what this does not settle

* the carry is spot-month basis on this repo's roll walk; a different
  contract month would price a different carry, and this page does not model
  the roll schedule;
* the windfall is r2007's single last-year window, not a distribution: a
  different 242 days would print a different CNY;
* the extra short is naked, so its direction leg is a real position and not a
  hedge -- the page separates the two halves but does not judge whether the
  desk wanted either;
* margin, roll cost and financing on the extra lot are not in these numbers.

<!-- END:IDX-FUT-CARRY-HEDGE-CARRY-CLOCK -->
