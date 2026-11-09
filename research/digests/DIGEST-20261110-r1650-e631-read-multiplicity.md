# DIGEST — E631 read multiplicity (r1650 bm-b, 2026-11-10)

**Question.** E630 closed the caller and callee arms with zero writes, so the last place the
published duplicate count could be wrong is the read side: E625 counts a duplicate when a
same-object read of the key lands after the dead line, and this card asks whether that read is the
only one.

**Reading.** 34 live dead face-key lines carry 13 reads of the key after the dead line, over 6
lines; 3 lines carry two or three such reads; 3 of the 4 duplicate rows sit in a function that holds
more than two reads (cn_mkneutral `simulate` 3, e590 `face_problems` 5, ew6 `write_outputs` 6).

**The coverage check is the answer.** E625's `sibling_reads` list accounts for every read in the
function on all 34 lines (`len(list) == reads_of_the_key_in_the_function − dead_reads_on_that_line`,
0 uncovered). The duplicate test therefore already saw the second and third read, and the
denominator stands. The hole E631 was opened to price is empty — by measurement, not assumption.

**Reusable.** Before pricing any "the study only counted the first X" doubt, publish a coverage
table (published list length vs the function's own total) and make "list does not cover the
function" a class that refuses to price the denominator, never a quiet member of the normal class.

**Evidence.** `scripts/e631_read_multiplicity.py` (selftest 26/26), `results/state_tilt/
READMULTIPLICITY.json` + `readmultiplicity_latest.json`, `scripts/run_e631_smoke_leg.py` (1/1 PASS,
`--doctor` 1/1 red, face restored byte-identically), smoke leg E631, S6 leg `read_multiplicity`.
