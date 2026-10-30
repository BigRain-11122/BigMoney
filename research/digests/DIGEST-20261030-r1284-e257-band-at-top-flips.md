# DIGEST 2026-10-30 r1284 bm-b — E257: re-judging every published band verdict at the top draw count

**Question.** E254/E255/E256 established that the shuffled band's 5% endpoint is still rising at
1920 permutation draws and that the increment per doubling does not decay. Every published
"outside the band" verdict in the star family was nevertheless judged against an edge measured at
a few hundred draws. What changes when the band is taken at the top draw count?

**Design.** Arithmetic on published faces only: no panel read, no refit, no bootstrap, no
coefficient re-priced.

- Multiplier `m = edge(1920 draws) / edge(row's own published draw count)`, read off E256's
  per-rung `edge_self` ladder with log-log interpolation in the draw count.
- The multiplier is **a range, not a number**: E256 measured its ladder inside `era_2025_now` in
  two families (head = first n sessions, tail = last n). A published cell is a fixed window and
  is neither, so no family is nominated as its analogue. Every row is re-judged at **all 2 x 7**
  multipliers; "flips" requires flipping at every one, "survives" surviving every one, otherwise
  the verdict is `flips_depends_on_measurement`.
- The published flag must reproduce from the row's own numbers first. A row that fails is
  published as `published_flag_not_reproduced` and counted separately, never silently re-judged.
- Both edges are scaled by `m`, so the published band asymmetry survives; the comparison stays the
  published rule (`val < lo or val > hi`).

**Reading (cutoff 2026-10-29).**

| | |
|---|---|
| rows re-judged | 16 (E252 handful of windows × self/cross, plus E251's star lag-1 residual) |
| outside at published draws | 10 |
| survive the widened band at every measurement | 8 |
| flip at every measurement | 0 |
| flip for some rung/family combination | 2 rows = **1 distinct coefficient** |
| unjudgeable (no band: the two windows with no named star) | 4 |
| multiplier range (median) | 1.098 .. 1.664 (1.232) |

The single coefficient that moves is `b = -0.4942` in the `early_three` window, published twice
(E252's cross row and E251's star lag-1 residual — the same number, not two findings). It sits
outside its published edge (0.308 / 0.299) and inside the band at the widest multipliers
(0.406 / 0.394), so its "outside" reading is real at the measured grid, not at the top of the
band's own rise.

The tightest surviving verdict sits at margin **1.49**, i.e. 49% beyond the widened edge — so the
star family's headline exclusions are not artefacts of a small draw budget.

**Downstream verdicts re-judged at the top draws.**

- **E254 (`exponent_undetermined_inside_the_cell`) survives, but for a different reason.** At 1920
  draws both families clear the frozen r2 ≥ 0.80 floor (HEAD 0.890, TAIL 0.933) — the original
  reason ("r2 below floor") no longer applies. What keeps it undetermined is the straddle:
  gamma HEAD 0.301 vs TAIL 0.565, gap 0.264 = 2.6x the frozen tolerance 0.1.
- **E255 (`draw_starvation_confirmed`) holds**: the smallest draw count in the grid where both
  families clear the floor is 480, exactly the count E255 published.
- **E256 is unchanged by construction** — its verdict is about the draw axis itself, which is this
  face's input.

**Pit (mine, and caught by the gates I was writing).** The first smoke leg asserted that *every*
moving row flips at the median widened band. The two `depends` rows do not: they flip only at the
extreme multiplier, which is precisely what `flips_depends_on_measurement` means. The face was
right and the assertion was wrong — the same shape as r1281's "assertion vs flag" defect. The leg
now pins the published flag pair (`flips_on_any_measurement` / `flips_on_every_measurement`)
instead of a single median draw.

**Second pit.** The face's `_write` called `io.dump` instead of `json.dump`: every function-level
selftest was green while `run()` died on the first save. Run and selftest are a pair (r1281 pit 1,
second occurrence in this family).

**Product.** `scripts/e257_band_at_top_flips.py` (run / selftest 23/23 / verify OK),
`results/state_tilt/BANDTOPFLIP-2026-10-29.json` + `bandtopflip_latest.json`, S6 leg
`band_at_top_flips`, smoke leg, methodology card E257.

**Engineering side-product.** `Tools/s6_chain_bmb.py` gained `--only <leg,...>` (r1281 recorded
that the whole chain could not be spot-run inside a round, so a single leg could only be verified
by hand-copying its argv). The selector filters the existing LEGS table, so a subset runs exactly
the commands the full chain would run, and an unknown leg name is rejected with rc=2 listing the
available names.