# E273 — a threshold replaces the triple exactly, but only with its rule attached

**Round** r1297 bm-b · **Cutoff** 2026-10-29 · **Face** results/state_tilt/BANDTHRESHGUARD-2026-10-29.json
**Runner** scripts/e273_guard_from_threshold.py (selftest 20/20, verify 0 problems)

## Why this card exists

E270 measured the limit of the band family: the guard consumes four numbers per row
(`b`, `band_lo`, `band_hi`, `own_p95`), only 4 of 17 published band collections carry all four, and
27 verdict-bearing collections (584 records) publish a judgement a reader cannot re-decide.

But every rule in this family is really `multiplier vs threshold`:

```
t_max_end = |b| / max(|lo|,|hi|)          (E264/E265 form — exact: outside(m) ⟺ m < t)
t_side    = |b| / |the band end on the row's own side|    (S3's published form)
```

so the band itself is redundant arithmetic **if the published threshold is really that band's
threshold**. The question E273 was seeded to answer is whether that substitution is exact or merely
plausible, and how far it reaches.

## What was measured (36 comparisons that publish BOTH spellings)

| check | result |
|---|---|
| threshold re-derives from the band | max abs diff `t_max_end` 0.0, `t_side` 0.0 |
| literal band test vs `m < t_max_end` | 36/36 agree |
| literal side test vs `m < t_side` | 36/36 agree |
| published `own_verdict` vs max-end form | 36/36 agree |
| S1 single / S2 guarded / S3 bracket re-run from threshold columns only | 36/36, 36/36, 36/36 |
| triple columns consulted to re-run any of the three | **0** |
| rows carrying two DIFFERENT published thresholds | 18 of 36 |
| rows whose own verdict differs between the two forms | **6 of 36 (16.7%)** |
| rows whose guarded screen differs between the two forms | 1 of 36 |

Reach: 10 collections are threshold-runnable, of which **9 collections / 120 records are newly
runnable** beyond E270's 4 guard-complete collections (BANDMARGIN `/comparison_margins`,
BANDPOOLED `/comparisons` + 4 `mislabelled` sub-collections, BANDSCREEN's
`/counterexamples_of_the_written_screen`, `/summary/rows_moved`, `/thresholds_that_differ`).

## Verdict

`threshold_substitutes_for_the_triple_only_alongside_its_rule` — the substitution is exact (0.0
residual, 36/36 on all three rules, zero band columns consulted), but half the rows publish two
different thresholds and 6 of those read a *different verdict* on them. A threshold-only face is
therefore re-runnable only if it also names which form its verdict used; a bare "the threshold"
is ambiguous on 6 of 36 comparisons.

## What a reader can do with this

- A face publishing `t_max_end` + `own_p95` (+ `donor_p95` for pair screens) is **fully
  re-runnable** without `b`/`band_lo`/`band_hi`. The missing triple is a documentation gap, not a
  barrier.
- A face publishing only `t_side` is re-runnable **for the rules that were fitted on `t_side`**
  (S3 bracket); reading it as the transfer threshold mis-decides 6 of 36 rows.
- The 27 verdict-bearing collections E270 flagged are not all un-re-runnable: 9 of them already
  carry a usable threshold, they just never said so.

## Pit (in-window)

The census detector counted the fixture's own `comparison_rows` collection as newly runnable
because the selftest fixture published thresholds — the correct reading was "two collections in the
fixture, not one", not a defect in `census()`. The fix went into the selftest expectation (L17/L18)
and the code was left alone; a leg that *widens* the code to match a hand-typed expectation is how
a detector stops detecting.

Sibling (the family's standing trap, avoided by construction here): `verify` re-derives every
published number from the sources rather than from its own summary, and L20 pins that doctoring the
`rederivation` block is caught — a face whose verdict lives only in its own summary is not a gate
(r1266).