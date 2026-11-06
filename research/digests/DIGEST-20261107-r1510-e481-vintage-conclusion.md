# DIGEST 2026-11-07 r1510 bm-b — E481: a "different answer" is usually a different number in the same sentence

**Card.** E481 -- DO THE VINTAGES THAT DIFFER FROM THEIR TWIN ALSO STATE A DIFFERENT ANSWER (pool
card seeded by r1505, burned r1510).

**Producer.** `scripts/e481_vintage_conclusion.py` -- `run` rc0, `check` problems=[], `verify`
problems=[] (rebuild on the same tree), **selftest 34/34**.

**Faces.** `results/state_tilt/VINTAGECONC-2026-11-07.json` + `vintageconc_latest.json`.

**Population.** Inherited, never restated: the 145 rows E478 classed
`differs_beyond_the_top_level_clock_fields` out of E472's 571 unread-vintage member files.

## Reading

- 145 differing vintages, 98 comparable against the frozen conclusion vocabulary (eight names):
  **21 same conclusion in different rows / 77 a different conclusion / 47 twin states no conclusion
  field**; 0 unreadable, 0 twin missing.
- Verdict: `some_differing_vintages_state_their_twins_conclusion_and_the_majority_state_a_different_one`.
- Same-conclusion bytes: 1,117,833 B (21.4% of the comparable set). Different: 7,848,356 B.
- **Of the 77 "different", 70 differ only in their numbers** -- collapse every digit to `#` and the
  two strings are identical (7,524,781 B). Only 7 state a substantively different verdict.
- Vocabulary census: `answer` is stated by 67 twins and differs in 67 of 67 (every one of those a
  numeric move); `verdict` is stated by 31 twins, 21 agree / 10 differ; the other six frozen names
  never fire. A zero-hit word is a measurement about the corpus, not proof that nobody writes it.
- Secondary arm (all twin-stated top-level scalars, clock names excluded): 61 rows differ **only**
  on `evidence_cutoff` -- a republish stamp, not a conclusion move. Every row the primary arm calls
  comparable also moves somewhere at the surface, which is why the scalar arm can only ever price
  the surface, not the claim.

## The seven substantive differences

| vintage | twin | member says | twin says |
|---|---|---|---|
| `PRECISIONGAP-2026-10-31` | latest | `none_of_the_face_level_rows_is_at_risk` | `some_face_level_rows_stay_at_risk` |
| `PRECISIONGAP-2026-11-01` | latest | `none_of_the_face_level_rows_is_at_risk` | `some_face_level_rows_stay_at_risk` |
| `UNFLOORED-2026-11-03` | latest | `a_stale_face_passes_every_reader_that_never_asks_how_old_it_is` | `every_face_in_this_set_is_behind_the_panel_and_no_reader_asks_how_old_it_is` |
| `UNFLOORED-2026-11-05` | latest | (same as above) | (same as above) |
| `DIRFIELD-2026-11-03` | latest | `..._but_no_published_row_could_double` | `..._and_published_rows_could_double` |
| `DIRISFACE-2026-11-05` | latest | `directory_values_are_face_home_directories_and_none_of_them_compose` | `directory_values_are_face_names_but_no_row_composes_onto_a_file` |
| `PRECISIONCENSUS-2026-10-30` | latest | `printed_copies_are_compared_finer_than_they_print` | `legs_compare_face_values_finer_than_the_faces_print` |

Read by hand (the face does not grade this): PRECISIONGAP is a **flip** -- the earlier vintage says
nothing is at risk and the later one says something is; the two UNFLOORED rows are a scope rewrite
(`every face` -> `a stale face`); DIRFIELD/DIRISFACE/PRECISIONCENSUS are re-wordings of one claim.
That split is published as prose precisely because a token overlap cannot tell a rename from a flip.

## The rule

"Differs from its twin" is not one fact. Price the difference in three layers, cheapest witness
first:

1. bytes identical (E477) -- nothing to keep;
2. beyond the clock names (E478) -- a row moved;
3. beyond the conclusion (this study) -- what moved was a number in the same sentence, or the claim.

Only layer 3 (7 rows here) makes the old file a second measurement. Layer 2 at 70 rows is one
measurement printed twice with updated magnitudes: still not deletable on its own (the old numbers
are gone from the new file), but the reason is "the numbers differ", not "the finding differs".

## Pits

- **A numeric move reads as a conclusion move unless you collapse the digits.** Exact string
  equality published 77 "different conclusions"; 70 of them are the same sentence with new
  numbers. The numeric-shape arm is published beside the verdict, never folded into it -- the
  verdict must stay the strictest witness, the arm says how much of it is magnitude.
- **A frozen vocabulary hides the class it cannot see.** 47 of 145 twins state no field in the
  eight names; they are published `twin_states_no_conclusion_field` (unmeasured), never "same".
  Publishing the per-word hit count (six of eight words at zero) is what keeps that residue legible.
- **The same face must be compared, not the family.** Each vintage is compared with its own family's
  twin, and the twin is excluded from the population -- a twin compared to itself would score
  "identical" forever and inflate the retirable count.
- **A date stamp is not a conclusion.** 61 rows differ only on `evidence_cutoff`; treating that as a
  conclusion difference would charge every republish as a new finding.

## Witnesses

Five doctored copies go red while the live face reads clean: a moved same-conclusion count, a
same-conclusion row that names a differing field, a tally that no longer sums to the population, a
field outside the frozen vocabulary, and a vocabulary histogram that does not re-derive. The smoke
leg is extracted verbatim from `smoke_test.py` (`scripts/run_e481_smoke_leg.py`), red-proved on a
doctored face and restored byte-identical (sha in == sha out).

## Next

E482 (do the `*_latest` spellings outside E479's 36 families resolve to a file that exists) is the
next ready card; E483 and E485 stay on the supply floor. E481's own residue for a later card: the
70 numeric-only rows are a distinct class of "same claim, older magnitudes", and nothing has yet
asked whether a reader ever wants the older magnitudes (E478/E479 both only asked which bytes
survive).