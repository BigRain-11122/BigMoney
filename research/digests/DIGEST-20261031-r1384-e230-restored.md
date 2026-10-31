# r1384 bm-c — the module six runners imported had never been committed; the face it published is what proved the restoration

**Date** 2026-10-31 · **Round** 1384 · **Machine** bm-c · **Dept** 研究/工程

## What was wrong

`scripts/e230_hysteresis_toll.py` was written by bm-b in r1256 and never entered a commit
(`git log --all -- scripts/e230_hysteresis_toll.py` is empty). Six runners import it —
`e231`, `e232`, `e233`, `e234`, `e235`, `e236`, `e237` — so on a clean checkout not one of
them could start. r1360 recorded this as the top supply blocker and the pool floor has
been reading `ready 0 / floor 3` ever since.

Underneath it sat a second, older loss: `e228_matched_exposure.rows_for` no longer exists,
and `e229.channel_rows` still calls it. So even with `e230` present the accounting chain
was dead — proven live by `python scripts/e232_cost_curvature.py selftest`, which crashed
on `e228.rows_for` in its gamma=1 crosscheck.

## What was restored, and how it was proved

The faces the missing module produced WERE committed (`HYSTERESIS-2026-10-29.json`,
`hysteresis_by_rung_2026-10-29.csv`, `bandpath/costcurve/granularity/..._latest.json`), so
the reconstruction is not article-writing: the published face is an executable acceptance
test.

* `scripts/e230_hysteresis_toll.py` — the rule (`hold the committed weight until
  |v - v_at_last_commit| >= band`), the band scale (in-sample sd), the per-session channel
  decomposition against ONE frozen constant per (panel, arm), the paired delta, the frozen
  verdict vocabulary, the ladder runner and its face/CSV, plus 16 selftest legs.
* `scripts/e228_matched_exposure.py` — `rows_for` restored (the panel the whole E229..E237
  family decomposes) with three legs, one of which pins it to `excess_series`, the function
  the published E228 face uses, so the two cannot drift apart.
* `e230.rows_for` delegates to `e228.rows_for`; the accounting exists once.

**Acceptance evidence.** `python scripts/e230_hysteresis_toll.py reproduce` re-runs the
ladder with both panels truncated to the face's own session counts and diffs it field by
field: **0 numeric differences** across 2 panels × 3 arms × 6 rungs × 2 cost levels plus the
30-row summary — every published number, to the last bit, including the verdict counts
(1 BAND_PAYS / 5 BAND_COSTS / 24 BAND_NOISE).

Two prose diffs remain and are **not** reproduced, deliberately: the r1256 BAND_PAYS reason
string prints `toll +226.8` where the delta it publishes beside it is `+113.4` (twice the
x2 toll delta). The restored module prints the number it measured. Reproducing an arithmetic
slip in a sentence would make the sentence wrong on purpose, so `reproduce()` separates
`numeric_identical` from `prose_diffs` and the selftest asserts only the numbers.

## Live reading (2026-10-30 bar, refreshed by this round)

`results/state_tilt/HYSTERESIS-2026-10-30.json` + `hysteresis_latest.json` +
`hysteresis_by_rung_2026-10-30.csv`: 30 cells, **1 BAND_PAYS / 7 BAND_COSTS / 22
BAND_NOISE**, 6 rungs collapsed at or below 5 weight changes. One extra bar moved two cells
from *point estimate only* into *costs* — the composition is not yet a fixed property, which
is exactly what W231 (band path) exists to test.

## The whole family is green again

| script | selftest |
| --- | --- |
| `e228_matched_exposure.py` | 22/22 (was 19, +3) |
| `e230_hysteresis_toll.py` | 16/16 (restored) |
| `e231_band_path_test.py` | 18/18 |
| `e232_cost_curvature.py` | 10/10 (crashed before) |
| `e233_empirical_gamma.py` | 13/13 |
| `e234_per_member_gamma.py` | 14/14 |
| `e235_charge_granularity.py` | 18/18 |
| `e236_share_difference.py` | 18/18 |
| `e237_information_structure.py` | 18/18 |

## What this round did NOT fix

The pool is now empty rather than unstartable (`ready_total 0`, `ready_launchable 0`,
`ready_dep_broken 0` — the dep class is gone). **Empty supply is not supply**: the floor
still needs a new frozen prereg + runner, and refreshing an existing face is a determinism
proof, not new science (r1360's own rule). That is the next round's whole subject.

## Next

* W231-band-path is now runnable on a clean checkout — whether the one passing rung is a
  property of the rule or of the split it was measured at can finally be measured here.
* Write W23 (new frozen prereg + runner) so the pool floor has something to point at.
* `e229.channel_rows` still calls a function that exists again but whose callers were all
  rewritten around it; either re-point it at `e228.rows_for` (it already does) or retire it
  with a tombstone — one of the two, in a round that touches nothing else.