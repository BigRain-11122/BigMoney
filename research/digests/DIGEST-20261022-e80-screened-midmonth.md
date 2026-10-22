# DIGEST 2026-10-22 — E80: does the mid-month membership claim survive the split screen?

Face: `results/e44_midmonth/MIDSCREEN-20261021.json` (evidence_cutoff 2026-10-21)
Runner: `scripts/e39_panel_census.py midscreen` (new leg; `run_midmonth(raw=...)` opt-in hook)
Selftest: 169/169 (8 new hermetic legs)
Pool: E80 (bm-b lane, cpu-only)

## What was asked

E44 (r1132) put the newest-era mid-month gap (−87bp/yr) on **membership** rather than fees:
turnover was equal (0.591 vs 0.594/yr) while the churn sleeve (names bought minus names
given up) favoured month-end by 219bp per swap. E77/E78 then showed the split screen moves
exactly that era. E80 re-derives the same churn rows from the repaired universe so the
membership claim is measured instead of assumed.

## Numbers (2024_now, x1 cost)

| book | unscreened | neutralise_int | neutralise | drop |
|---|---|---|---|---|
| mid-vs-month-end gap (bp/yr) | −87.0 | −83.0 | −77.0 | −63.0 |
| surviving share of the gap | 100% | 95.4% | 88.5% | 72.4% |
| month-end churn alpha (bp/swap) | 87.3 | 92.4 | 92.4 | 52.1 |
| mid churn alpha (bp/swap) | −123.7 | −364.7 | −364.7 | **+28.0** |
| churn alpha gap (mid − me) | −211.0 | −457.1 | −457.1 | −24.1 |
| negative-swap share me / mid (%) | 44.4 / 48.1 | 44.4 / 48.1 | 44.4 / 48.1 | 51.9 / 48.1 |

Turnover control (x1): me 0.590 / mid 0.593 unscreened; 0.588 / 0.590 neutralised — the
screen moves the return path, not the traded book, so the fee channel stays excluded.

Era sign flips: **none**, on either the gap column or the churn-gap column. The 2021_2023
gap does weaken (−77 → −58 neutralised) while its churn gap is bit-identical (318.9), i.e.
in that era the screen moves the price path and not the swaps.

Screen size: neutralise_int touches 65 names / 65 events; neutralise 129 names / 135 events.

## Reading

1. **The headline survives.** Month-end still beats mid-month in the newest era after every
   repair (−77 to −83bp/yr under the two neutralise modes, 88–95% of the original gap). The
   membership story is not carried by unadjusted prints.
2. **The churn sleeve does not merely survive — it amplifies** under neutralise
   (−211 → −457bp per swap), because the month-end book's churn alpha is stable (87 → 92)
   while mid-month's degrades (−124 → −365). Repaired, the mid-month swaps are *worse*
   than the raw prints suggested, not better.
3. **But drop mode removes it** (−24bp churn gap, +28bp mid alpha, gap −63). Dropping the
   129 flagged names changes the universe and reshuffles the mid-month book, so the churn
   sleeve is not robust to composition; the return gap is (−63bp still negative).
4. `2017_2020` prints an exact `0.0bp` gap in every mode = the burn-in/cash slice of that
   era, not calendrical robustness (r1135 crib).

## Verdict

- Membership mechanism: **supported** for the return gap (survives all repairs).
- Membership magnitude via the churn sleeve: **sensitivity-bound** (−211 to −457bp per swap
  depending on the repair), so quote it with its mode.
- Not a pre-registration; no gate, no verdict, no trial booking. Published MIDMONTH faces
  are not rewritten — this is a parallel face.

## Pit notes

- The face's book keys are `me` and `mid15` (not `mid`); reading `books[mid]` silently
  yielded `None` in the first burn and would have published an empty turnover control.
  The selftest's `mid15` fixture now pins the real key.
- `_dig` returns None on the first broken path segment, so a missing mode emits `None`
  cells instead of fabricated zeros.