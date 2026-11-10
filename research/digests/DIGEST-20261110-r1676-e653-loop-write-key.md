# DIGEST 2026-11-10 r1676 bm-b -- E653: what a loop-guarded module-level write actually does

**Card** E653 (pool head, watermark red: pool-batch-runnable-idle-low-cpu).
**Face** `results/state_tilt/LOOPWRITEKEY.json` (+ `loopwritekey_latest.json`), 845 rows.
**Script** `scripts/e653_loop_write_key.py` (selftest 22/22; build/check/verify problems=[]).
**Wiring** smoke leg E653 (+ `scripts/run_e653_smoke_leg.py`, `--doctor` red and byte-restored),
S6 leg `loop_write_key` rc=0 140.5s.

## What was asked

E649 published 1,012 residual module-level write sites "behind a guard" and put 548 of them in a
`loop` bucket with the execution line `runs_at_import_zero_or_more_times`. That label answers
neither half of the question a reader has:

1. `loop` there is the INNERMOST guard region, so `for ...: if ...: P['a']['b'] = v` is published as
   `conditional` while it still executes once per iteration. The population that runs inside a loop
   is the union over every chain that mentions one.
2. "zero or more times" is one sentence for two write shapes: a body that writes the same address N
   times (last-write-wins) and a body whose row key or container key comes from the loop target
   (accumulation -- a distinct address per pass).

## What was measured

| reading | value |
|---|---|
| residual write sites executing inside a loop | 845 |
| E649's published innermost-`loop` bucket | 548 |
| sites the guard label hides | 297 |
| address varies with the loop target (accumulation) | 696 (82.4%) |
| address repeats (last-write-wins) | 149 (17.6%) |
| loop write sites naming a counted row key | 0 (E649's single hit is outside every loop) |

Iterables: `module_constant` 364, `comprehension` 186, `call` 107, `literal_container` 94,
`bare_name` 66, `operator` 14, `enumerate_call` 7, `attribute_or_subscript` 4, while-condition 2,
`other` 1. Row-key forms: `loop_target` 443, `unpack_member` 168, `literal` 95, `computed_name` 84,
`computed_call` 32, `computed` 11, `computed_member` 6, `literal_nonstring` 4, `slice` 2,
`other` 2. Container-key forms: `literal` 799, `loop_target` 21, `unpack_member` 13,
`computed_name` 9, `computed_call` 2, `computed_member` 1.

## Method notes that matter

* The address is read as TWO components: the deepest Subscript at the site position (E638's own
  depth ruler) gives the row key, the shallowest gives the container key. A name census over one
  subscript level would have called a container key a row key.
* `slice` is its own key form. Two sites (`b[bucket][t + 1:t + 1 + span] += ...`) assign a RANGE,
  and filing them under `other` would have hidden a real shape behind an "unrecognised" label.
* A `while` binds no target, so every address inside it reads as last-write-wins; the test form is
  published beside it so the ruler's edge is visible rather than assumed away.
* `verify` compares row-derived readings only. `python_files_scanned` and `holes` are tree-vintage:
  the first build's leg went red for a file added later in the same round (E420/E421 family), so
  those two are published and never compared -- `compared_counts()` carries the split and two
  selftest legs pin both directions.

## Verdict

`the_loop_guarded_residual_is_two_write_shapes...` -- `zero or more times` is one statement and two
write shapes, and the loop bucket a reader is given is not the population that runs per iteration.

**Next** E659: how many repetitions the 149 fixed-address sites collapse into, i.e. whether each
loop bound is statically countable (`range(3)`, a literal list, a module constant) or not (a bare
name, a call, a comprehension, a generator).
