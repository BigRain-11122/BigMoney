# DIGEST 2026-11-09 r1637 bm-b — E615: does a live sweep open what it globs?

**Question seeded by E613 (r1636).** E613 priced *reachability*: 76 ancestor-only faces rest on
five round scripts nothing names, and the one landing module a live chain runs
(`scripts/e396_face_basename_suffix.py`) reaches 54 of them only through a pattern that names
nothing. Whether the sweep that reaches a face does anything with the hit was not asked.

**Method.** Each glob call in every landing module is resolved to the loop that consumes it —
including the two-hop shape `targets = sorted(glob(...))` followed by `for t in targets` — and the
loop body is classified one hop in: an opener applied to the yield, a module helper that opens its
parameter, a call whose literals name a git reader, a name-shaped question (basename/relpath/
endswith/getsize/attribute), no reference at all, or no loop this scan can follow. Pattern literal-
ness is a separate field: a computed pattern (`f + '/**/*'`) is priced in its own row but pairs
with no face, because the landing was E609's measurement.

**Readings** (`results/state_tilt/GLOBSWEEPUSE.json`, cutoff 2026-11-06):

| | |
|---|---|
| landing modules | 9 |
| glob calls | 13 (7 with a static pattern) |
| opens the yield | 9 (5 direct, 1 through a helper, 3 handed to `git hash-object`) |
| reads only the name | 3 (`results/_r843bmc_inputs.py` ×2, `scripts/e396_face_basename_suffix.py`) |
| faces opened by some sweep | 76 / 76 |
| faces opened by a sweep an entry point runs again | **0** |
| faces opened only by a one-off | 76 |

**The load-bearing number is a zero.** The only sweeper that runs every round reads names:
`os.path.relpath(p, root)`, `p.endswith("_smoke.json")`, then the name is bucketed and the face is
dropped. So "these 76 faces are swept by a live chain" (E613) and "not one of them is ever opened"
(this study) are both true, and only the pair is a price.

**Self-caught (four).**
1. A composed pattern is not a missing pattern: accepting only `ast.Constant` graded the most common
   spelling `os.path.join("results","**","*.json")` as computed — E470's one-hop lesson, second
   occurrence. Fixed by static evaluation of Constant / `+` / all-static `join` / one-hop name.
2. The loop's own `iter` mentions the binding: `for t in targets` after `targets = glob(...)` made
   that mention a use of the yield and graded every sweep unclassifiable (7 × `no_loop`). The body
   is now the loop's statements, classified under the loop's own target name.
3. Method-style name calls hide behind an Attribute: `p.endswith(...)` is `Call(Attribute(Name p))`,
   so climbing from the `Name` hit the Attribute branch and dropped the name class to 0.
4. Literalness and treatment are two facts. Folding "the pattern is computed" into the class would
   have hidden that a computed sweep does open; the class now answers only what the body does.

**Limits.** One hop only (a yield renamed into `rel` and opened later reads as a name use); a
computed pattern pairs with no face, so a live *and* opening sweep behind one would be under-credited;
literal openers elsewhere in the corpus are E606's measurement and are not re-derived here.

**Evidence.** `scripts/e615_glob_sweep_use.py` (selftest 26/26, run/check/verify `problems=[]`) →
`results/state_tilt/GLOBSWEEPUSE.json` (+ `-latest.json`) → `scripts/run_e615_smoke_leg.py`
(PASS, `--doctor` 1/1 red, face byte-restored) → `smoke_test.py` leg E615 → S6 leg
`glob_sweep_use` → `results/runnable_pool.json` E615 done + E617 seeded.
