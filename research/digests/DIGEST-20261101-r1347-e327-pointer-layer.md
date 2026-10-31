# DIGEST 2026-11-01 r1347 -- E327: the pointer layer E326 counted is 3 pointers, not 143

**Card** E327 (seeded by r1346 when E326 closed with an explicit hedge).

**Question.** E326 published "11 of 20 parameterised faces are reachable through 143 `*latest*.json` pointers whose readers never see a date in a file name" and marked the layer measured-not-traversed. Traverse it: which published numbers are read through a pointer, and does the pointer's content republish the face it names?

**Answer.** The layer is 3 pointers. 140 of the 143 pairs are something else, and 137 of those are faces that *measured* the target.

## Method

Static analysis over E326's published population (20 parameterised faces) and the python corpus E323/E326 already use (scripts/Tools/live/monitor/firm, 2280 sources), this scanner excluded. Every `*latest*.json` sibling E326's helper returns is classified on **parsed content**, never on a substring:

| class | rule |
|---|---|
| `POINTER_IDENTICAL` | the pointer's parsed content equals the dated face |
| `POINTER_SAME_STUDY` | same study, another vintage |
| `CITES_AS_INPUT` | the face appears only under `source_faces` / `upstream` / `inputs` |
| `MEASURED_SUBJECT` | the face appears inside a census result (`faces_censused`, `rows[].face`, …) |
| `UNEXPLAINED` | present and unaccounted for -- must be 0 |

Only the two `POINTER_*` classes are read through; for those the python corpus is scanned for writers, cutoff-readers and silent readers.

## Readings

- pairs 143 | real pointers **3** | citations 3 | censuses 137 | unexplained **0** | over-count **47.67x**
- 3 pointer files, **3 faces** (upstream said 11) -- `banddeflate_latest.json`, `gateoperands_latest.json`, `gatetol_latest.json`
- all 3 pointers are content-identical copies whose `evidence_cutoff` equals the date token they mirror → the parameter survives one indirection
- consumers 5: 1 writer (e283), 2 read the cutoff back (e313), 2 name a pointer and never surface it (e312)
- verdict `the_parameter_survives_one_indirection_in_content_but_some_reader_quotes_the_pointer_without_surfacing_the_cutoff`

## Pits

1. **Classify the link, not the string.** The helper's substring test counts "a file that mentions the face" as "a pointer to the face"; the gap is 140/143. Fourth appearance of one defect class (E321/E322/E325/E327) -- now at the sibling layer.
2. **A walk truncated for display reclassifies rows.** First draft capped list walking at 8 items and "found" 109 pairs mentioning nothing; they were items 9+ of `faces_censused`.
3. **A writer is a source that binds the pointer's name and writes to it**, not a source containing `json.dump`. e313 writes its own face and merely reads `gateoperands_latest`; the broad test makes every auditor the pointer's writer.
4. **Self-inclusion one level up**: the published face spells every pointer it found, so its own two files must be excluded from the sibling scan or the population grows each run (143 -> 154 observed before the guard).

## Reusable

Before reading anything through an indirection, publish what fraction of it is an indirection. "N pointers" from a substring test is a count of mentions; here 143 -> 3, a correction larger than the finding it supported. Publish content-level survival and reader-level honesty separately (3/3 vs 3/5) -- collapsing them hides the readers that quote a pointer without showing its cutoff.

## Evidence

- `scripts/e327_who_reads_a_face_through_a_pointer.py` -- selftest 16/16, verify `problems=[]` (143 pairs, 3 real pointers, 5 consumers)
- `results/state_tilt/POINTERREAD-2026-11-01.json` + `pointerread_latest.json`
- S6 leg `who_reads_a_face_through_a_pointer`; smoke leg executed standalone: PASS
- card `knowledge/METHODOLOGY_ASSETS.md` E327