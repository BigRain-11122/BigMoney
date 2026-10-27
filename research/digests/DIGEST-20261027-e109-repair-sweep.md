# E109 — the repair-factor fix reached 13 of 14 remaining screened legs, and the biggest number was the one carrying the fewest

Date: 2026-10-27 · round r1173 · dept: research+engineering
Face: `results/e44_midmonth/REPAIRSWEEP-20261026.json` (per-leg before/after, ranked by numbers carried)
Tool: `scripts/e109_repairsweep.py` (two-arm burn on one panel + selftest 3/3)

## Why this leg exists

E108 fixed `panel_screen.split_events` (the factor is now the cancelling `1/(1+r)` on
every event) but re-derived only the seven gap-arm consumers. Thirteen other census
legs join a `neutralise` / `neutralise_int` arm and were still publishing numbers
computed with the mirrored factor on upward prints. Nothing in the repo said whether
that mattered for them, and their published faces are dated (20261021 family), so a
naive re-run would have mixed the factor with five sessions of panel arrival.

## The measurement

Every leg was burned **twice on today's panel**: once with the old folded-ratio factor
monkeypatched back (`e108_repairfix.run_leg(leg, legacy=True)`) and once with the shipped
code. Panel is identical between the two arms, so the delta is the factor and nothing
else. The arms are harvested by moving — the fixed-arm face is then published under the
today's-cutoff filename, so the repo carries corrected numbers rather than only a diff.

Totals: **14 legs, 47,385 numeric leaves compared, 1,792 moved (3.8%)**. 13 legs moved;
`burncontrol` is bit-identical (44 leaves), which is the expected control — it joins no
screened arm.

## Ranking by numbers carried (the ticket's ordering rule)

| leg | numbers carried | moved | largest single move |
|---|---|---|---|
| screenwide | 4,725 | 391 | screened spread 2024_now x1 **456 → 192 bp** (−264) |
| midscreen | 4,280 | 242 | `worst_correction` **−470.3 → −100.7 bp** |
| screenreg | 4,230 | 108 | era worst-correction **456 → 192 bp** |
| screenweek | 4,072 | 177 | `residual_survival` share **75.0% → 125.0%** (sign flip) |
| loodist | 4,050 | 87 | `loo_min` **−399.1 → −15.3 bp** |
| churnse | 4,045 | 92 | `boot_p05` **−1,122.5 → −110.9 bp** |
| topnames | 4,031 | 96 | top-1 churn alpha **−9,979.4 → −1,077.6 bp** |
| robustchurn | 3,998 | 81 | top-3 concentration **−11,676.8 → −1,168.0 bp** (exactly ÷10) |
| churngap | 3,982 | 72 | mid15 2024_now `delta_sum_hit` **−6,506.8 → +3,471.6 bp** |
| singleprint | 3,876 | 93 | `removed_alpha` **−9,979.4 → +141.3 bp** |
| gapsplit | 3,129 | 99 | identical −6,506.8 → +3,471.6 on gap1/2/5 |
| screentilt | 2,513 | 37 | factor table only — **zero tilt levels moved** |
| screenspread | 410 | 217 | `share_of_spread_from_size` **−133.2% → −2,683.9%** |
| burncontrol | 44 | 0 | (control: no screened arm) |

## What the numbers say

1. **The mirrored factor is an order-of-magnitude error, not a rounding one.** The
   concentration cell is exactly ÷10.0 (−11,676.8 → −1,168.0), and the recurring
   −9,979.4 witnesses are the same reverse-split transitions read through `(1+r)` on a
   `1/(1+r)` event.
2. **Two verdicts flip, not just levels.** `screenweek` residual survival reads 75.0% →
   **125.0%** (a share above 100% means the residual changed sign against a shrinking
   base) and `topnames` third-place churn alpha goes **−619.8 → +529.4 bp**. Every
   published "the effect survives under the repaired arm" sentence written on the legacy
   arm has to be re-read on the fixed one.
3. **Three legs are structurally saturated.** gap1/gap2/gap5 publish the same corrected
   number to the bp even now (−6,506.8 → +3,471.6 each), the E103/E99 saturation seen
   again on the repair side.
4. **The most contaminated leg carries the fewest numbers.** `screenspread` moved 217 of
   410 leaves (53%), because it publishes *ratios*: `share_of_spread_from_size` for
   `neutralise_int` reads −133.2% → **−2,683.9%**, a share dividing by a near-zero
   engine-vs-arm difference. The bp pair beside it (456 → 192) is the stable reading; the
   percentage is a denominator-fragile derivative and should not be quoted alone.
5. **`screentilt` is the clean negative.** Its 37 moved leaves are all `factor_applied`
   records in the screen report; not one tilt level changed (`2024_now` stays 697.6
   unscreened / 609.2·x on the screened arms). Screening touched the print table, not the
   tilt story.

## Open item (not this factor)

`burncontrol` exits rc=1 with `status: MISMATCH, shared_cells 56, mismatched 11` in **both**
arms (0 numeric leaves moved between them). So that mismatch is not the sign fix — the
control compares a recompute against faces burned at a different start/burn. Logged as its
own ticket rather than folded into this one.

## Verify

```
python scripts/e109_repairsweep.py selftest      # 3/3
python scripts/e109_repairsweep.py sweep --publish --legs <comma list>
python -m smoke_test                             # 84/84
```