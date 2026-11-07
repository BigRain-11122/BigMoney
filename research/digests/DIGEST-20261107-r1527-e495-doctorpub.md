# r1527 bm-b — E495: did the diagnostic become the publication?

**Card:** E495 · **Round:** r1527 · **Date:** 2026-11-07 · **Face:** `results/state_tilt/doctorpub_latest.json`

## The question

E492 published 13 `*_latest.json` faces whose only visible composers are doctor harnesses
(`scripts/run_eNNN_smoke_leg.py`). The natural reading of "no producer among the visible
composers" is "a test wrote this face, and the publication is the diagnostic". This study prices
that reading instead of repeating it: what does the harness do with the name, who else writes
it, and who reads it.

## Three arms (static, no network, nothing mutated)

- **A — harness discipline.** Re-derived from each composer's own call sites: write once and
  leave the bytes, or write twice so the original goes back (located, when present, inside a
  `finally`).
- **B — author.** Every call in every scanned source whose argument folds to the basename,
  graded by whether the callee is an opener or a local helper that reaches an opener with that
  parameter. Two extra channels are measured because the first draft found nothing without them:
  a module-level `FACE_NAME = "<basename>"` constant that reaches a write, and local-name
  carriers (`path = join(OUTDIR, FACE_NAME)` → `targets = [path, ...]` → `for target in targets`
  → `open(target, 'w')`).
- **C — readers.** Each direct read site priced by `e499.price_site` (E483's debt vocabulary),
  consumer reads separated from the harness's own restore-reads.

## Readings

| axis | reading |
|---|---|
| population | 13 faces (E492's `has_a_producer_composer == false`) |
| A: harness sites | 27 of 27 restore the original, 25 inside a `finally`; **0 leave their bytes behind** |
| B: writers other than the harness | **12 of 13** — 5 module constant, 4 local-name carriers, 2 helper parameter, 1 direct opener |
| B: unnamed | 1 face (`freshnessbound_latest.json`) |
| C: consumer read sites | 9 (8 more arrive through a helper and are not priced) |
| C: faces read by no consumer | **8 faces / 2,781,043 B** — written by a producer, consumed by nobody |
| retirement | narrowest rule (no writer, no reader, no constant) = **0** |

**Verdict (recomputed by the gate, not written by hand):**
`a_no_producer_face_is_not_named_by_any_source_in_the_scan_while_every_harness_restores_the_original`.

## Two census blinds found while pricing the writers

1. **A cross-module directory alias kills the open argument.** `OUTDIR = ST` where `ST` is
   another module's constant; `path = os.path.join(OUTDIR, FACE_NAME)`; then
   `for target in (path, os.path.join(OUTDIR, "x_latest.json")): open(target, "w")`. The
   directory half never folds, so an opener-argument census sees no writer at all for a
   producer that plainly writes the face. Reading the *arguments* of a composition call (not
   the composed expression) is what makes these visible.
2. **A leading BOM is not a negative.** `scripts/e429_two_hop_writer.py` is UTF-8-with-BOM;
   `ast.parse` raises `invalid non-printable character U+FEFF` and the source then reads as a
   file that names nothing. Strip the BOM, and disclose the source list
   (`sources.start_with_a_bom`) instead of counting an unparseable file as evidence of absence.

## Reusable rules

1. **"Nobody writes it" must name the writer's shape.** A writer that hands the name to a
   local helper, or carries it through local names, or names it with a module constant, is
   invisible to an opener-argument scan. Publish the writer classes, not one "no writer" word.
2. **Parse failure is not a negative.** BOM, encoding and syntax errors make a whole source
   disappear; publish the unparseable/unstripped sources by name, in their own column.
3. **Read the arguments of a composition, not just the composition.** The outer `join(OUTDIR,
   FACE_NAME)` cannot fold while its literal half folds perfectly; a judgement placed on the
   expression alone loses every f-string and every loop-built target list.

## Bounds

Population is E492's published row set (not a fresh composer scan). Writers are followed one
local helper hop and two local-name hops inside one module; a path composed entirely inside a
foreign module and never passed in stays invisible (this is why one face still reads
"unnamed"). Readers that reach the payload through a helper are counted but not priced — 8 of
the 9 consumer sites. `B_NONE` means "no source in the scan names it", never "no source writes
it".

## Verification

- `python scripts/e495_doctorpub.py run` rc0 · `check` `problems=[]` · `verify`
  `problems=[]` (rebuild identical) · `selftest` **13/13**
- `python scripts/run_e495_smoke_leg.py` **9/9** (two doctored arms red: a hidden leaving
  harness, a carried summary)
- smoke leg `E495 (r1527 bm-b)` run verbatim through `scripts/run_smoke_legs_by_name.py` —
  1/1 green
- S6 leg `doctor_pub` rc0 0.07 s
- Product: `results/state_tilt/DOCTORPUB-2026-11-07.json` + `doctorpub_latest.json`
  (13 rows, per face harness discipline, writer class with sites, reader prices, payload
  hash/size/self-reported study)