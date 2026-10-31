# E333 — one repair, five verdicts' arithmetic: the counts move, the verdicts do not

Date: 2026-11-01 · round r1353 bm-b · face `results/state_tilt/SURVIVINGCONCLUSIONS-2026-11-01.json`

## Question

E332 measured that `e326.code_lines` hides 4,284 real code lines across 30 sources and re-priced
exactly one consumer (E331). Four other studies read the same helper — E326 (template parameters),
E328 (quoted-number staleness), E329 (two-vintage binding) and E330 (unpinned choice). If their
published counts are floors of the same shape, which of their conclusions survive when the corpus is
read with the tokenizer?

## Design

Each consumer's own `build()` is run twice into scratch directories over **one** file list: once with
the shipped helper and once with a tokenizer-backed replacement. The patch is restored in a `finally`
block and the restore is asserted. Every numeric leaf of the summary block is compared by dotted path
(booleans and strings are not published numbers). Because both halves use today's corpus and today's
faces, the delta is the helper and nothing else.

Attribution: a moved number is *attributed* when re-running the same build with **one** source
recovered reproduces it, and *explained exactly* when that one source produces the whole delta. The
ablation budget (3 / 8 / 6 / 4 builds for E326 / E328 / E329 / E330) is spent on the sources where
that consumer's own reader changed most: E326 re-runs `face_record` over the population against one
file, E328 re-runs `reader_index`, E329 re-runs `collect`; the generic fallback ranks by the change in
face-handle and load-site lines.

## Reading

- **17 of 69** published numbers move; **no verdict flips** (4/4 verdicts identical).
- E326: consumers 36 → 35, and the class split flips one row (a source that names a face without a
  parameter in sight is now correctly its writer). Attributed to `scripts/e312_gate_operand_identity.py`
  (-1, -2) and `scripts/e308_leg_vs_producer_tolerance.py` (+1).
- E328: quoted numbers 1,430 → 1,933 (+503), numbers that move 536 → 709 (+173), stale faces quoted
  4 → 5, stale faces unquoted 129 → 128. All six attributed to
  `scripts/e280_e251_rng_drift_repin.py`, which explains the whole delta exactly: its swallowed
  literal holds the one stale face that had no other reader.
- E329: source-family pairs 621 → 608, pairs naming two vintages 12 → 15, pairs with two dated cuts
  8 → 12, pairs with a pointer pair 4 → 5. Two sources carry it: `e280` (the negative direction —
  prose handles leave the corpus) and `scripts/e330_unpinned_choice.py` (the positive direction — 602
  of its 635 code lines were invisible).
- E330: 0 of 21 numbers move. The largest single loss in the corpus does not move its own counts,
  because the hidden lines are its definitions and load sites, which it already sees through the
  functions it calls.

## Second axis (control, not folded into the delta)

The shipped half does **not** reproduce any of the four published faces: `faces_scanned` 550 → 555,
`sources_scanned` 2,284 → 2,287, E326 consumers 34 → 36, E329 pairs 9 → 12. That is corpus growth
since each face was written (this study's own file is one of the new sources), not the helper. The
face publishes the control per consumer so the two axes cannot be confused, and the delta is always
recomputed on one corpus.

## Rules worth keeping

1. **A shared helper is a shared floor.** One repair changed five studies' arithmetic; a per-study
   check would have re-priced one and left four quoting floors.
2. **A pointed verdict survives a floor.** Four verdicts hold on 52 of 69 unchanged numbers and on the
   direction of the 17 that moved — because they are statements about a mechanism, not about a count.
3. **The delta and the drift are two axes.** Publishing only the delta would have silently absorbed a
   corpus that grew 5 faces since publication; the reproduction control is what separates them.
4. **Ablation beats a plausible story.** The diffused reader changes (34 basenames for E328) look
   unattributable until each consumer's own reader is measured per source: then one file explains the
   whole +503 and the second explainer turns out to be the file whose 602 hidden lines are its body.