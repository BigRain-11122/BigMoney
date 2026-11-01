# E334 — a repair of the shared corpus helper is a decision, and the decision is `decide()`

**Face:** `results/state_tilt/HELPERREPAIR-2026-11-01.json` (+ `helperrepair_latest.json`)
**Study:** `scripts/e334_helper_repair_blast_radius.py` (selftest 19/19)
**Upstream:** E332 `INVISIBLETAIL-2026-11-01.json` (the defect), E333 `SURVIVINGCONCLUSIONS-2026-11-01.json` (the delta)
**Card:** `E334-FIX-THE-HELPER-OR-KEEP-IT`

## The question the card asked

E332 measured that `e326.code_lines` hides 4,284 real code lines. E333 re-priced four consumers of
that helper and found 17 of 69 published numbers move, with no verdict flip. Neither answer is a
decision: *may the helper be fixed in place today?* A repair moves numbers that more than forty
faces were derived from, so the answer has to be a blast radius, not an opinion.

## What was measured

Three axes, one corpus, one file list (`e326.corpus()`), and each consumer's own `build()` run
twice — once under the shipped helper, once under the tokenizer reading from E332. The patched
helper is restored in a `finally` block and the restore is asserted after every build.

| axis | what it answers | how it is read |
|---|---|---|
| delta | which published numbers the repair moves | every numeric leaf of each consumer's summary block, by dotted path |
| published | what a reader of today's face would have to re-read | published face vs shipped build (corpus-drift control) and vs repaired build |
| evidence | what the repair *erases* instead of moving | a study whose published number states the defect's size collapses to zero |

### Six consumers, not four

E333 priced E326, E328, E329, E330. Two more read the same helper and were never priced: **E327**
(pointer readers) and **E331** (pointer-only readers, which E332 re-priced by hand and E333 never
folded into its registry).

**29 of 122 published numbers move. One verdict flips.**

E327's verdict is the flip:

> `the_parameter_survives_one_indirection_in_content_but_some_reader_quotes_the_pointer_without_surfacing_the_cutoff`
> → `the_parameter_survives_one_indirection_and_every_reader_of_a_real_pointer_either_writes_it_or_reads_its_cutoff_back`

Its two "silent readers" (`readers_that_do_not_surface_the_cutoff` 2 → 0,
`consumer_names_the_pointer_and_never_shows_the_parameter` 2 → 0) are real code that lives inside a
span the shipped helper never shows. The published defect claim was an artifact of the instrument.
That is the strongest argument *for* repairing the helper and the strongest argument *against*
repairing it silently: the correction only exists if someone re-reads the face.

### Evidence is erased, not moved

| study | published number | shipped | repaired |
|---|---|---|---|
| E332 | `summary.recovered_code_lines` | 4,284 | **0** |
| E333 | `summary.published_numbers_moved` | 17 of 69 | **0** |

E332's blindness is measured (it is rebuilt under the repair). E333's is structural and disclosed as
such: its two halves are the shipped reading and the recovered reading, so once the tokenizer *is*
the shipped reading both halves are one function and it would publish "nothing moves" — a clean
zero from a study that no longer measures anything. E333 happens to survive a *runtime* patch
because it captures the helper at import (`SHIPPED = e326.code_lines`); a source repair re-captures
the repaired helper at the next import, which is the case the recommendation assumes. `reading_site`
publishes that distinction per consumer (all six read at the call site; E333 captures).

### The corpus-drift control

`published vs shipped` differs on 5 of 6 faces (E326 4, E328 3, E329 2, E330 1, E331 2) — those
faces no longer reproduce from today's corpus at all. E330 moves **zero** numbers under the repair
while its published face still differs by 1: that one is drift, and the two axes never mix.

## The decision

```
decide(verdict_flips, numbers_with_no_single_source_explanation, studies_whose_evidence_is_erased)
```

in-place is allowed only when all three are zero; otherwise the repair ships as a sibling entry
point. On this face: **1 flip, 27 unattributed, 2 erased** → **sibling entry point**.

| scenario | published numbers that move | faces to republish | evidence erased | files to edit |
|---|---|---|---|---|
| fix in place today | 37 | 6 | 2 | 1 |
| publish beside the old one | 0 | 0 (until a consumer opts in) | 0 | 2 |

**Recommendation:** publish the tokenizer reading beside the shipped one, keep the shipped reading
pinned under an explicit legacy name for the studies that measure the defect, and republish the six
faces only in the window where their readers opt in.

## Pits

1. **A rule that returns its first failure reads as if the others were absent.** The first version
   of `decide()` returned the erasure verdict and dropped the E327 flip from the reason string — the
   flip was in `decision.inputs` but the sentence a reader quotes would not have mentioned it. Same
   defect one level down: a verdict that is true but incomplete. Every failing condition is named now.
2. **A budget that is never spent looks like a budget that was respected.** The first run printed
   "ablating 6 sources" per consumer while `candidates` was empty, so `attribute()` returned nothing
   and every moved number read as unattributed for free. A silent no-op inside a measurement budget
   is indistinguishable from discipline unless the tried-count is published (`ablation_sources_tried`).
3. **27 of 29 moved numbers are unattributed on purpose.** Six shared ablations cannot explain 29
   numbers over 2,286 sources. They are published as unattributed, never guessed — and the
   recommendation does not need them: the evidence axis alone blocks an in-place repair, which is
   why `decide()` checks it first.
4. **Publication is the expensive part, measurement is not.** Blindness is 2 × ~70 s of E332 rebuild;
   twelve consumer builds are the rest. Running it inline under a wall budget kills it mid-corpus
   (this window's first attempt died at 5 minutes inside E330) — a detached build with a progress
   stream on stderr is the only honest way to measure a six-minute number.
5. **The study is inside its own corpus.** Its script is one of the ~2,286 sources every consumer
   scans, so an edit to the study moves the very numbers it publishes: `scenario_in_place` read 34
   while the study's source was one size and 37 after three edits to it, and E328's drift control
   went 0 → 3 in the same breath. The face is deterministic at rest (verify re-derives it byte for
   byte), but the value is only true of a fixed tree — which is why the face records the corpus it
   measured rather than presenting the number as a property of the helper alone. Own *faces* are
   dropped from the corpus (`own_face_excluded`, 0 found today because `e326.corpus()` does not
   walk `results/`), own *source* cannot be.