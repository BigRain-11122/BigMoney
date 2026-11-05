# DIGEST 2026-11-05 r1461 bm-b — E441: is E435's empty composition a timing accident or a structural safety?

**Question.** E435 (r1458) published directory values that are the home directory of a published
face, and **0** composable joins that lands on an existing path. A zero like that is only readable
next to a second number nobody had taken: is the base still being written to?

**Method.** For every face-home row, list the published `.json` faces living **directly** under the
named directory (`e435.face_index`), drop the carrier itself and this study's own outputs, and count
members whose mtime is strictly later than the carrier's. Rows are graded live / frozen per carrier;
directories live if any carrier was outlived. The composable subset is then cross-tabbed against that
grading, because that subset is the population a landing target would change.

**Answer.** `some_face_home_bases_are_live_writer_directories_and_the_rest_are_frozen`.

| reading | value |
|---|---|
| face-home rows / distinct directories | 522 / 72 |
| live directories | 21 |
| frozen directories | 51 |
| carriers outlived by a member of their base | 83 of 522 (15.9%) |
| composable rows on a live base | 36 |
| composable rows on a frozen base | 349 |
| carriers that name their own directory | 44 (all in `results/state_tilt`) |

**The population is not stable, and that is the second finding.** This face first measured **626**
rows. After the census faces it inherits from were rebuilt in the same window it fell to **522**: the
104 rows that vanished were directory values *republished by stale censuses*. Much of what E435
counted was other censuses restating the same directories, so any count in this family must name the
round it was taken in.

**Two exclusions that are different facts.** The carrier must leave its own member list, or a face
that names its own directory is always its own newest member and every such base reads frozen. And
this study's own faces must leave the scan, or the largest family reads live *because of the reader*
(E180/E207 self-inclusion, sixth recurrence). `is_own_output()` carries four selftest legs.

**Two defects caught by inspection, not by the code.** (a) The aggregate directory key was first
spelled `directory`, which put this study's own face back into the population it censuses — measured
in-window at exactly **+144 rows** (72 directories x the dated face and its `latest` twin). Renaming
the key to `base` (the spelling the rows already used) removed the self-inflation: the r1234
name-is-semantics law firing on a study about names. (b) The first distance check compared this
study's row count against E435's *whole* directory-valued population rather than the face-home
subset, so it fired on its own correctness every run.

**Republishing cascade, disclosed.** Ten census faces opened red in the full suite (329/339) because
their populations had grown since they were published. Rebuilding them is not a single pass: each
publication changes the population the next face counts, so the faces were rebuilt twice in
dependency order (`e411 → e416 → e418 → e417 → e409 → e398 → e422 → e423 → e435 → e441`) plus `e433`
afterwards, and every affected leg was re-run green.

**Products.** `scripts/e441_facehome_family.py` (selftest 24/24),
`results/state_tilt/facehome_latest.json` + `FACEHOME-2026-11-05.json`, S6 leg `face_home_family`
(verify), smoke leg extracted verbatim with a doctored frozen directory as control
(`scripts/run_e441_smoke_leg.py --doctor`), card `E441` in `knowledge/METHODOLOGY_ASSETS.md`.

**Reusable.** A published zero about an unperformed composition is not a safety claim; it is a claim
about the last write to the base. Read the base's own newest member before calling a zero structural
— and re-read the population count afterwards, because refreshing a census shrinks its population.